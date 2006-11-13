################################################################################
## (C) Numbler LLC 2006
################################################################################

import sys,traceback

from zope.interface import implements, Interface
from twisted.python.components import registerAdapter
from twisted.internet import reactor,defer,threads

from nevow import athena, inevow, loaders, util,rend,url
from nevow import tags as T

from numbler.server.colrow import Col,Row

from support_pages import NumblerTemplatePage,NumblerTemplatePageBase
from invite import newImportMail,sendMail

from numbler.import_plugins.excelXML import ExcelXMLImporter
from numbler.import_plugins.csvimport import CSVImporter
from numbler.import_plugins.gnumeric import GnumericImporter
from numbler.importwarnings import *
from numbler.account_pages import hasPrincipal


class SheetImport(NumblerTemplatePage):
    addSlash = True
    xmlcontent = 'import.xml'
    title = 'Import your spreadsheets'

    def renderHTTP(self,ctx):
        
        if not hasPrincipal(ctx,inevow.IRequest(ctx).URLPath().parentdir(),'simport'):
            return ''
        return super(SheetImport,self).renderHTTP(ctx)

class ProcessSheetImport(NumblerTemplatePageBase,athena.LivePage):

    #addSlash = True
    xmlcontent = 'procimport.xml'
    title = 'Numbler: importing data'

    headerFactory = loaders.xmlfile('importheader.xml',templateDir='templates',pattern='header')

    def locateMethod(self,ctx,methodName):
        return getattr(self,methodName)

    def render_extrascripts(self,ctx):
        return self.headerFactory

    def render_liveglue(self,ctx,data):
        # extremely ugly code to make sure that athena doesn't import mochikit
        try:
            self.BOOTSTRAP_MODULES.remove('MochiKit')
            return super(ProcessSheetImport,self).render_liveglue(ctx,data)
        finally:
            self.BOOTSTRAP_MODULES.insert(0,'MochiKit')


    def __init__(self,sess):
        NumblerTemplatePageBase.__init__(self)
        athena.LivePage.__init__(self,jsModuleRoot=url.here.parentdir().child('athenajs'))
        self.fileExists = False
        self.importdata = None
        self.sess = sess
        self.filename = None
        self.emailInfo = []

    def filesaver(self,filename,data):
        """ save user submitted spreadsheets for later analysis if a bug occurs """
        from numbler.server.sslib.utils import guid16
        import os

        fp = None
        try:
            fname = '%s%s%s%s%s%s_%s' % (os.sep,'tmp',os.sep,'numbler',os.sep,guid16(),filename)
            print 'saving imported spreadsheet',fname
            fp = open(fname,'w')
            fp.write(data)
            fp.close()
            print 'done saving data'
        except:
            print 'error occurred saving original imported data'



    def beforeRender(self,ctx):
        request = inevow.IRequest(ctx)
        self.urlpath = request.URLPath()

        self.useremail = ctx.arg('useremail')

        arg = request.args.get('uploadfile')
        if arg is not None:
            self.importdata = arg[0]
            self.filename = request.fields['uploadfile'].filename

        
        threads.deferToThread(self.filesaver,self.filename,self.importdata)
        self.fileExists = self.importdata is not None and len(self.importdata)        

    def render_status(self,ctx,data):
        request = inevow.IRequest(ctx)
        
        if self.fileExists:
            return 'Importing your spreadsheet....'
        else:
            return [
                T.div["Oops!  Numbler couldn't find the import file. Did you specify a valid file?"],
                T.br,
                T.div["Please ",
                         T.a(href=request.URLPath().sibling('simport'))['return'],
                         ' to the import page.']]

    def _becomeLive(self):
        # we need to override _becomeLive to do a bunch of disconnect operations
        athena.LivePage._becomeLive(self)
        d = defer.Deferred()
        d.addCallback(self.runImport)
        reactor.callLater(0,d.callback,None)


    ############################################################
    ## import specific
    ############################################################


    def runImport(self,arg):

        if not self.fileExists:
            return
        
        # decide which importer to run
        importFunc = self.importExtensions.get(self.filename[-3:].lower())
        if importFunc:
            importFunc(self)
        else:
            self.extensionsWarning()
            self.defaultImport()

    ############################################################
    ## CSV import
    ############################################################
    def getSheetName(self):
        sheetname = u' new sheet'
        try:
            sheetname = unicode(self.filename[:-4])
        except UnicodeDecodeError,e:
            pass
        return sheetname
            
            
    def startCsvImport(self):
        # ask for the sheetname... try to get it from the filename but bail if not possible
        self.callRemote('importTools.newSheetName',self.getSheetName()).addCallback(self.beginCSV)

    def beginCSV(self,userSpecSheetName):
        self.callRemote('importTools.onStartServerImport')
        self.importer = CSVImporter(self.importdata,userSpecSheetName,self.sess.principal)
        self.generateSheet(None)


    def startXlsImport(self):
        self.callRemote('importTools.newSheetName',self.getSheetName()).addCallback(self.beginXLS)

    def beginXLS(self,userSpecSheetName):
        self.callRemote('importTools.onStartServerImport')
        self.importer = GnumericImporter(self.importdata,userSpecSheetName,self.sess.principal)
        self.generateSheet(None)
    

    ############################################################
    ## XML import
    ############################################################

    def startXmlImport(self):
        self.importer = ExcelXMLImporter(self.importdata,self.sess.principal)
        self.callRemote('importTools.startParse')
        d = defer.Deferred()
        d.addCallbacks(self.parseSuccess,self.parseFailure)
        self.importer.parse(d)

    def fetchSheets(self,arg):
        d = defer.Deferred()
        d.addCallbacks(self.showSheets,self.numSheetError)
        self.importer.numberOfSheets(d)

    def importSheet(self,*args):
        print 'importSheet arguments',args
        if len(args) > 1:
            arg = args[1]
        else:
            arg = args[0]
            
        
        # filter out any worksheets that were not marked as import
        targetsheets = [worksheet[0] for worksheet in arg if worksheet[1]]
        if not len(targetsheets):
            self.noSheetsSelected()            
        else:
            self.importer.setTargetSheets(targetsheets)
            d = defer.Deferred()
            d.addCallbacks(self.styleFinished,self.styleError)
            self.importer.processStyles(d)

    def loadData(self,arg):

        finished = defer.Deferred()
        finished.addCallbacks(self.loadedMetaData,self.metaDataFailure)

        rowdef = defer.Deferred()
        rowdef.addCallback(self.importer.processRows)
        rowdef.chainDeferred(finished)

        coldef = defer.Deferred()
        coldef.chainDeferred(rowdef)
        self.importer.processColumns(coldef)


    def generateSheet(self,arg):
        """ put everything together and generate the sheet. """

        d = defer.Deferred()
        d.addCallbacks(self.sheetGenSuccess,self.sheetGenFailure)
        #print self.importer
        
        self.importer.generateSheet(d)
        
        

    ############################################################
    ## UI handlers
    ############################################################        
    
    def parseSuccess(self,arg):
        self.callRemote('importTools.endParse',True).addCallback(self.fetchSheets)

    def parseFailure(self,arg):
        self.callRemote('importTools.endParse',False)
        
    def showSheets(self,arg):
        if arg == 1:
            d  = self.callRemote('importTools.onStartServerImport');
            d.addCallback(self.importSheet,[[self.importer.sheetnames[0],True]])
        else:
            d = self.callRemote('importTools.multiSheets',self.importer.sheetnames);
            d.addCallback(self.importSheet);
        


    def numSheetError(self,arg):
        d = self.callRemote('importTools.addMsgFailure',
                            u'Unable to find any spreadsheets in the work book.')

    def styleFinished(self,arg):
        d = self.callRemote('importTools.addMsg',
                        u'Processed spreadsheet formatting.')
        d.addCallback(self.loadData)
        

    def styleError(self,arg):
        self.callRemote('importTools.addMsgFailure',
                        u'Numbler encountered an error processing the spreadsheet formatting.')

    def loadedMetaData(self,arg):
        self.callRemote('importTools.addMsg',
                        u'Processed spreadsheet contents').addCallback(self.sendWarnings)

    def metaDataFailure(self,arg):
        self.callRemote('importTools.addMsgFailure',
                        u'Numbler encountered an error processing the spreadsheet contents')

    def sendWarnings(self,arg):
        warnings =  self.importer.warningText()
        if len(warnings):
            self.callRemote('importTools.addWarnings',warnings)
        d = self.callRemote('importTools.addMsg',u'generating new spreadsheet...')
        d.addCallback(self.generateSheet)

    def sheetGenSuccess(self,args):
        uid,name = args
        self.emailInfo.append(args)
        moresheets = self.importer.continueImport()
        self.callRemote('importTools.newSheet',
                        unicode(self.urlpath.sibling(uid)),
                        unicode(name,'utf-8'),
                        moresheets)
        if moresheets:
            self.loadData(None)
        elif self.useremail:
            # send email regarding the successful sheet generation.
            sendMail(newImportMail([(self.urlpath.sibling(arg[0]),arg[1]) for arg in self.emailInfo]),self.useremail)


    def sheetGenFailure(self,arg):
        self.callRemote('importTools.addMsgFailure',u'Failed to create spreadsheet')
                            

    def extensionsWarning(self):
        self.callRemote('importTools.addMsg',u'Numbler can not determine the type of file you are trying to import.  Trying xml...')

    def noSheetsSelected(self):
        self.callRemote('importTools.noSheetsSelected')

    # dictionary to keep track of the appropriate import handlers
    importExtensions = {
        'csv':startCsvImport,
        'xml':startXmlImport,
        'xls':startXlsImport
        }

    defaultImport = startXlsImport
        


