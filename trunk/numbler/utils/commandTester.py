#!/usr/bin/env python
############################################################
## Copyright (c) 2006 Numbler LLC
############################################################

from numbler.server import engine,sheet,cell
from numbler.server.colrow import Col,Row
from optparse import OptionParser

eng = engine.Engine.getInstance()




def getsheetH(name):
    return sheet.Sheet.getInstance(name).getHandle()
    

def main():

    parser = OptionParser()
    parser.add_option("-s","--sheet",dest="sheetUID",help="sheet to load")
    parser.add_option("-c","--cell",action="store",dest="cell",
                      help="target cell.  Default action will dump cell contents")
    parser.add_option("-f","--formula",action="store",dest="formula",help="formula for cell")
    parser.add_option("-r","--rangedeps",action="store_true",dest="rangedeps",help="dump the sheet range dependencies")

    (options,args) = parser.parse_args()
    print options,args

    if not options.sheetUID:
        print 'sheetUID required.'
        return

    shtH = getsheetH(options.sheetUID)

    if options.rangedeps:
        rangef = shtH().getRangeFinder()
        print '*** stored ranges *** '
        print '\n'.join(rangef.dumpMap())

    if options.cell:
        cellH = cell.CellHandle.parse(shtH,options.cell)
        if options.formula:
            cellH().setFormula(options.formula)
        print cellH().getData()
        

    # print yacc.parse("4 + C")
    
if __name__ == '__main__': main()
