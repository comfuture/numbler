# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

import urllib
from twisted.internet import protocol,defer,reactor
from twisted.web import http,client,error
from xml import xpath
from xml.dom.minidom import parseString
from numbler.inumbler import IRemoteWSProxy
from numbler.proxytools import fireCallbackURI,WebServiceShell
from zope.interface import Interface,implements
from numbler.proxytools import ProxyResponse
from nevow import flat
from xml.parsers.expat import ExpatError

from numbler.site_settings import settings

client.HTTPClientFactory.noisy = False


class AwsRequest(object):
    """
    A request to amazon.  the accesKey and associateTag are obtained
    from the site settings.
    """

    basestr = 'http://webservices.amazon.com/onca/xml?Service=AWSECommerceService&'
    accessKey = settings['amazon_access_key']
    associateTag = settings['amazon_associateTag']
    agent = 'Numbler awsRequester'
    host = 'webservices.amazon.com'
    port = 80

    # override for specific handling
    operation = 'ItemSearch'
    responseGroup = 'OfferSummary'

    def __init__(self,keywords,params=None):

        #keywords = keywords.encode('utf-8')

        urlparams = [('AWSAccessKeyId',self.accessKey),
            ('Operation',self.operation),
            ('Keywords',urllib.quote(keywords)),
            ('AssociateTag',self.associateTag),
            #         ('ResponseGroup','OfferFull'),#'Offers,ItemAttributes'),
            ('ResponseGroup',self.responseGroup),
            #('SubCondition','acceptable'),
                     ]
        if params:
            urlparams.extend(params)

        url = ''.join([self.basestr,urllib.urlencode(urlparams)])
        headers = {'HOST':self.host,
                 'User-Agent':self.agent}

        self.deferredCall = client.getPage(url,headers=headers)

class awsPriceLookup(AwsRequest):

    def __init__(self,searchstr,xpathQuery,**kw):

        self.xpathQuery = xpathQuery
        extraargs = []
        if 'Condition' in kw:
            extraargs.append(('Condition',kw['Condition']))
        if 'SearchIndex' in kw:
            extraargs.append(('SearchIndex',kw['SearchIndex']))
        else:
            extraargs.append(('SearchIndex','Blended'))

        #print 'initing AwsRequest with',searchstr,extraargs
        super(awsPriceLookup,self).__init__(searchstr,extraargs)        
        self.deferredCall.addCallback(self.procResults)
        #self.usedPrices = []

    def procResults(self,xmlstr):
        try:
            domtree = parseString(xmlstr)
            #print domtree.toprettyxml()
            nodes = xpath.Evaluate('//Items/Item',domtree)
            self.usedPrices = []
            
            for awsItem in nodes:
                price = xpath.Evaluate(self.xpathQuery,awsItem)
                if price is not None and len(price) > 0:
                    pval = price[0].firstChild.nodeValue
                    asin = xpath.Evaluate('ASIN',awsItem)[0].firstChild.nodeValue
                    self.usedPrices.append((pval,asin))
            
        except ExpatError,e:
            print 'amazon.py: Error parsing response',e,xmlstr
            raise e
    
def dumper(arg):
    print arg




class amazonPriceService(WebServiceShell):
    """
    proxy for amazon used price lookup
    """

    
    def doRemoteRequest(self,arg,parsedRequest,callbackURI):
        """

        TODO: multiple transactions against the amazon API
        """
        request = parsedRequest.requests[0]
        keyword = request['params']['keywords']

        #print 'AWS used price called for keyword',keyword,type(keyword)
        if 'category' in request['params']:
            category = request['params']['category']        
            lookup = awsPriceLookup(keyword.encode('utf-8'),
                                    self.xpathQuery,
                                    SearchIndex=category.encode('utf-8'),Condition=self.Condition)
        else:
            lookup = awsPriceLookup(keyword.encode('utf-8'),
                                    self.xpathQuery,
                                    Condition=self.Condition)
        lookup.deferredCall.addCallback(self.getResultsCB,lookup,parsedRequest,callbackURI)
        return lookup.deferredCall

    def getResultsCB(self,defarg,awsLookup,parsedRequest,callbackURI):

        #print 'getREsultsCb called',awsLookup,awsLookup.usedPrices
        if len(awsLookup.usedPrices):
            usedPrice,ASIN = awsLookup.usedPrices[0]
        else:
            # raise a 500 error to simulate an error.  this isn't quite right obviously.
            raise error.Error(500)

        # generate a amazon referral URL
        amazonURL = 'http://www.amazon.com/exec/obidos/ASIN/%s/%s' % (ASIN,AwsRequest.associateTag)
        results = [[{'name':'cost','value':usedPrice},{'name':'itemURL','value':amazonURL}]]
        #print 'returning results:',results
        return self._onSuccess(parsedRequest,callbackURI,results)


class amazonUsedPriceService(amazonPriceService):
    implements(IRemoteWSProxy)
    Condition = 'Used'
    xpathQuery = 'OfferSummary/LowestUsedPrice/FormattedPrice'

class amazonNewPriceService(amazonPriceService):
    implements(IRemoteWSProxy)
    Condition = 'New'
    xpathQuery = 'OfferSummary/LowestNewPrice/FormattedPrice'

def main():

    def printResults(self,pricelookup):
        print 'Amazon used prices are',pricelookup.usedPrices
    
    import sys
    awstester = awsPriceLookup(sys.argv[1],'OfferSummary/LowestUsedPrice/FormattedPrice',Condition='Used',SearchIndex='Books')
    d = awstester.deferredCall
    d.addCallback(printResults,awstester)
    d.addBoth(dumper)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()

if __name__ == '__main__': main()
