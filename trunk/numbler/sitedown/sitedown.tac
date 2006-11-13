from twisted.application import service, strports
from nevow import appserver
from sitedown import createResource,get_ip_address
servicestr = "tcp:80:interface=" + get_ip_address('eth0')

site = appserver.NevowSite(createResource())
application = service.Application("sitedown")
strports.service(servicestr, site).setServiceParent(application)


