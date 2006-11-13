# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

from numbler.server.ssdb import ssdb
from twisted.web import http
import time

class SheetCookieHandler(object):
    maxremembersheets = 10

    def __init__(self,request):
        self.oldrecent = request.getCookie('recent')
        self.recent = request.getCookie('recentsheets')
        self.username = request.getCookie('sheetusername')
        self.request = request

    def _expires(self):
        return http.datetimeToString(time.time() + 60*60*24*14);

    def updateRecent(self):
        # the cookie expires in two weeks time
        self.request.addCookie('recentsheets',self.recent,
                               expires= self._expires(),path='/')
        
    def updateUserName(self,name):
        self.username = name
        self.request.addCookie('sheetusername',self.username,
                               expires= self._expires(),path='/')

    def touchRecent(self,siteID):
        """ ensure that the most recently loaded sheet stays
        is now at the top of the list """
        if self.recent is not None:
            self.recent = ''.join([siteID,self.recent.replace(siteID,'')])
            # truncate to the maximum numbler
            self.recent = self.recent[0:self.maxremembersheets*16]
        else:
            self.recent = siteID
        self.updateRecent()
        
    def addNewSheet(self,siteID):
        if self.recent:
            if self.recent.find(siteID) < 0:
                self.recent += siteID
        else:
            self.recent = siteID
        # the cookie expires in two weeks time
        #print 'addNewSheet called',siteID
        self.updateRecent()

    def recentSheets(self):
        if self.recent:
            recentpages = tuple([self.recent[x:x+16] for x in range(0,len(self.recent),16)])
            d = ssdb.getInstance().getSheetAliases(recentpages)
            d.addCallback(self.processAliases,recentpages)
            return d
        else:
            return None

    def processAliases(self,dbresults,recentpages):
        # create a dictonary so we can map the UID's to the sheet names.
        # this is necessary because we want to enable higher level layers to return
        # results in the order of the request rather than the DB order.
        retdict = {}
        for val in dbresults:
            retdict[val[1]] = val[0]
        return recentpages,retdict
        

    def rememberemail(self,email):
        self.request.addCookie('numbleremail',email,path='/',expires= self._expires())

    def getemail(self):
        email = self.request.getCookie('numbleremail')
        if email:
            return email
        else:
            return ''

    def forgetemail(self):
        self.request.addCookie('numbleremail','',path='/')

    def forgetoldsheets(self):
        self.request.addCookie('recent','',path='/')
