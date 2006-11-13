# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.
#
# this tac file is used for running in debug mode or
# in user mode an high number ports (8080)

from numbler.tac_common import *

start_psyco()

from twisted.application import service, strports,internet
from nevow import appserver
from numbler import livesheet
from numbler.utils import get_ip_address


# change if you have a different NIC to use.
servicestr = "tcp:8080:interface=" + get_ip_address('eth0')

# Note: Use the NumberContextFactory if you have a certificate
# that was issued by a commercial provider with a chain file.
# this code simply overides the DefaultOpenSSLConextFactory; there
# may be better support in twisted for this now.
#from numbler.sslutil import NumblerContextFactory
#sslContext = NumblerContextFactory('keys/yourSITE.key','keys/yourSITE.certificate')

sslContext = getBasicSSLContext()

import sys
sys.setrecursionlimit(5000)

httplogging = False

site = appserver.NevowSite(livesheet.createResource(),logPath="web.log")
application = service.Application("sheet")

# turn on manhole (access to your app via SSH while it is running)
enableManhole(site,application)

if httplogging:
	from twisted.protocols.policies import TrafficLoggingFactory
	logfactory = TrafficLoggingFactory(site,"http_log")
	strports.service(servicestr,logfactory).setServiceParent(application)
else:
	strports.service(servicestr, site).setServiceParent(application)

internet.SSLServer(8443,site,sslContext).setServiceParent(application)
start_webservice_proxy(port=8080)
