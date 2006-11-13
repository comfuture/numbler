# (C) Numbler LLC 2006
# See LICENSE for details.

##
## formula lexer parser
##

"""
this is the lexer module for Numbler.

because of the lexer design unit tests can't be run in each function so the
doctests are are all listed in the module docstring.  suxors.

float support:
The following formats are supported.
[sign] [integer value ] [ fracitonal value] [exponent] [percentange]

a couple of examples:
1.4
-1.2
1.3e+5%
1e+9
18e-8
etc

>>> l = getLexer()
>>> l.input('1.3')
>>> l.token().value
1.3
>>> l.input('.3')
>>> str(l.token().value)
'0.3'
>>> l.input('1.3e+5')
>>> l.token().value
130000.0
>>> l.input('1.3e+5%')
>>> l.token().value
1300.0
>>> l.input('1e-5%')
>>> str(l.token().value)
'1e-07'
>>> l.input('.005e5')
>>> l.token().value
500.0
>>> l.input('5e-000005')
>>> str(l.token().value)
'5e-05'
>>> l.input('5e+000005')
>>> l.token().value
500000.0
>>> l.input('2e5')
>>> l.token().value
200000.0
"""


import lex, re

from primitives import *
from ast import funcs

## next: add relative references

# List of token names.   This is always required
tokens = (
   'FLOAT',
   'INTEGER',
   'TRUE',
   'FALSE',   
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'EXP',
   'LPAREN',
   'RPAREN',
   'SHEETNAME',
   'IF',
   'FUNC',
   'COLUMN',
   'ABSREF',
   'RANGEOP',
   'POINT',
   'COMMA',
   'ERR',
   'STRING',
   'LE',
   'LT',
   'GE',
   'GT',
   'EQ',
   'NEQ',
   'CONCAT'
)

# Regular expression rules for simple tokens
t_ERR           = r'\#[A-Z]+[!?]'
t_STRING        = r'\"[^\"]*\"'
t_LPAREN        = r'\('
t_RPAREN        = r'\)'
t_COLUMN        = r'[A-Ha-h][A-Za-z]|[Ii][A-Va-v]|[A-Za-z]'
t_ABSREF        = r'\$'
t_RANGEOP       = r':'
t_POINT         = r'\.'

colMatch = re.compile(t_COLUMN)

def t_COMMA(t):
    r'[ \t]*\,[ \t]*' # eats space
    return t

def t_SHEETNAME(t):
    r'[A-Za-z0-9]*\!'
    t.value = t.value[:-1]      # strip trailing !
    return t

def t_TRUE(t):
    r'(?i)true(\(\))?'
    t.value = True
    return t

def t_FALSE(t):
    r'(?i)false(\(\))?'
    t.value = False
    return t

def t_IF(t):
    r'(?i)if'
    return t

def t_FUNC(t):
    r'[A-Za-z]+'

    # check against known functions
    # FIXME: shouldn't do this in lexer.  if not valid row, fail or something
    if t.value.upper() in funcs:
        return t

    # check if column
    if len(t.value) <= 2 and colMatch.match(t.value):
        #peek inside lexer to make sure that the user isn't actually try to call
        # a formula. if not then using the column logic.
        if not (t.lexer.lexpos < len(t.lexer.lexdata) and t.lexer.lexdata[t.lexer.lexpos] == '('):
            ret = lex.LexToken()
            ret.type = 'COLUMN'
            ret.value = t.value
            ret.lineno = t.lineno
            return ret

    # tell the parser to bail out on an unsupported function
    ret = lex.LexToken()
    ret.type = 'FUNC'
    ret.value = '__notimpl'
    ret.lineno = t.lineno
    return ret

def t_PLUS(t):
    r'[ \t]*\+[ \t]*'
    t.value = '+'
    return t

def t_MINUS(t):
    r'[ \t]*-[ \t]*'
    t.value = '-'
    return t

def t_TIMES(t):
    r'[ \t]*\*[ \t]*'
    t.value = '*'
    return t

def t_DIVIDE(t):
    r'[ \t]*/[ \t]*'
    t.value = '/'
    return t

def t_EXP(t):
    r'[ \t]*\^[ \t]*'
    t.value = '^'
    return t

def t_NEQ(t):
    r'[ \t]*\<\>[ \t]*'
    t.value = '<>'
    return t

def t_LE(t):
    r'[ \t]*\<\=[ \t]*'
    t.value = '<='
    return t

def t_LT(t):
    r'[ \t]*\<[ \t]*'
    t.value = '<'
    return t

def t_GE(t):
    r'[ \t]*\>\=[ \t]*'
    t.value = '>='
    return t

def t_GT(t):
    r'[ \t]*\>[ \t]*'
    t.value = '>'
    return t
    
def t_EQ(t):
    r'[ \t]*\=[ \t]*'
    t.value = '='
    return t

def t_CONCAT(t):
    r'[ \t]*\&[ \t]*'
    t.value = '&'
    return t

def t_FLOAT(t):
    r'((((\d+(\.\d*))|(\d*\.\d+))([eE][\+\-]{0,1}\d+)?)|(\d+[eE][\+\-]{0,1}\d+))[ ]*%?'

    origstr = t.value
    if t.lexer.decsep != '.':
        t.value = t.value.replace(t.lexer.decsep,'.')
    
    if t.value[-1:] == '%':
        t.value = srcfloat(float(t.value[:-1]) / 100)
    else:
        t.value = srcfloat(t.value)
    t.value.strval = origstr
    return t

def t_INTEGER(t):
    r'\d+[ ]*%?'
    if t.value[-1:] == '%':
        t.value = srcfloat(t.value[:-1]) / 100
    else:
        try:
            t.value = srcint(t.value)
        except OverflowError:
            t.value = srclong(t.value)
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
# t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.skip(1)


def main():

    # Test it out
    # data = '''3 + 4 * 10 + -20 *2 AB HA A B $IV'''
    data = '''A3 33. .33 3.3 3.03'''
    # data = '''A3 + DONG + SIN  33. .33 3.3 3.03 > < <= ^ assmonkey! #REF!'''
    # data = '''A3 + DONG + SIN  33. > < <= ^ "<img src=\"http://www.animated-teeth.com/wisdom_teeth/p_wisdom_tooth.gif\">"'''
    print data
    # data = '''c:c 4:5'''

    # Build the lexer
    lexer = getLexer()

    # Give the lexer some input
    lexer.input(data)

    # Tokenize
    while 1:
        tok = lexer.token()
        if not tok: break      # No more input
        print tok


def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
