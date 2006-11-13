# (C) Numbler Llc 2006
# See License For Details.

from astbase import Function,checkstack,CellRef,ensureNumeric
import string
from exc import *
import engine
from sslib.flatten import flatten,isiterable
from nevow import tags as T

# used by doc generator
__shortmoddesc__ = 'Text Functions'

class textFunction(Function):
    """
    base class for text functions
    """


    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        if len(self.args) != self.expectedargs:
            raise WrongNumArgumentsError(self.__class__.__name__)         
        return self.runfunc(stackvalue)


class PROPER(textFunction):
    """
    convert text_value to it's proper format, meaning the first character of every letter is converted to upper case.
    """

    funcargs = {'args':[
        ('text_value',True,'Any value that evaluates to a text value, either text enclosed in quotation marks or reference to a cell or formula that computes a text value')
        ]}

    expectedargs = 1
    def runfunc(self,stackvalue):
        text = self.args[0].eval(stackvalue)
        if not isinstance(text,basestring):
            # simply pass through the value
            return text
        return string.capwords(text)


class INDIRECT(textFunction):
    """
    convert's ref_text to a real cell reference.
    """

    funcargs = {'args':[
        ('ref_text',True,'ref_text can be a text value (e.g "A4") or a cell reference that refers to another cell.')
        ]}

    funcdetails = T.div["Use INDIRECT if you want to make sure that a cell reference never gets translated if you move the formula around the spreadsheet.  To always refer to C12 use =INDIRECT('C12')"]
    
    # tell the parser we need a sheet handle
    needsSheetHandle = True
    expectedargs = 1
    def runfunc(self,stackvalue):
        refstr = self.args[0].eval(stackvalue)
        if not isinstance(refstr,basestring):
            raise SSRefError()

        indirnode = engine.Engine.getInstance().parser.parse(self.sheetHandle,refstr,self.locale.dectype)
        if not isinstance(indirnode,CellRef):
            raise SSRefError()
        return indirnode.eval(stackvalue)

class CONCATENATE(Function):
    """
    concatenate one or more text values together into one text value.
    """

    funcargs = {
        'varargs':True,
        'args':[
        ('text1',True,'any value that can be converted to a text value (e.g numbers, dates, etc)'),
        ('text2',False,'second argument')
        ]}

    funcdetails = T.div['CONCATENATE is supported for backwards compatability with existing spreadsheet programs.  Numbler supports the native ampersand operator to join strings, eg ="hello"&" "&"world".']

    expectedargs = 0
    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        if len(self.args) == 0:
            raise WrongNumArgumentsError('CONCATENATE')         
        return ''.join([str(x) for x in flatten([y.eval(stackvalue) for y in self.args])])


class offsetBase(Function):
    """
    base class for LEFT and RIGHT
    """

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)

        arglen = len(self.args)
        if arglen == 1:
            offset = 1
        elif arglen == 2:
            offset, = ensureNumeric(self.args[1].eval(stackvalue))
        else:
            raise WrongNumArgumentsError(self.__class__.__name__)

        val = self.args[0].eval(stackvalue)
        if not isinstance(val,basestring) or offset < 0:
            raise BadArgumentsError()
        if offset > len(val):
            offset = len(val)
        return self.runfunc(val,offset)

class LEFT(offsetBase):
    """
    return the first N characters in text_value.
    """

    funcargs = {'args':[
        ('text_value',True,'the target text value'),
        ('num_chars',False,'the number of characters from the left (beginning) to return.  If num_chars is omitted the default value is 1.')
        ]}

    def runfunc(self,val,leftoffset):
        return val[0:leftoffset]
        
class RIGHT(offsetBase):
    """
    return the last N characters in text_value.
    """

    funcargs = {'args':[
        ('text_value',True,'text target text value'),
        ('num_chars',False,'the number of characters from the right (end) to return.  If num_chars is omitted the default value is 1.')
        ]}
    
    def runfunc(self,val,rightoffset):
        # special case
        if rightoffset == 0:
            return ''
        return val[-rightoffset:]
    

class HYPERLINK(Function):
    """
    Create a hyperlink.
    """

    funcargs = {'args':[
        ('link',True,'location of link.  You must include the HTTP specifier to create a web link.'),
        ('name',False,'the name of the link.  If name is not specified the link will be displayed as the name.')
        ]}

    funcdetails = T.div["Numbler natively supports hyperlinks that are directly typed into a cell.  The HYPERLINK function is provided for backwards compatability and when you want to name a link."]
    

    def eval(self,stackvalue):
        stackvalue = stackvalue +1
        checkstack(stackvalue)
        arglen = len(self.args)

        link = self.args[0].eval(stackvalue)
        disptext = ''
        if arglen == 1:
          disptext = link  
        elif arglen == 2:
            disptext = self.args[1].eval(stackvalue)
        elif arglen == 0 or arglen > 2:
            raise WrongNumArgumentsError('HYERLINK')

        # I could use stan here I suppose but I am not.
        return '<a href="%s" target="numblerwin">%s</a>' % (link,disptext)


funclist = (PROPER,INDIRECT,CONCATENATE,LEFT,RIGHT,HYPERLINK)
