# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

from twisted.application import strports, service
from nevow import appserver
from numbler.wsproxy import ProxyRoot
application = service.Application('wsproxy')
website = appserver.NevowSite(ProxyRoot())
webservice = strports.service('9005', website)
webservice.setServiceParent(application)