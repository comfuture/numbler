# (C) Numbler Llc 2006
# See License For Details.


## CappedStack
## 
## Stack that keeps around cap items
##


class CappedStack:
    def __init__(self, cap, cls, **kwds):
        self._stack = []
        self._cap = cap
        self._cls = cls
        self._idx = -1
        self.kwds = kwds

    def get(self):
        self._idx += 1
        if self._idx >= len(self._stack):
            self._stack.append(self._cls(**self.kwds))
        ret = self._stack[self._idx]
        return ret

    def release(self):
        self._idx -= 1
        # if we're over the cap, pop off the top item
        if len(self._stack) > self._cap:
            self._stack.pop()

def main():
    class Donk:
        def __init__(self, idx):
            self.idx = idx
        def __repr__(self):
            return "%s(%d)" % (self.__class__.__name__, self.idx)

    cs = CappedStack(3, Donk)
    for x in range(6):
        print cs.get(idx=x), len(cs._stack), cs._idx
    for x in range(5):
        cs.release()
        print len(cs._stack), cs._idx
    for x in range(4):
        print cs.get(idx=x), len(cs._stack), cs._idx

if __name__ == '__main__': main()


