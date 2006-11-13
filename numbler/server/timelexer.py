# (C) Numbler Llc 2006
# See License For Details.

import lex
from pyparsing import Or,Word,nums,Literal,And,Or,StringEnd,alphas,alphas8bit
from pyparsing import Literal as CaselessLiteral
from PyICU import DateFormat,Locale,DecimalFormat,DateFormatSymbols

class DateFragment(object):
    token = 'INTEGER'
    ignore = False
    expects = int
    def __init__(self,val):
        self.val = val
    def getExpects(self):
        return self.expects
    def getToken(self):
        return self.token

class Era(DateFragment):

    def genParseObject(self,cLocale):
        sym = DateFormatSymbols(cLocale)
        val = sym.getEras()
        frag = Or(CaselessLiteral(val[0].encode('utf-8')))
        for item in val[1:]:
            frag.append(CaselessLiteral(item.encode('utf-8')))
        return frag.setResultsName('era')

class DateSeperator(DateFragment):
    token = 'datesep'
    ignore = True
    def genParseObject(self,cLocale):
        val = Literal('-') | Literal('/') | Literal('.')
        return val.setResultsName('datesep')
    
class TimeSeperator(DateFragment):
    token = 'TIMESEP'
    ignore = True
    def genParseObject(self,cLocale):
        return Literal(':').setResultsName('timesep')


class Year(DateFragment):
    def genParseObject(self,cLocale):
        val = Word(nums,min=1,max=4)
        return val.setResultsName('year')

class MonthInYear(DateFragment):
    token = 'month'

    def getExpects(self):
        if len(self.val) < 3:
            return int
        else:
            return str
    def getToken(self):
        if self.getExpects() == int:
            return 'INTEGER'
        else:
            return 'month'
    
    def genParseObject(self,cLocale):

        # generate dictionary of months
        self.monthdict = {}
        x = 1
        sym = DateFormatSymbols(cLocale)
        for sm in sym.getShortMonths():
            self.monthdict[sm.encode('utf-8').lower()] = x
            x += 1
        x = 1            
        for mm in sym.getMonths():
            self.monthdict[mm.encode('utf-8').lower()] = x
            x += 1

        def parseHandler(s,loc,toks):
            if toks[0].lower() not in self.monthdict:
                raise 'fuck'
        
        ret = Word(alphas + alphas8bit).setResultsName('month')
        ret.setParseAction(parseHandler)
        return ret
        
class DateInMonth(DateFragment):
    def genParseObject(self,cLocale):
        return Word(nums,min=1,max=2).setResultsName('dayinmonth')

class TwelveHour(DateFragment):
    def genParseObject(self,cLocale):
        return Word(nums,min=1,max=2).setResultsName('12hour')

class TwentyFourHour(DateFragment):
    def genParseObject(self,cLocale):
        return Word(nums,min=1,max=2).setResultsName('24hour')

class Minute(DateFragment):
    def genParseObject(self,cLocale):
        return Word(nums,min=1,max=2).setResultsName('minute')

class Second(DateFragment):
    def genParseObject(self,cLocale):
        return Word(nums,min=1,max=2).setResultsName('second')        

class Millisec(DateFragment):
    def genParseObject(self,cLocale):
        return Word(nums,min=1,max=3).setResultsName('millisec')        

class DayInWeek(DateFragment):
    token = 'DAYINWEEK'
    def genParseObject(self,cLocale):
        return Word(alphas + alphas8bit)        
##        sym = DateFormatSymbols(cLocale)
##        def buildList():
##            day = 1
##            # the ICU weekdays and shortweekdays have an empty first value            
##            for dayval in sym.getShortWeekdays()[1:]:
##                yield CaselessLiteral(dayval.encode('utf-8')).setResultsName('day' + str(day))
##                day += 1
##            day = 1
##            for dayval in sym.getWeekdays()[1:]:
##                yield CaselessLiteral(dayval.encode('utf-8')).setResultsName('day' + str(day))
##                day += 1
            
##        return Or(list(buildList()))

class DayInYear(DateFragment):
    def genParseObject(self,cLocale):
        return Word(nums,min=1,max=3).setResultsName('dayinyear')            

class DayWeekMonth(DateFragment):
    def genParseObject(self,cLocale):
        return Word(nums,exact=1).setResultsName('dayweekmonth')

class WeekInYear(DateFragment):
    def genParseObject(self,cLocale):
        return Word(nums,min=1,max=2).setResultsName('weekinyear')

class AmPm(DateFragment):
    token = 'CLOCK'
    def genParseObject(self,cLocale):
        sym = DateFormatSymbols(cLocale)
        ampm = sym.getAmPmStrings()
        val = CaselessLiteral(ampm[0].encode('utf-8')).setResultsName('am')
        val |= CaselessLiteral(ampm[0].encode('utf-8')).setResultsName('pm')
        val |= CaselessLiteral('am').setResultsName('am')
        val |= CaselessLiteral('pm').setResultsName('pm')
        val |= CaselessLiteral('a').setResultsName('am')
        val |= CaselessLiteral('p').setResultsName('pm')
        return val

class PassThroughLit(DateFragment):
    token = 'CUSTOMLIT'        
    
    def genParseObject(self,cLocale):
        return Literal(self.val.strip(' '))

tokens = (
    'ERA',
    'YEAR',
    'MONTH',
    'DAY',
    '12HOUR',
    '24HOUR','MINUTE','SECOND','MILLISEC','DAYOFWEEK','DAYINYEAR','DAYWEEKMONTH',
    'WEEKINYEAR','WEEKINMONTH',
    'AMPM','24HOURDAY_OFFSET1','12HOURDAY_OFFSET1','TZ','TEXTMATCH'
    )

def t_ERA(t):
    r'[G]+'
    t.value = Era(t.value)
    return t
    
def t_YEAR(t):
    r'[y]+'
    t.value = Year(t.value)
    return t
    
    
def t_MONTH(t):
    r'[M]+'
    t.value = MonthInYear(t.value)
    return t

def t_DAY(t):    
    r'[d]+'
    t.value = DateInMonth(t.value)
    return t
    
def t_12HOUR(t):
    r'[h]+'
    t.value = TwelveHour(t.value)
    return t

def t_24HOUR(t):
    r'[H]+'
    t.value = TwentyFourHour(t.value)
    return t

def t_MINUTE(t):
    r'[m]+'
    t.value = Minute(t.value)
    return t

def t_SECOND(t):
    r'[s]+'
    t.value = Second(t.value)
    return t

def t_MILLISEC(t):
    r'[S]+'
    t.value = Millsec(t.value)
    return t

def t_DAYOFWEEK(t):
    r'[E]+'
    t.value = DayInWeek(t.value)
    return t

def t_DAYINYEAR(t):
    r'[D]+'
    t.value =DayInYear(t.value)
    return t
    
def t_DAYWEEKMONTH(t):
    r'[F]+'
    t.value = DayWeekMonth(t.value)
    return t

def t_WEEKINYEAR(t):
    r'[w]+'
    t.value = WeekInYear(t.value)
    return t

def t_WEEKINMONTH(t):
    r'[W]+'
    t.value = WeekInMonth(t.value)
    return t
    
def t_AMPM(t):
    r'a'
    t.value = AmPm(t.value)
    return t

# skip these tokens as they aren't widely used (at all in the defaults AFAIK)
# or they aren't used by excel

def t_24HOURDAY_OFFSET1(t):
    r'[k]+'
    t.skip(len(t.value))

def t_12HOURDAY_OFFSET1(t):
    r'[K]+'
    t.skip(len(t.value))

def t_TZ(t):
    r'[zZ]+'
    t.skip(len(t.value))

def t_TEXTMATCH(t):
    r"\'[^\']+[\']{1}"
    t.value = PassThroughLit(t.value[1:-1])
    return t
    #t.skip(len(t.value))


def t_SINGLEQUOTE(t):
    r'\"'
    t.value = "'"
    return t

t_ignore ='\t'

def t_error(t):
    t.skip(1)
    if t.value[0] in ['.','-','/',' ']:
        t.value = DateSeperator(t.value[0])
    elif t.value[0] in [':']:
        t.value = TimeSeperator(t.value[0])
    else:
        t.value = PassThroughLit(t.value[0])
    return t


def getLexer():
    return lex.lex()


class FragHandler:
    def __init__(self,fragments):
        self.fragments=fragments

    def gettokens(self):
        return ' '.join([x.getToken() for x in self.fragments])

    def gettokensRng(self,startcount,endcount):
        return ' '.join([x.token for x in self.fragments[startcount:endcount+1]])        

    def getvals(self):
        return [x.val[0] for x in self.fragments]

    def genCustomLits(self,existingLits,maxlit):
        for x in self.fragments:
            if x.getToken() == 'CUSTOMLIT':
                if x.val in existingLits:
                    x.token = existingLits[x.val]
                else:
                    existingLits[x.val] = 'CUSTOMLIT' + str(maxlit)
                    x.token = existingLits[x.val]
                    maxlit += 1
        return maxlit

    def hasDayInWeek(self):
        return 'DAYINWEEK' in [x.getToken() for x in self.fragments]

def doLex(utf8string,cLocale):

    l = lex.lex()
    l.input(utf8string)
    fragments = []
    
    while True:
        val = l.token()
        if not val:
            break
        else:
            fragments.append(val.value)

    return FragHandler(fragments)
    #return ' '.join([x.token for x in fragments]),[x.val[0] for x in fragments]
    #ret = [x.genParseObject(cLocale) for x in fragments]
    #ret.append(StringEnd())
    #return ret

def generateDateParser(cLocale):
    l = cLocale
    vals = []

    datep = [
        And(doLex(DateFormat.createDateInstance(DateFormat.SHORT,l).toPattern().encode('utf-8'),l)),
        And(doLex(DateFormat.createDateInstance(DateFormat.MEDIUM,l).toPattern().encode('utf-8'),l)),
        And(doLex(DateFormat.createDateInstance(DateFormat.LONG,l).toPattern().encode('utf-8'),l))
        ]

    timep = [
        And(doLex(DateFormat.createTimeInstance(DateFormat.SHORT,l).toPattern().encode('utf-8'),l)),
        And(doLex(DateFormat.createTimeInstance(DateFormat.MEDIUM,l).toPattern().encode('utf-8'),l)),
        And(doLex(DateFormat.createTimeInstance(DateFormat.LONG,l).toPattern().encode('utf-8'),l))
        ]

    datetimep = []

    for x in datep:
        for y in timep:
            datetimep.append(x + y)

    datep = [x+StringEnd() for x in datep]
    timep = [x+StringEnd() for x in timep]

    final = datep + timep + datetimep
    return Or(final)
    

def generateDateParsers():
    res = {}
    alllocales = Locale('').getAvailableLocales()
    for lkey in alllocales.keys():
        vals = []
        l = alllocales[lkey]
        res[str(l)] = generateDateParser(l)
    return res


