# (C) Numbler LLC 2006
# See LICENSE for details.

# variations on IF, SUMIF, COUNTIF

from astbase import Function
import re
from localedb import LocaleParser,ParseCtx
from littools import LitNode
from exc import *
from sslib import mrudict

class IfBase(Function):
    """
    IfBase is used by the SUMIF and COUNTIF
    implementions.  the derived class must support the proccell method

    def procCell(cellHandle,cellValue)

    """

    IgnoreChildStyles = True
    compMatcher = re.compile('^(?P<op>[<>=]*)(?P<parseval>.*)$')

    # keep around an MRUdict of values for if comparisons
    criteriaCache = mrudict.MRUDict(128)
    needsLocale = True

    def getCompareOps(self,stackvalue):
        # if we are dealing with a string we need to do a "mini parse"
        # operation where we quote any embedded strings.  bleh.

        # set the default comparision operator
        op = '='

        from ast import String,Concat
        if isinstance(self.args[1],(String,Concat)):

            # lookup and see if this value has already been computed in the past.
            rawcomparitor = self.args[1].eval(stackvalue)
            if not rawcomparitor in self.criteriaCache:
                match = self.compMatcher.match(rawcomparitor)
                if match:
                    if match.groupdict()['op']:
                        op = match.groupdict()['op']
                else:
                    # I can't think of a senario when this happens.  the purpose of the
                    # regexp is mostly to identify content in the string.
                    raise "error"
                
                comparitor = match.groupdict()['parseval']

                try:
                    ctx = ParseCtx()
                    res = LocaleParser.getInstance(str(self.locale)).parse(ctx,comparitor)
                    if isinstance(res,LitNode):
                        compval = res.eval()
                    else:
                        compval = res
                except LiteralConversionException,e:
                    compval = comparitor

                if isinstance(compval,basestring):
                    compval = compval.lower()
                    
                self.criteriaCache[rawcomparitor] = (compval,op)
            else:
                compval,op = self.criteriaCache[rawcomparitor]
        else:
            compval = self.args[1].eval(stackvalue)
            if isinstance(compval,basestring):
                compval = compval.lower()


        return compval,op

    def runCompare(self,cellval,compval,op):
        if op == '=':
            if cellval == compval:
                self.procCell(cellH,cellval)
        elif op == '<=':
            if cellval <= compval:
                self.procCell(cellH,cellval)
        elif op == "<":
            if cellval < compval:
                self.procCell(cellH,cellval)
        elif op == ">":
            if cellval > compval:
                self.procCell(cellH,cellval)
        elif op == ">=":
            if cellval >= compval:
                self.procCell(cellH,cellval)
        elif op == "<>":
            if cellval != compval:
                self.procCell(cellH,cellval)                                                    


