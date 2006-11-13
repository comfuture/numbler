################################################################################
## (C) Numbler LLC 2006
################################################################################

from twisted.internet import reactor,defer
from server.sslib.utils import *
from numbler.server import exc
from numbler.server.astbase import CellRef,Range
import datetime

class Rect(object):
    """
    basic rect class snarfed from pygame (although the pygame impl is in C)
    """
    
    def __init__(self,x,y,w,h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def contains(self,target):
        res = self.x <= target.x and self.y <= target.y and \
              (self.x+self.w >= target.x+target.w) and \
              (self.y+self.h >= target.y+target.h) and \
              (self.x+self.w > target.x) and \
              (self.y+self.h > target.y)
        return res

    def colliderect(self,target):
        return ((self.x >= target.x and self.x < target.x+target.w) or \
                (target.x >= self.x and target.x < self.x+self.w)) and \
                ((self.y >= target.y and self.y < target.y+target.h) or \
                 (target.y >= self.y and target.y1 < self.y+self.h))
    def __eq__(self,t):
        return self.x == t.x and self.y == t.y and self.w == t.w and self.h == t.h

    def __ne__(self,t):
        return not self.__eq__(t)
    

def getRect(c1,r1,c2,r2):
    """ create a native rect object from the inputs """
    return Rect(c1,r1,c2-c1+1,r2-r1+1)


class sheetlock(object):
    """ the purpose of this class is to sanitity check the data and
    do some rudimentary data massaging"""

    def __init__(self,clientHandle,clientlock):
        """ client lock is a dictionary of values """
        self.lockFromClient = clientlock
        #print clientlock['topleft'],clientlock['bottomright']

        self.callHandle = None
        self.clientHandle = clientHandle
        x1,y1 = clientlock['topleft']['col'],clientlock['topleft']['row']
        x2,y2 = clientlock['bottomright']['col'],clientlock['bottomright']['row']
        self.boundingrect = Rect(x1,y1,x2-x1+1,y2-y1+1)
        #print self.boundingrect
        # assumes that the timestamp is in the appropriate format.
        # DateTimeFrom(clientlock['timerequested'])

        # this value may be supplied by the client but we overwrite it.
        self.timerequested = datetime.datetime.utcnow()
        self.lockduration = int(clientlock['lockduration'])
        self.lockend = 0
        self.locked = False
        self.lockuid = unicode(alphaguid16())
        # this property is for if the lock is owned by client.  it is
        # manipulated by the upper layer
        self.owner = False             
        self.user = unicode(clientlock['user']) # should be set by the caller

    def toDict(self):

        """ returns all properties in a dictionary for consumption by JSON """
        return {u'topleft':self.lockFromClient['topleft'],
                                        u'bottomright':self.lockFromClient['bottomright'],
                                        u'rect':self.lockFromClient['rect'],
                                        u'timerequested':unicode(self.timerequested),
                                        u'lockduration':self.lockduration,
                                        u'lockend':unicode(self.lockend),
                                        u'lockuid':self.lockuid,
                                        u'owner':self.owner,
                                        u'user':unicode(self.user),
                                        u'locked':self.locked
                                        }
    def lockForUser(self,clientId):
        ret = self.toDict()
        if self.clientHandle == clientId:
            ret['owner'] = True
        return ret

    def succeed(self,duration):
        """ mark the lock as successful """
        self.locked = True
        self.lockend = self.timerequested + datetime.timedelta(0,duration)

    def fail(self):
        self.locked = False
        self.lockend = self.timerequested

    def cellLocked(self,clientId,col,row):
        return self.clientHandle != clientId and self.boundingrect.contains(Rect(col,row,0,0))

    def regionLocked(self,clientId,testrect):
        print 'regionLocked: checking %s against %s' % (self.boundingrect,testrect)
        return self.clientHandle != clientId and self.boundingrect.colliderect(testrect)

    def overlaps(self,testrect):
        print 'overlaps: testing %s against %s' % (testrect,self.boundingrect)
        return self.boundingrect.colliderect(testrect)

   ## def after(self,testrect):
##        """
##        indicate lock is greater than testrect in either the x or y axis.  this only
##        really works with rectanges that take up an entire row or column
##        """
##        return (testrect.bottom > self.boundingrect.bottom and testrect.right < self.boundingrect.left) or\
##               (testrect.right > self.boundingrect.right  and testrect.bottom < self.boundrect.top)
        

    def mutate(self,sht,tR,nR,tC,nC):
        """
        expand shrink the lock rectange based on the arguments.
        tr = top row, nR = end row (negative for deletes).  This implementation
        reuses the heavily tested mutation implementatoin for cell ranges.  for this
        case we convert the bounding rect to a cell ref, mutate it, and then convert
        back to a rect.
        """

        rng = Range(CellRef(sht.getCellHandle(self.boundingrect.x,self.boundingrect.y),"",""),
                    CellRef(sht.getCellHandle(self.boundingrect.x+self.boundingrect.w-1,
                                               self.boundingrect.y+self.boundingrect.h-1),"",""))
        newrng = rng.mutate(tR,nR,tC,nC)
        if not isinstance(newrng,Range):
            raise exc.LockRegionError()
        newl = int(newrng.cell0.getCol())
        newt = int(newrng.cell0.getRow())
        newrect = Rect(newl,newt,int(newrng.cell1.getCol())-newl+1,
                                 int(newrng.cell1.getRow())-newt+1)
        return newrect

    def setNewRect(self,newrect):
        self.boundingrect = newrect
        self.lockFromClient['rect'] = {u'l':newrect.x,
                                       u't':newrect.y,
                                       u'r':newrect.x+newrect.w-1,
                                       u'b':newrect.y + newrect.h-1}
        


class lockManager(object):
    """ Manage a collection of range locks for a particular sheet.
    At this points all the locks are temporary and will time out eventually. """

    def __init__(self,defaultduration = 300):
        self.locks = {}
        self.defaultduration = defaultduration

    def locksForClient(self,clientHandle):
        """ return all current locks for a particular client.  All locks belonging to
        the client will be marked as owner=True"""
        return map(lambda x: x.lockForUser(clientHandle),self.locks.values())

    def lookupLock(self,lockuid):
        return self.locks.get(lockuid)

    def _removeLock(self,cb,lockuid):
        print '_removeLock called',lockuid
        if lockuid in self.locks:
            print 'deleting lock!'
            del self.locks[lockuid]

    def cellLocked(self,clientHandle,col,row):
        """ return if a cell is locked by another user """

        # The first cut of this algorithm is inefficient - it will visit every locked region and
        # see if the cell is in the region.
        for item in self.locks.values():
            if item.cellLocked(clientHandle,col,row):
                return True
        return False
        
    def regionLocked(self,clientHandle,c1,r1,c2,r2):
        testrect = getRect(c1,r1,c2,r2)
        #testrect = Rect(c1,r1,c2-c1,r2-r1)
        print 'regionLocked checking against',testrect
        for item in self.locks.values():
            if item.regionLocked(clientHandle,testrect):
                raise exc.LockRegionOverlap()                
        

    def adjustLockedRegions(self,clientId,sht,matchrect,changetuple,deleteRegion=False):
        """
        iterate through any locked regions that overlap the specified region and
        grow / shrink them based on newrect.
        """
        print 'adjustLockedRegions: called with',matchrect,changetuple,deleteRegion
        
        ret = []
        for lock in self.locks.values():
            if lock.overlaps(matchrect):
                # if the lock is owned by someone else the operation fails.
                if clientId != lock.clientHandle:
                    raise exc.LockRegionOverlap()
                if matchrect.contains(lock.boundingrect) and deleteRegion:
                    # mark the lock for deletion
                    ret.append((lock,None))
                else:
                    # clone the lock and extend it.
                    ret.append((lock,lock.mutate(sht,*changetuple)))
            else:
                result = lock.mutate(sht,*changetuple)
                # only put in results that actually change the lock
                if result != lock.boundingrect:
                    ret.append((lock,result))

        print 'adjustLockedRegions: ret is ',ret

        # if we got this far we have a list of lock regions that we can
        # adjust. do that now.  If we haven't reached this point an exception
        # has been raised (lock overlap, other user has a lock, etc.
        for oldlock,newlockrect in ret:
            if newlockrect is None:
                print 'releasing lock!!'
                self.releaseLock(oldlock.lockuid)
            else:
                #oldlock.owner = True
                print 'setting new rect to ',newlockrect,'old rect is',oldlock.boundingrect
                self.locks[oldlock.lockuid].setNewRect(newlockrect)
                # replace the old lock rect with the new lock rect
                #self.locks[oldlock.lockuid].boundingrect = newlockrect

        return [x[0].toDict() for x in ret if x[1] is not None]

    def getLock(self,lock):
        # check the that the lock area doesn't overlap.  returns a deferred
        # that will callback on normal lock expiration, errback on
        # client disconnection.
        print 'lock requested for ',lock.boundingrect
        if not lock.lockduration:
            lock.lockduration = self.defaultduration

        for item in self.locks.values():
            print 'check %s against %s' % (str(item.boundingrect),str(lock.boundingrect))
            if item.boundingrect.colliderect(lock.boundingrect):
                print 'lock failed!'
                lock.fail()
                return None

        self.locks[lock.lockuid] = lock
        lock.succeed(self.defaultduration)

        # set the duration to a default value
        d = defer.Deferred()
        d.addBoth(self._removeLock,lock.lockuid)
        lock.callHandle = reactor.callLater(lock.lockduration,d.callback,lock)
        lock.deferred = d
        return d

    def releaseLock(self,lockuid):
        if lockuid in self.locks:
            lock = self.locks[lockuid]
            lock.callHandle.cancel()
            lock.deferred.callback(lock)

    def onDisconnect(self,cb,clientHandle):
        """ event handler for when a client disconnects (abnormally or normally)
        from a livepage """
        print 'Page disconnected; freeing up locks for',clientHandle
        for item in self.locks.values():
            if item.clientHandle == clientHandle:
                print 'removing lock',item.lockuid
                # cancel the outstanding timer
                item.callHandle.cancel()
                print 'calling errbacks...'
                item.deferred.errback(Exception('None'))
        #print 'OnDisconnect: Done!'
        #return cb
