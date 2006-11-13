# (C) Numbler Llc 2006
# See License For Details.

from datetime import datetime,timedelta
from astbase import Function,checkstack
from exc import *
from localedb import LocaleParser,ParseCtx
import littools,math
import numpy
from sslib.flatten import flatten,isiterable
from nevow import tags as T
from twisted.python import context
from numblerInterfaces import RecalcMixin

# used by doc generator
__shortmoddesc__ = 'Date and Time Functions'

class NOW(Function,RecalcMixin):
    """
    returns the current serial date and time.  By default the result will display as a date-time.
    """

    funcdetails = T.p['the formatted result is dependent on your language settings. NOW is calculated every time the sheet is recalculated, meaning that whenever a new value is entered or the sheet is reloaded the value of NOW will change.']

    funcargs = {'args':[]}

    needsLocale = True
    impliesFormatting = ParseCtx.dateTimeFormat
    def func(self):
        # never cache the value of NOW, it is always 
        context.get('ctx')['cache'] = False
        if len(self.args) != 0:
            raise SSValueError("NOW takes no arguments")
        return littools.datetimeToSerialDate(datetime.now(self.locale.tz))

class TODAY(Function,RecalcMixin):
    """
    returns the current serial date.  By default the result will display as a date.
    """

    funcargs = {'args':[]}
    funcdetails = T.p['the formatted result is dependent on your language settings.  The value of TODAY is refreshed whenever the sheet is recalculated.']    
    
    needsLocale = True
    impliesFormatting = ParseCtx.mediumDateFormat

    def eval(self,stackvalue):
        context.get('ctx')['cache'] = False        
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        if len(self.args) != 0:
            raise SSValueError("TODAY takes no arguments")
        return littools.datetimeToSerialDate(datetime.now(self.locale.tz))


class DATE(Function):
    """
    return a serial date from the arguments.  By default the result will display as a date.
    """
    #
    # this currently has a bug for DATE(1900,3,1)
    #
    
    funcdetails = T.p['For compatibility with other spreadsheet programs DATE supports positive and negative values in month and day.']

    funcargs = {'args':[
        ('year',True,'year component of a date expressed as an number'),
        ('month',True,'month component of a date expressed as a number'),
        ('day',True,'day component of a date expressed as a number')
        ]}

    impliesFormatting = ParseCtx.mediumDateFormat
    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        if len(self.args) != 3:
            raise SSValueError("DATE takes a year, month, and day")

        year,month,day = self.args
        try:
            year,month,day = int(year.eval(stackvalue)),int(month.eval(stackvalue)),int(day.eval(stackvalue))
        except ValueError:
            raise BadArgumentsError()

        if month != 12:
            if month == 0:
                realmonth = 12
                year -= 1
            else:
                yearoverflow,realmonth = divmod(month,12)
                year += yearoverflow
                if realmonth == 0:
                    year -= 1
                    realmonth = 12
        else:
            realmonth = month

        if year < 0 or year >= 10000:
            raise SSOutOfRangeError()
        # excel does this
        if year >= 0 and year <= 1899:
            year = 1900 + year

        try:
            serialval = littools.dateDeltaToSerial(datetime(year,realmonth,1) + timedelta(day-1))
        except OverflowError:
            raise SSOutOfRangeError
        if serialval < 1:
            raise SSOutOfRangeError()
        return serialval


class ValueBase(Function):
    needsLocale = True

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)        
        if len(self.args) != 1:
            raise SSValueError("%s takes one argument" % self.converter.im_class.__name__)

        parseval = self.args[0].eval(stackvalue)
        if type(parseval) is not str:
            raise SSValueError("wrong data type")

        ctx = ParseCtx()
        try:
            res = LocaleParser.getInstance(str(self.locale)).parse(ctx,parseval)
            if not ctx.isDateLike():
                # this could happen if someone enters a timevalue or a currency
                raise SSValueError("bad input")

            # only return the integer portion (chop off the fractional piece if
            # it was a datetime
            return self.converter(res.eval(),stackvalue)
        except LiteralConversionException:
            raise SSValueError()
    


class DATEVALUE(ValueBase):
    """
    convert date_text (e.g the date string) to a serial date format.  This is useful when you want to do date arithmetic or convert another cell value to a date.
    """

    funcargs = {'args':[
        ('date_text',True,'a text value that represents a date. The value must conform to the standards for your language.')
        ]}
    
    def converter(self,val,stackvalue):
            # only return the integer portion (chop off the fractional piece if
            # it was a datetime
            return int(val)

class TIMEVALUE(ValueBase):
    """
    returns the fractional portion of the date-time value represented by time_text.  The value must conform to the standards for your language.
    """

    funcargs = {'args':[
        ('time_text',True,'a text value that represents a time value, a date value, or a date-time value.')
        ]}
    
    
    def converter(self,val,stackvalue):
        # return only the fractional component
        return math.modf(val)[0]

class SerialFuncs(Function):
    """
    base class for simple classes which extra data
    from a serial date such as DAY, MONTH, YEAR
    """
    needsLocale = True
    maxargs = 1
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        if len(self.args) > self.maxargs:
            raise WrongNumArgumentsError(self.converter.im_class.__name__)
        serialdate = self.args[0].eval(stackvalue)        
        if type(serialdate) is str:
            # need to parse the date type
            try:
                ctx = ParseCtx()
                res = LocaleParser.getInstance(str(self.locale)).parse(ctx,serialdate)
                if isinstance(res,littools.LitNode):
                    serialdate = res.eval()
                else:
                    serialdate = res
            except LiteralConversionException:
                raise SSValueError()
        if type(serialdate) not in self.allowedTypes:
            raise SSValueError("bad value")
        if serialdate < 0 or serialdate > littools.maxserialdate:
            raise SSOutOfRangeError()
        return self.converter(serialdate,stackvalue)


class HOUR(SerialFuncs):
    """
    returns the hour from time_value expressed in a 24 hour clock.
    """

    funcargs = {'args':[
        ('time_value',True,'a time value expressed either as a text value (e.g "10:30 p") or in a serial number format.')
        ]}
    
    def converter(self,serialdate,stackvalue):
        return int(littools.serialDateToHour(serialdate))

class DAY(SerialFuncs):
    """
    return the day from date_value expressed as the numeric day in the month (e.g 15 for "May-15-2006")
    """

    funcargs = {'args':[
        ('date_value',True,'a date value expressed as a text value or a serial date number.')
        ]}

    def converter(self,serialdate,stackvalue):
        if serialdate == 0:
            return 0
        return littools.serialDateToDay(serialdate)
        
class MONTH(SerialFuncs):
    """
    return the month from date_value expressed as the numeric month in the year (e.g. 1 = January, 12 = December)
    """

    funcargs = {'args':[
        ('date_value',True,'a date value expressed either as a text date or a serial date number')
        ]}
    
    def converter(self,montharg,stackvalue):
        return littools.serialDateToMonth(montharg)
        
class YEAR(SerialFuncs):
    """
    return the year from date_value.
    """

    funcargs = {'args':[
        ('date_value',True,'a date value expressed either as a text date or a serial date number')
        ]}

    funcdetails = T.p['For Excel compatibility the range of valid years is 1900-9999.']
    
    def converter(self,yeararg,stackvalue):
        return littools.serialDateToYear(yeararg)

class SECOND(SerialFuncs):
    """
    return the second from time_value as a number in the range from zero to 59.
    """

    funcargs = {'args':[
        ('time_value',True,'a time value expressed as a text date-time, text time, or a serial time number')
        ]}
        
    
    def converter(self,secondarg,stackvalue):
        return int(littools.serialDateToSec(secondarg))
        
class MINUTE(SerialFuncs):
    """
    return the minute from time_value as a number in the range from zero to 59.
    """
    funcargs = {'args':[
        ('time_value',True,'a time value expressed as a text date-time, text time, or a serial time number')
        ]}
    
    def converter(self,minutearg,stackvalue):
        return int(littools.serialDateToMinute(minutearg))

class WEEKDAY(SerialFuncs):
    """
    return the day of the week from date_value.  By default Sunday=1 and is considered first day of the week.
    """

    funcargs = {'args':[
        ('date_value',True,'a date value expressed as a text date or a serial date value'),
        ('week_type',False,'Indicates how the day of the week is computed.  The default value is 1.')
        ]}

    funcdetails = T.div[T.p['for Excel compatibility week_type supports 3 different variations:'],
                        T.table[T.tr[T.td['1'],T.td['Sunday = 1 and Saturady = 7.']],
                                T.tr[T.td['2'],T.td['Monday = 1 and Sunday = 7.']],
                                T.tr[T.td['3'],T.td['Monday = 0 and Sunday = 6.']]
                                ]
                        ]
                                     
            
      
    

    maxargs = 2
    def converter(self,serialarg,stackvalue):
        weektype = 1
        if len(self.args) == 2:
            try:
                weektype = int(self.args[1].eval(stackvalue))
                if weektype not in (1,2,3):
                    raise BadArgumentsError()
            except ValueError:
                raise BadArgumentsError()                
        return littools.serialDateToWeekday(serialarg,weektype)


class TIME(Function):
    """
    returns the fractional value for the specified time.  By default the value is formatted as a time.
    """

    funcargs = {'args':[
        ('hour',True,'hour component of time value ranging from 0 to 32767.'),
        ('minute',True,'minute component of time_value ranging from 0 to 32767.'),
        ('second',True,'second component of time_value ranging from 0 to 32767.')
        ]
        }

    funcdetails = T.p['If any of the arguments to TIME overflow (e.g 99 hours, 75 minutes, etc) the date will automatically role over (99 hours = 4 days  + 3 hours)']


    impliesFormatting = ParseCtx.mediumTimeFormat
    maxinput = 2 ** 15

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        if len(self.args) != 3:
            raise SSSValueError("TIME requres an hour, minute, and second")
        hour,min,sec = self.args
        try:
            hour,min,sec = int(hour.eval(stackvalue)),int(min.eval(stackvalue)),int(sec.eval(stackvalue))
        except ValueError:
            raise BadArgumentsError()

        if hour < 0 or hour > self.maxinput or \
           min < 0 or min > self.maxinput or \
           sec < 0 or sec > self.maxinput:
            raise SSOutOfRangeError()

        result = datetime(1900,1,1) + timedelta(hours=hour,minutes=min,seconds=sec)
        serialval = littools.datetimeToSerialDate(result)
        return math.modf(serialval)[0]
        


funclist = (NOW,DATE,DATEVALUE,DAY,HOUR,MONTH,SECOND,TIME,TIMEVALUE,TODAY,YEAR,WEEKDAY,MINUTE)


