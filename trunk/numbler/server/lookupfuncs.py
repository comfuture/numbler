# (C) Numbler LLC 2006
# See LICENSE for details.

from astbase import Function,checkstack,CellRef,ensureNumeric,srcfloat
from astbase import srcint,RangeMixin,LookupRange,ensurePositiveNumeric
from exc import *
from sslib.flatten import flatten,isiterable
from twisted.python import context
from nevow import tags as T

# used by doc generator
__shortmoddesc__ = 'Lookup Functions'

def rowcmp(inst1,inst2):
    """
    compare two instances of a cell handle
    """
    return cmp(inst1.row,inst2.row)

def rowvaluecmp(inst1,inst2):
    """
    compare two cell values against each other
    """


class CacheMixin:
    def getCache(self,shtI,stackvalue):
        self.stackvalue = stackvalue
        try:
            self.instanceC = shtI.computeCache
            self.valueC = shtI.valueCache
        except:
            self.instanceC = {}
            self.valueC = {}

    def cacheLookup(self,cellH):
        # TODO: this code duplicates code in RangeMixin
        if not self.instanceC:
            compval = cellH().getValue(self.stackvalue)
        else:        
            compval = self.valueC.get(cellH.key)
            if not compval:
                cellI = self.instanceC.get(cellH.key)
                if not cellI:
                    cellI = cellH()
                    self.instanceC[cellH.key] = cellI
                compval = cellI.getValue(self.stackvalue)
                self.valueC[cellH.key] = compval
        return compval

    

class LookupBase(Function,CacheMixin):
    """
    base class for VLOOKUP, HLOOKUP

    """

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)        

        # step 1: argument processing
        
        arglen = len(self.args)
        if arglen < 3 or arglen > 4:
            raise WrongNumArgumentsError(self.__class__.__name__)

        if not isinstance(self.args[1],RangeMixin):
            raise SSNotAvailable()

        targetcol = self.args[2].eval(stackvalue)
        if arglen == 4:
            # we negate the value because from the user's perspective
            # FALSE means an exact match (excel compat). in this code
            # here we want exactmatch == True 
            exactmatch = not self.args[3].eval(stackvalue)
            if not isinstance(exactmatch,bool):
                raise BadArgumentsError()
        else:
            exactmatch = False

        testval = self.args[0].eval(stackvalue)

        # create a new cell range that is one dimension of the
        # the cell range.
        wholerng = self.args[1]
        # stuff the searchrng in a LookupRange to get the benefits
        # of caching in range mixin
        searchrng = self.getSearchRange(wholerng)
        shtH = wholerng.sheetHandle
        shtI = shtH()

        # sort by cell key
        searchlist = sorted(searchrng.getCellHandlesIter(shtH),cmp=rowcmp)

        # establish our value cache
        self.getCache(shtI,stackvalue)

        found = None
        largestH = None
        largestval = None

        #print 'testvalue is',testval,searchlist
        for cellH in searchlist:
            compval = self.cacheLookup(cellH)
            #print 'comparing against',compval,type(compval),testval,type(testval)
            if testval == compval:
                found = cellH
                break
            if not exactmatch:
                if testval > compval:
                    if largestval is None:
                        #print 'largest is now',compval                   
                        largestval = compval
                        largestH = cellH
                    else:
                        largestval = max(largestval,compval)
                        #print 'largest is now',largestval
                        if largestval == compval:
                            largestH = cellH
        if not found:
            if exactmatch or not largestH:
                raise SSNotAvailable()
            else:
                found = largestH

        # lookup in the target range for the exact match
        resultI = shtI.getCellHandle(*self.getMatchingCR(found,targetcol))()
        # test if the value does not exist: if not return 0
        if resultI.formula == '':
            return 0
        else:
            return resultI.getValue(stackvalue)


class VLOOKUP(LookupBase):
    """
    Search for search_value in the first column and return the value in the same row from another column based on column_index.
    """

    ##    do a vertical lookup from one column into another column
    ##    this fuction mimics the extensions of excel
    ##    the first argument is the lookup value.
    ##    the second argument is a cell range (array).  It must be
    ##    more than one dimension to be useful.
    ##    the implementation is not optimized for large data sets, the exact matching uses
    ##    an iteritive algorithm rather than using a data struture like hash-table or tree.


    funcargs = {'args':[
        ('search_value',True,'The value that you are looking for in search_range'),
        ('search_range',True,'A range of cells (e.g A5:B10, G22:AB100, A:C).  The first column in the range is the search column.'),
        ('column_index',True,'The offset from the start of the range that indicates the cell to return (based on the column).  1 is the search column, 2 is the next column to the right of the search column, etc.'),
        ('approx_match',False,'For Excel compatibility approx_match can be specified to indicate if VLOOKUP should perform an exact match or approximate match.  If TRUE or omitted the next largest value that is less than search_value is returned.  If FALSE only an exact match will be returned (otherwise an error occurs).')
        ]}

    funcdetails = T.p['An error will occur if column_index is outside the range of cells specified in search_range.  VLOOKUP does not support wildcard characters in search_value.']
    


    def getSearchRange(self,wholerng):
        return wholerng.getCellRange().getColumnRange(0)

    def getMatchingCR(self,foundCellH,target):
        return (foundCellH.col + (target-1),foundCellH.row)

class HLOOKUP(LookupBase):
    """
    Search for a value in the top row of search_range and return a value in the same column based on row_index.
    """

    funcargs = {'args':[
        ('search_value',True,'the value that you are looking for in search_range'),
        ('search_range',True,'A range of cells (e.g A5:B10, G22:AB100, A:C). The first row in the range is the search row'),
        ('row_index',True,'The offset from the start of the range that indicates the cell to return (based on the row).  1 is the search row, 2 is the next row below the search row, etc.'),
        ('approx_match',False,'For Excel compatibility approx_match can be specified to indicate if HLOOKUP should perform an exact match or approximate match.  If TRUE or omitted the next largest value that is less than search_value is returned.  If FALSE and exact match is returned (or an error is generated).')
        ]}

    funcdetails = T.p['An error will occur if row_index is outside the range of cells specified in search_range.  HLOOKUP does not support wildcard characters in search_value.']


    def getSearchRange(self,wholerng):
        return wholerng.getCellRange().getRowRange(0)

    def getMatchingCR(self,foundCellH,target):
        return (foundCellH.col,foundCellH.row + (target-1))

        
class MATCH(Function,CacheMixin):
    """
    Lookup the index of search_value in the range of cells specified by search_range.  Use Match when you need the position of the cell, not the cell value.
    """

    funcargs = {'args':[
        ('search_value',True,'the value to match in search_range'),
        ('search_range',True,'A range of cells that is one dimensional, (eg: a1:a10, 1:1, Q:Q, A10:Z10, etc)'),
        ('match_type',False,'For Excel compatibility match_type can be specified to determine how the match should be performed.  If match_type is 1 MATCH finds the largest value that is less than or equal to search_value.  If match_type is 0 MATCH finds the first value that is exactly equal to search_value.  If match type is -1 MATCH finds the smallest value that is greater than or equal to search_value.')
        ]}

    funcdetails = T.p['if match_type is 1 or -1 the cell range should be sorted.']
    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)

        arglen = len(self.args)
        if arglen not in (2,3):
            raise WrongNumArgumentsError('MATCH')

        lookupval = self.args[0].eval(stackvalue)
        if isinstance(lookupval,basestring):
            lookupval = lookupval.lower()
        
        lookuprng = self.args[1]
        if not isinstance(lookuprng,RangeMixin):
            raise BadArgumentsError()
        cr = lookuprng.getCellRange()
        # make sure the list is only one dimensional
        if not cr.oneDimensional():
            raise SSRefError()

        if arglen == 3:
            matchtype = self.args[2].eval(stackvalue)
        else:
            matchtype = 1

        shtH = lookuprng.sheetHandle
        shtI = shtH()
        searchlist = sorted(cr.getCellHandlesIter(shtH),cmp=rowcmp)
        
        self.getCache(shtI,stackvalue)

        largestval = None
        found = None
        smallestval = None
        for cellH in searchlist:
            compval = self.cacheLookup(cellH)
            if isinstance(compval,basestring):
                if not isinstance(lookupval,basestring):
                    # don't do string comparisions against non strings
                    continue
                compval = compval.lower()

            if matchtype == 0: # exact match
                if lookupval == compval:
                    found = cellH
                    break
            elif matchtype == 1: 
                # find the largest value that is <= lookupval
                if compval <= lookupval:
                    if largestval is None:
                        largestval = compval
                        found = cellH
                    else:
                        largestval = max(largestval,compval)
                        if largestval == compval:
                            found = cellH
            elif matchtype == -1:
                # find the smallest value that is >= the lookupval
                if compval >= lookupval:
                    if smallestval is None:
                        smallestval = compval
                        found = cellH
                    else:
                        smallestval = min(smallestval,compval)
                        if smallestval == compval:
                            found = cellH
        if not found:
            raise SSNotAvailable()
        else:
            # return the index of the cell position.. add +1
            # to go back into user space land
            return cr.getCellHOffset(found)+1

class INDEX(Function):
    """
    return the value from cell_range based on the specified arguments.
    """

    funcargs = {'args':[
        ('cell_range',True,'a range of cells (e.g D4:E9)'),
        ('row_index',False,'the row index'),
        ('col_index',False,'the column index')
        ]}

    funcdetails = T.p['If cell_range is one dimensional and only two arguments were supplied the second argument is assumed t be an index into the one dimensional range.  If cell_range is rectangular then both row_index and col_index must be supplied']

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)        

        arglen = len(self.args)
        if arglen not in (2,3):
            raise WrongNumArgumentsError('INDEX')

        arg1 = self.args[0]
        ref1, = ensurePositiveNumeric(self.args[1].eval(stackvalue))
        # adjust downwards by one (user thinks 1 = the first col or row)
        ref1 = max(ref1-1,0)
        if arglen > 2:
            ref2, = ensurePositiveNumeric(self.args[2].eval(stackvalue))
            # adjust downwards by one
            ref2 = max(ref2-1,0)
        else:
            ref2 = None

        
        if isinstance(arg1,CellRef):
            # kind of a silly case.  you have a single
            # cellref.  the possible values are 1 for the row ref
            # and 1 for the col ref
            if ref1 == 1:
                if ref2 is not None and ref2 != 1:
                    raise SSValueError("column reference out of range")
                return self.args[0].eval(stackvalue)
            else:
                raise SSValueEror("row reference out of range")
        elif isinstance(arg1,RangeMixin):
            cr = arg1.getCellRange()
            shtI = arg1.getSheetHandle()()

            if ref2 is None:
                # only looking for index into a single row or column.
                rtype = cr.getRangeType()
                if rtype == 0:
                    # get the column index
                    cellH = cr.getCellHByColIndex(ref1,shtI)
                elif rtype == 1:
                    cellH = cr.getCellHByRowIndex(ref1,shtI)
                else:
                    raise SSRefError()
            else:
                cellH = cr.getCellHByIndex(ref2,ref1,shtI)

            # ok, now we have a cellH.  if it is None return 0
            if not cellH:
                return 0
            else:
                return cellH().getValue(stackvalue)
        else:
            raise SSValueError("Expected a cell or range")


class ROW(Function):
    """
    return the row number of a cell reference or range reference.
    """

    funcargs = {'args':[
        ('reference',False,'a cell reference (e.g D4) or cell range reference (e.g D4:Q9).  If reference is not specified the current row is assumed.  If reference is a cell range the first row number is returned.')
        ]}
    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)        

        arglen = len(self.args)
        if arglen > 1:
            raise WrongNumArgumentsError('ROW')


        if arglen == 0:
            cellI = context.get('ctx')['cell']
            return int(cellI.cellHandle.row)
        else:
            check = self.args[0]
            if isinstance(check,CellRef):
                return int(check.cellHandle.row)
            elif isinstance(check,RangeMixin):
                return int(check.getCellRange()._ulRow)
            else:
                raise BadArgumentsError()
            
            
        

class COLUMN(Function):
    """
    return the column number of a cell reference or range reference.
    """

    funcargs = {'args':[
        ('reference',False,'a cell reference or cell range reference.  If reference is not specified the current column is assumed.  If reference is a cell range the first column is returned.')
        ]}
    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)        

        arglen = len(self.args)
        if arglen > 1:
            raise WrongNumArgumentsError('COLUMN')


        if arglen == 0:
            cellI = context.get('ctx')['cell']
            return int(cellI.cellHandle.col)
        else:
            check = self.args[0]
            if isinstance(check,CellRef):
                return int(check.cellHandle.col)
            elif isinstance(check,RangeMixin):
                return int(check.getCellRange()._ulCol)
            else:
                raise BadArgumentsError()


funclist = (VLOOKUP,ROW,COLUMN,INDEX,MATCH,HLOOKUP)

