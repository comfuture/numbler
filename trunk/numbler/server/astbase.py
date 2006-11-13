# (C) Numbler LLC 2006
# See LICENSE for details.

from sslib import log
from sslib.flatten import flatten
from exc import *
from colrow import Col, Row
from cell import CellHandle, CellRange, HandRange
import copy
from primitives import srcfloat,srcint,srclong

def checkstack(stackvalue):
    if stackvalue > 1000:
        print '**** CIRCULAR REFERENCE  ****** '
        #raise RuntimeError('circular reference')
        raise SSCircularRefError()

class Node(object):
    impliesFormatting = None
    __displayinfo = None

    def getImpliedFormatting(self,stackvalue):
        stackvalue = stackvalue + 1
        checkstack(stackvalue)
        
        if self.impliesFormatting:
            return self.impliesFormatting
        for x in self.astwalker(stackvalue):
            if not x:
                continue
            if isinstance(x,basestring):
                return x
            if x.impliesFormatting:
                return x.impliesFormatting
            child = x.getImpliedFormatting(stackvalue)
            if child:
                return child
        return None


    def setdisplayinfo(self,val): self.__displayinfo = val
    displayinfo = property(lambda self: self.__displayinfo,setdisplayinfo)

    def getAsyncNodes(self,stackvalue,checkSelf=False):
        """
        walk the AST looking for nodes that identify themselves
        as performing asynchronously.  This enables nodes
        higher up in the AST to defer their execution
        until the children have completed.
        """

        if checkSelf and getattr(self,'isAsync',False):
            yield self
        
        stackvalue = stackvalue + 1
        for x in self.astwalker(stackvalue):
            if not x or isinstance(x,basestring):
                continue
            if getattr(x,'isAsync',False):
                yield x
            for y in x.getAsyncNodes(stackvalue):
                yield y

    def translate(self,dc,dr):
        """
        must be implemented by the derived class to translate the formula
        on move.
        """
        assert not "not implemented"

    def mutate(self,targetRow,numRows,targetCol,numCols):
        """
        like translate except that the implementation does not pay attention
        to absolute references, i.e the formula is always translated.  This
        was originally implemented for the addcolumn, add row support.

        targetRow = beginning row.  In the case of positive numRows, this is the
        number of rows that will be added before targetRow.
        numRow = number of rows to add (positive) or number of rows to delete
        targetCol = beginning col.  In the case of positive numCols this is the nubmer
        of columns that will be added before targetCol
        numCols = number of columsn to add.
        """

# A CellRef isa Node.  It lives in an AST tree.  It holds a CellHandle.
class CellRef(Node):

    def __init__(self, cellHandle, absCol, absRow, explicit=False):
        """set explicit=True if sheetHandle is to be displayed"""
        self.cellHandle = cellHandle
        self.absCol, self.absRow = absCol, absRow
        self.explicit = explicit

    def getOriginCellH(self):
        return self.cellHandle
        
    def __deepcopy__(self, memo):
        return CellRef(self.cellHandle, self.absCol, self.absRow, self.explicit)

    def __repr__(self):
        return "%s(%s, absCol=%s, absRow=%s, explicit=%s)" % (self.__class__, repr(self.cellHandle),
                                                              self.absCol, self.absRow, self.explicit)
    def __str__(self):
        h = self.cellHandle
        return "%s%s%s%s%s" % (self.explicit and "%s!" % h.sheetHandle or "",
                               self.absCol and "$" or "", h.col,
                               self.absRow and "$" or "", h.row)
    def getR1C1(self, relCellH):
        """returns R1C1-style reference.  Relative references
        described relative to relCellH"""
        h = self.cellHandle
        return "%sR%sC%s" % (self.explicit and "%s!" % h.sheetHandle or "",
                             self.absRow and str(int(h.row)) or "[%d]" % (h.row - relCellH.row),
                             self.absCol and str(int(h.col)) or "[%d]" % int(h.col - relCellH.col))

    def translate(self, dc, dr):
        try:
            ret = CellRef(self.cellHandle.translate(dc, dr, self.absCol, self.absRow),
                          self.absCol, self.absRow, self.explicit)
        except:
            ret = SSRefError("bad translation %s to %d %d" % (str(self), dc, dr))
        return ret

    def mutate(self,targetRow,numRows,targetCol,numCols):
        try:
            ret = CellRef(self.cellHandle.mutate(targetRow,numRows,targetCol,numCols),
                    self.absCol,self.absRow,self.explicit)
        except SSRangeError:
            ret = SSRefError("sheet underflow")
        return ret

    def walk(self):
        yield self
        yield self.cellHandle

    def astwalker(self,stackvalue):
        """
        yield the type of the cell or 'lit' if none found 
        """
        fmt = self.cellHandle().numFormat()
        yield fmt is not None and fmt or u'lit'

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        try:
            cache = self.cellHandle.sheetHandle().valueCache
            ret = cache.get(self.cellHandle.key)
            if not ret:
                ret = self.cellHandle().getValue(stackvalue)
                cache[self.cellHandle.key] = ret
        except SSCircularRefError,e:
            #print 'caught circ ref error',e
            raise e
        except Exception,e:
            #print 'warning: cache miss',e
            ret = self.cellHandle().getValue(stackvalue)
        if isinstance(ret, SSError):
            #print 'raising error',ret
            raise ret
        return ret

    ##
    ## useful proxies
    ##
    def getSheetHandle(self): return self.cellHandle.getSheetHandle()
    def getCol(self): return self.cellHandle.col
    def getRow(self): return self.cellHandle.row


class RangeMixin:
    """
    Mixin class for common range functionality 
    """
    
    def walk(self):
        yield self
        yield HandRange(self.sheetHandle, self._cr)

    def getSheetHandle(self):
        return self.sheetHandle

    def eval(self,stackvalue,wantHandles=False):
        stackvalue = stackvalue +1
        checkstack(stackvalue)

        try:
            instancecache = self.sheetHandle().computeCache
            valuecache = self.sheetHandle().valueCache
        except:
            #print 'warning: cache miss'
            if not wantHandles:
                return [x.eval(stackvalue) for x in self._cr.getCellHandles(self.sheetHandle)]
            else:
                return [(x.eval(stackvalue),x) for x in self._cr.getCellHandles(self.sheetHandle)]                

        ret = []
        for cellH in self._cr.getCellHandles(self.sheetHandle):
            value = valuecache.get(cellH.key)
            if not value:
                cellI = instancecache.get(cellH.key)
                if not cellI:
                    cellI = cellH()
                    instancecache[cellH.key] = cellI

                value = cellI.getValue(stackvalue)
                valuecache[cellH.key] = value
            if not wantHandles:
                ret.append(value)
            else:
                ret.append((value,cellH))
        return ret

    def cellHandles(self):
        return self._cr.getCellHandles(self.sheetHandle)

    def formulaOnlyCells(self):
        return self._cr.getFormulaOnlyCells(self.sheetHandle)

    def getCellRange(self):
        return self._cr

    def fullcellIter(self,stackvalue):
        for cellH in self._cr.getCellHandlesIter(self.sheetHandle):
            yield (cellH().getValue(stackvalue),cellH)
    

    def astwalker(self,stackvalue):
        """
        walk the range looking for hints on the formatting.  This bails
        out on the *first* literal that is found
        
        """
        for x in self._cr.getSparseIter(self.sheetHandle):
            cellI = x()
            if cellI._ast:
                yield cellI._ast
            else:
                res = cellI.numFormat()
                if res:
                    yield res
                else:
                    yield u'lit'
                break

class LookupRange(RangeMixin):
    """
    wrapper class for pre-existing ranges
    """

    def __init__(self,cr,shtH):
        self._cr = cr
        self.sheetHandle = shtH

class Range(Node,RangeMixin):
    # 1d or 2d, eg: V1:V10 or V1:D2

    def __init__(self, cell0, cell1):
        self.cell0, self.cell1 = cell0, cell1
        self._cr = CellRange.getInstance(cell0.getCol(), cell0.getRow(),
                                         cell1.getCol(), cell1.getRow())
        self.sheetHandle = cell0.getSheetHandle()

    def __deepcopy__(self, memo):
        return Range(copy.deepcopy(self.cell0, memo),
                     copy.deepcopy(self.cell1, memo))

    def __repr__(self):
        return "%s(%s, %s, %s)" % (self.__class__, repr(self.sheetHandle), repr(self.cell0), repr(self.cell1))

    def __str__(self):
        return "%s:%s" % (self.cell0, self.cell1)

    def getR1C1(self, relCellH):
        return "%s:%s" % (self.cell0.getR1C1(relCellH), self.cell1.getR1C1(relCellH))

    def translate(self, dc, dr):
        c0, c1 = self.cell0.translate(dc, dr), self.cell1.translate(dc, dr)
        if isinstance(c0, Node) and isinstance(c1, Node):
            return Range(c0, c1)
        else:
            return SSRefError("bad translation %s to %d %d" % (str(self), dc, dr))

    def mutate(self,tR,nR,tC,nC):
        c0,c1 = None,None
        if tC <> 0:
            delta = tC + nC
            if nC < 0:
                if tC >= self.cell1.getCol() and delta < self.cell0.getCol():
                    return SSRefError()
                # case for deleting and shrinking in the middle or the end
                elif delta <= self.cell1.getCol() and delta >= self.cell0.getCol():
                    #c0 = CellHandle.getInstance(self.sheetHandle,self.cell0.getCol(),self.cell0.getRow())
                    c0 = self.cell0.cellHandle
                    if tC > self.cell1.getCol():
                        targetcol = delta
                    else:
                        targetcol = self.cell1.getCol() + nC
                    c1 = CellHandle.getInstance(self.sheetHandle,Col(targetcol),self.cell1.getRow())
                # case for deleting and shrinking at the beginning
                elif delta <= self.cell0.getCol() and delta >= 0 and tC <= self.cell1.getCol():
                    c0 = CellHandle.getInstance(self.sheetHandle,Col(max(self.cell0.getCol() + nC,delta+1)),
                                                self.cell0.getRow())
                    c1 = CellHandle.getInstance(self.sheetHandle,Col(self.cell1.getCol() + nC),self.cell1.getRow())
        if tR <> 0:
            delta = tR + nR
            if nR < 0:
                if tR >= self.cell1.getRow() and delta < self.cell0.getRow():
                    return SSRefError()
                elif delta <= self.cell1.getRow() and delta >= self.cell0.getRow():
                    #c0 = CellHandle.getInstance(self.sheetHandle,self.cell0.getCol(),self.cell0.getRow())
                    c0 = self.cell0.cellHandle
                    if tR > self.cell1.getRow():
                        targetrow = delta
                    else:
                        targetrow = self.cell1.getRow() + nR
                    c1 = CellHandle.getInstance(self.sheetHandle,self.cell1.getCol(),Row(targetrow))
                elif delta <= self.cell0.getRow() and delta >= 0 and tR <= self.cell1.getRow():
                    
                    c0 = CellHandle.getInstance(self.sheetHandle,self.cell0.getCol(),
                                                Row(max((self.cell0.getRow() + nR),delta+1)))
                    c1 = CellHandle.getInstance(self.sheetHandle,self.cell1.getCol(),Row(self.cell1.getRow() + nR))
        if c0 is not None and c1 is not None:
            c0 = CellRef(c0,self.cell0.absCol,self.cell0.absRow)
            c1 = CellRef(c1,self.cell1.absCol,self.cell1.absRow)
        else:
            c0 = self.cell0.mutate(tR,nR,tC,nC)
            c1 = self.cell1.mutate(tR,nR,tC,nC)
        if isinstance(c0,Node) and isinstance(c1,Node):
            return Range(c0,c1)
        else:
            return SSRefError("bad mutation %d %d %d %d" % (tR,nR,tC,nC))

    def getOriginCellH(self):
        return self.cell0

# ColumnRange has absolute/relative attributes
class ColumnRange(Node,RangeMixin):

    def __init__(self, sheetHandle, c0, c1, abs0, abs1):
        """
        sheetHandle: this sheet
        c0: column0
        c1: column1
        absC0: is c0 absolute?
        absC1: is c0 absolute?
        """
        if c0 > c1: raise RefError("first col must be <= second")
        self.sheetHandle = sheetHandle
        self.abs0, self.abs1 = abs0, abs1        
        self._cr = CellRange.getInstance(c0, Row(1), c1, Row.getMax())
        self.c0 = c0
        self.c1 = c1

    def getOriginCellH(self):
        return CellHandle.getInstance(self.sheetHandle,self.c0,Row(1))

    def __deepcopy__(self, memo):
        return self.__class__(self.sheetHandle, self._cr._ulCol, self._cr._lrCol, self.abs0, self.abs1)

    def __repr__(self):
        return "%s(%s, %s, %s, %s, %s)" % (self.__class__, repr(self.sheetHandle), repr(self._cr._ulCol), repr(self._cr._lrCol),
                                           self.abs0, self.abs1)

    def __str__(self):
        return "%s%s:%s%s" % (self.abs0 and "$" or "", self._cr._ulCol, self.abs1 and "$" or "", self._cr._lrCol)

    def getR1C1(self, relCellH):
        """returns R1C1-style reference.  Relative references
        described relative to relCellH"""
        return "C%s:C%s" % (self.abs0 and str(int(self._cr._ulCol)) or "[%d]" % int(self._cr._ulCol - relCellH.col),
                            self.abs1 and str(int(self._cr._lrCol)) or "[%d]" % int(self._cr._lrCol - relCellH.col))

    def translate(self, dc, dr):
        nr = copy.copy(self)
        cr = nr._cr
        try:
            nr._cr = CellRange.getInstance(Col(self.abs0 and int(cr._ulCol) or cr._ulCol + dc),
                                           cr._ulRow,
                                           Col(self.abs1 and int(cr._lrCol) or cr._lrCol + dc),
                                           cr._lrRow)
        except:
            nr = SSRefError("bad translation %s to %d %d" % (str(self), dc, dr))

        return nr

    def mutate(self,tR,nR,tC,nC):
        # we only care about column changes, not row changes.
        if tC <> 0:
            delta = tC + nC
            if nC < 0:
                # case for deleting an enclosed range
                if tC >= self.c1 and delta < self.c0:
                    return SSRefError()
                # case for shrinkage above the range
                elif delta > self.c1 and tC > self.c1:
                    return self
                # case for shrinkage below the range
                elif delta < self.c0 and tC < self.c0:
                    startcol = Col(self.c0 + nC)
                    endcol = Col(self.c1 + nC)
                # case for deleting and shrinking in the middle or end
                elif delta <= self.c1 and delta >= self.c0:
                    startcol = self.c0
                    endcol = max(self.c0,Col(tC + nC))
                # case for deleting and shrinking at the beginning
                elif delta <= self.c0 and delta >= 0 and tC <= self.c1:
                    startcol = Col(delta+1)
                    endcol = Col(self.c1 + nC)
                else:
                    return SSRefError()
            else:
                # case for expansion above the range
                if tC > self.c1:
                    return self
                # case for expansion below the range
                elif tC <= self.c0:
                    startcol = Col(self.c0 + nC)
                    endcol = Col(self.c1 + nC)
                # case for expansion in the middle of the range
                elif tC <= self.c1:
                    startcol = self.c0
                    endcol = Col(self.c1 + nC)
            # if we got this far compute a new cell range.
            nr = copy.copy(self)
            cr = nr._cr
            try:
                nr._cr = CellRange.getInstance(startcol,
                                               cr._ulRow,
                                               endcol,
                                               cr._lrRow)
            except SSRangeError:
                nr = SSRefError("bad mutation %d %d %d %d" % (tR,nR,tC,nC))
            return nr                
        return self


# RowRange has absolute/relative attributes
class RowRange(Node,RangeMixin):
    def __init__(self, sheetHandle, r0, r1, abs0, abs1):
        """
        sheetHandle: this sheet
        r0: row0
        r1: row1
        absC0: is c0 absolute?
        absC1: is c0 absolute?
        """
        if r0 > r1: raise RefError("first row must be <= second")
        self.sheetHandle = sheetHandle
        self.abs0, self.abs1 = abs0, abs1        
        self._cr = CellRange.getInstance(Col(1), r0, Col.getMax(), r1)
        self.r0 = r0
        self.r1 = r1

    def getOriginCellH(self):
        return CellHandle.getInstance(self.sheetHandle,Col(1),self.r0)

    def __deepcopy__(self, memo):
        return self.__class__(self.sheetHandle, self._cr._ulRow, self._cr._lrRow, self.abs0, self.abs1)

    def __repr__(self):
        return "%s(%s, %s, %s, %s, %s)" % (self.__class__, repr(self.sheetHandle), repr(self._cr._ulRow), repr(self._cr._lrRow),
                                           self.abs0, self.abs1)
    def __str__(self):
        return "%s%s:%s%s" % (self.abs0 and "$" or "", self._cr._ulRow, self.abs1 and "$" or "", self._cr._lrRow)

    def getR1C1(self, relCellH):
        """returns R1C1-style reference.  Relative references
        described relative to relCellH"""
        return "R%s:R%s" % (self.abs0 and str(self._cr._ulRow) or "[%d]" % int(self._cr._ulRow - relCellH.row),
                            self.abs1 and str(self._cr._lrRow) or "[%d]" % int(self._cr._lrRow - relCellH.row))

    def translate(self, dc, dr):
        nr = copy.copy(self)
        cr = nr._cr
        try:
            nr._cr = CellRange.getInstance(cr._ulCol,
                                           Row(self.abs0 and int(cr._ulRow) or cr._ulRow + dr),
                                           cr._lrCol,
                                           Row(self.abs1 and int(cr._lrRow) or cr._lrRow + dr))
        except:
            nr = SSRefError("bad translation %s to %d %d" % (str(self), dc, dr))
            
        return nr

    def mutate(self,tR,nR,tC,nC):
        if tR <> 0:
            delta = tR + nR
            if nR < 0:
                # case for deleting an enclosed range
                if tR >= self.r1 and delta < self.r0:
                    return SSRefError()
                # case for shrinkage above the range
                elif delta > self.r1 and tR > self.r1:
                    return self
                # case for shrinkage below the range
                elif delta < self.r0 and tR < self.r0:
                    startrow = Row(self.r0 + nR)
                    endrow = Row(self.r1 + nR)
                # case for deleting and shrinking in the middle or end
                elif delta <= self.r1 and delta >= self.r0:
                    startrow = self.r0
                    endrow = max(self.r0,Row(tR + nR))
                # case for deleting and shrinking at the beginning
                elif delta <= self.r0 and delta >= 0 and tR <= self.r1:
                    startrow = Row(delta+1) #Row((tR+1) - self.r0)
                    endrow = Row(self.r1 + nR)
                else:
                    return SSRefError()
            else:
                 # case for expansion above the range
                 if tR > self.r1:
                     return self
                 # case for expansion below the range
                 elif tR <= self.r0:
                     startrow = Row(self.r0 + nR)
                     endrow = Row(self.r1 + nR)
                 # case for expansion in the middle of the range.
                 elif tR <= self.r1:
                     startrow = self.r0
                     endrow = Row(self.r1 + nR)
            nr = copy.copy(self)
            cr = nr._cr
            try:
                nr._cr = CellRange.getInstance(cr._ulCol,
                                           startrow,
                                           cr._lrCol,
                                           endrow)
            except SSRangeError:
                nr = SSRefError("bad mutation %d %d %d %d" % (tR,nR,tC,nC))
            return nr
        return self

class Function(Node):
    allowedTypes = (int, float, long, bool,srcfloat,srcint,srclong)
    strTypes = (str,unicode)
    # set this to True if your function needs access to the locale of the sheet
    needsLocale = False
    # see the comment for ast walker
    IgnoreChildStyles = False
    # put the sheet handle on the Function object
    needsSheetHandle = False

    # override user doc to provide detailed documentation to the user.
    userdoc = ''

    def __init__(self, *args):
        self.args = args

    def __deepcopy__(self, memo):
        return self.__class__(*copy.deepcopy(self.args, memo))

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__.upper(), ','.join(map(str, self.args)))

    def getR1C1(self, relCellH):
        return "%s(%s)" % (self.__class__.__name__.upper(), ','.join([x.getR1C1(relCellH) for x in self.args]))

    def __repr__(self):
        return "%s(%s)" % (self.__class__, ','.join(map(repr, self.args)))


    def getFuncargs(self):
        """
        return the arguments for this function.  Arg information comes in the form
        of a dictionary.  Sample dictionary for SUM (note the varargs property)

        {
        'name':'SUM',
        'varargs':'True',
        'args':
        [
        ('number1',True,'a number to sum')
        ('number2',False)
        ]
        }

        sample dictionary for IRR

        {
        'args':[
        ('values',True,'cell range on which to compute the internal rate of return')
        ('guess',False,'a number is close to the expected value of IRR.  Do not specify this value unless IRR returns #NUM.')
        ]
        }

        the default implementation of hint will look for a 'hint' class variable on the object.  It will
        use the class name for the name of the function so most of the time you don't need to specify the
        name.
        
        """

        if not hasattr(self,'funcargs'):
            raise MissingFormulaHint(self.__class__.__name__)

        argdict = self.funcargs
        if 'name' not in argdict:
            argdict['name'] = self.__class__.__name__

        return argdict
        
    def docsummary(self):
        """
        return summary information about this function from the
        docstring.  if the docstring is missing this is considered an
        error condition.
        """
        if self.__doc__ is None:
            raise MissingDocString(self.__class__.__name__)
        
        if len(self.__doc__) == 0:
            raise MissingDocString(self.__class__.__name__)
        return self.__doc__

    def getFuncdetails(self):
        """
        return detailed information about this function. the default
        implementation (this one) simply returns the funcdetails class
        variable if it is present.  otherwise it returns a blank string.
        """
        if hasattr(self,'funcdetails'):
            return self.funcdetails
        return ''

    def getFuncExamples(self):
        """
        return a detailed example for the function.  the default
        implemention returns the funcexamples class variable if it
        is present.
        """
        if hasattr(self,'funcexamples'):
            return self.funcexamples
        return ''

    def translate(self, dc, dr):
        nArgs = []
        for arg in self.args:
            if isinstance(arg, Node):
                nArg = arg.translate(dc, dr)
            else:
                nArg = copy.copy(arg)
            nArgs.append(nArg)
        return self.__class__(*nArgs)

    def mutate(self, tR,nR,tC,nC):
        nArgs = []
        for arg in self.args:
            if isinstance(arg, Node):
                nArg = arg.mutate(tR,nR,tC,nC)
            else:
                nArg = copy.copy(arg)
            nArgs.append(nArg)
        return self.__class__(*nArgs)


    def walk(self):
        yield self
        for arg in self.args:
            if isinstance(arg, Node):
                for x in arg.walk():
                    yield x
            else:
                yield arg

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        
        # only run math functions on numeric types
        # passes evaluated args (called vals) to func
        # FIXME: flatten necessary??
        return self.func(*[x for x in flatten([x.eval(stackvalue) for x in self.args]) if type(x) in self.allowedTypes])

    def getImpliedFormatting(self,stackvalue):
        stackvalue = stackvalue + 1
        checkstack(stackvalue)
        
        if self.IgnoreChildStyles:
            return None
        else:
            return super(Function,self).getImpliedFormatting(stackvalue)

    def astwalker(self,stackvalue):
        """
        walk the ast looking for style information.  All functions
        are responsible for saying whether the set styling or ignore styling

        for instance, count() always returns an int. sum() passes through styling.

        the default for IgnoreChildStyles is False
        
        """
        if self.IgnoreChildStyles:
            yield None
        
        for arg in self.args:
            if isinstance(arg, Node):
                yield arg


def ensureNumeric(*args):
    ret = []
    for arg in args:
        if type(arg) is str:
            if arg is "":
                ret.append(0)
            else:
                # attempt to coerce to an integer value.
                raise SSValueError('value "%s" not numeric' % arg)
        else:
            ret.append(arg)
    return ret


def ensurePositiveNumeric(*args):
    ret = []
    for arg in args:
        if type(arg) is str:
            if arg is "":
                ret.append(0)
            else:
                # attempt to coerce to an integer value.
                raise SSValueError('value "%s" not numeric' % arg)
        else:
            if arg < 0:
                raise SSValueError('value must be positive')
            ret.append(arg)
    return ret
    


class mathFunction(Function):
    """
    base class for certain types of math functions.  This class
    provides basic error and stack checking.  The derived class
    must have a class variable indicating the number of arguments
    and a function call runfunc(). the derived class is responsible for
    processing arguments
    """


    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        if len(self.args) != self.expectedargs:
            raise WrongNumArgumentsError(self.__class__.__name__)         
        return self.runfunc(stackvalue)



