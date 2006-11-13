# (C) Numbler Llc 2006
# See License For Details.

from astbase import Function,checkstack,RangeMixin,CellRef
from exc import *
from localedb import LocaleParser,ParseCtx
import littools,math
import numpy
from sslib.flatten import flatten,isiterable
from ifbase import IfBase
from nevow import tags as T
from twisted.python import context
from numblerInterfaces import RecalcMixin

# used by doc generator
__shortmoddesc__ = 'Statistical Functions'

class MIN(Function):
    """
    return the smallest number in a set of values.
    """

    funcargs = {'varargs':True,'args':[
        ('number1',True,'any numberic value or cell reference'),
        ('number2',False,'any number')
        ]}
    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)                        
        proclist = [x for x in flatten([y.eval(stackvalue) for y in self.args]) if type(x) in self.allowedTypes]
        if len(proclist):
            return min(proclist)
        return 0

class MAX(Function):
    """
    return the largest number in a set of values.
    """

    funcargs = {'varargs':True,'args':[
        ('number1',True,'any numeric value or cell reference'),
        ('number2',False,'any numeric value')
        ]}
    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)                        
        proclist = [x for x in flatten([y.eval(stackvalue) for y in self.args]) if type(x) in self.allowedTypes]
        if len(proclist):
            return max(proclist)
        return 0


class COUNT(Function):
    """
    Count the number of cells that contain numeric values.  Non numeric values are ignored.
    """

    funcargs = {'varargs':True,'args':[
        ('value1',True,'any numeric value or cell reference'),
        ('value2',False,'any numeric value or cell reference')        
        ]}
    
    IgnoreChildStyles = True
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)        
        return len([x for x in flatten([y.eval(stackvalue) for y in self.args]) if type(x) in self.allowedTypes])

class COUNTIF(IfBase):
    """
    Count the number of cells within range that match criteria.
    """

    funcargs = {'args':[
        ('range',True,'a range of cells over which to count'),
        ('criteria',True,'a value which can be used to compute a boolean match against all values in range.  Examples include ">34" (greater than 34), a5 (must match the value in a5), "<>0" (any value that is not zero), etc.')
        ]};
                

    
    IgnoreChildStyles = True
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)        
        if len(self.args) != 2:
            raise SSValueError("incorrect number of arguments")
        if not isinstance(self.args[0],(RangeMixin,CellRef)):
            raise SSValueError("Expected a range")

        count = 0

        # get the comparision values from the shared implementation
        compval,op = self.getCompareOps(stackvalue)
        #print 'compval is',compval,type(compval),op

        iterable = self.args[0].eval(stackvalue)
        if not isiterable(iterable):
            iterable = [iterable]
        
        for cellval in iterable:
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
                   count += 1

        return count




class COUNTA(Function):
    """
    Count the number of cells that are not empty.
    """

    funcargs = {'varargs':True,'args':[
        ('value1',True,'any value or cell reference'),
        ('value2',True,'any value or cell reference')
        ]}

    IgnoreChildStyles = True
    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)                
        return len([x for x in flatten([y.eval(stackvalue) for y in self.args]) if x is not None and x != ''])    
    

class statVarBase(Function):
    """
    base class for stat functions that take a variable number of arguments
    """

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        if len(self.args) == 0:
            raise BadArgumentsError()
        arguments = [x for x in flatten([x.eval(stackvalue) for x in self.args]) if type(x) in self.allowedTypes]
        if not len(arguments):
            raise SSZeroDivisionError()

        return self.runfunc(arguments)


class STDEV(statVarBase):
    """
    calculate the standard deviation for a sample population.
    """

    funcargs = {'varargs':True,'args':[
        ('number1',True,'a value in the population'),
        ('number2',False,'a value in the population'),        
        ]}
    
    def runfunc(self,arguments):
        return numpy.std(arguments)


def calcVarP(arguments):
    mean = numpy.mean(arguments)
    return numpy.square([(x - mean) for x in arguments]).sum() / len(arguments)

class STDEVP(statVarBase):
    """
    calculate the standard deviation assuming that the arguments represent the entire population.
    """

    funcargs = {'varargs':True,'args':[
        ('number1',True,'a value in the population'),
        ('number2',False,'a value in the population'),        
        ]}

    funcdetails = T.p['STDEVP is the same as the square root of the variance for the population, e.g. =SQRT(VARP(...))']


    #calculate the standard deviation for the entire population.  the difference
    #is that you divide by N instead of n -1.
    #
    #this is basically just the square root of the variance for the population,
    #or =SQRT(VARP(...))


    funcargs = {'varargs':True,'args':[
        ('number1',True,'a value in the population'),
        ('number2',False,'a value in the population'),        
        ]}

    
    def runfunc(self,arguments):
        return numpy.sqrt(calcVarP(arguments))

class VAR(statVarBase):
    """
    calculate the variance for a sample population.
    """

    funcargs = {'varargs':True,'args':[
        ('number1',True,'a sample of the population'),
        ('number2',False,'a sample of the population'),        
        ]}

    def runfunc(self,arguments):
        return numpy.var(arguments)

class VARP(statVarBase):
    """
    calculate the variance for the entire population.
    """
    funcargs = {'varargs':True,'args':[
        ('number1',True,'a member of the population'),
        ('number2',False,'a member of the population'),        
        ]}

    
    def runfunc(self,arguments):
        return calcVarP(arguments)

class RAND(Function,RecalcMixin):
    """
    Compute a random real number between 0 and 1.  A new random number is returned every time the sheet is loaded or recalculated.
    """

    funcargs = {'args':[]}
    funcdetails = T.p['RAND is implemented with triple redunancy to pass the diehard test in order to ensure true randomness.']

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        if len(self.args) != 0:
            raise BadArgumentsError()            

        # implement the randomness designed to pass the diehard test
        # (what excel does in modern versions)
        # see http://support.microsoft.com/default.aspx?scid=kb;en-us;828795&Product=xl2003

        # create an array of 3 items and sum them and take the fractional value.
        # we cast to a float because of type checking by other methods

        # never cache this value
        context.get('ctx')['cache'] = False
        return float(numpy.modf(numpy.random.rand(3).sum())[0])

class MEDIAN(Function):
    """
    return the median value (e.g the middle value) in a range of values.
    """

    funcargs = {'varargs':True,'args':[
        ('number1',True,'any number'),
        ('number2',False,'any number')
        ]}


    def func(self,*vals):
        if self.args == 0:
            raise WrongNumArgumentsError('MEDIAN')
        return float(numpy.median(vals))


class SMALL(Function):
    """
    return the K-th smallest value in a data set.
    """

    funcargs = {'args':[
        ('cell_range',True,'a range of cells to compute the smallest value'),
        ('k',True,'the position from the smallest to return.  K should be >0 and < number of values in cell_range')
        ]}

    def eval(self,stackvalue):
        stackvalue = stackvalue + 1
        checkstack(stackvalue)

        if len(self.args) != 2:
            raise WrongNumArgumentsError('SMALL')

        testrng = self.args[0].eval(stackvalue)
        if not isiterable(testrng):
            testrng = [testrng]
        
        # k is the index.  it must be > 0
        k = self.args[1].eval(stackvalue)

        # ensure a numeric chekc
        if type(k) not in self.allowedTypes:
            raise BadArgumentsError()
        if k <= 0 or k > len(testrng):
            raise SSNumError()
        
        testrng.sort()
        return testrng[k-1]


funclist = (STDEV,RAND,MEDIAN,SMALL,STDEVP,VAR,VARP,MAX,MIN,COUNT,COUNTA,COUNTIF)

