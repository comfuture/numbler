# (C) Numbler LLC 2006
# See LICENSE for details.

from sslib import singletonmixin,cappedStack
from numbler.server import literal_parser,literal_lexer
import lex,PyICU,datetime,math
from numbler.server import yacc
from numbler.server.exc import SSNumError,SSError
from pkg_resources import resource_filename


def converterCatcher(func,*args,**kwargs):
    """
    generic generator to catch and retranslate exceptions.
    
    @converterCatcher
    def tester():
        a = 4/0
    """
    
    def converter(*args,**kwargs):
        try:
            return func(*args,**kwargs)
        except ArithmeticError:
            raise SSNumError()
    return converter




class NumblerLocale(object):
    """
    provides basic locale support for use by higher level
    objects.  This class shields upper level code
    from the nastiness of the locale dictionary
    """
    daysecs = 86400
    timebase = datetime.datetime(1900,1,1)
    lowbounds = datetime.datetime(1900,1,1)-datetime.timedelta(1)    
    maxserialdate = 2958465.999
    defSciBoundary = 1e+11-1

    def __init__(self,localeCode,tzName):
        self.locale = PyICU.Locale(localeCode)
        # decimal seperator for use by the formula parser
        self.dectype = LocaleParser.getSeparator(localeCode)
        self.tz = PyICU.ICUtzinfo.getInstance(tzName)
        self.dateFmt,self.currFmt,self.timeFmt = None,None,None
        self.dtFmt,self.perctFmt,self.decFmt = None,None,None
        self.sciFmt,self.shortDateFmt,self.longDateFmt = None,None,None
        self.longTimeFmt,self.vsmdFormat,self.vsmyFormat = None,None,None
        self.commaFmt = None

    def __str__(self):
        return str(self.locale)

    ### private conversion methods

    @converterCatcher
    def _convertDate(self,value):
        if value < 0 or value > self.maxserialdate:
            raise SSNumError()
        
        intval = math.modf(value)[1]
        # -1 for 1900 leap year bug
        return self.lowbounds + datetime.timedelta(intval-1)

    @converterCatcher
    def _convertTime(self,value):
        if value < 0 or value > self.maxserialdate:       
            raise SSNumError()
        
        fract = math.modf(value)[0]
        sec = int(self.daysecs * fract)
        return self.timebase + datetime.timedelta(0,sec)

    @converterCatcher
    def _convertDateTime(self,value):
        if value < 0 or value > self.maxserialdate:               
            raise SSNumError()
        
        fract,intval = math.modf(value)
        sec = int(self.daysecs * fract)
        return self.lowbounds + datetime.timedelta(intval-1,sec)

    ### public conversion methods

    ## the very short methods aren't local specific and exist
    ## for excel compatibility

    def veryShortMonthDay(self,value):
        if not self.vsmdFormat:
            self.vsmdFormat = PyICU.DateFormat.createDateInstance(PyICU.DateFormat.SHORT,self.locale)
            self.vsmdFormat.applyPattern('d-MMM')
        return self.vsmdFormat.format(self._convertDate(value))

    def veryShortMonthYear(self,value):
        if not self.vsmyFormat:
            self.vsmyFormat = PyICU.DateFormat.createDateInstance(PyICU.DateFormat.SHORT,self.locale)
            self.vsmyFormat.applyPattern('MMM-YYYY')
        return self.vsmyFormat.format(self._convertDate(value))
            

    def defCurrencyFormat(self,value):
        if not self.currFmt:
            self.currFmt = PyICU.DecimalFormat.createCurrencyInstance(self.locale)
        return self.currFmt.format(value)

    def defShortDateFormat(self,value):
        if not self.shortDateFmt:
            self.shortDateFmt = PyICU.DateFormat.createDateInstance(PyICU.DateFormat.SHORT,self.locale)
            pat =  self.shortDateFmt.toPattern()
            # ensure that we always use 4 digit years.
            if pat.find('yyyy') < 0:
                self.shortDateFmt.applyPattern(pat.replace('yy','yyyy'))
        return self.shortDateFmt.format(self._convertDate(value))

    def defDateFormat(self,value):
        if not self.dateFmt:
            self.dateFmt = PyICU.DateFormat.createDateInstance(PyICU.DateFormat.MEDIUM,self.locale)
        return self.dateFmt.format(self._convertDate(value))

    def longDateFormat(self,value):
        if not self.longDateFmt:
            self.longDateFmt = PyICU.DateFormat.createDateInstance(PyICU.DateFormat.LONG,self.locale)
        return self.longDateFmt.format(self._convertDate(value))

    def defTimeFormat(self,value):
        if not self.timeFmt:
            self.timeFmt = PyICU.DateFormat.createTimeInstance(PyICU.DateFormat.SHORT,self.locale)
        return self.timeFmt.format(self._convertTime(value))

    def longTimeFormat(self,value):
        if not self.longTimeFmt:
            self.longTimeFmt = PyICU.DateFormat.createTimeInstance(PyICU.DateFormat.MEDIUM,self.locale)
        return self.longTimeFmt.format(self._convertTime(value))

    def defPercentFormat(self,value):
        """ ICU expects that the value is already a fraction """
        if not self.perctFmt:
            self.perctFmt = PyICU.DecimalFormat.createPercentInstance(self.locale)
        return self.perctFmt.format(value)

    def defDateTimeFormat(self,value):
        if not self.dtFmt:
            self.dtFmt = PyICU.DateFormat.createDateTimeInstance(PyICU.DateFormat.MEDIUM,
                                                                    PyICU.DateFormat.MEDIUM,
                                                                    self.locale)
        return self.dtFmt.format(self._convertDateTime(value))

    def defDecimalFormat(self,value):
        if value > self.defSciBoundary:
            return self.defScientificFormat(value)
        if not self.decFmt:
            self.decFmt = PyICU.DecimalFormat.createInstance(self.locale)
            self.decFmt.setMaximumFractionDigits(6)
            self.decFmt.setGroupingSize(-1)
        return self.decFmt.format(value)

    def defCommaFormat(self,value):
        if not self.commaFmt:
            self.commaFmt = PyICU.DecimalFormat.createInstance(self.locale)
            self.commaFmt.setMaximumFractionDigits(2)
        return self.commaFmt.format(value)

    def defScientificFormat(self,value):
        if not self.sciFmt:
            self.sciFmt = PyICU.DecimalFormat.createScientificInstance(self.locale)
            self.sciFmt.applyPattern('0.#####E+0')
        return self.sciFmt.format(value)

    lookupTable = {
        u'vsmd' : veryShortMonthDay,
        u'vsmy' : veryShortMonthYear,
        u'sd'   : defShortDateFormat,
        u'md'   : defDateFormat,
        u'ld'   : longDateFormat,
        u'mt'   : defTimeFormat,
        u'lt'   : longTimeFormat,
        u'dt'   : defDateTimeFormat,
        u'dc'   : defDecimalFormat,
        u'de'   : defScientificFormat,
        u'%'    : defPercentFormat,
        u'$'    : defCurrencyFormat,
        u','    : defCommaFormat
        }

    def formatPerLocale(self,value,fmt):
        handler = self.lookupTable.get(fmt)
        if handler:
            try:
                value = handler(self,value)
            except SSError,e:
                value = str(e)
            except Exception,e:
                print 'WARNING: generic exception handled for',e,value
        else:
            print 'WARNING: handler not found for',fmt
        return value
        
    
# A parser/lexer pair that is locale specific
class PL:
    optimize = 0
    debug = 0
    def __init__(self,localeCode):
        # Use this if you want to build the parser using LALR(1) instead of SLR
        # yacc.yacc(method="LALR")
        localeparser = __import__('numbler.server.locale.parser_%s' % (str(localeCode)),{},{},'*')
        self.parser = yacc.yacc(tabmodule="localtab_%s" % localeCode,
                                tabmoduleparent="numbler.server.locale",
                                outputdir=resource_filename('numbler.server.locale',''),
                                module=localeparser,
                                optimize=self.optimize)
        self.lexer = lex.lex(module=localeparser,debug=self.debug) #optimize=self.optimize,
                             
class Parser(object):
    def __init__(self,localeCode):
        self.pls = cappedStack.CappedStack(4, PL,localeCode=localeCode)

    def parse(self,parsectx,literalval):
        """
        parse a literal and return the value.  Any style specific
        information is remembered in the parsectx
        """
        literalval = literalval.strip()
        if len(literalval):
            try:
                pl = self.pls.get()
                pl.parser.parsectx = parsectx
                # use the parse context
                ret = pl.parser.parse(literalval.strip(), lexer=pl.lexer,debug=pl.debug)
            finally:
                self.pls.release()
        else:
            return literalval
        return ret

class LocaleParser(object):
    """
    The LocaleParser is a collection of all Parser instances bound to a specific
    locale.  each locale is automatically generated if it does not exist using
    module hackery.  Basically, we create a module on the fly, copy the lexer
    properties and then inject modified properties that are specific to a locale
    (like the names of months)
    """
    
    parserdict = {}

    def getInstance(cls,localeCode):
        if localeCode not in cls.parserdict:
            cls.parserdict[localeCode] = Parser(localeCode)
        return cls.parserdict[localeCode]
    getInstance = classmethod(getInstance)

    # dictionary of decimal separators. right now we only expect that this will ever
    # have more than three entries, ".", ",", and \u066b (arabic decimal separator)

    decimalSepDict = {}
    translatetbl = {'.':0,',':1,'\xd9\xab':2}
    
    def getSeparator(cls,localeCode):
        if localeCode not in cls.decimalSepDict:
            sym = PyICU.DecimalFormatSymbols(PyICU.Locale(localeCode))
            val = sym.getSymbol(sym.kMonetarySeparatorSymbol).encode('utf-8')
            index = cls.translatetbl.get(val)
            if index is None:
                print 'WARNING: unknown decimal separator'
                index = 0
            cls.decimalSepDict[localeCode] = index
        return cls.decimalSepDict[localeCode]
    getSeparator = classmethod(getSeparator)
        
    
class ParseCtx(object):
    """
    The ParseCtx class is used for every parse action over
    a literal value.
    """

    # list of available formats.  This is hidden for the most
    # part but is accessible by other object to build lookup
    # tables

    formats = [
        'vsmd',          # very short month day
        'vsmy',          # very short month year
        'sd',            # short date
        'md',            # medium date
        'ld',            # long date
        'mt',            # medium time
        'lt',            # long time
        'dt'             # datetime
        'dc',            # decimal, integer or floating point
        'de',            # integer or floating point with exponent
        '%',             # percentage
        '$',             # currency
        ','              # comma style
        ]
    
    currencyFormat = u'$'
    dateTimeFormat = u'dt'
    mediumDateFormat = u'md'
    mediumTimeFormat = u'mt'
    longTimeFormat = u'lt'
    shortDateFormat = u'sd'
    percentFormat = u'%'
    scientificFormat = u'de'
    dateIds = [u'sd',u'md',u'mt',u'lt',u'dt',u'vsmd',u'vsmy']
    overridableFormats = [u'dc',u'de',u'lit']
    defaultDecimalFormat = u'dc'
    commaFormat = u','
    veryshortMonthDayFormat = u'vsmd'
    veryshortMonthYearFOrmat = u'vsmy'
    
    def __init__(self):
        self.fmt = None

    def rememberFmt(self,val):
        self.fmt = val

    def isDateLike(self):
        # also does times
        return self.fmt in self.dateIds


def testAll():
    from PyICU import Locale
    alllocales = Locale('').getAvailableLocales()
    for lkey in alllocales.keys():
        print 'testing',str(lkey)
        l = alllocales[lkey]        
        ctx = ParseCtx()
        p = LocaleParser.getInstance(str(l))
        try:
            p.parse(ctx,'10 p')
        except Exception,e:
            print 'failed to parse simple time on with',str(l)
        
