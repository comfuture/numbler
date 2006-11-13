# (C) Numbler Llc 2006
# See License For Details.

##
## rangefinder.py
##
## Contains ranges for a sheet.  Looks up cell stabs 
##

import ssdb, sheet, cell

class RangeFinderError(ValueError):
    pass

#
# Implements lame O(n) search.  Could be improved to log(n)
#
class RangeFinder:
    def __init__(self):
        # rangeMap is
        # {range: set([cellHandle, cellHandle]), ... }
        self._rangeMap = {}

    def load(self, sheetHandle):
        """load from db"""

        ranges = ssdb.ssdb.getInstance().getRangesOnSheet(str(sheetHandle))

        rm = {}
        for rng in ranges:
            obsSheetHandle = sheet.SheetHandle.getInstance(rng[0])
            obsCellHandle = cell.CellHandle.getInstance(obsSheetHandle, cell.Col(rng[1]), cell.Row(rng[2]))
            r = cell.CellRange.getInstance(cell.Col(rng[3]), cell.Row(rng[4]), cell.Col(rng[5]), cell.Row(rng[6]))

            # duplicated below in add, but saves fn call
            if r in rm:
                chs = rm[r]
            else:
                chs = set()
                rm[r] = chs
            chs.add(obsCellHandle)

        self._rangeMap = rm
        return self
    
    def hasMap(self, rng, cellHandle):
        rm = self._rangeMap
        return rng in rm and cellHandle in rm[rng]

    def add(self, sht, rng, cellHandle,noSave = False):
        """
        cell with cellHandle has range in it's AST
        """
        rm = self._rangeMap
        if rng in rm:
            chs = rm[rng]
        else:
            chs = set()
            rm[rng] = chs

        if cellHandle not in chs:
            chs.add(cellHandle)

            dbStuff = rng.get()
            args = (str(sht), dbStuff[0], dbStuff[1], dbStuff[2], dbStuff[3],
                    (str(cellHandle.getSheetHandle()), cellHandle.getCol(), cellHandle.getRow()))
            
            if not noSave:
                ssdb.ssdb.getInstance().setRangeDep(*args)
            else:
                return args

    def dumpMap(self):
        return [str(rng) for rng in self._rangeMap]
                                            

    def remove(self, sht, rng, cellHandle):
        """removes this range -> cellHandle mapping"""
        if not rng in self._rangeMap:
            raise RangeFinderError("no range %s in %s" % (rng, self))

        chs = self._rangeMap[rng]
        
        if not cellHandle in chs:
            raise RangeFinderError("no cellHandle %s in %s in %s" % (cellHandle, rng, self))

        chs.remove(cellHandle)
        dbStuff = rng.get()
        ssdb.ssdb.getInstance().deleteRangeDep(str(sht), dbStuff[0], dbStuff[1], dbStuff[2], dbStuff[3],
                                                (str(cellHandle.getSheetHandle()), cellHandle.getCol(), cellHandle.getRow()))
        
    # Violate's cell.CellRange's privacy, but makes HUGE improvement
    # for lots of ranges
    def intersects(self, cellHandle):
        """Returns list of cellHandles with ranges that intersect given cellHandle"""
        ret = []
        col, row = cellHandle.col, cellHandle.row
        for rng, cells in self._rangeMap.iteritems():
            if col >= rng._ulCol and \
               col <= rng._lrCol and \
               row >= rng._ulRow and \
               row <= rng._lrRow:
                ret.extend(list(cells))
        return ret

    def intersects2(self, cellHandle):
        """Returns list of cellHandles with ranges that intersect given cellHandle"""
        ret = []
        col, row = cellHandle.col, cellHandle.row
        for rng, cells in self._rangeMap.iteritems():
            if rng.inRangeCR(col, row):
                ret.extend(list(cells))
        return ret
