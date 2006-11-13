# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

from numbler.tac_common import *

start_psyco()
    

from twisted.application import service, strports,internet
from nevow import appserver
from numbler import livesheet
from numbler.utils import get_ip_address


# change if you have a different NIC
servicestr = "tcp:80:interface=" + get_ip_address('eth0')

# Note: Use the NumberContextFactory if you have a certificate
# that was issued by a commercial provider with a chain file.
# this code simply overides the DefaultOpenSSLConextFactory; there
# may be better support in twisted for this now.
#from numbler.sslutil import NumblerContextFactory
#sslContext = NumblerContextFactory('keys/yourSITE.key','keys/yourSITE.certificate')

sslContext = getBasicSSLContext()

import sys
sys.setrecursionlimit(5000)

site = appserver.NevowSite(livesheet.createResource(),logPath="web.log")
application = service.Application("sheet")

# turn on manhole (access to your app via SSH while it is running)
enableManhole(site,application)

strports.service(servicestr, site,sslContext).setServiceParent(application)
internet.SSLServer(443,site,sslContext).setServiceParent(application)

# Note: you should pass DNS the name of this box to the web service
# proxy otherwise the default is the local machine name
start_webservice_proxy()
