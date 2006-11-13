# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

"""
The wsproxy module is a general purpose mechanism for
wrapping a request from a numbler sheet server to a server
that is responsible for mediating a web service request (to amazon for example)

Primarily wsproxy takes a request, validates the input data, and then returns
immediately to the caller.  The remote web service is then invoked or queued. When
finished it will call back to the sheet server on the supplied callback URI.

"""

from zope.interface import Interface,implements
from xml.sax import handler,parseString,make_parser,SAXException
from nevow import inevow,rend,tags as T,loaders,flat
from numbler.server.exc import ParseException
from twisted.web import http,server,client
from twisted.internet import reactor,defer
from twisted.web.server import UnsupportedMethod
from numbler.inumbler import IRemoteWSProxy
from numbler.proxytools import ProxyResponse
from proxytools import tags
from twisted.web import error
from numbler.server.sslib import mrudict
from numbler.proxytools import fireCallbackURI
import cElementTree as et,cStringIO

#plugins: make this work better
from numbler.clients import amazon,currency,ebay

############################################################
## Exceptions
############################################################

class WsException(Exception):
    """
    base class for web service exceptions
    """

    def renderException(self):
        return tags.transaction_ack(status="error",
                                    id=self.transaction_id,
                                    reason=self.reason)

class BadWsParamException(Exception):
    """ a parameter is not correct"""
    def __init__(self,id,paramName,value):
        self.transaction_id = id
        self.reason = "Parameter %s value %s is not valid" % (paramName,value)


class echoService(object):
    """
    A Simple echo service which simply returns back the original request
    but in the appropriate format.
    """
    
    implements(IRemoteWSProxy)

    def validateRequest(self,parsedRequest):
        # the echo service does nothing.
        pass

    def doRemoteRequest(self,arg,parsedRequest,callbackURI):
        print 'running echoService: calling back on a one second delay',callbackURI

        d = defer.Deferred()
        d.addCallback(self.doRemoteRequestLater,parsedRequest,callbackURI)
        reactor.callLater(1,d.callback,None)
        return d


    def doRemoteRequestLater(self,arg,parsedRequest,callbackURI):
        host,port,path = client._parse(callbackURI)[1:]
        path = path.encode('ascii')
        # generate the request - echo back everything
        
        results=  [[{'name':key,'value':req['params'][key]}
                    for key in req['params'].keys()] for req in parsedRequest.requests]

        resp = ProxyResponse(
            [{'id':req['id'],'status':200} for req in parsedRequest.requests],
                           results)

        factory = client.HTTPClientFactory(path,method='PUT',
                                           postdata=flat.flatten(resp.generateResponse()))
        factory.noisy = False
        reactor.connectTCP(host,port,factory)
        return factory.deferred



class ResponseData(object):
    def __init__(self,id,status,reason):
        self.id = id
        try:
            self.status = int(status)
        except ValueError:
            self.status = status
        self.reason = reason
        self.params = {}
        
class xmlResponseHandler(object):
    """
    parse a remote web service response.

    The request element can contain multiple result_sets and the
    each result_set can contain multiple values.  The actual values
    return on defined by the service definition.

    sample:

    <response>
      <request id="123" status="200" reason="ok">
        <result_set>
        <value name="price">35.05</value>
        <value name="url">http://foo.com</value>
        </result_set>
      </request>
    </response>

    notes: the status code is required.  The reason is optional.
    
    """
    def __init__(self):
        self.requests = []
          
    def doparseString(self,data):
        self._parseInternal(cStringIO.StringIO(data))

    def doparse(self,fileOrFileName):
        self._parseInternal(fileOrFileName)

    def _parseInternal(self,fileLike):
        for event,elem in et.iterparse(fileLike):
            if elem.tag == 'request':
                id = elem.attrib.get('id')
                status = elem.attrib.get('status')
                reason = elem.attrib.get('reason')
                if id is None:
                    raise ParseException('missing id')
                if status is None:
                    raise ParseException('missing status')
                if reason is None:
                    reason = ''
                cval = ResponseData(id,status,reason)
                self.requests.append(cval)
                for itemel in elem.getiterator():
                    if itemel.tag == 'value':
                        cval.params[itemel.attrib['name']] = itemel.text

    def dump(self):
        return self.requests

class xmlTransactionHandler(handler.ContentHandler):
    """

    parse a remote web service request.

    sample:

    <transaction callbackURI="http://hali:8080/wsresponse">
      <request id="123">
        <param name="category">books</param>
        <param name="keywords">Twisted Network Programming Essentials</param>
      </request>
    </transaction>
    """

    def __init__(self):
        self.callbackURI = ''
        self.requests = []
        self.crequest = None
        self.cparams = None
        self.paramname = None

    def doparseString(self,data):
        parseString(data,self)
        
    def doparse(self,data):
        parser = make_parser()
        parser.setContentHandler(self)
        parser.parse(data)

    def dump(self):
        data = '%s:%s\n%s:%s\n%s' %\
               ('callbackURI:',self.callbackURI,'# requests',str(len(self.requests)),
                '\n'.join([str(x) for x in self.requests]))
        print 'dump: data is ',data
        return data

                

    def startElement(self,name,attrs):

        # clear the parameter name
        self.paramname = None
        
        lstr = name.lower()
        if lstr == 'transaction':
            self.callbackURI = attrs.get('callbackURI')
            if self.callbackURI is None:
                raise ParseException('missing callback URI')
        elif lstr == 'request':
            transID = attrs.get('id')
            if transID is None:
                raise ParseException('missing id')
            self.cparams = {}
            crequest = {'id':transID,'params':self.cparams}
            self.requests.append(crequest)
        elif lstr == 'param' and self.cparams is not None:
            name = attrs.get('name')
            if name is None:
                raise ParseException('missing name on param')
            self.paramname = name

    def characters(self,content):
        self.cparams[self.paramname] = content



class txnStatus(object):

    pending = 0
    retry = 1
    done = 2
    failed = 3

    states = {pending:'pending',retry:'retry',done:'done',failed:'failed'}

    def __init__(self,txnId):
        self.txnId = txnId
        self.state = self.pending

    def setretry(self):
        self.state = self.retry

    def complete(self):
        self.state = self.done

    def failtxn(self):
        self.state = self.failed

    def isDone(self):
        return self.state == self.done

    def stateStr(self):
        statedesc = self.states.get(self.state)
        if statedesc is None:
            return "unknown state %s (programmer error)" % (self.state,)
        return statedesc

    def __str__(self):
        return '%d => %s' % (self.txnId,self.stateStr())

            
class WSProxy(object):
    """
    handle a web service proxy request
    """
    implements(inevow.IResource)
    allowedMethods = ('PUT',)

    normalResponse = tags.transaction_ack(status="accepted")
    recentTxns = mrudict.MRUDict(500)

    def __init__(self,webServiceProxy):
        self.proxyHandler = webServiceProxy

    def locateChild(self,ctx,segments):
        return None,()

    def handleWsFailure(self,failureInst,handler,callbackURI):
        """
        called in case of failure condition.
        """
        failureInst.trap(error.Error)

        # handle the various status codes
        scode = int(failureInst.value.status)

        #print 'failureInst.value is',failureInst.value,failureInst.value.status,type(failureInst.value.status)
        if scode == 503:

            # mark the state as retry
            for req in handler.requests: self.recentTxns[req['id']].setretry()
            
            # try again - service is temporarily unavailable.
            d = defer.Deferred()
            donecb = d.addCallback(self.proxyHandler.doRemoteRequest,handler,callbackURI)
            donecb.addCallback(self.clearTxn,handler)
            donecb.addErrback(self.handleWsFailure,handler,callbackURI)            
            reactor.callLater(2,d.callback,None)        
        else:
            # return the error code back
            resp = ProxyResponse([{'id':req['id'],'status':scode} for req in handler.requests],[])
            fireCallbackURI(callbackURI,flat.flatten(resp.generateResponse()))

        # trap all the errors here.
        return None


    def clearTxn(self,arg,handler):
        for req in handler.requests: self.recentTxns[req['id']].complete()

    def renderHTTP(self,ctx):
        """
        use the associated proxy request handler and process the
        results.
        """
        req = inevow.IRequest(ctx)
        ret = ''

        if req.method != 'PUT':
            req.setHeader('Allow','PUT')
            # copied from server.py - just something to display if someone tries
            # to hit the resource with a GET or something
            return server.error.ErrorPage(http.NOT_ALLOWED,"Method Not Allowed",'').render(req)
        try:
            handler = xmlTransactionHandler()
            handler.doparse(req.content)
        except ParseException:
            # indicate malformed request.
            req.setResponseCode(http.BAD_REQUEST)
        except SAXException,e:
            # indicate XML parsing error
            req.setResponseCode(http.BAD_REQUEST)            
        except Exception,e:
            print '** WSProxy ** error occurred',e
            # anything else
            import traceback,sys
            traceback.print_tb(sys.exc_info()[2])
            #traceback.print_stack()                                                
            req.setResponseCode(http.INTERNAL_SERVER_ERROR)             
        else:
            try:
                self.proxyHandler.validateRequest(handler)

                # create a pending record
                for req in handler.requests:
                    id = req['id']
                    self.recentTxns[id] = txnStatus(id)
                
                d = defer.Deferred()
                donecb = d.addCallback(self.proxyHandler.doRemoteRequest,handler,handler.callbackURI)
                donecb.addCallback(self.clearTxn,handler)
                donecb.addErrback(self.handleWsFailure,handler,handler.callbackURI)
                reactor.callLater(0,d.callback,None)
                ret = flat.flatten(self.normalResponse)
            except WsException,e:
                ret = flat.flatten(e.renderException())
            #except:
            #    req.setResponseCode(http.INTERNAL_SERVER_ERROR)
        #req.finish()
        #print 'returning',ret
        #req.finish()
        return ret



class TransactionList(rend.Page):

    def renderTxns(self,ctx,data):
        if ctx.arg('showAll'):
           showAll = True
        else:
            showAll = False
        
        for statusObj in WSProxy.recentTxns.values():
            if not showAll and statusObj.isDone():
                continue
            yield T.tr[
                T.td[
                statusObj.txnId
                ],
                T.td[
                statusObj.stateStr()
                ]
                ]
            

    docFactory = loaders.stan(
        T.html[
        T.head[
        T.title["Current transactions"]
        ],
        T.body[
        T.table[
        renderTxns,
        ]]])

class ProxyRoot(rend.Page):

    docFactory = loaders.stan(T.html[T.head[T.title[""]],T.body["nothing here"]])

    children=dict(echoService=WSProxy(echoService()),
                  awsUsedPrice=WSProxy(amazon.amazonUsedPriceService()),
                  awsNewPrice=WSProxy(amazon.amazonNewPriceService()),                  
                  currencylookup=WSProxy(currency.currencyConversionService()),
                  ebayprice=WSProxy(ebay.ebayItemLookup()),
                  transactions=TransactionList()
                  )

    def __init__(self,*args,**kw):

        # check and populate the ebay catalog if the information is
        # missing or out of date.
        catalog = ebay.eBayCatalog.getInstance()
        catalog.checkCatalog()
        super(ProxyRoot,self).__init__(*args,**kw)

class ProxyClient(object):
    """
    base class for transmitting a web service proxy request.

    This class is ignorant of the actual web service details.
    """

    agent = 'Numbler proxyRequester'

    def __init__(self,host,port,resource,postData):
        self.host = host
        self.port=port
        headers = {'HOST':host,'User-Agent':self.agent}

        #targeturl = 'http://%s:%d%s' % (host,port,resource)
        #client.getPage(

        self.factory = client.HTTPClientFactory(resource,headers=headers,method='PUT',
                                                agent=self.agent,postdata=postData)
        self.factory.noisy = False

    def connect(self):
        cancelable = reactor.connectTCP(self.host,self.port,self.factory)
        return self.factory.deferred,cancelable
