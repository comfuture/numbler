# (C) Numbler LLC 2006
# See LICENSE for details.

##
## dump.py
##
## Dump a sheet to stdout
##

import sys, os
import sheet, cell, engine

def getTerminalDimensions():
    import struct, fcntl, termios
    height, width = struct.unpack(
        "hhhh", fcntl.ioctl(0, termios.TIOCGWINSZ ,"\000"*8))[0:2]
    return height, width 

def dump(sht, dfunc, maxC, maxR):
    th, tw = getTerminalDimensions()
    cw = (tw - 8 - int(maxC)) / int(maxC)
    
    printme = []

    # Column header
    printme.append("   ")
    for col in cell.Col.getRange(cell.Col(1), maxC):
        fmt = " %" + "%d.%ds" % (cw, cw)
        printme.append(fmt % col)
    printme.append("\n")

    fmt = "|%" + "%d.%ds" % (cw, cw)
    for row in cell.Row.getRange(1, int(maxR)):
        printme.append("%4.4s" % row)
        for col in cell.Col.getRange(cell.Col(1), maxC):
            if sht.hasCell(col, row):
                printme.append(fmt % dfunc(sht.getCellHandle(col, row)()))
            else:
                printme.append(fmt % "")
        printme.append("|\n")
    print "".join(printme)

def noNone(val):
    if val is None:
        return ""
    return val

def dumpAll(shtH, verbose=False):
    """shth: sheetHandle"""
    sht = shtH()
    maxC, maxR = [x - 1 for x in sht.getDimensions()]

    if verbose:
        funcs = str, lambda x: noNone(x.getValue()), lambda x: " ".join(map(lambda y: y.getLocalStr(shtH), x.getDependsOnMe())), \
                lambda x: x.getFormulaR1C1()
    else:
        funcs = str, lambda x: noNone(x.getValue())
    for func in funcs:
        print
        dump(sht, func, maxC, maxR)

def doDump():
    eng = engine.Engine.getInstance()
    eng.log.quiet = True
    verbose = False
    if sys.argv[1] == "-v":
        verbose = True
        del sys.argv[1]

    sheetId = sys.argv[1]
    shtH = sheet.SheetHandle.getInstance(sheetId)
    dumpAll(shtH, verbose)
    
def main():

    if sys.argv[1] == "-p":
        profileIt = True
        del sys.argv[1]
    else:
        profileIt = False

    if profileIt:

        import profile, pstats
        profile.run("doDump()", "dumpstats.dat")
        p = pstats.Stats("dumpstats.dat") 
        p.sort_stats('cumulative').print_stats(40)
        p.sort_stats('calls').print_stats(40)
        # p.sort_stats('time').print_stats(40)
    else:
        doDump()

if __name__ == '__main__':
    main()

