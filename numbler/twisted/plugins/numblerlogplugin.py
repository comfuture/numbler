# (C) Numbler LLC 2006
# See LICENSE for details.

from twisted.python import log
from twisted.plugin import IPlugin
from zope.interface import implements

class NumblerLogger(object):
    implements(IPlugin,log.ILogObserver)

    def __repr__(self):
        return 'custom logger for Numbler to include seconds'

    def setFile(self,f):
        self.filelogger = log.FileLogObserver(f)
        self.filelogger.timeFormat = "%Y/%m/%d %H:%M:%S %Z"

    def emit(self,eventDict):
        self.filelogger.emit(eventDict)

    def start(self):
        self.filelogger.start()

    def stop(self):
        self.filelogger.stop()

NumblerLoggerObj = NumblerLogger()
