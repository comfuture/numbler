# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

from nevow import rend, loaders, appserver,static,inevow,url,flat,stan,util,static,athena,tags as T
from twisted.web import http
from numbler.server import account,sheet
from nevow.flat import flatten
import re
from numbler.support_pages import NumblerTemplatePage,Footer,LoggedInHeaderFragment,NumblerTemplatePageBase
from numbler.utils import validEmail
from numbler.server.exc import *
from cookiemgmt import SheetCookieHandler
from numbler.server.sslib.utils import alphaguid8
from twisted.names.client import getHostByName
from twisted.internet.defer import DeferredList


def redirIfNotSecure(req,targetpath = None):
    """ redirect to a secure URL """
    if not req.isSecure():
        urlpath = targetpath is not None and targetpath or req.URLPath()
        if urlpath.netloc.find(':') > 0:
            host,port = urlpath.netloc.split(':')
            if int(port) == 8080:
                req.redirect(urlpath.secure(port=8443))
        else:
            req.redirect(urlpath.secure())
        req.finish()
        return True
    return False
    
def hasPrincipal(ctx,pathurl=None,continuearg=None):
    """ guard a page to make sure that principal exists """
    sess = inevow.ISession(ctx)
    req = inevow.IRequest(ctx)
    if not hasattr(sess,'principal'):
        if continuearg:
            fullurl = pathurl.child('accountlogin').add('continue',pathurl.child(continuearg))
            req.redirect(fullurl)            
        else:
            req.redirect('/accountlogin')
        req.finish()
        return False
    return True
    

def getnonsecureroot(ctx):
    ctx = inevow.IRequest(ctx)
    urlpath = ctx.URLPath()
    targetport = 80
    if urlpath.netloc.find(':') > 0:
        host,port = urlpath.netloc.split(':')
        if int(port) == 8443:
            targetport = 8080
    return url.root.secure(False,targetport)    
    


class MyAccountPage(athena.LivePage):
    docFactory = loaders.xmlfile('myaccountpage.xml',templateDir='templates')

    def __init__(self):
        super(MyAccountPage,self).__init__(jsModuleRoot=url.here.parentdir().child('athenajs'))
        self.jsModules.mapping[u'Numbler'] = util.resource_filename('numbler.js','myaccount.js') #numbler.js is a directory!
        self._shouldInclude('Numbler')

    def renderHTTP(self,ctx):
        if not hasPrincipal(ctx):
            return ''
        self.principal = inevow.ISession(ctx).principal
        return super(MyAccountPage,self).renderHTTP(ctx)
    

    def beforeRender(self,ctx):
        d = self.principal.getSheetSummary()
        d.addCallback(self.processSheetSummary)
        return d

    def processSheetSummary(self,args):
        self.ownedsheets,self.membersheets = args

    def render_footer(self,ctx,data):
        return Footer()

    def render_manageaccount(self,ctx,data):

        # save off the base URL for later use by the fragments
        self.rootURL = inevow.IRequest(ctx).URLPath().parentdir()
        f = AccountManageFragment(self.principal)
        f.setFragmentParent(self)
        return ctx.tag[f]

    def render_mysheets(self,ctx,data):
        """
        create a bunch of fragments for each spreadsheet
        """
        def gen():
            for sheet in self.ownedsheets:
                f = SheetManageFragment(self.principal,sheet)
                f.setFragmentParent(self)
                yield f
        yield ctx.tag[gen()]

    def render_membersheets(self,ctx,data):
        def gen():
            for sheet in self.membersheets:
                f = memberListFragment(self.principal,sheet)
                f.setFragmentParent(self)
                yield f

        yield ctx.tag[gen()]

    def addNewSheet(self,sheetname):
        resultdict = self.principal.createNewSheet(sheetname)
        f = SheetManageFragment(self.principal,resultdict)
        f.setFragmentParent(self)
        # flatten magically takes the fragment and flattens it out.
        res = unicode(flat.flatten(T.div(xmlns="http://www.w3.org/1999/xhtml")[f]),'utf-8')
        return res,f._athenaID


    def render_debug(self, ctx, data):
        f = athena.IntrospectionFragment()
        f.setFragmentParent(self)
        return ctx.tag[f]

    def render_header(self,ctx,data):
        return LoggedInHeaderFragment(self.principal,True)


class AccountManageFragment(athena.LiveFragment):
    jsClass = u'Numbler.MyAccount'
    docFactory = loaders.xmlfile('manageaccount.xml',templateDir='templates')
    
    def __init__(self,principal):
        super(AccountManageFragment, self).__init__()
        self.principal = principal

    # remote handlers

    def addnewsheet(self,name):
        """
        add a new sheet
        """
        newfrag = self.page.addNewSheet(name)
        return newfrag

    athena.expose(addnewsheet)

    def render_existingsheets(self,ctx,data):
        frag = MainPageAuthUserFragment(self.principal)
        return frag.render_existingsheets(ctx,data)

    

class SheetManageFragment(athena.LiveFragment):
    jsClass = u'Numbler.ManageSheet'
    docFactory = loaders.xmlfile('managesheet.xml',templateDir='templates')

    def __init__(self,principal,datadict):
        super(SheetManageFragment, self).__init__()

        self.principal = principal
        self.sheetInfo = datadict
        self.memberlist = None

    def render_sheetsummary(self,ctx,data):
        ctx.fillSlots('url','/' + self.sheetInfo['sheetUid'])
        ctx.fillSlots('name',self.sheetInfo['name'])
        ctx.fillSlots('invites',self.sheetInfo['numInvites'])
        ctx.fillSlots('pending',self.sheetInfo['pendingInvites'])        
        return ctx.tag

    ## UI handlers

    def getDetails(self):
        """
        get the details about the sheet
        """
        d = self.principal.getUserList(self.sheetInfo['sheetId'])
        d.addCallback(self.processDetails)
        return d

    def processDetails(self,ret):
        # save off a list for later checking
        self.userlist = set([x['username'] for x in ret])
        return [self.sheetInfo,ret]

    def applyChanges(self,sheetType,sheetName):
        self.principal.renameSheet(self.sheetInfo['sheetId'],sheetName.encode('utf-8'))
        self.principal.changeSheetType(self.sheetInfo['sheetId'],int(sheetType))



    def addUsers(self,useremail):
        """
        invite a user to a spreadsheet
        """
        dupes = self.userlist.intersection(set(useremail))
        if len(dupes):
            return {u'error':u'dupe',u'dupelist':dupes}

        useremail = [x.strip() for x in useremail]
        emailmatch = [y for y in [validEmail(x) for x in useremail] if y is not None]
        
        if len(emailmatch) != len(useremail):
            return {u'error':u'badaddrs',u'invalidusers':[x for x in useremail if not validEmail(x)]}

        # look through the invites checking for bad domainnames.
        dnlist = [match.groupdict()['domainname'] for match in emailmatch]
        
        d = DeferredList([getHostByName(x) for x in dnlist]).addBoth(self.afterNsLookup,dnlist,useremail)
        return d


    def afterNsLookup(self,arglist,domains,useremail):
        """
        called when all the DNS requests for the user email addresses have completed.
        """
        invalidDN = []
        
        # process all the requests.
        for i in range(0,len(arglist)):
            cbres  = arglist[i]
            if not cbres[0]:
                invalidDN.append(unicode(domains[i]))

        if len(invalidDN) == 0:
            # success.
            return self.sendInvites(useremail)
        else:
            return {u'error':u'dnfailure',u'invaliddn':invalidDN}
        

    def sendInvites(self,useremail):
        try:
            invitees = set([addr.encode('utf-8') for addr in useremail])
            pending,current = self.principal.inviteToSheet(self.sheetInfo['sheetId'],invitees,self.page.rootURL)
            self.userlist.update(pending)
            # 0  = no errors
            return {u'error':u'none',u'pending':pending,u'current':current}
        except SelfInviteException:
            return {u'error':u'selfinvite',u'pending':[]}
    

    def removeUsers(self,useremail):
        """
        remove a users's write permsisions
        """
        self.userlist.difference_update(useremail)
        invitees = set([addr.encode('utf-8') for addr in useremail])        
        self.principal.revokeInvite(self.sheetInfo['sheetId'],invitees)


    def beforeDeleteSheet(self):
        """
        return the number of connected users before deleting a sheet
        """
        return self.principal.checkDeleteSheet(self.sheetInfo['sheetId'])

    def deleteSheet(self):
        """
        permamently remove this spreadsheet
        """
        self.principal.deleteSheet(self.sheetInfo['sheetId'])

    allowedMethods = ['applyChanges','addUsers','removeUsers','deleteSheet','getDetails','beforeDeleteSheet']


class memberListFragment(athena.LiveFragment):
    jsClass = u'Numbler.ManageMemberList'
    docFactory = loaders.xmlfile('managememberlist.xml',templateDir='templates')

    def __init__(self,principal,sheet):
        super(memberListFragment, self).__init__()
        self.principal = principal
        self.sheet = sheet

    def render_memberattrs(self,ctx,data):
        ctx.fillSlots('href','/' + self.sheet['sheetUid'])
        ctx.fillSlots('name',self.sheet['name'])
        return ctx.tag

    def deleteMembership(self):
        return self.principal.removeMemberInvite(self.sheet['sheetId'])

    athena.expose(deleteMembership)
    


class CreateAccountPage(NumblerTemplatePageBase,athena.LivePage):
    xmlcontent = 'createaccount.xml'
    title = 'Create Numbler Account'

    def __init__(self):
        athena.LivePage.__init__(self,jsModuleRoot=url.here.parentdir().child('athenajs'))
        NumblerTemplatePageBase.__init__(self)
        self.jsModules.mapping[u'Numbler'] = util.resource_filename('numbler.js','myaccount.js') #numbler.js is a directory!

    def beforeRender(self,ctx):
        req = inevow.IRequest(ctx)
        sess = inevow.ISession(ctx)

        redirIfNotSecure(req)

    def render_liveglue(self,ctx,data):
        # extremely ugly code to make sure that athena doesn't import mochikit
        try:
            self.BOOTSTRAP_MODULES.remove('MochiKit')
            return super(CreateAccountPage,self).render_liveglue(ctx,data)
        finally:
            self.BOOTSTRAP_MODULES.insert(0,'MochiKit')
    
    def render_extrascripts(self,ctx,data):
        return self.render_liveglue(ctx,data)

    def render_theform(self,ctx,data):
        emailaddr = ctx.arg('emailaddr')
        if emailaddr is None:
            emailaddr = ''
        f = CreateAccFormFragment(emailaddr)
        f.setFragmentParent(self)
        return f

    def render_debug(self, ctx, data):
        f = athena.IntrospectionFragment()
        f.setFragmentParent(self)
        return ctx.tag[f]


def generateLangs():
    """
    generate all the languages support by PyICU.  this method returns a flattened
    list of options plus a lookup dictionary to tranlate localecodes used 
    """
    
    from PyICU import Locale
    results = [(Locale(x).getDisplayName(),x) for x in Locale('').getAvailableLocales()]
    results.sort()
    lookupdict = dict([(results[x][1],x) for x in range(0,len(results))])
    return flat.flatten([T.option(value=x[1])[x[0]] for x in results]),lookupdict

def generateTzDict():
    """
    generate a dictionary to map the timezone list index to the value in the database
    """
    from xml.dom.minidom import parse
    from xml import xpath
    from pkg_resources import resource_filename
    
    fname = resource_filename('numbler.templates','tzlist.xml')
    tzlist = [x.value for x in xpath.Evaluate('//*/@value',parse(fname).documentElement)]
    lookupdict = dict([(tzlist[x],x) for x in range(0,len(tzlist))])
    return lookupdict
    

class CreateAccFormFragment(athena.LiveFragment):
    jsClass = u'Numbler.CreateAccount'
    docFactory = loaders.xmlfile('createaccountform.xml',templateDir='templates')
    preRenderedLangs,langLookup = generateLangs()
    tzList = loaders.xmlfile('tzlist.xml',templateDir='templates')
    tzLookup = generateTzDict()
    
    def __init__(self,emailaddr = ''):
        self.emailaddr = emailaddr
        self.existingsheets = None
    
    def render_theform(self,ctx,data):
        req = inevow.IRequest(ctx)
        self.rootURL = req.URLPath().parentdir()
        
        # grab any existing sheets for upgrade purposes
        chandler = SheetCookieHandler(req)
        self.existingsheets = chandler.oldrecent
        
        ctx.fillSlots('emailaddr',self.emailaddr)
        return ctx.tag

    def render_langoptions(self,ctx,data):
        return ctx.tag[self.preRenderedLangs]

    def render_timezones(self,ctx,data):
        return ctx.tag[self.tzList]

    # remote handlers

    def validateEmail(self,name):
        match = validEmail(name)
        if not match:
            return {u'error':u'badaddr'}
        if account.accountExists(name):
            return {u'error':u'exists'}

        # check the domain name.
        dnname = match.groupdict()['domainname']
        
        d = getHostByName(dnname).addCallbacks(
            lambda _: {u'error':u'none'},
            lambda _: {u'error':u'dnfailure',u'dn':unicode(dnname)})
        
        return d

    
    def createAccount(self,email,password,nick,locale,tz):
        try:
            principal,oldsheetsDeferred = account.createAccount(email.encode('utf-8'),
                                                                nick.encode('utf-8'),
                                                                password.encode('utf-8'),
                                                                locale.encode('utf-8'),
                                                                tz.encode('utf-8'),self.existingsheets)
            d = principal.sendEmailConfirm(self.rootURL)
            if not oldsheetsDeferred:
                def returnres(arg):
                    return {u'error':u'none'}
                d.addCallback(returnres)
                return d
            else:
                # we could chain the deferred with the email but I don't really care about that too much
                def returnres(dbresults):
                    return {u'error':u'oldsheets',u'sheetlist':[unicode(res[0],'utf-8') for res in dbresults]}
                def dumper(arg):
                    print arg
                oldsheetsDeferred.addCallback(returnres)
                oldsheetsDeferred.addErrback(dumper)
                return oldsheetsDeferred
        except AccountExists,e:
            return {u'error':u'exists'}

        # send invite mail
    athena.expose(validateEmail,createAccount)

class VerifyPage(NumblerTemplatePageBase,rend.Page):

    contentFactory = loaders.xmlfile('verifyaccount.xml',templateDir='templates')
    successPat = inevow.IQ(contentFactory).patternGenerator("success")
    badtokenPat = inevow.IQ(contentFactory).patternGenerator("badtoken")

    title = 'Verify your email address'
    
    def __init__(self):
        self.guid = None

    def beforeRender(self,ctx):
        # if someone just hits the url without a child
        if not self.guid:
            self.rendPat = self.badtokenPat
            return

        self.rendPat = self.successPat
        # lookup the account information
        try:
            principal = account.resolveByStateToken(self.guid)
            principal.accountVerified()

            # clear the oldsheets cookie
            chandler = SheetCookieHandler(inevow.IRequest(ctx))
            chandler.forgetoldsheets()
            
        except AccountTokenNotExist:
            self.rendPat = self.badtokenPat


    def childFactory(self,ctx,name):
        if len(name) != 40:
            return None
        self.guid = name
        return self

    def render_main(self,ctx,data):
        return ctx.tag[self.rendPat()]


class AccountLoginFragment(rend.Fragment):
    """
    the login box, basically
    """
    docFactory = loaders.xmlfile('accountloginfragment.xml',templateDir='templates')
    errorpat = inevow.IQ(docFactory).patternGenerator("loginerror")
    welcomepat = inevow.IQ(docFactory).patternGenerator("welcome")
    welcomepublicpat = inevow.IQ(docFactory).patternGenerator("welcomepublic")

    def __init__(self,emailaddr=None,error = False,showmessage = None,continueURL = None):
        self.emailaddr = emailaddr
        self.loginerror = error
        if showmessage is None:
            self.messagepat = None
        elif showmessage == 'welcome':
            self.messagepat = self.welcomepat
        elif showmessage == 'welcomepublic':
            self.messagepat = self.welcomepublicpat
        self.continueURL = continueURL

    def render_emailaddr(self,ctx,data):
        if not self.emailaddr:
            # lookup via cookie
            self.emailaddr = SheetCookieHandler(inevow.IRequest(ctx)).getemail()
        return ctx.tag(value=self.emailaddr)

    def render_checkbox(self,ctx,data):
        if len(self.emailaddr):
            return ctx.tag(checked=True)
        else:
            return ctx.tag

    def render_error(self,ctx,data):
        if self.loginerror:
            return ctx.tag[self.errorpat()]
        else:
            return ctx.tag['']

    def render_message(self,ctx,data):
        if self.messagepat:
            return self.messagepat()
        else:
            return ''

    def render_formattrs(self,ctx,data):
        req = inevow.IRequest(ctx)
        urlpath = req.URLPath()
        urlpath = urlpath.parentdir()
        if not req.isSecure():
            if urlpath.netloc.find(':') > 0:
                host,cport = urlpath.netloc.split(':')
                # always go up to the parent - this does nothing if we are already at the top
                ctx.fillSlots('action',urlpath.secure(port =(int(cport) == 8080 and 8443 or 443)).child('accountlogin'))
            else:
                ctx.fillSlots('action',urlpath.secure().child('accountlogin'))
        else:
            ctx.fillSlots('action',urlpath.child('accountlogin'))
        if self.continueURL:
            ctx.fillSlots('continueURL',self.continueURL)
        else:
            ctx.fillSlots('continueURL','')
            
        return ctx.tag

class accountLogout(rend.Page):

    def renderHTTP(self,ctx):
        req = inevow.IRequest(ctx)
        sess = inevow.ISession(ctx)
        if hasattr(sess,'principal'):
            del sess.principal
        # always redirect to the http root
        return getnonsecureroot(ctx)

class AccountLoginPage(NumblerTemplatePage):
    """
    verify credentials and establish a principal
    """

    title = "Login to your numbler account"
    xmlcontent = "accountlogin.xml"
    contentFactory = loaders.xmlfile(xmlcontent,templateDir='templates')
    notvalidatedpat = inevow.IQ(contentFactory).patternGenerator("notvalidated")
    messagepat = inevow.IQ(contentFactory).patternGenerator("infomessage")
    
    def __init__(self,continueToCurrentURL = False):
        """
        continueToCurrentURL means that we should continue to same URL as the request.
        this is necessary because some times we return this page on a different URL.
        """
        
        self.validationErr = False
        self.existingemail = ''
        self.accountNotVerified = False
        self.continueToCurrentURL = continueToCurrentURL
        
    def beforeRender(self,ctx):
        """ redirect to either myaccount or to the continuation URL"""
        req = inevow.IRequest(ctx)

        # if we were given a continuation argument make sure it goes on the query string
        if self.continueToCurrentURL:
            self.contineToCurrentURL = req.URLPath()
            redirpath = req.URLPath().replace('continue',req.URLPath())
        else:
            redirpath = None
            
        # make sure the request comes over SSL
        if redirIfNotSecure(req,redirpath):
            return
        
        sess = inevow.ISession(ctx)

        remembermail = ctx.arg('remembermail')
        username = ctx.arg('user')
        passwd = ctx.arg('passwd')

        chandler = SheetCookieHandler(req)
        if ctx.arg('frompost'):
            if remembermail:
                chandler.rememberemail(username)
            else:
                chandler.forgetemail()                

        if username and passwd:
            try:
                principal = account.lookupAccount(username,passwd)
                if principal.isAccountVerified():
                    sess.principal = principal
                else:
                    self.accountNotVerified = True
                    if hasattr(self,'principal'):
                        del sess.principal
                
                #TODO: check that the account is verified
            except AccountNotFound,e:
                self.validationErr = True
                return

        # allow for pass through as a query parameter
        #if username and not len(self.existingemail):
        #    self.existingemail = username
            
        if not hasattr(sess,'principal'):
            # proceed to render the screen
            return

        # at this point we have a valid principal.
        # if we are supposed to be somewhere else - go there. otherwise
        # take the user to the account management page

        # continue comes from the query string
        # embedcontinue is a hidden form field in the accountlogin fragment
        contURL = ctx.arg('continue')
        if not contURL:
            contURL = ctx.arg('embedcontinue')
        
        if contURL:
            req.redirect(contURL)
        else:
            req.redirect("/myaccount")
        req.finish()

    def render_message(self,ctx,data):
        if self.accountNotVerified:
            return self.notvalidatedpat()
        else:
            return self.messagepat()

    def render_loginfrag(self,ctx,data):
        if not self.accountNotVerified:
            if self.continueToCurrentURL:
                req = inevow.IRequest(ctx)
                return AccountLoginFragment(self.existingemail,self.validationErr,continueURL = req.URLPath())
            else:
                return AccountLoginFragment(self.existingemail,self.validationErr)
        else:
            return ''

    def render_extrascripts(self,ctx):
        return T.script(type='text/javascript')[T.raw("""
        MochiKit.DOM.addLoadEvent(function() { roundElement('loginparent'); });
        """)]

        


class ResetPassword(NumblerTemplatePage):

    title = "Reset your Numbler account password"
    xmlcontent = "resetpasswd.xml"
    contentFactory = loaders.xmlfile(xmlcontent,templateDir='templates')
    notexistpat = inevow.IQ(contentFactory).patternGenerator("notexist")
    notverified = inevow.IQ(contentFactory).patternGenerator("notverified")
    theform = inevow.IQ(contentFactory).patternGenerator("theform")
    mailsent = inevow.IQ(contentFactory).patternGenerator("mailsent")
    
    def __init__(self):
        self.emailaddr = ""
        self.rendpat = None

    def beforeRender(self,ctx):
        emailaddr = ctx.arg('emailaddr')
        if not emailaddr:
            self.rendpat = self.theform
        else:
            self.emailaddr = emailaddr
            try:
                req = inevow.IRequest(ctx)
                account.requestPasswordChange(self.emailaddr,req.URLPath().parentdir())
                self.rendpat = self.mailsent
            except AccountNotVerified:
                self.rendpat = self.notverified
            except AccountNotFound:
                self.rendpat = self.notexistpat

    def render_email(self,ctx,data):
        return ctx.tag[self.emailaddr]
    
    def render_theform(self,ctx,data):
        return ctx.tag[self.rendpat()]
                    


class NewPasswordPage(NumblerTemplatePageBase,rend.Page):

    contentFactory = loaders.xmlfile('changepassword.xml',templateDir='templates')
    successPat = inevow.IQ(contentFactory).patternGenerator("success")
    badtokenPat = inevow.IQ(contentFactory).patternGenerator("badtoken")
    formPat = inevow.IQ(contentFactory).patternGenerator("theform")
    errorPat = inevow.IQ(contentFactory).patternGenerator("error")

    title = 'change your password'
    
    def __init__(self):
        self.rendPat = None
        self.guid = None
        self.badPassword = False

    def childFactory(self,ctx,name):
        """ lookup the token from the URL """
        if len(name) != 40:
            return None
        self.guid = name
        return self

    def beforeRender(self,ctx):
        req = inevow.IRequest(ctx)
        redirIfNotSecure(req)
        
        if not self.guid:
            self.rendPat = self.badtokenPat
            return

        password1 = ctx.arg('password1')
        password2 = ctx.arg('password2')
        if password1 or password2:
            if password1 != password2:
                self.badPassword = True
                self.rendPat = self.formPat
            else:
                principal = account.lookupAccOnPasswordChange(self.guid)
                principal.changePasswd(password1)
                self.rendPat = self.successPat
        else:
            try:
                principal = account.lookupAccOnPasswordChange(self.guid)
                self.rendPat = self.formPat
            except PasswordChangeTokenExpire:
                self.rendPat = self.badtokenPat
            

    def render_main(self,ctx,data):
        return ctx.tag[self.rendPat()]

    def render_error(self,ctx,data):
        if self.badPassword:
            return ctx.tag[self.errorPat()]
        else:
            return ctx.tag
        

class getAPIID(NumblerTemplatePage):
    title = 'register for API access ID'
    xmlcontent = "getapiid.xml"
    contentFactory = loaders.xmlfile(xmlcontent,templateDir='templates')    
    
    def __init__(self):
        pass

    def renderHTTP(self,ctx):
        req = inevow.IRequest(ctx)
        path = req.URLPath().parentdir()
        if not hasPrincipal(ctx,path,'getAPIid'):
            return ''
        self.principal = inevow.ISession(ctx).principal
        return super(getAPIID,self).renderHTTP(ctx)        

    def beforeRender(self,ctx):
        # registerForApiAccount is idempotent.  it returns
        # a deferred but we don't really care about when it finishes
        self.principal.registerForApiAccount()
        self.principal.sendApiDetailsEmail()



class ModifyAccountPage(athena.LivePage):
    docFactory = loaders.xmlfile('modifyaccount.xml',templateDir='templates')

    def __init__(self):
        super(ModifyAccountPage,self).__init__(jsModuleRoot=url.here.parentdir().child('athenajs'))
        self.jsModules.mapping[u'Numbler'] = util.resource_filename('numbler.js','myaccount.js') #numbler.js is a directory!

    def renderHTTP(self,ctx):
        self.rootURL = inevow.IRequest(ctx).URLPath().parentdir()        
        if not hasPrincipal(ctx,self.rootURL,'myaccountsettings'):
            return ''
        self.principal = inevow.ISession(ctx).principal
        return super(ModifyAccountPage,self).renderHTTP(ctx)

    def render_footer(self,ctx,data):
        return Footer()

    def beforeRender(self,ctx):
        req = inevow.IRequest(ctx)
        sess = inevow.ISession(ctx)
        redirIfNotSecure(req)

    def render_header(self,ctx,data):
        return LoggedInHeaderFragment(self.principal)        

    def render_theform(self,ctx,data):
        f = ModifyAccFormFragment(self.principal)
        f.setFragmentParent(self)
        return f


class ModifyAccFormFragment(CreateAccFormFragment):
    jsClass = u'Numbler.ModifyAccount'

    def __init__(self,principal):
        self.principal = principal
        # populate the field with dummy values
        self.boguspasswd = alphaguid8()
        self.emailaddr = self.principal.userid

    def getInitialArguments(self):
        """
        special athena handler to populate widgets with the correct arguments
        """
        return (unicode(self.principal.userid,'utf-8'),
                unicode(self.principal.displayname,'utf-8'),
                unicode(self.boguspasswd,'utf-8'),
                self.langLookup[str(self.principal.locale)],
                self.tzLookup[str(self.principal.locale.tz)])
                                

    def modifyAccount(self,email,password,nick,lang,tz):
        modargs = {}
        ret = {u'error':u'none'};
        nick = nick.encode('utf-8')
        email = email.encode('utf-8')
        lang = lang.encode('utf-8')
        tz = tz.encode('utf-8')

        # check if the password is different and update
        if password != self.boguspasswd:
            modargs['passwd'] = password.encode('utf-8')
        # check if the nick is different and update
        if nick != self.principal.displayname:
            modargs['dispname'] = nick
        if email != self.principal.userid:
            ret[u'error'] = u'emailchange'
            modargs['email'] = email

        if tz != str(self.principal.locale.tz):
            modargs['tz'] = tz
        if lang != str(self.principal.locale):
            modargs['locale'] = lang
        
        # check if the email address is different
        def onsuccess(arg):
            return ret

        def onfailure(failure):
            if failure.check(AccountExists):
                return {u'error':u'exists'}
            else:
                return {u'error':u'unknown'}
        
        d = self.principal.modifyAccount(modargs,self.page.rootURL)
        d.addCallbacks(onsuccess,onfailure)
        return d

    def validateEmail(self,name):
        if name == self.principal.userid:
            return {u':error':u'none'}
        else:
            return super(ModifyAccFormFragment,self).validateEmail(name)
          

    athena.expose(modifyAccount,validateEmail)



class MainPageAuthUserFragment(rend.Fragment):
    docFactory = loaders.xmlfile('mainpageauthuser.xml',templateDir='templates')

    def __init__(self,principal):
        self.principal = principal

    def render_displayname(self,ctx,data):
        return ctx.tag[self.principal.displayname]

    def render_existingsheets(self,ctx,data):
        request = inevow.IRequest(ctx)
        handler = SheetCookieHandler(request)
        d = handler.recentSheets()
        if d:
            d.addCallback(self.processResults,ctx)
            return d
        else:
            return T.div(id='recentresults')                    

    def processResults(self,args,ctx):

        recentPages,namedict = args
        knownpages = [item for item in recentPages if namedict.has_key(item)]
        ret = T.div(id='recentresults')[
            [T.div[T.a(href=url.root.child(item))[
            namedict[item]]] for item in knownpages[0:5]]]
        return ret


class upgradeToAccountsPage(NumblerTemplatePage):
    title = 'upgrade to a Numbler account'
    xmlcontent = 'upgradetoaccount.xml'
    

    def beforeRender(self,ctx):
        req = inevow.IRequest(ctx)
        chandler = SheetCookieHandler(req)
        # if the user somehow encounters this URL but doesn't have
        # any old cookies redirect back to the main page
        if not chandler.oldrecent:
            req.redirect('/')
            req.finish()
            return

        forgetsheets = ctx.arg('forgetsheets')
        if forgetsheets:
            chandler.forgetoldsheets()
            req.redirect('/')
            req.finish()

    
    def render_extrascripts(self,ctx):
        return T.script(type='text/javascript')[T.raw("""
        MochiKit.DOM.addLoadEvent(function() { 
          roundElement("clearoldsheets");
          });
        """)]
