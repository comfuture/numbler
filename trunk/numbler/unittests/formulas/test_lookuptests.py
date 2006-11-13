#!/usr/bin/env python

from numbler.unittests.testtools import *

class miscLookupTestCase(sheetTester):
    sheets = [
        {
        'name':'misclookups',
        'cells':[
        ('a192','=ROW()'),
        ('a193','=ROW(Z65344)'),
        ('b1','=ROW("hi")'),
        ('b2','=ROW(Q103:BB494)'),
        ('bb9304','=COLUMN()'),
        ('c1','=COLUMN(R5)'),
        ('c2','=COLUMN(R5:Z9)'),
        ('c3','=COLUMN("hi")')
        ]
        }
        ]
    def testMiscFuncs(self):
        sht = self.sheetHandles['misclookups']
        self.failUnless(self.value(sht,'a192') == 192)
        self.failUnless(self.value(sht,'a193') == 65344)
        self.checkException(sht,'b1',BadArgumentsError)
        self.failUnless(self.value(sht,'b2') == 103)
        
        self.failUnless(self.value(sht,'bb9304') == 54)
        self.failUnless(self.value(sht,'c1') == 18)
        self.failUnless(self.value(sht,'c2') == 18)
        self.checkException(sht,'c3',BadArgumentsError)        
        

class matchTestCase(sheetTester):
    sheets = [
        {
        'name':'matchtestsheet',
        'cells':[
        # basic test cells
        ('a10','rasp'),
        ('a11','dingle'),
        ('a12','45'),
        ('a19','=a12'),
        ('a22','=SUM(a12,45)'),
        ('a100','rasp'),
        ('a101','dingle'),
        # horizontal data
        ('aa100','dang'),
        ('ab100','=SUM(3,4,5)'),
        ('ag100','radish'),
        ('ar100','azb'),
        ('b1','=MATCH("rasp",a1:a1000,0)'),
        ('b2','=MATCH(90,a1:a1000,0)'),
        ('b3','=MATCH(1001,a1:a1000,0)'),          
        # largest value
        ('c1','=MATCH("dinglz",a1:a1000)'),
        ('c2','=MATCH("dinglz",a1:a1000,1)'),
        ('c3','=MATCH(46,a1:a1000)'),
        ('c4','=MATCH(45,a1:a1000,1)'),
        ('c5','=MATCH("a",a1:a1000,1)'),
        ('c6','=MATCH(-1,a1:a1000,1)'),                

        # smallest value
        ('d1','=MATCH("aza",100:100,-1)'),
        ('d2','=MATCH(2e10,100:100,-1)'),
        ('d3','=MATCH("dang",100:100,-1)'),                

        # test case sensitivity
        ('d4','=MATCH("Dang",100:100,-1)'),

        ('d5','=MATCH("Dang",a1:B19)')
        ]
        }
        ]

    def testMatch(self):
        sht = self.sheetHandles['matchtestsheet']
        v = self.value(sht,'b1')

        # equiv tests
        self.failUnless(self.value(sht,'b1') == 10)
        self.failUnless(self.value(sht,'b2') == 22)       
        self.checkException(sht,'b3',SSNotAvailable)


        # less than tests
        self.failUnless(self.value(sht,'c1') == 101)
        self.failUnless(self.value(sht,'c2') == 101)
        self.failUnless(self.value(sht,'c3') == 19)
        self.failUnless(self.value(sht,'c4') == 19)
        self.failUnless(self.value(sht,'c5') == 22)
        self.checkException(sht,'c6',SSNotAvailable)
        #print '*** c5 is ',self.value(sht,'c5')

        # greater than tests

        self.failUnless(self.value(sht,'d1') == int(Col('ar')))
        print '** d2 is ',self.value(sht,'d2')
        self.checkException(sht,'d2',SSNotAvailable)
        self.failUnless(self.value(sht,'d3') == int(Col('aa')))
        self.failUnless(self.value(sht,'d4') == int(Col('aa')))
        self.checkException(sht,'d5',SSRefError)        




        # failure tests

class indexTestCase(sheetTester):
    sheets = [
        {
        'name':'indexsheet',
        'cells':[
        ('a2','hello'),
        ('a5','11-feb'),
        ('b1','71.64'),
        ('b3','$5'),
        ('c2','bing'),
        ('c6','23.94'),
        ('e1','=INDEX(A1:D1,2)'),
        ('e2','=INDEX(A1:A7,2)'),
        ('e3','=INDEX(A1:D1,1,2)'),
        ('e4','=INDEX(A1:A7,2,1)'),
        ('e5','=INDEX(A1:A7,2,0)'),
        # cases where we should get 0
        ('e6','=INDEX(A1:C6,1,1)'),
        ('e7','=INDEX(A1:C6,6,3)'),        

        # out of range cases
        ('e50','=INDEX(A1:C6,50,1)'),
        ('e51','=INDEX(A1:C6,1,50)'),
        ('e52','=INDEX(A1:C6,50)'),                
        

        # negative cases

        ('e100','=INDEX()'),
        ('e101','=INDEX(A1:A7,-1)'),
        ('e102','=INDEX(A1:C7,-1,-1)'),
        ('e103','=INDEX("froogle",-1,-1)'),                
        ]
        }
        ]
    
    def testIndexFunction(self):
        sht = self.sheetHandles['indexsheet']        
        self.failUnless(self.value(sht,'e1') == 71.64)
        self.failUnless(self.value(sht,'e2') == 'hello')
        self.failUnless(self.value(sht,'e3') == 71.64)
        self.failUnless(self.value(sht,'e4') == 'hello')
        self.failUnless(self.value(sht,'e5') == 'hello')
        self.failUnless(self.value(sht,'e6') == 0)
        self.failUnless(self.value(sht,'e7') == 23.94)

        # out of range cases
        self.checkException(sht,'e50',SSRefError)
        self.checkException(sht,'e51',SSRefError)
        self.checkException(sht,'e52',SSRefError)

        # negative cases
        self.checkException(sht,'e100',WrongNumArgumentsError)
        self.checkException(sht,'e101',SSValueError)
        self.checkException(sht,'e102',SSValueError)
        self.checkException(sht,'e103',SSValueError)                        

class vlookupTestCase(sheetTester):
    sheets = [
        {
        'name':'vlookupsheet',
        'cells':[
        ('a1','apple'),
        ('a5','bananna'),
        ('a10','boozle'),
        ('a12','zang!'),
        ('b1','5'),
        ('b5','10'),
        ('b10','15'),
        ('c1','=VLOOKUP("bingo",a1:B10,2)'),
        ('c2','=VLOOKUP("bingo",a1:B10,1)'),
        ('c3','=VLOOKUP("aaa",a1:B10,2)'),
        ('c4','=VLOOKUP("red",a1:B12,2)'),
        ('c5','=VLOOKUP("zzz",a1:B12,2)'),        
        
        ]
        },
        {
        'name':'exactmatch',
        'cells':[
        ('a1','dinky'),
        ('a2','winky'),
        ('b2','21'),
        ('a3','pickle'),
        ('a4','orange'),
        ('b4','$3.01'),
        ('a5','jello'),
        ('a6','5'),
        ('a7','103'),
        ('b7','ding!'),
        ('a8','44'),
        ('b8','8'),
        ('c1','=VLOOKUP(44,a1:b8,2,FALSE)'),
        ('c2','=VLOOKUP("bazle",a1:b8,2,FALSE)'),
        ('c3','=VLOOKUP(103,a1:b8,2,FALSE)'),
        ('c4','=VLOOKUP(44,a1:b8,2,FALSE)'),
        ('c5','=VLOOKUP("pickle",a1:b8,2,FALSE)')
        ]
        }
        ]

    def testApproxLookup(self):
        sht = self.sheetHandles['vlookupsheet']

        self.failUnless(self.value(sht,'c1') == 10)
        self.failUnless(self.value(sht,'c2') == 'bananna')        
        self.checkException(sht,'c3',SSNotAvailable)
        self.failUnless(self.value(sht,'c4') == 15)
        self.failUnless(self.value(sht,'c5') == 0)                        
        #self.checkException(sht,'c2',SSNumError)
        #self.checkException(sht,'c6',SSNumError)        

    def testExactMatch(self):
        sht = self.sheetHandles['exactmatch']
        self.failUnless(self.value(sht,'c1') == 8)
        self.checkException(sht,'c2',SSNotAvailable),
        print 'c3 value is ',self.value(sht,'c3')
        self.failUnless(self.value(sht,'c3') == "ding!")
        self.failUnless(self.value(sht,'c4') == 8)
        self.failUnless(self.value(sht,'c5') == 0)
        


class hlookupTestCase(sheetTester):
    sheets = [
        {
        'name':'hlookupsheet',
        'cells':[
        ('a1','Axles'),
        ('b1','Bearings'),
        ('c1','Bolts'),
        ('a2','4'),
        ('b2','4'),
        ('c2','9'),
        ('a3','5'),
        ('b3','7'),
        ('c4','10'),
        ('a4','6'),
        ('b4','8'),
        ('c4','11'),
        ('e1','=HLOOKUP("Axles",A1:C4,2,TRUE)'),
        ('e2','=HLOOKUP("Bearings",a1:C4,3,FALSE)'),
        ('e3','=HLOOKUP("B",A1:C4,3,TRUE)'),
        ('e4','=HLOOKUP("Bolts",A1:C4,4)'),
        ]
        }
        ]

    def testHlookup(self):
        sht = self.sheetHandles['hlookupsheet']
        self.failUnless(self.value(sht,'e1') == 4)
        self.failUnless(self.value(sht,'e2') == 7)
        self.failUnless(self.value(sht,'e3') == 5)
        self.failUnless(self.value(sht,'e4') == 11)        

suitelist = [vlookupTestCase]


if __name__ == '__main__': testmain(suitelist)
