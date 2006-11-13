# (C) Numbler LLC 2006
# See LICENSE for details.

from astbase import Function
from twisted.python import context
from twisted.internet import defer
from numbler import wsmanager
from numbler.server.exc import *
from numbler.server.localedb import LocaleParser,ParseCtx
from numbler.server.littools import LitNode
from numbler.wsproxy import ResponseData
from nevow import tags as T

__shortmoddesc__ = 'Web Service Functions'

class AsyncFunction(Function):
    """
    Base class for all asynchronous functions, that is functions
    where the result is not immediately available.
    """
    # indicate if your function is asynchronous (see asyncfunction.py)
    isAsync = True

    def __init__(self,*args):
        super(AsyncFunction,self).__init__(*args)
        self.cachedValue = None
        
        #self.dependentFuncs = list(self.getAsyncNodes(1))

    def clearCachedValue(self):
        self.cachedValue = None

    def asyncEval(self,stackvalue):
        """
        kick of an asynchronous evaluation.  this is the meat of an
        asynchronous implementation.

        @return: deferred.
        """
        raise NotImplementedError("implement in your asynchronous implementation")

    def checkArgs(self):
        """
        verify that the correct number of arguments are present.
        """
        raise NotImplementedError("implement in your asnchronous implementation")

    def eval(self,stackvalue):
        stackvalue = stackvalue +1

        if self.cachedValue is not None:
            if isinstance(self.cachedValue,Exception):
                raise self.cachedValue
            else:
                return self.cachedValue

        self.checkArgs(stackvalue)

        # build a list of child asynchronous functions
        self.waitingList = [childNode.asyncEval(stackvalue) for childNode in self.getAsyncNodes(stackvalue)
                            if childNode.checkArgs(stackvalue)]

        # if children exist, wait on them.
        if len(self.waitingList):
            self.waitForChildren(stackvalue,context.get('txnMgr'))
        else:
            #print 'my cached value is ',self.cachedValue,type(self.cachedValue),self.args
            #print 'calling asyncEval',id(self)
            self.asyncEval(stackvalue)

        # fix me: return whatever is the correct value for the
        # service definition
        return 0


class WS(AsyncFunction):
    """
    Runs a remote function or web service request.
    """

    funcdetails = T.p[
        'The WS function is capable of running a number of different remote functions such as ebay price lookup, amazon price lookup, currency conversion, etc. as documented in the web service section.'
        ]

    funcargs = {'varargs':True,'args':[
        ('service',True,'The Name of the web service'),
        ('argument',False,'an argument for the web service')
        ]}
    
    def checkArgs(self,stackvalue):
        """
        verify that the number of arguments available are correct for the service definition.
        """
        arglen = len(self.args)
        if not arglen: 
           raise SSValueError("a service name is required")
        self.svcname = self.args[0].eval(stackvalue)
        try:
            mngr = wsmanager.wsServiceManager.getInstance()
            self.svc = mngr.lookupService(self.svcname)
            # check if there are enough arguments
            if arglen -1  < len(self.svc.reqprops):
                raise WrongNumArgumentsError(self.__class__.__name__)
            
        except wsServiceNotFound:
            raise SSValueError("%s is not a valid service",self.svcname)
        return True

    def waitForChildren(self,stackvalue,txnMgr):
        """
        prepare for an asynchronous evaluation but don't do it
        yet.  This is necessary when you have a child function that
        is asynchronous and you need its results to continue.  However,
        you need some information ahead of time so the transaction manager
        knows that you are out there.
        """
        dl = defer.DeferredList(self.waitingList)
        
        txnId = wsmanager.GlobalTxnManager.getInstance().getTxnId()

        finishdef = defer.Deferred()
        finishdef.addCallback(self.onWsResponse,txnMgr)        
        # registered a deferred with bound to our transaction ID
        # note that is won't be fired until we receive a response from
        # our web service call.
        txnMgr.registerTxn(finishdef,txnId)
        wsmanager.GlobalTxnManager.getInstance().recordTxn(txnId,finishdef,txnMgr.timeout)
        #print 'waitForChildren: waiting on ',self.waitingList
        dl.addCallback(self.onChildEvaluation,stackvalue,txnId)

    def onChildEvaluation(self,arg,stackvalue,txnid):
        """
        invoke the web service. Note: we don't wait for the deferred
        here because we (presumably) have already registered a deferred to
        wait for the transaction id
        """
        #print 'onChildEvaluation called - generating web service request'
        mngr = wsmanager.wsServiceManager.getInstance()
        # reqCon is an IConnector that we can use to cancel the request
        self.reqCon = mngr.generateTxnRequest(self.svcname,txnid,
                                    *[x.eval(stackvalue) for x in self.args[1:]])

    def asyncEval(self,stackvalue,txnMgr=None):
        # get the transaction mgr: FIXME: is this check still necessary?
        if not txnMgr:
            txnMgr = context.get('txnMgr')
            if txnMgr is None:
                raise Exception("txnMgr not found")
        
        # generate the web service request and record the deferred
        # in the transaction manager.  the first argument is skipped because it
        # is the service name.  At this point any child functions that are asynchronous
        # should have already been evaluated.
        mngr = wsmanager.wsServiceManager.getInstance()

        self.reqCon,txnid = mngr.generateRequest(self.svcname,
                            *[y for y in [x.eval(stackvalue) for x in self.args[1:]] if y != ''])

        # the deferred in this case is the one for when the request is initiated.
        # we create another one here that is fired when the response is received from
        # the remote web service.
        
        finishdef = defer.Deferred()
        finishdef.addCallbacks(self.onWsResponse,self.onWsError,callbackArgs=(txnMgr,),errbackArgs=(txnMgr,))
        #finishdef.addCallback(self.onWsResponse,txnMgr)
        #finishdef.addErrback(self.onWsError,txnMgr)
        # register with the cell transaction mgr.
        txnMgr.registerTxn(finishdef,txnid)
        # register with the global transaction mgr.
        wsmanager.GlobalTxnManager.getInstance().recordTxn(txnid,finishdef,txnMgr.timeout)
        return finishdef


    def onWsResponse(self,wsResults,txnMgr):
        """
        get the results back.  erm - what exactly do we do here?
        """
        #print 'onWsResponse called: got from the web service:',wsResults

        # we don't need to outgoing deferred anymore
        self.pendingReq = None
        
        #value = wsResults[wsResults.keys()[0]].encode('utf-8')
        value,dispUrl = self.svc.processResults(wsResults)

        # get the locale through the sheet (yes this is arduous)
        locale = txnMgr.cellHandle().getSheetHandle()().ownerPrincipal.locale

        # parse the value through the literal parser.
        # Note: this duplicates cod from cell.py getNum
        ctx = ParseCtx()
        try:
            parsedval = LocaleParser.getInstance(str(locale)).parse(ctx,value)
            if isinstance(parsedval,LitNode):
                value = parsedval.eval()
            elif type(parsedval) in (float,long,int):
                value = parsedval
            elif type(parsedval) is str:
                value = parsedval.encode('utf-8')
        except LiteralConversionException,e:
            pass
        except RuntimeError,e:
            pass

        if ctx.fmt:
            self.impliesFormatting = unicode(ctx.fmt)

        if dispUrl is not None:
            self.setdisplayinfo({u'url':unicode(dispUrl)})
        
        self.cachedValue = value

        # kick off a recurring transaction which will refresh the value
        txnMgr.scheduleFutureRun(self.svc.runinterval,lambda : self.clearCachedValue())
        
        #print 'cachedValue is',self.cachedValue,id(self)
        return wsResults

    def onWsError(self,failureArg,txnMgr):
        #print 'onWsError called',failureArg

        failureArg.trap(ResponseData,RemoteWsTxnCancelled,RemoteWsTxnExpired)
        responsedata = failureArg.value
        self.cachedValue = None

        if isinstance(responsedata,RemoteWsTxnExpired):
            self.reqCon.disconnect()

        if isinstance(responsedata,RemoteWsTxnCancelled):
            # don't set the cached value
            return None

        if isinstance(responsedata,ResponseData):
            if responsedata.status == 401: self.cachedValue = SSAuth()
        if self.cachedValue is None:
            # the catch all error; timeouts, 500 errors,
            self.cachedValue = SSNotAvailable()
        #print 'onWsError end:',self.cachedValue            
        return None

funclist = (WS,)
