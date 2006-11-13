# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

from twisted.internet import protocol
from twisted.internet import reactor,defer
from numbler.server.sslib.utils import alphaguid16
import os

from gzip import GzipFile

class GnumericConverter(protocol.ProcessProtocol):
    """ this class calls out to the gnumeric spreadsheet converter
    program to translate an excel file to the gnumeric XML representation.

    ssconvert can actually support lots of differnt file types and right now we
    are assuming that the input file will be XLS.  this could change obviously
    """

    def __init__(self,data,ondonecb):
        """ data is assumed right now to be all of the data from the file """
        self.data = data
        self.ondonecb = ondonecb

        self.infname = os.sep.join(['/tmp',alphaguid16()+'.xls'])
        self.ofname = os.sep.join(['/tmp',alphaguid16()+'.xls'])

        ifile = open(self.infname,'w+')
        ifile.write(data)
        ifile.close()
        self.errdata = []

    def startprocess(self):
        reactor.spawnProcess(self,"ssconvert",["ssconvert","-T","Gnumeric_XmlIO:xml_sax",
                                                    self.infname,self.ofname],{})

    def processEnded(self,status_object):
        # gnumeric outputs its files in with gzipped compression.
        # we need to extract that information.  Note we don't
        # actually read the file here but delay the read until later.
        
        try:
            data = GzipFile(self.ofname)
        except Exception,e:
            failure = e
            data = None

        if self.infname:
            try:
                os.unlink(self.infname)
            except:
                print 'warning: couldnt delete file',self.infname
        if self.ofname:
            try:
                os.unlink(self.ofname)
            except:
                print 'warning: couldnt delete file',self.ofname

        if data:
            self.ondonecb.callback(data)
        else:
            self.ondonecb.errback((failure,''.join(self.errdata)))


    def errReceived(self, data):
        self.errdata.append(data)



def tester():
    import sys

    def ondonesuccess(arg):
        print 'Success! reactor stopped'
        print arg.read()
        reactor.stop()
        
    def ondonefailure(arg):
        #print arg,type(arg),arg.value
        print 'Failure. reactor stopped'
        for val in arg.value:
            print val
        reactor.stop()


    if len(sys.argv) < 2:
        print 'file name required'
        return

    data = open(sys.argv[1],'rb')
    d = defer.Deferred()
    d.addCallbacks(ondonesuccess,ondonefailure)
    converter = GnumericConverter(data.read(),d)
    converter.startprocess()
    reactor.run()
                         
if __name__ == '__main__': tester()
