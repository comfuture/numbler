# (C) Numbler LLC 2006
# See LICENSE for details.

from astbase import Function,checkstack,CellRef,ensureNumeric,srcfloat,srcint,srclong,RangeMixin
from exc import *
from sslib.flatten import flatten,isiterable
from textfuncs import INDIRECT

# used by doc generator
__shortmoddesc__ = 'Information Functions'

class isBase(Function):
    """
    base class for text functions
    """

    funcargs = {'args':[
        ('value',True,'The value you want tested.')
        ]}

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        if len(self.args) != 1:
            raise WrongNumArgumentsError(self.__class__.__name__)         
        return self.runfunc(stackvalue)

class ISBLANK(isBase):
    """
    returns TRUE if value refers to an empty cell.
    """

    def runfunc(self,stackvalue):

        # if a cellref see if the cell exists.
        arg = self.args[0]
        if isinstance(arg,CellRef):
            if arg.cellHandle().formula == '':
                return True
        return False


class ISERROR(isBase):
    """
    returns TRUE if value is an error (either directly or via a cell reference)
    """
    
    def runfunc(self,stackvalue):

        isError = False
        try:
            self.args[0].eval(stackvalue)
        except SSError,e:    # for anything else
            isError = True
        return isError

class ISERR(ISERROR):
    """
    Same as ISERROR.  This is slightly different from Excel where ISERR will not return TRUE if value is #N/A.
    """
    
    pass

class ISLOGICAL(isBase):
    """
    returns TRUE if value is either TRUE or FALSE.  1 and 0 are not considered TRUE and FALSE (respectively) in ISLOGICAL.
    """
    
    def runfunc(self,stackvalue):
        try:
            val = self.args[0].eval(stackvalue)
        except:
            return False
        return isinstance(val,bool)
        
class ISNONTEXT(isBase):
    """
    returns TRUE if value is not a text value.  A blank cell is considered a non text value.
    """
    
    def runfunc(self,stackvalue):
        try:
            val = self.args[0].eval(stackvalue)
        except:
            # exceptions are not text values!
            return True
        if val == '':
            # special case for excel compatibility
            return True
        return not isinstance(val,basestring)
    

class ISNUMBER(isBase):
    """
    returns TRUE if value is a number.
    """

    # note: for compatibility we don't include booleans
    numberTypes = (int, float, long,srcfloat,srcint,srclong)
    
    def runfunc(self,stackvalue):
        try:
            val = self.args[0].eval(stackvalue)
        except:
            # excepts are not numbers!
            return False
        return isinstance(val,self.numberTypes)

class ISREF(isBase):
    """
    returns TRUE if value refers to a cell or range of cells.
    """
    
    def runfunc(self,stackvalue):
        # special case for the indirect function. indirect
        # creates an evaluates a cell reference from
        # a text string.  because our eval method expects the
        # final result after every nested eval INDIRECT can't return
        # the referenced cell but the cells' value.  This won't work
        # for ISREF so we need eval it manually and catch any errors. 
        if isinstance(self.args[0],INDIRECT):
            try:
                self.args[0].eval(stackvalue)
                # if we get here we were able to deference the cell
                return True
            except:
                return False
        else:
            return isinstance(self.args[0],(CellRef,RangeMixin))

class ISTEXT(isBase):
    """
    returns TRUE if value is a text value.
    """
    
    def runfunc(self,stackvalue):
        try:
            val = self.args[0].eval(stackvalue)
        except:
            # excepts are not text values
            return False
        return isinstance(val,basestring)

class ISEVEN(isBase):
    """
    returns TRUE if value is divisible by 2.
    """
    def runfunc(self,stackvalue):
        val, = ensureNumeric(self.args[0].eval(stackvalue))
        return int(val) % 2 == 0

class ISODD(isBase):
    """
    returns TRUE if value is not divisible by 2.
    """
    def runfunc(self,stackvalue):
        val, = ensureNumeric(self.args[0].eval(stackvalue))
        return int(val) % 2 != 0    
    
                             

funclist = (ISBLANK,ISERROR,ISERR,ISLOGICAL,ISNONTEXT,ISNUMBER,ISREF,ISTEXT,ISEVEN,ISODD)
