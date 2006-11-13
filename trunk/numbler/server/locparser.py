# (C) Numbler LLC 2006
# See LICENSE for details.

from timelexer import *
import PyICU

def writeascoded(utf8str):
    #return repr(utf8str)[1:-1]
    return utf8str

us_SHORT= 'jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec'
us_SHORT_dict = {'mar': 3, 'feb': 2, 'aug': 8, 'sep': 9, 'apr': 4, 'jun': 6, 'jul': 7, 'jan': 1, 'may': 5, 'nov': 11, 'dec': 12, 'oct': 10}

us_LONG = 'january|february|march|april|may|june|july|august|september|october|november|december'
us_LONG_dict = {'february': 2, 'october': 10, 'march': 3, 'august': 8, 'september': 9, 'may': 5, 'january': 1, 'june': 6, 'april': 4, 'december': 12, 'july': 7, 'november': 11}

monthdictoverride = {
    'or_IN' : 'short',
    'cs_CZ' : 'short',
    'cs' : 'short',
    'or' : 'short',
    'ur' : 'both',
    'ur_PK' : 'both'
    }

existingDateExpressions = {
    'monthday' : 'month datesep INTEGER',
    'monthyear' : 'INTEGER datesep month'
        }

existingTimeExpressions = {
    'medtime' : 'INTEGER TIMESEP INTEGER',
    'longtime' : 'medtime TIMESEP INTEGER'
    }

def findExistingTimeMatch(tokens):
    return findExistingMatch(tokens,existingTimeExpressions)

def findExistingDateMatch(tokens):
    return findExistingMatch(tokens,existingDateExpressions)

def findExistingMatch(tokens,testdict):
    for matcher in testdict.keys():
        val = testdict[matcher]
        #print val,matcher
        if tokens.find(val) == 0:
            return tokens.replace(val,matcher)
    return None

    

def write_monthdict(cLocale):
    """
    generate a dictionary of all the month names
    """

    src = """
monthdict = %s
t_SHORTMONTH = r'(?i)%s'
t_LONGMONTH = r'(?i)%s'
    """    
    monthdict = {}
    smonth = []
    lmonth = []
    x = 1
    sym = DateFormatSymbols(cLocale)
    if str(cLocale)in monthdictoverride and monthdictoverride[str(cLocale)] in ['short','both']:
        smonth = us_SHORT.split('|')
        monthdict.update(us_SHORT_dict)
    else:
        for sm in sym.getShortMonths():
            val= sm.encode('utf-8').lower()
            smonth.append(escapeForRe(val))
            monthdict[val] = x
            x += 1

    x = 1
    if str(cLocale) in monthdictoverride and monthdictoverride[str(cLocale)] in ['long','both']:
        lmonth = us_LONG.split('|')
        monthdict.update(us_LONG_dict)
    else:
        for mm in sym.getMonths():
            val = mm.encode('utf-8').lower()
            lmonth.append(escapeForRe(val))
            monthdict[val] = x
            x += 1

    # check that we don't have months as numbers

    return src % (str(monthdict),writeascoded('|'.join(smonth)),writeascoded('|'.join(lmonth)))


p_monthyearint_src = """
def p_monthyearint(p):
    ' monthyearint : INTEGER datesep INTEGER'
    val1 = int(p[1])
    val2 = int(p[3])
    daybeforemonth = %s
    monthbeforeyear = %s

    if daybeforemonth and val1 < 1000:
        p[0] = DateNode(p.parser.parsectx,month=val2,day=val1)
        p.parser.parsectx.fmt = 'vsmd'
    elif not monthbeforeyear and val1 > 1000:
        p[0] = DateNode(p.parser.parsectx,month=val2,year=val1)
        p.parser.parsectx.fmt = 'vsmy'        
    elif not daybeforemonth and val2 < 1000:
        p[0] = DateNode(p.parser.parsectx,month=val1,day=val2)
        p.parser.parsectx.fmt = 'vsmd'        
    elif monthbeforeyear and val2 > 1000:
        p[0] = DateNode(p.parser.parsectx,month=val1,year=val2)
        p.parser.parsectx.fmt = 'vsmy'                
    else:
        raise LiteralConversionException()        

"""

# monthyearint does a combination of the following:
# day-month (integer) per locale convention
# month (integer) per locale convention

def write_p_monthyearint(frag):
    exp = frag.getvals()
    dayi = exp.index('d')
    monthi = exp.index('M')
    yeari = exp.index('y')
    return p_monthyearint_src % (str(dayi < monthi),str(monthi < yeari))

p_shortdate_src = """
def p_shortdate(p):
    ' shortdate : %s '
    monthasint = %s
    month = p[%s]
    day = int(p[%s])
    year = int(p[%s])

    if monthasint:
        monthint = int(month)
    else:
        monthint = monthdict[month]

    p[0] = DateNode(p.parser.parsectx,day,month=monthint,year=year)
    p.parser.parsectx.fmt = 'sd'
    
"""


def write_p_shortdate(shortf):

    tokens = shortf.gettokens()
    exp = shortf.getvals()
    vals = shortf.getvals()
    mp = shortf.fragments[vals.index('M')]
    
    expectsint = mp.getExpects() == int and True or False
    
    return p_shortdate_src % (tokens,expectsint,
                              vals.index('M')+1,vals.index('d')+1,vals.index('y')+1)

p_mediumdate_src = """
def p_meddate(p):
    ' meddate : %s '
    monthasint = %s
    day = int(p[%s])
    month = p[%s]
    year = int(p[%s])

    if monthasint:
        monthint = int(month)
    else:
        monthint = monthdict[month.lower()]

    p[0] = DateNode(p.parser.parsectx,day,month=monthint,year=year)
    p.parser.parsectx.fmt = 'md'

"""


p_meddate_reduced = """
def p_meddate(p):
    ' meddate : %s '
    dn = p[1]
    %s
    p[0] = dn
    p.parser.parsectx.fmt = 'md'

"""

def write_p_meddate(shortf,medf):
    if medf.gettokens() == shortf.gettokens():
        return ''

    tokens = medf.gettokens()
    vals = medf.getvals()
    reduced = findExistingDateMatch(tokens)
    if reduced:
        # what values don't we have?
        newvals = vals[len(tokens.split(' ')) - len(reduced.split(' ')):]
        newvals[0] = reduced.split(' ')[0]
        #print newvals,reduced
        if 'd' in newvals:
            partial = 'dn.setDay(int(p[%s]))' % (newvals.index('d')+1)
        elif 'y' in newvals:
            partial = 'dn.setYear(int(p[%s]))' %( newvals.index('y')+1)
        return p_meddate_reduced % (reduced,partial)
    else:
        exp = medf.getvals()
        mp = medf.fragments[vals.index('M')]
        
        expectsint = mp.getExpects() == int and True or False

        return p_mediumdate_src % (tokens,expectsint,
                                   vals.index('d')+1,vals.index('M')+1,vals.index('y')+1)    



p_longdate_src = """
def p_longdate(p):
    ' longdate : %s '
    monthasint = %s
    day = int(p[%s])
    month = p[%s]
    year = int(p[%s])

    if monthasint:
        monthint = int(month)
    else:
        monthint = monthdict[month.lower()]

    p[0] = DateNode(p.parser.parsectx,day,month=monthint,year=year)
    p.parser.parsectx.fmt = 'ld'
"""


def write_p_longdate(shortf,medf,longf):
    if shortf.gettokens() == longf.gettokens() or medf.gettokens() == longf.gettokens():
        return ''
    exp = longf.getvals()
    vals = longf.getvals()
    mp = longf.fragments[vals.index('M')]

    expectsint = mp.getExpects() == int and True or False
    
    return p_longdate_src % (longf.gettokens(),expectsint,
                              vals.index('d')+1,vals.index('M')+1,vals.index('y')+1)    


    

p_formaldate_src = """
def p_formaldate(p):
    ''' formaldate : %s '''

    p[0] = p[1]
"""


def write_formaldate(cLocale,shortf,medf,longf):
    st = shortf.gettokens()
    mt = medf.gettokens()
    lt = longf.gettokens()

    output = 'shortdate'
    if mt != st:
        output += '\n                   | meddate'
    if lt != st and lt != mt:
        output += '\n                   | longdate'
    output += '\n   '
    return p_formaldate_src % output

def escapeForRe(lit):
    savelit = []
    for ch in lit:
        #properly escape any regex special characters
        if ch in '\^$.|?*+()\'\"':
            ch = '\\' + ch
        savelit.append(ch)
    return ''.join(savelit)
    

new_lit_src = """
tokens.append('%s')

t_%s = r'%s'

"""

def write_custom_lits(customdict):
    ret = []
    for lit in customdict.keys():
        savelit = escapeForRe(lit)
        ret.append(new_lit_src % (customdict[lit],customdict[lit],writeascoded(savelit)))
    return ''.join(ret)
                  

p_datesep_src = """
def p_datesep(p):
    ''' datesep : SLASH
                | DASH
                | SPACE
                %s
    '''
    
    p[0] = p[1]
"""

def write_date_sep_rule(fraglist,customlits):
    newseps = []
    for x in fraglist:
        toks = x.gettokens().split(' ')
        try:
            i = toks.index('datesep')
            if x.fragments[i].val not in ['/','-',' ']:
                if x.fragments[i].val not in customlits:
                    newlit = 'CUSTOMLIT' + str(len(customlits))
                    customlits[x.fragments[i].val] = newlit
                else:
                    newlit = customlits[x.fragments[i].val]

                if newlit not in newseps:
                    newseps.append(newlit)
        except ValueError:
            pass
    output = ''
    for val in newseps:
        output += '| %s' % (val)
    return p_datesep_src % output


groupseptranslator = {
    '\xc2\xa0' : ' '
    }

def write_decimal_rules(cLocale):
    ret = ['']

    sym = PyICU.DecimalFormatSymbols(cLocale)
    ret.append("t_FRACTION = r'\%s\d*'" % sym.getSymbol(sym.kDecimalSeparatorSymbol).encode('utf-8'))
    ret.append("gdectype = '%s'" % sym.getSymbol(sym.kDecimalSeparatorSymbol).encode('utf-8'))
    ret.append("t_CURRENCY = r'\%s'" % writeascoded(sym.getSymbol(sym.kCurrencySymbol).encode('utf-8')))
    ret.append("t_PERCENT = r'\%s'" % writeascoded(sym.getSymbol(sym.kPercentSymbol).encode('utf-8')))
    groupsep = sym.getSymbol(sym.kGroupingSeparatorSymbol).encode('utf-8')
    if groupsep in groupseptranslator:
        groupsep = groupseptranslator[groupsep]

    # write out the raw group seperator
    if groupsep == "'":
        ret.append('gseptype = "%s"' % groupsep)
    else:
        ret.append("gseptype = '%s'" % groupsep)
    if groupsep == ' ':
        groupsep = '\\ '
    else:
        groupsep = escapeForRe(groupsep)
        
    ret.append("t_COMMAINT = r'\d{1,3}(%s\d{3})+(?!\d)'" % groupsep)

    dsym = PyICU.DateFormatSymbols(cLocale)
    clocksyms = ['am','pm','p','a']
    ampm = dsym.getAmPmStrings()
    for x in ampm:
        x = x.encode('utf-8').lower()
        if x not in clocksyms:
            clocksyms.append(x)
    ret.append("t_CLOCK = r'(?i)%s'" % writeascoded('|'.join(clocksyms)))
    return '\n'.join(ret)


p_medtimeclock_src = """

def p_medtimeclock(p):
    ' medtimeclock : %s '
    t = TimeNode(int(p[%s]),int(p[%s]))
    t.setAMPM(p[%s])
    p[0] = t
"""

p_medtimeclock_reduced_src = """
def p_medtimeclock(p):
    ' medtimeclock : %s '
    t = p[1]
    t.setAMPM(p[%s])
    p[0] = t

"""

def write_medtimeclock(frag):

    tokens = frag.gettokens().split(' ')
    if 'datesep' in tokens:
        for x in range(0,len(tokens)):
            if tokens[x] == 'datesep':
                tokens[x] = 'SPACE'
    if 'CLOCK' not in tokens:
        tokens.append('SPACE')
        tokens.append('CLOCK')

    ampm = tokens.index('CLOCK')
    reduced = findExistingTimeMatch(' '.join(tokens))
    if reduced:
        ampm = reduced.split(' ').index('CLOCK')+1
        return p_medtimeclock_reduced_src % (reduced,ampm)
    else:
        vals = frag.getvals()
        if 'h' in vals:
            hours = vals.index('h')
        else:
            hours = vals.index('H')
        mins = vals.index('m')
        return p_medtimeclock_src % (' '.join(tokens),hours+1,mins+1,ampm+1)

p_longtimeclock_src = """

def p_longtimeclock(p):
    ' longtimeclock : %s '
    t = TimeNode(int(p[%s]),int(p[%s]),int(p[%s]))
    t.setAMPM(p[%s])
    p[0] = t
"""

p_longtimeclock_src_reduced = """

def p_longtimeclock(p):
    ' longtimeclock : %s '
    t = p[1]
    t.setAMPM(p[%s])
    p[0] = t

"""

def write_longtimeclock(medfrag,longfrag):
    try:
        medfrag.getvals().index('s')
    except ValueError:
        frag = longfrag
    else:
        frag = medfrag
    
    tokens = frag.gettokens().split(' ')
    if 'datesep' in tokens:
        for x in range(0,len(tokens)):
            if tokens[x] == 'datesep':
                tokens[x] = 'SPACE'
    if 'CLOCK' not in tokens:
        tokens.append('SPACE')        
        tokens.append('CLOCK')

    ampm = tokens.index('CLOCK')

    reduced = findExistingTimeMatch(' '.join(tokens))
    if reduced:
        # try reducing again... may get another hit
        second = findExistingTimeMatch(reduced)
        if second:
            reduced = second
        ampm = reduced.split(' ').index('CLOCK') + 1
        return p_longtimeclock_src_reduced % (reduced,ampm)
        
    else:    
        vals = frag.getvals()
        if 'h' in vals:
            hours = vals.index('h')
        else:
            hours = vals.index('H')
        mins = vals.index('m')
        secs = vals.index('s')
        return p_longtimeclock_src % (' '.join(tokens),hours+1,mins+1,secs+1,ampm+1)

dayinweek_src = """
tokens.append('DAYINWEEK')

t_DAYINWEEK = r'%s'

"""

def write_dayinweek(cLocale):
    sym  = PyICU.DateFormatSymbols(cLocale)
    days = sym.getShortWeekdays() + sym.getWeekdays()
    return dayinweek_src % writeascoded('|'.join([x.encode('utf-8').lower() for x in days if len(x)]))
    

p_currency_before_str = """
def p_currency(p):
    ''' currency : CURRENCY number
                 | CURRENCY SPACE number
    '''
    p.parser.parsectx.fmt = '$'
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = p[3]

"""

p_currency_after_str = """
def p_currency(p):
    ''' currency : number CURRENCY
                 | number SPACE CURRENCY
    '''
    p.parser.parsectx.fmt = '$'
    p[0] = p[1]

"""

def write_currency(currencypat,cLocale):

    if ';' in currencypat:
        currencypat = currencypat.split(';')[0]

    cindex = currencypat.index('\xc2\xa4')
    if cindex == 0:
        return p_currency_before_str
    else:
        return p_currency_after_str



def genNewLocaleFile(cLocale):

    customLits = {}

    parentdir = __file__[0:__file__.rfind('/')]
    targetdir = '/'.join([parentdir,'locale'])
    fp = open('%s/parser_%s.py' % (targetdir,str(cLocale)),'w+')
    fp.write(open('/'.join([parentdir,'literal_parser.py'])).read())
    fp.write('############################################################\n')
    fp.write('##below is generated code\n')
    fp.write('############################################################\n')

    fp.write(write_monthdict(cLocale))
    fp.write(write_decimal_rules(cLocale))

    frag = doLex(DateFormat.createDateInstance(DateFormat.SHORT,cLocale).toPattern().encode('utf-8'),
                      cLocale)
    mfrag = doLex(DateFormat.createDateInstance(DateFormat.MEDIUM,cLocale).toPattern().encode('utf-8'),
                      cLocale)
    lfrag = doLex(DateFormat.createDateInstance(DateFormat.LONG,cLocale).toPattern().encode('utf-8'),
                      cLocale)

    if frag.hasDayInWeek() or mfrag.hasDayInWeek() or lfrag.hasDayInWeek():
        fp.write(write_dayinweek(cLocale))
    
    
    frag.genCustomLits(customLits,len(customLits))
    mfrag.genCustomLits(customLits,len(customLits))
    lfrag.genCustomLits(customLits,len(customLits))    

    fp.write(write_date_sep_rule((frag,mfrag,lfrag),customLits))
    

    fp.write(write_p_monthyearint(frag))
    fp.write(write_formaldate(cLocale,frag,mfrag,lfrag))
    fp.write(write_p_shortdate(frag))
    fp.write(write_p_meddate(frag,mfrag))
    fp.write(write_p_longdate(frag,mfrag,lfrag))
    #fp.write(write_meddatecustom(cLocale))

    shorttime = doLex(DateFormat.createTimeInstance(DateFormat.SHORT,cLocale).toPattern().encode('utf-8'),
                      cLocale)
    medtime = doLex(DateFormat.createTimeInstance(DateFormat.MEDIUM,cLocale).toPattern().encode('utf-8'),
                      cLocale)
    longtime = doLex(DateFormat.createTimeInstance(DateFormat.LONG,cLocale).toPattern().encode('utf-8'),
                      cLocale)

    shorttime.genCustomLits(customLits,len(customLits))
    medtime.genCustomLits(customLits,len(customLits))
    longtime.genCustomLits(customLits,len(customLits))        


    fp.write(write_medtimeclock(shorttime))
    fp.write(write_longtimeclock(medtime,longtime))
    

    currencypat = PyICU.DecimalFormat.createCurrencyInstance(cLocale).toPattern().encode('utf-8')
    fp.write(write_currency(currencypat,cLocale))


    fp.write(write_custom_lits(customLits))

    fp.write("tokens.append('SPACE')\n")
    fp.close()


