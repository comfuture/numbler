##
## MRUDict: A dict object with max size
## Eliminates least recently updated / used
##
## MRUDict: A dict object with max size
##   A hybrid of two approaches:
##     Skip Montanaro's MRU cache
##     http://manatee/mojam.com/~skip/python/
##   And mrucache.py
##     mrucache.py -- defines class MRUCache
##     Takes capacity at construction.
##
##     Alpha version. NO WARRANTY. Use at your own risk
##     Copyright (c) 2002 Bengt Richter 2001-10-05. All rights reserved.
##     Use per Python Software Foundation (PSF) license.
## 

class Node:
    """For linked list kept in most-recent .. least-recent *use* order"""
    __slots__ = ['value', 'key', 'older', 'newer']

    def __init__(self, value, key, older=None, newer=None):
        self.value = value
        self.key = key
        self.older = older  # link to node not as recently used as current
        self.newer = newer  # Note that list is circular: mru.newer is lru
                            # and lru.older is mru, which is the reference point.

class MRUDict(dict):
    """Produces cache object with given capacity for MRU/LRU list.
    """
    def __init__(self, capacity, updates=False):
        """
        capacity: max number of simultaneous cache MRU values kept
        updates: track use: reorders list at each access
        """
        self.capacity = capacity
        self.mru = None

        # set True for Most Recently Used
        #     False for Most Recently Updated
        
        self.updates = updates

        dict.__init__(self)

    def __setitem__(self, key, val):
        # get mru use node if cache is full, else make new node

        ln = len(self)
        if ln == 0:
            self.mru = Node(val, key)
            self.mru.older = self.mru.newer = self.mru
            dict.__setitem__(self, key, self.mru)
            return

        if key in self:
            # already have this key.  make node with this key most recent
            node = dict.__getitem__(self, key)
            node.value = val
            self._setMru(node)
            return

        lru = self.mru.newer    # newer than mru circularly points to lru node
        
        if ln < self.capacity:
            # put new node between existing lru and mru
            node = Node(val, key, self.mru, lru)
            # update links on both sides
            self.mru.newer = node     			# newer from old mru is new mru
            lru.older = node    			# older than lru points circularly to mru
            self.mru = node				# make new node the mru
        else:
            # position of lru node is correct for becoming mru so
            # just replace value and key
            # print "replace", lru.key, lru.value, val
            lru.value = val
            dict.__delitem__(self, lru.key)		# delete invalidated key->node mapping
            lru.key = key
            self.mru = lru				# new lru is next newer from before

        dict.__setitem__(self, key, self.mru)		# add new key->node mapping

    def __getitem__(self, key):
        """ Get value from cache."""
        item = dict.__getitem__(self, key)
        if self.updates: self._setMru(item)
        return item.value

    def __delitem__(self, key):

        node = dict.__getitem__(self, key)

        # clean up mru if necesary
        if len(self) == 1:
            self.mru = None
        elif self.mru == node:
            self.mru = node.older

        # cut out node
        node.older.newer = node.newer   # older neighbor points to newer neighbor
        node.newer.older = node.older   # newer neighbor points to older neighbor
        
        node.older = node.newer = None			# prevent loops

        dict.__delitem__(self, key)

    def _setMru(self, node):
        """Make node the MRU"""

        # Here we have a valid node. Just update its position in linked lru list
        # we want take node from older <=> node <=> newer
        # and put it in lru <=> node <=> mru and then make new node the mru
        # first cut it out unless it's first or last
        if node is self.mru:            # nothing to do
            return
        lru = self.mru.newer            # circles from newest to oldest
        if node is lru:
            self.mru = lru              # just backs up the circle one notch
            return
        # must be between somewhere, so cut it out first
        node.older.newer = node.newer   # older neighbor points to newer neighbor
        node.newer.older = node.older   # newer neighbor points to older neighbor
        # then put it between current lru and mru
        node.older = self.mru           # current mru is now older
        self.mru.newer = node
        node.newer = lru                # newer than new mru circles to lru
        lru.older = node
        self.mru = node                 # new node is new mru

    def __repr__(self):
        return "{" + ', '.join(map(lambda x: str(x[0]) + ": " + str(x[1]), self.items())) + "}"

    def dump(self):
        """testing: dump cache in order of oldest to newest"""
        if not self.mru: return

        show = self.mru.newer
        while 1:
            print (show.key, show.value),
            if show == self.mru: break
            show = show.newer
        print

    def values(self):
        return map(lambda x: x.value, dict.values(self))

    def items(self):
        return zip(self.keys(), self.values())


def perfTest():
    import random
    cache = MRUDict(128)

    for x in xrange(100000):
        key = random.randint(1, 512)
        cache[key] = 'a'

    print cache

def accPerfTest():
    import random
    sz = 4096

    cache = MRUDict(sz, True)
    # cache = MRUDict(sz)

    for x in xrange(sz):
        cache[x] = 'a'

    for x in xrange(100000):
        foo = cache[random.randint(0, sz - 1)]

    cache.dump()

def test():
    # cache = MRUDict(4)

    # woot = ["aoink", "boink", "coink", "doink", "froink", "ploink", "zroink"]
    # for x in range(len(woot)):
    #     cache[x] = woot[x]
    #    print cache

    cache = MRUDict(4, True)

    woot = [(0, "a"), (1, "b"), (2, "c"), (3, "d"), (0, "e"), (4, "g"), (5, "h"), (6, "i"), (7, "j")]
    # woot = [(0, "a"), (1, "b"), (2, "c"), (3, "d"), (2, "e")]
    for x in woot:
        print "new", x[0], "=", x[1]
        cache[x[0]] = x[1]
        print len(cache), cache
        cache.dump()

    for x in [4, 7]:
        print "del", x
        del cache[x]
        print len(cache), cache
        cache.dump()
    
    for x in [(4, "k"), (8, "l"), (9, "m")]:
        print "new", x[0], "=", x[1]
        cache[x[0]] = x[1]
        print len(cache), cache
        cache.dump()

    print "reorder 8"
    print cache[8]
    cache.dump()
    print

    for x in [8, 6, 4]:
        print "del", x
        del cache[x]
        print len(cache), cache
        cache.dump()

    print cache.keys()

if __name__ == '__main__':
    # perfTest()
    # accPerfTest()
    test()

