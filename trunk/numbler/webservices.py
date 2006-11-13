# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.
#
# manages the REST based web service API
#

from nevow import rend, loaders, appserver,static,guard,inevow,url,flat,stan,util
from nevow.util import escapeToXML
from nevow.inevow import ISession,IRequest
from numbler.server import sheet,engine,cell,ast
from numbler.server.colrow import Col,Row
from numbler.server.exc import *
from twisted.internet import defer,threads,reactor
from twisted.internet.defer import deferredGenerator,waitForDeferred
from numbler.utils import yieldDef,cellDepFlattener
import traceback,sys
import math

from xml.sax import handler,parseString,make_parser

class NumblerAPI(rend.Page):
    docFactory = loaders.xmlfile('apitemplatesmall.xml',templateDir='templates')
    errFactory = loaders.xmlfile('apierror.xml',templateDir='templates')
    
    #docFactory = loaders.xmlfile('apitemplate.xml',templateDir='templates')    
    sheetpattern =inevow.IQ(docFactory).patternGenerator("sheet")
    sheetchanged = inevow.IQ(docFactory).patternGenerator("sheetchanged")
    cellpattern =inevow.IQ(docFactory).patternGenerator("cell")
    errPattern = inevow.IQ(errFactory).patternGenerator("error")
    
    def __init__(self,sheetUID,url):
        self.sheetUID = sheetUID
        self.url = url
        self.eng = engine.Engine.getInstance()
        
    def locateChild(self,ctx,segments):
        self.url = segments
        return self,[]

    def authenticate(self,req,id):
        """
        authenticate a request against this sheet
        """
        # get the authorization information from the headers
        headers = req.received_headers
        auth = headers.get('authorization')
        if not auth:
            raise AuthRequired(req.path)

        api_id,hash = auth[auth.find(' ')+1:].split(':')
        self.principal = self.eng.ssdb.resolveApi(api_id)
        self.principal.checkCanAccess(id)

        # verify the message was signed with the secret key
        self.principal.verifymessage(hash,req.method,req.path,headers)

    def handleException(self,e,request):
        """
        handle an exception and send the appropriate response
        back to the client
        """
        
        self.docFactory = self.errFactory
        self.exp = e
        request.setResponseCode(e.httpcode)
        
        
    def render_error(self,ctx,data):
        #self.request.write('<?xml version="1.0" encoding="utf-8"?>\n')        
        return ctx.tag[self.errPattern()]

    def render_internalerror(self,ctx,data):
        ctx.fillSlots('code',self.exp.code)

        if hasattr(self.exp,'message'):
            msg = self.exp.message
        else:
            msg = self.exp.__doc__
        
        ctx.fillSlots('message',msg)
        ctx.fillSlots('resource',self.exp.res)
        return ctx.tag

    def beforeRender(self,ctx):
        req = inevow.IRequest(ctx)
        req.args['showerr'] = 1

        req.setHeader("Content-Type", "text/xml; charset=UTF-8")


        getres = ctx.arg('recvResults')
        # set a flag if the user wants results
        self.wantresults = not (getres is not None and int(getres) == 0)

        if not self.eng.ssdb.getInstance().sheetExists(self.sheetUID):
            e = SheetNotFound()
            e.res = req.path
            self.handleException(e,req)
            return

        self.sheetH = sheet.SheetHandle.getInstance(self.sheetUID)
        e = None
        if self.sheetH().authRequired():
            try:
                # make sure the user is authorized to view this sheet.
                self.authenticate(req,self.sheetH.sheetId)

            except AccessDenied,e:
                #print 'Access Denied:',self.principal.sheets,self.principal.ownedsheets
                self.handleException(e,req)
            except AuthRequired,e:
                self.handleException(e,req)                
            except InvalidSignature,e:
                # set the uri of the request
                e.res = req.path
                self.handleException(e,req)
            except AccountNotFound,e:
                # set the uri of the request                
                e.res = req.path
                self.handleException(e,req)
            except DeleteSheetException,e:
                e.res = req.path
                self.handleException(e,req)                
            except Exception,e:
                traceback.print_tb(sys.exc_info()[2])                
                raise e

        if e is not None:
            return

        self.sheetH = sheet.SheetHandle.getInstance(self.sheetUID)
        # assume the last argument is a cell reference
        self.sheetH.attach(self)
        self.updates = set()

        # save of the request object for right now because
        # it is used by the error handler
        self.request = req
        
        if req.method == "PUT":
            # the input processing runs in a seperate thread because this could
            # be a lot of data.  the actual additions to cells must
            # run in the main thread.
            d = threads.deferToThread(self.handlePUT,req.content)
            d.addCallback(self.processNewCells)#,self.handleErr)
            d.addErrback(self.handleErr)
            d.addBoth(self.donewithrequest)
        elif req.method == "GET":
            d = defer.Deferred()
            d.addCallback(self.processGET)
            d.addErrback(self.handleErr)
            d.addBoth(self.donewithrequest)
            reactor.callLater(0,d.callback,None)
        elif req.method =="DELETE":
            d = defer.Deferred()
            d.addCallback(self.processDELETE)
            d.addErrback(self.handleErr)
            d.addBoth(self.donewithrequest)
            reactor.callLater(0,d.callback,None)            
        return d

    def handleErr(self,arg):
        # arg is a Failure instance
        #print '** handleErr called ***',arg
        if isinstance(arg.value,(ParseException,DeleteSheetException)):
            self.handleException(arg.value,self.request)
        elif isinstance(arg.value,SSError):
            e = GeneralWebSvcException()
            e.message = ' '.join([unicode(str(arg.value)),unicode(len(arg.value.args) > 0 and arg.value.args[0]
                                                      or 'unknown error')])
            self.handleException(e,self.request)            
        else:
            #print '** handleErr called ***',arg
            self.handleException(GeneralWebSvcException(),self.request)
        return arg

    def processNewCells(self,arg):
        # the parser supports multiple sheets but we don't currently
        # support more than one via the api right now.
        # pull out the first sheet and iterate through that.
        sheet = self.handler.sheets[self.handler.sheets.keys()[0]]
        d = defer.Deferred()
        if len(sheet) <= 500:
            d.addCallback(self.normalCellUpdate)
        else:
            d.addCallback(self.bulkCellUpdate)
        reactor.callLater(0,d.callback,sheet)
        return d


    @deferredGenerator
    def normalCellUpdate(self,sheet):
        """
        process all the cells.  since web services requests have low
        priority we will all the requests through the deferred generator
        to make sure any other user requests get processed when they come in.
        """
        ndict = {}
        i = 0
        ownerlocale = self.sheetH().ownerPrincipal.locale
        for col,row,formula in sheet:
            i = i + 1
            self.sheetH().getCellHandle(Col(col),Row(row))().setFormula(formula,ownerlocale,
                                                                        notify=False,notifyDict = ndict)
            if i % 10 == 0:
                yield waitForDeferred(yieldDef())
                
        # notify in batch
        for sheetHandle in ndict:
            sheetHandle.notify(ndict[sheetHandle])
            yield waitForDeferred(yieldDef())

        # convert cell handles to cells. we only want the ones that have a valid formula
        self.updates = (x for x in self.updates if len(x().formula) != 0)        

    def runclosure(self,arg):
        """
        run the closure returned by the ssdb layer. this must
        run in the main thread because we don't have locks around
        the various MRUdicts
        """
        arg()

    def logSqlError(self,arg):
        print 'bulkCellUpdate: SQL error',arg
        self.bulkLoadError = True

    @deferredGenerator    
    def bulkCellUpdate(self,sheet):
        """
        bulk cell update is similar to the functionality in the gnumeric or XLS importers
        except that it focuses only on the formula data rather than styles or dimension info
        """

        # force the response into want results mode
        self.wantresults = False

        # batch stuff up into 1000 cell updates
        chunksize = 2000
        cells = len(sheet)
        chunkcount = math.ceil(float(cells) / chunksize)

        def getIterator(start):
            return ((Col(x[0]),Row(x[1]),u'',x[2]) for x in sheet[start:start+chunksize])        

        print 'saving %d chunks' % (chunkcount)
        startcount = 0
        handle = self.sheetH
        ownerlocale = handle().ownerPrincipal.locale
        for i in range(0,int(chunkcount)):
            print 'chunk %d: saving cells' % (i)
            self.bulkLoadError = False
            d = self.eng.ssdb.bulkLoadCells(str(handle),getIterator(startcount))
            d.addCallbacks(self.runclosure,self.logSqlError)
            yield waitForDeferred(d)
            # check that we didn't encounter a bulk load error.
            if self.bulkLoadError:
                raise 'bulk load error'
            
            cell.Cell.bulkLoadCells(handle,getIterator(startcount))
            print 'chunk %d: loading cells' % (i)            
            yield waitForDeferred(yieldDef())

            allcelldeps = []
            allrangedeps = []
            # create cells
            yieldcount = 0
            print 'chunk %d: getting dependencies' % (i)                        
            for colID,rowID,style,formula in getIterator(startcount):
                yieldcount += 1
                cellH = handle().getCellHandle(colID,rowID)
                cellH().setFormulaFromDb(formula,ownerlocale)
                # generate the dependencies for persistance later.
                celldeps,rangedeps = cellH().bulkGetDeps()
                if celldeps:
                    allcelldeps.append(celldeps)
                if rangedeps:
                    allrangedeps.append(rangedeps)
                if yieldcount % 100 == 0:
                    yield waitForDeferred(yieldDef())
                

            print 'chunk %d: saving dependencies' % (i)                                    
            # bulk load the cell dependencies
            if len(allcelldeps) > 0:
                yield waitForDeferred(eng.ssdb.bulkSetDeps(cellDepFlattener(allcelldeps)).addErrback(self.logSqlError))
            if len(allrangedeps) > 0:
                yield waitForDeferred(end.ssdb.bulkSetRangeDeps(cellDepFlattener(allrangedeps)).addErrback(self.logSqlError))
                                  
            startcount += chunksize

        # mark the number of cells processed
        self.finalcellcount = len(sheet) 

    def processGET(self,arg):
        """
        process a get request
        """

        if len(self.url) == 0:
            # user wants entire sheet
            # return iterator of cell instances if they have a valid formula
            self.updates = (x for x in self.sheetH().safeGetCellHandleIter() if len(x().formula) != 0)
        elif self.url[-1].find('-') > 0:
            # cell range

            # somewhat of a hack - make a fake formula to trick the parser into parsing the range.
            tempformula = 'SUM(%s:%s)' % tuple(self.url[-1].split('-'))
            formula = self.eng.parser.parse(self.sheetH,tempformula,self.sheetH().ownerPrincipal.locale.dectype)
            targetrng = formula.args[0]
            if not isinstance(targetrng,ast.RangeMixin):
                raise "didn't find a range"
            self.updates = targetrng.formulaOnlyCells()

        else:
            # single cell
            parseval = self.eng.parser.parse(self.sheetH,self.url[-1],self.sheetH().ownerPrincipal.locale.dectype)
            cellH = self.sheetH().getCellHandle(parseval.getCol(),parseval.getRow())
            self.updates = set([cellH])

    def processDELETE(self,arg):
        if len(self.url) == 0:
            # return an error: can't delete entire sheet
            # raise an error: can't delete sheet
            e = DeleteSheetException()
            e.res = self.request.path
            raise e
        elif self.url[-1].find('-') > 0:
            # cell range
            tempformula = 'SUM(%s:%s)' % tuple(self.url[-1].split('-'))
            formula = self.eng.parser.parse(self.sheetH,tempformula,self.sheetH().ownerPrincipal.locale.dectype)
            targetrng = formula.args[0]
            if not isinstance(targetrng,ast.RangeMixin):
                raise "didn't find a range"
            return self.sheetH().deleteCellHandleArray(targetrng.getCellRange().getCellHandles(self.sheetH),selfNotify=True)
        
        else:
            # single cell
            parseval = self.eng.parser.parse(self.sheetH,self.url[-1],self.sheetH().ownerPrincipal.locale.dectype)
            cellH = self.sheetH().getCellHandle(parseval.getCol(),parseval.getRow())
            self.sheetH().deleteCell(cellH)
            
    def donewithrequest(self,arg):
        # detach
        #print 'done with requested called',arg,type(arg)
        self.sheetH.detach(self)
    
    def update(self,*args,**kwargs):
        """ called by the sheet engine """
        self.updates.update(args[1])

    @deferredGenerator
    def render_sheet(self,ctx,data):
        """
        render all the cells in the sheet, occasionally pausing the yield to the reactor
        """
        
        ctx.fillSlots('guid',str(self.sheetH))
        ctx.fillSlots('name',self.sheetH().getAlias())
        #print '*** rendering cells for sheet ****',list(self.updates)

        ret = []
        count = 1
        for cellH in self.updates:
            if count % 10 == 0:
                yield waitForDeferred(yieldDef())
            count = count + 1
            ret.append(self.cellpattern(data=cellH))
        yield ctx.tag[ret]

    def render_sheetchanged(self,ctx,data):
        ctx.fillSlots('guid',str(self.sheetH))
        ctx.fillSlots('name',self.sheetH().getAlias())

        # finalcellcount is generated by the bulk cell loader
        finalcount = getattr(self,'finalcellcount',None)
        if finalcount:
            ctx.fillSlots('changedCells',finalcount)            
        else:
            ctx.fillSlots('changedCells',len(list(self.updates)))
        return ctx.tag
            
    def render_cell(self,ctx,data):
        cellH = data
        ctx.fillSlots('col',cellH.col)
        ctx.fillSlots('row',cellH.row)
        cellI = cellH()
        ctx.fillSlots('formula',escapeToXML(cellI.getFormula(),True))

        value = cellI.getValue()
        if isinstance(value,SSError):
            value = ' '.join([unicode(str(value)),unicode(len(value.args) > 0 and value.args[0]
                                                      or 'unknown error')])
        
        if type(value) is str:
            ctx.fillSlots('value',escapeToXML(value,True))
        else:
            ctx.fillSlots('value',value)
 
        return ctx.tag

    def render_content(self,ctx):
        #self.request.write('<?xml version="1.0" encoding="utf-8"?>\n')
        if self.wantresults:
            return self.sheetpattern(data=None)
        else:
            return self.sheetchanged(data=None)
        
    def handlePUT(self,filelike):
        self.handler = XmlPostHandler()
        self.handler.doparse(filelike)


    


class XmlPostHandler(handler.ContentHandler):
    """
    parse a web service request
    sample:
    <xml>
    <sheet guid="asdfasdfasdfasfd">
    <cell col="1" row="1" formula="23"/>
    </sheet>
    </xml>

    """
    
    def __init__(self):

        self.sheets = {}
        self.currentsheet = None

    def doparse(self,data):
        parser = make_parser()
        parser.setContentHandler(self)
        parser.parse(data)

    def startElement(self,name,attrs):
        lstr = name.lower()
        if lstr == 'sheet':
            guid = attrs.get('guid')
            if not guid:
                raise ParseException("guid")
            self.currentsheet = []
            self.sheets[guid] = self.currentsheet
        elif lstr == 'cell' and self.currentsheet is not None:
            col = attrs.get('col')
            row = attrs.get('row')
            formula = attrs.get('formula')
            if col is None:
                raise ParseException("col")                
            if row is None:
                raise ParseException("row")
            if formula is None:
                raise ParseException("formula")                

            if type(formula) is unicode:
                formula = formula.encode('utf-8')
            self.currentsheet.append((col,int(row),formula))

    def endElement(self,name):
        pass

    
