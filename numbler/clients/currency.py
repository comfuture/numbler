# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

from twisted.web import client
from twisted.internet import reactor
import urllib
from numbler.inumbler import IRemoteWSProxy
from xml.dom.minidom import parseString
from xml import xpath
from numbler.proxytools import WebServiceShell
from zope.interface import Interface,implements

client.HTTPClientFactory.noisy = False

class currencyConversionService(WebServiceShell):

    implements(IRemoteWSProxy)

    targetURL = 'http://www.webserviceX.NET/CurrencyConvertor.asmx/ConversionRate'

    def validateRequest(self,parsedRequest):
        pass

    def doRemoteRequest(self,arg,parsedRequest,callbackURI):

        request = parsedRequest.requests[0]
        params = request['params']

        payload = urllib.urlencode({'FromCurrency':params['fromCurrency'],
                                    'ToCurrency':params['toCurrency']})
        d = client.getPage(self.targetURL,method='POST',
                           headers={'content-type':'application/x-www-form-urlencoded'},
                           postdata=payload)
        d.addCallback(self.onSuccess,parsedRequest,callbackURI)
        d.addErrback(self.onFailure,parsedRequest,callbackURI)
        return d

    def onSuccess(self,xmlcontent,parsedRequest,callbackURI):

        # TODO: this doesn't properly deal with batches
        
        doc = parseString(xmlcontent)
        xfactor = xpath.Evaluate('/double',doc)[0].firstChild.nodeValue

        results = [[{'name':'conversion','value':xfactor}]]
        self._onSuccess(parsedRequest,callbackURI,results)
