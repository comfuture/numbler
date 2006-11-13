# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

"""
EBAY API integration.  very basic at this point.

"""

from twisted.web import client,error
from twisted.internet import reactor,defer
import cElementTree as et
from cStringIO import StringIO
from pkg_resources import resource_filename
from tempfile import gettempdir
import cPickle,os,stat,time
from twisted.internet.task import LoopingCall
from numbler.inumbler import IRemoteWSProxy
from numbler.proxytools import WebServiceShell
from zope.interface import Interface,implements
from numbler.server.sslib import singletonmixin
from xml.dom.minidom import parseString
        


# get the ebay keys from the site_settings
from numbler.site_settings import settings
#production keys
production = settings['ebay']


commonHeaders = {
            'X-EBAY-API-COMPATIBILITY-LEVEL':'473',
            'X-EBAY-API-SESSION-CERTIFICATE':';'.join([production['DevID'],production['AppID'],production['CertID']]),
            'X-EBAY-API-DEV-NAME':production['DevID'],
            'X-EBAY-API-APP-NAME':production['AppID'],
            'X-EBAY-API-CERT-NAME':production['CertID'],
            'X-EBAY-API-SITEID':'0', # US
            }

# REST token

# TOsOybIPDNc%3D**XGhIHiMIaVX88oH%2Fy4qNxhL3tho%3D


def ebayRequest(body,callName):
        headers = commonHeaders
        headers['X-EBAY-API-CALL-NAME'] = callName
        d = client.getPage(production['url'],method='POST',headers=headers,postdata=body)
        return d
    


class ebayItemSearch(object):


    #<DetailLevel>ReturnAll</DetailLevel>
    #<!--<CategorySiteID>0</CategorySiteID> -->
    #    <DetailLevel>ItemReturnCategories</DetailLevel>

    #        <ItemTypeFilter>AllItemTypes</ItemTypeFilter>
    #         <SearchLocationFilter><CountryCode>US</CountryCode></SearchLocationFilter>

    def lookupItem(self,queryString,category=None):
        request = """
        <?xml version="1.0" encoding="utf-8"?>
        <GetSearchResultsRequest xmlns="urn:ebay:apis:eBLBaseComponents">
        <RequesterCredentials> 
        <eBayAuthToken>%s</eBayAuthToken> 
        </RequesterCredentials> 
        <Pagination>
        <EntriesPerPage>10</EntriesPerPage>
        </Pagination>        
        <query>%s</query>
        %s
        <DetailLevel>ReturnAll</DetailLevel>
        </GetSearchResultsRequest>
        """

        args = [production['authtoken'],queryString.encode('utf-8')]

        if category is not None:
            # lookup category
            catalog = eBayCatalog.getInstance()
            catcode = catalog.catalogdict.get(category.lower())
            if not catcode:
                print '*** catcode not found ***',category,len(eBayCatalog.catalogdict)
                # raise error here
            else:
                args.append('<CategoryId>%s</CategoryId>' % catcode)
        else:
            args.append('')


        body = request % tuple(args)
        #print body
        d = ebayRequest(body,'GetSearchResults')
        d.addCallback(self.processResults)
        return d

    class ebayItem(object):
        def __init__(self):
            self.url = ''
            self.price = ''

        def __str__(self):
            return '%s => %s' % (self.price,self.url)
        __repr__ = __str__

    def processResults(self,data):
        results = []
        citem = None
        #domtree = parseString(data)
        #print domtree.toprettyxml()

        for event,elem in et.iterparse(StringIO(data)):
            #print elem.tag
            if elem.tag == '{urn:ebay:apis:eBLBaseComponents}Item':
                citem = self.ebayItem()
                results.append(citem)
                for itemel in elem.getiterator():
                    if itemel.tag == '{urn:ebay:apis:eBLBaseComponents}ViewItemURL':
                        citem.url = itemel.text
                    elif itemel.tag == '{urn:ebay:apis:eBLBaseComponents}CurrentPrice':
                        citem.price = itemel.text
        return results        


class ebayItemLookup(WebServiceShell):
    implements(IRemoteWSProxy)

    def validateRequest(self,parsedRequset):
        pass

    def doRemoteRequest(self,arg,parsedRequest,callbackURI):
        request = parsedRequest.requests[0]
        params = request['params']

        searcher = ebayItemSearch()
        d = searcher.lookupItem(params['query'],params.get('category'))
        d.addCallback(self.onSuccess,parsedRequest,callbackURI)
        d.addErrback(self.onFailure,parsedRequest,callbackURI)
        return d

    def onSuccess(self,priceInfo,parsedRequest,callbackURI):
        #print priceInfo
        if not len(priceInfo):
            raise error.Error(500)
        firstval = priceInfo[0]
        results = [[{'name':'price','value':firstval.price.encode('utf-8')},
                    {'name':'url','value':firstval.url.encode('utf-8')}]]
        #print 'ebay results are ',results
        self._onSuccess(parsedRequest,callbackURI,results)


class eBayCatalog(singletonmixin.Singleton):

    catRequest = """
    <?xml version="1.0" encoding="utf-8"?> 
    <GetCategoriesRequest xmlns="urn:ebay:apis:eBLBaseComponents"> 
    <RequesterCredentials> 
        <eBayAuthToken>%s</eBayAuthToken> 
    </RequesterCredentials> 
    <CategorySiteID>0</CategorySiteID> 
    <DetailLevel>ReturnAll</DetailLevel> 
    <LevelLimit>%d</LevelLimit> 
    <ViewAllNodes>False</ViewAllNodes> 
    </GetCategoriesRequest> 
    """


    def __init__(self):
        self.catalogdict = {}
        self.catname = 'ebaycatalog.pickle'

    def makeRequest(self):

        body = self.catRequest % (production['authtoken'],3)

        d = ebayRequest(body,'GetCategories')
        d.addCallback(self.parseRequest)
        return d

    def parseRequest(self,data):
        currentCat = None
        tempcat = {}

        # save off the file. temporary hack!!
        domtree = parseString(data)
        f = open('/tmp/output.xml','w')
        f.write(domtree.toprettyxml().encode('utf-8'))
        f.close()
        
        try:
            for event,elem in et.iterparse(StringIO(data)):
                if elem.tag == '{urn:ebay:apis:eBLBaseComponents}Category':
                    for itemel in elem.getiterator():
                        if itemel.tag == '{urn:ebay:apis:eBLBaseComponents}CategoryID':
                            currentCat = itemel.text
                        if itemel.tag == '{urn:ebay:apis:eBLBaseComponents}CategoryName':
                            if itemel.text == 'Cycling':
                                print 'cycling found,value is',currentCat,itemel.text.lower() in tempcat
                            if itemel.text.lower() not in tempcat:
                                tempcat[itemel.text.lower()] = currentCat
        except Exception,e:
            print 'error loading catalog; keeping existing entries',e
        else:
            self.catalogdict = tempcat
            print 'catalog loaded, %d items' % (len(self.catalogdict),)

    def _catalogfile(self):
        return '/'.join([gettempdir(),self.catname])

    def archiveCatalog(self):
        """
        save off the current ebay catalog.
        """
        tmpf = self._catalogfile()
        fh = open(tmpf,'w+')
        cPickle.dump(self.catalogdict,fh)
        fh.close()

    def updateCatalog(self):
        return self.makeRequest().addCallback(lambda _: self.archiveCatalog())

    def loadCatalog(self):
        """ load the archived catalog.  This method assumes the catalog file exists """
        fh = open(self._catalogfile(),'r')
        self.catalogdict = cPickle.load(fh)
        fh.close()
        print 'catalog file loaded'

    def checkCatalog(self,installLoop=False):
        fname = self._catalogfile()
        try:
            mtime = os.stat(fname)[stat.ST_MTIME]
            if time.time() - mtime < 60*60*24:
                print 'file up to date'
                self.loadCatalog()
                if installLoop:
                    looper = LoopingCall(self.updateCatalog)
                    # run every 24 hours
                    return looper.start(60*60*24)
                else:
                    return defer.succeed(None)
        except:
            pass
        # if we got this far kick off an update
        return self.updateCatalog()

def main():

    def dumper(*args):
        print args

##    searcher = ebayItemSearch()
##    d = searcher.lookupItem('06 Giant TCR Composite')
##    d.addBoth(dumper)
##    d.addBoth(lambda _: reactor.stop())
##    reactor.run()
##    return
    
    catalog = eBayCatalog()
    d = catalog.checkCatalog()
    if not d.called:
        d.addErrback(dumper)
        d.addBoth(lambda _: reactor.stop())
        reactor.run()
    

if __name__ == '__main__' : main()


