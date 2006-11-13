# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

from twisted.internet import ssl

class NumblerContextFactory(ssl.DefaultOpenSSLContextFactory):
    """
    added support for certificate chaining
    """

    certchain = 'keys/chain.crt'

    def cacheContext(self):
        ctx = ssl.SSL.Context(self.sslmethod)
        ctx.use_certificate_chain_file(self.certchain)
        ctx.use_privatekey_file(self.privateKeyFileName)
        self._context = ctx        
