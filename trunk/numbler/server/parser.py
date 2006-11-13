# (C) Numbler Llc 2006
# See License For Details.

import readline, copy
from numbler.server import yacc

# Get the token map from the lexer.  This is required.
import sheet, exc
from lexer import tokens
from ast import *
from sslib import singletonmixin, cappedStack
from colrow import Col,Row
from cell import CellHandle
from logicalfuncs import IF
parseroutdir = ''

try:
    import os
    lastsep = __file__.rfind(os.sep)
    parseroutdir = __file__[0:lastsep]
except:
    print '*** warning: failed to determine output folder for parser ****'

# lower is higher precedence
precedence = (
    ('left', 'EQ', 'LT', 'GT', 'LE', 'GE', 'NEQ','CONCAT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'EXP'),
    ('right', 'NEGATION'),            # Unary minus operator
    ('right', 'POSITIVE'),            # Unary plus operator
    ('left', 'RANGEOP')
)

binFuncs = {'+': Plus,
            '-': Minus,
            '*': Times,
            '/': Divide,
            '^': Exp,
            '=': EQ,
            '<=': LE,
            '<': LT,
            '>=': GE,
            '>': GT,
            '<>': NEQ,
            '&': Concat
            }

def p_binary_operators(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EXP expression
                  | expression LE expression
                  | expression LT expression
                  | expression GE expression
                  | expression GT expression
                  | expression EQ expression
                  | expression NEQ expression
                  | expression CONCAT expression
                  '''

    p[0] = binFuncs[p[2]](p[1], p[3])

def p_expression_cell(p):
    'expression : cell'
    p[0] = p[1]

def p_expression_function(p):
    '''expression : function
                  | ifFunction
    '''
    p[0] = p[1]

def p_expression_string(p):
    '''expression : STRING'''
    p[0] = String(p[1])

def p_expression_err(p):
    '''expression : ERR'''
    if p[1] in exc.errs:
        p[0] = exc.errs[p[1]]()
    else:
        raise SSValueError("Syntax error in input! " + str(p))

# unary minus
def p_expr_negation(p):
    'expression : MINUS expression %prec NEGATION'
    if isinstance(p[2],(int, long, float)):
        p[0] = -p[2]
    else:
        p[0] = Negation(p[2])

def p_expr_positive(p):
    'expression : PLUS expression %prec POSITIVE'
    if isinstance(p[2],(int,long,float)):
        p[0] = +p[2]
    else:
        p[0] = Positive(p[2])

# true, false
def p_expression_boolean(p):
    '''expression : TRUE
                  | FALSE
    '''
    p[0] = Boolean(p[1])

def p_expression_number(p):
    '''expression : INTEGER
                  | FLOAT
                  '''
    p[0] = Number(p[1])

def p_expression_expr(p):
    'expression : LPAREN expression RPAREN'
    p[0] = Paren(p[2])


def p_if(p):
    # If requires special handling because excel
    # introduced this crappy syntax so that with a trailing ,
    # you get a 0 or 1 value rather than the literal TRUE or FALSE
    '''ifFunction : IF LPAREN expression COMMA expression COMMA expression RPAREN
                  | IF LPAREN expression COMMA expression COMMA RPAREN
                  | IF LPAREN expression COMMA expression RPAREN
    '''
    if len(p) == 9:
        p[0] = IF(p[3],p[5],p[7])
    elif len(p) == 8:
        p[0] = IF(p[3],p[5],trailing=True)
    elif len(p) == 7:
        p[0] = IF(p[3],p[5])

def p_function(p):
    '''function : FUNC LPAREN arglist RPAREN
                | FUNC LPAREN RPAREN
    '''
    if p[1] == '__notimpl':
        raise SSNameError("function not supported")
        
    if len(p) == 4:
        p[0] = funcs[p[1].upper()]()
    else:
        p[0] = funcs[p[1].upper()](*p[3])
    if not p.parser.locale:
        p.parser.locale = p.parser.sheetHandle().ownerPrincipal.locale
    p[0].locale = p.parser.locale
    if p[0].needsSheetHandle:
        p[0].sheetHandle = p.parser.sheetHandle
    #if p[0].needsLocale:
    #    p[0].locale = p.parser.sheetHandle().ownerPrincipal.locale

def p_arglist(p):
    '''arglist : arg
               | arglist COMMA arg'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]

def p_arg(p):
    '''arg : expression
           | areareference'''
    p[0] = p[1]

def p_areareference(p):
    '''areareference : range
                     | vector'''
    p[0] = p[1]

def p_vector(p):
    '''vector : colrange
              | rowrange'''
    p[0] = p[1]

def p_arg_range(p):
    'range : cell RANGEOP cell'
    p[0] = Range(p[1], p[3])

def p_arg_colrange(p):
    'colrange : column RANGEOP column'
    p[0] = ColumnRange(p.parser.sheetHandle, p[1][1], p[3][1], p[1][0], p[3][0])

def p_arg_rowRange(p):
    # this is convoluted to prevent a reduce-reduce conflict
    '''rowrange : INTEGER RANGEOP INTEGER
                | absrow RANGEOP INTEGER
                | INTEGER RANGEOP absrow
                | absrow RANGEOP absrow'''

    r0, r1 = p[1], p[3]
    
    if isinstance(r0,int):
        a0 = False
    else:
        r0, a0 = r0[1], True

    if isinstance(r1,int):
        a1 = False
    else:
        r1, a1 = r1[1], True

    p[0] = RowRange(p.parser.sheetHandle, Row(r0), Row(r1), a0, a1)

def p_cell_col_row(p):
    '''cell : column row
            | SHEETNAME column row'''
    if len(p) == 4:
        p[0] = CellRef(CellHandle.getInstance(sheet.SheetHandle.getInstance(p[1]), p[2][1], p[3][1]),
                       p[2][0], p[3][0], explicit=True)
    else:
        p[0] = CellRef(CellHandle.getInstance(p.parser.sheetHandle, p[1][1], p[2][1]), p[1][0], p[2][0])

def p_column_col(p):
    '''column : COLUMN
              | ABSREF COLUMN'''
    if len(p) == 3:
        p[0] = True, Col(p[2])
    else:
        p[0] = False, Col(p[1])

def p_absrow_int(p):
    '''absrow : ABSREF INTEGER'''
    p[0] = True, Row(p[2])

def p_row_int(p):
     '''row : INTEGER
            | ABSREF INTEGER'''
     if len(p) == 3:
         p[0] = True, Row(p[2])
     else:
         p[0] = False, Row(p[1])

# Error rule for syntax errors
def p_error(p):
    raise SSValueError("Syntax error in input! " + str(p))

def interactive():

    import sys, engine, traceback
    eng = engine.Engine.getInstance()
    eng.log.quiet = True
    sht = sheet.Sheet.getInstance("booya").getHandle()

    while 1:
        try:
            s = raw_input('calc > ')
        except EOFError:
            break
        if not s: continue
        result = Parser.getInstance().parse(sht, s)
        print "formula:", result
        print "ast:    ", repr(result)

        import cell
        d4 = cell.CellHandle.parse(sht, "d4")

        if result != None:
            if type(result) == types.InstanceType:
                try:
                    print "     =", result.eval()
                    print "R1C1: ", result.getR1C1(d4)
                    # print "kids", [x for x in result]         # testing iterator
                except:
                    print "got exception"
                    exctype, value, tb = sys.exc_info()
                    print exctype, value, value.args[0]
                    traceback.print_tb(tb)

                # tr = result.translate(-1, -1)
                # print "translated:", tr, repr(tr)
                # print "tr exec   :", tr.eval()
                # print "orig:      ", result
            else:
                print "=", result

def main():
    interactive()
    # print yacc.parse("4 + C")
    
if __name__ == '__main__': main()
