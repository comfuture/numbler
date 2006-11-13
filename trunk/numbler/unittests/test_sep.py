from numbler.unittests.testtools import *

##class sampleTestCase(formulaTestCase):

##    def testfoo(self):
##        val = self.getParsed('SUM(J4:N50)')
##        res = val.mutate(0,0,Col('j'),-1)
##        print '***** testAdjustColMiddle: res is',str(res)                                                        
##        self.failUnless(str(res) == 'SUM(j4:m50)')        


##        val = self.getParsed('SUM(J:N)')
##        res = val.mutate(0,0,Col('j'),-1)
##        print '***** testAdjustColMiddle: res is',str(res)                                                        
##        self.failUnless(str(res) == 'SUM(j:m)')        
    
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

        #import pdb
        #pdb.set_trace()        
        rng = cell.CellRange.getInstance(Col("b"),Row(2),Col("c"),Row(9))
        d = sht().deleteCells(rng)
        d.addCallback(self.verifyNotification,sht,verifyValues)
        return d
