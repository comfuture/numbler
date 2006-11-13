# (C) Numbler LLC 2006
# See LICENSE for details.

from astbase import Function,checkstack
from exc import *
from nevow import tags as T

# used by doc generator
__shortmoddesc__ = 'Logical Functions'

##
## Logical Funcs
##

##class TRUE(Function):
##    def eval(self,stackvalue): return True

##class FALSE(Function):
##    def eval(self,stackvalue): return False

class LogicBase(Function):
    funcdetails = T.p['for more information see the wikipedia article on ',
                      T.a(href="http://en.wikipedia.org/wiki/Boolean_logic")['boolean logic.']
                      ]
    funcargs = {
        'varargs':'True',
        'args':[
        ('logical1',True,'a logical expression that is either TRUE or FALSE.'),
        ('logical2',False)
        ]
        }


class AND(LogicBase):
    """
    returns TRUE if all the arguments evaluate to TRUE.  FALSE is returned if one or more arguments is FALSE.
    """

    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)        
        if len(self.args) == 0:
            raise SSValueError("AND must have at least one argument")

        for arg in self.args:
            val = arg.eval(stackvalue)
            # Excel kinda sloppy
            if val in (0, 0.0, False): return False
            
        return True

class OR(LogicBase):
    """
    returns TRUE if one or more of the arguments evaluate to TRUE.  FALSE is only returned if all arguments are FALSE.
    """

    #funcdetails = T.p['for more information see the wikipedia article on ',
    #                  T.a(href="http://en.wikipedia.org/wiki/Boolean_logic")['boolean logic.']
    #                  ]

    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)                
        if len(self.args) == 0:
            raise SSValueError("OR must have at least one argument")

        for arg in self.args:
            val = arg.eval(stackvalue)
            if val is True: return True
            if isinstance(val,(int, long)) and val != 0: return True
            if isinstance(val,float) and val != 0.0: return True
            
        return False

class NOT(Function):
    """
    returns the opposite logical value of the specified value.
    """

    funcargs = {
        'args':[
        ('logical',True,'an expression that is either TRUE or FALSE.')
        ]
        }
        
    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)                        
        if len(self.args) != 1:
            raise SSValueError("NOT must have one argument")

        val = self.args[0].eval(stackvalue)
        if not isinstance(val,(bool, int, long, float)):
            raise SSValueError("NOT argument must be boolean or numeric")
        return not val

class IF(LogicBase):
    """
    IF returns the true_value if logical_test is True and false_value if logical_test is False.
    """

    funcargs = {
        'args':[
        ('logical_test',True,'an expression that evalutes to TRUE or FALSE'),
        ('true_value',True,'the value that is returned if logical_test is TRUE'),
        ('false_value',False,'the value that is returned if logical_test is FALSE. if false_value is not present then 0 is returned.')
        ]
        }
    
    
    IgnoreChildStyles = True

    def __init__(self,*args,**kwargs):
        self.args = args
        self.trailing = 'trailing' in kwargs

    # special versions of self representation routines to
    # deal with wacky trailing comma

    def __str__(self):
        return "IF(%s%s)" % (','.join([str(x) for x in self.args]),self.trailing and ',' or '')

    def getR1C1(self):
        return "IF(%s%s)" % (','.join([x.getR1C1(relCellH) for x in self.args]),self.trailing and ',' or '')

    def __repr__(self):
        return self.__str__()

    def translate(self,dc,dr):
        # custom translate handling to pass in the trailing argument
        ret = super(IF,self).translate(dc,dr)
        if self.trailing:
            ret.trailing = True
        return ret

    def mutate(self, tR,nR,tC,nC):
        ret = super(IF,self).mutate(tR,nR,tC,nC)
        if self.trailing:
            ret.trailing = True
        return ret
    
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)                                
        if len(self.args) == 0:
            raise NameError("Unrecognized name IF")
        elif len(self.args) > 3:
            raise SSValueError("Incorrect number of arguments")

        if len(self.args) == 3:
            elseVal = self.args[2]
        else:
            elseVal = False
        if len(self.args) > 1:
            ifVal = self.args[1]
        else:
            ifVal = True

        cond = self.args[0].eval(stackvalue)

        if not isinstance(cond,(bool, int, float, long)):
            # FIXME: allow empty text cell refs to return false?
            raise SSValueError()

        if cond:
            return ifVal.eval(stackvalue)
        else:
            if self.trailing:
                return 0
            elif type(elseVal) is bool:
                return elseVal
            else:
                return elseVal.eval(stackvalue)




funclist = (AND,OR,NOT,IF) # note: true and false are missing
