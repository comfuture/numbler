#!/usr/bin/env python

from numbler.unittests.testtools import *

class ifTestCase(formulaTestCase):
    """
    test basic boolean functionality
    """

    def testSuccessNoFailureArg(self):
        pass

    def testSuccessWithFailureArg(self):
        pass

    def testFailureWithFailureArg(self):
        pass

    def testFailureWithTrailingComma(self):
        pass

    def testFailureWithNoFailureArg(self):
        pass

    def testNestedIfs(self):
        pass

    def testWrongArguments(self):
        pass


class SumIfTestCase(sheetTester):

    sheets = [
        {'name':'sumsheet',
         'cells':[
        ('a1','100'),
        ('b1','-5'),
        ('a44','$100'),
        ('a45','hi'),
        ('b45','10'),
        ('a99','105'),
        ('b99','44'),
        ('c1','=SUMIF(a1:a100,">=100")'),
        ('c2','=SUMIF(a1:a100,">=100",b1:B100)'),
        ('c3','=SUMIF(a1:a100,"hi",b1:B100)'),
        ('c4','=SUMIF(A:A,"<=1000000000",B:B)'),
        ('c5','=SUMIF(1:1,"<>0")')
        ]
        },
        {
        'name':'refsumsheet',
        'cells':[
        ('a44','="hi"&" "&"there"'),
        ('BB44','$1,234.33'),
        ('b1','=SUMIF(a44,"hi there",bb44)'),
        ('b2','=SUMIF(a44,"hi there",bb:bb)'),     
        ]
        },
        {
        'name':'matrixsheet',
        'cells':[
        ]
        },
        {
        'name':'sumifnoteq',
        'cells':[
        ('b1','100'),
        ('b2','100'),
        ('d1','=SUMIF(a1:a2,"<>0",b1:b2)'),
        ('d2','=SUMIF(a:a,"<>0",b:b)'),        
        ]
        }
        ]
        


    def testSumIfBasic(self):
        """ basic SumIf test cases """
        shtH = self.sheetHandles['sumsheet']
        # no sum range
        self.failUnless(self.value(shtH,'c1') == 305)
        # test basic SUM range
        self.failUnless(self.value(shtH,'c2') == 39)

        # test that string sums works
        self.failUnless(self.value(shtH,'c3') == 10)                

        # column reference
        self.failUnless(self.value(shtH,'c4') == 39)

        # row reference
        self.failUnless(self.value(shtH,'c5') == 400) # includes value from c1     

    def testSumIfCellREfs(self):
        """ test sumif with cell references intead of ranges """
        shtH = self.sheetHandles['refsumsheet']
        self.failUnless(self.value(shtH,'b1') == 1234.33)
        self.failUnless(self.value(shtH,'b2') == 0)

    def testSumIfNotEqSumRange(self):
        """ test sum if with a not equal value and a sum range """
        shtH = self.sheetHandles['sumifnoteq']
        # TODO: fix these
        #
        #self.failUnless(self.value(shtH,'d1') == 200)
        #self.failUnless(self.value(shtH,'d2') == 200)        

    def testNegativeCases(self):
        """ test that values are correctly passed """

    def testMatrixCases(self):
        """ test adding up multiple rows """
        
        
##    def testSumIfWithAlphas(self):
##        """ test sumIf with character strings"""
##        pass
##    def testRangeError(self):
##        """ verify that a range is required for both the source range and the sum range"""
##        pass

##    def testSumIfWithAlphaNumerics(self):
##        """ test sumIf with values that look like 14!"""
##        pass

##    def testSumIfWithPercentages(self):
##        """ test sumif with a range of percentages"""
##        pass

##    def testSumIfWIthStringConcat(self):
##        """ tst sumif with "="&"apple" semantics """

class CountIfTestCase(sheetTester):
    """ test countIf formulas """


    sheets = [{
        'name':'countsheet',
        'cells':[
        ('a100','55'),
        ('a3223','234.56e-1'),
        ('a30000','$1.0005'),
        ('a14','-50'),
        ('b1','=COUNTIF(a1:a100,0)'),
        ('b2','=COUNTIF(a1:a100,">0")'),
        ('b3','=COUNTIF(a1:a100,"<0")'),
        ('b4','=COUNTIF(a:a,"<2e99")'),
        ('c1','United States'),
        ('c2','united states'),
        ('c3','Japan'),
        ('d1','=COUNTIF(C:C,"United States")'),
        ('d2','=COUNTIF(C:C,"United"&" "&"States")'),
        ('d3','=COUNTIF(C:C,"united states")'),
        # row range tests
        ('r50','=DATE(2010,5,5)'),
        ('t50','=SUM(1,2,94)'),
        ('CC50','93000%'),
        ('r51','=COUNTIF(50:50,"5/5/2010")'),
        ('r52','=COUNTIF(50:50,"<=93000%")'),
        ('r53','=COUNTIF(50:50,">94")'),
        ('z1','$444.55'),
        ('z2','bling'),
        ('z3','1.10000000'),
        ('z4','=COUNTIF(z1:z3,444.55)'),
        ('z5','=COUNTIF(z1:z3,">1")'),
        ('z6','=COUNTIF(A:A,SUM(54,1))'),
        ]
        }]

    def testCountBasic(self):
        """ count a number of cells that match the criteria"""
        shtH = self.sheetHandles['countsheet']

        # test some basic counts
        self.failUnless(self.value(shtH,'b1') == 0)
        self.failUnless(self.value(shtH,'b2') == 1)
        self.failUnless(self.value(shtH,'b3') == 1)
        self.failUnless(self.value(shtH,'b4') == 4)                

        # string tests
        self.failUnless(self.value(shtH,'d1') == 2)
        self.failUnless(self.value(shtH,'d2') == 2)
        self.failUnless(self.value(shtH,'d3') == 2)                

        # test row range
        self.failUnless(self.value(shtH,'r51') == 1)
        self.failUnless(self.value(shtH,'r52') == 2)
        self.failUnless(self.value(shtH,'r53') == 3)                        

        # string match
        
        #currency match
        self.failUnless(self.value(shtH,'z4') == 1)
        self.failUnless(self.value(shtH,'z5') == 2)        

        # test formulas as the second arg
        self.failUnless(self.value(shtH,'z6') == 1)
        

    def testCountFull(self):
        """ test that something like =COUNTIF(A:D,"<>7") returns
        a full count of cells. (this currently doesn't work
        """
        pass

    


suitelist = [ifTestCase,SumIfTestCase,CountIfTestCase]


if __name__ == '__main__': testmain(suitelist)
