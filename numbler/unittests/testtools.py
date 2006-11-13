# (C) Numbler LLC 2006
# See LICENSE for details.

from numbler.server import sheet,parser,engine,cell,account
from numbler.server.colrow import Col,Row
from numbler.server.exc import *

from twisted.trial import unittest
#import unittest
from numbler.server import localedb
from numbler.server.littools import LitNode
from decimal import *

from twisted.python import log,failure
import sys
from twisted.internet.defer import DeferredList
from twisted.internet import defer
from twisted.internet.defer import FirstError

class accountShell:
    locale = None

eng = engine.Engine.getInstance()

import sys
sys.setrecursionlimit(5000)

class sheetTester(unittest.TestCase):
    """
    generate test class for a sheet test case.  A sheet
    should be a class variable like this:

    sheets =
    [
    {
    'name':'booya',
    'cells': [
    ("a1": "Plus"),
    ("b1": "5"),
    ("c1": "10"),
    ("d1": "=b1+c1")
    ],
    'styles' : [
    ("a1": {u'background-color': u'#cc0000'})
    ],
    'colprops' : [
    ("g": {u'background-color': u'#cc0000'})
    ],
    'rowprops' : [
    (45: {u'background-color': u'#cc0000'})
    ]    
    }
    ]
    """

    testuser = '__sheettestacc'
    sheets = []
    
    def setUp(self):
        """ set up the basic account infrastructure """
        try:
            self.principal = account.lookupAccount(self.testuser,self.testuser)
        except AccountNotFound,e:
            self.principal,existingsheets = account.createAccount(self.testuser,self.testuser,self.testuser,
                                                                  'en_US','America/Chicago')
            self.principal = eng.ssdb.markAccountVerified(self.principal)
            self.locale = localedb.NumblerLocale('en_US','America/Chicago')

        # create the sheets for this test run
        self.sheetHandles = {}
        for sheetdata in self.sheets:
            name = sheetdata['name']
            sht = sheet.Sheet.getNew(name,self.principal)
            #print '*** new sheet is ***',str(sht.getHandle())
            self.sheetHandles[name] = sht.getHandle()
            self.sheetHandles[name].attach(self)
            cells = sheetdata.get('cells')
            if cells:
                for cellkey,cellvalue in cells:
                    cl = cell.CellHandle.parse(sht.getHandle(),cellkey).getCell()
                    cl.setFormula(cellvalue,self.principal.locale,notify=False)
            styles = sheetdata.get('styles')
            if styles:
                for cellkey,formatInfo in styles:
                    cl = cell.CellHandle.parse(sht.getHandle(),cellkey).getCell()
                    cl.setFormat(formatInfo)
            colprops = sheetdata.get('colprops')
            if colprops:
                for key,format in colprops:
                    prop = sht.getColProp(int(key),20) # default width
                    prop.setFormat(format)
                    sht.saveColumnProps(prop)
            rowprops = sheetdata.get('rowprops')
            if rowprops:
                for key,format in rowprops:
                    prop = sht.getRowProp(int(key),20) # default hight
                    prop.setFormat(format)
                    sht.saveRowProps(prop)

        self.updateSet = set()

    def update(self,*args,**kwarsg):
        self.updateSet.update(args[1])

    def tearDown(self):
        """ cleanup.  Note that we must return a deferred here in order for the delete to run! """

        self.updateSet = set()
        d = DeferredList([eng.ssdb.deleteSheet(str(self.sheetHandles[key])) for key in self.sheetHandles.keys()])
        return d
        
    def checkImpliedStyle(self,cellI,expected):
        f = cellI.getFormat()
        self.failUnless('__sht' in f);
        self.failUnless(f['__sht'],expected)

    def checkNoImplStyle(self,cellI):
        f = cellI.getFormat()
        if f:
           self.failUnless('__sht' not in f)

    def getCell(self,shtH,cellkey):
        return cell.CellHandle.parse(shtH,cellkey)

    def value(self,shtH,cellkey):
        return self.getCell(shtH,cellkey)().getValue()

    def getFormula(self,shtH,cellkey):
        return self.getCell(shtH,cellkey)().getFormula()

    def getFormat(self,shtH,cellkey):
        return self.getCell(shtH,cellkey)().getFormat()        

    def setFormula(self,shtH,cellkey,value):
        self.getCell(shtH,cellkey)().setFormula(value,shtH().ownerPrincipal.locale)

    def dispvalue(self,shtH,cellkey):
        val = self.getCell(shtH,cellkey)().getData()
        return val['text']

    def checkException(self,shtH,cellkey,exceptionType):
        e  = None
        try:
            e = self.getCell(shtH,cellkey)().getValue(1)
        except Exception,e:
            print 'checkException: unhandled error'
            raise e
        self.failUnless(e is not None)
        # if this is going to fail tell us why
        if not isinstance(e,exceptionType):
            print '** getValue returned %s; expected %s' % (e,exceptionType)
        self.failUnless(isinstance(e,exceptionType))
        
        
    def checkNumResults(self,arg,expected):
        if len(self.updateSet) != expected:
            self.fail("length of update set %d does not match the expected number of results %d"
                       % (len(self.updateSet),expected))

    def verifyNotification(self,arg,sht,expected):
        ulist = list(self.updateSet)
        for cellId,val in expected:
            cellH = self.getCell(sht,cellId)
            if cellH in self.updateSet:
                found = ulist[ulist.index(cellH)]
                self.failUnless(found().getValue() == val,"lookup for value %s, found %s" % (val,found().getValue()))
            else:
                self.fail("%s not in notification list" % cellId)
                

        
    def verifyResults(self,arg,sht,expected):
        for cellId,val in expected:
            found = self.value(sht,cellId)
            if found != val:
                print 'looking for value in %s; expecting %s.  found %s' % (cellId,val,found)
            self.failUnless(found == val)

    def verifyFormulas(self,arg,sht,expected):
        #print 'entering verifyFormulas'
        for cellId,val in expected:
            found = self.getFormula(sht,cellId)
            if found != val:
                print 'looking for value in %s; expecting %s.  found %s' % (cellId,val,found)
                #import pdb
                #pdb.set_trace()
            self.failUnless(found == val)

    def verifyStyles(self,arg,sht,expected):
        for cellId,val in expected:
            found = self.getFormat(sht,cellId)
            for key in val.keys():
                if key not in found:
                    print 'looking for value in %s; expecting %s.  found %s' % (cellId,val,found)                    
                    self.fail("%s does not exist in style dictionary" % key)
                else:
                    if found[key] != val[key]:
                        print 'looking for value in %s; expecting %s.  found %s' % (cellId,val,found)
                        self.fail("%s != %s" % (found[key],val[key]))

    def verifyColStyles(self,arg,sht,expected):
        return self.verifyColRowStyles(arg,sht,expected,True)

    def verifyRowStyles(self,arg,sht,expected):
        return self.verifyColRowStyles(arg,sht,expected,False)        

    def verifyColRowStyles(self,arg,sht,expected,col=True):
        for key,val in expected:
            prop = col == True and sht().getColProp(int(key),20) or sht().getRowProp(int(key),20)
            existingstyle = prop.getFormat()
            if val == u'':
                if existingstyle != u'':
                    self.fail('expecting an empty format, found %s' % existingstyle)
            else:
                for key in val.keys():
                    if key not in existingstyle:
                        self.fail("%s does not exist in current format" % key)
                    else:
                        if existingstyle[key] != val[key]:
                            self.fail('%s != %s' % (existingstyle[key],val[key]))
        

    # default errback
    def defErrB(self,err):
        print '*** error occured in %s: %s' % (self.__class__.__name__,err)
        self.failUnless(err is None)
    
    def dumpResults(self,arg):
        """
        dump any updates that have come through
        """
        
        print '*** dumping results: '
        for cellH in self.updateSet:
            print cellH


    def emptyCaches(self):
        """
        empty all the caches in the system to force reload from the database.
        """
        while 1:
            try:
                val = sheet.Sheet._sheets.popitem()
                #print 'emptyCaches: removing',val
            except KeyError:
                break
        while 1:
            try:
                val = cell.Cell._cells.popitem()
                #print 'emptyCaches: removing',val                
            except KeyError:
                break

        sheet.SheetHandle.purge()
                


class formulaTestCase(unittest.TestCase):
    """ supports operations on temporary sheets"""

    # default locale str - override for language specific tests
    localestr = 'en_US'
    localeobj = localedb.NumblerLocale(localestr,'CST')

    def getParsed(self,formula):
        # create a temporary sheet with a fake account
        tempH = sheet.Sheet.getTemp(accountShell())
        tempH.ownerPrincipal.locale = self.localeobj
        return eng.parser.parse(tempH.getHandle(),formula)

    def expectParseFailure(self,formula,expected):
        try:
            self.getParsed(formula)
        except Exception,e:
            pass
        self.failUnless(e is not None)
        self.failUnless(isinstance(e,expected))

    def checkException(self,astobj,exceptionType):
        """
        return exception object that you can test against.
        this is only useful for negative scenarios
        """

        e = None
        try:
            astobj.eval(1)
        except Exception,e:
            pass
        self.failUnless(e is not None)
        self.failUnless(isinstance(e,exceptionType))


    def parseLiteralNumber(self,literalVal):
        """
        send a literal number to a cell and verify that it parses correctly
        """
        ctx = localedb.ParseCtx()
        try:
            ret = localedb.LocaleParser.getInstance(self.localestr).parse(ctx,literalVal)
            if isinstance(ret,LitNode):
                return ret.eval()
            elif type(ret) in (float,long,int):
                return ret
            else:
                return literalVal

        except LiteralConversionException,e:
            return literalVal


    def convertToUserDecimal(self,numberVal):
        """
        convert a decimal value to the format that would be viewed by the user
        """
        return self.localeobj.defDecimalFormat(numberVal)

    
    def roundedResult(self,val):
        """ return a rounded string for test assertion purposes """
        return str(Decimal(str(val)).quantize(Decimal('.0001'),rounding=ROUND_HALF_UP))


from numbler.sheetlock import getRect,sheetlock,lockManager

class lockingTestCase(unittest.TestCase):

    def setUp(self):
        self.lockmanager = lockManager(900)
        self.clientHandles = []
        self.shtH = sheet.Sheet.getTemp(accountShell())

    def tearDown(self):
        """ release all locks """
        #print 'tearDown called'
        for ch in self.clientHandles:
            self.lockmanager.onDisconnect(None,ch)

    def releaseAll(self,clientHandle):
        self.lockmanager.onDisconnect(None,clientHandle)

    def getClientHandle(self):
        self.clientHandles.append(len(self.clientHandles)+1)
        return self.clientHandles[-1]
    

    def lockRow(self,clientHandle,rowID):
        return getLock(clientHandle,1,rowID,Col.getMax(),rowId)

    def lockCol(self,clientHandle,colID):
        return getLock(clientHandle,colID,1,colID,Row.getMax())

    def getColRect(self,col,spacing=0):
        colID = int(col)
        return getRect(colID,1,colID+spacing,Row.getMax())

    def getRowRect(self,row,spacing=0):
        rowID = int(row)
        return getRect(1,rowID,Col.getMax(),rowID + spacing)
        

    def getLock(self,clientHandle,c1,r1,c2,r2):
        """
        create a lock object and request a lock. this goes through
        a bunch of work to simulate a lock dictionary that would come
        from the UI.
        """
        testrect = getRect(c1,r1,c2,r2)
        # create the lock.
        lockdict = {
            'topleft':{'col':c1,'row':r1},
            'bottomright':{'col':c2,'row':r2},
            'lockduration':3000,
            'user':'bob',
            'rect':{'l':c1,'r':c2,'t':r1,'b':r2}
            }
        newlock = sheetlock(clientHandle,lockdict)
        return self.lockmanager.getLock(newlock),newlock

    def checkExpandedLock(self,lockUID,c1,r1,c2,r2):
        testrect = getRect(int(c1),int(r1),int(c2),int(r2))
        self.checkExpandedLockByRect(lockUID,testrect)

    def checkExpandedLockByRect(self, lockUID,newrect):
        lock = self.lockmanager.lookupLock(lockUID)
        self.failUnless(lock is not None,"failed to find lock for %s" % lockUID)
        self.failUnlessEqual(lock.boundingrect,newrect,
                             'old rect %s does not match new rect %s' % (lock.boundingrect,newrect))
        
    def verifyLockDeleted(self,lockUID):
        self.failUnlessEqual(self.lockmanager.lookupLock(lockUID),None,"lock was not deleted")


eng.ssdb.log = None

def testmain(suitelist):
    """
    pass in alist of suites
    """
    eng.ssdb.log = None # turn off db logging
    log.startLogging(sys.stdout,0)

    suites = [unittest.makeSuite(x) for x in suitelist]
    combined = unittest.TestSuite(suites)
    t = unittest.TextTestRunner()

    from twisted.internet import reactor,defer

    def done(arg):
        reactor.stop()

    d = defer.Deferred()
    d.addCallback(t.run)
    d.addBoth(done)

    reactor.callLater(0,d.callback,combined)
    reactor.run()
