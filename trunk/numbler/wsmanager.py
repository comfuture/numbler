# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.
#
# manager classes for outbound web services calls (amazon, ebay)
#

from nevow import inevow
from zope.interface import Interface,implements
from numbler.server.sslib import singletonmixin

from xml.dom.minidom import parse
from xml import xpath

from numbler.wsproxy import tags as wstags,ProxyClient,xmlResponseHandler
from numbler.server.exc import *
from nevow.flat import flatten
from pkg_resources import resource_filename
import os
from numbler.server import engine
from datetime import datetime,timedelta
from twisted.internet import defer,reactor
from nevow import inevow
from numbler.server import fdb

class wsResponseManager(object):
    """
    Manages a callback from a remote web service.
    """
    
    implements(inevow.IResource)


    def locateChild(self,ctx,segments):
        return None,()

    def errHandler(self,arg):
        #print 'wsResponseManager: error on handling transaction callback',arg
        return arg

    def renderHTTP(self,ctx):
        req = inevow.IRequest(ctx)
        handler = xmlResponseHandler()

        try:
            handler.doparse(req.content)
            # iterate through all the requests
            for aResponse in handler.requests:
                if aResponse.status == 200:
                    d = globalTxnMgr.resolveTxn(int(aResponse.id))
                    d.addErrback(self.errHandler)
                    #d.callback(aResponse.params)
                    reactor.callLater(0,d.callback,aResponse)
                else:
                    d = globalTxnMgr.resolveTxn(int(aResponse.id))
                    #d.errback(aResponse)
                    reactor.callLater(0,d.errback,aResponse)
                    
        except RemoteWsTxnNotFound:
            # TODO: put better logging code here
            print 'Transaction not found'
        except RemoteWsTxnExpired:
            pass
        except Exception,e:
            print 'error parsing response',e        
        return ''

class wsServiceManager(singletonmixin.Singleton):
    """
    Manage all the web services known to the system.
    
    """

    def __init__(self):
        """
        load all of the service definitions on the system.
        """
        self.services = {}

        svcdir = resource_filename('numbler','remoteServices')
        files = os.listdir(svcdir)
        for fname in [os.sep.join([svcdir,x]) for x in files if x[-4:] == '.xml']:
            doc = parse(fname)
            servicedef = wsDefinition.createInstance(doc)
            self.services[servicedef.name] = servicedef
        self.ssdb = engine.Engine.getInstance().ssdb
        

    def configureServer(self,hostname,callbackResource=None,port=80,sslport=443):
        """
        configure information necessary to generate the callbackURI.  This method
        should be called from a tac file.
        """
        
        self.hostname = hostname
        self.callbackRes = callbackResource
        if self.callbackRes is None:
            self.callbackRes = '/wsresponse'
        self.port = port
        self.sslport = sslport

        self.fullURI = 'http://%s:%s%s' % (self.hostname,self.port,self.callbackRes)

    def lookupService(self,name):
        """
        resolve a service based on its name
        """
        svcdef = self.services.get(name)
        if not svcdef:
            raise wsServiceNotFound(name)
        return svcdef

    def generateTxnRequest(self,name,txnid,*args,**kwargs):
        """
        Generate a request to a web service.

        @return: deferred

        a deferred that is fired when the request is
        sent.  Note that is won't give you the result of the call, but will
        will either complete succesfully indicating the message was sent
        OR will errback if the parameters are not correct or the service
        is not available.
        """        
        svc = self.lookupService(name)

        msg = svc.createMessage(txnid,self.fullURI,*args,**kwargs)

        host,port,resource = svc.hostinfo

        
        pclient = ProxyClient(host.encode('ascii'),int(port),resource.encode('ascii'),msg.encode('ascii'))
        ondonDeferred,cancelable = pclient.connect()
        return cancelable


        

    def generateRequest(self,name,*args,**kwargs):
        """
        Utility function for generating a request and supplying a txn ID at the same time.

        @return: deferred, txn_id

        a deferred that is fired when the request is
        sent.  Note that is won't give you the result of the call, but will
        will either complete succesfully indicating the message was sent
        OR will errback if the parameters are not correct or the service
        is not available.
        """
        txnid = GlobalTxnManager.getInstance().getTxnId()
        return self.generateTxnRequest(name,txnid,*args,**kwargs),txnid
    


class wsDefinition(object):
    """
    The web service definition object.  This class is responsible
    for a single web service and can be used to validate and generate
    the correct XML that should be sent to the service.

    @ivar name: the name of the web service
    @ivar desc: a description of the service (for end user consumption)
    @ivar hostinfo: tuple of host name, port number, and resource used to access the service
    @ivar params: a list of parameters that define the service.
    @ivar outputs: a list of expected output values
    
    """

    def createInstance(cls,domrep):
        """
        create an instance of the definition from a DOM tree.
        """
        newdef = wsDefinition()
        try:
            newdef.name = xpath.Evaluate('/servicedef/@name',domrep)[0].value
        except:
            raise Exception('mssing name on service definition')

        try:
            newdef.desc = xpath.Evaluate('/servicedef/@desc',domrep)[0].value
        except:
            raise Exception('missing description on service definition')

        try:
            conNode = xpath.Evaluate('/servicedef/connection',domrep)[0]
            newdef.hostinfo = conNode.getAttribute('host'),conNode.getAttribute('port'),conNode.getAttribute('resource')
        except:
            raise Exception('missing or malformed connection information')

        try:
            refresh = xpath.Evaluate('/servicedef/refreshInterval',domrep)[0]
            cls.__runinterval = int(refresh.childNodes[0].nodeValue)
        except Exception,e:
            print 'warning: refresh interval not specified, using default',e
            
            
        newdef.reqprops = [x.getAttribute('name') for x in
                         xpath.Evaluate('/servicedef/params/inputs/param',domrep)
                         if x.getAttribute('required').lower() == 'true']
        newdef.optprops = [x.getAttribute('name') for x in
                         xpath.Evaluate('/servicedef/params/inputs/param',domrep)
                         if x.getAttribute('required').lower() == 'false']
        newdef.params = newdef.reqprops + newdef.optprops
        newdef.paramdict = dict([(x,True) for x in newdef.reqprops])
        newdef.paramdict.update(dict([(x,False) for x in newdef.optprops]))

        newdef.outputs = []
        # outCalcName indicates which value should be interpreted as the
        # formula value
        newdef.outCalcName,newdef.outLinkName = None,None
        for outparam in xpath.Evaluate('/servicedef/params/outputs/param',domrep):
            outname = outparam.attributes.get('name')
            if not outname:
                raise Exception('name missing on output parameter')
            outname = outname.nodeValue
            newdef.outputs.append(outname)
            if outparam.attributes.get('calcValue'):
                newdef.outCalcName = outname
            if outparam.attributes.get('link'):
                newdef.outLinkName = outname

        if len(newdef.outputs) == 0:
            raise Exception('missing outputs')                
        if newdef.outCalcName is None:
            raise Exception('no output properties marked as the calcValue')
        return newdef
        
    createInstance = classmethod(createInstance)

    __runinterval = 86400
    runinterval = property(lambda self: self.__runinterval)

    def createMessage(self,txn_id,callbackURI,*args,**kwargs):
        """
        create a new web service message using the service definition.

        pass in either args or kwargs but not both.
        """
        if len(args) and len(kwargs):
            raise Exception("pass in either args or kwargs but not both")
        if len(kwargs):
            raise NotImplementedError()        
        else:
            if len(args) < len(self.reqprops):
                raise wsNotEnoughArguments()
        
        stantree = wstags.transaction(callbackURI=callbackURI)[
            wstags.request(id=txn_id)[
            self._genParams(args)
            ]
            ]
        return flatten(stantree)
                                     

    def _genParams(self,args):
        for index in range(0,len(args)):
            yield wstags.param(name=self.params[index])[args[index]]


    def processResults(self,results):
        """
        results must be a ResponseData instance.

        returns a tuple of the calcValue and the link.  the link is optional
        so that value can be missing.
        
        """

        # TODO: only handle the first response element
        p = results.params
        try:
            calcval = p[self.outCalcName]
        except:
            raise Exception('expected calcValue not found in response')
        linkval = None
        if self.outLinkName is not None:
            try:
                linkval = p[self.outLinkName]
            except:
                raise Exception('missing link value in response')
            return calcval.encode('utf-8'),linkval.encode('utf-8')
        else:
            return calcval.encode('utf-8'),None

    


class FormulaTxnManager(object):
    """
    manages all of the deferred calculations that can take
    place when evaluating a cell's AST.  This class was originally
    designed for use with asynchronous web service calls (the WS function)
    """

    # default transaction timeout.
    __timeout = 30

    def __init__(self,cellHandle):
        self.txnIds = []
        self.defCbList = []
        self.cellHandle = cellHandle
        self.currentdl = None
        self.isAsync = False
        self.futureRunHandle = None

    def setTimeout(self,val): self.__timeout = val
    def getTimeout(self): return self.__timeout
    timeout = property(getTimeout,setTimeout,None,"length of time to wait for transaction to complete")

    def setTimeout(self,value):
        self.transactionTimeout = value

    def registerTxn(self,defCb,txnId):
        """
        register that a deferred function has started to be evaluated.
        """
        self.txnIds.append(txnId)
        self.defCbList.append(defCb)

        # set this isAsync flag if a deferred is registered.
        self.isAsync = True

    def cancelTransactions(self):
        """
        cancel all pending transactions to the remote web service.
        """
        if len(self.txnIds):
            GlobalTxnManager.getInstance().cancelTxns(*self.txnIds)
            self.txnIds = []

    def calcOnFinish(self):
        """
        register a callback to fully calculate the formula
        once all of the dependent deferred results are available.
        """

        if self.defCbList:
            self.currentdl = defer.DeferredList(self.defCbList,fireOnOneErrback=True,consumeErrors=True)
            self.currentdl.addBoth(self._onAstReady)
            #self.currentdl.addCallbacks(self._onAstReady,self._clearCurrentCb)
            self.defCbList = []
            return self.currentdl

    def getPendingDeferred(self):
        return self.currentdl

    def _clearCurrentCb(self,arg):
        self.currentdl = None
        # return the subfailure encapsulated by the deferredList FirstError class
        return arg.value.subFailure

    def _onAstReady(self,arg):
        """
        a callback for handling a fully ready AST tree.

        this will notify the sheet server of a pending change
        and force the recalc of this cell and any cells that depend on it.
        """
        cellI = self.cellHandle()
        # finalize the formatting for this cell
        cellI.deferredFormatCheck()

        try:
            # clear the async bit so that we don't clear the cached value
            # during evaluation the *first* time we evaluate
            self.isAsync = False
            notifyDict = {}
            cellI.notify(notifyDict)
            for sheetHandle in notifyDict:
                sheetHandle.notify(notifyDict[sheetHandle])
        finally:
            self.currentdl = None
            self.isAsync = True

        return arg

    def cancelFutureRun(self):
        """
        cancel any outstanding callLater's that are running
        to refresh the data.
        """
        
        if self.futureRunHandle:
            if self.futureRunHandle.active():
                self.futureRunHandle.cancel()
            self.futureRunHandle = None
        

    def scheduleFutureRun(self,nextrun,cleanupFunc):
        """
        Schedule the formula to be re-evaluated in the future.  this is done
        because the data at the end of the web service could be out of date.

        The refresh criteria is specific to the web service that in use.

        @nextrun: next run in seconds 
        """

        # don't do this if refreshasync is turned off
        if not globalTxnMgr.refreshasync:
            return
        
        self.cancelFutureRun()
        self.futureRunHandle = reactor.callLater(nextrun,self._doFutureRun,cleanupFunc)
        

    def _doFutureRun(self,cleanupFunc):
        """
        refresh a formula.  The sheet cache is checked to make sure that
        users are still connected to the sheet (in order to avoid an unecessary load)
        
        """

        # note: we always purge old data regardless if a user is connected or not.
        cellI = self.cellHandle()
        try:
            cleanupFunc()
            cellI._val = None  # fixme: this should be a method
        except Exception,e:
            pass
        
        finstance = fdb.FDB.getInstance()
        existing = finstance.get(str(self.cellHandle.sheetHandle))
        # only do the run if clients are connected.
        if existing is not None and len(existing.clients):
            value = cellI.getValue(1)
            


class GlobalTxnManager(singletonmixin.Singleton):
    """
    responsible for managing web service transactions
    """

    __refreshAsyncFunctions = True

    def __init__(self):
        self.idstart = 0
        self.idend = 0
        self.transactions = {}

    def setAsyncRefresh(self,val): self.__refreshAsyncFunctions = val
    refreshasync = property(lambda self: self.__refreshAsyncFunctions,setAsyncRefresh)
    

    def getTxnId(self):
        """
        get a transaction ID.  This ID doesn't mean
        anything besides it is a unique ID opaque ID in the
        Numbler system.
        """
        if self.idstart == self.idend:
            # need to get a new id range.
            self.idstart,self.idend = engine.Engine.getInstance().ssdb.getTxnIdRange()
        ret = self.idstart
        self.idstart += 1
        return ret

    def recordTxn(self,txnId,defCb,timeout=30):
        """
        register a transaction ID and a deferred that will be fired
        when the transaction completes.  Once the deferred is fired
        the transaction manager will remove the transaction from the system.
        """
        self.transactions[txnId] = (datetime.utcnow() + timedelta(seconds=timeout),defCb)

        # register a callback to expire the transaction
        expireHandle = reactor.callLater(timeout,self.expireTxn,txnId)
        defCb.addBoth(self._removeTxn,txnId,expireHandle)

    def _removeTxn(self,arg,txnId,expireHandle):
        del self.transactions[txnId]
        # cancel the expiration callback
        if expireHandle.active():
            expireHandle.cancel()
        return arg

    def expireTxn(self,txnId):
        if txnId in self.transactions:
            expiredt,defCb = self.transactions[txnId]
            defCb.errback(RemoteWsTxnExpired(txnId,expiredt))

    def cancelTxns(self,*args):
        """
        forget about one or more transactions.
        """
        for arg in args:
            if arg in self.transactions:
                expiredt,defCb = self.transactions[arg]
                defCb.errback(RemoteWsTxnCancelled())

    def resolveTxn(self,txnId):
        """
        @return: deferred.
        
        lookup a transaction by transaction ID.  if
        the transaction has expired the transaction.
        """
        if txnId in self.transactions:
            expiredt,defCb = self.transactions[txnId]
            if datetime.utcnow() > expiredt:
                # the transaction will be deleted by the errback handler
                expiredExc = RemoteWsTxnExpired(txnId,expiredt)
                defCb.errback(expiredExc)
                raise expiredExc
            return defCb
        else:
            raise RemoteWsTxnNotFound()


globalTxnMgr = GlobalTxnManager.getInstance()
