# (C) Numbler LLC 2006
# See LICENSE for details.

##
## getdeps.py sheetName cell
##
## prints all dependencies of cell
##

import sys
import engine, sheet, cell

def getDepsR(total, printed, cellHandle):
    deps = cellHandle().getDependsOnMe()
    print "%8s %16.16s: " % (cellHandle, cellHandle().formula),
    for x in deps:
        total.add(x)
        print "%s [%s]" % (x.getLocalStr(cellHandle.getSheetHandle()), x().formula),
    print
    printed.add(cellHandle)
    for x in deps:
        if x not in printed:
            getDepsR(total, printed, x)

def getDeps():
    eng = engine.Engine.getInstance()
    eng.log.quiet = True

    shtH = sheet.SheetHandle.getInstance(sys.argv[1])
    cellHandle =  cell.CellHandle.parse(shtH, sys.argv[2])
    total = set()
    printed = set()
    getDepsR(total, printed, cellHandle)
    print
    print "total", len(total), ":"
    for x in total:
        print x.getLocalStr(cellHandle.getSheetHandle()),

def main():
    getDeps()

if __name__ == '__main__':
    main()
