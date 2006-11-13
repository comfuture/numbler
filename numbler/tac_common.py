# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

import os
from twisted.internet import ssl

def start_psyco():
    """
    run psyco if it is installed
    """

    try:
        import psyco
        print "starting psyco..."
        import re
        psyco.cannotcompile(re.compile)
        psyco.full()
    except:
        pass    

class missingSSLInfo(Exception):
    """
    \a\a
    private key and certificate not found in keys.  please generate
    or install a openSSL key pair in keys.  Example:
    openssl genrsa > keys/private.pem
    openssl req -new -x509 -key keys/private.pem -out keys/cacert.pem -days 1000
    """
    def __str__(self):
        return self.__doc__


def getBasicSSLContext():
    """
    return an SSL context with the given keys.  error out
    if the keys don't exist.
    """
    # check for the existance of an SSL key
    if not os.path.exists('keys/private.pem') or not os.path.exists('keys/cacert.pem'):
        raise missingSSLInfo()

    return ssl.DefaultOpenSSLContextFactory('keys/private.pem','keys/cacert.pem')
    
    

def start_webservice_proxy(hostname = None,port=80,sslport=443):
    """
    configure and start the web service proxy.
    if your host is on the internet you should pass in
    the name of your server, eg. numbler.com, foobar.com, etc.
    """

    if not hostname:
        import socket
        hostname = socket.gethostname()
        print "** Using %s as the hostname for the web service proxy ** " % hostname
                

    from numbler.wsmanager import wsServiceManager
    wsServiceManager.getInstance().configureServer(hostname,port=port,sslport=sslport)
    
    # start up the proxy process
    from subprocess import Popen
    Popen(['twistd','-noy','wsproxy.tac','-l','proxy.log','--pidfile','wsproxy.pid'])
    
def enableManhole(site,application):
    from twisted.conch import manhole_tap
    manhole_tap.makeService({'telnetPort':'tcp:9001',
                             'sshPort':'tcp:9002','namespace':{'service':site},
                             'passwd':'passwd'}).setServiceParent(application)
