#!/bin/env python

from numbler.unittests.testtools import *

class NPVTestCase(formulaTestCase):
    """
    TODO: not an exhaustive case yet.
    """
    

    def testNPV(self):

        val = self.getParsed("ROUND(NPV(10%,-100,10,200),4)")
        self.failUnless(val.eval(1) == 67.6183)

class IRRTestCase(sheetTester):
    sheets = [
        {
        'name':'irrsheet',
        'cells':[
        ('a1','-70000'),
        ('a2','12000'),
        ('a3','15000'),
        ('a4','18000'),
        ('a5','21000'),
        ('a6','26000'),
        ('b1','=IRR(A1:A5)'),
        ('b2','=IRR(A1:A6)'),
        ('b3','=IRR(a1:a3,-10%)'),
        ('b4','=NPV(IRR(a1:a6),a1:a6)')
        ]
        }]


    def testIRR(self):
        sht = self.sheetHandles['irrsheet']
        self.failUnless(self.dispvalue(sht,'b1'),'2%')
        self.failUnless(self.dispvalue(sht,'b2'),'9%')
        self.failUnless(self.dispvalue(sht,'b2'),'-44%')                

        print 'b4 val is',self.value(sht,'b4'),self.dispvalue(sht,'b4')


class PMTTestCase(sheetTester):
    sheets = [
        {
        'name':'pmtsheet',
        'cells':[
        ('a2','8%'),
        ('a3','10'),
        ('a4','10000'),
        ('b2','=PMT(a2/12,a3,a4)'),
        ('b3','=PMT(a2/12,a3,a4,0,1)')
        ]
        }
        ]

    def testPMT(self):
        sht = self.sheetHandles['pmtsheet']
        self.failUnless(self.dispvalue(sht,'b2') == '($1,037.03)')
        self.failUnless(self.dispvalue(sht,'b3') == '($1,030.16)')        
        
        
