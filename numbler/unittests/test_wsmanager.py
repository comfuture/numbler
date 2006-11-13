from twisted.trial import unittest
from numbler.unittests.testtools import *
from numbler.wsmanager import wsDefinition,wsServiceManager,wsResponseManager,FormulaTxnManager
from numbler.wsproxy import xmlResponseHandler
from twisted.python import context

from xml.dom.minidom import parse

from pkg_resources import resource_filename
servicedefs = resource_filename('numbler.unittests','servicedefs')
import os

from wstools import proxyHarness

class wsDefinitionTestCase(unittest.TestCase):


    def testBasicDefinition(self):
        #TODO: Fix this
        
        """
        test a basic service definition
        """
##        basicDef = wsDefinition.createInstance(parse(os.sep.join([servicedefs,'basic.xml'])))
##        self.failUnless(basicDef.name == 'pricelookup')
##        self.failUnless(basicDef.desc == 'lookup price')
##        self.failUnless(basicDef.params == ['category','keywords','hint'])
##        self.failUnless(basicDef.reqprops == ['category','keywords'])        

    def testMissingAttrs(self):
        """
        test that a service definition can't be created if it is missing key attributes
        """
        # check for missing name
        self.failUnlessRaises(Exception,wsDefinition.createInstance,
                              parse(os.sep.join([servicedefs,'basic_missingname.xml'])))

        # check for missing desc
        self.failUnlessRaises(Exception,wsDefinition.createInstance,
                              parse(os.sep.join([servicedefs,'basic_missingdef.xml'])))

        # check for missing outputs
        self.failUnlessRaises(Exception,wsDefinition.createInstance,
                              parse(os.sep.join([servicedefs,'basic_missingoutputs.xml'])))

        # check for outputs that are not annotated correctly
        self.failUnlessRaises(Exception,wsDefinition.createInstance,
                              parse(os.sep.join([servicedefs,'basic_outputnotdecorated.xml'])))

    def testNoInputs(self):
        """
        make sure that a service definition works that doesn't have any inputs
        """
        timesvc = wsDefinition.createInstance(parse(
            os.sep.join([servicedefs,'getutctime.xml'])))
        

    def testBasicMessageGen(self):
        basicDef = wsDefinition.createInstance(parse(os.sep.join([servicedefs,'basic.xml'])))
        xmlstr = basicDef.createMessage('1','http://localhost/wsresponse','Books',
                                        'Twisted Network Programming Essentials')
        self.failUnless(xmlstr == '<transaction callbackURI="http://localhost/wsresponse"><request id="1"><param name="category">Books</param><param name="keywords">Twisted Network Programming Essentials</param></request></transaction>')
        xmlstr = basicDef.createMessage('1','http://localhost/wsresponse','Books',
                                        'Twisted Network Programming Essentials') #,'hardcover')
        self.failUnless(xmlstr == '<transaction callbackURI="http://localhost/wsresponse"><request id="1"><param name="category">Books</param><param name="keywords">Twisted Network Programming Essentials</param></request></transaction>')

    def testNoParamMessageGen(self):
        timesvc = wsDefinition.createInstance(parse(os.sep.join([servicedefs,'getutctime.xml'])))
        xmlstr = timesvc.createMessage('1','http://localhost/wsresponse')
        self.failUnless(xmlstr == '<transaction callbackURI="http://localhost/wsresponse"><request id="1"></request></transaction>')



    def testOutputPropDescriptions(self):
        """
        verify that the output properties are classified correctly based on the service def.
        """
        basicDef = wsDefinition.createInstance(parse(os.sep.join([servicedefs,'basic.xml'])))
        self.failUnless(basicDef.outCalcName == "cost")
        self.failUnless(basicDef.outLinkName == "homeURL")        

    def testResponseProcessing(self):
        """
        verify that we can correctly parse the results from a web service response
        """
        responseXML = """
        <response>
        <request id="123" status="200" reason="ok">
        <result_set>
        <value name="cost">35.05</value>
        <value name="homeURL">http://foo.com</value>
        </result_set>
        </request>
        </response>
        """
        basicDef = wsDefinition.createInstance(parse(os.sep.join([servicedefs,'basic.xml'])))
        handler = xmlResponseHandler()
        handler.doparseString(responseXML)
        self.failUnless(basicDef.processResults(handler.requests[0]) == ('35.05','http://foo.com'))


    def testDictArgs(self):
        """
        test message generation with dictionary style arguments (not currently implemented)
        """


class wsManagerTestCase(unittest.TestCase):

    def testWsManager(self):

        wsManager = wsServiceManager.getInstance()
        self.failUnless(wsManager.lookupService('amazon_usedprice') is not None)
        self.failUnlessRaises(wsServiceNotFound,wsManager.lookupService,'frogle fringle')





class fullRemoteManagerTestCase(proxyHarness):
    """
    test everything tied together
    """

    sheets = [
        {'name':'wstest',
         'cells':[
        ('a1','=WS("amazon_usedprice","twisted network programming essentials","Books")'),
        ('a2','=SUM(WS("amazon_usedprice","twisted network programming essentials","Books"),WS("amazon_usedprice","stranger in a strange land","Books"))'),
        ('a3','=WS("amazon_usedprice",WS("amazon_usedprice","stranger in a strange land","Books"),"Books")'),
        # this is a duplicate of a1 but distinct for the formatting test
        ('a4','=WS("amazon_usedprice","twisted network programming essentials","Books")'),
        ('a5','=WS("amazon_usedprice","Crime and Punishment")'),
        ('a6','=WS("amazon_usedprice")'),
        ('a7','=WS("amazon_usedprice",a8,"Books")'),
        ('a8','fringle'),                        
        ]
         }]

    def setUp(self):
        super(fullRemoteManagerTestCase,self).setUp()
        self.sht = sheet.Sheet.getTemp(account.Principal(1,[]))

    def verifyUpdates(self,arg,shtH):
        """
        verify that update gets called because of the available formula
        """
        self.failUnless(len(self.updateSet) == self.numExpectedUpdates)

        #for x in self.updateSet:
        #    print 'Value for %s is %s'%(x,x().getValue(1))
    

    def testBasicFormula(self):

        self.numExpectedUpdates = 1

        sht = self.sheetHandles['wstest']
        sht.attach(self)
        cellH = sht().getCellHandle(Col('a'),1)
        txnMgr = FormulaTxnManager(cellH)
        ctx = {'cell':cellH(),'cache':True}
        context.call({'ctx':ctx,'txnMgr':txnMgr},cellH()._ast.eval,1)
        d = txnMgr.calcOnFinish()
        d.addCallback(self.verifyUpdates,sht)
        return d

    def testMultipleCalls(self):
        self.numExpectedUpdates = 1
        
        sht = self.sheetHandles['wstest']
        sht.attach(self)
        cellH = sht().getCellHandle(Col('a'),2)
        txnMgr = FormulaTxnManager(cellH)
        ctx = {'cell':cellH(),'cache':True}
        context.call({'ctx':ctx,'txnMgr':txnMgr},cellH()._ast.eval,1)
        d = txnMgr.calcOnFinish()
        d.addCallback(self.verifyUpdates,sht)
        return d

    def testParentChild(self):
        self.numExpectedUpdates = 1
        
        sht = self.sheetHandles['wstest']
        sht.attach(self)
        cellH = sht().getCellHandle(Col('a'),3)
        txnMgr = FormulaTxnManager(cellH)
        ctx = {'cell':cellH(),'cache':True}
        context.call({'ctx':ctx,'txnMgr':txnMgr},cellH()._ast.eval,1)
        d = txnMgr.calcOnFinish()
        d.addCallback(self.verifyUpdates,sht)
        return d        


    def testImpliedCurrencyFormatting(self):
        """
        verify that a web service that returns a currency value
        is parsed as a dollar amount.
        """
        self.numExpectedUpdates = 1
        
        sht = self.sheetHandles['wstest']
        sht.attach(self)
        cellH = sht().getCellHandle(Col('a'),4)
        txnMgr = FormulaTxnManager(cellH)
        ctx = {'cell':cellH(),'cache':True}
        context.call({'ctx':ctx,'txnMgr':txnMgr},cellH()._ast.eval,1)
        d = txnMgr.calcOnFinish()
        d.addCallback(self.verifyUpdates,sht)

        def checkFormatting(arg,shtH):
            self.failUnless(self.getFormat(shtH,'a4') == {'__sht':localedb.ParseCtx.currencyFormat})
        d.addCallback(checkFormatting,sht)
        return d


    def testExpiredTransaction(self):
        """
        test that an expired transactions errors out correclty.
        """
        sht = self.sheetHandles['wstest']
        cellI = self.getCell(sht,'a5')()
        # set the timeout to be 1 second.
        cellI.getTxnMgr().timeout = 0
        cellI.getValue()
        # return the deferredlist
        cellI.getTxnMgr().currentdl.addBoth(lambda _: self.checkException(sht,'a5',SSNotAvailable))

    def testNotEnoughArguments(self):
        sht = self.sheetHandles['wstest']
        self.checkException(sht,'a6',SSValueError)
        

    def testOutstandingRequestCancelled(self):
        """
        make two requests.  Verify that the second request is cancelled.
        """
        sht = self.sheetHandles['wstest']
        cellI = self.getCell(sht,'a7')()
        cellI.getValue()
        # change the formula for a8 -- causing a7 to recalculate
        self.setFormula(sht,'a8','The Brothers Karamazov')
        # evaluate the formula again - we would be notified of
        # this change anyway but need to actually run getValue to kick
        # off the ws
        cellI.getValue()

        def checkValue():
            res = cellI.getValue()
            self.failUnless(isinstance(res,(int,long,float)))
            self.failUnless(res > 0)

        d = cellI.getTxnMgr().currentdl
        d.addBoth(lambda _: checkValue())
        return d
    

    def testChildWithBadArgs(self):
        """
        test you get an error when a child async function
        has an argument error.
        """
    
