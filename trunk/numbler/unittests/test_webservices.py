#!/usr/bin/env python

# unittests for web services

from twisted.trial import unittest
from numbler.server import sheet,parser,engine,cell,account
from numbler.server.colrow import Col,Row
from numbler.server.exc import *
from numbler.sdk import api
from xml.dom.minidom import parseString
from xml import xpath
from numbler.server.sslib.utils import alphaguid16,alphaguid20,guid16
from xml.sax.saxutils import XMLGenerator
from numbler.server import localedb

eng = engine.Engine.getInstance()
eng.ssdb.log = None


ghost = 'hali'
gport = 8080

def getNewUser():
    return alphaguid16() + '@numbler.com'


testbigrequest = False



class FaultRequestGenerator:
    """
    generate bad XML for error testing.
    """

    def __init__(self,sheetUID):
        self.cells = []
        self.sheetUID = sheetUID

        # set the flags to manipulate the test
        self.skipguid = False
        self.skipCol = False
        self.skipRow = False
        self.skipFormula = False
        self.badxml = False
        

    def addCell(self,col,row,formula):
        if type(col) is int:
            col = translatecol(col)
            
        self.cells.append((col,str(row),str(formula)))

    def generateXML(self,output):

        gen = XMLGenerator(output,"UTF-8")
        gen.startDocument()
        gen.startElement("xml",{});

        if self.skipguid:
            gen.startElement("sheet",{})
        else:
            gen.startElement("sheet",{'guid':self.sheetUID})

        for cellattrs in [{'col':val[0],'row':val[1],'formula':val[2]} for val in self.cells]:
            if self.skipCol:
                del cellattrs['col']
            if self.skipRow:
                del cellattrs['row']
            if self.skipFormula:
                del cellattrs['formula']
            
            gen.startElement("cell",cellattrs)
            gen.endElement("cell")
        gen.endElement("sheet")
        if not self.badxml:
            gen.endElement("xml")
        gen.endDocument()

    def dumpxml(self):
        import StringIO
        writer = StringIO.StringIO()
        self.generateXML(writer)
        writer.seek(0)
        return writer.read()


class webservicesTestCase(unittest.TestCase):
    

    testuser = alphaguid16() + '@numbler.com'

    sheets = {
        'testcellprivate':1,
        'testcellbadapi':1,
        'publicsheet':1,
        'privatesheet':1,
        'formulatest':1,
        'getallcells':1,
        'getcellrange':1,
        'noresponsewanted':1,
        'testbaddattrs':1,
        'multisheet1':1,
        'multisheet2':1,
        'bigsheettest':1,
        'testdeletesheet':1,
        'testdeletesheetrng':1,
        'testgetcolrange':1,
        'testgetrowrange':1,
        'testdelcolrange':1,
        'testdelrowrange':1,
        'testbadrangesheet':1
        }


    def setUp(self):
        """ set up the basic account infrastructure """
        try:
            self.principal = account.lookupAccount(self.testuser,self.testuser)
        except AccountNotFound,e:
            self.principal,existingsheets = account.createAccount(self.testuser,self.testuser,self.testuser,
                                                                  'en_US','America/Chicago')
            self.principal = eng.ssdb.markAccountVerified(self.principal)
            for name in self.sheets:
                self.sheets[name] = sheet.Sheet.getNew(name,self.principal)

        self.locale = localedb.NumblerLocale('en_US','America/Chicago')
        return self.principal.registerForApiAccount()

    def getSheet(self,name):
        return self.sheets[name]

    def createWebCon(self,sheetUid,principal = None,port=gport,secure=False,secret_key=None,api_id=None):
        if not principal:
            principal = self.principal
        if not secret_key:
            secret_key = principal._secret_key
        if not api_id:
            api_id = principal.api_id
        return api.NumblerConnection(sheetUid,api_id,secret_key,ghost,port=port,is_secure=secure)

    def testCellGetPrivate(self):
        """
        test a cell get from a private sheet
        """
        sht = self.getSheet('testcellprivate')
        con = self.createWebCon(str(sht.getHandle()))
        sht.getCellHandle(Col('D'),4)().setFormula(u'50',self.locale)
        res = con.getCell('D',4)
        #print res.contents,res.error
        doc = parseString(res.contents)
        formulas = xpath.Evaluate('/xml/sheet/cell/@formula',doc)
        self.failUnless(formulas[0].value == u'50')

    def testCellGetBadApi(self):
        """
        test a cell get from a private sheet
        with a bad api_id
        """
        sht = self.getSheet('testcellbadapi')
        con = self.createWebCon(str(sht.getHandle()),api_id=45)
        res = con.getCell('D',4)
        #print res.contents
        self.failUnless(res.error)
        code,message,resource = res.getError()
        self.failUnless(int(code) == 4004)


    def testCellGetBadSignature(self):
        """
        test getting a cell with a badly signed header (caused
        by a corrupted secret key)
        """
        sht = self.getSheet('testcellbadapi')
        # screw with the secret key
        con = self.createWebCon(str(sht.getHandle()),secret_key='45')
        res = con.getCell('D',4)
        self.failUnless(res.error)
        code,message,resource = res.getError()
        self.failUnless(int(code) == 4003)
        
    def testCellGetPublicSheet(self):
        """
        test access to a public sheet by account which is not
        the owner
        """
        sht = self.getSheet('publicsheet')
        sht.getCellHandle(Col('D'),4)().setFormula(u'50',self.locale)
        self.principal.makeSheetPublic(str(sht.getHandle()))

        username = getNewUser()
        newp = eng.ssdb.markAccountVerified(account.createAccount(username,username,username,'en_US','America/Chicago')[0])
        newp.registerForApiAccount()
        con = self.createWebCon(str(sht.getHandle()),newp)
        res = con.getCell('D',4)
        #print 'GetPublicSheet:',res.contents
        doc = parseString(res.contents)
        formulas = xpath.Evaluate('/xml/sheet/cell/@formula',doc)
        self.failUnless(formulas[0].value == u'50')        


    def testCellGetPrivateSheetNotInvited(self):
        """
        verify that an account not authorized to write to a sheet
        gets an accessed denied error
        """
        sht = self.getSheet('privatesheet')
        sht.getCellHandle(Col('D'),4)().setFormula(u'50',self.locale)

        username = getNewUser()
        newp = eng.ssdb.markAccountVerified(account.createAccount(username,username,username,'en_US','America/Chicago')[0])
        newp.registerForApiAccount()
        con = self.createWebCon(str(sht.getHandle()),newp)
        res = con.getCell('D',4)
        doc = parseString(res.contents)
        #print res.contents
        self.failUnless(res.error)
        code,message,resource = res.getError()
        self.failUnless(int(code) == 4001)

    def testValidPostDataResponse(self):
        """
        send data to the server and validate that you received
        a valid response with the right formulas
        """
        sht = self.getSheet('formulatest')
        con = self.createWebCon(str(sht.getHandle()))
        updater = con.newCellUpdater()
        updater.addCell('A',8,'=SUM(A1:A7)')
        updater.addCell('b',8,'=SUM(B1:B7)')
        updater.addCell('c',8,'=SUM(C1:C7)')
        updater.addCell('d',8,'=SUM(A:C)')
        res = con.sendCells(updater)
        self.failUnless(not res.error)

        updater = con.newCellUpdater()
        updater.addCell('A',1,20)
        updater.addCell('A',3,50)
        res = con.sendCells(updater)
        #print res.contents
        self.failUnless(not res.error)        

        # verify computed data
        doc = parseString(res.contents)
        self.failUnless(xpath.Evaluate('/xml/sheet/cell[@col="a" and @row="8"]/@value',doc)[0].value == u'70')
        self.failUnless(xpath.Evaluate('/xml/sheet/cell[@col="d" and @row="8"]/@value',doc)[0].value == u'140')
        

    def testMissingXmlAttributes(self):
        """
        run a series of test missing XML attributes

        missing col
        missing row
        missing guid
        missing formula
        
        """
        def populateUpdater(updater):
            updater.addCell('A',1,20)
            updater.addCell('A',3,50)        
            updater.addCell('A',8,'=SUM(A1:A7)')
            updater.addCell('b',8,'=SUM(B1:B7)')
            updater.addCell('c',8,'=SUM(C1:C7)')
            updater.addCell('d',8,'=SUM(A:C)')            
        
        sht = self.getSheet('testbaddattrs')
        con = self.createWebCon(str(sht.getHandle()))
        updater = FaultRequestGenerator(str(sht.getHandle()))
        populateUpdater(updater)
        updater.skipguid = True
        res = con.sendCells(updater)
        self.failUnless(res.error)
        doc = parseString(res.contents)
        code = xpath.Evaluate('/error/code',doc)
        self.failUnless(code[0].firstChild.nodeValue == '4005')

        updater = FaultRequestGenerator(str(sht.getHandle()))
        populateUpdater(updater)
        updater.skipCol = True
        res = con.sendCells(updater)
        self.failUnless(res.error)
        doc = parseString(res.contents)        
        code = xpath.Evaluate('/error/code',doc)
        self.failUnless(code[0].firstChild.nodeValue == '4005')

        updater = FaultRequestGenerator(str(sht.getHandle()))
        populateUpdater(updater)
        updater.skipRow = True
        res = con.sendCells(updater)
        self.failUnless(res.error)
        doc = parseString(res.contents)        
        code = xpath.Evaluate('/error/code',doc)
        #print res.contents
        self.failUnless(code[0].firstChild.nodeValue == '4005')

        updater = FaultRequestGenerator(str(sht.getHandle()))
        populateUpdater(updater)
        updater.skipFormula = True
        res = con.sendCells(updater)
        self.failUnless(res.error)
        doc = parseString(res.contents)        
        code = xpath.Evaluate('/error/code',doc)
        self.failUnless(code[0].firstChild.nodeValue == '4005')                        

        # test general 500 error (send bogus xml)
        updater = FaultRequestGenerator(str(sht.getHandle()))
        populateUpdater(updater)
        updater.badxml = True
        #print updater.dumpxml()
        res = con.sendCells(updater)
        self.failUnless(res.error)
        doc = parseString(res.contents)        
        code = xpath.Evaluate('/error/code',doc)
        self.failUnless(code[0].firstChild.nodeValue == '5000')                        
        


    def testMultiSheetPost(self):
        """
        post data to multiple sheets and verify that a formula
        was correctly calculated across many sheets
        """
        sht1 = self.getSheet('multisheet1')
        sht2 = self.getSheet('multisheet2')
        con1 = self.createWebCon(str(sht1.getHandle()))        
        updater1 = con1.newCellUpdater()
        updater1.addCell('A',1,'=' + str(sht2.getHandle()) + '!A1')
        updater1.addCell('B',2,'=' + str(sht2.getHandle()) + '!A2')
        res = con1.sendCells(updater1)
        #print res.contents

        con2 = self.createWebCon(str(sht2.getHandle()))
        updater2 = con2.newCellUpdater()
        updater2.addCell('A',1,'25')
        updater2.addCell('A',2,'50')
        res = con2.sendCells(updater2)
        #print res.contents

        res = con1.getAllCells()
        #print res.contents

        
    def testBadFormula(self):
        """
        test posting a bad formula to a sheet and that it is handled well
        """

        sht = self.getSheet('testbaddattrs')
        con = self.createWebCon(str(sht.getHandle()))
        updater = con.newCellUpdater()
        updater.addCell('A',8,'=SUM(34,PI(,23,-99')
        res = con.sendCells(updater)
        #print 'bad formula\n',res.contents,res.error
        self.failUnless(not res.error)


    def testBadColRef(self):
        """
        send an invalid column and handle the error
        """

        sht = self.getSheet('testbaddattrs')
        con = self.createWebCon(str(sht.getHandle()))
        updater = con.newCellUpdater()
        updater.addCell('ZZZ',90,'90')
        res = con.sendCells(updater)
        #print 'badcolreftest',res.contents
        self.failUnless(res.error)        

    def testBadRowRef(self):
        """
        send a bad row ref and handle the error
        """
        sht = self.getSheet('testbaddattrs')
        con = self.createWebCon(str(sht.getHandle()))
        updater = con.newCellUpdater()
        updater.addCell('A',90000,'90')
        res = con.sendCells(updater)
        self.failUnless(res.error)

    def testBadCellRangeGet(self):
        """
        test a bogus cell request... seomthing like ZZ900000
        """
        sht = self.getSheet('testbaddattrs')        
        con = self.createWebCon(str(sht.getHandle()))
        res = con.getCellRange('EE',50000,'ZZZ',100000)
        doc = parseString(res.contents)
        self.failUnless(res.error)        


    def testBadCellGet(self):
        sht = self.getSheet('testbaddattrs')        
        con = self.createWebCon(str(sht.getHandle()))
        res = con.getCell('D',10000000000)
        #print res.contents
        self.failUnless(res.error)
        res = con.getCell('ZZ',1000)
        #print res.contents
        self.failUnless(res.error)        

    def testGiganticCellRequest(self):
        """
        test sending a huge number of cells to a sheet
        """
        if not testbigrequest:
            return
        
        sht = self.getSheet('bigsheettest')        
        con = self.createWebCon(str(sht.getHandle()))
        updater = con.newCellUpdater()        
        print 'start generating cells'
        for i in range (1,256):
            for j in range(100,500):
                updater.addCell(i,j,alphaguid16())
        print 'done generating cells'
        res = con.sendCells(updater)
        print res.contents
        doc = parseString(res.contents)
        count = xpath.Evaluate('/xml/sheet/@changedCells',doc)
        print count[0].value
        self.failUnless(count[0].value == u'102000')

    def testNoResponseWanted(self):
        """
        test that the server didn't send back any cell changes
        if the user did not ask for them

        """
        sht = self.getSheet('noresponsewanted')
        con = self.createWebCon(str(sht.getHandle()))
        updater = con.newCellUpdater()
        updater.addCell('A',1,'34')
        updater.addCell('A',2,'34')
        updater.addCell('C',4,'34')                
        updater.addCell('A',8,'=SUM(A1:A7)')
        updater.addCell('b',8,'=SUM(B1:B7)')
        updater.addCell('c',8,'=SUM(C1:C7)')
        updater.addCell('d',8,'=SUM(A:C)')
        res = con.sendCells(updater,False)
        #import pdb
        #pdb.set_trace()                
        doc = parseString(res.contents)
        cells = xpath.Evaluate('/xml/sheet/cell',doc)
        self.failUnless(len(cells) == 0)
        count = xpath.Evaluate('/xml/sheet/@changedCells',doc)
        print 'testNoResponseWanted: ',count[0].value,res.contents
        self.failUnless(count[0].value == u'7');

    def testGetAllCells(self):
        """
        verify that I am able to retrieve all cells in a document
        """
        sht = self.getSheet('getallcells')
        con = self.createWebCon(str(sht.getHandle()))
        # put stuff in the sheet
        sht.getCellHandle(Col('D'),4)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('A'),5)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('A'),40)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('Z'),5)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('I'),9)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('BB'),1000)().setFormat("{background-color:blue}")
        sht.getCellHandle(Col('EE'),1000)().setFormat("{background-color:blue}")
        res = con.getAllCells()
        #print res.contents
        doc = parseString(res.contents)        
        cells = xpath.Evaluate('/xml/sheet/cell',doc)

        self.failUnless(len(cells) == 5)        
        
    def testGetCellRange(self):
        """
        verify the ability to retrieve a range of cells
        """
        sht = self.getSheet('getcellrange')
        sht.getCellHandle(Col('D'),4)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('A'),5)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('A'),40)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('Z'),5)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('I'),9)().setFormula(u'50',self.locale)
        con = self.createWebCon(str(sht.getHandle()))
        res = con.getCellRange(1,1,10,10)
        doc = parseString(res.contents)
        cells = xpath.Evaluate('/xml/sheet/cell',doc)
        self.failUnless(len(cells) == 3)

    def testDeleteCell(self):
        """
        verify ability to delete a single cell on a sheet
        that we have write privileges
        """
        sht = self.getSheet('testdeletesheet')
        con = self.createWebCon(str(sht.getHandle()))
        updater = con.newCellUpdater()
        updater.addCell('A',1,'25')
        updater.addCell('b',5,'50')
        updater.addCell('c',9,'75')
        updater.addCell('d',11,'100')
        updater.addCell('A',22,'=SUM(1:11)')
        res = con.sendCells(updater)
        #print res.contents
        self.failUnless(not res.error)

        res = con.deleteCell('b','5',False)
        #print res.contents
        doc = parseString(res.contents)
        count = xpath.Evaluate('/xml/sheet/@changedCells',doc)
        print '*** count is',count[0].value,type(count[0].value)
        self.failUnless(count[0].value == u'2')
        
        res = con.deleteCell('a','1')
        print 'after delting a1:',res.contents
        doc = parseString(res.contents)
        cells = xpath.Evaluate('/xml/sheet/cell',doc)
        #import time
        #time.sleep(100000)

        self.failUnless(len(cells) == 2)        

        # verify the number of cells left over
        res = con.getCellRange(1,1,100,100)
        #print res.contents
        doc = parseString(res.contents)
        cells = xpath.Evaluate('/xml/sheet/cell',doc)
        self.failUnless(len(cells) == 3)       
    

    def testDeleteCellRange(self):
        """
        verify the ability to delete a cell range on a sheet
        that we have write priviledges
        """
        sht = self.getSheet('testdeletesheetrng')
        con = self.createWebCon(str(sht.getHandle()))
        updater = con.newCellUpdater()
        updater.addCell('A',2,'25')
        updater.addCell('b',5,'50')
        updater.addCell('c',9,'75')
        updater.addCell('d',11,'100')        
        con.sendCells(updater)
        #import pdb
        #pdb.set_trace()        

        res = con.deleteCellRange(1,1,100,100,False)
        doc = parseString(res.contents)
        print res.contents
        count = xpath.Evaluate('/xml/sheet/@changedCells',doc)
        # this isn't quite right because we get a count of the cell handles back instead
        # of the real cells.  a bug has been logged.
        self.failUnless(count[0].value == u'6')

    def testDeleteEntireSheet(self):
        """
        test that we get an appropriate error code back when someone
        attempts to delete an entire sheet (not supported)
        """
        # verify forbidden response
        sht = self.getSheet('testdeletesheetrng')
        con = self.createWebCon(str(sht.getHandle()))
        res = api.Response(con.makeRequest('DELETE','/'.join([con.sheetUID,'API'])))
        #print res.contents
        self.failUnless(res.response.status == 403);        
        pass

    def testGetFromNonExistantSheet(self):
        """
        attempt an operation on a non existant sheet
        """
        bogusguid = guid16()
        con = self.createWebCon(bogusguid)
        res = con.getAllCells()
        #print res.contents
        self.failUnless(res.response.status == 404)

    def testSSL(self):
        """
        do a cell fetch via SSL
        """
        sht = self.getSheet('testcellprivate')
        con = self.createWebCon(str(sht.getHandle()),port=8443,secure=True)
        sht.getCellHandle(Col('AA'),30454)().setFormula(u'50',self.locale)
        res = con.getCell('AA',30454)
        doc = parseString(res.contents)
        formulas = xpath.Evaluate('/xml/sheet/cell/@formula',doc)
        self.failUnless(formulas[0].value == u'50')        
        
    def testGetRowRange(self):
        """
        get a range of cells based on a row range
        """
        sht = self.getSheet('testgetrowrange')
        sht.getCellHandle(Col('D'),4)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('A'),5)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('A'),40)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('Z'),5)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('I'),9)().setFormula(u'50',self.locale)
        con = self.createWebCon(str(sht.getHandle()))
        res = con.getRowRange(1,10)
        doc = parseString(res.contents)
        cells = xpath.Evaluate('/xml/sheet/cell',doc)
        self.failUnless(len(cells) == 4)

    def testGetColRange(self):
        """
        get a range of cells based on a column range
        """
        sht = self.getSheet('testgetcolrange')
        sht.getCellHandle(Col('D'),4)().setFormula(u'25',self.locale)
        sht.getCellHandle(Col('A'),5)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('A'),40)().setFormula(u'100',self.locale)
        sht.getCellHandle(Col('Z'),5)().setFormula(u'125',self.locale)
        sht.getCellHandle(Col('I'),9)().setFormula(u'=SUM(125,125)',self.locale)      
        con = self.createWebCon(str(sht.getHandle()))
        res = con.getColRange('B','J')
        doc = parseString(res.contents)
        cells = xpath.Evaluate('/xml/sheet/cell',doc)
        self.failUnless(len(cells) == 2)        
    

    def testDelRowRange(self):
        """
        delete a range of cells based on a row range
        """
        sht = self.getSheet('testdelrowrange')
        sht.getCellHandle(Col('D'),4)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('A'),5)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('A'),40)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('Z'),5)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('I'),9)().setFormula(u'50',self.locale)
        con = self.createWebCon(str(sht.getHandle()))
        res = con.deleteRowRange(1,10)
        res = con.getAllCells()
        doc = parseString(res.contents)
        cells = xpath.Evaluate('/xml/sheet/cell',doc)
        self.failUnless(len(cells) == 1)

    def testDelColRange(self):
        """
        delete a range of cells based on a column range
        """
        sht = self.getSheet('testdelcolrange')
        sht.getCellHandle(Col('D'),4)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('A'),5)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('A'),40)().setFormula(u'50',self.locale)
        sht.getCellHandle(Col('Z'),5)().setFormula(u'=SUM(B:Y)',self.locale)
        sht.getCellHandle(Col('EE'),1000)().setFormula(u'=SUM(B:Z)',self.locale)
        sht.getCellHandle(Col('H'),9)().setFormula(u'99',self.locale)
        sht.getCellHandle(Col('J'),9)().setFormula(u'99',self.locale)
        con = self.createWebCon(str(sht.getHandle()))
        res = con.deleteColRange('D','I')
        doc = parseString(res.contents)
        print res.contents
        cells = xpath.Evaluate('/xml/sheet/cell',doc)
        self.failUnless(len(cells) == 4)
        res = con.getAllCells()
        doc = parseString(res.contents)
        cells = xpath.Evaluate('/xml/sheet/cell',doc)
        print res.contents
        self.failUnless(len(cells) == 5)

    def testGetBadRowRange(self):
        sht = self.getSheet('testbadrangesheet')
        con = self.createWebCon(str(sht.getHandle()))
        res = con.getRowRange(-1,3)
        self.failUnless(res.error)
        res = con.getRowRange(1,1000000000)
        self.failUnless(res.error)

    def testGetBadCellRange(self):
        sht = self.getSheet('testbadrangesheet')
        con = self.createWebCon(str(sht.getHandle()))
        res = con.getColRange('A','QQ')
        self.failUnless(res.error)

    def testDelBadsRowRange(self):
        sht = self.getSheet('testbadrangesheet')
        con = self.createWebCon(str(sht.getHandle()))
        res = con.deleteRowRange(1,100000)
        self.failUnless(res.error)

    def testDelBadColRange(self):
        sht = self.getSheet('testbadrangesheet')
        con = self.createWebCon(str(sht.getHandle()))
        res = con.deleteColRange('Z','QQ')
        self.failUnless(res.error)        


##suite = unittest.makeSuite(webservicesTestCase)

##def main():
##    t = unittest.TextTestRunner()
##    t.run(suite)


##if __name__ == '__main__': main()
    
