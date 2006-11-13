#!/usr/bin/env python

from numbler.utils import simplecell
from numbler.unittests.testtools import *
from twisted.internet.defer import deferredGenerator,waitForDeferred
from numbler.utils import yieldDef

class formulaGenTestCase(sheetTester):
    """ tests the formula generation code. This is the functionality
    where a user can select a region of cells and generate a formula from
    the region"""


    sheets = [{
        'name':'matrix',
        'cells':[
        ('a1','1'),
        ('b1','2'),
        ('c1','3'),
        ('a2','4'),
        ('b2','5'),
        ('c2','6')
        ]
        }]


    def testRightSum(self):
        sht = self.sheetHandles['matrix']
        sht().genSelectionFormulas(self.getCell(sht,"a1"),
                                   self.getCell(sht,"d1"),'SUM')
        val = self.value(sht,"d1")
        self.failUnless(val == 6)

    def testMultiRightSum(self):
        sht = self.sheetHandles['matrix']        
        sht().genSelectionFormulas(self.getCell(sht,"a1"),
                                 self.getCell(sht,"d2"),'SUM')        
        val = self.value(sht,"d1")
        val2 = self.value(sht,"d2")
        self.failUnless(val == 6 and val2 == 15)

    def testMultiRightSumWithGetData(self):
        sht = self.sheetHandles['matrix']                
        sht().genSelectionFormulas(self.getCell(sht,"a1"),
                                   self.getCell(sht,"d2"),'SUM')        
        val1 = self.getCell(sht,"d1")().getData()
        val2 = self.getCell(sht,"d2")().getData()
        self.failUnless(val1[u'text'] == u'6' and val2[u'text'] == u'15')        



class pasteTestCase(sheetTester):
    sheets = [
        {
        'name':'simplepaste',
        'cells':[
        ("a1","1"),
        ("a2","2"),
        ("a3","3"),
        ("b6","12"),
        ("a4","4"),
        ("a5","5"),
        ("a6","6"),
        ("a7","=SUM(a1:a6)"),
        ("b1","7"),
        ("b2","8"),
        ("b3","9"),
        ("b4","10"),
        ("b5","11"),
        ("b6","12")
        ]
        }]

    def testPasteFromExistingCell(self):
        sht = self.sheetHandles['simplepaste']
        rng = cell.CellRange(Col('a'),7,Col('a'),7)
        sht().paste(sht,rng,Col('b'),7)
        res = self.getCell(sht,'b7')().getData()
        self.failUnless(res['text'] == u'57')

    def testPastFromBuffer(self):
        sht = self.sheetHandles['simplepaste']        
        cellbuf = [
            simplecell({'formula':'100','col':Col('g'),'row':'1'}),
            simplecell({'formula':'200','col':Col('g'),'row':'2'}),
            simplecell({'formula':'300','col':Col('g'),'row':'3'}),
            simplecell({'formula':'400','col':Col('g'),'row':'4'}),            
            simplecell({'formula':'500','col':Col('g'),'row':'5'}),
            simplecell({'formula':'600','col':Col('g'),'row':'6'}),
            simplecell({'formula':'=SUM(G1:G6)','col':Col('g'),'row':'7'})
            ]

        sht().pasteFromBuffer(sht,cellbuf,Col('R'),1)
        res = self.getCell(sht,'R7')().getData()
        self.failUnless(res['text'] == u'2100')
           

class ConcatTestCase(sheetTester):
    """ test case for string concat operations """

    def testLiteralConcat(self):
        pass

    def testRefConcat(self):
        pass

    def testNumericConcat(self):
        pass

    def testNumericRefConcat(self):
        pass

class MoveRegionTestCase(sheetTester):

    def testMoveRegion(self):
        """ test moving a region of cells"""
        pass

    def testUndoMoveRegion(self):
        """  test undoing a move region """
        pass


class CutCellTestCase(sheetTester):
    sheets = [
        {
        'name':'cutsheet',
        'cells':[
        ("a1","=SUM(B2:C9)"),
        ("b2","45"),
        ("c3","45"),
        ("b8","90")
        ]
        }]


    def testcutRegionCellUpdate(self):
        sht = self.sheetHandles['cutsheet']

        verifyValues = [
            ("a1",0)
            ]

        rng = cell.CellRange.getInstance(Col("b"),Row(2),Col("c"),Row(9))
        d = sht().deleteCells(rng)
        d.addCallback(self.verifyNotification,sht,verifyValues)
        return d


class BulkDeleteTestCase(sheetTester):

    colA = [('a' + str(x),str(x)) for x in range(1,150)]
    colB = [('b' + str(x),'=a' + str(x)) for x in range(1,150)]
    colC = [('c' + str(x),'=SUM(a%d:b%d)' % (x,x)) for x in range(1,150)]

    precompcells = colA + colB + colC + [('d1','=SUM(a:a)')]
    sheets = [{
        'name':'bigdeletetest',
        'cells':precompcells
        }]

    def testDeleteSums(self):
        """ test delting a big bunch of cells """
        sht = self.sheetHandles['bigdeletetest']
        return sht().deleteCellHandleArray(cell.CellRange(Col('c'),1,Col('c'),150).getCellHandles(sht))

    def testDeleteCummulativeSum(self):
        """ test delting a big bunch of cells """
        sht = self.sheetHandles['bigdeletetest']
        return sht().deleteCellHandleArray(cell.CellRange(Col('d'),1,Col('d'),150).getCellHandles(sht))

    def testDeleteRefs(self):
        """ test delting a big bunch of cells """
        sht = self.sheetHandles['bigdeletetest']
        return sht().deleteCellHandleArray(cell.CellRange(Col('b'),1,Col('b'),150).getCellHandles(sht))

    def testDeleteSrc(self):
        """ test delting a big bunch of cells """
        sht = self.sheetHandles['bigdeletetest']
        return sht().deleteCellHandleArray(cell.CellRange(Col('a'),1,Col('a'),150).getCellHandles(sht))            

suitelist = [formulaGenTestCase,pasteTestCase,BulkDeleteTestCase]


if __name__ == '__main__': testmain(suitelist)

