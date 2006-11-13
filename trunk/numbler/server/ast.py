# (C) Numbler LLC 2006
# See LICENSE for details.

##
## Formula Abstract Syntax Tree support
##

import types, math, copy
from sslib.flatten import flatten,isiterable
from astbase import checkstack,Node,CellRef,RangeMixin,Range,ColumnRange,RowRange,Function,ensureNumeric
from exc import *
from localedb import ParseCtx
from twisted.python.reflect import namedAny
from primitives import srcfloat,srcint,srclong

function_modules = ['mathfuncs','textfuncs','isfuncs','lookupfuncs',
                    'financialfuncs','timefuncs','statfuncs',
                    'logicalfuncs',
                    'asyncfunction']

# numberfuncs is the definitve list of all sheet functions in the system.
numblerfuncs = list(flatten([namedAny(fullmod).funclist
                             for fullmod in ['numbler.server.' + x for x in function_modules]]))
# funcs is a string dictionary of all functions
funcs = dict([(x.__name__.upper(), x) for x in numblerfuncs])

##
## Binary operators
##
class BinOp(Node):

    def __init__(self, left, right):
        self.left, self.right = left, right

    def __deepcopy__(self, memo):
        return self.__class__(copy.deepcopy(self.left, memo),
                              copy.deepcopy(self.right, memo))

    def __repr__(self):
        return "%s(%s, %s)" % (self.__class__, repr(self.left), repr(self.right))

    def __str__(self):
        return "%s %s %s" % (self.left, self.op, self.right)

    def getR1C1(self, relCellH):
        return "%s %s %s" % (self.left.getR1C1(relCellH), self.op, self.right.getR1C1(relCellH))

    def translate(self, dc, dr):
        nArgs = []
        for arg in self.left, self.right:
            if isinstance(arg, Node):
                nArg = arg.translate(dc, dr)
            else:
                nArg = copy.copy(arg)
            nArgs.append(nArg)
        return self.__class__(*nArgs)

    def mutate(self,tR,nR,tC,nC):
        nArgs = []
        for arg in self.left, self.right:
            if isinstance(arg, Node):
                nArg = arg.mutate(tR,nR,tC,nC)
            else:
                nArg = copy.copy(arg)
            nArgs.append(nArg)
        return self.__class__(*nArgs)        

    def walk(self):
        yield self
        for arg in self.left, self.right:
            if isinstance(arg, Node):
                for x in arg.walk():
                    yield x
            else:
                yield arg

    def astwalker(self,stackvalue):
        """
        walk left to rgiht
        This implemention considers both the left and right,
        if a value on the left does not exist take one from the right
        """
        stackvalue = stackvalue + 1
        checkstack(stackvalue)
        
        if isinstance(self.left,Node):
            leftret = self.left.getImpliedFormatting(stackvalue)

        if not leftret or leftret in ParseCtx.overridableFormats:
            yield self.right
        else:
            yield leftret
        
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)                                
        return self.func(self.left.eval(stackvalue), self.right.eval(stackvalue))

class Plus(BinOp):
    op = "+"
    def func(self, a, b):
        a, b = ensureNumeric(a, b)
        return a + b
    
class Minus(BinOp):
    op = "-"
    def func(self, a, b):
        a, b = ensureNumeric(a, b)
        return a - b

class Times(BinOp):
    op = "*"
    def func(self, a, b):
        a, b = ensureNumeric(a, b)
        return a * b

class Divide(BinOp):
    op = "/"
    def func(self, a, b):
        a, b = ensureNumeric(a, b)
        try:
            return float(a) / float(b)
        except ZeroDivisionError:
            raise SSZeroDivisionError("Attempt to divide by zero: %d / %d" % (a, b))

class Exp(BinOp):
    op = "^"
    def func(self, a, b):
        a, b = ensureNumeric(a, b)
        return a ** b

# Comparison operators
class LE(BinOp):
    op = "<="
    def func(self, a, b):
        if type(a) is str and type(b) is str:
            return a.lower() <= b.lower()
        else:
            return a <= b

class LT(BinOp):
    op = "<"
    def func(self, a, b):
        if type(a) is str and type(b) is str:
            return a.lower() < b.lower()
        else:
            return a < b

class GE(BinOp):
    op = ">="
    def func(self, a, b):
        if type(a) is str and type(b) is str:
            return a.lower() >= b.lower()
        else:
            return a >= b

class GT(BinOp):
    op = ">"
    def func(self, a, b):
        if type(a) is str and type(b) is str:
            return a.lower() > b.lower()
        else:        
            return a > b

class EQ(BinOp):
    op = "="
    def func(self, a, b):
        if type(a) is str and type(b) is str:
            return a.lower() == b.lower()
        else:                
            return a == b

class NEQ(BinOp):
    op = "<>"
    def func(self, a, b):
        if type(a) is str and type(b) is str:
            return a.lower() != b.lower()
        else:                
            return a != b

# string concatination operator
class Concat(BinOp):
    op = "&"
    def func(self,a,b):
        return ''.join([str(a),(str(b))])

# Nodes with single args
class UniOp(Node):
    def __init__(self, val):
        self.val = val

    def __deepcopy__(self, memo):
        return self.__class__(copy.deepcopy(self.val, memo))

    def __repr__(self):
        return "%s(%s)" % (self.__class__, repr(self.val))

    def translate(self, dc, dr):
        if isinstance(self.val, Node):
            nArg = self.val.translate(dc, dr)
        else:
            nArg = copy.copy(self.val)
        return self.__class__(nArg)

    def mutate(self, tR,nR,tC,nC):
        if isinstance(self.val, Node):
            nArg = self.val.mutate(tR,nR,tC,nC)
        else:
            nArg = copy.copy(self.val)
        return self.__class__(nArg)
        

    def walk(self):
        yield self
        if isinstance(self.val, Node):
            for x in self.val.walk():
                yield x
        else:
            yield self.val

    def astwalker(self,stackvalue):
        yield None

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)                                        
        return self.val.eval(stackvalue)
    
class Paren(UniOp):

    def __str__(self):
        return "(%s)" % self.val

    def getR1C1(self, relCellH):
        return "(%s)" % self.val.getR1C1(relCellH)

class Negation(UniOp):

    def __str__(self):
        return "-%s" % self.val

    def getR1C1(self, relCellH):
        return "-%s" % self.val.getR1C1(relCellH)

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)                                                
        return -1 * self.val.eval(stackvalue)

class Positive(UniOp):
    def __str__(self):
        return "+%s" % self.val

    def getR1C1(self, relCellH):
        return "+%s" % self.val.getR1C1(relCellH)

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)                                                        
        return 1 * self.val.eval(stackvalue)
        
class String(UniOp):

    def __str__(self):
        return self.val
        # return self.val.replace('"', '\\"')

    def getR1C1(self, relCellH):
        return self.val

    def translate(self, dc, dr):
        return String(self.val)

    def mutate(self,tR,nR,tC,nC):
        return String(self.val)

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        return self.val[1:-1].replace("\\", "")

# passthrough for use in formulas like "=5"
class Number(UniOp):
    def __str__(self):
        return "%s" % self.val

    def getR1C1(self, relCellH):
        return "%s" % self.val

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)        
        return self.val

    translateTypes= (srcint,srcfloat,srclong)
    def translate(self, dc, dr):
        # self.val should be a srcint or srcfloat object
        if isinstance(self.val,self.translateTypes):
            return self.val.strval
        else:
            return str(self.val)

    def mutate(self, tR,nR,tC,nC):
        return self
    

    def walk(self):
        yield self
        yield self.val

class Boolean(UniOp):
    def __str__(self):
        return self.val and "TRUE" or "FALSE"

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)                
        return self.val

    def getR1C1(self,relCellH):
        return self.__str__()

    def translate(self,dc,dr):
        return self.__str__()

    def mutate(self, tR,nR,tC,nC):
        return self
