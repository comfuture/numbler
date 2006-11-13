# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.


# csv specific
import csv,traceback,sys
from StringIO import StringIO
from twisted.internet.defer import deferredGenerator,waitForDeferred
from numbler.utils import yieldDef

from numbler.server.colrow import Col,Row
from numbler.server.sheet import Sheet
from numbler.importwarnings import *

class CSVImporter(object):
    """
    Import CSV files
    """
    
    def __init__(self,sourcedata,sheetname,principal):
        self.sourcedata = sourcedata
        self.sheetname = sheetname
        self.principal = principal

    def continueImport(self):
        """ indicate if the UI should continue import.
        since CSV files only contain one spreadsheet this always
        returns false.
        """
        return False

    @deferredGenerator
    def generateSheet(self,defcb):
        """ run the import using a complicated list comprehension """

        try:
            newsheet = Sheet.getNew(self.sheetname,self.principal)
            memfile = StringIO(self.sourcedata)

            rowcnt = 1
            yieldcount = 1
            cells = []
            
            for row in csv.reader(memfile):
                if len(row) != 0:
                    for col,formula in zip(range(1,len(row)+1),row):
                        if len(formula) == 0:
                            continue
                        formula = unicode(formula,'iso-8859-1').encode('utf-8')
                        cells.append((col,rowcnt,u'',formula))
                        yieldcount += 1
                        if yieldcount % 10 == 0:
                            yield waitForDeferred(yieldDef())

                rowcnt += 1

            from numbler.server import ssdb,cell
            sdb = ssdb.ssdb.getInstance()
            # add all the cells at once
            yield waitForDeferred(sdb.bulkLoadCells(str(newsheet.getHandle()),cells))
            # dump data in the cell cache.  Don't know if this is really necessary with CSV
            # as there are no dependencies to build
            cell.Cell.bulkLoadCells(newsheet.getHandle(),cells)
            
            defcb.callback((str(newsheet.getHandle()),newsheet.getAlias()))
        except Exception,inst:
            print 'Error caught while generating sheet from CSV',inst
            traceback.print_tb(sys.exc_info()[2])
            defcb.errback(inst)
