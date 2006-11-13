# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

from nevow import rend, loaders, appserver,static,inevow,url,flat,stan,util,tags as T,json
from twisted.web import http
import export # haha
from numbler.server import sheet
import os
from xml.dom.minidom import parse as parseXML
from nevow import static
from pkg_resources import resource_filename

class NumblerTemplatePageBase(object):
    """ base class for pages that use the main site template """
    docFactory = loaders.xmlfile('sitetemplate.xml',templateDir='templates')
    
    def __init__(self):
        self.contentFactory = loaders.xmlfile(self.xmlcontent,templateDir='templates') 
    
    def render_content(self,ctx):
        return self.contentFactory
    
    def render_title(self,ctx):
        return hasattr(self,'title') and self.title or 'Numbler'

    def render_extrascripts(self,ctx):
        return ''

    def render_header(self,ctx,data):
        sess = inevow.ISession(ctx)
        if hasattr(sess,'principal'):
            return LoggedInHeaderFragment(sess.principal)
        return LoggedOutHeaderFragment()

    def render_footer(self,ctx):
        return Footer()


class NumblerTemplatePage(NumblerTemplatePageBase,rend.Page):
    def __init__(self):
        super(NumblerTemplatePage,self).__init__()

class BadLinkPage(NumblerTemplatePage):
    """ 404 page for Numbler """

    xmlcontent = '404.xml'
    title = 'Page not found'

    def renderHTTP_notFound(self,ctx):
        return self.renderHTTP(ctx)

class AccessDenied(NumblerTemplatePage):
    """ 403 page (Forbidden) """
    xmlcontent = '403.xml'
    title = 'Access denied'
    

class ErrorPage(NumblerTemplatePage):
    """ Server error page for Numbler.  Add the URL param ?showerr=1
    to see all the sordid details"""

    xmlcontent = '500.xml'
    title = 'Server error'

    def renderHTTP_exception(self,ctx,failure):
        showerr = ctx.arg('showerr')
        if showerr and showerr in ('true','1'):
            handler = appserver.DefaultExceptionHandler()
            return handler.renderHTTP_exception(ctx,failure)
        else:
            print 'Exception occured while rendering page',failure
            request = inevow.IRequest(ctx)
            request.setResponseCode(http.INTERNAL_SERVER_ERROR)
            res = self.renderHTTP(ctx)
            request.finishRequest( False )
            return res

class ApiErrorPage(rend.Page):
    """ Server error page for Numbler.  Add the URL param ?showerr=1
    to see all the sordid details"""
    #implements(inevow.ICanHandleException)

    docFactory = loaders.xmlfile('apierror.xml',templateDir='templates')
    errPattern = inevow.IQ(docFactory).patternGenerator("error")
    
    def renderHTTP_exception(self,ctx,failure):
        print '**** ApiError Occurred *****',failure
        request = inevow.IRequest(ctx)
        request.setHeader("Content-Type", "text/xml; charset=UTF-8")
        request.setResponseCode(http.INTERNAL_SERVER_ERROR)
        request.write('<?xml version="1.0" encoding="utf-8"?>\n')
        res = self.renderHTTP(ctx)
        request.finishRequest( False )
        return res

    def render_error(self,ctx,data):
        return ctx.tag[self.errPattern()]

    def render_internalerror(self,ctx,data):
        ctx.fillSlots('code',5000)
        ctx.fillSlots('message','unknown error')
        ctx.fillSlots('resource','')
        return ctx.tag



class AboutPage(NumblerTemplatePage):
    xmlcontent = 'about.xml'
    title = 'About Numbler'

    def render_installed_software(self,ctx,data):
        import twisted,nevow,numbler,sys
        # the server won't even start without these installed
        yield self.install_item("python",sys.version)
        yield self.install_item("Numbler",numbler.__version__)        
        yield self.install_item("twisted",twisted.version.base())
        yield self.install_item("nevow",nevow.__version__)

        try:
            import MySQLdb
            mysqlver = MySQLdb.__version__
        except:
            mysqlver = 'not found'
        yield self.install_item("MySQLdb",mysqlver)

        try:
            import numpy
            numpyver = numpy.__version__
        except:
            numpyver = 'not found'
        yield self.install_item("numpy",numpyver)

        try:
            import Crypto
            cryptover = Crypto.__version__
        except:
            cryptover = "not found"
        yield self.install_item("pycrypto",cryptover)

        try:
            import PyICU
            version = "installed"
        except:
            version = "not found"
        yield self.install_item("PyICU",version)

        try:
            import zope.interface
            version = "installed"
        except:
            version = "not found"
        yield self.install_item("zope-interface",version)

    def install_item(self,name,ver):
        return T.tr[T.td[name],T.td[ver]]

    def render_extrascripts(self,ctx,data):
        return T.style(type="text/css")[
            """
            table {
            width:80%;
            }
            td {

            }
            """
            ]
        
        

class ExportPage(NumblerTemplatePage):
    xmlcontent = 'exportoptions.xml'

    def __init__(self,sheetUID):
        super(ExportPage,self).__init__()
        self.sheetUID = sheetUID
        self.sheetname = sheet.SheetHandle.getInstance(sheetUID)().getAlias()
        self.xmlchild = self.sheetname + ".xml"
        self.csvchild = self.sheetname + ".csv"

    def render_content(self,ctx,data):
        request = inevow.IRequest(ctx)
        if ctx.arg('xmlexport'):
            request.redirect(request.URLPath().child(self.xmlchild))
        elif ctx.arg('csvexport'):
            request.redirect(request.URLPath().child(self.csvchild))
        else:
            return super(ExportPage,self).render_content(ctx)

    def render_title(self,ctx):
        return 'export "%s"' % self.sheetname


    def childFactory(self,ctx,name):
        if name == self.xmlchild:
            return export.msExcelExport(self.sheetUID)
        elif name == self.csvchild:
            return export.CSVExport(self.sheetUID)

class SupportPage(NumblerTemplatePage):
    """
    generates support content from a number of XML files stored
    in the support folder.  If the XML file is modified or a new XML
    file is added the content will be picked up.
    """

    xmlcontent = 'support.xml'
    title = 'Numbler support'
    supportfolder = 'templates/support'
    cache = {}
    #lastmtime = None
    headerpattern = None
    

    def __init__(self):
        super(SupportPage,self).__init__()
        if not self.headerpattern:
            self.headerpattern= inevow.IQ(self.contentFactory).patternGenerator("supportheader")
            self.headeritempat = inevow.IQ(self.contentFactory).patternGenerator("headeritem")
            self.contentpat = inevow.IQ(self.contentFactory).patternGenerator("supportlnk")
        

    def render_content(self,ctx,data):
        if not len(self.cache):
            # rebuild the cache
            self.fullrebuild()
            #self.lastmtime= os.path.getmtime(self.supportfolder)
        else:
            # TODO: this could be optimzed to only scan the folder
            # IF the modify time on the directory changes.
            self.partialrebuild()

        self.renderindex = 1
        return super(SupportPage,self).render_content(ctx)        

    def generateProcessOrder(self):
        """ generate the list a sorted list of files that will correspond to the rendering
        order. This is determined by the position attribute in each XML file
        """
        self.procorder = sorted(self.cache.values(),lambda x,y: cmp(x[0].position,y[0].position))        

    def render_supporttop(self,ctx,data):
        return ctx.tag[
            [self.headerpattern(data=item[0]) for item in self.procorder]
            ]

    def render_headeritems(self,ctx,data):
        return [self.headeritempat(data=i) for i in data.desclist]

    def render_supportheader(self,ctx,data):
        ctx.fillSlots('topic',data.title)
        ctx.fillSlots('headeritems',[self.headeritempat(data=i) for i in data.desclist])
        return ctx.tag

    def render_headeritem(self,ctx,data):
        # corresponds to ref from xml file
        ctx.fillSlots('href','#' + data[1])
        # corresponds to description from the xml file        
        ctx.fillSlots('name',data[0]) 
        return ctx.tag

    def render_supportcontents(self,ctx,data):
        return ctx.tag[
            [self.contentpat(data=(cacheitem[0],index)) for
                            cacheitem in self.procorder
                            for index in range(0,len(cacheitem[0].contentlist))]
            ]

    def render_supportlnk(self,ctx,data):
        item,index = data
        ctx.fillSlots('name',item.desclist[index][1])
        ctx.fillSlots('desc','%d. %s' % (self.renderindex,item.desclist[index][0]))
        self.renderindex += 1
        ctx.fillSlots('content',T.xml(item.contentlist[index]))
        return ctx.tag

    def fullrebuild(self):
        """ rebuild the content from all files.  This should only be
        called when the server starts
        """
        
        for contentF in [os.sep.join([self.supportfolder,sfile])
                         for sfile in os.listdir(self.supportfolder) if sfile[-3:] == 'xml']:
            self.rebuild(contentF)
        self.generateProcessOrder()

    def partialrebuild(self):
        """ called whenever a content file changes """
        changed = False
        for contentF in [os.sep.join([self.supportfolder,sfile])
                         for sfile in os.listdir(self.supportfolder) if sfile[-3:] == 'xml']:
            cacheitem = self.cache.get(contentF)
            if not cacheitem or (cacheitem and cacheitem[1] < os.path.getmtime(contentF)):
                self.rebuild(contentF)
                changed = True

        if changed:
            self.generateProcessOrder()

    def rebuild(self,fname):
        print 'rebuilding',fname
        handler = SupportParser()
        handler.parse(fname)
        self.cache[fname] = (handler,os.path.getmtime(fname))


class SupportParser(object):
    """
    Support class which is responsible for parsing each help file.
    """
    
    def __init__(self):
        self.title = None
        self.desclist = []
        self.contentlist = []
        self.initem = 0
        self.position = 0        

    def parse(self,fname):
        doc = parseXML(fname)
        fileinfo = doc.getElementsByTagName('fileinfo')[0]
        self.title = fileinfo.attributes['name'].value
        self.position = fileinfo.attributes['position'].value

        for item in doc.getElementsByTagName('item'):
            attr = item.attributes
            self.desclist.append((attr['description'].value,attr['ref'].value))
            self.contentlist.append(''.join([child.toxml() for child in item.childNodes]))
        

class NumblerFile(static.File):

    def directoryListing(self):
        return BadLinkPage()



class Footer(rend.Fragment):
    docFactory = loaders.xmlfile('footer.xml',templateDir='templates')
    
class LoggedOutHeaderFragment(rend.Fragment):
    docFactory = loaders.xmlfile('loggedoutheader.xml',templateDir='templates')


class LoggedInHeaderFragment(rend.Fragment):
    docFactory = loaders.xmlfile('loggedinheader.xml',templateDir='templates')

    def __init__(self,principal,showSettings=False):
        # if showSettings is false than we show the myaccount
        self.username = principal.userid
        self.showSettings = showSettings

    def render_username(self,ctx,data):
        return self.username
    
    def render_acclink(self,ctx,data):
        if self.showSettings:
            return ctx.tag(href="/myaccountsettings")[u'My settings']
        else:
            return ctx.tag(href="/myaccount")[u'My Account']


from pkg_resources import resource_filename
from twisted.python.reflect import namedAny
from gendoc import functionDocGenerator

class FunctionDocPage(rend.Page):
    
    docFactory = loaders.xmlfile('functiondoc.xml',templateDir='templates')
    docdirectory = resource_filename('numbler','function_docs')
    child_sections = NumblerFile(docdirectory)
    
    def __init__(self):

        moddict = {}
        modulelist = []
        from numbler.server.ast import numblerfuncs
        
        for func in numblerfuncs:
            mod = namedAny(func.__module__)
            moddesc = unicode(mod.__shortmoddesc__)
            if moddesc not in moddict:
                moddict[moddesc] = (unicode(mod.__name__.split('.')[-1] + '.xml'),[])
                modulelist.append(mod)
                
            moddict[moddesc][1].append(unicode(func.__name__))
            
            
        self.funclist = [[x,moddict[x][0],moddict[x][1]] for x in moddict.keys()]

        self.rebuild(modulelist)

    def rebuild(self,modulelist):

        for mod in modulelist:
            fullpath = os.sep.join([self.docdirectory,mod.__name__.split('.')[-1] + '.xml'])
            print 'generating',fullpath

            try:
                fh = open(fullpath,'w+')
                try:
                    fulldoc = functionDocGenerator(mod.funclist)
                    containerstan = T.div(id='contentcon')[fulldoc]
                    fh.write(flat.flatten(containerstan))
                except Exception,e:
                    print '***** ERROR GENERATING FUNCTION DOC',fullpath
                    print 'exception is:',e
                    #import traceback,sys
                    #traceback.print_tb(sys.exc_info()[2])
                    #traceback.print_stack()                                    
                    #os.unlink(fullpath)

            finally:
                fh.close()

    def render_footer(self,ctx,data):
        return Footer()
        
    def render_content(self,ctx,data):
        return T.h3[
            'click on a link on the left to view the documentation on a particular section.'
            ]

    def render_loadtree(self,ctx,data):
        return T.script(type='text/javascript')[
            T.raw("""
            addLoadEvent(function() { Numbler.funcdoc.loadTree('%s'); });
            """ % json.serialize(self.funclist))
            ]
                 
                  
