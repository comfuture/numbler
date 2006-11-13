# (C) Numbler LLC 2006
# See LICENSE for details.

from astbase import Function,ensureNumeric,checkstack,ensurePositiveNumeric,mathFunction,RangeMixin
from decimal import ROUND_HALF_UP,ROUND_DOWN,ROUND_UP,Decimal
from exc import *
import math
import numpy
from sslib.flatten import flatten
from localedb import ParseCtx
from nevow import tags as T
from itertools import izip

# used by doc generator
__shortmoddesc__ = 'Financial Functions'

## financial math functions

def pow1p(x, y):
    # FIXME: see comment below
    return pow(1 + x, y)

# Calculate ((1+x)^r)-1 accurately.
def pow1pm1(x, y):
    # Depending on python pow impl... could be bad.
    # FIXME determine whether to lift more code from gnumeric
    return pow(1 + x, y) - 1


def calculate_pvif(rate, nper):
    return pow1p(rate, nper)

def calculate_fvifa(rate, nper):
    # Removable singularity at rate == 0.  */
    if rate == 0:
        return nper
    else:
        return pow1pm1(rate, nper) / rate

def calculate_interest_part(pv, pmt, rate, per):
    return -(pv * pow1p(rate, per) * rate + pmt * pow1pm1(rate, per))

def calculate_pmt(rate, nper, pv, fv, type):

    # Calculate the PVIF and FVIFA
    pvif = calculate_pvif(rate, nper)
    fvifa = calculate_fvifa(rate, nper)

    return ((-pv * pvif - fv ) / ((1.0 + rate * type) * fvifa))

class PMT(Function):
    """PMT returns the amount of payment for a loan based on a constant
    interest rate and constant payments (each payment is equal amount).
    """

    funcargs = {'args':[
        ('rate',True,'the constant interest rate'),
        ('nper',True,'the overall number of payments'),
        ('pv',True,'the present value of future payments worth now, also known as the principal'),
        ('fv',False,'the future value.  The default value is 0'),
        ('type',False,'must be 0 or omitted (payment at the end of the period)')
        ]}

    #@rate is the constant interest rate.
    #@nper is the overall number of payments.
    #@pv is the present value.
    #@fv is the future value.
    #@type is the type of the payment: 0 means at the end of the period
    #and 1 means at the beginning of the period.

    #If @fv is omitted, Gnumeric assumes it to be zero.
    #If @type is omitted, Gnumeric assumes it to be zero."""

    impliesFormatting = ParseCtx.currencyFormat

    def func(self, rate, nper, pv, fv = 0, tp = 0):
        return calculate_pmt(float(rate), float(nper), float(pv), fv, tp)



class DDB(Function):
    """
    returns the depreciation of an asset using the standard double declining balance method.
    """

    funcargs = {'args':[
        ('cost',True,'the initial cost'),
        ('salvage',True,'the end of life value of the asset (can be 0)'),
        ('life',True,'the number of periods over which you are depreciating the asset.'),
        ('period',True,'the target period which you want to calculate the depreciation.  Period must be the same units as life, e.g if life is 10 and period is 1 DDB will calculate the depreciation in the first year of the asset.'),
        ('factor',False,'The factor at which to depreciate the asset.  The default value is 2 (for double declining)')
        ]}

    impliesFormatting = ParseCtx.currencyFormat
    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        arglen = len(self.args)
        if arglen not in (4,5):
            raise BadArgumentsError()                

        try:
            vals = ensurePositiveNumeric(*[x.eval(stackvalue) for x in self.args])
        except SSValueError:
            raise SSNumError()
        
        if arglen == 5:
            cost,salvage,life,period,factor = [float(x) for x in vals]
        else:
            cost,salvage,life,period = [float(x) for x in vals]
            factor = 2

        if period > life:
            raise SSNumError()

        # Double Declining balance works by calculating the
        # depreciation for the current period and then using that
        # in subsequent calculations.

        value = cost
        cum_depr = 0
        for cperiod in xrange(0,period):
            depr = value * (factor / life)
            cum_depr += depr
            value -= depr
            if cost - cum_depr < salvage:
                delta = ((cost-cum_depr) -salvage)
                depr += delta
                cum_depr += delta
                # no reason to continue
                if depr < 0:
                    break

        # if the depreciation dips below 0 we return 0 (excel compat)
        ret = max(depr,0)
        return ret


class SLN(mathFunction):
    """
    compute the straight line depreciation of an asset for one period.
    """

    funcargs = {'args':[
        ('cost',True,'the initial cost of the asset'),
        ('salvage',True,'the end of life value of the asset'),
        ('life',True,'the number of periods over which the asset is depreciated.  If life is 10 SLN computes the yearly depreciation over 10 years.')
        ]}
    
    impliesFormatting = ParseCtx.currencyFormat
    expectedargs = 3

    def runfunc(self,stackvalue):
        cost,salvage,life = ensureNumeric(*[float(x.eval(stackvalue)) for x in self.args])
        return ((cost-salvage)/life)


class IRR(Function):
    """
    Compute the internal rate of return using an interative process.  IRR works
    by trying to solve for an NPV (net present value) of 0.
    """

    funcargs = {'args':[
        ('values',True,'a cell reference or cell range containing a set of cash flows'),
        ('guess',False,'a starting value that is close to the final IRR.  guess is only necessary if IRR returns #NUM! or if your sample size is small.')
        ]}

    funcdetails = T.p['For more information see ',
                      T.a(href="http://en.wikipedia.org/wiki/Internal_rate_of_return")['internal rate of return']
                      ]
   

    impliesFormatting = ParseCtx.percentFormat
    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        if len(self.args) not in (1,2):
            raise BadArgumentsError()

        # the first arg should be a cell array reference
        if not isinstance(self.args[0],RangeMixin):
            raise BadArgumentsError()
    
        #arguments = [x for x in flatten([x.eval(stackvalue) for x in self.args]) if type(x) in self.allowedTypes]
        arguments = [x for x in self.args[0].eval(stackvalue) if type(x) in self.allowedTypes]
        if len(self.args) == 2:
            guess, = ensureNumeric(self.args[1].eval(stackvalue))
        else:
            guess = 0.2

        ACCURACY = 1.0e-5
        MAX_ITERATIONS = 50
        x1 = 0.0
        x2 = guess

        f1 = calcNPV(arguments, x1)
        f2 = calcNPV(arguments, x2)

        for x in xrange(MAX_ITERATIONS):
            if ((f1 * f2) < 0.0): break
            if (abs(f1) < abs(f2)):
                x1 = x1 + (1.6 * (x1-x2))
                f1 = calcNPV(arguments, x1)
            else:
                x2 = x2 + (1.6 * (x2-x1))
                f2 = calcNPV(arguments, x2)

        if ((f2 * f1) > 0.0):
            raise SSNumError()

        f = calcNPV(arguments, x1)
        dx = 0
        if ( f < 0.0 ):
            rtb = x1
            dx = x2 - x1
        else:
            rtb = x2
            dx = x1 - x2
        for x in xrange(MAX_ITERATIONS):
            dx = dx * 0.5
            x_mid = rtb + dx
            f_mid = calcNPV(arguments, x_mid)
            if ( f_mid <= 0.0 ): rtb = x_mid
            if ( (abs(f_mid) < ACCURACY) or (abs(dx) < ACCURACY) ):
                #print '** IRR returning',x_mid
                return x_mid

        raise SSNumError()

        



def calcNPV(arguments,rate):
        iters = len(arguments)
        return numpy.sum([x / numpy.power((1 + rate),y) for x,y in izip(arguments,range(1,iters+1))])


class NPV(Function):
    """
    calculate the net present value for an investment.
    """

    funcargs = {'varargs':True,'args':[
        ('rate',True,'the value of discount over the length of one period'),
        ('value1',True,'the first cashflow'),
        ('value2',False,'the second cashflow')
        ]}


    impliesFormatting = ParseCtx.currencyFormat

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        if len(self.args) < 2:
            raise BadArgumentsError()
        
        rate = self.args[0].eval(stackvalue)
        arguments = [x for x in flatten([x.eval(stackvalue) for x in self.args[1:]]) if type(x) in self.allowedTypes]

        #print 'about to calc NPV with rate',rate

        return calcNPV(arguments,rate)
        


class PV(Function):
    """
    compute the present value of a stream of future payments
    """
    pass


funclist = (DDB,SLN,PMT,IRR,NPV)
