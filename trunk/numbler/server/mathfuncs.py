# (C) Numbler LLC 2006
# See LICENSE for details.

from astbase import Function,ensureNumeric,checkstack,ensurePositiveNumeric,mathFunction,CellRef,RangeMixin
from decimal import ROUND_HALF_UP,ROUND_DOWN,ROUND_UP,Decimal
from exc import *
import math
import numpy
from sslib.flatten import flatten
from localedb import ParseCtx
from nevow import tags as T
import statfuncs
from ifbase import IfBase


# used by doc generator
__shortmoddesc__ = 'Math Formulas'


class Trig(Function):
    """
    
    Base class for all trigometry related functions
    """
    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        if len(self.args) < 1 or len(self.args) > 1:
            raise SSValueError("Invalid number of arguments")
        return self.func(self.args[0].eval(stackvalue))


class RealTrig(Trig):
    funcdetails = T.p['for more information see ',
                      T.a(href="http://en.wikipedia.org/wiki/Trigonometric_function")['Trigonometric Functions']
                      ]

class SIN(RealTrig):
    """
    return the sine of the specified angle.
    """
    funcargs = {'args':[
        ('angle',True,'the angle in radians used to compute the sine')
        ]}


    #@return: the computed sine

    func = math.sin

class COS(RealTrig):
    """
    return the cosine of the specified angle.
    """
    funcargs = {'args':[
        ('angle',True,'the angle in radians used to compute the cosine')
        ]}

    
    func = math.cos

class TAN(RealTrig):
    """
    return the tangent of the specified angle.
    """
    funcargs = {'args':[
        ('angle',True,'the angle in radians used to compute the tangent')
        ]}
    
    func = math.tan
    
class ASIN(RealTrig):
    """
    return the arcsine (or inverse sine) of a number.
    """
    funcargs = {'args':[
        ('angle',True,'the arcsine of the angle you want in the range -1 to 1 (inclusive)')
        ]}
    
    func = math.asin

class ATAN(RealTrig):
    """
    return the arctangent (or inverse tangent) of a number.
    """
    funcargs = {'args':[
        ('number',True,'the tangent of the angle you want.')
        ]}

    func = math.atan

# atan2 doesn't currently work because the parser has a bug with functions that have numbers
class ATAN2(RealTrig):
    func = math.atan2

class COSH(RealTrig):
    """
    returns the hyperbolic cosine of a number.
    """
    funcargs = {'args':[
        ('number',True,'the number for which you want the hyperbolic cosine.')
        ]}
    func = math.cosh

class DEGREES(Trig):
    """
    convert a number in radians to degrees.
    """
    funcargs = {'args':[
        ('angle',True,'the angle in radians to convert')
        ]}
    
    func = math.degrees

class SINH(RealTrig):
    """
    compute the hyperbolic sine of a number.
    """

    funcargs = {'args':[
        ('number',True,'any real number')
        ]}

    
    func = math.sinh

class POWER(mathFunction):
    """
    raise number1 to the power of number2.  =POWER(5,2) is the same as =5^2
    """

    funcargs = {'args':[
        ('number1',True,'the base value'),
        ('number2',True,'the exponent to which to raise number1')
        ]}
    

    expectedargs = 2
    def runfunc(self,stackvalue):
        number,power = ensureNumeric(self.args[0].eval(stackvalue),self.args[1].eval(stackvalue))
        return number ** power

class INT(mathFunction):
    """
    converts a floating point or decimal value to an integer value.
    """

    funcargs = {'args':[
        ('number',True,'the real number you wish to convert to an integer')
        ]}

    funcdetails = T.div["WARNING: do not use INT to properly round a number, instead use one of the ROUND functions."]
    
    expectedargs = 1
    def runfunc(self,stackvalue):
        val, = ensureNumeric(self.args[0].eval(stackvalue))
        return int(val)

class LOG(Function):
    """
    returns the logarithm of number with base base_val.
    """

    funcargs = {'args':[
        ('number',True,'any positive number'),
        ('base_val',False,'the base of the logarithm.  If base_val is omitted the default is base 10')
        ]}

    def func(self,number,base=10):
        return math.log(number,base)

class EXP(mathFunction):
    """
    calculate e raised to the power of number.
    """

    funcargs = {'args':[
        ('number',True,'the exponent applied to the base e')
        ]}
    
    expectedargs = 1
    def runfunc(self,stackvalue):
        number, = ensureNumeric(self.args[0].eval(stackvalue))
        return math.exp(number)

class RoundBase(mathFunction):

    expectedargs = 2
    def runfunc(self,stackvalue):
        value,prec = ensureNumeric(self.args[0].eval(stackvalue),self.args[1].eval(stackvalue))

        if prec == 0:
            precstr = '0'
        elif prec > 0:
            precstr = '1e-%d' % prec
        elif prec < 0:
            precstr = '1e%d' % (-1*prec)
        return float(Decimal(str(value)).quantize(Decimal(precstr),rounding=self.rounding))

class ROUND(RoundBase):
    """
    round to the nearest value using the "half-up" convention.  Any number less than .5 at the specified precision is rounded down while values >= .5 are rounded up.
    """

    funcargs = {'args':[
        ('number',True,'the number you wish to round'),
        ('digits',True,'the number of digits left after rounding')
        ]}
    
    rounding = ROUND_HALF_UP


class ROUNDUP(RoundBase):
    """
    round up to the next largest value (away from 0)
    """
    funcargs = {'args':[
        ('number',True,'the number you wish to round'),
        ('digits',True,'the number of digits left after rounding')
        ]}
    
    rounding = ROUND_UP

class ROUNDDOWN(RoundBase):
    """
    round down the the next smallest value (towards 0).
    """
    funcargs = {'args':[
        ('number',True,'the number you wish to round'),
        ('digits',True,'the number of digits left after rounding')
        ]}
    rounding = ROUND_DOWN

class PRODUCT(Function):
    """
    multiply all the values together and return the product.
    """
    funcargs = {'varargs':True,'args':[
        ('number1',True,'numbers you want to multiply'),
        ('number2',False,'numbers you want to multiply')
        ]}
               
    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        if len(self.args) == 0:
            raise BadArgumentsError()        
        return numpy.product([x for x in flatten([y.eval(stackvalue) for y in self.args]) if type(x) in self.allowedTypes],
                             dtype=numpy.Float64)


class ABS(Trig):
    """
    compute the absolute value of a numbler.
    """

    funcargs = {'args':[
        ('number',True,'any real number')
        ]}
    
    func = abs

class SUM(Function):
    """
    add all the specified cells as individual values or ranges of cells.
    """

    funcargs = {'varargs':True,'args':[
        ('number1',True,'any numeric value'),
        ('number2',False,'any numeric value')
        ]}

    funcdetails = T.p['any non numeric values are ignored by SUM.']
    

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        # hmm.. blows up lots of memory
        return sum([x for x in flatten([y.eval(stackvalue) for y in self.args]) if type(x) in self.allowedTypes])

class SUMIF(IfBase):
    """
    Compute a SUM based specified by range based on criteria.
    """

    funcargs = {'args':[
        ('cell_range',True,'A range of cells to compute the SUM (e.g. A4:C12, B:D, etc)'),
        ('criteria',True,'A psuedo logical expression that indicates the criteria for evaluating whether a value from cell_range should be included.'),
        ('sum_range',False,'an optional cell range that is used to compute the sum based on an offset match with cell_range.  If sum_range is omitted the sum is performed from cell_range.')
        ]}

    funcdetails = T.p['SUMIF does not support wildcards in the criteria field. The criteria field must establish a boolean expression to indicate if the cell in cell_range meets the conditions.  Example criteria values are ">45" (any value greater than 45) and  "bananna" (any cell equal to "bananna").']
    
    #sum_range is not required.  if the sum_range is not present then the values from the range
    #are used.  sum_range isn't a really range since the only value it provides is the starting
    #cell location.  If the end location is less than the range dimensions then the sum range is
    #simply expanded.

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)        
        
        arglen = len(self.args)
        if arglen not in range(2,4):
            raise SSValueError("Incorrect number of arguments")

        # check that the first argument is a range
        if not isinstance(self.args[0],(RangeMixin,CellRef)):
            raise SSValueError("Expected a range or cell reference")

        if arglen == 3:
            if not isinstance(self.args[2],(RangeMixin,CellRef)):
                raise SSValueError("Expected a range or cell reference")
            else:
                # we only care about the beginning of the range so that
                # an offset calculation can be performed.
                sourceStart = self.args[0].getOriginCellH()
                sumRangeStart = self.args[2].getOriginCellH()
                sheetI = self.args[0].getSheetHandle()()
        else:
            sumRangeStart = None

        sumvalue = 0

        compval,op = self.getCompareOps(stackvalue)

        # lookup the value cache
        try:
            valuecache = sheetI.valueCache
        except:
            #print 'warning: SumIf value cache missing'
            valuecache = None

        # special case for when you have a sum range and a not equal
        # comparison.  in this case we iterate through the *sumrange*.
        # if a value exists and there is no cell in the actual range
        # then you have a match.  If there is a cell run the cell comparison.
        # and see if a match exists.
        #if op == '<>' and sumRangeStart and isinstance(self.args[0],RangeMixin):
        #    iterable = self.args[0].fullcellIter(stackvalue)
        #else:
        if isinstance(self.args[0],(RangeMixin)):
            iterable = self.args[0].eval(stackvalue,True)
        else:
            iterable = [(self.args[0].eval(stackvalue),self.args[0].cellHandle)]

        for cellval,cellH in iterable:
            if not cellval:
                continue

            if isinstance(cellval,basestring):
                if not isinstance(compval,basestring):
                    # if we aren't comparing against strings skip over them.
                    continue
                else:
                    # for string comparisions always do a case insensitive compare
                    cellval = cellval.lower()

            if (op == '=' and cellval == compval) or\
                   (op == '<=' and cellval <= compval) or\
                   (op == "<" and cellval < compval) or\
                   (op == ">" and cellval > compval) or\
                   (op == ">=" and cellval >= compval) or\
                   (op == "<>" and cellval != compval):
                if sumRangeStart:
                    # logic if we have a sum range.
                    diffC = cellH.getCol() - sourceStart.getCol()
                    diffR = cellH.getRow() - sourceStart.getRow()
                    tarC = sumRangeStart.getCol() + diffC
                    tarR = sumRangeStart.getRow() + diffR
                    if sheetI.hasCell(tarC,tarR):
                        targetcellH = sheetI.getCellHandle(tarC,tarR)
                        # use the valuecache if present
                        if valuecache is not None:
                            cellval = valuecache.get(targetcellH.key)
                            if not cellval:
                                cellval = targetcellH().getValue(stackvalue)
                                valuecache[targetcellH.key] = cellval
                        else:
                            cellval = targetcellH().getValue(stackvalue)

                        if type(cellval) in self.allowedTypes:
                            sumvalue += cellval
                elif type(cellval) in self.allowedTypes:
                    sumvalue += cellval
        return sumvalue




class AVG(Function):
    """
    Compute the average (mean) of the supplied numeric arguments.
    """

    funcargs = {'varargs':True,'args':[
        ('number1',True,'any number value'),
        ('number2',False,'any number value')
        ]}
    
    
    def func(self, *vals):
        if len(vals) == 0: return 0.0
        return sum(vals) / float(len(vals))

class AVERAGE(AVG):
    """
    Compute the average (mean) of the supplied numeric arguments.
    """    

class TRUNC(Trig):
    """
    Truncate a number to an integer by removing the fractional portion of the number.
    """

    funcargs = {'args':[
        ('number',True,'The number to truncate')
        ]}
    
    funcdetails = T.p['TRUNC does not support a precision argument (Excel does)']

    def func(self, x):
        if x >= 0:
            return math.floor(x)
        else:
            return math.ceil(x)

class PI(mathFunction):
    """
    returns the value of Pi, the ratio of a circle's circumference to its diameter.
    """
    funcargs = {'args':[]}
    
    expectedargs = 0
    def runfunc(self,stackvalue):
        return math.pi

class MOD(Function):
    """
    Returns the remainer of number divided by divisor.
    """

    funcargs = {'args':[
        ('number',True,'the number that you want to compute the remainder of after dividing by divisor'),
        ('divisor',True,'the value used to divide number')
        ]}
    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)                
        if len(self.args) != 2:
            raise SSValueError("mod takes a number and a divisor")
        number,divisor = ensureNumeric(self.args[0].eval(stackvalue),self.args[1].eval(stackvalue))
        try:
            return number % divisor
        except ZeroDivisionError:
            raise SSZeroDivisionError("Attempt to divide by zero: %d %% %d " % (number,divisor))

class SQRT(Function):
    """
    Compute the square root of number.
    """

    funcargs = {'args':[
        ('number',True,'number to compute the square root.  Negative numbers will return #NUM!')
        ]}
    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)                        
        if len(self.args) != 1:
            raise SSValueError("Square root requires one number")
        number, = ensureNumeric(self.args[0].eval(stackvalue))
        if number < 0:
            raise SSNumError("value must be greater than 0")
        return math.sqrt(number)

    
class SUBTOTAL(Function):
    """
    evaluate a function over a series of cell ranges.
    """

    funcargs = {'varargs':True,'args':[
        ('function_id',True,'the number of the function you wish to use'),
        ('ref1',True,'the first cell reference'),
        ('ref2',False,'the second cell reference')
        ]}
    
    funcdetails = T.p['SUBTOTAL does not avoid double counting so be sure not include overlapping or duplicate cell ranges.  This function is supported mostly for excel compatibility.']    

    lookupDict = {
        1: AVERAGE,
        2: statfuncs.COUNT,
        3: statfuncs.COUNTA,
        4: statfuncs.MAX,
        5: statfuncs.MIN,
        6: PRODUCT,
        7: statfuncs.STDEV,
        8: statfuncs.STDEVP,
        9: SUM,
        10: statfuncs.VAR,
        11: statfuncs.VARP,
        101: AVERAGE,
        102: statfuncs.COUNT,
        103: statfuncs.COUNTA,
        104: statfuncs.MAX,
        105: statfuncs.MIN,
        106: PRODUCT,
        107: statfuncs.STDEV,
        108: statfuncs.STDEVP,
        109: SUM,
        110: statfuncs.VAR,
        111: statfuncs.VARP        
        }
    
    def eval(self,stackvalue):

        arglen = len(self.args)
        if arglen < 2:
            raise WrongNumArgumentsError('SUBTOTAL')            

        funcIndex = self.args[0].eval(stackvalue)
        if funcIndex not in self.lookupDict:
            raise SSValueError("first argument not a valid function number")

        # ensure that all the other arguments are refs
        validrefs = (CellRef,RangeMixin)
        
        for ref in (isinstance(x,validrefs) for x in self.args[1:]):
            if not ref:
                raise SSValueError("arguments must a reference")

        runFuncI = self.lookupDict[funcIndex]()
        #runFuncI.args = [x for x in flatten([y.eval(stackvalue) for y in self.args[1:]])]
        runFuncI.args = self.args[1:]
        return runFuncI.eval(stackvalue)
        
        




funclist = (ROUND,ROUNDUP,ROUNDDOWN,POWER,INT,LOG,EXP,SIN,COS,TAN,ASIN,ATAN,COSH,DEGREES,SINH,
             PRODUCT,ABS,SUM,AVG,AVERAGE,TRUNC,PI,MOD,SQRT,SUBTOTAL,SUMIF)
