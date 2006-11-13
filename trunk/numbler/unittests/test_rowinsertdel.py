
from numbler.unittests.testtools import *

class formulaAdjustmentSampleCase(formulaTestCase):

    def _handleResults(self,arguments):
        print 'arglen is',len(arguments)
        self.failUnless(len(arguments) > 0)

    def testDb(self):
        pass
        #sht = sheet.Sheet.getInstance('JuihGQSDiCKDaNrk')
        #d = eng.ssdb.addColFindChangeCells(sht.getHandle(),4,1)
        #d.addCallback(self._handleResults)
        #return d


class formulaAdjustmentTestCase(formulaTestCase):

    def testAdjustRowDown(self):
        """ simulate adjusting a row downwards by doing an insert """

        # *** test cell reference ***

        # move down by one row

        val = self.getParsed("E4")
        res = val.mutate(3,1,0,0)
        self.failUnless(str(res) == 'e5')
        val = self.getParsed("$E$4")
        res = val.mutate(3,1,0,0)
        self.failUnless(str(res) == '$e$5')

        # move down by 5 rows
        val = self.getParsed("E4")
        res = val.mutate(3,5,0,0)
        self.failUnless(str(res) == 'e9')
        val = self.getParsed("$E$4")
        res = val.mutate(3,5,0,0)
        self.failUnless(str(res) == '$e$9')                

        # test column reference
        val = self.getParsed("SUM(C:C)")
        res = val.mutate(44,5,0,0)
        # verifying no effect
        self.failUnless(str(res) == 'SUM(c:c)')

        # test row references        
        val = self.getParsed('SUM(4:4)')
        res = val.mutate(Row(4),1,0,0)
        self.failUnless(str(res) == 'SUM(5:5)')
        res = val.mutate(Row(4),2,0,0)
        self.failUnless(str(res) == 'SUM(6:6)')
        val = self.getParsed('SUM(20:20)')
        res = val.mutate(1,2,0,0)
        self.failUnless(str(res) == 'SUM(22:22)')

    def testMisc(self):
        """ test misc stuf fthat doesn't actually mutate but does have mutation methods """

        # test Binary ops
        val = self.getParsed('3+4')
        res = val.mutate(4,4,0,0)
        self.failUnless(str(res) == '3 + 4')
        val = self.getParsed('3+4+C9')
        res = val.mutate(0,0,Col('b'),1)        
        self.failUnless(str(res) == '3 + 4 + d9')
        # test UniOp
        val = self.getParsed('3+4+ -C9')
        res = val.mutate(0,0,Col('b'),1)        
        self.failUnless(str(res) == '3 + 4 + -d9')                
        # test string
        val = self.getParsed('"hello"')
        res = val.mutate(0,0,Col('b'),1)
        self.failUnless(str(res) == '"hello"')
        # test number
        val = self.getParsed('24')
        res = val.mutate(0,0,Col('b'),1)
        self.failUnless(str(res) == '24')        
        # test boolean
        val = self.getParsed('TRUe')
        res = val.mutate(0,0,Col('b'),1)
        self.failUnless(str(res) == 'TRUE')                
        # test IF function (has custom translate?  forget why)
        val = self.getParsed('IF("foo"="bar","wowza",)')
        res = val.mutate(0,0,Col('b'),1)
        print '***** testMisc: res is',str(res)                
        self.failUnless(str(res) == 'IF("foo" = "bar","wowza",)')
        # SSREffError
        

    def testRangeReference(self):

        # test after range (expansion)
        val = self.getParsed('SUM(C2:E20)')
        res = val.mutate(0,0,Col('K'),3)
        self.failUnless(str(res) == 'SUM(c2:e20)')
        # test before range (shrinkage)
        res = val.mutate(0,0,Col('b'),-2)
        self.failUnless(str(res) == 'SUM(a2:c20)')
        val = self.getParsed('SUM(C20:E40)')
        res = val.mutate(10,-5,0,0)
        self.failUnless('SUM(C15:E35)')

        # test expansion (middle)
        val = self.getParsed('SUM(C20:E40)')
        res = val.mutate(35,10,0,0)
        self.failUnless(str(res) == 'SUM(c20:e50)')
        
        # test expansion (ovelrap start)
        val = self.getParsed('SUM(C20:E40)')
        res = val.mutate(18,5,0,0)
        self.failUnless(str(res) == 'SUM(c25:e45)')        

        # test expansion (overlap end)
        res = val.mutate(35,5,0,0)
        self.failUnless(str(res) == 'SUM(c20:e45)')

        # expansion (boundary start)
        val = self.getParsed('SUM(C20:E40)')        
        res = val.mutate(20,1,0,0)
        self.failUnless(str(res) == 'SUM(c21:e41)')        
        val = self.getParsed('SUM(G20:Q40)')
        res = val.mutate(0,0,Col('G'),1)
        self.failUnless(str(res) == 'SUM(h20:r40)')                
        
        # expansion (boundary end)
        val = self.getParsed('SUM(C20:E40)')        
        res = val.mutate(40,2,0,0)
        self.failUnless(str(res) == 'SUM(c20:e42)')        
        val = self.getParsed('SUM(G20:Q40)')
        res = val.mutate(0,0,Col('Q'),2)
        print '***** test range ref: res is',str(res)                        
        self.failUnless(str(res) == 'SUM(g20:s40)')                
        

        # test deletion (middle)
        val = self.getParsed('SUM(C20:E40)')        
        res = val.mutate(35,-10,0,0)
        self.failUnless(str(res) == 'SUM(c20:e30)')        
        val = self.getParsed('SUM(G20:Q40)')
        res = val.mutate(0,0,Col('m'),-5)
        self.failUnless(str(res) == 'SUM(g20:l40)')                
        
        # test deletion (overlap start)
        val = self.getParsed('SUM(C20:E40)')                
        res = val.mutate(25,-10,0,0)
        self.failUnless(str(res) == 'SUM(c16:e30)')
        val = self.getParsed('SUM(G20:Q40)')
        res = val.mutate(0,0,Col('i'),-5)
        self.failUnless(str(res) == 'SUM(e20:l40)')

        # test deletion (overlap end)
        val = self.getParsed('SUM(C20:E40)')                
        res = val.mutate(45,-10,0,0)
        self.failUnless(str(res) == 'SUM(c20:e35)')
        val = self.getParsed('SUM(G20:Q40)')
        res = val.mutate(0,0,Col('p'),-8)
        self.failUnless(str(res) == 'SUM(g20:i40)')
        
        # test deletion (boundary end)
        val = self.getParsed('SUM(C20:E40)')                
        res = val.mutate(40,-10,0,0)
        self.failUnless(str(res) == 'SUM(c20:e30)')
        val = self.getParsed('SUM(G20:Q40)')
        res = val.mutate(0,0,Col('q'),-3)
        self.failUnless(str(res) == 'SUM(g20:n40)')        
        
        # test deletion (boundary start)
        val = self.getParsed('SUM(C20:E40)')                
        res = val.mutate(20,-5,0,0)
        self.failUnless(str(res) == 'SUM(c16:e35)')
        val = self.getParsed('SUM(G20:Q40)')
        res = val.mutate(0,0,Col('g'),-3)
        self.failUnless(str(res) == 'SUM(e20:n40)')        

        # test delete entire range at boundaries
        val = self.getParsed('SUM(C20:E40)')                
        res = val.mutate(0,0,Col('e'),-3)
        self.failUnless(str(res) == 'SUM(#REF!)')
        val = self.getParsed('SUM(G20:Q40)')
        res = val.mutate(40,-21,0,0)
        #print 'testRangeRef: res is now',str(res)
        self.failUnless(str(res) == 'SUM(#REF!)')                



    def testAdjustRowUp(self):
        """
        test deleting one or more rows 
        """
        val = self.getParsed('E22')
        res = val.mutate(21,-11,0,0)
        #print 'res is now',str(res)
        self.failUnless(str(res) == 'e11')
        val = self.getParsed('$E22')
        res = val.mutate(21,-11,0,0)
        self.failUnless(str(res) == '$e11')

        val = self.getParsed('SUM(4:4)')
        res = val.mutate(17,-4,0,0)
        self.failUnless(str(res) == 'SUM(4:4)')
        res = val.mutate(17,-17,0,0)
        self.failUnless(str(res) == 'SUM(#REF!)')
        res = val.mutate(3,-3,0,0)
        self.failUnless(str(res) == 'SUM(1:1)')
        res = val.mutate(4,-1,0,0)
        self.failUnless(str(res) == 'SUM(#REF!)')

        # test deleting overlapping at the end
        val = self.getParsed('SUM(10:15)')
        res = val.mutate(20,-10,0,0)
        self.failUnless(str(res) == 'SUM(10:10)')
        val = self.getParsed('SUM(10:20)')        
        res = val.mutate(25,-10,0,0)
        self.failUnless(str(res) == 'SUM(10:15)')

    def testAdjustRowMiddle(self):
        """ simulate inserting a row in the middle of a range """
        val = self.getParsed('SUM(5:10)')
        res = val.mutate(6,2,0,0)
        # two row expansion
        self.failUnless(str(res) == 'SUM(5:12)')
        # boundary conditions
        res = val.mutate(5,6,0,0)
        self.failUnless(str(res) == 'SUM(11:16)')

        # delete downards on a column range
        res = val.mutate(12,-4,0,0)
        self.failUnless(str(res) == 'SUM(5:8)')

        res = val.mutate(12,-12,0,0)
        self.failUnless(str(res) == 'SUM(#REF!)')
        res = val.mutate(11,-6,0,0)
        self.failUnless(str(res) == 'SUM(5:5)')

        # outward boundary expansion
        val = self.getParsed('SUM(10:15)')        
        res = val.mutate(10,5,0,0)
        self.failUnless(str(res) == 'SUM(15:20)')

        # delete from the beginning of the range
        val = self.getParsed('SUM(10:15)')        
        res = val.mutate(11,-3,0,0)
        self.failUnless(str(res) == 'SUM(9:12)')
        res = val.mutate(11,-4,0,0)
        self.failUnless(str(res) == 'SUM(8:11)')
        res = val.mutate(14,-8,0,0)
        self.failUnless(str(res) == 'SUM(7:7)')
        res = val.mutate(14,-9,0,0)
        self.failUnless(str(res) == 'SUM(6:6)')
        res = val.mutate(14,-10,0,0)
        self.failUnless(str(res) == 'SUM(5:5)')
        res = val.mutate(14,-13,0,0)
        self.failUnless(str(res) == 'SUM(2:2)')
        res = val.mutate(14,-14,0,0)
        self.failUnless(str(res) == 'SUM(1:1)')
        res = val.mutate(14,-15,0,0)
        self.failUnless(str(res) == 'SUM(#REF!)')                                

        
    def testAddColsRight(self):
        """ test adding columns """

        # column range stuff

        val = self.getParsed('SUM(D:D)')
        res = val.mutate(0,0,Col('Q'),5)
        # should have no effect
        self.failUnless(str(res) == 'SUM(d:d)')
        res = val.mutate(0,0,Col('D'),1)
        self.failUnless(str(res) == 'SUM(e:e)')        
        res = val.mutate(0,0,Col('D'),2)
        self.failUnless(str(res) == 'SUM(f:f)')
        val = self.getParsed('SUM(F:F)')
        res = val.mutate(0,0,Col('C'),3)
        #print '*** res is',str(res)
        self.failUnless(str(res) == 'SUM(i:i)')
        res = val.mutate(0,0,Col('A'),2)
        self.failUnless(str(res) == 'SUM(h:h)')
        res = val.mutate(0,0,Col('B'),5)
        self.failUnless(str(res) == 'SUM(k:k)')        

    def testDeleteCols(self):
        """ test deleting columns """
        val = self.getParsed('SUM(D:D)')
        res = val.mutate(0,0,Col('Q'),-4)
        self.failUnless(str(res) == 'SUM(d:d)')
        val = self.getParsed('SUM(D:D)')
        res = val.mutate(0,0,Col('Q'),-Col('Q'))
        self.failUnless(str(res) == 'SUM(#REF!)')
        res = val.mutate(0,0,Col('Q'),-Col('BB'))
        self.failUnless(str(res) == 'SUM(#REF!)')        
        res = val.mutate(0,0,Col('F'),-4)
        self.failUnless(str(res) == 'SUM(#REF!)')
        res = val.mutate(0,0,Col('C'),-3)
        self.failUnless(str(res) == 'SUM(a:a)')
        res = val.mutate(0,0,Col('D'),-1)
        #print '*** res is now',str(res)        
        self.failUnless(str(res) == 'SUM(#REF!)')        


    def testAdjustColMiddle(self):
        """ simulate additions / deletions of a  a column in the middle of the range """
        val = self.getParsed('SUM(E:G)')
        res = val.mutate(0,0,Col('F'),4)
        # verify that the range was expanded
        #print '*** testAdjustColMiddle: res is now',str(res)                
        self.failUnless(str(res) == 'SUM(e:k)')

        # boundary conditions
        res = val.mutate(0,0,Col('E'),2)
        self.failUnless(str(res) == 'SUM(g:i)')

        # delete downards on a coumn range.
        res = val.mutate(0,0,Col('H'),-3)
        #verify that the range was shrunk
        self.failUnless(str(res) == 'SUM(e:e)')        

        val = self.getParsed('SUM(E:I)')
        res = val.mutate(0,0,Col('K'),-4)
        self.failUnless(str(res) == 'SUM(e:g)')

        # delete the entire range- should be a ref error
        val = self.getParsed('SUM(E:G)')        
        res = val.mutate(0,0,Col('G'),-3)
        self.failUnless(str(res) == 'SUM(#REF!)')

        # delete from the beginning of the range
        val = self.getParsed('SUM(J:N)')
        res = val.mutate(0,0,Col('K'),-3)
        self.failUnless(str(res) == 'SUM(i:k)')
        res = val.mutate(0,0,Col('L'),-5)
        self.failUnless(str(res) == 'SUM(h:i)')
        res = val.mutate(0,0,Col('M'),-12)
        self.failUnless(str(res) == 'SUM(b:b)')
        res = val.mutate(0,0,Col('M'),-13)
        #print '***** testAdjustColMiddle: res is',str(res)                                                
        self.failUnless(str(res) == 'SUM(a:a)')
        res = val.mutate(0,0,Col('M'),-14)
        self.failUnless(str(res) == 'SUM(#REF!)')


        val = self.getParsed('SUM(J4:N50)')
        res = val.mutate(0,0,Col('j'),-1)
        print '***** testAdjustColMiddle: res is',str(res)                                                        
        self.failUnless(str(res) == 'SUM(j4:m50)')        

        val = self.getParsed('SUM(J:N)')
        res = val.mutate(0,0,Col('j'),-1)
        print '***** testAdjustColMiddle: res is',str(res)                                                        
        self.failUnless(str(res) == 'SUM(j:m)')        


    def testAdjustColOverlap(self):
        """ overlapping cases """
        val = self.getParsed('SUM(E:G)')
        res = val.mutate(0,0,Col('D'),4)
        # insert on overlap start
        self.failUnless(str(res) == 'SUM(i:k)')

        # overlap on the end - should just be expansions
        res = val.mutate(0,0,Col('G'),3)
        self.failUnless(str(res) == 'SUM(e:j)')
        
    

class insertColTestCase(sheetTester):
    sheets = [
        {
        'name':'insertsheet',
        'cells':[
        ('a1','3'),
        ('a5','3.001'),
        ('F10','2e30'),
        ('G20','45'),
        ('e4','-1'),
        ('e5','-2e5'),
        ('z19','22'),
        ]
        }]
    
    def testInsertNoAction(self):
        # do the insert
        sht = self.sheetHandles['insertsheet']
        # insert one column at way at the end (this basically should have no effect)
        d = defer.Deferred()        
        d.addCallback(self.checkNumResults,0)
        d.addErrback(self.defErrB)
        return sht().insertColumn(Col('aa'),1,d)


    def testInsertOneCol(self):
        """
        verify the ability to insert one row.
        """

        verifycontents = [
            ('g10',2e+30),
            ('h20',45),
            ('aa19',22),
            ('f10',''),
            ('g20',''),
            ('z19','')
            ]
        
        sht = self.sheetHandles['insertsheet']

        d = defer.Deferred()                
        d.addCallback(self.checkNumResults,6)
        d.addCallback(self.verifyResults,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().insertColumn(Col('f'),1,d)

        # verify that formula values are the same

        # verify that formula is adjusted.
        pass

    def testColStyleMove(self):
        """
        verify that whens a column gets inserted that it's style information is updated properly.
        """

class insertFormulaAdjTestCase(sheetTester):
    sheets = [
        {
        'name':'insertsheet',
        'cells':[
        ('a1','=SUM(b5:d50)'),
        ('b5','30'),
        ('b10','40.5'),
        ('d25','50'),
        ('d50','90'),
        ('f20','=SUM(b5:d50)'),
        ('f21','=SUM(b:b)'),
        ('f22','=SUM(b5,b10,d25,d50,d51)'), # note that d51 has nothing in it
        ('a100','=SUM(E100:G100)'),
        ('f100','23'),
        ('g100','99'),
        ('f101','=G101'),
        ('f102','=aa102'),
        ('g101','2')
        ]
        }]

    def testColInsertBefore(self):

        verifycontents = [
            ('g20','=SUM(c5:e50)'),
            ('b5',''),
            ('g22','=SUM(c5,c10,e25,e50,e51)'),
            ]
        
        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().insertColumn(Col('a'),1,d)


    def testDepUpdates(self):

        sht = self.sheetHandles['insertsheet']

        def updateAfter(arg):
            # clear the cache and reload from db to verify results.
            guid = str(sht)
            self.emptyCaches()
            shtH = sheet.SheetHandle.getInstance(guid)
            print '*** g21 is ',self.value(shtH,'g21'),'g21',self.getFormula(shtH,'g21'),'f21',self.getFormula(shtH,'f21'),
            self.failUnless(self.value(shtH,'g21') == 70.5)
            self.setFormula(shtH,'c5','35')
            cellI = shtH().getCellHandle(Col('g'),22)()
            self.verifyResults(None,shtH,[('g21',75.5),('g22',215.5)])
        
        d = defer.Deferred()        
        d.addCallback(updateAfter)
        d.addErrback(self.defErrB)
        return sht().insertColumn(Col('a'),1,d)

    def testRangeRefNoMove(self):
        """ verify that a cell that references part of the move region
        but is before the move region stays put """
        verifycontents = [
            ('g100','23'),
            ('a100','=SUM(f100:h100)')

            ]
        
        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().insertColumn(Col('b'),1,d)

    def testCellRefChangeOnNewCol(self):
        """
        verify that individual cell dependencies will trigger an update
        if a formula that is before the increase area refers to a cell in the increase area.
        """
        verifycontents = [
            ('f101','=h101'),
            ]


        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()        
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().insertColumn(Col('g'),1,d)

    def testCellRefChangeOnNewColDelDown(self):
        """
        verify that individual cell dependencies will trigger an update
        if a formula that is before the increase area refers to a cell in the increase area.
        """
        verifycontents = [
            ('f102','=v102'),
            ]

        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()        
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().deleteColumn(Col('r'),-5,d)


    
        
    def testColInsertMiddle(self):
        verifycontents = [
            ('a1','=SUM(b5:e50)'),
            ('g20','=SUM(b5:e50)'),
            ('b5','30'),
            ('f20',''),
            ('e25','50')
            ]
        
        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        #import pdb
        #pdb.set_trace()        
        return sht().insertColumn(Col('c'),1,d)

    def testColInsertAfter(self):
        verifycontents = [
            ('i20','=SUM(b5:d50)'),
            ]
        
        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()        
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().insertColumn(Col('e'),3,d)        


class maximumTestCase(sheetTester):
    sheets = [
        {
        'name':'insertsheet',
        'cells':[
        ('iv5','=SUM(1,2,3)'),
        ('a65536','ding!')
        ]
        }]

    def testMaxCol(self):
        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()
        retd = sht().insertColumn(Col('a'),1,d)
        self.assertFailure(retd,ExpansionOverflow)
        return retd

    def testMaxRow(self):
        sht = self.sheetHandles['insertsheet']        
        d = defer.Deferred()
        newd = sht().insertRow(1,1,d)
        self.assertFailure(newd,ExpansionOverflow)
        return newd
    
class rowInsertTestCase(sheetTester):
    sheets = [
        {
        'name':'insertsheet',
        'cells':[
        ('a1','=SUM(b5:d10)'),
        ('b5','30'),
        ('e5','40.5'),
        ('a9','50'),
        ('d10','90'),
        ('q20','=SUM(b5:e10)'),
        ('r20','=SUM(5:5)'),
        ('p20','=SUM(b5,e5,a9,d10,d11)'), # note that d51 has nothing in it
        ('z2','3'),
        ('z3','5'),
        ('z4','=SUM(z2,z3)'),
        ('t2','=SUM(t5:t10)'),
        ('t6','4'),
        ('t9','=PI()'),
        ('y2','=y5'),
        ('y5','9')
        ]
        }]

    def testRowInsertBefore(self):

        verifycontents = [
            ('q21','=SUM(b6:e11)'),
            ('r21','=SUM(6:6)'),
            ('p21','=SUM(b6,e6,a10,d11,d12)')
            ]

        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()        
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().insertRow(1,1,d)

    def testRowInsertVerifySum(self):
        verifyvalues = [
            ('z5',8),
            ]
        
        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()        
        d.addCallback(self.verifyResults,sht,verifyvalues)
        d.addErrback(self.defErrB)
        return sht().insertRow(2,1,d)

    def testRowInsertMiddle(self):
        verifycontents = [
            ('a1','=SUM(b5:d11)'),
            ('q21','=SUM(b5:e11)'),
            ('r21','=SUM(5:5)'),
            ('p21','=SUM(b5,e5,a10,d11,d12)')
            ]
        
        
        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()        
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().insertRow(9,1,d)

    def testRangeRefNoMove(self):
        """ verify that a cell that references part of the move region
        but is before the move region stays put """
        verifycontents = [
            ('t2','=SUM(t6:t11)')

            ]
        
        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()        
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().insertRow(5,1,d)

    def testCellRefChangeOnNewCol(self):
        """
        verify that individual cell dependencies will trigger an update
        if a formula that is before the increase area refers to a cell in the increase area.
        """
        verifycontents = [
            ('y2','=y7'),
            ]


        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().insertRow(4,2,d)

    def testRowInsertAfter(self):
        verifycontents = [
            ('r20','=SUM(5:5)'),
            ]
        
        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().insertRow(10000,3,d)

class deleteTestCase(sheetTester):
    sheets = [
        {
        'name':'insertsheet',
        'cells':[
        ('b5','30'),
        ('e5','40.5'),
        ('a9','50'),
        ('d10','90'),
        ('q20','=SUM(b5:e10)'),
        ('r20','=SUM(5:5)'),
        ('p20','=SUM(b5,e5,a9,d10,d11)'), # note that d51 has nothing in it
        ('z2','3'),
        ('z3','5'),
        ('z4','=SUM(z2,z3)'),
        ('t2','=SUM(t5:t10)'),
        ('t6','4'),
        ('t9','=PI()'),
        ('y2','=y5'),
        ('y5','9')
        ]
        }]
    

    def testDeleteColumn(self):
        verifycontents = [
            ('p20','=SUM(b5:d10)'),
            ]
        
        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().deleteColumn(Col('c'),-1,d)

    def testDeleteColumn2(self):
        verifycontents = [
            ('p20','=SUM(a5:d10)'),
            ('s2','=SUM(s5:s10)'),
            ]
        
        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().deleteColumn(Col('a'),-1,d)

    def testDeleteColumnRefError(self):
        verifycontents = [
            ('l20','=SUM(#REF!)'),
            ]
        
        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().deleteColumn(Col('e'),-5,d)
        
    def testDeleteRow(self):
        verifycontents = [
            ('r19','=SUM(4:4)'),
            ('z3','=SUM(z1,z2)'),
            ('t1','=SUM(t4:t9)'),
            ('q19','=SUM(b4:e9)'),
            ]
        
        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().deleteRow(1,-1,d)

    def testDeleteRow2(self):
        verifycontents = [
            ('q20',''),
            ('r20',''),
            ('p20',''),
            ('q19',''),
            ('r19',''),
            ('p19','')
            ]
        
        sht = self.sheetHandles['insertsheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().deleteRow(20,-1,d)

class deleteTestCaseBeginning(sheetTester):
    sheets = [
        {
        'name':'deletesheet',
        'cells':[
        ('a1','44'),
        ('g2','99')
        ]
        }]


    def testDeleteEarlyRows(self):
        verifycontents = [
            ('a1',''),
            ('g2',''),
            ('g1','')
            ]
        
        sht = self.sheetHandles['deletesheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyFormulas,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().deleteRow(2,-2,d)


class styleMoveTestCase(sheetTester):
    """
    verify that a styled cell is updated when a cell changes.
    """
    sheets = [
        {
        'name':'deletesheet',
        'cells':[
        ('g2','99')
        ],
        'styles':[
        ('g2',{u'background-color': u'#cc0000'}),
        ('g3',{u'background-color': u'#cc0000'})        
        ]
        }]    

    def testDeleteBeforeStyle(self):
        verifycontents = [
            ('f2',{u'background-color': u'#cc0000'}),
            ('f3',{u'background-color': u'#cc0000'})
            ]
        
        sht = self.sheetHandles['deletesheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyStyles,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().deleteColumn(Col('b'),-1,d)
        


class colrowStyleMoveTestCase(sheetTester):
    """
    tests for verifying that styles associated with a row or column
    get deleted or moved appropriately.
    """
    sheets = [
        {
        'name':'deletesheet',
        'colprops':[
        (Col('b'),{u'background-color': u'#cc00ff'}),
        (Col('c'),{u'background-color': u'#ccff00'}),                
        (Col('g'),{u'background-color': u'#cc0000'}),
        (Col('ab'),{u'background-color': u'#cc0000'})        
        ],
        'rowprops':[
        (1000,{u'background-color': u'#cc00ee'}),
        (42,{u'background-color': u'#cc00FF'})        
        ]
        }]        


    def testDeleteColStyleExcat(self):
        """
        delete the exact row and make sure the style is gone.
        """
        verifycontents = [
            (Col('g'),u'')
            ]
        
        sht = self.sheetHandles['deletesheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyColStyles,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().deleteColumn(Col('g'),-1,d)
        
    def testDeleteBeforeStyle(self):
        verifycontents = [
            (Col('f'),{u'background-color': u'#cc0000'}),
            (Col('aa'),{u'background-color': u'#cc0000'}),
            (Col('g'),u''),
            (Col('ab'),u''),
            ]
        
        sht = self.sheetHandles['deletesheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyColStyles,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().deleteColumn(Col('a'),-1,d)

    def testInsertBeforeStyle(self):
        verifycontents = [
            (Col('g'),u''),
            (Col('ab'),u''),
            (Col('h'),{u'background-color': u'#cc0000'}),
            (Col('ac'),{u'background-color': u'#cc0000'})                    
            ]
        
        sht = self.sheetHandles['deletesheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyColStyles,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().insertColumn(Col('a'),1,d)

    def testInsertExact(self):

        verifycontents = [
            (Col('g'),u''),
            (Col('ab'),u''),
            (Col('h'),{u'background-color': u'#cc0000'}),
            (Col('ac'),{u'background-color': u'#cc0000'})                    
            ]
        
        sht = self.sheetHandles['deletesheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyColStyles,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().insertColumn(Col('g'),1,d)

    def testInsertMiddle(self):

        verifycontents = [
            (Col('b'),{u'background-color': u'#cc00ff'}),
            (Col('c'),u''),
            (Col('d'),{u'background-color': u'#ccff00'}),                
            ]
        
        sht = self.sheetHandles['deletesheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyColStyles,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().insertColumn(Col('c'),1,d)

    def testDeleteColStyleEnclosing(self):
        """
        delete a range exclosing the column and make sure that the
        style is gone.
        """
        verifycontents = [
            (Col('g'),u''),
            (Col('ab'),u''),
            (Col('h'),u''),
            (Col('ac'),u''),
            (Col('f'),u''),
            (Col('aa'),u'')
            ]
        
        sht = self.sheetHandles['deletesheet']
        d = defer.Deferred()                
        d.addCallback(self.verifyColStyles,sht,verifycontents)
        d.addErrback(self.defErrB)
        return sht().deleteColumn(Col('ac'),-(int(Col('ac'))-2),d)

    def testDeleteRowStyleExcat(self):
        """
        delete the exact row and make sure the style is gone.
        """

    def testDeleteRowStyleEnclosing(self):
        """
        delete a range exclosing the column and make sure that the
        style is gone.
        """        


    def testDeleteRowBefore(self):
        """
        verify that the style shifts down
        """

    def testInsertRowBefore(self):
        """
        verify that the style shifts up
        """


    
