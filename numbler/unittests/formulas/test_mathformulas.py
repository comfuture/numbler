#!/usr/bin/env python

from numbler.unittests.testtools import *

class modTestCase(formulaTestCase):
    """ test basic formulas that don't require a persisted sheet"""

    def testMOD(self):
        val = self.getParsed("MOD(10,3)")
        self.failUnless(val.eval(1) == 1)

        val = self.getParsed("MOD(1)")
        self.checkException(val,SSValueError)

        val = self.getParsed("MOD(1,2,3)")
        self.checkException(val,SSValueError)

        val = self.getParsed('MOD("HI",3)')
        self.checkException(val,SSValueError)

class sqrtTestCase(formulaTestCase):

    def testSQRT(self):
        val = self.getParsed("SQRT(4)")
        self.failUnless(val.eval(1) == 2)

        val = self.getParsed('SQRT("hi")')
        self.checkException(val,SSValueError)

        val = self.getParsed("SQRT(-1)")
        self.checkException(val,SSNumError)

        val = self.getParsed('SQRT(24,23)')
        self.checkException(val,SSValueError)        


class roundTestCase(formulaTestCase):
    """
    test the round functions.
    """

    def testROUND(self):
        val = self.getParsed("ROUND(123.93,0)")
        self.failUnless(str(val.eval(1)) == '124.0')

        val = self.getParsed("ROUND(123.93,-1)")
        self.failUnless(str(val.eval(1)) == '120.0')

        val = self.getParsed("ROUND(123.93,-2)")
        self.failUnless(str(val.eval(1)) == '100.0')
        val = self.getParsed("ROUND(123.93,-3)")
        self.failUnless(str(val.eval(1)) == '0.0')

        val = self.getParsed("ROUND(123.93,-3)")
        self.failUnless(str(val.eval(1)) == '0.0')        
        
        val = self.getParsed("ROUND(123.93,1)")
        self.failUnless(str(val.eval(1)) == '123.9')

        val = self.getParsed("ROUND(123.939,2)")
        self.failUnless(str(val.eval(1)) == '123.94')

        val = self.getParsed("ROUND(123.934,2)")
        self.failUnless(str(val.eval(1)) == '123.93')

        val = self.getParsed("ROUND(123.934,2)")
        self.failUnless(str(val.eval(1)) == '123.93')                        

        val = self.getParsed('ROUND(1)')
        self.checkException(val,WrongNumArgumentsError)
        val = self.getParsed('ROUND()')
        self.checkException(val,WrongNumArgumentsError)        
        

    def testROUNDDOWN(self):
        val = self.getParsed("ROUNDDOWN(172.4939,5)")
        self.failUnless(str(val.eval(1)) == '172.4939')
        val = self.getParsed("ROUNDDOWN(172.4939,4)")
        self.failUnless(str(val.eval(1)) == '172.4939')
        val = self.getParsed("ROUNDDOWN(172.4939,3)")
        self.failUnless(str(val.eval(1)) == '172.493')
        val = self.getParsed("ROUNDDOWN(172.4939,2)")
        self.failUnless(str(val.eval(1)) == '172.49')
        val = self.getParsed("ROUNDDOWN(172.4939,1)")
        self.failUnless(str(val.eval(1)) == '172.4')
        val = self.getParsed("ROUNDDOWN(172.4939,0)")
        self.failUnless(str(val.eval(1)) == '172.0')
        val = self.getParsed("ROUNDDOWN(172.4939,-1)")
        self.failUnless(str(val.eval(1)) == '170.0')
        val = self.getParsed("ROUNDDOWN(172.4939,-2)")
        self.failUnless(str(val.eval(1)) == '100.0')
        val = self.getParsed("ROUNDDOWN(172.4939,-3)")
        self.failUnless(str(val.eval(1)) == '0.0')                                                                        


    def testROUNDUP(self):
        val = self.getParsed("ROUNDUP(1.22994,5)")
        self.failUnless(str(val.eval(1)) == '1.22994')
        val = self.getParsed("ROUNDUP(1.22994,4)")
        self.failUnless(str(val.eval(1)) == '1.23')
        val = self.getParsed("ROUNDUP(1.22994,3)")
        self.failUnless(str(val.eval(1)) == '1.23')
        val = self.getParsed("ROUNDUP(1.22994,2)")
        self.failUnless(str(val.eval(1)) == '1.23')
        val = self.getParsed("ROUNDUP(1.22994,1)")
        self.failUnless(str(val.eval(1)) == '1.3')
        val = self.getParsed("ROUNDUP(1.22994,0)")
        self.failUnless(str(val.eval(1)) == '2.0')
        val = self.getParsed("ROUNDUP(1.22994,-1)")
        self.failUnless(str(val.eval(1)) == '10.0')

    def testMEDIAN(self):
        val = self.getParsed("MEDIAN(0)")
        self.failUnless(val.eval(1) == 0.0)

        val = self.getParsed("MEDIAN(1,3,5)")
        self.failUnless(val.eval(1) == 3.0)
        val = self.getParsed("MEDIAN(1.23,4,9999,-20000)")
        self.failUnless(val.eval(1) == 2.615)

    def testPOWER(self):
        val = self.getParsed("POWER(5,2)")
        self.failUnless(val.eval(1) == 25)
        val = self.getParsed("POWER(5,5)")
        self.failUnless(val.eval(1) == 3125)
        val = self.getParsed("ROUND(POWER(5.453,0.01),4)")
        print 'value is',val.eval(1)
        self.failUnless(val.eval(1) == 1.0171)  
        

    def textEXP(self):
        """ just a wrapper around math.exp """
        val = self.getParsed("ROUND(exp(5),7)")
        self.failUnless(val.eval(1) == 148.4131591)
        val = self.getParsed("exp()")        
        self.checkException(val,WrongNumArgumentsError)
        val = self.getParsed("exp(4,4)")        
        self.checkException(val,WrongNumArgumentsError)                

    def testINT(self):

        val = self.getParsed("INT(8.9)")
        self.failUnless(val.eval(1) == 8)
        val = self.getParsed("INT(8.0)")        
        self.failUnless(val.eval(1) == 8)
        val = self.getParsed("INT(-9.45)")        
        self.failUnless(val.eval(1) == -9)                

    def testEXP(self):
        val = self.getParsed("ROUND(EXP(5),4)")
        self.failUnless(val.eval(1) == 148.4132)

    def testLOG(self):
        val = self.getParsed("LOG(8,2)")
        self.failUnless(val.eval(1) == 3.0)

    def testTRIG(self):
        """ just make sure this stuff actually runs"""
        self.getParsed("SIN(1.5)").eval(1)
        self.getParsed("cos(1.5)").eval(1)
        self.getParsed("tan(1.5)").eval(1)
        self.getParsed("asin(0.3)").eval(1)
        self.getParsed("atan(0.3)").eval(1)
        # the parser has a bug that doesn't let atan2 work
        #self.getParsed("atan2(0.3)").eval(1)        
        self.getParsed("cosh(1.5)").eval(1)
        self.getParsed("sinh(1.5)").eval(1)
        self.getParsed("DEGREES(SIN(32))").eval(1)

        val = self.getParsed("ROUND(atan(1)*4,2)")
        self.failUnless(val.eval(1) == 3.14)

    def testPRODUCT(self):
        val = self.getParsed("PRODUCT(5,5,5)")
        self.failUnless(val.eval(1) == float(5 * 5 * 5))
        val = self.getParsed("PRODUCT(5,5,-3,2e-1,24,102,75,99,44)")
        self.failUnless(val.eval(1) == -11996424000)
        val = self.getParsed("PRODUCT()")        
        self.checkException(val,BadArgumentsError)
                        
    def testDDB(self):
        """ test the double declining balance method for calculating depreciation """

        val = self.getParsed("ROUND(DDB(20000,2000,10,8),2)")
        self.failUnless(val.eval(1) == 838.86)
        val = self.getParsed("ROUND(DDB(20000,2000,10,11),2)")        
        self.checkException(val,SSNumError)
        val = self.getParsed("DDB(20000,10000,10,8)")
        self.failUnless(val.eval(1) == 0)
        val = self.getParsed("ROUND(DDB(2400,300,10*365,1),2)")
        self.failUnless(val.eval(1) == 1.32)
        val = self.getParsed("ROUND(DDB(2400,300,10*12,1,2),2)")
        self.failUnless(val.eval(1) == 40.00)
        val = self.getParsed("ROUND(DDB(2400,300,10,1,2),2)")
        self.failUnless(val.eval(1) == 480.00)
        val = self.getParsed("ROUND(DDB(2400,30,10,2,1.5),2)")
        self.failUnless(val.eval(1) == 306.00)
        val = self.getParsed("ROUND(DDB(2400,300,10,10),2)")
        print 'value is',val.eval(1)
        self.failUnless(val.eval(1) == 22.12)

    def testSLN(self):
        """ test the straight line depreciation """
        val = self.getParsed("SLN(30000,7500,10)")
        self.failUnless(val.eval(1) == 2250)
        val = self.getParsed("SLN(2000,3000,4)")
        self.failUnless(val.eval(1) == -250.00)        
        self.checkException(self.getParsed("SLN()"),WrongNumArgumentsError)




class subtotalTestCase(sheetTester):
    sheets = [
        {
        'name':'subtotalsheet',
        'cells':[
        ('a1','3'),
        ('a5','3.001'),
        ('a10','997.003'),
        ('a20','45'),
        ('b4','-1'),
        ('b5','-2e2'),
        ('b20','22'),
        ('c1','=PI()'),
        ('R92','howdy'),
        ('R100','$35.542'),
        ('R101','5-jun'),
        ('AA1','=SUBTOTAL(9,a1:a20,b1:b20)'),
        ('AA2','=SUM(a1:b20)'),
        ('aa3','=ROUND(AA1,3)'),
        ('aa4','=SUBTOTAL(1,a1:a20,b1:b20,c1,R92:R101)'),
        ('aa5','=SUBTOTAL(2,a1:a20,b1:b20,c1,R92:R101)'),
        ('aa6','=SUBTOTAL(3,a1:a20,b1:b20,c1,R92:R101)'),
        ('aa7','=SUBTOTAL(4,a1:a20,b1:b20,c1,R92:R101)'),
        ('aa8','=SUBTOTAL(5,a1:a20,b1:b20,c1,R92:R101)'),
        ('aa9','=SUBTOTAL(6,a1:a20,b1:b20,c1,R92:R101)'),
        ('aa10','=SUBTOTAL(7,a1:a20,b1:b20,c1,R92:R101)'),
        ('aa11','=SUBTOTAL(8,a1:a20,b1:b20,c1,R92:R101)'),
        ('aa12','=SUBTOTAL(9,a1:a20,b1:b20,c1,R92:R101)'),               
        ('aa13','=SUBTOTAL(10,a1:a20,b1:b20,c1,R92:R101)'),
        ('aa14','=SUBTOTAL(11,a1:a20,b1:b20,c1,R92:R101)')               
        ]
        }]
    def testSubtotal(self):
        sht = self.sheetHandles['subtotalsheet']
        v = self.value(sht,'AA1')
        self.failUnless(self.value(sht,'AA1') == self.value(sht,'AA2'))
        self.failUnless(self.value(sht,'AA3') == 869.004)

        # make sure these all evaluate
        self.value(sht,'aa4')
        self.value(sht,'aa5')
        self.value(sht,'aa6')
        self.value(sht,'aa7')
        self.value(sht,'aa8')
        self.value(sht,'aa9')
        self.value(sht,'aa10')
        self.value(sht,'aa11')
        self.value(sht,'aa12')
        self.value(sht,'aa13')
        self.value(sht,'aa14')                


class absTestCase(formulaTestCase):

    def testAbs(self):
        val = self.getParsed("Abs(-5.669)")
        self.failUnless(val.eval(1) == 5.669)
        val = self.getParsed("Abs(92.004)")
        self.failUnless(val.eval(1) == 92.004)        
        

class truncTestCase(formulaTestCase):

    def testTrunc(self):
        val = self.getParsed("TRUNC(8.9)")
        self.failUnless(val.eval(1) == 8)
        val = self.getParsed("TRUNC(-8.9)")
        self.failUnless(val.eval(1) == -8)
        val = self.getParsed("TRUNC(PI())")
        self.failUnless(val.eval(1) == 3)        


class logTestCase(formulaTestCase):

    def testLOG(self):
        val = self.getParsed("LOG(10)")
        self.failUnless(val.eval(1) == 1)
        val = self.getParsed("LOG(8,2)")
        self.failUnless(val.eval(1) == 3)
        val = self.getParsed("ROUND(LOG(86,2.7182818),4)")
        self.failUnless(val.eval(1) == 4.4543)
        



suitelist = [modTestCase,sqrtTestCase,roundTestCase]


if __name__ == '__main__': testmain(suitelist)
