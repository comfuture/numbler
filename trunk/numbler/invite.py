# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.
# with the exception of  createhtmlmail which is from
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/67083
#


from nevow import rend,loaders,inevow, tags as T
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import formatdate
import cStringIO
from xml.sax.handler import ContentHandler
import xml.sax

from twisted.internet import threads

from numbler.site_settings import settings

# get rid of adjoining white space
def cleanup(val):
    oldval = None
    for x in val:
        if x != '':
            yield x
            oldval = ''
            yield ' '
        elif x == '' and oldval == '':
            continue
        else:
            yield ' '
        oldval = x
	


class flatToTextHandler(ContentHandler):

    def __init__(self):
        self.content = []

    def textvalue(self):
        #return ''.join(self.content).replace('\n','')
        #return ''.join(self.content)
        return ''.join(cleanup(''.join(self.content).split(' ')))
    
    def characters(self,ch):
        self.content.append(ch)

def xmlToText(sourceStr):
    try:
        gentext = flatToTextHandler()
        xml.sax.parseString(sourceStr,gentext)
        return gentext.textvalue().encode('ascii','replace')
    except Exception,e:
        print 'unknown exception occurred trying to convert XML to text',e,sourceStr
        return ''

class emailBase(rend.Page):
    def getContents(self):
        return self.renderSynchronously()

    def render_sheetname(self,ctx):
        return self.sheetname

    def render_org(self,ctx):
        return settings['org']

    def render_linkname(self,ctx):
        return T.a(href=settings['servername'])[settings['servername']]

    def render_supportemail(self,ctx):
        return T.a(href="mailto:%s" % settings['support_mail'])[settings['support_mail']]


class inviteEmail(emailBase):
    """
    this is the base for sending email invites and can
    be used for public sheets (where auth is not required
    """
    
    docFactory = loaders.xmlfile('invite.xml',templateDir='templates')
    subject = 'Invite from %s' % settings['org']
    emailaddress = 'no-reply@%s' % settings['servername']

    def __init__(self,username,URL,sheetname):
        self.username = username
        self.URL = URL
        self.sheetname = sheetname

    def render_username(self,ctx):
        return self.username

    def render_url(self,ctx):
        return T.a(href=self.URL)[self.URL]


class inviteEmailExistingUser(inviteEmail):
    docFactory = loaders.xmlfile('inviteexisting.xml',templateDir='templates')

    def render_fqdn(self,ctx):
        return settings['servername']
        

class inviteEmailNewUser(inviteEmail):
    docFactory = loaders.xmlfile('invitenewuser.xml',templateDir='templates')

    def __init__(self,username,URL,sheetname,dest_addr):
        super(inviteEmailNewUser,self).__init__(username,URL,sheetname)
        self.dest_addr = dest_addr
        self.createURL = self.URL.parentdir().child('createaccount').add('emailaddr',self.dest_addr)
        print 'new URL is',str(self.createURL)

    def render_createaccount(self,ctx,data):
        return T.a(href=self.createURL)['http://%s/createaccount' % settings['servername']]


class newSheetEmail(emailBase):
    docFactory = loaders.xmlfile('newsheetmail.xml',templateDir='templates')

    def __init__(self,URL,sheetname):
        self.URL = URL
        self.sheetname = sheetname

    def render_url(self,ctx):
        return T.a(href=self.URL)[self.URL]

    def render_org(self,ctx):
        return settings['org']

class newImportMail(emailBase):
    subject = 'new spreadsheets available at %s' % settings['servername']
    emailaddress = 'import@%s' % settings['servername']
    docFactory = loaders.xmlfile('importmail.xml',templateDir='templates')

    def __init__(self,emailInfo):
        self.emailInfo = emailInfo

    def render_listsheets(self,ctx):

        return [T.div[
            T.span(style="font-weight:bold;")[
            T.a(href=i[0])[i[1]]],' located at ',
            T.a(href=i[0])[i[0]]
            ] for i in self.emailInfo]
        

class confirmEmail(emailBase):
    subject = 'please confirm your email address'
    emailaddress = 'no-reply@%s' % settings['servername']
    docFactory = loaders.xmlfile('confirmmail.xml',templateDir='templates')

    def __init__(self,emailaddr,confirmlink):
        self.emailaddr = emailaddr
        self.URL = confirmlink

    def render_link(self,ctx):
        return T.a(href=self.URL)[self.URL]
    
class resetPassword(confirmEmail):
    subject = 'instructions for changing your %s password' % settings['org']
    emailaddress = 'no-reply@%s' % settings['servername']
    docFactory = loaders.xmlfile('resetpasswdmail.xml',templateDir='templates')

    def render_emailaddr(self,ctx):
        return T.span(style="font-weight:bold")[self.emailaddr]

class ApiKeyMail(emailBase):
    subject = 'Your %s web services account information' % settings['org']
    emailaddress = 'no-reply@%s' % settings['servername']
    docFactory = loaders.xmlfile('apikeymail.xml',templateDir='templates')    

    def __init__(self,api_id,api_key):
        self.api_id = api_id
        self.api_key = api_key

    def render_apiid(self,ctx):
        return self.api_id

    def render_apikey(self,ctx):
        return self.api_key


class notifyEmailChange(emailBase):
    subject = 'Your email address registered with %s has changed' % settings['org']
    emailaddress = 'no-reply@%s' % settings['servername']
    docFactory = loaders.xmlfile('emailchange.xml',templateDir='templates')

    def __init__(self,newmailaddr):
        self.newmailaddr = newmailaddr

    def render_newmail(self,ctx):
        print '**** new mail addr is ',self.newmailaddr
        return self.newmailaddr

def sendMail(contentGen,target,subject = None,me = None):
    threads.deferToThread(sendMailInternal,contentGen,target,subject,me)
        
def sendMailInternal(contentGen,target,subject = None,me = None,displayName=None):
    if subject is None:
        subject = getattr(contentGen,'subject','Invite from %s' % settings['org'])
    if me is None:
        me = getattr(contentGen,'emailaddress','invite@%s' % settings['servername'])
    if displayName is None:
        displayName = getattr(contentGen,'displayname',settings['org'])

    xmlcontents = contentGen.getContents();
    text = xmlToText(xmlcontents)
    msg = createhtmlmail(text,xmlcontents,subject,me,target,displayName)

    sender = smtplib.SMTP()
    sender.connect(settings['smtpserver'])
    sender.sendmail(me,[target],msg)
    sender.close()


def createhtmlmail(text,html,subject,frommail,recipient,displayName):
    """Create a mime-message that will render HTML in popular
    MUAs, text in better ones"""

    # create the two parts of the MIME email - the text part and the HTML part.
    # we use UTF-8 encoding to be the safest (although it must be base64 encoded so
    # it takes up more space)
    
    plain = MIMEText(text)
    msg = MIMEText(html,'html','UTF-8')

    final = MIMEMultipart('alternative')
    final['Subject'] = subject
    final['From'] = '%s <%s>' % (displayName,frommail)
    final['To'] = recipient
    final['Date'] = formatdate()
    final.attach(plain)
    final.attach(msg)
    
    return final.as_string()
