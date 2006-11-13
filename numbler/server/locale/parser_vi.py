#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
## (C) Numbler LLC 2006
#
#
# This file is a *template* and not used directly - unless you are seeing
# this comment in a generated file.
#
################################################################################

from numbler.server import yacc
from numbler.server.exc import *
import datetime
from numbler.server.littools import *

tokens = [
    'COMMAINT',
    'INTEGER',
    'FRACTION',
    'CURRENCY',
    'PERCENT',    
    'PLUS',
    'SLASH',
    'EXP',
    'TIMESEP',
    'SHORTMONTH',
    'LONGMONTH',
    'DASH',
    'CLOCK',
]

t_DASH = r'-'
t_SLASH = r'/'
t_TIMESEP = r':'
t_PLUS = r'\+'
t_EXP = r'[eE][\+\-]{0,1}\d+'
t_INTEGER = r'\d+'
t_SPACE = r'[ ]+'

t_ignore = '\t'

def t_error(t):
    raise LiteralConversionException()    

precedence = (
    ('left', 'INTEGER'),
    ('left', 'SPACE'),
    ('right', 'NEGATION'),            # Unary minus operator
    ('right', 'POSITIVE')            # Unary plus operator
)


def p_all_expressions(p):
    ''' expression : datetime
                   | timedate
                   | time
                   | date
                   | number
                   | currency
                   | percentage
    '''
    p[0] = p[1]

def p_datetime(p):
    ''' datetime : date SPACE time'''
    p.parser.parsectx.fmt = 'dt'
    p[0] = DateTime(p[1],p[3])
    
def p_timedate(p):
    ''' timedate : time SPACE date'''
    p.parser.parsectx.fmt = 'dt'
    p[0] = DateTime(p[3],p[1])

def p_date(p):
    ''' date : formaldate
             | monthday
             | monthyear
             | monthyearint
    '''
    p[0] = p[1]


# monthday, monthyear serve a couple of purposes.  in general, the
# date form of month-year or day-month is not specified at all by
# the various localization databases.  the only thing we use from the
# locale is the datesep; otherwise we allow any combination of these
# date parameters

def p_monthday(p):
    ' monthday : month datesep INTEGER'
    dayval = int(p[3])
    monthval = p[1].lower()
    if monthval not in monthdict:
        raise LiteralConversionException()
    monthnum = monthdict[monthval]
    if dayval > 1000:
        p.parser.parsectx.fmt = 'vsmy'
        p[0] = DateNode(p.parser.parsectx,year=dayval,month=monthnum)
    else:
        p.parser.parsectx.fmt = 'vsmd'
        p[0] = DateNode(p.parser.parsectx,day=dayval,month=monthnum)       

    
def p_monthyear(p):
    ' monthyear : INTEGER datesep month'
    yearval = int(p[1])
    monthval = p[3].lower()
    if monthval not in monthdict:
        raise LiteralConversionException()
    monthnum = monthdict[monthval]
    if yearval < 1000:
        p.parser.parsectx.fmt = 'vsmd'
        p[0] = DateNode(p.parser.parsectx,month=monthnum,day=yearval)
    else:
        p.parser.parsectx.fmt = 'vsmy'
        p[0] = DateNode(p.parser.parsectx,month=monthnum,year=yearval)

def p_time(p):
    '''time : shorttime
            | medtime
            | longtime
            | medtimeclock
            | longtimeclock
    '''
    p[0] = p[1]


def p_medtime(p):
    ' medtime : INTEGER TIMESEP INTEGER '
    t = TimeNode(int(p[1]),int(p[3]))
    p.parser.parsectx.fmt = 'mt'
    p[0] = t

def p_longtime(p):
    ' longtime : medtime TIMESEP INTEGER '
    t = p[1]
    p[1].seconds = int(p[3])
    p[0] = t
    p.parser.parsectx.fmt = 'lt'

def p_short_time(p):
    'shorttime : INTEGER SPACE CLOCK'
    t = TimeNode(int(p[1]))
    t.setAMPM(p[3])
    p[0] = t
    p.parser.parsectx.fmt = 'mt'    

def p_number(p):
    ''' number : normalint
               | float
    '''
    p[0] = p[1]
    ctx = p.parser.parsectx
    if not ctx.fmt:
        ctx.fmt = 'dc'

def p_commaint(p):
    'commaint : COMMAINT'
    p[0] = p[1].replace(gseptype,'')

def p_normalint(p):
    ''' normalint : commaint
                  | INTEGER
                  | commaint EXP
                  | INTEGER EXP
    '''
    if len(p) == 3:
        p[0] = float(''.join([p[1],p[2]]))
        p.parser.parsectx.fmt = 'de'
    else:
        p[0] = int(p[1])

def p_floatdec(p):
    ''' floatdec : FRACTION
                 | FRACTION EXP
    '''
    if len(p) == 3:
        p.parser.parsectx.fmt = 'de'
    p[0] = ''.join([p[1],len(p) == 3 and p[2] or ''])
    if gdectype != '.':
        p[0] = p[0].replace(gdectype,'.')

def p_float(p):
    ''' float : floatdec
              | commaint floatdec
              | INTEGER floatdec              
    '''
    if len(p) == 3:
        converter = ''.join([p[1],p[2]])
    else:
        converter = p[1]
    # this check isn't against the localized value because it was
    # converted in p_floatdec
    if converter[-1] == '.':        
        if len(converter) == 1:
            raise LiteralConversionException()
        else:
            p[0] = float(converter[0:-1])
    else:
        p[0] = float(converter)

def p_percentage(p):
    ''' percentage : number PERCENT
                   | INTEGER PERCENT
                   | INTEGER SPACE PERCENT
                   | number SPACE PERCENT
    '''
    p.parser.parsectx.fmt = '%'
    p[0] = float(p[1]) / 100

def p_expr_negation(p):
    ''' expression : DASH expression %prec NEGATION
                   | DASH SPACE expression %prec NEGATION
    '''
    if len(p) == 3:
        p[0] = -p[2]
    else:
        p[0] = -p[3]    

def p_expr_positive(p):
    ''' expression : PLUS expression %prec POSITIVE
                   | PLUS SPACE expression %prec POSITIVE
    '''
    if len(p) == 3:
        p[0] = +p[2]
    else:
        p[0] = +p[3]

def p_month(p):
    ''' month : SHORTMONTH
              | LONGMONTH
    '''
    p[0] = p[1]


def p_error(p):
    raise LiteralConversionException()


def validate_month(val):
    if val.lower() not in monthdict:
        LiteralConversionException()

############################################################
##below is generated code
############################################################

monthdict = {'th\xc3\xa1ng t\xc6\xb0': 4, 'th\xc3\xa1ng s\xc3\xa1u': 6, 'th\xc3\xa1ng n\xc4\x83m': 5, 'thg 10': 10, 'th\xc3\xa1ng ba': 3, 'th\xc3\xa1ng m\xc6\xb0\xe1\xbb\x9di hai': 12, 'th\xc3\xa1ng m\xe1\xbb\x99t': 1, 'th\xc3\xa1ng m\xc6\xb0\xe1\xbb\x9di m\xe1\xbb\x99t': 11, 'th\xc3\xa1ng m\xc6\xb0\xe1\xbb\x9di': 10, 'th\xc3\xa1ng hai': 2, 'thg 6': 6, 'thg 7': 7, 'thg 4': 4, 'thg 5': 5, 'thg 2': 2, 'thg 3': 3, 'thg 1': 1, 'th\xc3\xa1ng t\xc3\xa1m': 8, 'th\xc3\xa1ng b\xe1\xba\xa3y': 7, 'thg 8': 8, 'thg 9': 9, 'th\xc3\xa1ng ch\xc3\xadn': 9, 'thg 11': 11, 'thg 12': 12}
t_SHORTMONTH = r'(?i)thg 1|thg 2|thg 3|thg 4|thg 5|thg 6|thg 7|thg 8|thg 9|thg 10|thg 11|thg 12'
t_LONGMONTH = r'(?i)tháng một|tháng hai|tháng ba|tháng tư|tháng năm|tháng sáu|tháng bảy|tháng tám|tháng chín|tháng mười|tháng mười một|tháng mười hai'
    
t_FRACTION = r'\,\d*'
gdectype = ','
t_CURRENCY = r'\¤'
t_PERCENT = r'\%'
gseptype = '.'
t_COMMAINT = r'\d{1,3}(\.\d{3})+(?!\d)'
t_CLOCK = r'(?i)am|pm|p|a|sa|ch'
def p_datesep(p):
    ''' datesep : SLASH
                | DASH
                | SPACE
                
    '''
    
    p[0] = p[1]

def p_monthyearint(p):
    ' monthyearint : INTEGER datesep INTEGER'
    val1 = int(p[1])
    val2 = int(p[3])
    daybeforemonth = True
    monthbeforeyear = True

    if daybeforemonth and val1 < 1000:
        p[0] = DateNode(p.parser.parsectx,month=val2,day=val1)
        p.parser.parsectx.fmt = 'vsmd'
    elif not monthbeforeyear and val1 > 1000:
        p[0] = DateNode(p.parser.parsectx,month=val2,year=val1)
        p.parser.parsectx.fmt = 'vsmy'        
    elif not daybeforemonth and val2 < 1000:
        p[0] = DateNode(p.parser.parsectx,month=val1,day=val2)
        p.parser.parsectx.fmt = 'vsmd'        
    elif monthbeforeyear and val2 > 1000:
        p[0] = DateNode(p.parser.parsectx,month=val1,year=val2)
        p.parser.parsectx.fmt = 'vsmy'                
    else:
        raise LiteralConversionException()        


def p_formaldate(p):
    ''' formaldate : shortdate
                   | longdate
    '''

    p[0] = p[1]

def p_shortdate(p):
    ' shortdate : INTEGER datesep INTEGER datesep INTEGER '
    monthasint = True
    month = p[3]
    day = int(p[1])
    year = int(p[5])

    if monthasint:
        monthint = int(month)
    else:
        monthint = monthdict[month]

    p[0] = DateNode(p.parser.parsectx,day,month=monthint,year=year)
    p.parser.parsectx.fmt = 'sd'
    

def p_longdate(p):
    ' longdate : CUSTOMLIT0 datesep INTEGER datesep CUSTOMLIT1 datesep INTEGER datesep CUSTOMLIT2 datesep INTEGER '
    monthasint = True
    day = int(p[3])
    month = p[7]
    year = int(p[11])

    if monthasint:
        monthint = int(month)
    else:
        monthint = monthdict[month.lower()]

    p[0] = DateNode(p.parser.parsectx,day,month=monthint,year=year)
    p.parser.parsectx.fmt = 'ld'

def p_medtimeclock(p):
    ' medtimeclock : medtime SPACE CLOCK '
    t = p[1]
    t.setAMPM(p[3])
    p[0] = t



def p_longtimeclock(p):
    ' longtimeclock : longtime SPACE CLOCK '
    t = p[1]
    t.setAMPM(p[3])
    p[0] = t


def p_currency(p):
    ''' currency : number CURRENCY
                 | number SPACE CURRENCY
    '''
    p.parser.parsectx.fmt = '$'
    p[0] = p[1]


tokens.append('CUSTOMLIT0')

t_CUSTOMLIT0 = r'Ngày'


tokens.append('CUSTOMLIT2')

t_CUSTOMLIT2 = r'năm'


tokens.append('CUSTOMLIT1')

t_CUSTOMLIT1 = r'tháng'

tokens.append('SPACE')
