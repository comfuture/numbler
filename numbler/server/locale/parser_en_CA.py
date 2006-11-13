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

monthdict = {'sep': 9, 'apr': 4, 'december': 12, 'november': 11, 'feb': 2, 'aug': 8, 'jan': 1, 'september': 9, 'oct': 10, 'mar': 3, 'march': 3, 'august': 8, 'may': 5, 'june': 6, 'jun': 6, 'jul': 7, 'july': 7, 'february': 2, 'october': 10, 'nov': 11, 'january': 1, 'april': 4, 'dec': 12}
t_SHORTMONTH = r'(?i)jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec'
t_LONGMONTH = r'(?i)january|february|march|april|may|june|july|august|september|october|november|december'
    
t_FRACTION = r'\.\d*'
gdectype = '.'
t_CURRENCY = r'\$'
t_PERCENT = r'\%'
gseptype = ','
t_COMMAINT = r'\d{1,3}(,\d{3})+(?!\d)'
t_CLOCK = r'(?i)am|pm|p|a'
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
                   | meddate
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
    

def p_meddate(p):
    ' meddate : monthyear datesep INTEGER '
    dn = p[1]
    dn.setYear(int(p[3]))
    p[0] = dn
    p.parser.parsectx.fmt = 'md'


def p_longdate(p):
    ' longdate : month datesep INTEGER CUSTOMLIT0 datesep INTEGER '
    monthasint = False
    day = int(p[3])
    month = p[1]
    year = int(p[6])

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
    ''' currency : CURRENCY number
                 | CURRENCY SPACE number
    '''
    p.parser.parsectx.fmt = '$'
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = p[3]


tokens.append('CUSTOMLIT0')

t_CUSTOMLIT0 = r','

tokens.append('SPACE')
