
from numbler.unittests.testtools import *

class lockExpansionTestCase(lockingTestCase):

    def testExpandLockEnd(self):
        ch = self.getClientHandle()
        d,newlock = self.getLock(ch,Col('e'),5,Col('g'),22)
        # insert a column
        changetuple = (0,0,int(Col('g')),1)
        ret = self.lockmanager.adjustLockedRegions(ch,self.shtH,self.getColRect(Col('g')),changetuple)
        self.checkExpandedLock(newlock.lockuid,Col('e'),5,Col('h'),22)

    def testExpandLockMiddle(self):
        ch = self.getClientHandle()
        d,newlock = self.getLock(ch,Col('e'),5,Col('g'),22)
        # insert a column
        changetuple = (0,0,int(Col('f')),10)
        ret = self.lockmanager.adjustLockedRegions(ch,self.shtH,self.getColRect(Col('f'),10),changetuple)
        self.checkExpandedLock(newlock.lockuid,Col('e'),5,Col('q'),22)

    def testAdjustDelLock(self):
        ch = self.getClientHandle()
        d,newlock = self.getLock(ch,Col('e'),5,Col('g'),22)
        
        changetuple = (0,0,int(Col('k')),-10)
        ret = self.lockmanager.adjustLockedRegions(ch,self.shtH,self.getColRect(Col('b'),10),changetuple,deleteRegion=True)
        self.verifyLockDeleted(newlock.lockuid)

    def testAdjustDelLockExact(self):
        ch = self.getClientHandle()
        d,newlock = self.getLock(ch,Col('e'),5,Col('g'),22)
        
        changetuple = (0,0,int(Col('g')),-3)
        ret = self.lockmanager.adjustLockedRegions(ch,self.shtH,self.getColRect(Col('e'),3),changetuple,deleteRegion=True)
        self.verifyLockDeleted(newlock.lockuid)

    def testAdjustDelLockExact2(self):
        ch = self.getClientHandle()
        d,newlock = self.getLock(ch,Col('b'),5,Col('c'),22)
        
        changetuple = (0,0,int(Col('c')),-2)
        ret = self.lockmanager.adjustLockedRegions(ch,self.shtH,self.getColRect(Col('b'),2),changetuple,deleteRegion=True)
        self.verifyLockDeleted(newlock.lockuid)

    def testAdjustShrinkLock(self):
        ch = self.getClientHandle()
        d,newlock = self.getLock(ch,Col('e'),5,Col('g'),22)
        
        changetuple = (0,0,int(Col('g')),-2)
        ret = self.lockmanager.adjustLockedRegions(ch,self.shtH,self.getColRect(Col('f'),2),changetuple,deleteRegion=True)
        self.checkExpandedLock(newlock.lockuid,Col('e'),5,Col('e'),22)        
    
    def testAdjustOverNonOwnedLock(self):
        ch,ch1 = self.getClientHandle(),self.getClientHandle()
        d,newlock = self.getLock(ch,Col('e'),5,Col('g'),22)
        
        changetuple = (0,0,int(Col('g')),-2)
        self.failUnlessRaises(LockRegionOverlap,self.lockmanager.adjustLockedRegions,
                              ch1,self.shtH,self.getColRect(Col('f'),2),changetuple,deleteRegion=True)

                                           

    def testInsertBeforeCol(self):
        ch,ch1 = self.getClientHandle(),self.getClientHandle()
        d,newlock = self.getLock(ch,Col('e'),5,Col('g'),22)
        
        changetuple = (0,0,int(Col('b')),2)
        ret = self.lockmanager.adjustLockedRegions(ch,self.shtH,self.getColRect(Col('b'),2),changetuple)
        self.checkExpandedLock(newlock.lockuid,Col('g'),5,Col('i'),22)

    def testInsertBeforeColExact(self):
        ch,ch1 = self.getClientHandle(),self.getClientHandle()
        d,newlock = self.getLock(ch,Col('e'),5,Col('g'),22)
        
        changetuple = (0,0,int(Col('e')),5)
        ret = self.lockmanager.adjustLockedRegions(ch,self.shtH,self.getColRect(Col('e'),5),changetuple)
        self.checkExpandedLock(newlock.lockuid,Col('j'),5,Col('l'),22)

    def testInsertBeforeRow(self):
        ch,ch1 = self.getClientHandle(),self.getClientHandle()
        d,newlock = self.getLock(ch,Col('e'),5,Col('g'),22)
        
        changetuple = (4,4,0,0)
        ret = self.lockmanager.adjustLockedRegions(ch,self.shtH,self.getRowRect(4,4),changetuple)
        self.checkExpandedLock(newlock.lockuid,Col('e'),9,Col('g'),26)

    
    def testInsertAdjNonOwner(self):
        ch,ch1 = self.getClientHandle(),self.getClientHandle()
        d,newlock = self.getLock(ch,Col('e'),5,Col('g'),22)
        
        changetuple = (0,0,Col('d'),1)
        ret = self.lockmanager.adjustLockedRegions(ch1,self.shtH,self.getColRect(Col('d'),0),changetuple)
        self.checkExpandedLock(newlock.lockuid,Col('f'),5,Col('h'),22)
        

    def testdeleteAdjacentNonOwner(self):
        ch = self.getClientHandle()
        d,newlock = self.getLock(ch,Col('b'),5,Col('c'),22)
        
        changetuple = (0,0,int(Col('d')),-1)
        #import pdb
        #pdb.set_trace()        
        ret = self.lockmanager.adjustLockedRegions(ch,self.shtH,self.getColRect(Col('d'),0),changetuple,deleteRegion=True)
        self.checkExpandedLock(newlock.lockuid,Col('b'),5,Col('c'),22)        
