# (C) Numbler Llc 2006
# See License For Details.

##
##
## sheet.py
##
## APIs for sheet backend
##

import types, sys, weakref
import ssdb, engine, cell, rangefinder
from sslib import observer, utils, mrudict, handle
import cPickle
from colrow import Col,Row

## We maintain only a sparse set of cells: only non-empty gridpoints
## get a cell instance

nonecmp = [None,'']

def sheetcmp(xinst,yinst):
    return _shtcmp(xinst,yinst,False)

def revsheetcmp(xinst,yinst):
    return _shtcmp(xinst,yinst,True)

def _shtcmp(xinst,yinst,reverse):
    """
    sheet comparision function that differentiates from normal cmp
    by always storing empty strings and None values at the bottom of a
    sort, regardless of the sort type.
    """

    x = xinst.eval(1)
    y = yinst.eval(1)
    
    if x in nonecmp:
        return y not in nonecmp and (reverse and -1 or 1) or 0
    elif y in nonecmp:
        return x not in nonecmp and (reverse and 1 or -1) or 0
    else:
        return cmp(x,y)    

class Sheet(observer.Observer):
    """represents a single spreadsheet

    Also is a cell observer... this is used internally.

    """
    _sheets = mrudict.MRUDict(64)

    def getInstanceFromHandle(cls, sheetHandle):
        return cls.getInstance(str(sheetHandle))
    getInstanceFromHandle = classmethod(getInstanceFromHandle)

    def getInstance(cls, sheetId):
        """pulls sheet from cache or DB, as required"""
        if sheetId in cls._sheets:
            return cls._sheets[sheetId]
        sheet = Sheet(sheetId)
        cls._sheets[sheetId] = sheet
        sheet._loadCells()
        return sheet
    getInstance = classmethod(getInstance)

    def getInstanceFromCache(cls,sheetId):
        if sheetId in cls._sheets:
            return cls._sheets[sheetId]
        return None
    getInstanceFromCache = classmethod(getInstanceFromCache)

    def getNew(cls, alias,principal):
        """Call this to instantiate a new blank sheet.  Call only
        once, ever, per sheet in db.

        FIXME: maybe roll this into getInstance

        """
        sheetId = utils.guid16()

        if type(alias) is unicode:
            alias = alias.encode('utf-8')
        ssdb.ssdb.getInstance().setSheetAlias(sheetId, alias,principal)
        return cls.getInstance(sheetId)
    getNew = classmethod(getNew)


    def getTemp(cls,ownerPrincipal):
        """ get a temporary sheet handle that is only used for specific
        operations, like parsing.
        """
        sheetID = utils.guid16()
        sheet = Sheet(sheetID)
        sheet.ownerPrincipal = ownerPrincipal
        cls._sheets[sheetID] = sheet
        return sheet
    getTemp = classmethod(getTemp)

    def __init__(self, sheetId):
        self.ssdb = ssdb.ssdb.getInstance()

        self._sheetHandle = SheetHandle.getInstance(sheetId)
        self._cellHandles = {}          # handles to all my non-empty cells in this sheet
        self.rangeFinder = rangefinder.RangeFinder()
        self._colProps = {}
        self._rowProps = {}
        self.eng = engine.Engine.getInstance()
        # the database ID for internal use
        self.sheetDbId = -1
        self.noRecalcCells = set()

    def _loadCells(self):
        """populate instance from DB/cache"""
        vals = self.ssdb.getSheetAlias(str(self._sheetHandle))
        self.alias,self.sheettype,self.sheetDbId,self.ownerID = vals
        self.ownerPrincipal = self.ssdb.getAccountByID(self.ownerID)

        # FIXME: overwrite cellhandle dict?  kinda brute force
        C, sh = cell.Cell, self._sheetHandle
        self._cellHandles = dict([(x.getKey(), x.cellHandle) for x in C.getCellsInSheet(sh,self.ownerPrincipal)])
        self.rangeFinder.load(sh)

    #def getRangeFinder(self):
    #    return self._rangeFinder

    def addCellHandle(self, cellHandle):
        key = cellHandle.getKey()
        if key in self._cellHandles:
            return
        self._cellHandles[key] = cellHandle

    def delete(self):
        # remove from the cache.  I don't think we need to bother
        # deleting from the cell cache as they will be orphaned
        # and eventually age out.
        del self._sheets[str(self._sheetHandle)]
        # delete from the db
        self.ssdb.deleteSheet(str(self._sheetHandle))

    def getHandle(self):
        return self._sheetHandle

    def getAlias(self):
        return self.alias

    def setAlias(self, alias,principal):
        self.alias = alias
        self.ssdb.setSheetAlias(str(self._sheetHandle), alias,principal)

    def getCellHandleIter(self):
        """returns an iterator for all [ non-empty  ** cut ] cellsHandles in sheet"""
        # this was bad... instantiating cell to get the handle can cause problems
        for handle in self._cellHandles.itervalues():
            # if handle().notempty():
            yield handle
            # else:
            #      continue

    def safeGetCellHandleIter(self):
        """
        return an iterator that is safe for use while mutating the cellHandle list.
        """
        for key in self._cellHandles.keys():
            yield self._cellHandles[key]

    def hasCell(self, col, row):
        """returns True if cell at col, row is set to some value"""
        
        key = col << 16 | row            # cell.getKey() inlined for perf
        if not key in self._cellHandles: return False
        cl = self._cellHandles[key]()
        return cl.notempty()

    def getCellHandle(self, col, row):
        """return cellHandle at row, col"""

        # pull cellhandle out of local dict...
        key = col << 16 | row           # cell.getKey() inlined for perf
        if key in self._cellHandles:
            return self._cellHandles[key]

        return cell.CellHandle(self._sheetHandle, col, row)

    # FIXME: add getIfHasCellHandle

    def getDimensions(self):
        """
        return size of sheet (maximum column row that contain values)
        not terribly efficient: use for debugging
        """
        engine.Engine.getInstance().log.info("CellRange.getDimensions")
        maxC = cell.Col('a')
        maxR = cell.Row(1)
        cols = [ch.getCol() for ch in self.getCellHandleIter()]
        rows = [ch.getRow() for ch in self.getCellHandleIter()]
        if len(cols):
            maxC = max(cols)
        if len(rows):
            maxR = max(rows)
        # return the maximums in the user space of rows and columns where
        # the set starts at 1
        return maxC+1, maxR+1

    def translate(self,col,row,ch):
        """ translate a formula based on the new position in the sheet"""
        
        formula = ch().getFormula()
        if len(formula) > 0 and formula[0] == '=':
            try:
                formula = '=%s' % self.eng.parser.parse(self._sheetHandle,formula[1:]).\
                          translate(col - ch.col,row - ch.row)
            except:
                # this is not good... it means we tried to move a cell to
                # a new location but that cell could not be parse originally
                pass
            return formula
        else:
            return formula
        
    def sortCells(self,fromSheetH,sortType,cRange):
        """
        sort a range range cells.  Sort only works on regions or columns.
        """
        if sortType in ('asc','desc'):
            startrow = cRange._ulRow
            startcol = cRange._ulCol
            endrow = cRange._lrRow
            endcol = cRange._lrCol
            eng = engine.Engine.getInstance()

            retRng = []
            delRng = []

            nfs = {}

            # step 1: compute the oldkeys dictionary - it tracks all of the
            # current cells in the range.  if those values are ever cleared out
            # the cell needs to be deleted.
            
            # when setting a new cell value we need to check if the delete list
            # has already been populated for this cell.  If so we need to remove it
            oldkeys = cell.CellRange(startcol,startrow,endcol,endrow).existingCellKeys(fromSheetH)
            
            # step 2: create the range for the first column
            rng = cell.CellRange(startcol,startrow,startcol,endrow)

            # step 3: sort the column.  Sorted uses an iterable and
            # returns a new sorted list.  sheetpcmp and revsheetcmp
            # are special compare functions that ensure that null values
            # and empty strings are always sorted to the bottom.
            
            rev = sortType == 'desc'
            sortedcol = sorted(rng.getCellHandlesIter(fromSheetH,False),
                               cmp=rev and revsheetcmp or sheetcmp,
                               reverse = rev)

            rowmapper = {}

            # step 4: iterate through the sorted column.  for every positive value
            # add to the update list.  Negative values we check to see if
            # that cell should be added to the delete list.
            for cellval,i in zip(sortedcol,cell.Row.getRange(startrow,endrow)):
                rowmapper[cellval.row] = i

                if cellval.eval(1) is not None:
                    # step 5: translate the cell and add to the update list
                    formula = self.translate(startcol,startrow,cellval)
                    nfs[self.getCellHandle(cellval.col,i)] = (formula,cellval().getFormat())

            # step 7: go through the cell handles that aren't part of the sort column
            # and check the proper location.
            if startcol != endcol:
                sortrng = cell.CellRange(startcol+1,startrow,endcol,endrow)
                for sortcellH in sortrng.getCellHandles(fromSheetH):
                    # find out new home for this cell.
                    newrow = rowmapper[sortcellH.row]
                    if newrow == sortcellH.row:
                        del oldkeys[sortcellH.key]
                    formula = self.translate(sortcellH.col,newrow,sortcellH)
                    newcell = self.getCellHandle(sortcellH.col,newrow)
                    nfs[newcell] = (formula,sortcellH().getFormat())

            cellsToNotify = {}
            
            # step 8: process Cell update list
            for cellH,(formula,format) in nfs.items():
                cellobj = cellH()
                cellobj.setFormula(formula,self.ownerPrincipal.locale,notify=False,notifyDict = cellsToNotify)
                cellobj.setFormat(format,notifyDict = cellsToNotify)

            #print 'nfs keys',nfs.keys()
            #print 'nfs cellkeys',[x.key for x in nfs.keys()]

            # step 9: delete the cells that didn't make it into the sort (because they were empty)
            cellHiter = [self._cellHandles[i] for i in set(oldkeys).difference(set([x.key for x in nfs.keys()]))]

            # deleteCelLHandleArray will do notification
            d = self.deleteCellHandleArray(cellHiter,cellsToNotify,selfNotify=True)

            # step 11: build out the cells that were returned (used for undo).
            # this is last because of the possible ripple effects of other
            # cell modifications
            return d, [cellH().getData() for cellH,(formula,format) in nfs.items()
                    if cellH() is not None]
        else:
            raise ValueError('%s not a valid sort option' % (sortType))

    def pasteFromBuffer(self, fromSheetH, cellBuf, ulCol, ulRow):
        """ paste a buffer of cells into the sheet. The cells are not
        currently part of the sheet"""

        # cellBuf is expected to be arraylike of cell-like objects
        # which support the following properties: "formula", "row",
        # "col", and "format" (for style cache). The first cell in the
        # array is expected to be the upper left
        nfs = {}
        tl = cellBuf[0]
        dc, dr = ulCol - cell.Col(tl.col), ulRow - cell.Row(int(tl.row))
        eng = engine.Engine.getInstance()
        for c in cellBuf:
            formula = c.formula.encode('utf-8')
            if len(formula) > 0 and formula[0] == '=':
                try:
                    nf = '=%s' % eng.parser.parse(fromSheetH,formula[1:]).translate(dc, dr)
                except:
                    # not good.. means the formula was originally not parsable
                    # so we need to go with the original formula
                    nf = formula
            else:
                nf = formula
            nfs[cell.CellHandle.getInstance(fromSheetH,
                                            cell.Col(c.col) + dc,
                                            cell.Row(int(c.row)) + dr)] = (nf,c.format)
        self._processPaste(nfs)

    def paste(self, fromSheetH, cellRange, ulCol, ulRow,sparse=True):
        """paste a cell range 'cellRange' from sheet handle 'fromSheetH'
        to cell at ulCol, ulRow"""
        # handle overlapping ranges -- convert all formulas, then place
        nfs = {}
        dc, dr = ulCol - cellRange._ulCol, ulRow - cellRange._ulRow

        if sparse:
            handles = cellRange.getCellHandles(fromSheetH)
        else:
            handles = cellRange.getFullCellHandles(fromSheetH)
        for cellHandle in handles:
            c = cellHandle()
            if c._ast:
                # nf = "=%s" % engine.parser.translate(c._ast, dc, dr)
                nf = "=%s" % c._ast.translate(dc, dr)
            else:
                nf = c.formula
            nfs[cell.CellHandle.getInstance(fromSheetH, cellHandle.col + dc,
                                            cellHandle.row + dr)] = (nf,c.getFormat())
        
        self._processPaste(nfs)

    def bagPaste(self,fromSheetH,cellbuf):
        """
        dump in a 'bag' or unordered set of cells into the database.
        """
        nfs = {}
        for c in cellbuf:
            nfs[cell.CellHandle.getInstance(fromSheetH,
                                            cell.Col(c.col),
                                            cell.Row(c.row))] = (c.formula.encode('utf-8'),c.format)
        self._processPaste(nfs)

    def _processPaste(self,nfs):
        # shared between the pastebuffer and pasting from cells in the sheet
        cellsToNotify = {}
        for key,(formula,format) in nfs.items():
            # keep notify list between pastes, do notify once
            cell = key()
            cell.setFormat(format,persist=False,notifyDict = cellsToNotify)
            cell.setFormula(formula, self.ownerPrincipal.locale,notify=False, notifyDict = cellsToNotify)
            # NOTE: you can't do persist = False here because the dependency stuff depends on the cell
            # existing in the db.  if this code was reconfigured to use the batch processor you could
            # use persist=False


            # persist=False
            #cell._saveToDb()
                    
        for sheetHandle in cellsToNotify:
            # print "notify", sheetHandle, ", ".join([str(x) for x in notifyDict[sheetHandle]])
            sheetHandle.notify(cellsToNotify[sheetHandle])

    def deleteCells(self, cellRange):
        """delete contents of all cells in range"""
        return self.deleteCellHandleArray(cellRange.getCellHandles(self._sheetHandle))

    def deleteCellHandleArray(self,cellHarr,notifyDict = None,selfNotify=False,saveData = None):
        """
        delete an arbitrary array of cell handles.
        """
        # create a batch delete context
        try:
            batchDelCtx = self.ssdb.newbatchDbCtx()

            if notifyDict is None:
                notifyDict = {}

            self._deleteCellHandlesBatch(cellHarr,batchDelCtx,notifyDict,selfNotify,saveData)
            # persist all the changes.
            d = batchDelCtx.save()

            for sheetHandle in notifyDict:
                sheetHandle.notify(notifyDict[sheetHandle])
            return d
        except:
            self.ssdb.clearBatchDbCtx()
            raise

    def _deleteCellHandlesBatch(self,cellHarr,ctx,notifyDict,selfNotify=False,saveData=None):
        for cellH in cellHarr:
            c = cellH()
            #print 'deleting',c,cellH
            # step 1: check the cell dependency.  if it has
            # depencies than we can't really delete it completely from
            # the database (because it will simply be created again the next
            # time the cell is referenced)
            saveVal = len(c.dependsOnMe) != 0

            # step 2: clear the format info
            c.setFormat("",persist=False,notifyDict = notifyDict)

            # step 3: update the cell. the persist flag indicates if a blank value
            # should be saved or not.
            #print 'clearing formula,selfNotify is',saveVal
            c.setFormula("", None,notify=False, notifyDict = notifyDict,persist=saveVal,selfNotify=selfNotify)

            # save off the cell contents for the UI
            if saveData is not None:
                saveData.append(c.getData())

            # step 4: delete the cell if it has no dependencies.  note that you can't
            # reuse saveVal here because dependsOnMe might change!
            if len(c.dependsOnMe) == 0:
                del self._cellHandles[c.getKey()]
                c.delete()
        

    def deleteCell(self,cellH,notify=True,notifyDict = None):
        """
        deleteCell should only be call when deleting a single cell
        in non batch scenarios.  In general, you should avoid this method
        and use deleteCellHandleArray
        """
        
        c = cellH()
        c.setFormula("", None,notify=notify, notifyDict = notifyDict)
        # this probably isn't necessary if you are going to delete the cell anyway
        c.setFormat("")
        
        # FIXME: only deletes cell if formula and format are empty
        # and nobody depends on cell.  Could allow deletion even
        # if someone depends on the cell if we unwire that dependency
        if len(c.dependsOnMe) == 0:
            del self._cellHandles[c.getKey()]
            c.delete()

    def notify(self):
        # proxy notifies to my sheetHandle
        self._sheetHandle.notify()

    # Observer implementation
    def update(self, notifyCells):
        # tell my observers that these cells have changed
        self.notify(notifyCells)

    ##
    ## Row and Column management
    ##
    def getRowProps(self):
        """returns a list of all non-default Rows in sheet"""
        ret = [RowProps(*x) for x in self.ssdb.getRows(str(self.getHandle()))]
        for rprop in ret:
            self._rowProps[rprop.getId()] = rprop
        return ret
    
    def getRowProp(self,row,defaultHeight):
        ret = self._rowProps.get(row)
        if ret:
            return ret

        res = self.ssdb.getRow(str(self.getHandle()),row)
        ret = len(res) != 0 and RowProps(*res[0]) or RowProps(row,defaultHeight,u'')
        self._rowProps[ret.getId()] = ret
        return ret
    
    def getColumnProps(self):
        """returns a list of all non-default Columns in sheet"""
        ret =  [ColumnProps(*x) for x in self.ssdb.getCols(str(self.getHandle()))]
        for cprop in ret:
            self._colProps[cprop.getId()] = cprop
        return ret

    def getColProp(self,col,defaultWidth):
        ret = self._colProps.get(col)
        if ret:
            return ret
        
        res = self.ssdb.getCol(str(self.getHandle()),col)
        ret = len(res) != 0 and ColumnProps(*res[0]) or ColumnProps(col,defaultWidth,u'')
        self._colProps[ret.getId()] = ret
        return ret

    def saveColumnProps(self, column):
        """persist column to db"""
        self.ssdb.setCol(str(self._sheetHandle), column.getId(), column.getWidth(), column.format)
        self._colProps[column.getId()] = column

    def saveRowProps(self, row):
        """persist row to db"""
        self.ssdb.setRow(str(self._sheetHandle), row.getId(), row.getHeight(), row.format)
        self._rowProps[row.getId()] = row

    def delColumnProps(self,column):
        self.ssdb.delCol(str(self._sheetHandle),column.getId())
        del self._colProps[column.getId()]
        
    def delRowProps(self,row):
        self.ssdb.delRow(str(self._sheetHandle),row.getId())
        del self._rowProps[row.getId()]

    def propInRowOrCol(self,row,col,propname):
        # arbitrary preference to columns
        ret = None
        cprop = self._colProps.get(col)
        if cprop:
            fmt = cprop.getFormat()
            if fmt:
                ret = fmt['cache'].get(propname)
        if ret is None:
            rprop = self._rowProps.get(row)
            if rprop:
                fmt = rprop.getFormat()
                if fmt:
                    ret = fmt['cache'].get(propname)
        return ret
        
    def _cellrange(self,cell1,cell2):
        return '%s:%s' % (cell1.getLocalStr(self._sheetHandle),cell2.getLocalStr(self._sheetHandle))

    def fxOnRange(self,formula,cell1,cell2):
        return '=%s(%s)' % (formula,self._cellrange(cell1,cell2))
    
    
    # topl = topleft cell of selection, botr = bottom right of selection
    def genSelectionFormulas(self,topl,botr,formulaType):
        """ generate formula's based on the user's selection.
        for the business rules see http://wiki.clingfire.net/index.php/Formulas """
        #print topl,botr
        l = topl.col
        r = botr.col+1
        t = topl.row
        b = botr.row+1
        undolist = []
        newformulas = [];

        # check the extents of the selection
        botrow = filter(lambda x: self.getCellHandle(x,botr.row).getCell().getFormula() == '',
                        range(l,r)) == range(l,r)
        rightcol = filter(lambda x: self.getCellHandle(botr.col,x).getCell().getFormula() == '',
                          range(t,b)) == range(t,b)
        if rightcol:
            for x in range(t,b):
                cell = self.getCellHandle(botr.col,x)()
                undolist.append(cell.getData())
                formula = self.fxOnRange(formulaType,
                                          self.getCellHandle(l,x),
                                          self.getCellHandle(r-2,x))
                newformulas.append(unicode(formula))
                cell.setFormula(formula,self.ownerPrincipal.locale)
            if not botrow:
                return undolist,newformulas

        if not botrow:
            # must search downwards for the proper row to utilize.
            # ideally this would be a good set operation for the database
            # but it doesn't seem to make much sense using our current sparse schema.
            found = False
            row = b
            while True:
                if not filter(lambda x: self.getCellHandle(x,row).getCell().getFormula() == '',
                              range(l,r)) == range(l,r):
                    row += 1
                else:
                    break;
        else:
            row = botr.row

        for x in range(l,r - (rightcol == True and 1 or 0)):
            cell = self.getCellHandle(x,row)()
            undolist.append(cell.getData())
            formula = self.fxOnRange(formulaType,
                                           self.getCellHandle(x,t),
                                           self.getCellHandle(x,max(1,b-2)))
            newformulas.append(unicode(formula))
            cell.setFormula(formula,self.ownerPrincipal.locale)

        return undolist,newformulas


    def referencedSheets(self):
        """ return a list of uniqe referenced sheets.
        The current implementation visits ever formula in the
        tree to extra the list of referenced sheets.
        """

        uniqSheets = set()

        for astgen in [cellI._ast.walk() for cellI in
         [cellH() for cellH in self.getCellHandleIter()]
         if cellI._ast]:
            for val in astgen:
                if hasattr(val,'getSheetHandle'):
                    uniqSheets.add(str(val.getSheetHandle()))

        # remove ourself
        uniqSheets.discard(str(self.getHandle()))
        return uniqSheets

    ## auth stuff

    def authRequired(self):
        return self.sheettype != 0

    def setAuthType(self,sheettype):
        """
        set the authentication required by the sheet.  This should only be called by the principal!
        """
        self.sheettype = sheettype

    def addRecalc(self,cellH):
        self.noRecalcCells.add(cellH)

    def clearRecalc(self,cellH):
        self.noRecalcCells.discard(cellH)


    def notifyRecalcCells(self):
        if not len(self.noRecalcCells):
            return
        
        notifydict = {}
        for cellH in self.noRecalcCells:
            cellH().notify(notifydict)
        for sheetHandle in notifydict:
            sheetHandle.notify(notifydict[sheetHandle])


    # column / row insert and delete

    def deleteColumn(self,col,delta,cbDef):
        """
        col is expected to be the end of the extend and delta is a negative number.
        """

        cr = cell.CellRange.getInstance(col + delta+1,Row(1),col,Row.getMax())
        d = self.deleteCellHandleArray(cr.getCellHandles(self._sheetHandle),selfNotify=True)
        d.addCallback(lambda _: self.insertColumn(col,delta,cbDef))
        return d

    def deleteRow(self,row,delta,cbDef):
        """
        row is expected to be the end of the extent and delta is a negative number
        """
        cr = cell.CellRange.getInstance(Col(1),row + delta+1,Col.getMax(),row)
        #print 'deleteRow: deletion cells are',cr.getCellHandles(self._sheetHandle),row+delta+1,row
        d = self.deleteCellHandleArray(cr.getCellHandles(self._sheetHandle),selfNotify=True)
        d.addCallback(lambda _: self.insertRow(row,delta,cbDef))
        return d

    def insertColumn(self,col,delta,cbDef):
        """
        insert new column(s) after col
        """
        d = self.ssdb.addColFindChangeCells(self._sheetHandle,int(col),delta)
        d.addCallbacks(self._processInsert,
                       callbackArgs=(int(col),delta),
                       callbackKeywords={'cbDef':cbDef})
        # for some reason setting the errback here means that the error doesn't
        # get propagated back to nevow.  I don't know why
        return d

    def insertRow(self,row,delta,cbDef):
        d = self.ssdb.addRowFindChangeCells(self._sheetHandle,int(row),delta)
        d.addCallbacks(self._processInsert,
                       callbackArgs=(0,0,int(row),delta),
                       callbackKeywords={'cbDef':cbDef})
                       #errback=cbDef.errback)
        return d

    def _checkForRowColAdjustments(self,targetcol=0,coldelta=0,targetrow=0,rowdelta=0):
        """
        see if we need to adjust the number of row or columns styles on a row or column
        insert or deletion.
        """
        if targetcol != 0:
            self.getColumnProps()
            props = self._colProps
            delta = coldelta
            adj = targetcol + ((coldelta < 0) and (coldelta+1) or 0)
        else:
            self.getRowProps()
            props = self._rowProps
            delta = rowdelta
            adj = targetrow + ((rowdelta < 0) and (rowdelta+1) or 0)

        saveprops = {}
        dellist = []

        if targetcol <> 0:
            if coldelta < 0:
                dellist = range(targetcol+coldelta+1,targetcol+1)
        else:
            if rowdelta < 0:
                dellist = range(targetrow + rowdelta + 1,targetrow+1)

        oldvals = [prop.values() for prop in props.itervalues()]
        changedict = {}

        removedict = {}
        
        for id,dim,format,prop in oldvals:
            #prop = props[propkey]
            print 'processing ',id,dim,format,prop
            if id in dellist:
                #prop.setFormat(u'')
                #prop.setVal(0)
                #prop.clear()
                removedict[id] = prop
                #saveprops[id] = prop
            elif id >= adj:
                newid = id+delta
                newp = props.get(newid)
                if not newp:
                    if targetcol != 0:
                        newp = ColumnProps(Col(newid),dim,u'')
                    else:
                        newp = RowProps(Row(newid),dim,u'')
                saveprops[newid] = newp
                changedict[newid] = True
                newp.setValue(dim)
                newp.setFormat(format)


        for id,dim,format,prop in oldvals:
            if id not in changedict and id >= adj:
                # clear the old prop
                #prop.clear()
                removedict[id] = prop                
                #saveprops[id] = prop
                #prop.setFormat(u'')

        # save off a list of changes
        updateStyles,removeStyles = [],[]

        for prop in removedict.itervalues():
            if prop.getId() not in saveprops:
                removeStyles.append(prop)
                if targetcol != 0:
                    self.delColumnProps(prop)
                else:
                    self.delRowProps(prop)

        for prop in saveprops.itervalues():
            #if prop.getFormat() == u'':
            #    removeStyles.append(prop)
            #else:
            assert prop._val != 0
            updateStyles.append(prop)
            if targetcol != 0:
                self.saveColumnProps(prop)
            else:
                self.saveRowProps(prop)

        return updateStyles,removeStyles


    def _processInsert(self,cells,targetcol=0,coldelta=0,targetrow=0,rowdelta=0,cbDef=None):

        # if the user adds another column that is after all cells in the sheet
        # there is no action to take.
        
        #if not len(cells): 
        #    return

        changelist = {}
        notifydict = {}

        deletionlist = []

        # process all the cells that we found from our db query.
        # any cells that have a formula are mutated into the new location.
        
        for cellId,col,row in cells:
            cellH = self.getCellHandle(col,row)
            cellI = cellH()

            cellIsMoving = True

            # only add to the deletion list if the cell is >= the expansion range.
            if targetcol != 0 and col >= targetcol:
                deletionlist.append(cellH)
            elif targetrow != 0 and row >= targetrow:
                deletionlist.append(cellH)
            else:
                # in this case the cell is not moving, it is simply referencing
                # a cell in the move area.
                cellIsMoving = False
                
            if cellI._ast is not None:
                formula = '=%s' % cellI._ast.mutate(targetrow,rowdelta,targetcol,coldelta)
            else:
                formula = cellI.formula
            newH = cell.CellHandle.getInstance(self._sheetHandle,
                                               max(1,cellH.col + (cellIsMoving and coldelta or 0)),
                                               max(1,cellH.row + (cellIsMoving and rowdelta or 0)))
            changelist[newH] = (formula,cellI.getFormat())


        delcells = set(deletionlist)
        
        ## create a new batch context.  save all the new cells.
        try:
            batchCtx = self.ssdb.newbatchDbCtx()

            # if we have to adjust any column or row styles do it here.
            colrowchanges = self._checkForRowColAdjustments(targetcol,coldelta,targetrow,rowdelta)

            for cellH,(formula,format) in changelist.items():

                # discard from deletion list if we are adding. this can happen
                # if there are cells that were next to us that now occupy a new position.
                delcells.discard(cellH)
                cellI = cellH(loadFromDb=False)
                cellI.setFormat(format,notifyDict=notifydict,persist=False)
                cellI.setFormula(formula,self.ownerPrincipal.locale,notifyDict=notifydict,persist=False)
                cellI._saveToDb()

            # delete all the old cells.
            self._deleteCellHandlesBatch(delcells,batchCtx,notifydict,selfNotify=True)

            # do the database work.  when done we will notify all of the changed cells.
            # Note: it feels like there needs to be some sort of sheet level locking here for this
            # kind of operation. this is async.
            d = batchCtx.save()
            d.addCallback(self.doNotifyOnBatchCompletion,colrowchanges,notifydict)
            if cbDef:
                d.chainDeferred(cbDef)
            return d
        except:
            self.ssdb.clearBatchDbCtx()
            raise
                      
    def doNotifyOnBatchCompletion(self,arg,colrowchanges,notifyDict):
        for sheetHandle in notifyDict:
            sheetHandle.notify(notifyDict[sheetHandle])
        return arg,colrowchanges
        

# A SheetHandle isa SheetID -- str() to get val
class SheetHandle(handle.Handle, observer.Subject):
    """
    observe this sheetHandle for cell changes.  When a cell's formula or
    value changes, this calls observer.update([cell, cell, cell...])
    """
    _Obj = Sheet

    def argsToKey(cls, sheetId):
        return str(sheetId)
    argsToKey = classmethod(argsToKey)

    def __init__(self, sheetId):
        handle.Handle.__init__(self)
        observer.Subject.__init__(self)
        self.sheetId = sheetId

    def __repr__(self):
        return "%s(%s)" % (self.__class__, repr(self.sheetId))

    def __str__(self):
        return self.sheetId

    def getSheet(self):
        # FIXME: deprecated -- use __call__() instead
        return self()

class PropMixin(object):
    def getKey(self):
        return self.keyprefix + str(int(self._id))
    
    def setFormat(self,format):
        self.format = format and len(format) > 0 and cPickle.dumps(format) or u''

    def getFormat(self):
        return len(self.format) and cPickle.loads(self.format) or unicode(self.format)

    def __cmp__(self,other):
        return cmp(self._id,other._id)

    def __str__(self):
        return '%s: %d %s' % (self.__class__.__name__,self._id,self.getFormat())

    def __repr__(self):
        return self.__str__()

    def getData(self):
        """ return a simplified rep for JSON consumption"""
        return {u'key':unicode(self.getKey()),u'id': int(self._id), u'val': self._val, u'format': self.getFormat()}

    def getId(self):
        return self._id

    def clear(self):
        self.format = u''
        self._val = 0

    def values(self):
        return self._id,self._val,self.getFormat(),self

    def setValue(self,val):
        self._val = val

class RowProps(observer.Subject,PropMixin):

    keyprefix = 'r'

    def __init__(self, row, height, format):
        self._id = row                  # An ast.row instance
        self._val = height              # 0 - 65535 pixels
        self.format = format

    def setHeight(self, height):
        self._val = height

    def getHeight(self):
        return self._val


class ColumnProps(observer.Subject,PropMixin):
    keyprefix = 'c'

    def __init__(self, col, width, format):
        self._id = col                  # An ast.col instance
        self._val = width               # 0 - 65535 pixels
        self.format = format

    def setWidth(self, width):
        self._val = width

    def getWidth(self):
        return self._val

def main():
    # testing moved to regression.py
    eng = engine.Engine.getInstance()
    shtH = SheetHandle.getInstance("booya")

    h = shtH().getCellHandlesInRange(cell.CellHandle.parse(shtH, "a1"),
                                     cell.CellHandle.parse(shtH, "z10"))         # WTF???
    for x in h:
        print x


def testhelper():
    eng = engine.Engine.getInstance()
    shtH = SheetHandle.getInstance("booya")
    return sht

if __name__ == '__main__': main()
