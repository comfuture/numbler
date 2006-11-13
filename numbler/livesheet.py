#
# livesheet.py
# (C) Numbler LLC 2006
# See LICENSE for details.
#
# contains the nevow classes for rendering livesheet pages
#
# updated to include code to generate sheet from nevow

#nevow goodness
from nevow.livepage import IClientHandle,js
from nevow import rend, loaders, appserver,static,guard,inevow,url,flat,stan,util,athena,json
from nevow import tags as T
from nevow.inevow import ISession,IRequest

#twisted
from twisted.internet.defer import deferredGenerator,waitForDeferred

# general
import time
import traceback
import types
import math
import traceback,sys

# numbler server

from numbler.server.sheet import *
from numbler.server.cell import CellHandle, CellRange
from numbler.server import ast,fdb
from numbler.server.sslib.observer import Observer
from numbler.server.sslib.utils import *

from numbler.server.colrow import Col, Row
from numbler.server.ssdb import ssdb
from numbler.server.account import lookupAccount
from numbler.server import exc
from numbler.wsmanager import wsResponseManager

# numbler web
from sheetlock import *
import sharedlivepage
from jscompressor import JSCompressor
import sheetimport
import invite
from support_pages import *
from numbler.utils import simplecell,validEmail
from numbler import webservices
from cookiemgmt import *
import account_pages
import apimanager


#class ISessionPages(compy.Interface):
#    """ dummy interface for getting and setting the pages that are attached to the session"""
#    pass


def decodeCellKey(key):
    """ return column, row from key """
    return (key % 256,key >> 8)




class clipboardItem:
    """ server side representation of an item in the clipboard"""

    def __init__(self,dict):
        if dict.has_key('startcell') and dict.has_key('endcell'):
            self.startcell = simplecell(dict['startcell'])
            self.endcell = simplecell(dict['endcell'])
            self.origin_col = min(self.startcell.col,self.endcell.col)
            self.origin_row = min(self.startcell.row,self.endcell.row)

        self.source = dict['source']
        if type(self.source) == types.ListType:
            # pass in the top left of the bounding area the cell is aware of it's offset 
            self.cells = map(lambda x: simplecell(x,self.origin_col,self.origin_row),self.source)
        else:
            self.cells = [simplecell(self.source)]


class chatHistory:
    def __init__(self):
        self.max = 20
        self.comments = []
        self.users = {}
    def addComment(self,ts,username,comment):
        self.comments.append((ts,username,comment))
        if len(self.comments) > self.max:
            self.comments.pop(0)

    def addUser(self,clientID,username):
        self.users[clientID] = username

    def removeUser(self,clientID):
        if clientID in self.users:
            del self.users[clientID]

    def userList(self):
        return self.users.values()
    
    def replay(self):
        return map(lambda x: {u'ts':x[0],u'u':x[1],u'c':x[2]},self.comments)


class SheetFactory(athena.LivePageFactory):
    """ a simple extension to the athena LivePageFactory. """

    def __init__(self,name):
        athena.LivePageFactory.__init__(self);
        self.chatHistory = chatHistory();
        self.lockmanager = lockManager(900); # default timeout of 15 minutes
        self.sheetname = name;
        self.updates = {}
        self.cachingUpdates = False

    def startCachingUpdates(self):
        self.cachingUpdates = True
        #print 'start caching Updates:',self.updates

    def accumulateUpdates(self,clientID,values):
        """ used by the clients to accumulate updates from the sheet engine. This
        is useful because the engine can fire multiple updates but we want
        to control how these updates are sent to client in order to efficiently use
        athena transports (e.g. ajax).
        """

        if not self.cachingUpdates:
            # if we are not caching updates then the update came from another
            # sheet.
            self.getClient(clientID).sendUpdates(self.flusher(values),False)
        else:
            if self.updates.get(clientID):
                self.updates[clientID].update(values)
            else:
                self.updates[clientID] = values
            #print 'accumulateUpdates:',self.updates

    def flusher(self,cellHandles):
        """
        generator to return computed cell values.  this function performs a number of tricks
        to optimize the way we calculate results for presentation.
        """
        #start = time.time()
        try:
            sheetCache = {}
            ret = self.flushInternal(sheetCache,cellHandles)
        finally:
            for item in sheetCache.keys():
                sheetI = sheetCache[item]
                del sheetI.computeCache
                del sheetI.valueCache
                #del sheetI.dataCache
        #end = time.time()
        #print 'flusher duration:',end-start
        return ret


    def flushInternal(self,sheetCache,cellHandles,cacheData = False):
        """
        flushInternal does a bunch of work to cache values when building
        results for the user's sheet.

        It has a multilevel cache:

        1) sheet Instances (from sheet HandleS)
        2) cellRange instances (computeCache, probably poorly named)
        3) cell Instance (also stuck in the compute Cache, the keys don't overlap)
        4) valueCache: cached evaluated values of cells
        5) dataCache: cache of the final production that will be sent to the user.  This is
        not used if the request is from the initial load (or a specific client load)
        or if there is not more than one client connected to the sheet.

        """
        ret = []
        #print 'flush internal called:'
        #for cellH in cellHandles:
        #    print cellH,cellH.key,id(cellH),cellH().getValue()
        
        for cellH in cellHandles:
            sheetI = sheetCache.get(cellH.sheetHandle.sheetId)
            if not sheetI:
                sheetI = cellH.sheetHandle()
                sheetCache[cellH.sheetHandle.sheetId] = sheetI
            if cellH is not None:
                if not hasattr(sheetI,'computeCache'):
                    computeCache = {}
                    sheetI.computeCache = computeCache
                    sheetI.valueCache = {}
                    if cacheData:
                        sheetI.dataCache = {}            
                else:
                    computeCache = sheetI.computeCache

                if cacheData:
                    dataval = sheetI.dataCache.get(cellH.key)
                    if not dataval:
                        cellI = computeCache.get(cellH.key)
                        if not cellI:
                            cellI = cellH()
                            computeCache[cellH.key] = cellI
                        dataval = cellI.getData()
                        sheetI.dataCache[cellH.key] = dataval
                else:
                    cellI = computeCache.get(cellH.key)
                    if not cellI:
                        cellI = cellH()
                        computeCache[cellH.key] = cellI
                    dataval = cellI.getData()

                ret.append(dataval)
        return ret

    def flushUpdates(self,callee,ignoreSelf = False,extraData = None):
        """ flush all current updates from the engine out to the appropriate clients.
        this should be called after a transaction has finished.
        """
        #start = time.time()        
        ret = None
        try:
            sheetCache = {}
            keylist = self.updates.keys()
            numcons = len(keylist)
            for client in keylist:
                athenaclient = self.clients.get(client)
                # Need to check for the existance of the client handle because between
                # the time the update occured and flushupdates gets called the client
                # could disconnect.  I have only seen this in error situations but it
                # is possible there are other pathological scenarios.
                if athenaclient:
                    tempret = athenaclient.sendUpdates(self.flushInternal(sheetCache,self.updates[client],
                                                                          numcons > 1),
                                                       client == callee,ignoreSelf,extraData)
                    if client == callee:
                        ret = tempret
            self.updates = {}
        finally:
            for item in sheetCache.keys():
                sheetI = sheetCache[item]
                del sheetI.computeCache
                del sheetI.valueCache
                if numcons > 1:
                    del sheetI.dataCache
            self.cachingUpdates = False
        #end = time.time()
        #print 'flushUpdates duration:',end-start
        return ret

    def NumConnections(self):
        return len(self.clients)

    def KillAllClients(self):
        """
        disconnect all the clients connected to the sheet.  This is used when the sheet
        is about to be deleted.

        """
        for client in self.clients.keys():
            self.clients[client].action_close(None) # ctx = None
        del fdb.FDB.getInstance()[self.sheetname]

    def broadcastSystemMessage(self,msg):
        if len(self.clients):
            if type(msg) is not unicode:
                msg = unicode(msg)
            aClient = self.clients.values()[0]
            timeval = unicode(time.strftime("%I:%M "))
            self.chatHistory.addComment(timeval,u'Numbler',msg)
            aClient.broadcastEvent('chatwindow.newmessage',timeval,u'Numbler',msg)
                                   


class SheetLinkBar(rend.Fragment):
    docFactory = loaders.xmlfile('sheetlinkbar.xml',templateDir='templates')    
    loggedinpat = inevow.IQ(docFactory).patternGenerator("loggedin")

    def __init__(self,principal,shtH):
        self.principal = principal
        self.shtH = shtH

    def render_username(self,ctx,data):
        if self.principal:
            return self.principal.userid;
        else:
            return ''

    def render_accountinfo(self,ctx,data):
        if self.principal:
            return self.loggedinpat()
        else:
            return ''

    def render_invite(self,ctx,data):
        authreq = self.shtH().authRequired()
        if not authreq or (authreq and self.principal and self.shtH().sheetDbId in self.principal.ownedsheets):
            if not self.principal:
                return T.a(id="invitelink",href="",title="Invite another user",_class="left")['Invite']
            else:
                return T.a(id="invitelink",href="",title="Invite another user")['Invite']                
        return ''

    def rend(self, ctx, data):
        ctx.fillSlots('exportURL',url.here.child('export'))
        return super(SheetLinkBar, self).rend(ctx, data)


class LiveSheetPage(sharedlivepage.SharedLivePage): # Observer
    # with athena there is one LiveSheetPage instance per client connection
    docFactory = loaders.xmlfile('sheet.htm')

    jsdata = [
        ('js','./js','utils.js'),
        ('js','./js','benchmark.js'),
        ('js','./js','geometry.js'),
        ('js','./js','locking.js'),
        ('js','./js','widgets.js'),
        ('js','./js','graphics.js'),
        ('js','./js','undo.js'),
        ('js','./js','cache.js'),        
        ('js','./js','cell.js'),
        ('js','./js','RedBlackNode.js'),
        ('js','./js','RedBlackTree.js'),
        ('js','./js','sheetdim.js'),
        ('js','./js','dimchange.js'),
        ('js','./js','style.js'),
        ('js','./js','undodropdown.js'),
        ('js','./js','sheetbar.js'),
        ('js','./js','clipboard.js'),
        ("""
        //Divmod.debugging = true;
        """,),
        ('js','./js','chat.js'),
        ('js','./js','invite.js'),
        ('js','./js','drag.js'),
        ('js','./js','sheet.js')
       ]
    releasejs = ('js','./js','gensheetcode.js')

    copyright = """
    /*
    Copyright (c) 2006 Numbler LLC
    see http://numbler.org/license.html for license.
    RBT code derived from Kevin Lindsey's RBT sample (c) 2000-2004.
    see http://www.kevlindev.com/license.txt for license.
    */
    """

    # decodeCellKey is only used here to give a reference to something
    # defined in this module.  this is used by the compressor to decide whether
    # to regenerate the file based on the timestamp of the source file.
    compressor = JSCompressor(jsdata,releasejs,decodeCellKey,prefix = copyright)

    def __init__(self,factory,ctx,username):
        sharedlivepage.SharedLivePage.__init__(self,factory)
        self.sess = inevow.ISession(ctx)
        self.sheetname = factory.sheetname
        self.dbsheet = SheetHandle.getInstance(self.sheetname)
        self.chathistory = factory.chatHistory
        self.lockmanager = factory.lockmanager
        self.lastresults = None
        self.defwidth = 80
        self.defheight = 20
        self.updateInProg = False
        if not username:
            print '******** warning **** blank username'
            self.username = unicode('missing','utf-8')
        else:
            self.username = unicode(username,'utf-8')
        self.rootURL = inevow.IRequest(ctx).URLPath()

    def userName(self):
        return self.username
        #return unicode(self.sess.username,'utf-8')

    # nevow specific overrides / additions
    def cleanupOnDisconnect(self,cb):
        self.dbsheet.detach(self)
        self.chathistory.removeUser(self.clientID)
        # tell the other clients the user has left.
        self.sendEvent(self.clientID,'chatwindow.onleave',unicode(time.strftime("%I:%M ")),
                       self.userName())
        
    def _becomeLive(self):
        # we need to override _becomeLive to do a bunch of disconnect operations
        athena.LivePage._becomeLive(self)
        # attach this object as a sheet observer
        self.dbsheet.attach(self)

        self.notifyOnDisconnect().addBoth(self.lockmanager.onDisconnect,self.clientID)
        self.notifyOnDisconnect().addBoth(self.cleanupOnDisconnect)

        # add ourself to the chat users list
        self.chathistory.addUser(self.clientID,self.userName())

        
    ################################################################################
    ## render specific methods
    ################################################################################

    def render_title(self,ctx,data):
        # definately not part of the title but might as well
        # do it here
        self.ownURL = inevow.IRequest(ctx).URLPath()
        return self.dbsheet().getAlias()

    def render_scriptheaders(self,ctx,data):
        debug_scripts = ctx.arg('debugscripts')
        if debug_scripts and debug_scripts in ('true','1'):
            return self.compressor.debugMode()
        else:
            return self.compressor.releaseMode()

    def render_mochikit(self,ctx,data):
        debug_scripts = ctx.arg('debugscripts')
        if debug_scripts and debug_scripts in ('true','1'):
            return T.script(src="mochikit/MochiKit/MochiKit.js",type="text/javascript")
        else:
            return T.script(src="mochikit/packed/MochiKit/MochiKit.js",type="text/javascript")            

    def render_dojo(self,ctx,data):
        debug_scripts = ctx.arg('debugscripts')
        if debug_scripts and debug_scripts in ('true','1'):
            return [
                T.script(src="dojo/dojo.js",type="text/javascript"),
                T.script(type="text/javascript")[T.raw("""
                dojo.require("dojo.event.*");
                dojo.require("dojo.widget.Toolbar");
                dojo.require("dojo.widget.HtmlColorPalette");
                dojo.require("dojo.widget.Dialog");
                dojo.require("dojo.widget.Menu2");
                """)]]
        else:
            return T.script(src="dojo/compresseddojo.js",type="text/javascript")

    def render_chat(self,ctx,data):
        return (T.div(id='chatarea'),
                T.form(action='',_id='chatform',onsubmit="chatwindow.submitMessage();return false;")[
            T.div['type your message here:'],
            T.div[T.xml('&nbsp;')],
            T.input(id='chattextarea',name='chattextarea',type='text'),
                ])

    def render_linkbar(self,ctx,data):
        sess = inevow.ISession(ctx)
        return SheetLinkBar(getattr(sess,'principal',None),self.dbsheet)

    ################################################################################
    ## engine update methods
    ################################################################################

    # support utility for used to capture and accumulate engine updates
##    def updateHandler(func):
##        print dir(func),dir(func.func_closure)        
##        def runfunc(*args,**kwargs):
##            print dir(func),dir(func.func_closure)
##            self = func.im_self
##            try:
##                self.beginCellUpdate()
##                func(*args,**kwargs)
##                self.endCellUpdate()
##            finally:
##                self.clearUpdate()
##        return runfunc

    
    def beginCellUpdate(self):
        """ set a flag that an update is in progress.  This will ignore database updates
        until we have finished processing."""
        self.updateInProg = True
        self.factory.startCachingUpdates()

    def _internalSend(self,results):
        self.sendEvent(self.clientID,'currentsheet.onCellCalc',results,False)
        return self.callRemote('currentsheet.onCellCalc',results,True)        

    def endCellUpdateCb(self,arg,ignoreSelf=False,extraData = None):
        #print 'endCellUpdateCb called',ignoreSelf
        ret = self.endCellUpdate(ignoreSelf,extraData)
        if ignoreSelf:
            if extraData:
                return ret + extraData,True
            else:
                return ret,True

    def endCellUpdate(self,ignoreSelf=False,extraData = None):
        """ send the accumulated results back to one or more clients """
        # make sure the sheet updates any non-saved cell values (like RAND,NOW,etc)
        self.dbsheet().notifyRecalcCells()
        return self.factory.flushUpdates(self.clientID,ignoreSelf,extraData)

    def sendUpdates(self,results,fromSelf,ignoreSelf = False,extraData = None):
        if extraData is not None:
            results = results + extraData
        if results:
            if fromSelf and ignoreSelf:
                return results
            return self.callRemote('currentsheet.onCellCalc',results,fromSelf)
        return None

    def clearUpdateCb(self,arg):
        #print 'clearUpdateCb called',arg
        self.updateInProg = False
        return arg

    def clearUpdate(self):
        """ clear an update in progress, usually called from a finally block"""
        self.updateInProg = False
        #print 'updateInProg: False'

    def update(self,*args,**kwargs):
        """ callback when the sheet engine notifies us of updates.  We only
        keep track of the cell handles and don't fetch the actual data until
        we send the results - this avoid errors if you have multiple cascading
        operations that may invalidate the previous value of a cell before we
        have had a chance to respond to the client """
        self.factory.accumulateUpdates(self.clientID,args[1])
                

    def onSheetLoad(self):
        """ when a new client connects send the updated sheet from the database """
        print 'received sheet load event'
        # fetch the current sheet data from the DB.  this is
        # a sparse set of data that only includes values explicitly set by the user.

        extents = self.dbsheet().getDimensions()
        dimensions = {u'defwidth':self.defwidth,
                      u'defheight':self.defheight,
                      u'maxColWithData':int(extents[0]),
                      u'maxRowWidthData':int(extents[1]),
                      u'rows':[x.getData() for x in self.dbsheet().getRowProps()],
                      u'cols':[x.getData() for x in self.dbsheet().getColumnProps()],
                      u'locks':self.lockmanager.locksForClient(self.clientID)
                      }
        #print 'dimensions.locks:',dimensions['locks']

        rng = cell.CellRange(Col('A'),Row(1),Col(254),Row(65536))

        # grab the cell data using the factory optimized method
        celldata = self.factory.flusher(rng.getCellHandles(self.dbsheet))
        return dimensions,celldata

    def getChatHistory(self):
        val = self.chathistory.replay()
        # announce to other clients
        self.sendEvent(self.clientID,'chatwindow.onjoin',
                       unicode(time.strftime("%I:%M ")),
                       self.userName())
        return val,self.chathistory.userList(),self.userName()

    def onCellUpdate(self,jSONcell):
        # TODO: check if the cell is currently in focus by anyone
        self.sendTransientEvent(self.clientID,
                                'currentsheet.onEditingCell',jSONcell)

    def onCellLeave(self,jSONcell):
        #print 'onCellLeave',client
        self.sendTransientEvent(self.clientID,'currentsheet.onCellLeave',jSONcell)

    def onCellChange(self,jSONcells):
        #print 'onCellChange:',jSONcells
        try:
            self.beginCellUpdate()
            sht = self.dbsheet()
            for jSONcell in jSONcells:
                cell = simplecell(jSONcell)
                dbcell = self.dbsheet().getCellHandle(cell.col,cell.row)()
                dbcell.setFormula(cell.formula,sht.ownerPrincipal.locale)
            return self.endCellUpdate(True),True
        finally:
            self.clearUpdate()

    ################################################################################
    ## remote handlers
    ################################################################################

    def logClientError(self,error):
        if error is not None and 'error' in error:
            try:
                errRep = error.get('error')
                # this can fail if we don't really have a psuedo error object
                f = athena.getJSFailure(errRep,self.jsModules.mapping)
                print 'logClientError',f
            except Exception,e:
                print 'caught exception trying to display JS error:',e,error
        else:
            print 'logClientError',error

            
    def onColumnWidthChange(self,columnID,newwidth):
        #print 'Column %d Width %d ' % (columnID,widthDelta)
        col = int(columnID)
        width = int(newwidth)
        # update the DB
        prop = self.dbsheet().getColProp(col,self.defwidth);
        prop.setWidth(width)
        self.dbsheet().saveColumnProps(prop)
        self.sendTransientEvent(self.clientID,'currentsheet.onColumnWidthChange',col,width)

    def onRowHeightChange(self,rowID,newheight):
        row = int(rowID)
        height = int(newheight)
        #update the db
        prop = self.dbsheet().getRowProp(row,self.defheight)
        prop.setHeight(height)
        self.dbsheet().saveRowProps(prop)
        self.sendTransientEvent(self.clientID,'currentsheet.onRowHeightChange',
                                row,height)

    def onPasteCellBuffer(self,sourceBuffer,target):
        # when the client has a buffer of cells to paste into the sheet.
        
        try:
            self.beginCellUpdate()
            #print 'onPasteCellBuffer:',sourceBuffer,target
            targetcell = simplecell(target)
            # convert to simplecells to avoid having the engine deal with the JSON nastiness
            self.dbsheet().pasteFromBuffer(self.dbsheet,
                                           [simplecell(x) for x in sourceBuffer],
                                           targetcell.col,targetcell.row)
            return self.endCellUpdate()
        finally:
            self.clearUpdate()

    def onPasteCellBag(self,sourceBuffer):
        """
        paste an unordered set of cells back into the sheet.  Format and formula information
        are both set.
        """
        try:
            self.beginCellUpdate()
            self.dbsheet().bagPaste(self.dbsheet,
                                    [simplecell(x) for x in sourceBuffer])
            return self.endCellUpdate(True),True
        finally:
            self.clearUpdate()

    def onPasteCells(self,sourceRect,target):
        #print 'onPasteCells',sourceRect,target
        try:
            self.beginCellUpdate()
            rc = sourceRect
            targetcell = simplecell(target)
            
            rng = cell.CellRange(Col(rc['l']),Row(rc['t']),
                                 Col(rc['r']),Row(rc['b']))
            #print 'onPasteCells: range is',rng

            # do the paste event
            self.dbsheet().paste(self.dbsheet,rng,targetcell.col,targetcell.row);
            return self.endCellUpdate()
        finally:
            self.clearUpdate()

    def onCutCells(self,clipItem):
        """ We have a seperate cutCells method so we can know to put these cells in undo list"""
        print 'onCutCells called'
        self.beginCellUpdate()            
        cutCells = clipboardItem(clipItem)

        cr = CellRange.getInstance(cutCells.startcell.col,cutCells.startcell.row,
                           cutCells.endcell.col,cutCells.endcell.row)
        cellHlist = cr.getCellHandles(self.dbsheet)
        d = self.dbsheet().deleteCellHandleArray(cellHlist)
        d.addCallback(self.endCellUpdateCb)
        d.addBoth(self.clearUpdateCb)
        self.sendEvent(self.clientID,'currentsheet.onCutCells',clipItem)

    def onMoveUndo(self,startcell,copiedcells,destcell,targetcells):
        #print 'onMoveundo',startcell,copiedcells,destcell,targetcells
        try:
            self.beginCellUpdate()
            start = simplecell(startcell)
            dest = simplecell(destcell)
            self.dbsheet().pasteFromBuffer(self.dbsheet,
                                           [simplecell(x) for x in targetcells],
                                           dest.col,dest.row)
            self.dbsheet().pasteFromBuffer(self.dbsheet,
                                           [simplecell(x) for x in copiedcells],
                                           start.col,start.row)

            #self.endCellUpdate()
            ret = self.endCellUpdate(True) # don't send back to self
            return ret,True
        finally:
            self.clearUpdate()
            
    #@updateHandler
    def onMoveCells(self,startcell,endcell,destcell):
        """
        move a range of cells - useful for a drag type drop operation
        where you want the move to occur in one transaction instead of
        two transactions like in a cut and paste
        """
        self.beginCellUpdate()
        start = simplecell(startcell)
        end = simplecell(endcell);
        dest = simplecell(destcell)
        rng = cell.CellRange(start.col,start.row,end.col,end.row)
        # step 1: paste the cells
        self.dbsheet().paste(self.dbsheet,rng,dest.col,dest.row,False) # non sparse paste
        # step 2: clear the original cells
        pastrng = cell.CellRange(dest.col,dest.row,
                                 dest.col + (end.col - start.col),
                                 dest.row + (end.row - start.row))

        # delete only cells that are not overlapping
        delCells = set(rng.getCellHandles(self.dbsheet)).difference(pastrng.getCellHandles(self.dbsheet))

        deletedValues = []
        d = self.dbsheet().deleteCellHandleArray(delCells,saveData = deletedValues)
        d.addCallback(self.endCellUpdateCb,True,deletedValues)
        d.addBoth(self.clearUpdateCb)
        return d
        

    def onCopyCells(self,clipItem):
        #print 'onCopyCells'
        # simply pass through to the other client at this time.  In the future
        # we want to keep track of this for a server side clipboard feature
        self.sendEvent(self.clientID,'currentsheet.onCopyCells',clipItem)

    def onClearCells(self,startcell,endcell):
        self.beginCellUpdate()
        start = simplecell(startcell)
        end = simplecell(endcell)
        d = self.dbsheet().deleteCellHandleArray(cell.CellRange(start.col,start.row,end.col,end.row).getCellHandles(self.dbsheet))
        # when do with the delete process the results
        d.addCallback(self.endCellUpdateCb)
        # always clear the updating bit
        d.addBoth(self.clearUpdateCb)
        self.sendEvent(self.clientID,'currentsheet.onClearCells',startcell,endcell)


    def _afterInsertDel(self,cbData,colID,coldelta,rowID,rowdelta):
        # send back cell updates
        self.endCellUpdateCb(cbData)
        #print '_afterInsertDel: cbData is',cbData
        changevals = cbData[1]
        
        if len(changevals[0]) > 0 or len(changevals[1]) > 0:
            changecol =[x.getData() for x in changevals[0]]
            changerow = [x.getData() for x in changevals[1]]
            #print 'calling updateMultipelStyleClasses',changecol,changerow
            self.broadcastEvent('currentsheet.updateMultipleStyleClasses',changecol,changerow,colID,
                                coldelta,rowID,rowdelta)


        #return 
    def _adjustLocksOnRowInsert(self,defArg,rowID,numRows,deleteRegion):
        checkrect = getRect(1,min(rowID,rowID+numRows+1),Col.getMax(),max(rowID,rowID+numRows-1))
        adjustedlocks = self.lockmanager.adjustLockedRegions(self.clientID,self.dbsheet(),checkrect,
                                                             (rowID,numRows,0,0),deleteRegion)
        #print 'adjustedLocksOnColInsert called, adjustedlocks are',adjustedlocks
        if len(adjustedlocks):
            self.broadcastEvent('currentsheet.lockmanager.onUpdateLocks',adjustedlocks)
        


    def onRowInsert(self,rowID,numRows):
        """
        insert a row
        """
        # check for any non owned locks
        self.lockmanager.regionLocked(self.clientID,1,rowID,Col.getMax(),rowID+numRows-1)
        
        self.beginCellUpdate()
        d = defer.Deferred()
        d.addCallback(self._afterInsertDel,0,0,rowID,numRows)
        d.addCallback(self._adjustLocksOnRowInsert,rowID,numRows,False)
        d.addBoth(self.clearUpdateCb)
        return self.dbsheet().insertRow(rowID,numRows,d)


    def onRowDelete(self,rowID,numRows):
        """
        delete a row
        """
        self.lockmanager.regionLocked(self.clientID,1,rowID+numRows+1,Col.getMax(),rowID)
        
        self.beginCellUpdate()
        d = defer.Deferred()
        d.addCallback(self._afterInsertDel,0,0,rowID,numRows)
        d.addCallback(self._adjustLocksOnRowInsert,rowID,numRows,True)
        d.addBoth(self.clearUpdateCb)
        return self.dbsheet().deleteRow(rowID,numRows,d)

    def _adjustLocksOnColInsert(self,defArg,colID,numCols,deleteRegion):
        checkrect = getRect(min(colID,colID+numCols+1),1,max(colID,colID+numCols-1),Row.getMax())
        adjustedlocks = self.lockmanager.adjustLockedRegions(self.clientID,self.dbsheet(),checkrect,
                                                             (0,0,colID,numCols),deleteRegion)
        #print 'adjustedLocksOnColInsert called, adjustedlocks are',adjustedlocks
        if len(adjustedlocks):
            self.broadcastEvent('currentsheet.lockmanager.onUpdateLocks',adjustedlocks)
        


    def onColInsert(self,colID,numCols):
        """
        insert a column
        """
        # check for conflict with any existing locked regions.  if so an error will be raised.
        self.lockmanager.regionLocked(self.clientID,colID,1,colID+numCols-1,Row.getMax())
        
        self.beginCellUpdate()
        d = defer.Deferred()        
        d.addCallback(self._afterInsertDel,colID,numCols,0,0)
        d.addCallback(self._adjustLocksOnColInsert,colID,numCols,False)
        d.addBoth(self.clearUpdateCb)
        return self.dbsheet().insertColumn(colID,numCols,d)

    def onColDelete(self,colID,numCols):
        """ delete a column """
        self.lockmanager.regionLocked(self.clientID,colID+numCols+1,1,colID,Row.getMax())
        
        self.beginCellUpdate()
        d = defer.Deferred()        
        d.addCallback(self._afterInsertDel,colID,numCols,0,0)
        d.addCallback(self._adjustLocksOnColInsert,colID,numCols,True)
        d.addBoth(self.clearUpdateCb)
        return self.dbsheet().deleteColumn(colID,numCols,d)

    def _afterColRowDeleteUndo(self,cbData,undoCols,undoRows,id,delta,isColumn):
        # insert any of the undo information back
        if len(undoCols):
            for undoCol in undoCols:
                # set the formatting if present
                if len(undoCol['format']):
                    print 'afterColRowDeleteUndo: setting %s to %s' % (undoCol['key'],undoCol['format'])
                    self._internalSetStyle(undoCol['key'],undoCol['format'])
                # sent the dimension info if present.
                if undoCol['val'] > 0:
                    prop = self.dbsheet().getColProp(int(undoCol['key'][1:]),self.defheight)
                    prop.setWidth(undoCol['val'])
                    self.dbsheet().saveColumnProps(prop)
                    
        if len(undoRows):
            for undoRow in undoRows:
                if len(undoRow['format']):
                    self._internalSetStyle(undoRow['key'],undoRow['format'])
                if undoRow['val'] > 0:
                    prop = self.dbsheet().getRowProp(int(undoRow['key'][1:]),self.defwidth)
                    prop.setHeight(undoRow['val'])
                    self.dbsheet().saveRowProps(prop)

        self.endCellUpdateCb(cbData)

        changevals = cbData[1]
        changecol,changerow = [],[]
        if len(changevals[0]) > 0 or len(changevals[1]) > 0:
            changecol =[x.getData() for x in changevals[0]]
            changerow = [x.getData() for x in changevals[1]]        

        # merge the data from the undo with the changed style information.
        if len(undoCols):
            changecol.extend(undoCols)
        if len(undoRows):
            changecol.extend(undoRows)
        if len(changecol) > 0 or len(changerow) > 0:
            self.broadcastEvent('currentsheet.updateMultipleStyleClasses',changecol,changerow,
                                isColumn and id or 0,isColumn and delta or 0,
                                not isColumn and id or 0,not isColumn and delta or 0)

    def onColDeleteUndo(self,colID,numCols,undoCells,undoCols):
        return self.onColRowDeleteUndoInternal(colID,numCols,undoCells,undoCols)

    def onRowDeleteUndo(self,rowID,numRows,undoCells,undoRows):
        return self.onColRowDeleteUndoInternal(rowID,numRows,undoCells,undoRows,column=False)

    def onColRowDeleteUndoInternal(self,id,numItems,undoCells,undoStyles,column=True):
        """
        unfortunately this is somewhat complicated because of all the work that has to be done
        to put back together the previous data.
        """
        self.beginCellUpdate()
        d = defer.Deferred()

        def pastecb(arg):
            self.dbsheet().bagPaste(self.dbsheet,
                                    [simplecell(x) for x in undoCells])
            return arg
        
        d.addCallback(pastecb)
        d.addCallback(self._afterColRowDeleteUndo,
                      column and undoStyles or [],
                      not column and undoStyles or [],id,numItems,column)
        d.addBoth(self.clearUpdateCb)
        if column:
            return self.dbsheet().insertColumn(id,numItems,d)
        else:
            return self.dbsheet().insertRow(id,numItems,d)

            
    def genFormula(self,formulaType,startcell,endcell):
        """ called by the UI when the user requests to generate a aggregate formula based
        on the current selection """
        try:
            self.beginCellUpdate()
            start = simplecell(startcell)
            end = simplecell(endcell)
            #print 'genFormula:',startcell,endcell
            
            formulaType = formulaType.encode('utf-8')
        
            undolist,formulalist = self.dbsheet().genSelectionFormulas(
                self.dbsheet().getCellHandle(start.col,start.row),
                self.dbsheet().getCellHandle(end.col,end.row),
                formulaType)
            self.endCellUpdate()
            return undolist, formulalist, unicode(str(cell.CellRange(Col(start.col),
                                                                     Row(start.row),Col(end.col),Row(end.row))))
        finally:
            self.clearUpdate()

    def sortCells(self,sortType,startcell,endcell):
        """ sort of range of cells determined by the user.  The return value is a array of
        rows of cells used for undo."""
        self.beginCellUpdate()
        start = simplecell(startcell)
        end = simplecell(endcell)
        # because sortCells uses a defered delete we need to hang
        # a couple of callbacks off the deferred before the results can be sent to the client
        d,retRng = self.dbsheet().sortCells(self.dbsheet,sortType,
                                                  cell.CellRange(Col(min(start.col,end.col)),
                                                                 Row(min(start.row,end.row)),
                                                                 Col(max(start.col,end.col)),
                                                                 Row(max(start.row,end.row))))
        d.addCallback(self.endCellUpdateCb)
        d.addBoth(self.clearUpdateCb)
        # return the list of undo cells
        return retRng
            

    def sortCol(self,sortcol,sortType):
        """ sort a column of cells """

        start = {'row':1,'col':sortcol,'formula':''}
        maxC,maxR = self.dbsheet().getDimensions()
        end ={'row':maxR,'col':sortcol,'formula':''}
        ret = self.sortCells(sortType,start,end)
        # covert to single array
        return ret

    def undoColSort(self,sortcol,cells):
        """ undo a column sort by first deleting the cells and pasting them back """
        self.beginCellUpdate()
        sht = self.dbsheet()
        # step 1: delete the entire column
        d = sht.deleteCellHandleArray(cell.CellRange(sortcol,1,sortcol,Row.getMax()).getCellHandles(self.dbsheet))
        d.addCallback(self.undoColSortAfterDelete,cells)
        d.addCallback(self.endCellUpdateCb)
        d.addBoth(self.clearUpdateCb)

    def undoColSortAfterDelete(self,deferred,cells):
        """
        put humpty dumpty back together again after a sort.  this
        function needs to be batchified
        """
        sht = self.dbsheet()
        for cellObj in [simplecell(x) for x in cells]:
            cellI = sht.getCellHandle(cellObj.col,cellObj.row)()
            cellI.setFormula(cellObj.formula,sht.ownerPrincipal.locale)
            # note: this should be done before setFormula and the persist flag should be false
            if cellObj.format:
                cellI.setFormat(cellObj.format)        
        

    def pageInCells(self,cellregion):
        """ load in a region of cells that were out of view """
        #print 'pageInCells',cellregion
        region = cellregion;
        start = simplecell(region['start'])
        end = simplecell(region['end'])
        cells = self.dbsheet().getCellByRegion(start.col,start.row,end.col,end.row)
        celldata = map(lambda x: x.getCell().getData(),cells)
        return celldata
    
        ## chat specific handlers

    def chatsubmit(self,chatvalue):
        timeval = unicode(time.strftime("%I:%M "))
        self.chathistory.addComment(timeval,self.userName(),chatvalue)
        self.sendEvent(self.clientID,'chatwindow.newmessage',timeval,self.userName(),chatvalue)
        return timeval,chatvalue

    def onUnlockRegion(self,cb,lock):
        """ callback when a region is unlocked """
        print 'onUnlockRegion: lock is ',lock
        print 'onUnlockRegion: unlocking ',lock.lockuid
        self.broadcastEvent('currentsheet.lockmanager.onReleaseLock',lock.lockuid)
        #       js.currentsheet.lockmanager.onReleaseLock(lock.lockuid))
        return lock

    def unlockOnDisconnect(self,fail,lock):
        print 'unlockOnDisconnect'
        self.sendEvent(self.clientID,'currentsheet.lockmanager.onReleaseLock',lock.lockuid)

    ## locking handlers
    def requestLock(self,jsonlock,requestID):
        """ called by the client on a lock request"""
        print 'client %s is requesting a lock' % (self.clientID),jsonlock
        thelock = sheetlock(self.clientID,jsonlock)
        thelock.user =self.userName()
        
        defcb = self.lockmanager.getLock(thelock)
        retlock = thelock.toDict()
        if defcb:
            # register the appropriate callbacks
            defcb.addCallback(self.onUnlockRegion,thelock)
            defcb.addErrback(self.unlockOnDisconnect,thelock)
            retlock['owner'] = False
            self.sendEvent(self.clientID,
                           'currentsheet.lockmanager.onLockRegion',retlock)
            # js.currentsheet.lockmanager.onLockRegion(json.write(retlock)))
            
            # always send a response back to the lock originator
            retlock['owner'] = True
            return retlock,requestID
            #client.send(js.currentsheet.lockmanager.onRequest(json.write(retlock),requestID))
            
    def releaseLock(self,lockuid):
        # add lock release stuff here
        print 'releaseLock: ',lockuid
        self.lockmanager.releaseLock(lockuid)

    #style handlers
    def updateStyleClass(self,key,jsonstyle,changeprops):
        """ add/update the style data in the DB"""
        # decode row or column from the key - not that this is a userspace
        # key, not a db key
        self._internalSetStyle(key,jsonstyle)

        # pass on event to the other clients
        self.sendEvent(self.clientID,'currentsheet.onUpdateStyleClass',
                       key,jsonstyle,changeprops)
            

    def _internalSetStyle(self,key,style):
        sht = self.dbsheet()
        id = key[0].lower()
        val = int(key[1:])
        
        if id == u'c':
            prop = sht.getColProp(val,self.defwidth)
            prop.setFormat(style)
            sht.saveColumnProps(prop)
        elif id == u'r':
            prop = sht.getRowProp(val,self.defheight)
            prop.setFormat(style)
            sht.saveRowProps(prop)

    def removeStyleClass(self,key,lastprops):
        """remove the style class (if it is now empty)"""
        # save to db
        self._internalSetStyle(key,u'')
        # update clients
        self.sendEvent(self.clientID,'currentsheet.onRemoveStyleClass',key,lastprops)

    def _updateAllStyleCells(self,rect,proplist,deleteProp):
        """we set the style on every db cell right now - not very nice but it works """
        sht = self.dbsheet()
        for cell in [sht.getCellHandle(i,j)()
         # +1 on the ranges to make them inclusive
         for i in range(rect['l'],rect['r']+1) for j in range(rect['t'],rect['b']+1)
                     if not self.lockmanager.cellLocked(self.clientID,i,j)]:
            tempdict = cell.getFormat()
            if not len(tempdict) and deleteProp:
                continue
            if not len(tempdict):
                tempdict = {}
            for k in range(0,len(proplist),deleteProp and 1 or 2):
                if deleteProp:
                    try:
                        del tempdict[proplist[k]]
                    except KeyError,e:
                        # this can happen if we are deleting one style attribute but there
                        # is another (like we are deleting background color but there
                        # is text align
                        pass
                        #print 'failed to delete',proplist[k]
                else:
                    tempdict[proplist[k]] = proplist[k+1]
            cell.setFormat(tempdict)
        

    def updateStyleRegion(self,rect,proplist):
        """add a single style value to a region of cells"""
        #print 'updateStyleRegion',rect,proplist #type(rect),type(proplist)
        # update the database
        self._updateAllStyleCells(rect,proplist,False)
        self.sendEvent(self.clientID,'currentsheet.onUpdateStyleRegion',rect,
                       proplist)

    def updateCurrencyRegion(self,rect,curType):
        """ update the currency style attributes """
        #print 'updateCurrencyRegion',rect
        self.beginCellUpdate()
        try:
            proplist = [u'__sht',unicode(curType)]
            self._updateAllStyleCells(rect,proplist,len(proplist[1]) == 0)
            self.sendEvent(self.clientID,'currentsheet.onUpdateStyleRegion',rect,
                           proplist)
            # get all the cells in the change region
            rng = cell.CellRange(rect['l'],rect['t'],rect['r'],rect['b'])
            cellHandles = rng.getCellHandles(self.dbsheet)
            results = [x().getData() for x in cellHandles if x().cellHandle is not None]            
            self._internalSend(results)
            return results
        finally:
            self.clearUpdate()

    def updateCurrencyClass(self,key,jsonStyle):
        """ update the currency attributes for row or column class """

        #print 'updateCurrencyClass',key
        try:
            self.beginCellUpdate()
            self._internalSetStyle(key,jsonStyle)
            id = key[0].lower()
            val = int(key[1:])
            if id == u'c':
                rng = cell.CellRange(val,1,val,Row.getMax())
            elif id == u'r':
                rng = cell.CellRange(1,val,Col.getMax(),val)

            cellHandles = rng.getCellHandles(self.dbsheet)
            results = [x().getData() for x in cellHandles if x().cellHandle is not None]                        
            self._internalSend(results)            
            self.sendEvent(self.clientID,'currentsheet.onUpdateStyleClass',
                           key,jsonStyle)
        finally:
            self.clearUpdate()
        
    def removeStyleRegion(self,rect,proplist):
        """clear a single style value from a region of cells"""
        #print 'removeStyleRegion',rect,proplist
        # update the database
        self._updateAllStyleCells(rect,proplist,True)
        # update clients
        self.sendEvent(self.clientID,'currentsheet.onRemoveStyleRegion',rect,proplist)

    def updateStyleCells(self,styleCells):
        """ update the style attributes on a range of cells (usually because of undo)
        this blows away any previous style information
        """
        sht = self.dbsheet()
        for val in styleCells:
            scell = simplecell(val)
            sht.getCellHandle(scell.col,scell.row)().setFormat(scell.format)
        
        self.sendEvent(self.clientID,'currentsheet.onUpdateStyleCells',styleCells)
        

    def sendEmailInvite(self,target):
        #print 'sendEmailInvite',target,self.ownURL
        if not validEmail(target):
            return {u'error':u'badaddress'}
        try:
            invitees = set([target.encode('utf-8')])
            self.sess.principal.inviteToSheet(self.dbsheet().sheetDbId,invitees,self.rootURL)
            return {u'error':u'none'}
        except exc.SelfInviteException:
            return {u'error':u'selfinvite'}
        except exc.DuplicateInviteException:
            return {u'error':u'duplicate'}


class UserNameFragment(rend.Fragment):

    def userName(self,ctx,data):
        username = SheetCookieHandler(inevow.IRequest(ctx)).username
        #print 'UserName is:',username
        if username:
            return username
        else:
            return ''

    docFactory = loaders.stan(
            T.div(id='sheetuser')[
            T.div(_class='label')['Your user name'],
            T.input(type='text',id='sheetusernick',_class='sheettext',value=userName,name='sheetuser'),
            T.div(_class='example')['example: Bob']
            ]
    )



class SheetCredPage(NumblerTemplatePage):
    xmlcontent = 'sheetcred.xml'
    title = 'Numbler user name required'

    def __init__(self,targetsheet):
        super(SheetCredPage,self).__init__()        
        self.target = targetsheet

    def render_form(self,ctx,data):
        sess = inevow.ISession(ctx)
        request = inevow.IRequest(ctx)

        if ctx.arg('sheetuser'):
            sess.username = ctx.arg('sheetuser')
            handler = SheetCookieHandler(request)
            handler.updateUserName(sess.username)
            handler.addNewSheet(self.target)
            request.redirect(request.URLPath())
            request.finish()
        else:
            return UserNameFragment

    def render_loginfragment(self,ctx,data):
        return account_pages.AccountLoginFragment(showmessage='welcomepublic',continueURL=inevow.IRequest(ctx).URLPath())


## DisplayOlderSheets is obsolete I think
## 

class DisplayOlderSheets(NumblerTemplatePage):
    xmlcontent = 'oldersheets.xml'
    title = 'Older Numbler spreadsheets'


    def render_showallsheets(self,ctx,data):
        request = inevow.IRequest(ctx)
        handler = SheetCookieHandler(request)
        recentPages,namedict = handler.recentSheets()
        return T.div(id='recentresults')[
                [T.div[T.a(href=request.URLPath().parentdir().child(item))[
                namedict[item]]] for item in recentPages if namedict.has_key(item)]
                ]



class SignInFragment(rend.Fragment):
    docFactory = loaders.xmlfile('signinfragment.xml',templateDir='templates')

################################################################################
## RootFragment
##
## renders the main page content
################################################################################        

class RootPageFragment(rend.Fragment):

    docFactory = loaders.xmlfile('mainpage.xml',templateDir='templates')

    def render_loginbar(self,ctx,data):
        sess = inevow.ISession(ctx)
        if hasattr(sess,'principal'):
            return account_pages.MainPageAuthUserFragment(sess.principal)
        else:
            return account_pages.AccountLoginFragment(showmessage='welcome')

    def render_signin(self,ctx,data):
        sess = inevow.ISession(ctx)
        if hasattr(sess,'principal'):
            return ''
        else:
            return SignInFragment

    def render_sheetuser(self,ctx,data):
        username = SheetCookieHandler(inevow.IRequest(ctx)).username
        if username:
            ctx.fillSlots('name',username)
            return ctx.tag
        else:
            ctx.fillSlots('name','')
            return ctx.tag
        
    
    def render_existingsheets(self,ctx,data):
        request = inevow.IRequest(ctx)
        handler = SheetCookieHandler(request)
        recentPages,namedict = handler.recentSheets()
        if recentPages:
            knownpages = [item for item in recentPages if namedict.has_key(item)]

            def show_existing():
                if len(knownpages) > 5:
                    return T.div[T.a(href=url.here.child('oldersheets'))['older spreadsheets...']]
                return ''
            
            ret = T.div(id='recentresults')[
                [T.div[T.a(href=url.here.child(item))[
                namedict[item]]] for item in knownpages[0:5]],
                show_existing()
                ]
            return ret
        else:
            return T.div(id='recentresults')



################################################################################
## SheetRootPage
################################################################################                                

class SheetRootPage(NumblerTemplatePageBase,rend.Page):
    child_mochikit = NumblerFile('./mochikit',defaultType='text/javascript')
    child_MochiKit = NumblerFile('./MochiKit',defaultType='text/javascript')
    child_css = NumblerFile('./css',defaultType='text/plain')
    child_js = NumblerFile('./js',defaultType='text/javascript')
    child_LiveSheet = NumblerFile('./js',defaultType='text/javascript')
    child_lib = NumblerFile('./js',defaultType='text/javascript')
    child_img = NumblerFile('./img')
    child_dojo = NumblerFile('./dojo',defaultType='text/javascript')
    child_static = NumblerFile('./static',defaultType='text/html')
    child_jstests = NumblerFile('./js/tests',defaultType='text/html')


    addSlash = True
    handleBadLinks = BadLinkPage()
    handleSiteErrors = ErrorPage()
    apiErrors = ApiErrorPage()

    # child dictory that maps URLs to page objects
    children = dict(
        simport=sheetimport.SheetImport(),
        oldersheets=DisplayOlderSheets(),
        About=AboutPage(),
        support=SupportPage(),
        logout=account_pages.accountLogout(),
        accessdenied=AccessDenied(),
        apidoc=apimanager.APIManager(),
        functiondoc=FunctionDocPage(),
        wsresponse=wsResponseManager()
    )


    fdb = fdb.FDB.getInstance()
    eng = engine.Engine.getInstance()
    sinstance = ssdb.getInstance()
    eng.ssdb.log = None # turn off db logging

    def __init__(self):
        # here to avoid constructor in NumblerTemplatePageBase
        pass

    def beforeRender(self,ctx):
        req = inevow.IRequest(ctx)
        chandler = SheetCookieHandler(req)
        if chandler.oldrecent:
            req.redirect('/accupgrade')
            req.finish()
            return
    

    def render_content(self,ctx,data):
        return RootPageFragment

    def render_title(self,ctx,data):
        return 'Welcome to Numbler'

    ## end rendering stuff


    def child_procimport(self,ctx):
        sess = inevow.ISession(ctx)
        if hasattr(sess,'procImport'):
            return sess.procImport
        else:
            return sheetimport.ProcessSheetImport(inevow.ISession(ctx))

    def child_accountlogin(self,ctx):
        return account_pages.AccountLoginPage()

    def child_myaccount(self,ctx):
        return account_pages.MyAccountPage()

    def child_createaccount(self,ctx):
        return account_pages.CreateAccountPage()

    def child_resetpasswd(self,ctx):
        return account_pages.ResetPassword()

    def child_verifyaccount(self,ctx):
        return account_pages.VerifyPage()

    def child_changepass(self,ctx):
        return account_pages.NewPasswordPage()

    def child_getAPIid(self,ctx):
        return account_pages.getAPIID()

    def child_accupgrade(self,ctx):
        return account_pages.upgradeToAccountsPage()

    #athenaModules = athena.JSPackage(
    def child_athenajs(self,ctx):
        return athena.JSModules(athena.jsDeps.mapping)

    def child_myaccountsettings(self,ctx):
        return account_pages.ModifyAccountPage()

    def locateChild(self, ctx, segments):
        req = inevow.IRequest(ctx)
        senthost = req.getAllHeaders().get('host')
        if senthost and senthost == 'www.numbler.com':
            # if they have an old cookie... well let them use the site the old
            # way.  this way we won't loose their sheets
            if not req.getCookie('recent'):
                cpath = req.URLPath()
                newurl = url.URL(cpath.scheme,'numbler.com',segments,cpath._querylist)
                return newurl,()


        ctx.remember(self.handleBadLinks,inevow.ICanHandleNotFound)
        ctx.remember(self.handleSiteErrors,inevow.ICanHandleException)        
        seglen = len(segments)
        #print 'locateChild',segments
        # algorithm.
        #
        # step 1: see if we are dealing with a sheet (a 16 digit UID)
        # step 2: if so AND that is the end of the URL check it's validity (is this right?)
        # step 3: check the username
        # step 4: if a sheet and that's the end of the URL get/create the factory.
        # return a new livepage instance.b
        # step 5: if a sheet and the sheet is not the end of the URL, get the factory
        # step 6: check if the next segment is in the factory. if so, return that sheet
        # if not, return rend.NotFound (necessary if you get a request for a livepage transport
        # after a sheet has disconnected.

        # step 1
        try:
            if len(segments[0]) == 16:
                sheetUID = segments[0]
                if seglen == 1: #step 2
                    if not ssdb.getInstance().sheetExists(sheetUID):
                        # we used to redirect here but I couldn't figure out
                        # how to get it work with locate child.  the problem
                        # was returning the right arguments so the request would go to the
                        # root
                        return rend.NotFound

                    shtH = SheetHandle.getInstance(sheetUID)
                    
                    sess = inevow.ISession(ctx)
                    principalExists = hasattr(sess,'principal')
                    handler = SheetCookieHandler(req)
                    username = None
                    if shtH().authRequired():
                        if not principalExists:
                            return account_pages.AccountLoginPage(True),segments[1:]
                        else:
                            try:
                                sess.principal.checkCanAccess(sheetUID)
                                username = sess.principal.displayname
                            except exc.AccessDenied:
                                return AccessDenied(),segments[1:]
                    else:
                        if principalExists:
                            username = sess.principal.displayname
                        else:
                            # always go to the cred page so the user has the option to log in
                            # or change there username
                            if not hasattr(sess,'username'):
                                return SheetCredPage(sheetUID),segments[1:]
                            else:
                                username = sess.username
                                # delete the session user so people need to go back to sheetcredpage
                                del sess.username

                            
                    # step 4
                    
                    factory = self.fdb.get(sheetUID)
                    if not factory:
                        factory = self.fdb[sheetUID] = SheetFactory(sheetUID)

                    # modify the recent cookies to make sure this sheet goes to the top
                    handler.touchRecent(sheetUID)
                    return LiveSheetPage(factory,ctx,username),segments[1:]
                else:
                    if seglen >= 2:
                        if segments[1] == 'export':
                            return ExportPage(segments[0]),segments[2:]
                        elif segments[1] == 'API':
                            ctx.remember(self.apiErrors,inevow.ICanHandleException)
                            return webservices.NumblerAPI(segments[0],segments[2:]),segments[2:]
                            
                    # step 5:
                    factory = self.fdb.get(sheetUID)
                    if not factory:
                        # this works for now because we expect someone to hit the parent
                        # URL first.  however, for web services we need to rethink this.
                        return rend.NotFound
                    # step 6:
                    try:
                        client = factory.getClient(segments[1])
                    except KeyError:
                        #print '*** request for livepage client not in factory, passing up'
                        return super(SheetRootPage,self).locateChild(ctx,segments[1:])
                    else:
                        return client, segments[2:]

            return rend.Page.locateChild(self,ctx,segments)
            #return super(SheetRootPage,self).locateChild(ctx,segments)
        except:
            print 'exception caught!'
            traceback.print_tb(sys.exc_info()[2])
            traceback.print_stack()            
            return self.handleSiteErrors,segments[1:]


# singleton site for right now
def createResource():
    return SheetRootPage()



