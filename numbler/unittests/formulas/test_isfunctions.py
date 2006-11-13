#!/usr/bin/env python

from numbler.unittests.testtools import *


class isFunctionsTestCase(sheetTester):
    sheets = [
        {
        'name':'isfunctestsheet',
        'cells':[
        ('a1','5'),
        # don't put anything in a10
        ('b1','=ISBLANK(a1)'),
        ('b2','=ISBLANK(a10)'),
        ('b3','=ISBLANK(4/0)'),

        # is eerror
        ('c1','=C2'),
        ('c2','=C1'),
        ('c3','=SUM(1,2,3)'),
        ('c4','=4/0'),
        ('d1','=ISERROR(c1)'),
        ('d2','=ISERROR(c3)'),
        ('d3','=ISERROR(a1)'),
        ('d4','=ISERROR(c4)'),
        ('d5','=ISERROR(4/0)'),
        # alias
        ('d6','=ISERR(4/0)'),
        # islogical
        ('f1','=ISLOGICAL(d1)'),
        ('f2','=ISLOGICAL(c3)'),
        ('f3','=ISLOGICAL(0)'),
        ('f4','=ISLOGICAL(1)'),
        ('f5','=ISLOGICAL(TRUE)'),
        ('f6','=ISLOGICAL(false)'),
        ('f7','=ISLOGICAL(4/0)'),
        # isnontext
        ('g1','Hi there'),
        ('g2','35'),
        ('g3','"35"'),
        ('g4','="foo"&" "&"bar"'),
        ('g5','=g2'),
        ('h1','=ISNONTEXT(g1)'),
        ('h2','=ISNONTEXT(g2)'),
        ('h3','=ISNONTEXT(g3)'),
        ('h4','=ISNONTEXT(g4)'),
        ('h5','=ISNONTEXT(g5)'),
        ('h6','=ISNONTEXT(g6)'),
        ('h7','=ISNONTEXT(35.34)'),
        ('h8','=ISNONTEXT(4/0)'),
        ('i1','44'),
        ('i2','$3.4'),
        ('i3','2e5'),
        ('i4','4,000'),
        ('i5','TRUE'),
        ('i6','FALSE'),
        ('i7','hi there'),
        ('i8','4/0'),
        ('j1','=ISNUMBER(i1)'),
        ('j2','=ISNUMBER(i2)'),
        ('j3','=ISNUMBER(i3)'),
        ('j4','=ISNUMBER(i4)'),
        ('j5','=ISNUMBER(i5)'),
        ('j6','=ISNUMBER(i6)'),
        ('j7','=ISNUMBER(i7)'),
        ('j8','=ISNUMBER(i8)'),
        ('k1','=ISREF(a1)'),
        ('k2','=ISREF(1:2)'),
        ('k3','=ISREF(a:q)'),
        ('k4','=ISREF(INDIRECT("q9"))'),
        ('k5','=ISREF(INDIRECT(q9))'),
        ('k6','=ISREF(INDIRECT(4/0))'),
        ('k7','=ISREF(a9:b99)'),
        # is text
        ('l1','=ISTEXT("hi")'),
        ('l2','=ISTEXT("hi"&" "&"there")'),
        ('l3','=ISTEXT(45)'),
        ('l4','=ISTEXT(l1)'),
        ('l5','=ISTEXT(4/0)'),                
        # isodd
        ('m1','=ISODD(5)'),
        ('m2','=ISODD(1)'),
        ('m3','=ISODD(-1)'),
        ('m4','=ISODD(-9.00001)'),
        ('m5','=ISODD("hi")'),
        ('m6','=ISODD(0)'),
        ('m7','=ISODD(10)'),                                        
        # iseven
        ('n1','=ISEVEN(4)'),
        ('n2','=ISEVEN(5)'),
        ('n3','=ISEVEN("hi")')
        ]
        }]

    def testIsFunctions(self):
        """
        test the support is functions
        """
        sht = self.sheetHandles['isfunctestsheet']

        self.failUnless(self.value(sht,'b1') == False)
        self.failUnless(self.value(sht,'b2') == True)
        self.failUnless(self.value(sht,'b3') == False)        

        # iserror
        self.failUnless(self.value(sht,'d1') == True)
        self.failUnless(self.value(sht,'d2') == False)
        self.failUnless(self.value(sht,'d3') == False)
        self.failUnless(self.value(sht,'d4') == True)
        self.failUnless(self.value(sht,'d5') == True)        
        self.failUnless(self.value(sht,'d6') == True)        

        # islogical
        self.failUnless(self.value(sht,'f1') == True)
        self.failUnless(self.value(sht,'f2') == False)
        self.failUnless(self.value(sht,'f3') == False)
        self.failUnless(self.value(sht,'f4') == False)
        self.failUnless(self.value(sht,'f5') == True)
        self.failUnless(self.value(sht,'f6') == True)
        self.failUnless(self.value(sht,'f7') == False)

        #isnontext
        self.failUnless(self.value(sht,'h1') == False)
        self.failUnless(self.value(sht,'h2') == True)
        self.failUnless(self.value(sht,'h3') == False)
        self.failUnless(self.value(sht,'h4') == False)
        self.failUnless(self.value(sht,'h5') == True)
        self.failUnless(self.value(sht,'h6') == True)
        self.failUnless(self.value(sht,'h7') == True)
        self.failUnless(self.value(sht,'h8') == True)        

        #isnumber
        self.failUnless(self.value(sht,'j1') == True)
        self.failUnless(self.value(sht,'j2') == True)
        self.failUnless(self.value(sht,'j3') == True)
        self.failUnless(self.value(sht,'j4') == True)
        self.failUnless(self.value(sht,'j5') == False)
        self.failUnless(self.value(sht,'j6') == False)
        self.failUnless(self.value(sht,'j7') == False)
        self.failUnless(self.value(sht,'j8') == False)        
        
        # isref
        self.failUnless(self.value(sht,'k1') == True)
        self.failUnless(self.value(sht,'k2') == True)
        self.failUnless(self.value(sht,'k3') == True)
        self.failUnless(self.value(sht,'k4') == True)
        self.failUnless(self.value(sht,'k5') == False)
        self.failUnless(self.value(sht,'k6') == False)
        self.failUnless(self.value(sht,'k7') == True)

        # istext
        self.failUnless(self.value(sht,'l1') == True)
        self.failUnless(self.value(sht,'l2') == True)
        self.failUnless(self.value(sht,'l3') == False)
        self.failUnless(self.value(sht,'l4') == False)
        self.failUnless(self.value(sht,'l5') == False)
        # isodd
        self.failUnless(self.value(sht,'m1') == True)
        self.failUnless(self.value(sht,'m2') == True)
        self.failUnless(self.value(sht,'m3') == True)
        self.failUnless(self.value(sht,'m4') == True)
        self.checkException(sht,'m5',SSError)        
        self.failUnless(self.value(sht,'m6') == False)
        self.failUnless(self.value(sht,'m7') == False)

        self.failUnless(self.value(sht,'n1') == True)
        self.failUnless(self.value(sht,'n2') == False)
        self.checkException(sht,'n3',SSError)                

suitelist = [isFunctionsTestCase]


if __name__ == '__main__': testmain(suitelist)
    
