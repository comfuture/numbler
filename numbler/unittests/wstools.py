
from numbler import wsmanager
from numbler.wsmanager import wsDefinition,wsServiceManager,wsResponseManager,FormulaTxnManager
from nevow import rend,appserver
from twisted.application import strports,service
from twisted.internet import reactor,defer
from testtools import sheetTester

class ResponseRoot(rend.Page):

    def __init__(self):
        self.children = dict(wsresponse=wsResponseManager())


# configure the service manager to use port 9010
wsServiceManager.getInstance().configureServer('localhost',port=9010)

# turn off automatic asyncronous function refreshes
wsmanager.globalTxnMgr.refreshasync = False

class proxyHarness(sheetTester):
    """
    this derived from JML's post on howto safely disconnect in trial.
    http://blackjml.livejournal.com/23029.html
    """
    
    def setUp(self):
        super(proxyHarness,self).setUp()
        application = service.Application('wsproxy')
        self.responsesite = ResponseRoot()
        website = appserver.NevowSite(self.responsesite)
        self.listener = reactor.listenTCP(9010,website) # website

    def tearDown(self):
        super(proxyHarness,self).tearDown()
        d = defer.maybeDeferred(self.listener.stopListening)
        return d
