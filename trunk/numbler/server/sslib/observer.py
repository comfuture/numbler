# (C) Numbler Llc 2006
# See License For Details.

# Abstract Class - implement this
class Observer(object):
    def update(self, *args, **kwargs):
        pass

class RangeObserver(Observer):
    def setRange(self, range):
        """range: a utils.Range2d instance"""
        self.range = range

class Subject(object):
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def detach(self,observer):
        if observer in self.observers:
            del self.observers[self.observers.index(observer)]

    def detachIndex(self, index):
        del self.observers[index]

    def notify(self, *args, **kwargs):
        for observer in self.observers:
            observer.update(self, *args, **kwargs)

    def getCount(self):
        return len(self.observers)

class RangeSubject(Subject):
    def notify(self, cells):
        for observer in self.observers:
            
            observer.update(self, *args, **kwargs)
        

class ObservedVal(Subject):
    """Holds a value.  Notifies observers of changes"""

    def __init__(self, val):
        Subject.__init__(self)
        self.val = val
        self.changed = False

    def set(self, val):
        if self.val == val: return
        self.val = val
        self.notify()

    def get(self):
        return self.val

