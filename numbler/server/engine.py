# (C) Numbler LLC 2006
# See LICENSE for details.

##
##
## engine.py
##
## APIs for backend
##

import sys
import ssdb,yacc #parser
from sslib import log, singletonmixin,cappedStack
import lex

class Engine(singletonmixin.Singleton):

    def __init__(self):
        self.log = log.Log.getInstance(sys.stdout)
        self.ssdb = ssdb.ssdb.getInstance(self.log)
        self.parser = Parser.getInstance()

def main():
    engine = Engine.getInstance()

parseroutdir = ''

try:
    import os
    lastsep = __file__.rfind(os.sep)
    parseroutdir = __file__[0:lastsep]
except:
    print '*** warning: failed to determine output folder for parser ****'

def getLexer(decimalSepType = '.'):

    import lexer
    ret = None
    if decimalSepType == ',':
        lexer.t_FLOAT.__doc__ = r'((((\d+(\,\d*))|(\d*\,\d+))([eE][\+\-]{0,1}\d+)?)|(\d+[eE][\+\-]{0,1}\d+))[ ]*%?'
        lexer.t_COMMA.__doc__ = r'[ \t]*\;[ \t]*' # eats space
        ret = lex.lex(module=lexer)
        ret.decsep = ','
    elif decimalSepType == '.':
        lexer.t_FLOAT.__doc__ =     r'((((\d+(\.\d*))|(\d*\.\d+))([eE][\+\-]{0,1}\d+)?)|(\d+[eE][\+\-]{0,1}\d+))[ ]*%?'
        lexer.t_COMMA.__doc__ =     r'[ \t]*\,[ \t]*' # eats space
        ret = lex.lex(module=lexer)
        ret.decsep = '.'
    elif decimalSepType == '\xd9\xab':
        lexer.t_FLOAT.__doc__ = r'((((\d+(\xd9\xab\d*))|(\d*\xd9\xab\d+))([eE][\+\-]{0,1}\d+)?)|(\d+[eE][\+\-]{0,1}\d+))[ ]*%?'
        lexer.t_COMMA.__doc__ = r'[ \t]*\;[ \t]*' # eats space        
        ret = lex.lex(module=lexer)
        ret.decsep = '\xd9\xab'

    return ret


# A parser/lexer pair
class PL:
    def __init__(self,decType):
        # Use this if you want to build the parser using LALR(1) instead of SLR
        # yacc.yacc(method="LALR")
        import parser
        self.parser = yacc.yacc(tabmodule="numblertab",outputdir=parseroutdir,module=parser)
        self.lexer = getLexer(decType)

class Parser(singletonmixin.Singleton):
    def __init__(self):
        # initialize parsers for the three kinds of decimal seperators (for localization support)
        self.pls = cappedStack.CappedStack(4, PL,decType='.')
        self.commapls = cappedStack.CappedStack(4, PL,decType=',')
        self.arabicpls = cappedStack.CappedStack(4, PL,decType='\xd9\xab')        

    def parse(self, sheetHandle, formula,dectype = 0):
        if dectype == 0:
            pl = self.pls.get()
            release = self.pls.release
        elif dectype == 1:
            pl = self.commapls.get()
            release = self.commapls.release
        elif dectype == 2:
            pl = self.arabicpls.get()
            release = self.arabicpls.release
        else:
            raise 'parser not found'
        # Parse in the context of the current sheet
        try:
            pl.parser.sheetHandle = sheetHandle
            pl.parser.locale = None
            ret = pl.parser.parse(formula, lexer=pl.lexer)
        finally:
            release()
        return ret



if __name__ == '__main__': main()

