#!/usr/bin/env python

from numbler.unittests.testtools import *
from numbler.server.localedb import ParseCtx

class testFormulaInheritance(sheetTester):
    """
    test basic boolean functionality
    """

    sheets = [
        {
        'name':'sumsheet',
        'cells':[
        ('a1','5'),
        ('a2','$3'),
        ('a3','23'),
        ('a4','=SUM(a1:a3)'),
        ('a5','=a1+a2+a3'),
        ('a6','=a2'),
        ('b1','2%'),
        ('b2','3'),
        ('b3','3'),
        ('b4','=SUM(b1:b3)'),
        ('b5','=B1+B2+B3'),
        ('c1','2'),
        ('c2','2.002'),
        ('c3','$5'),
        ('c4','SUM(C1:c3)'),
        ('c5','=C1+C2+C3'),
        ('a20','$3'),
        ('b20','5%'),
        ('c20','=A20+b20'),
        ('a21','23'),
        ('b21','34'),
        ('c21','5%'),
        ('d21','=A21+B21+c21'),
        ('e21','=SUM(A21:C21)')
        ]
        }
       ]

    def testBasic(self):
        shtH = self.sheetHandles['sumsheet']

        cellI = shtH().getCellHandle(Col('a'),Row(6))()        
        f = cellI.getFormat()
        self.checkImpliedStyle(cellI,ParseCtx.currencyFormat)
        cellI = shtH().getCellHandle(Col('a'),Row(4))()
        # no currency inheritnace
        self.checkImpliedStyle(cellI,ParseCtx.defaultDecimalFormat)
        # currency inheritance
        cellI = shtH().getCellHandle(Col('a'),Row(5))()
        self.checkImpliedStyle(cellI,ParseCtx.currencyFormat)

        cellI = shtH().getCellHandle(Col('b'),Row(5))()
        self.checkImpliedStyle(cellI,ParseCtx.percentFormat)          

        cellI = shtH().getCellHandle(Col('b'),Row(4))()
        self.checkImpliedStyle(cellI,ParseCtx.percentFormat)
        
        cellI = shtH().getCellHandle(Col('c'),Row(4))()
        self.checkNoImplStyle(cellI)

        cellI = shtH().getCellHandle(Col('c'),Row(5))()
        self.checkImpliedStyle(cellI,ParseCtx.currencyFormat)

        cellI = shtH().getCellHandle(Col('c'),Row(20))()
        self.checkImpliedStyle(cellI,ParseCtx.currencyFormat)

        cellI = shtH().getCellHandle(Col('d'),Row(21))()
        self.checkImpliedStyle(cellI,ParseCtx.percentFormat)                                  

        cellI = shtH().getCellHandle(Col('e'),Row(21))()
        self.checkImpliedStyle(cellI,ParseCtx.defaultDecimalFormat)     


        
suitelist = [testFormulaInheritance]


if __name__ == '__main__': testmain(suitelist)
