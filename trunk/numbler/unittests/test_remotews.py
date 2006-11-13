from twisted.trial import unittest
from numbler.unittests.testtools import *

from numbler.wsproxy import tags as T,xmlTransactionHandler,ProxyClient,ProxyResponse,xmlResponseHandler
from nevow.flat import flatten

from twisted.application import strports,service
from twisted.internet import reactor
from nevow import appserver,rend,inevow,loaders
from zope.interface import Interface,implements
from wstools import proxyHarness

class xmlTransactionParserTestCase(unittest.TestCase):
    """
    validate that the xmlTransactionHandler parses results correctly. this simply verifies
    that the XML is correct, not that any associated web service is correct
    
    """

    def testSingleRequest(self):

        requestXML = T.transaction(callbackURI='http://hali:8080/wsresponse')[
            T.request(id="123")[
            T.param(name="category")["books"],
            T.param(name="keywords")["Twisted Network Programming Essentials"]
            ]
            ]

        handler = xmlTransactionHandler()
        handler.doparseString(flatten(requestXML))
        self.failUnless(handler.callbackURI == 'http://hali:8080/wsresponse')
        self.failUnless(len(handler.requests) == 1)

    def testMalformedRequest(self):
        # missing request ID
        requestXML = T.transaction(callbackURI='http://hali:8080/wsresponse')[
            T.request[
            T.param(name="category")["books"],
            T.param(name="keywords")["Twisted Network Programming Essentials"]
            ]
            ]        

        handler = xmlTransactionHandler()
        self.failUnlessRaises(ParseException,handler.doparseString,flatten(requestXML))

        # missing callbackURI
        requestXML = T.transaction[
            T.request(id="123")[
            T.param(name="category")["books"],
            T.param(name="keywords")["Twisted Network Programming Essentials"]
            ]
            ]        

        handler = xmlTransactionHandler()
        self.failUnlessRaises(ParseException,handler.doparseString,flatten(requestXML))
        

    def testMultipleRequests(self):
        requestXML = T.transaction(callbackURI='http://hali:8080/wsresponse')[
            T.request(id="123")[
            T.param(name="category")["books"],
            T.param(name="keywords")["Twisted Network Programming Essentials"]
            ],
            T.request(id="123")[
            T.param(name="category")["books"],
            T.param(name="keywords")["Stranger in a strange land"]
            ]
            ]

        handler = xmlTransactionHandler()
        handler.doparseString(flatten(requestXML))
        self.failUnless(len(handler.requests) == 2)


    def testResponseData(self):
        basicResponse = """
        <response>
        <request id="123" status="200" reason="ok">
        <result_set>
        <value name="price">35.05</value>
        <value name="url">http://foo.com</value>
        </result_set>
        </request>
        </response>
        """

        handler = xmlResponseHandler()
        handler.doparseString(basicResponse)
        self.failUnless(handler.requests[0].params['price'] == '35.05')
        

class xmlTransactionResponseTestCase(unittest.TestCase):

    def testSimpleResponse(self):

        res = ProxyResponse([{'id':123,'status':200}],
                            [[{'name':'price','value':35.05},
                              {'name':'condition','value':'shitty'}
                              ]])
        self.failUnless(flatten(res.generateResponse()) == '<response><request status="200" id="123"><result_set><value name="price">35.05</value><value name="condition">shitty</value></result_set></request></response>')

    def testMultiResponse(self):
        res = ProxyResponse([{'id':123,'status':200},
                             {'id':456,'status':500,'reason':'product not found'}
                             ],
                            [
                            [{'name':'price','value':35.05},
                            {'name':'condition','value':'shitty'}
                            ],
                            [{'name':'price','value':35.05},
                             {'name':'condition','value':'shitty'}
                             ]
                            ])
        self.failUnless(flatten(res.generateResponse()) == '<response><request status="200" id="123"><result_set><value name="price">35.05</value><value name="condition">shitty</value></result_set></request><request status="500" reason="product not found" id="456"><result_set><value name="price">35.05</value><value name="condition">shitty</value></result_set></request></response>')
        
##class testEchoService(proxyHarness):
##    """
##    send basic requests to the echo service.  The Web service
##    proxy must be started!
##    """

##    def verifyRequest(self,data,pclient):
##        print 'testEchoService: verifyRequest received',data,pclient.factory.status
##        return self.waitingDeferred

##    def verifyResultCB(self,result):
##        self.failUnless(result == '<response><request status="200" id="123"><result_set><value name="category">books</value><value name="keywords">Twisted Network Programming Essentials</value></result_set></request></response>')

##        handler = xmlResponseHandler()
##        handler.doparseString(result)
##        print 'veriyResultCb: parsed results are',handler.dump()

##    def testBasicRequest(self):
##        requestXML = T.transaction(callbackURI='http://localhost:9005/wsresponse')[
##            T.request(id="123")[
##            T.param(name="category")["books"],
##            T.param(name="keywords")["Twisted Network Programming Essentials"]
##            ]]

##        pclient = ProxyClient('localhost',9000,'/echoService',flatten(requestXML))
##        d = pclient.connect()
##        d.addCallback(self.verifyRequest,pclient)

##        self.waitingDeferred = defer.Deferred()
##        self.waitingDeferred.addCallback(self.verifyResultCB)
##        self.responsesite.setWaitDeferred(self.waitingDeferred)
##        return d

