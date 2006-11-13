#!/bin/env python

from numbler.unittests.testtools import *


class textFormulaTestCase(formulaTestCase):

    def testProper(self):
        val = self.getParsed('Proper("hi there how are you?")')
        self.failUnless(val.eval(1) == "Hi There How Are You?")

        val = self.getParsed('Proper("THIS IS OBNOXIOUS TEXT")')
        self.failUnless(val.eval(1) == "This Is Obnoxious Text")

        # pass through case
        val = self.getParsed('Proper(45)')
        self.failUnless(val.eval(1) == 45)

        val = self.getParsed('Proper()')
        self.checkException(val,WrongNumArgumentsError)
        val = self.getParsed('Proper("hi","there","how","you")')
        self.checkException(val,WrongNumArgumentsError)

        val = self.getParsed('Proper("hi"&" "&"there"&" "&"how"&" "&"you")')
        self.failUnless(val.eval(1) == 'Hi There How You')

    def testConcatenate(self):
        val = self.getParsed('Concatenate("Hi"," ","there,"," ","how"," ","are"," ","you?")')
        self.failUnless(val.eval(1) == 'Hi there, how are you?')
        val = self.getParsed('Concatenate()')
        self.checkException(val,WrongNumArgumentsError)
        val = self.getParsed('Concatenate("bling",44,"boozle")')
        self.failUnless(val.eval(1) == 'bling44boozle')
        val = self.getParsed('Concatenate("bling"&"44","boozle")')
        self.failUnless(val.eval(1) == 'bling44boozle')                


    def testLEFT(self):
        val = self.getParsed('left("hi there",3)')
        self.failUnless(val.eval(1) == 'hi ')
        val = self.getParsed('left("hi there",1e9)')
        self.failUnless(val.eval(1) == 'hi there')
        val = self.getParsed('left("hi there",0)')
        self.failUnless(val.eval(1) == '')
        val = self.getParsed('left("hi there",-1)')
        self.checkException(val,BadArgumentsError)        

    def testRIGHT(self):
        val = self.getParsed('RIGHT("hey there dog",3)')
        self.failUnless(val.eval(1) == 'dog')
        val = self.getParsed('RIGHT("hey there dog",1)')
        self.failUnless(val.eval(1) == 'g')        
        val = self.getParsed('RIGHT("hey there dog",0)')
        self.failUnless(val.eval(1) == '')
        val = self.getParsed('RIGHT("hey there dog",100)')
        self.failUnless(val.eval(1) == 'hey there dog')
        val = self.getParsed('RIGHT("hey there dog",-1)')
        self.checkException(val,BadArgumentsError)                
        

    def testHYPERLINK(self):
        val = self.getParsed('HYPERLINK("http://boston.com")')
        print 'val is ',val.eval(1)
        self.failUnless(val.eval(1) == '<a href="http://boston.com" target="numblerwin">http://boston.com</a>')
        
class textSheetTestCase(sheetTester):
    sheets = [
        {
        'name':'indirectsheet',
        'cells':[
        ('d5','wowza'),
        ('d6','d5'),
        ('d7','d6'),
        ('a1','=INDIRECT("d5")'),
        ('a2','=INDIRECT(d6)'),
        ('a3','=INDIRECT(d7)'),
        ('a4','=INDIRECT("D"&"5")')
        ]
        }
        ]

    def testIndirect(self):
        sht = self.sheetHandles['indirectsheet']

        self.failUnless(self.value(sht,'a1') == 'wowza')
        self.failUnless(self.value(sht,'a2') == 'wowza')
        self.failUnless(self.value(sht,'a3') == 'd5')
        self.failUnless(self.value(sht,'a4') == 'wowza')                        


suitelist = [textFormulaTestCase,textSheetTestCase]


if __name__ == '__main__': testmain(suitelist)
    
