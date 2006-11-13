# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

#
# utility classes for the web service proxy support
#

from twisted.web import client
from twisted.internet import reactor
from nevow.stan import Proto
from nevow import flat



class _Tags(object):
    transaction = Proto('transaction')
    transaction_ack = Proto('transaction_ack')
    request = Proto('request')
    response = Proto('response')
    param = Proto('param')
    result_set = Proto('result_set')
    value = Proto('value')
# stan tags for the transaction handler
tags = _Tags()



def fireCallbackURI(callbackURI,data):
    # make sure everything is utf-8 before continuing
    callbackURI = callbackURI.encode('utf-8')
    host,port,path = client._parse(callbackURI)[1:]
    factory = client.HTTPClientFactory(path,method='PUT',
                                       postdata=data)
    factory.noisy = False
    reactor.connectTCP(host,port,factory)
    return factory.deferred    


class ProxyResponse(object):

    def __init__(self,requests,results):
        self.requests = requests
        self.results = results

    def generateResponse(self):
        return tags.response[self.generateRequests()]

    def generateRequests(self):
        for index in range(0,len(self.requests)):
            req = self.requests[index]
            if 'reason' in req:
                yield tags.request(id=req['id'],status=req['status'],reason=req['reason'])[
                    self.generateResultSet(index)
                    ]
            else:
                yield tags.request(id=req['id'],status=req['status'])[
                    self.generateResultSet(index)
                    ]

    def generateResultSet(self,index):
        if index < len(self.results):
            valuelist = self.results[index]
            return tags.result_set[
                [tags.value(name=item['name'])[item['value']] for item in valuelist]
                ]

    

class WebServiceShell(object):
    """
    provide some basic methods for use by an object that is interfacing with
    external web services.
    
    """

    def validateRequest(self,parsedRequest):
        pass

    def _onSuccess(self,parsedRequest,callbackURI,results):
        resp = ProxyResponse([{'id':req['id'],'status':200} for req in parsedRequest.requests],
                           results)
        fireCallbackURI(callbackURI,flat.flatten(resp.generateResponse()))            

    def onFailure(self,defarg,parsedRequest,callbackURI):
        resp = ProxyResponse([{'id':req['id'],'status':500} for req in parsedRequest.requests],
                           [])
        fireCallbackURI(callbackURI,flat.flatten(resp.generateResponse()))                
