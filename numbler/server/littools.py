# (C) Numbler LLC 2006
# See LICENSE for details.

import datetime,math
from numbler.server.exc import *

#
# Serial date functions
#

lowbounds = datetime.datetime(1900,1,1)-datetime.timedelta(1)
maxserialdate = 2958465.999
daysecs = 86400

def dateDeltaToSerial(spectime):
    # return the number of days since Jan 1 1900.  why the plus 1
    # you ask?  well back in the days of lotus 123 they had a bug where
    # they consider 1900 a leap year.  According to the gregorian calendar
    # 1900 is NOT a leap year.  However, 123 included that in the calculations
    # so that all serial dates were off by 1.  Excel continued the bug
    # for compatability and so do we.
    days = (spectime - lowbounds).days
    if days <= 60:
        return days
    else:
        return days + 1

def serialDateToDay(serialDate):
    if serialDate < 60:
        return (lowbounds + datetime.timedelta(int(serialDate))).day
    elif serialDate == 60:
        # stupid leap year bug
        return 29
    else:
        return (lowbounds + datetime.timedelta(int(serialDate)-1)).day


def serialDateToHour(serialDate):
    fract = math.modf(serialDate)[0]
    return math.floor(fract * 24)

def serialDateToMinute(serialDate):
    fract = math.modf(serialDate)[0]
    return ((fract * 1440) % 60)

def serialDateToSec(serialDate):
    fract = math.modf(serialDate)[0]
    print 'serialDateToSec:',((fract * 86400) % 60)
    return ((fract * 86400) % 60)

def serialDateToMonth(serialDate):
    if serialDate < 60:
        return (lowbounds + datetime.timedelta(int(serialDate))).month
    elif serialDate == 60:
        # stupid leap year bug
        return 2
    else:
        return (lowbounds + datetime.timedelta(int(serialDate)-1)).month

def serialDateToYear(serialDate):
    if serialDate < 60:
        return (lowbounds + datetime.timedelta(int(serialDate))).year
    elif serialDate == 60:
        # stupid leap year bug
        return 1900
    else:
        return (lowbounds + datetime.timedelta(int(serialDate)-1)).year


def datetimeToSerialDate(dt):
    # if the datetime is not naive (i.e has a timezone) you can't used the cached value
    if dt.tzinfo:
        val = dt - (datetime.datetime(1900,1,1,tzinfo=dt.tzinfo)-datetime.timedelta(1))
    else:
        val = dt - lowbounds
    # see littols.py for explanation of the excel bug
    return float((val.days + 1)) + (val.seconds / 86400.)

def serialDateToWeekday(serialDate,rettype=1):
    if serialDate < 60:
        dt = (lowbounds + datetime.timedelta(int(serialDate)))
    elif serialDate == 60:
        # stupid leap year bug
        return rettype == 1 and 4 or ((rettype == 2) and 3 or 2)
    else:
        dt = (lowbounds + datetime.timedelta(int(serialDate)-1))

    if rettype == 1:
        val = dt.isoweekday()
        if val == 7:
            return 1
        else:
            return val + 1
        return dt.weekday() + 1
    elif rettype == 2:
        return dt.isoweekday()
    else:
        return dt.weekday()

def serialDateToISO(serialDate):
    fract,intval = math.modf(serialDate)
    sec = int(daysecs * fract)

    if intval == 60:
        #stupid leap year bug.  this isn't right
        # but I doubt anyone will notice.
        return '1900-02-29T00:00:00.000'
    if intval > 60:
        # dates greater than 2/29/1900 have -1 days
        intval -= 1
        
    dt = lowbounds + datetime.timedelta(intval,sec)
    return dt.isoformat()


class LitNode(object):
    pass

class DateNode(LitNode):



    def __init__(self,parsectx,day=1,month = None,monthstr = None,year = None):
        self.day = day
        self.month =month
        self.monthstr = monthstr
        self.year = year
        self.verifyArgs()

    def verifyArgs(self):
        if self.day < 1 or self.day > 31:
            raise LiteralConversionException()
        if self.month:
            if self.month < 1 or self.month > 12:
                raise LiteralConversionException()                
        if self.year:
            if self.year < 1900 or self.year > 9999:
                raise LiteralConversionException()
        
    def setDay(self,day):
        self.day = day
        self.verifyArgs()

    def setYear(self,year):
        self.year = year
        self.verifyArgs()

    def eval(self):
        if self.monthstr:
            # the month strings must be resolved from the locale
            self.month = parsectx.localedict['smonthdict'][self.monthstr.lower()]
        assert self.month is not None
        if self.year is None:
            self.year = datetime.datetime.utcnow().year

        self.verifyArgs()

        # verify that the data is valid.  if not raise an
        # error
        try:
            self.spectime = datetime.datetime(self.year,self.month,self.day)
        except ValueError,e:
            raise LiteralConversionException()

        return dateDeltaToSerial(self.spectime)

class TimeNode(LitNode):
    """
    Time class for dealing with time literals.  this class
    is instantiated by the parser.  It is responsible for throwing errors
    when some aspect of the data is incorrect (which is ok, is just means that
    we can convert to a time)
    """

    am = ['a','am']
    pm = ['p','pm']
    
    def __init__(self,hours,minutes = 0,seconds = 0):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    def setAMPM(self,val):
        if self.hours > 12:
            raise LiteralConversionException()
        checker = val.lower()
        if checker in self.pm and self.hours < 12:
            self.hours += 12
        elif checker in self.am and self.hours == 12:
            self.hours -= 12

    def eval(self):
        if self.hours > 23 or self.hours < 0:
            raise LiteralConversionException()            
        if self.minutes > 59 or self.minutes < 0:
            raise LiteralConversionException()                        
        if self.seconds > 59 or self.minutes < 0:
            raise LiteralConversionException()            

        return float(self.hours * 3600 + self.minutes * 60 + self.seconds) / 86400;


class DateTime(LitNode):
    def __init__(self,dateNode,timeNode):
        self.dateNode = dateNode
        self.timeNode = timeNode

    def eval(self):
        return self.dateNode.eval() + self.timeNode.eval()
