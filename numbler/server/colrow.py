# (C) Numbler LLC 2006
# See LICENSE for details.

##
## colrow.py
##
## Column and Row implementations
##

from exc import *

# There are only 256 possible Columns.  Build all of them, and put
# them in a lookup table.  Instantiating a column returns one from the
# table.

class _MetaCol(type):

    # Traps Col instantiations
    def __call__(cls, val):
        t = type(val)
        if t is int or t is long:
            if val < 1 or val > 256:
                raise SSRangeError("%d outside of valid column range 1 - 256" % val)
            return cls._instances[val - 1]
        elif t is str or t is unicode:
            lw = val.lower()
            if not lw in cls._strLookup:
                raise SSRangeError("%s outside of valid column range (A - IV)" % lw)
            return cls._strLookup[lw]
        else:
            raise SSValueError("%s of illegal type %s" % (val, t))

class Col(int):
    """represents a column. valid range from a (1) to iv (256)"""
    __metaclass__ = _MetaCol

    _maxVal = 256
    
    _instances = []
    _strLookup = {}

    @classmethod
    def _Init(cls):
        for c in range(1, cls._maxVal + 1):
            newC = cls.__new__(cls, c)
            cStr = cls._getStr(c)
            newC._strVal = cStr
            cls._instances.append(newC)
            cls._strLookup[cStr] = newC

    @classmethod
    def _getStr(cls, val):
        # from number to a-z, aa, ab, ac, etc...
        v = val - 1
        a = v / 26
        return "%s%s" % (a and chr(a + 96) or "", chr(v % 26 + 97))

    @classmethod
    def getMax(cls):
        """return maximum possible column"""
        return cls._instances[cls._maxVal - 1]

    @classmethod
    def getRange(cls, val0, val1):
        """returns range between col0 and col1, including endpoints"""
        return cls._instances[val0-1:val1]

    def __str__(self):
        # Old conv code
        # val = val.lower()
        # num = ord(val[0]) - 96
        # if len(val) == 2:
        #    num = num * 26 + ord(val[1]) - 96
        return self._strVal

    def __repr__(self):
        return "colRow.Col('%s')" % (str(self))

# Prep Col
Col._Init()

# Too many Rows for lookup table.. return new ones every time
class Row(int):
    """represents a row.  1 to 65536"""
    _maxVal = 65536

    @classmethod
    def getRange(cls, row0, row1):
        """returns range betwen row0 and row1, including endpoints"""
        return [cls(r) for r in xrange(row0, row1 + 1)]

    @classmethod
    def getMax(cls):
        """return maximum possible column"""
        return Row(Row._maxVal)

    def __init__(self, val):
        if val < 1 or val > self._maxVal:
            raise SSRangeError("row %d outside of valid range 1 - %d" % (val, self._maxVal))

    def __repr__(self):
        return "colrow.Row(%d)" % (int(self))

def test():
    # rudimentary tests
    for x in ["a", "b", "c", "d"]:
        c = Col(x)
        print "c", repr(c), "str", str(c), "int", int(c), "type", type(c), "id", id(c), "*2", c * 2

    print
    print Col.getRange(4, 7)
    
    for x in Row.getRange(1, 5):
        r = Row(x)
        print "r", repr(r), "str", str(r), "int", int(r), "type", type(r), "id", id(r)

def main():
    import profile, pstats
    profile.run("test()", "teststats.dat")
    p = pstats.Stats("teststats.dat") 
    p.sort_stats('cumulative').print_stats()

if __name__ == '__main__': main()
