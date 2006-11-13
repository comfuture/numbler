#!/usr/bin/env python

from numbler.unittests.testtools import *
from time import sleep


class timechangeTestCase(sheetTester):
    """
    now needs to be a sheet tester so we can use
    the context support in getValue() to test that now is not cached.
    """
    sheets = [{
        'name':'timesheet',
        'cells':[
        ('a1','=NOW()'),
        ('a2','=TODAY()'),
        ('a3','=SUM(1,2,A1)')
        ]
        }]

    def testNow(self):
        sht = self.sheetHandles['timesheet']
        self.failUnless(self.value(sht,'a1') != 0)

        nowset,sumset = set(),set()
        
        print 'running NOW tests...'    
        for x in xrange(0,4):
            nowset.add(self.value(sht,'a1'))
            sumset.add(self.value(sht,'a3'))
            sleep(1)

        print 'done with NOW test.'
        print 'sets are:',nowset,sumset
        self.failUnless(len(nowset) == 4)
        self.failUnless(len(sumset) == 4)

        self.failUnless(self.value(sht,'a2') != 0)
        # very that the value wasn't cached.
        self.failUnless(self.getCell(sht,'a2')()._val is None)
 
    

class timeFunctionsTestCase(formulaTestCase):

    def testDATE(self):

        val = self.getParsed("DATE(1900,1,1)")
        self.failUnless(val.eval(1) == 1)
        val = self.getParsed("DATE(0,1,1)")
        self.failUnless(val.eval(1) == 1)
        val = self.getParsed("DATE(1,1,1)")
        self.failUnless(val.eval(1) == 367)                

        val = self.getParsed("DATE()")
        self.checkException(val,SSValueError)

        val = self.getParsed('DATE("hi","there","bye")')
        self.checkException(val,SSValueError)

        val = self.getParsed("DATE(1900,1,-100)")


        val = self.getParsed("DATE(9999,1,1)")
        self.failUnless(val.eval(1) == 2958101)

        val = self.getParsed("DATE(9999,12,31)")
        self.failUnless(val.eval(1) == 2958465)
        
        val = self.getParsed("DATE(9999,12,32)")
        self.checkException(val,SSNumError)
        
        val = self.getParsed("DATE(10000,1,1)")        
        self.checkException(val,SSNumError)

        val = self.getParsed("DATE(2005,0,1)")
        # should be equal to 12/1/2004
        self.failUnless(val.eval(1) == 38322)

        val = self.getParsed("DATE(2005,-1,1)")
        # should be qual to 11/1/2004
        self.failUnless(val.eval(1) == 38292)

        val = self.getParsed("DATE(1000,1,1)")
        self.failUnless(val.eval(1) == 365245)

        # overflow tests
        val = self.getParsed("DATE(2006,1,300)")
        self.failUnless(val.eval(1) == 39017)

        val = self.getParsed("DATE(2006,120,1)")
        self.failUnless(val.eval(1) == 42339)

        val = self.getParsed("DATE(2006,120,400)")
        self.failUnless(val.eval(1) == 42738)

        val = self.getParsed("DATE(2006,120,31000)")
        self.failUnless(val.eval(1) == 73338)

        val = self.getParsed("DATE(2006,-10,-35)")
        self.failUnless(val.eval(1) == 38348)

        val = self.getParsed("DATE(2006,-35,-400)")
        self.failUnless(val.eval(1) == 37221)                

        # check that the formatting works
        self.failUnless(val.getImpliedFormatting(1) == 'md')

    def testDAY(self):

        val = self.getParsed("DAY(DATE(2006,5,2))")
        self.failUnless(val.eval(1) == 2)

        val = self.getParsed("DAY(DATE(045,92,29822))")
        self.failUnless(val.eval(1) == 25)

        val = self.getParsed("(DAY(DATE(1900,2,29)))")
        self.failUnless(val.eval(1) == 29)

        val = self.getParsed("DAY(0)")
        self.failUnless(val.eval(1) == 0)

        val = self.getParsed("DAY(28)")
        self.failUnless(val.eval(1) == 28)

        val = self.getParsed("""DAY("7/22/2007")""")
        self.failUnless(val.eval(1) == 22)        

        val = self.getParsed("""DAY("hi")""")
        self.checkException(val,SSValueError)        

    def testHOUR(self):

        val = self.getParsed("HOUR(0.5)")
        self.failUnless(val.eval(1) == 12)
        val = self.getParsed("""HOUR("0.5")""")
        self.failUnless(val.eval(1) == 12)

        val = self.getParsed("""HOUR("7/2/2104 10:39 a")""")        
        self.failUnless(val.eval(1) == 10)
        val = self.getParsed("""HOUR("7/2/2104 11:39 p")""")        
        self.failUnless(val.eval(1) == 23)

        val = self.getParsed("HOUR(0)")
        self.failUnless(val.eval(1) == 0)
        val = self.getParsed("HOUR(1)")
        self.failUnless(val.eval(1) == 0)
        val = self.getParsed("""HOUR("hi")""")
        self.checkException(val,SSValueError)

    def testMONTH(self):

        val = self.getParsed("MONTH(DATE(2005,12,5))")
        self.failUnless(val.eval(1) == 12)
        val = self.getParsed("MONTH(DATE(2005,1,5))")
        self.failUnless(val.eval(1) == 1)
        val = self.getParsed("MONTH(12)")
        self.failUnless(val.eval(1) == 1)
        val = self.getParsed("MONTH(60)")
        self.failUnless(val.eval(1) == 2)
        val = self.getParsed("MONTH(444444)")
        self.failUnless(val.eval(1) == 11)
        val = self.getParsed("MONTH(444444444)")        
        self.checkException(val,SSOutOfRangeError)
        val = self.getParsed("""MONTH("March 2006")""")
        self.failUnless(val.eval(1) == 3)
        val = self.getParsed("""MONTH("Dec 2006")""")
        self.failUnless(val.eval(1) == 12)                

    def testYEAR(self):
        val = self.getParsed("YEAR(60)")
        self.failUnless(val.eval(1) == 1900)
        val = self.getParsed("YEAR(DATE(2005,1,5))")
        self.failUnless(val.eval(1) == 2005)
        val = self.getParsed("YEAR(444444444)") 
        self.checkException(val,SSOutOfRangeError)
        val = self.getParsed("""YEAR("March 2005")""")
        self.failUnless(val.eval(1) == 2005)        

    def testMINUTE(self):
        val = self.getParsed("MINUTE(0)")
        self.failUnless(self.convertToUserDecimal(val.eval(1)) == "0")

        val = self.getParsed("MINUTE(0)")
        self.failUnless(self.convertToUserDecimal(val.eval(1)) == "0")        
        val = self.getParsed("MINUTE(234234.2444223)")
        print '******** val is *********',val.eval(1)
        self.failUnless(self.convertToUserDecimal(val.eval(1)) == "51")
        val = self.getParsed("""MINUTE("10:43 a")""")
        self.failUnless(val.eval(1) == 43)
        
    def testSECOND(self):
        val = self.getParsed("SECOND(0)")
        self.failUnless(val.eval(1) == 0)
        val = self.getParsed("""SECOND("12:43:00 a")""")        
        self.failUnless(val.eval(1) == 0)
        val = self.getParsed("""SECOND("12 a")""")        
        self.failUnless(val.eval(1) == 0)
        val = self.getParsed("SECOND(0.5)")        
        self.failUnless(val.eval(1) == 0)
        val = self.getParsed("""SECOND("9:04:54 p")""")        
        self.failUnless(val.eval(1) == 54)
        val = self.getParsed("SECOND(0.8784)")
        print '********* val *********',val.eval(1)
        # excel actual says this is 54 and rounds up. hmm.
        self.failUnless(val.eval(1) == 53)                                

    

    def testDATEVALUE(self):
        val = self.getParsed("""DATEVALUE("3/15/2005")""")
        self.failUnless(val.eval(1) == 38426)
        val = self.getParsed("""DATEVALUE("march 5")""")
        # specific to 2006!!!
        self.failUnless(val.eval(1) == 38781)
        val = self.getParsed("""DATEVALUE("hi")""")        
        self.checkException(val,SSValueError)
        val = self.getParsed("""DATEVALUE("4.5")""")        
        self.checkException(val,SSValueError)

        val = self.getParsed("""DATEVALUE("10:30 p")""")
        self.failUnless(val.eval(1) == 0)

    def testTIMEVALUE(self):
        val = self.getParsed("""TIMEVALUE("3/15/2005")""")
        self.failUnless(val.eval(1) == 0)
        val = self.getParsed("""TIMEVALUE("3/15/2005 12 PM")""")
        self.failUnless(val.eval(1) == 0.5)

    def testTIME(self):
        val = self.getParsed("TIME(61,23243,12242)")
        self.failUnless(self.roundedResult(val.eval(1)) == "0.8243")
        val = self.getParsed("TIME(0,0,0)")
        self.failUnless(val.eval(1) == 0)
        val = self.getParsed("TIME(23,59,59)")
        # this actually because we are rounding to 4 decimal places in the test
        self.failUnless(self.roundedResult(val.eval(1)) == "1.0000")
        val = self.getParsed("TIME(23,59,100)")
        self.failUnless(self.roundedResult(val.eval(1)) == "0.0005")        
        val = self.getParsed("TIME(2e9,3,3)")
        self.checkException(val,SSOutOfRangeError)
        val = self.getParsed("TIME(-1,3,3)")
        self.checkException(val,SSOutOfRangeError)                

    def testWEEKDAY(self):
        # test for stupid leap yar bug
        val = self.getParsed("WEEKDAY(DATE(1900,2,29))")
        self.failUnless(val.eval(1) == 4)
        val = self.getParsed("WEEKDAY(DATE(1900,2,29),2)")
        self.failUnless(val.eval(1) == 3)
        val = self.getParsed("WEEKDAY(DATE(1900,2,29),3)")
        self.failUnless(val.eval(1) == 2)
        val = self.getParsed("""WEEKDAY("May 4, 2006")""")
        self.failUnless(val.eval(1) == 5)
        val = self.getParsed("""WEEKDAY("May 4, 2006",2)""")
        self.failUnless(val.eval(1) == 4)
        val = self.getParsed("""WEEKDAY("May 4, 2006",3)""")
        self.failUnless(val.eval(1) == 3)
        val = self.getParsed("""WEEKDAY("May 7, 2006")""")
        self.failUnless(val.eval(1) == 1)        
        val = self.getParsed("""WEEKDAY("May 7, 2006",2)""")
        self.failUnless(val.eval(1) == 7)                
        val = self.getParsed("""WEEKDAY("May 7, 2006",3)""")
        self.failUnless(val.eval(1) == 6)
        val = self.getParsed("""WEEKDAY("May 7, 2006",19)""")
        self.checkException(val,BadArgumentsError)

suitelist = [timeFunctionsTestCase]


if __name__ == '__main__': testmain(suitelist)
