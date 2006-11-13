# (C) Numbler LLC 2006
# See LICENSE for details.

##
## cell.py
##
## Classes that represent column IDs, row IDs, cellIds, cellHandles, cells
##

import re, weakref, sys
import engine, sheet, ssdb, exc
from sslib import observer, mrudict, handle,singletonmixin
from colrow import Col, Row
import cPickle
import types
from math import modf
from localedb import LocaleParser,ParseCtx
from exc import LiteralConversionException
from littools import LitNode
from decimal import Decimal
from twisted.python import context
from numblerInterfaces import RecalcMixin
from numbler.wsmanager import FormulaTxnManager

class Cell(object):

    # _cells = mrudict.MRUDict(32)
    # _cells = mrudict.MRUDict(1024)
    # _cells = mrudict.MRUDict(2048)
    # _cells = mrudict.MRUDict(4096)
    _cells = mrudict.MRUDict(16384)
    
    def _getInstance(cls, cellHandle, loadFromDb=False):
        """pulls cell from cache or DB, as required"""
        if cellHandle in cls._cells:
            return cls._cells[cellHandle]
        # print "cache miss", cellHandle, len(cls._cells)
        # Create a new Cell instance.  This is the ONLY place a new
        # cell is instantiated.

        cell = Cell(cellHandle)
        if loadFromDb: cell._loadFromDb()
        cls._cells[cellHandle] = cell
        return cell
    _getInstance = classmethod(_getInstance)

    def getInstance(cls, cellHandle):
        """pulls cell from cache or DB, as required"""
        return cls._getInstance(cellHandle, loadFromDb=True)
    getInstance = classmethod(getInstance)


    def bulkLoadCells(cls,shtH,celldata):
        """ bulk load a number of cells into the cache from an in memory rep
        this method assumes the data is clean.

        the format is expected to be a list of cells with format
        (col,row,style,format)
        """
        shtI = shtH()
        for cellrep in celldata:
            cellH = shtI.getCellHandle(cellrep[0],cellrep[1])
            newcell = Cell(cellH)
            newcell.format = cellrep[2]
            newcell.formula = cellrep[3]
            cls._cells[cellH] = newcell
    bulkLoadCells = classmethod(bulkLoadCells)

    # Generator: Bulk-loads all cells for sheet with given sheetId
    def getCellsInSheet(cls, sheetHandle,ownerPrincipal):
        db = ssdb.ssdb.getInstance()
        data = db.getCells(str(sheetHandle))
        if len(data) == 0: return

        # bulk-load deps from db, build lookup dict
        deps = {}
        for dep in db.getAllDeps(str(sheetHandle)):
            key = dep[0], dep[1]
            val = dep[2:]
            if key in deps:
                deps[key].append(val)
            else:
                deps[key] = [val]

        sh = sheetHandle()
        for entry in data:
            col, row = entry[0], entry[1]
            cellHandle = sh.getCellHandle(col, row)
            cell = cls._getInstance(cellHandle)
            cell.format = entry[3]
            if cell.format == None:
                engine.Engine.getInstance().log.info("getCellsInSheet: None format")
            cell.setFormulaFromDb(entry[2],ownerPrincipal.locale)
            if (col, row) in deps:
                cell.dependsOnMe = set([CellHandle.getInstance(sheet.SheetHandle.getInstance(x[2]), x[0], x[1]) for x in deps[col, row]])
            # cls._cells[cellHandle] = cell     # cache it
            yield cell
    getCellsInSheet = classmethod(getCellsInSheet)

    def __init__(self, cellHandle):

        # Cell instantiation creates its own handle
        self.cellHandle = cellHandle

        # Design: rather than keeping references to individual cell
        # dependencies, it would be better to keep references between
        # 2d ranges of dependencies
        self.iDependOn = set()          # cellHandles I depend on
        self.dependsOnMe = set()        # cellHandles that depend on me
        self.rangesIDependOn = set()    # each entry: (sheetHandle, CellRange)

        self.formula = ""
        self.format = ""

        self._val = None                # cached evaluated value
        self._ast = None                # cached evaluated value
        self._dictfmt = None            # cached format dictionary
        self._txnMgr = None             # transaction mgr for asynchronous functions

    def __repr__(self):
        return "%s(%s, %s, %s)" % (self.__class__, repr(self.cellHandle.getSheetHandle()),
                                   repr(self.cellHandle.getCol()),
                                   repr(self.cellHandle.getRow()))
    def __str__(self):
        return self.formula or ""

    def __del__(self):
        pass
        #engine.Engine.getInstance().log.info("Cell.__del__ finalized", self.cellHandle)

    def _loadFromDb(self):
        shcr = self.cellHandle.getSHColRow()

        cellData = engine.Engine.getInstance().ssdb.getCell(*shcr)
        if cellData:
            self._setFormula(cellData[0],self.cellHandle.sheetHandle().ownerPrincipal.locale)
            self.format = cellData[1]
            if self.format == None:
                engine.Engine.getInstance().log.info("_loadFromDb: None format")
            # loads all direct dependencies for this cell
            sdb = ssdb.ssdb.getInstance()
            dom = sdb.getDependsOnMe(shcr) or {}
            self.dependsOnMe = set([sheet.SheetHandle.getInstance(x[2])().getCellHandle(x[0], x[1]) for x in dom])


    def _saveToDb(self):
        engine.Engine.getInstance().ssdb.setCell(self.formula, self.format, *self.cellHandle.getSHColRow())

    def getKey(self):
        return self.cellHandle.key

    def getHandle(self):
        return self.cellHandle

    def getSheetHandle(self):
        return self.cellHandle.getSheetHandle()

    def getSheet(self):
        return self.cellHandle.getSheetHandle()()

    def getName(self):
        return str(self.cellHandle)

    def delete(self):
        ssdb.ssdb.getInstance().deleteCell(*self.cellHandle.getSHColRow())

        del self.iDependOn
        del self.dependsOnMe
        del self.rangesIDependOn

        self._val = None
        self._ast = None

        del Cell._cells[self.cellHandle]
        self.cellHandle._obj = None
        self.cellHandle = None

    def clearDep(self, cellHandle):
        self.dependsOnMe.discard(cellHandle)
        # FIXME: blow out of db??

    def updateDeps(self, newDeps):
        """newDeps: a set of cellHandles.  removes old deps and adds new deps.  updates database"""

        sdb = ssdb.ssdb.getInstance()
        ch = self.cellHandle

        # print "woot", self.cellHandle
        # print "old     ", " ".join(str(x) for x in self.iDependOn)
        # print "new     ", " ".join(str(x) for x in newDeps)
        notInNew = self.iDependOn.difference(newDeps)
        notInOld = newDeps.difference(self.iDependOn)
        # print "notInNew", " ".join(str(x) for x in notInNew)
        # print "notInOld", " ".join(str(x) for x in notInOld)
        self.iDependOn = newDeps

        for dep in notInNew:
            dep().dependsOnMe.discard(ch)       # remove me from deps observers
            # print "deleting dep", dep, ch
            sdb.deleteDep(dep.getSHColRow(), ch.getSHColRow())

        for dep in notInOld:
            dpc = dep()
            if ch not in dpc.dependsOnMe:
                dpc.dependsOnMe.add(ch)
                # print "setting dep", dep, ch
                sdb.setDep(dep.getSHColRow(), ch.getSHColRow())
        # print

    def bulkGetDeps(self):
        """ fetch all of the dependencies for a cell but don't persist them.
        this function can only be used in bulk load scenarios (like import)"""
        ch = self.cellHandle

        sdb = ssdb.ssdb.getInstance()
        observer = sdb.safeGetCellId(*ch.getSHColRow())

        celldeps = []
        for dep in self.iDependOn:
           dpc = dep()
           if ch not in dpc.dependsOnMe:
               dpc.dependsOnMe.add(ch)
               celldeps.append((sdb.safeGetCellId(*dep.getSHColRow()),observer))

        rangedeps = []
        for dep in self.rangesIDependOn:
            sht = dep[0]
            rf,rng = sht().rangeFinder,dep[1]
            if not rf.hasMap(rng,ch):
                rangedeps.append(rf.add(sht,rng,ch,noSave=True))

        return celldeps,rangedeps

    def updateRangeDeps(self, newDeps):
        ch = self.cellHandle

        # print "old     ", " ".join(str(x) for x in self.rangesIDependOn)
        # print "new     ", " ".join(str(x) for x in newDeps)
        notInNew = self.rangesIDependOn.difference(newDeps)
        notInOld = newDeps.difference(self.rangesIDependOn)
        # print "notInNew", " ".join(str(x) for x in notInNew)
        # print "notInOld", " ".join(str(x) for x in notInOld)

        self.rangesIDependOn = newDeps

        for dep in notInNew:
            sht = dep[0]
            # print "map", sht().rangeFinder._rangeMap
            sht().rangeFinder.remove(sht, dep[1], ch)

        for dep in notInOld:
            sht = dep[0]
            rf, rng = sht().rangeFinder, dep[1]
            if not rf.hasMap(rng, ch):
                rf.add(sht, rng, ch)
                
    def clearIDependOn(self):
        """Remove my dependencies.  Also removes this cell from each
        of my dependencies' dependsOnMe"""
        for cellHandle in self.iDependOn:
            cellHandle().clearDep(self)
        self.iDependOn.clear()

        ssdb.ssdb.getInstance().clearDeps(self.cellHandle.getSHColRow())

    def getDependsOnMe(self):
        """returns set containing cellHandles that depend on me,
        either directly or via ranges"""
        # add in range-based deps
        rangeCellHandles = self.cellHandle.sheetHandle().rangeFinder.intersects(self.cellHandle)
        return self.dependsOnMe.union(rangeCellHandles)

    def getFormula(self):
        """return cell formula"""
        return self.formula

    def getTxnMgr(self):
        if self._txnMgr is None:
            self._txnMgr = FormulaTxnManager(self.cellHandle)
        return self._txnMgr

    def getFormulaR1C1(self):
        """return cell formula in legacy R1C1 notation"""
        if self._ast:
            return self._ast.getR1C1(self.cellHandle)
        else:
            return self.formula

    def notempty(self):
        try:
            return len(self.formula) != 0 or len(self.format) != 0
        except TypeError,e:
            print '** notempty exception caught',self.formula,self.format,type(self.format)
            raise e

    def getFormat(self):
        """ return the cell format.  Don't use for checking if format exists!!"""

        # return the cached value if it is present
        if self._dictfmt: return self._dictfmt
        elif len(self.format):
            self._dictfmt = cPickle.loads(self.format)
            return self._dictfmt
        else:
            return u''

    def notify(self, notifyDict):
        """builds notifyDict: a dict of sheetHandles to notify, with cells changed
           = {sheetHandle0: set(ch0, ch1, ch2...)
              sheetHandle1: set(ch0, ch1, ch2...)...}

           collects sheets, cells
        """
        cellHandle = self.cellHandle
        sheetHandle = cellHandle.sheetHandle

        if self._txnMgr is not None and self._txnMgr.isAsync:
            for nodeval in self._ast.getAsyncNodes(1,True):
                nodeval.clearCachedValue()



        if sheetHandle in notifyDict:
            cellSet = notifyDict[sheetHandle]

            if cellHandle in cellSet:
                # don't search this branch farther: already searched
                return
        else:
            cellSet = set()
            notifyDict[sheetHandle] = cellSet

        cellSet.add(cellHandle)

        # invalidate cached value
        self._val = None

        # notify dependent cells
        for dom in self.getDependsOnMe():
            dom().notify(notifyDict)

    def _setFmtOnParse(self,fmt,ftype):
        changed = False
        if not fmt:
            fmt = self.getFormat()
            if not fmt:
                fmt = {}
        existing = fmt.get('__sht')
        if not (existing and existing == ftype):
            changed = True
            fmt[u'__sht'] = ftype
        return fmt,changed

    def deferredFormatCheck(self):
        """
        run the formatting check at the end of an asynchronous operation.
        """
        if not self.numFormat():
            try:
                self.updateFormatNoSave(self._ast.getImpliedFormatting(1))
            except exc.SSCircularRefError,e:
                pass
            except RuntimeError,e:
                print 'deferredFormatCheck error',e
                                        

    def updateFormatNoSave(self,fmtVal):
        """
        update the formating information but don't save it to the db.  this
        is useful if you have the formatting is not available immediately
        but only asynchronously (as in a web service)
        """
        if fmtVal and fmtVal != u'lit':
            fmt = self.getFormat()
            if not fmt:
                fmt = {}
            fmt[u'__sht'] = fmtVal
            self._setFormatNoSave(fmt)

    def numFormat(self):
        fmt = self.getFormat()
        if fmt:
            existing = fmt.get('__sht')
            if existing:
                return existing
        return None

    def clearNumFormat(self):
        fmt = self.getFormat()
        if fmt:
            if '__sht' in fmt:
                del fmt['__sht']
                self._setFormatNoSave(fmt)
            

    def toNum(self,val,locale):

        if not locale:
            return val,True # the raw value, and changed (so it is saved)

        ctx = ParseCtx()
        try:
            parsedval = LocaleParser.getInstance(str(locale)).parse(ctx,val)
            if isinstance(parsedval,LitNode):
                ret = parsedval.eval()
            elif type(parsedval) in (float,long,int):
                ret = parsedval
            elif type(parsedval) is str:
                ret = parsedval.encode('utf-8')
            else:
                ret = val
        except LiteralConversionException,e:
            self.clearNumFormat()
            return val,True
        except RuntimeError,e:
            print 'toNum: caught runtime error on ',val,e
            #import traceback,sys
            #traceback.print_tb(sys.exc_info()[2])
            #traceback.print_stack()                                    
            return val,True

        changed = False
        if ctx.fmt:
            existing = self.getFormat()
            if existing and ctx.fmt in ParseCtx.overridableFormats:
                # if there is *any* existing formatting and we got that the value
                # is simply a number, don't override the formatting (whether it be
                # time, date, currency, etc.
                changed = False
            else:
                fmt,changed = self._setFmtOnParse(None,unicode(ctx.fmt))
                if changed:
                    self._setFormatNoSave(fmt)
        return ret,changed or ret != self._val

    def getValue(self,stackValue=1):
        """returns evaluated formula.
        """
        if self._val is not None:
            return self._val

        if self._ast:

            ctx = context.get('ctx')
            
            try:
                if self._txnMgr is None:
                    self._txnMgr = FormulaTxnManager(self.cellHandle)
                else:
                    # cancel any pending transactions
                    self._txnMgr.cancelTransactions()
                ctx = {'cell':self,'cache':True}
                # the context stuf automatically handles nested contexts
                self._val = context.call({'ctx':ctx,'txnMgr':self._txnMgr},self._ast.eval,stackValue)
                self._txnMgr.calcOnFinish()
            except exc.SSCircularRefError,e:
                # if we get a circular ref error we keep popping of
                # the stack until we get back to a stack count of 1.
                # hackish I know but necessary to use psyco.
                if stackValue != 1:
                    raise e
                self._val = e
            except exc.SSError,e:
                self._val = e                
            except:
                self._val = exc.SSValueError()
                engine.Engine.getInstance().log.warning("Cell.getValue exception",sys.exc_info()[1])
                #import traceback
                #traceback.print_tb(sys.exc_info()[2])
                #traceback.print_stack()

            if ctx is not None and not ctx['cache']:
                # some function values should never be cached - rand is an example.
                # in that case we don't cache the value or any dependencies
                ret = self._val
                self._val = None
                return ret
            else:
                return self._val

        self._val = self.formula
        return self._val

    def _setFormula(self, formula,locale):
        """returns cell and range dependencies"""
        # force the formula to be in ascii
        if type(formula) is unicode:
            formula = formula.encode('utf-8')
        self.formula = formula

        # clear ourselves from the recalculation set
        self.cellHandle.sheetHandle().clearRecalc(self.cellHandle)

        if len(formula) < 1 or formula[0] != '=' or (formula[0] == '=' and len(formula) == 1):
            self._ast = None
            self._val,changed = self.toNum(formula,locale)
            return set([]), set([]),changed
            
        self._val = None
        try:
            # if an existing asynchronous function exists, scheduling any
            # future updates
            self.getTxnMgr().cancelFutureRun()
            
            # parse the formula into an AST but don't evaluate it yet
            self._ast = engine.Engine.getInstance().parser.parse(self.getSheetHandle(), formula[1:],
                                                                 locale.dectype)
            if not self.numFormat():
                # if an existing format does not exist see if one is part of the AST
                try:
                    formatting = self._ast.getImpliedFormatting(1)
                    if formatting and formatting != u'lit':
                        fmt,changed = self._setFmtOnParse(None,unicode(formatting))
                        if changed:
                            self._setFormatNoSave(fmt)
                except exc.SSCircularRefError,e:
                    pass
                except RuntimeError,e:
                    # this could possible happen when iterating over the cell handles
                    # and something changes the cellHandle dictionary.  log a bunch of stuff
                    # and continue on our way as the formatting is not absolutely critical.
                    print 'Failed to getFormatting, error',e
                    print 'Failed formula is ',self.formula,self._ast
            
        except:
            self._val = sys.exc_info()[1]
            import traceback
            traceback.print_tb(sys.exc_info()[2])            
            engine.Engine.getInstance().log.warning("Cell._setFormula exception", self._val)
            return set([]), set([]),True

        cellKids = set()
        rangeKids = set()
        
        for walkedNode in self._ast.walk():
            if isinstance(walkedNode,CellHandle):
                cellKids.add(walkedNode)
            if isinstance(walkedNode,HandRange):
                rangeKids.add((walkedNode.sheetHandle,walkedNode.cellRange))
            if isinstance(walkedNode,RecalcMixin):
                self.cellHandle.sheetHandle().addRecalc(self.cellHandle)

        return cellKids, rangeKids,True

    # for bulk loading... no notifications, updating, etc
    def setFormulaFromDb(self, formula,locale):
        cellKids, rangeKids,changed = self._setFormula(formula,locale)
        self.iDependOn = set(cellKids)
        self.rangesIDependOn = set(rangeKids)
        
    def setFormula(self, formula, locale,notify=True, notifyDict = None,persist=True,selfNotify=True):
        """set cell formula"""

        if type(formula) is unicode:
            formula = formula.encode('utf-8')
        
        if formula == self.formula:
            # short-circuit no-change
            return
        cellKids, rangeKids,changed = self._setFormula(formula,locale)
        if not changed:
            # this can happen if the string contained formatting values that
            # are already set and the underlying value hasn't changed
            return

        if persist:
            self._saveToDb()
        self.updateDeps(cellKids)
        self.updateRangeDeps(rangeKids)

        # notify dependent cells
        cellHandle = self.cellHandle
        sh = cellHandle.sheetHandle
        if notifyDict is None: notifyDict = {}

        if sh in notifyDict:
            cellSet = notifyDict[sh]
        else:
            notifyDict[sh] = cellSet = set()

        if selfNotify:
            cellSet.add(cellHandle)
        for dom in self.getDependsOnMe():
            dom().notify(notifyDict)

        if notify:
            for sheetHandle in notifyDict:
                sheetHandle.notify(notifyDict[sheetHandle])

        return notifyDict

    def _setFormatNoSave(self,format):
        self._dictfmt = format
        self.format = format and len(format) > 0 and cPickle.dumps(format) or u''

    def toFormatRep(cls,format):
        return format and len(format) > 0 and cPickle.dumps(format) or u''
    toFormatRep = classmethod(toFormatRep)

        
    def setFormat(self, format,notifyDict = None,persist=True):
        self._dictfmt = format
        self.format = format and len(format) > 0 and cPickle.dumps(format) or u''
        # FIXME: duplicated code from setFormula.  Why do we need notifcation
        # for formatting?  Because if we cut and paste a region we want the update
        # from the server.  When the user applies the style directly (instead of from paste)
        # we don't need notification because the style information has already been applied.
        if notifyDict is not None:
            cellHandle = self.cellHandle            
            sh = cellHandle.sheetHandle
            if sh in notifyDict:
                cellSet = notifyDict[sh]
            else:
                notifyDict[sh] = cellSet = set()
                
            if cellHandle not in cellSet:
                cellSet.add(cellHandle)
                #for dom in self.getDependsOnMe():
                #    dom().notify(notifyDict)

        if persist:
            self._saveToDb()

    defaultDecFmt = {u'__sht':ParseCtx.defaultDecimalFormat}
    def getData(self):
        """ returns a dictionary of the data for consumption by the UI. """
        h = self.cellHandle
        r = int(h.row)
        c = int(h.col)

        #try:
        #    fmt = self.getFormat()
        #except Exception, inst:
        #    print 'getFormat failed, %d%d, error %s, format value %s' % (h.getCol(),h.getRow(),inst,self.format)
        #    fmt = u''

        # inlined
        fmt = self._dictfmt is not None and self._dictfmt or (len(self.format) and cPickle.loads(self.format) or u'')

        #if self._ast:
        #    formula = unicode(''.join(['=',str(self._ast)]),'utf-8')
        #else:
        formula = unicode(self.formula,'utf-8')

        ret = {u'row': r,
               u'col': c,
               u'formula': formula,
               u'format': fmt,
               }
        if self._ast and self._ast.displayinfo is not None:
            ret[u'disp'] = self._ast.displayinfo
        
        val = self.getValue()
        if isinstance(val, ValueError):
            ret[u'error'] = unicode(str(val),'utf-8'),unicode(len(val.args) > 0 and val.args[0]
                                                      or 'unknown error','utf-8')
        else:
            # must be first because bool is an instance of int
            if isinstance(val,bool):
                val = val and 'TRUE' or 'FALSE'                
            if isinstance(val,(int,float,long)):
                customFmt = None
                if fmt:
                    customFmt = fmt.get('__sht')
                # only pick up style from col or row if not dependent on the cell.
                parentFmt = h.sheetHandle().propInRowOrCol(r,c,'__sht')
                if parentFmt:
                    customFmt = parentFmt
                elif customFmt is None:
                    customFmt = ParseCtx.defaultDecimalFormat
                    if not fmt:
                        ret[u'format'] = self.defaultDecFmt
                locale = h.sheetHandle().ownerPrincipal.locale
                val = locale.formatPerLocale(val,customFmt)
            ret[u'text'] = type(val) is str and unicode(val,'utf-8') or unicode(val)
        return ret

#
# NEVER keep a direct reference to a cell or sheet laying around.
# Instead keep a CellHandle or SheetHandle.  
#
# REPEAT: this is the only object that should maintain a reference to
# a cell
#
class CellHandle(object):
    """Handle for a Cell"""

    cellMatch = re.compile(r'(?:([A-Za-z0-9]+)\!)?((?:\$?)(?:[A-Ha-h][A-Za-z]|[Ii][A-Va-v]|[A-Za-z]))(\$?[1-9][0-9]*)')

    def getInstance(cls, sheetHandle, col, row):
        # print "getInstance"
        # import debug
        # debug.stack()
        return sheetHandle().getCellHandle(col, row)
    getInstance = classmethod(getInstance)

    # FIXME: handle sheets: booya!c4
    # Use single regexp to do it
    def parse(cls, sheetHandle, txt):
        """create new CellHandle from textual rep. eg: $c$1"""
        match = cls.cellMatch.match(txt)
        col = Col(match.group(2))
        row = Row(int(match.group(3)))
        return cls.getInstance(sheetHandle, col, row)
    parse = classmethod(parse)

    # FIXME: no longer makes sense...
    def parseFull(cls, txt):
        """create new CellHandle from textual rep. eg: booya!$c$1
        handles sheet names"""
        match = cls.cellMatch.match(txt)
        col = Col(match.group(2))
        row = Row(int(match.group(3)))
        return cls.getInstance(sheet.SheetHandle.getInstance(match.group(1)), col, row)
    parseFull = classmethod(parseFull)

    ## WARNING: never instantiate directly... use getInstance
    def __init__(self, sheetHandle, col, row):
        """
        sheetHandle: sheetHandle
        col: Col instance or string or int
        row: Row instance or string or int
        """
        self._obj = None
        self.sheetHandle = sheetHandle
        self.col = isinstance(col, Col) and col or Col(col) 
        self.row = isinstance(row, Row) and row or Row(row)

        # precompute key
        self.key = col << 16 | row
        self.sheetHandle().addCellHandle(self)

    # various helper methods so that cell handle works properly as a dictionary entry
    # NOTE: can't use this right now - it breaks a bunch of stuff!

##    def __hash__(self):
##        return self.key
##    def __cmp__(self,other):
##        return cmp(self.key,other.key)
##    def __eq__(self,other):
##        return self.key == other.key

    def __call__(self,loadFromDb=True):
        """shorthand to return my referred object"""
        if self._obj == None:
            self._obj = weakref.ref(Cell._getInstance(self,loadFromDb))
            return self._obj()
        cell = self._obj()
        if cell == None:
            self._obj = weakref.ref(Cell._getInstance(self,loadFromDb))
            return self._obj()
        return cell

    def __repr__(self):
        return "%s(%s, %s, %s)" % (self.__class__, repr(self.sheetHandle), repr(self.col), repr(self.row))

    def __str__(self):
        return "%s!%s%s" % (self.sheetHandle, self.col, self.row)

    def translate(self, dc, dr, absCol, absRow):
        return CellHandle.getInstance(self.sheetHandle,
                                      Col(absCol and int(self.col) or self.col + dc),
                                      Row(absRow and int(self.row) or self.row + dr))

    def mutate(self,targetR,numR,targetC,numC):
        """
        mutate a cellHandle by the number of rows and/or columns specified. note that
        numR and numC can be negative (a deletion case).
        """
        destr = self.row
        destc = self.col
        if targetR <> 0 and targetR <= self.row:
            destr += numR
        if targetC <> 0 and targetC <= self.col:
            destc += numC
        return CellHandle.getInstance(self.sheetHandle,destc,destr)
            


    def getLocalStr(self, sheetHandle):
        return "%s%s%s" % (str(sheetHandle) != str(self.sheetHandle) and "%s!" % self.sheetHandle or "", self.col, self.row)

    def getKey(self):
        """return an integer that may be used as a dict key for cells in sheet"""
        return self.key
    
    def getSheetHandle(self):
        return self.sheetHandle

    def getCol(self):
        return self.col

    def getRow(self):
        return self.row

    def getSHColRow(self):
        """convenience method for db queries. returns tuple (sheetHandle, col, row)"""
        return str(self.sheetHandle), int(self.col), int(self.row)

    def getCell(self):
        return self()

    def eval(self,stackvalue):
        return self().getValue(stackvalue)

class CellRange(handle.OneOfSeveral):

    def argsToKey(cls, ulCol, ulRow, lrCol, lrRow):
        """
        regarding keys: the original implementation used 16 bits shit
        between lrCol and lorRow.  However, this caused an obscure bug
        when lrRow = 65536.  In this case B:B and B:C would have the same key.
        the workaround for right now was to increase the space so conflicts won't happen.
        probably the better solution is to make the references 0 based instead of 1 based
        before calculating the key.
        """
        
        return ulCol << 42 | ulRow << 24 | lrCol << 18 | lrRow
    argsToKey = classmethod(argsToKey)

    def __init__(self, ulCol, ulRow, lrCol, lrRow):
        """
        ulCol: upper left Column
        ulRow: upper left Row
        lrCol: lower right Column
        lrRow: lower right Row
        """
        self._ulCol, self._ulRow = ulCol, ulRow
        self._lrCol, self._lrRow = lrCol, lrRow
        self._key = self._ulCol << 42 | self._ulRow << 24 | self._lrCol << 18 | self._lrRow

    def __repr__(self):
        return "%s(%s, %s, %s, %s)" % (self.__class__, repr(self._ulCol), repr(self._ulRow),
                                       repr(self._lrCol), repr(self._lrRow))

    def __str__(self):
        return "%s%s:%s%s" % (str(self._ulCol), self._ulRow, str(self._lrCol), self._lrRow)

    def get(self):
        """returns all props for db saving"""
        return int(self._ulCol), int(self._ulRow), int(self._lrCol), int(self._lrRow)

    def getKey(self):
        return self._key

    def inRange(self, cellHandle):
        """returns true if cellHandle is in this range"""
        col, row = cellHandle.col, cellHandle.row
        return col >= self._ulCol and \
               col <= self._lrCol and \
               row >= self._ulRow and \
               row <= self._lrRow

    def inRangeCR(self, col, row):
        """returns true if cellHandle is in this range"""
        return col >= self._ulCol and \
               col <= self._lrCol and \
               row >= self._ulRow and \
               row <= self._lrRow

    def getRangeType(self):
        """
        determines if the range is confined to one column, one row, or
        represents a rectangular region.

        0 = confined to single column
        1 = confined to single row
        2 = rectangle
        
        """
        if self._ulRow == self._lrRow:
            return 0
        elif self._ulCol == self._lrCol:
            return 1
        else:
            return 2

    def getCellHByColIndex(self,col,shtI):
        """
        looks up a cell by its column index.  if the index
        is out of bounds raise an error.

        if the cell does not exist return None
        """
        
        idx = self._ulCol + col
        if idx > self._lrCol:
            raise exc.SSRefError()
    
        if shtI.hasCell(idx,self._ulRow):
            return shtI.getCellHandle(idx,self._ulRow)
        return None


    def getCellHByRowIndex(self,row,shtI):
        """
        lookup a cell by its row index.  if the index
        is out of bounds raise an error.

        if the cell does not exist return None
        """
        idx = self._ulRow + row
        if idx > self._lrRow:
            raise exc.SSRefError()
        if shtI.hasCell(self._ulCol,idx):
            return shtI.getCellHandle(self._ulCol,idx)
        return None

    def getCellHByIndex(self,col,row,shtI):
        """
        get a cell handle by indexes into the row and column array
        """
        cidx = self._ulCol + col
        ridx = self._ulRow + row
        if not self.inRangeCR(cidx,ridx):
            raise exc.SSRefError()
        else:
            if shtI.hasCell(cidx,ridx):
                return shtI.getCellHandle(cidx,ridx)
            else:
                return None

    def oneDimensional(self):
        """
        return true if the range is confined to
        a single column or row
        """
        return self._ulCol == self._lrCol or self._ulRow == self._lrRow

    def getCellHOffset(self,cellH):
        """
        return the cell offset from the range.  this function assumes
        that the cell is in the range already
        """
        if self._ulCol == cellH.col:
            return cellH.row - self._ulRow
        else:
            return cellH.col - self._ulCol

    def getCellHandlesIter(self,sheetHandle,sparse=True):
        """
        returns an iterable for the cellHandles in the range.
        Don't use this for large data sets right now or if you don't know right
        range and are 'guessing'.  The reason being that this function
        supports not sparse iteration for use by sort operations
        where empty values matter.  The second algorithm supported in getCellHandles
        doesn't work for non sparse data.
        """
        
        c0, r0, c1, r1 = self._ulCol, self._ulRow, self._lrCol, self._lrRow
        sht = sheetHandle()
        cellHandles = sht._cellHandles
        engine.Engine.getInstance().log("CellRange.getCellHandlesIter", c0, r0, c1, r1)

        colRange, rowRange = Col.getRange(c0, c1), Row.getRange(r0, r1)
        for cr in colRange:
            for rr in rowRange:
                exists = sht.hasCell(cr,rr)
                if exists:
                    yield sht.getCellHandle(cr,rr)
                elif not sparse:
                    yield NullCell(cr,rr)
    def existingCellKeys(self,sheetHandle):
        c0, r0, c1, r1 = self._ulCol, self._ulRow, self._lrCol, self._lrRow
        colRange, rowRange = Col.getRange(c0, c1), Row.getRange(r0, r1)
        retdict = {}
        sht = sheetHandle()        
        for cr in colRange:
            for rr in rowRange:
                if sht.hasCell(cr, rr):
                    retdict[cr << 16 | rr] = True
        return retdict

    def getCellHandles(self, sheetHandle):
        """
        returns list of cellHandles in this range
        """
        computeCache = getattr(sheetHandle(),'computeCache',None)
        if computeCache:
            existing = computeCache.get(self._key)
            if existing:
                return existing

        c0, r0, c1, r1 = self._ulCol, self._ulRow, self._lrCol, self._lrRow
        cellCount = (c1 - c0 + 1) * (r1 - r0 + 1)
        sht = sheetHandle()
        cellHandles = sht._cellHandles

        # two algorithms 
        if cellCount <= len(cellHandles):
            # fewer cells in range than in this sheet.  this works
            # great if the range is smaller than the number of cells
            # in sheet

            # engine.Engine.getInstance().log("alg1")
            colRange, rowRange = Col.getRange(c0, c1), Row.getRange(r0, r1)
            retvalue = [sht.getCellHandle(cr, rr) for cr in colRange for rr in rowRange if sht.hasCell(cr, rr)]
        else:
            # if the range is large and sheet is sparse, it is
            # better interrogate all cells in sheet
            
            # engine.Engine.getInstance().log("alg2")
            retvalue = [ch for ch in sht.getCellHandleIter() \
                    if ch.col >= c0 and ch.col <= c1 \
                    and ch.row >= r0 and ch.row <= r1]

        if computeCache:
            computeCache[self._key] = retvalue
        return retvalue

    def getFullCellHandles(self,sheetHandle):
        c0, r0, c1, r1 = self._ulCol, self._ulRow, self._lrCol, self._lrRow
        cellCount = (c1 - c0 + 1) * (r1 - r0 + 1)
        sht = sheetHandle()
        cellHandles = sht._cellHandles
        colRange, rowRange = Col.getRange(c0, c1), Row.getRange(r0, r1)
        return [sht.getCellHandle(cr, rr) for cr in colRange for rr in rowRange]        


    def getSparseIter(self, sheetHandle):
        """
        returns list of cellHandles in this range
        """

        c0, r0, c1, r1 = self._ulCol, self._ulRow, self._lrCol, self._lrRow
        cellCount = (c1 - c0 + 1) * (r1 - r0 + 1)
        sht = sheetHandle()
        cellHandles = sht._cellHandles
        #engine.Engine.getInstance().log("CellRange.getCellHandles", cellCount, len(cellHandles), c0, r0, c1, r1)

        # two algorithms 
        if cellCount <= len(cellHandles):
            # fewer cells in range than in this sheet.  this works
            # great if the range is smaller than the number of cells
            # in sheet

            # engine.Engine.getInstance().log("alg1")
            colRange, rowRange = Col.getRange(c0, c1), Row.getRange(r0, r1)
            return (sht.getCellHandle(cr, rr) for cr in colRange for rr in rowRange if sht.hasCell(cr, rr))
        else:
            # if the range is large and sheet is sparse, it is
            # better interrogate all cells in sheet

            # engine.Engine.getInstance().log("alg2")
            return (ch for ch in sht.getCellHandleIter() \
                    if ch.col >= c0 and ch.col <= c1 \
                    and ch.row >= r0 and ch.row <= r1)


    def getNonEmptyCells(self,sheetHandle):
        """
        get a set of cells that are not empty
        meaning they have a formula OR a formatting
        """
        for cellH in self.getSparseIter(sheetHandle):
            cellI = cellH()
            if cellI.notempty():
                yield cellI

    def getFormulaOnlyCells(self,sheetHandle):
        """
        ignore cells that are empty or cells that only have formatting.
        """
        for cellH in self.getSparseIter(sheetHandle):
            cellI = cellH()
            if len(cellI.formula) != 0:
                yield cellH
        
    def getColumnRange(self,colIndex):
        """
        return a new CellRange for *one* column in the range.
        if the range is A1:B99 getColumnRange(a1:b99,0) would return
        a1:A99.
        
        """
        if colIndex < 0 or self._ulCol + colIndex > self._lrCol:
            raise SSRangeError("%d index outside of existing range" % colIndex)
        
        targetcol = Col(self._ulCol + colIndex)
        return CellRange.getInstance(targetcol,self._ulRow,targetcol,self._lrRow)

    def getRowRange(self,rowIndex):
        """
        return a new CellRange fro *one* row in the range.
        if the range is a1:z99 getRowRange(a1:z99,0) would return a1:z1
        """
        if rowIndex < 0 or self._ulRow + rowIndex > self._lrRow:
            raise SSRangeError("%d index outside of existing range" % rowIndex)

        targetrow = Row(self._ulRow + rowIndex)
        return CellRange.getInstance(self._ulCol,targetrow,self._lrCol,targetrow)


# util func for parser
class HandRange:
    def __init__(self, sheetHandle, cellRange):
        self.sheetHandle, self.cellRange = sheetHandle, cellRange

class NullCell:
    def __init__(self,col,row):
        self.row = row
        self.col = col
    def __cmp__(self,other):
        # not currently used by sheetcmp
        return cmp(self.row,other.row)
    def getKey(self):
        return self.col << 16 | self.row
    def eval(self,stackvalue):
        return None
    def __repr__(self):
        return 'NullCell: %s %s' % (self.col,self.row)


def main():
    eng = engine.Engine.getInstance()

    # sh = sheet.SheetHandle.getInstance("booya")
    # c3 = CellHandle.parse(sh, "$c$3")
    # print "c3", c3, type(c3.getSheetHandle())
    # print c3.getCell()

    # sh = sheet.SheetHandle.getInstance("booya")
    # h = CellHandle.parse(sh, "a10")
    # h = CellHandle.parseFull("booya!b1")
    # print h, h()

if __name__ == '__main__': main()
