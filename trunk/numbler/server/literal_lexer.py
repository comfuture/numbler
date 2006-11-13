# (C) Numbler LLC 2006
# See LICENSE for details.

#import lex,re

tokens = (
    'COMMAINT',
    'INTEGER',
    'FRACTION',
    'CURRENCY',
    'PERCENT',    
    'PLUS',
    'SLASH',
    'EXP',
    'COLON',
    'MONTH',
    'DASH',
    'CLOCK'
)

t_DASH = r'-'
t_SLASH = r'/'
t_COLON = r':'
#t_MONTH = r'(?i)jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec'
t_CLOCK = r'(?i)am|pm|p|a'
t_PLUS = r'\+'
t_CURRENCY = r'\$'
t_PERCENT = r'%'
t_COMMAINT = '\d{1,3}(,\d{3})+'
t_EXP = r'[eE][\+\-]{0,1}\d+'
t_FRACTION = r'\.\d*'
t_INTEGER = r'\d+(?!,)'

t_ignore = ' \t'

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.skip(1)
