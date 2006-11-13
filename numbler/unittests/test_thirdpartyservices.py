from numbler.unittests.testtools import *
from numbler.unittests.wstools import proxyHarness
from twisted.python.failure import Failure
from numbler.wsproxy import ResponseData




class currencyTestCase(proxyHarness):
    sheets = [
        {'name':'wstest',
         'cells':[
        ('a1','=WS("convert_currency","USD","EUR")'),
        ('a2','=WS("convert_currency","USD","fringle")'),        
        ]
         }]

    def verifyUpdates(self,arg,shtH):
        """
        verify that update gets called because of the available formula
        """
        print 'updated cells are',self.updateSet
        for x in self.updateSet:
            self.fail
            print 'Value for %s is %s'%(x,x().getValue(1))



    def testUsdToEur(self):

        def verifyUpdates(arg,shtH):
            for x in self.updateSet:
                value = x().getValue(1)
                print 'USD to EUR conversion is',value
                self.failUnless(isinstance(value,float))

        sht = self.sheetHandles['wstest']
        # kick of the eval
        self.value(sht,'a1')
        txnMgr = self.getCell(sht,'a1')().getTxnMgr()
        self.failUnless(txnMgr is not None)
        d = txnMgr.getPendingDeferred()
        d.addCallback(verifyUpdates,sht)
        return d
        
    def testBadConversion(self):
        sht = self.sheetHandles['wstest']
        # kick of the eval
        self.value(sht,'a2')
        txnMgr = self.getCell(sht,'a2')().getTxnMgr()
        self.failUnless(txnMgr is not None)
        d = txnMgr.getPendingDeferred()
        #from twisted.internet.defer import FirstError
        #return self.assertFailure(d,FirstError).addCallback(lambda _: self.checkException(sht,'a2',SSNotAvailable))
        d.addBoth(lambda _: self.checkException(sht,'a2',SSNotAvailable))
        return d


class ebayPriceLookup(proxyHarness):
    sheets = [
        {'name':'wstest',
         'cells':[
        ('a1','=WS("ebay_price","Giant 06 TCR Composite")'),
        ('a2','=WS("ebay_price","fringle frangle bangle boozle")'),
        ('a3','=WS("ebay_price",z192)'),
        ('a4','=WS("ebay_price","jersey","cycling")')                        
        ]
         }]
    
    def testBikeLookup(self):
        """ lookup a bike product. """

        def verifyUpdates(arg,shtH):
            for x in self.updateSet:
                value = x().getValue(1)
                print 'bike price is',value
                self.failUnless(isinstance(value,float))
                print x().getData()
        
        sht = self.sheetHandles['wstest']
        self.value(sht,'a1')
        txnMgr = self.getCell(sht,'a1')().getTxnMgr()
        d = txnMgr.getPendingDeferred()
        d.addCallback(verifyUpdates,sht)
        return d

    def testBadLookup(self):
        sht = self.sheetHandles['wstest']
        # kick of the eval
        self.value(sht,'a2')
        txnMgr = self.getCell(sht,'a2')().getTxnMgr()
        d = txnMgr.getPendingDeferred()
        d.addBoth(lambda _: self.checkException(sht,'a2',SSNotAvailable))
        return d    


    def testMissingArgument(self):
        """
        verify that a lookup works when the argument is missing.
        """
        sht = self.sheetHandles['wstest']
        self.checkException(sht,'a3',SSValueError)

    def testCategoryLookup(self):
        """ lookup a bike product. """

        def verifyUpdates(arg,shtH):
            for x in self.updateSet:
                value = x().getValue(1)
                print 'wheelset price is',value
                self.failUnless(isinstance(value,float))
                print x().getData()
        
        sht = self.sheetHandles['wstest']
        self.value(sht,'a4')
        txnMgr = self.getCell(sht,'a4')().getTxnMgr()
        d = txnMgr.getPendingDeferred()
        d.addCallback(verifyUpdates,sht)
        return d



class amazonNewPrice(proxyHarness):
    sheets = [
        {'name':'wstest',
         'cells':[
        ('a1','=WS("amazon","Crown of thorns","Books")'),
        ('a2','=WS("amazon","Apocalypse now","DVD")'),
        ('a3','=WS("amazon","Crown of thorns")'),        
        ]
         }]

    def testBooks(self):
        """ lookup a bike product. """

        def verifyUpdates(arg,shtH):
            for x in self.updateSet:
                value = x().getValue(1)
                print 'book price',value
                self.failUnless(isinstance(value,float))
                print x().getData()
        
        sht = self.sheetHandles['wstest']
        self.value(sht,'a1')
        txnMgr = self.getCell(sht,'a1')().getTxnMgr()
        d = txnMgr.getPendingDeferred()
        d.addCallback(verifyUpdates,sht)
        return d

    def testDVD(self):
        """ lookup a DVD product. """

        def verifyUpdates(arg,shtH):
            for x in self.updateSet:
                value = x().getValue(1)
                print 'bike price is',value
                self.failUnless(isinstance(value,float))
                print x().getData()
        
        sht = self.sheetHandles['wstest']
        self.value(sht,'a2')
        txnMgr = self.getCell(sht,'a2')().getTxnMgr()
        d = txnMgr.getPendingDeferred()
        d.addCallback(verifyUpdates,sht)
        return d

    def testDVDWithNoCategory(self):
        """ lookup a DVD product. """

        def verifyUpdates(arg,shtH):
            for x in self.updateSet:
                value = x().getValue(1)
                print 'bike price is',value
                self.failUnless(isinstance(value,float))
                print x().getData()
        
        sht = self.sheetHandles['wstest']
        self.value(sht,'a3')
        txnMgr = self.getCell(sht,'a3')().getTxnMgr()
        d = txnMgr.getPendingDeferred()
        d.addCallback(verifyUpdates,sht)
        return d    
        
