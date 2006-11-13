# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.
#
# start of some interfaces for the remote web services support.
# not fully baked yet.


from zope.interface import Interface,implements

class IRemoteWSProxy(Interface):

    def validateRequest(self,parsedRequest):
        """
        parsedRequest contains the parsed XML request for use
        by the web service.  this method should raise a parse error
        if the contents are not accepatble (e.g bad parameter)

        the returned value should be a deferred that is executed
        later when appropriate to make the remote web service request.
        """

    def doRemoteRequest(self,arg,parsedRequest,callbackURI):
        """
        process the remote request and return the value on the callback URI.
        """
