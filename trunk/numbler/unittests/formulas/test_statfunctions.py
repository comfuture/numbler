#!/usr/bin/env python

from numbler.unittests.testtools import *

class miscStats(formulaTestCase):

    def testMax(self):
        val = self.getParsed("MAX(3,6,400)")
        self.failUnless(val.eval(1) == 400)
        val = self.getParsed("MAX(-100,-50,0)")
        self.failUnless(val.eval(1) == 0)                

    def testMin(self):
        val = self.getParsed("MIN(3,6,400)")
        self.failUnless(val.eval(1) == 3)
        val = self.getParsed("MIN(-100,-50,0)")
        self.failUnless(val.eval(1) == -100)                        

class STDEVTestCase(formulaTestCase):

    def testSTDEVP(self):
        val = self.getParsed("ROUND(STDEVP(3,6,9),4)")
        self.failUnless(val.eval(1) == 2.4495)
        val = self.getParsed("ROUND(STDEVP(1345,1301,1368,1322,1310,1370,1318,1350,1303,1299),4)")
        self.failUnless(val.eval(1) == 26.0546)


    def testSTDEV(self):
        val = self.getParsed("ROUND(STDEV(3,6,9),4)")
        self.failUnless(val.eval(1) == 3)
        val = self.getParsed("ROUND(STDEV(1345,1301,1368,1322,1310,1370,1318,1350,1303,1299),4)")
        self.failUnless(val.eval(1) == 27.4639)
        
    def testVAR(self):
        val = self.getParsed("ROUND(VAR(13,42,44,324,23,1,21),4)")
        self.failUnless(val.eval(1) == 13087.8095)

    def testVARP(self):
        val = self.getParsed("ROUND(VARP(13,42,44,324,23,1,21),4)")
        print 'var val is',val.eval(1)
        self.failUnless(val.eval(1) == 11218.1224)   



class statSheetFunctions(sheetTester):
    sheets = [
        {
        'name':'statsheet',
        'cells':[
        ('a1','3'),
        ('a5','3.001'),
        ('a10','2e30'),
        ('a20','45'),
        ('b4','-1'),
        ('b5','-2e5'),
        ('b19','22'),
        ('c1','=SMALL(A:B,-1)'),
        ('c2','=SMALL(A:B,0)'),
        ('c3','=SMALL(A:B,1)'),
        ('c4','=SMALL(A:B,4)'),
        ('c5','=SMALL(A:B,6)'),
        ('c6','=SMALL(A:B,8)'),
        ('c7','=SMALL(A:B)'),
        ('c8','=SMALL(8,A:B)'),
        ('c9','=SMALL(A:B,7)'),
        ('d1','=STDEV(Z:AA)')
        ]
        }]
    def testSMALL(self):
        sht = self.sheetHandles['statsheet']

        self.checkException(sht,'c1',SSNumError)
        self.checkException(sht,'c2',SSNumError)
        self.checkException(sht,'c6',SSNumError)        
        
        self.failUnless(self.value(sht,'c3') == -200000)
        self.failUnless(self.value(sht,'c4') == 3.001)
        self.failUnless(self.value(sht,'c5') == 45)
        self.failUnless(self.value(sht,'c9') == 2e30)

        
        self.checkException(sht,'c7',WrongNumArgumentsError)
        self.checkException(sht,'c8',BadArgumentsError)        

    def testBadArgs(self):

        sht= self.sheetHandles['statsheet']
        self.checkException(sht,'d1',SSZeroDivisionError)

class randTestSuite(sheetTester):
    sheets = [{
        'name':'randsheet',
        'cells':[
        ('a1','=RAND()'),
        ('a2','45'),
        ('a3','=SUM(A1:A2)'),
        ('a4','=SUM(RAND(),RAND(),RAND())')
        ]
        }]

    def testRandFunction(self):
        sht = self.sheetHandles['randsheet']

        randvals = set([self.value(sht,'a1') for x in range(0,5)])
        sumvals = set([self.value(sht,'a3') for x in range(0,5)])
        morerand = set([self.value(sht,'a4') for x in range(0,5)])        

        self.failUnless(len(randvals) == 5)
        print 'sumvals is',sumvals
        self.failUnless(len(sumvals) == 5)
        self.failUnless(len(morerand) == 5)        
        

        
        
        




suitelist = [STDEVTestCase,statSheetFunctions]


if __name__ == '__main__': testmain(suitelist)
    
