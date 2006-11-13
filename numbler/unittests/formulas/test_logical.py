
from numbler.unittests.testtools import *

class logicalTestCase(formulaTestCase):

    def testAND(self):
        val = self.getParsed("AND(3=3,4=4)")
        self.failUnless(val.eval(1) == True)
        val = self.getParsed("AND(3=3,4=5)")
        self.failUnless(val.eval(1) == False)
        
    def testOR(self):
        val = self.getParsed("OR(3=3,4=4)")
        self.failUnless(val.eval(1) == True)
        val = self.getParsed("OR(3=3,4=5)")
        self.failUnless(val.eval(1) == True)
        val = self.getParsed("OR(FALSE,TRUE)")
        self.failUnless(val.eval(1) == True)
        val = self.getParsed("OR(FALSE,FALSE)")
        self.failUnless(val.eval(1) == False)                        

    def testNOT(self):
        val = self.getParsed("NOT(OR(FALSE,FALSE))")
        self.failUnless(val.eval(1) == True)
        val = self.getParsed("NOT(FALSE)")
        self.failUnless(val.eval(1) == True)                                        
        val = self.getParsed("NOT()")
        self.checkException(val,SSValueError)

    def testTRUE(self):
        val = self.getParsed("TRUE()")
        self.failUnless(val.eval(1) == True)

    def testFALSE(self):
        val = self.getParsed("False()")
        self.failUnless(val.eval(1) == False)        
        

    def testIF(self):
        val = self.getParsed("IF(3=3,TRUE,FALSE)")
        self.failUnless(val.eval(1) == True)
        val = self.getParsed("IF(3=4,TRUE,FALSE)")
        self.failUnless(val.eval(1) == False)
