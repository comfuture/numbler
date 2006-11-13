# (C) Numbler LLC 2006
# See LICENSE for details.

daysecs = 86400
import math
import time
import datetime
from decimal import *

timebase = datetime.datetime(1900,1,1)
lowbounds = datetime.datetime(1900,1,1)-datetime.timedelta(1)

def timeFormat(nLocale,rep):
    """
    convert a serial time format to the time format specified by the locale.

    this function only looks at the fraction portion of rep.  Rep is expected
    to be in floating point form.
    """
    fract = math.modf(rep)[0]
    sec = int(daysecs * fract)
    temptime = timebase + datetime.timedelta(0,sec)
    return temptime.strftime(nLocale.defTimeFormat())



def dateFormat(nLocale,rep):
    """
    convert a serial date to the date format specified by the locale.

    this function only looks at the integer portion of rep.  Rep is expected
    to be in floating point form.
    """
    intval = math.modf(rep)[1]
    # -1 for 1900 leap year bug
    tempdate = lowbounds + datetime.timedelta(intval-1)
    return tempdate.strftime(nLocale.defDateFormat())

def dateTimeFormat(nLocale,rep):
    """
    display a date and time using timeFormat and dateFormat
    """
    return ' '.join([dateFormat(nLocale,rep),timeFormat(nLocale,rep)])


def moneyfmt(nLocale,value):
    """Convert Decimal to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<.02>'

    """
    lconv = nLocale.localeconv
    places = lconv['int_frac_digits']
    
    q = Decimal((0, (1,), -places))    # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    assert exp == -places    
    result = []
    digits = map(str, digits)
    build, next = result.append, digits.pop

    # start building    
    if sign:
        if not lconv['n_cs_precedes']:
            build(lconv['currency_symbol'])
            if lconv['n_sep_by_space']:
                build(' ')
        if lconv['n_sign_posn'] == 0:
            build(lconv['negative_sign'])
    else:
        if not lconv['p_cs_precedes']:
            build(lconv['currency_symbol'])
            if lconv['p_sep_by_space']:
                build(' ')
        if lconv['p_sign_posn'] == 0:
            build(lconv['positive_sign'])
            
    for i in range(places):
        if digits:
            build(next())
        else:
            build('0')
    build(lconv['mon_decimal_point'])
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(lconv['mon_thousands_sep'])
    if sign:
        if lconv['n_cs_precedes']:
            if lconv['n_sep_by_space']:
                build(' ')
            build(lconv['currency_symbol'])
        if lconv['n_sign_posn']:
            build(lconv['negative_sign'])
    else:
        if lconv['p_cs_precedes']:
            if lconv['p_sep_by_space']:
                build(' ')
            build(lconv['currency_symbol'])
        if lconv['p_sign_posn']:
             build(lconv['positive_sign'])
    result.reverse()
    return ''.join(result)
