#!/usr/bin/env python

from numbler.unittests.testtools import *

class booleanBasic(formulaTestCase):
    """
    test basic boolean functionality
    """
    def testTrue(self):
        val = self.getParsed("true")
        self.failUnless(val.eval(1) == True)

        val = self.getParsed("truE")
        self.failUnless(val.eval(1) == True)

        val = self.getParsed("TRUE")
        self.failUnless(val.eval(1) == True)        

    def testFalse(self):
        val = self.getParsed("false")
        self.failUnless(val.eval(1) == False)

        val = self.getParsed("False")
        self.failUnless(val.eval(1) == False)

        val = self.getParsed("FALSE")
        self.failUnless(val.eval(1) == False)                
    
    def testTrueFormula(self):
        val = self.getParsed("TRUE()")
        self.failUnless(val.eval(1) == True)

        val = self.getParsed("True()")
        self.failUnless(val.eval(1) == True)        

    def testFalseFormula(self):
        val = self.getParsed("False()")
        self.failUnless(val.eval(1) == False)

        val = self.getParsed("FALSE()")
        self.failUnless(val.eval(1) == False)                

    def testTrueAsFormula(self):
        self.expectParseFailure("TRUE(34)",SSValueError)

class booleanMath(formulaTestCase):

    def testBoolSums(self):
        val = self.getParsed("sum(false,true,TRUE())")
        self.failUnless(val.eval(1) == 2)

    def testBoolCounta(self):
        val = self.getParsed("counta(false,true,1)")
        self.failUnless(val.eval(1) == 3)
    
suitelist = [booleanBasic,booleanMath]


if __name__ == '__main__': testmain(suitelist)
