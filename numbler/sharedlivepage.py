# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.
#
# Share livepage framework
#

from nevow import athena,tags as T, stan,url
import time
import cPickle as pickle
from nevow import flat
from twisted.internet import reactor,defer
from twisted.python import log
import types

class SharedLivePage(athena.LivePage):
    """ Support for livepage implementations that are designed to be shared
    across multiple users (aka chatola)

    clients: the list of currently connected users
    events: list of all persisted and current events generated by users.
    sendeventupdate: set this to false if you want to defer event updates.

    """
    TRANSPORTLESS_DISCONNECT_TIMEOUT = 60


    def __init__(self,factory):
        # the athena.LivePage implementation has a class variable for the factory
        # this won't work for us because we want to associate a livepage object
        # with different URL's and isolate the client handles.
        self.factory = factory;
        self.events = []
        self.sendeventupdate = True
        super(SharedLivePage,self).__init__(jsModuleRoot=url.here.parentdir().child('athenajs'))


    def locateMethod(self,ctx,methodName):
        # instead of using the newstyle interface support we assume that derrived
        # classes will have the livepage methods on the page class.  Boo hoo
        # if this doesn't support the fancy interface abstraction of athena.
        return getattr(self,methodName)

##      def onAddClient(self,ctx,client):
##              """ handle when a new client joins """
##              pass

##      def onRemoveClient(self,client):
##              """ called when a client is removed """
##              pass

    def onSendEvent(self,source,persist,*event):
        """ called when sendEvent is called """
        pass

    def errHandler(self,error,clientID):
        """ called when a remote call fails."""
        log.msg("remote call to client %s failed" % (clientID))
        if error.value:
            if error.value.args:
                for arg in error.value.args:
                    if type(arg) in types.StringTypes:
                        log.msg(arg)
                    else:
                        for item in arg:
                            try:
                                log.msg("%s: %s" % (item,arg[item]))
                            except:
                                log.msg("%s" % (item))
                                
            else:
                log.msg(error.value)

    def send(self,clientID,event):
        #print 'SharedLivePage:send: ',clientID,event
        d = self.factory.clients[clientID].callRemote(event[0],*event[1:])
        d.addErrback(self.errHandler,clientID)
        return d

    def catchuponevents(self,client):
        """ catch up the client with the current events """
        #print 'catching up on %d events' % (len(self.events))
        for source,event in self.events:
            # skip deleted events
            if event:
                self.send(source,event)

    def nexteventid(self):
        """ returns the next event. Useful for removing an event
        if necessary """
        return len(self.events)

    def removeevent(self,id):
        """ remove an existing event.  Useful for an undo mechanism
        where you don't want to broadcast events to new clients"""
        #print 'removing event ',self.events[id][1]
        self.events[id] = (None,None)

    def broadcastEvent(self,*event):
        """ broadcasts an event to all parties and persists the event """
        return self.sendEvent(None,*event)

    def sendEvent(self, source, *event):
        """ send an event to all parties except the source and persist the event """

        # NOTE: this no longer persists the event!!
        return self._internalsendEvent(source,False,event)

    def broadcastTransientEvent(self,*event):
        """ broadcast event which is not saved for future clients """
        return self.sendTransientEvent(None,event)

    def sendTransientEvent(self,source,*event):
        """ send an event which is not saved for future clients"""
        return self._internalsendEvent(source,False,event)

    def _internalsendEvent(self, source,persist, *event):
        ret = None
        if persist:
            self.events.append((source, event))
        self.onSendEvent(source,persist,event)
        for target in self.factory.clients.keys():
            if source is None or target is not source:
                d = self.send(target,*event)
                if target == self.clientID:
                    ret = d
        return ret
                


class CaptureSharedPage(SharedLivePage):
    """ captures all events on a livepage for later replay.
    event time are captured so the events can be replayed as
    they occured in real time """

    def __init__(self):
        SharedLivePage.__init__(self)
        self.captureevents = []



    def onSendEvent(self,source,persist,*event):
        """ captures all events for later replay """
        self.captureevents.append((flat.flatten(event),time.time()))
        super(CaptureSharedPage,self).onSendEvent(source,persist,event)


    def topickle(self):
        # use pickle protocol 2
        return pickle.dumps(self.captureevents,2)



class ReplayLivePage(SharedLivePage):
    """ replay a captured livepage"""

    def __init__(self):
        SharedLivePage.__init__(self)
        self.replayevents = []



    def getPickleStr(self):
        raise assertionError('derived class must implement getPickleStr')

    def goingLive(self,ctx,client):
        self.client = client;
        self.replayevents = pickle.loads(self.getPickleStr())

    def startreplay(self):
        if not len(self.replayevents):
            return

        event,start = self.replayevents[0]
        self.client.send(event)         
        for delayedevent,nexttime in self.replayevents[1:]:
            reactor.callLater(nexttime - start,self.client.send,delayedevent)


class SharedPageTimedMutex(object):
    """
    lock an arbitrary resource to a single client.

    The intent is lock a single resource with mutex like behavior.  However,
    given the web design of a livepage you can't assume that the other
    end hasn't terminated the conneciton or has simply walked away
    from computer.  Therefore, this class implements a timer such that
    the mutex is only locked for the period of time (if no activity is detected)

    """

    def __init__(self,timeout = 30):
        self.timeout = timeout
        self.owner = None
        self.locked = False
        self.timer = None
        self.delayedcall = None

    def updatelock(self,client):
        if self.owner == client:
            assert self.delayedcall.active()
            # reset the timer
            self.delayedcall.reset(self.timeout)
            return True
        else:
            return False


    # acquire the lock for the particular client handle
    def acquire(self,client,cb):
        """ acquire the mutex and return true, false otherwise.
        the call back is fired when the lock times out """
        if not self.locked:
            self.locked = True
            self.owner = client

            def onexpire():
                cb(client)
                self.release(client)

            self.delayedcall = reactor.callLater(self.timeout,onexpire)
            return True
        else:
            return self.updatelock(client)

    # release the lock
    def release(self,client):
        """ release the mutex.  this also should be called if the client goes away """
        if self.owner == client:
            if self.delayedcall.active():
                self.delayedcall.cancel()
            self.delayedcall = None
            self.locked = False
            self.owner = None


def testtimemutex():

    mt = SharedPageTimedMutex(5)
    client1 = 'foo'
    client2 = 'bar'

    def onexpire(client):
        print 'expired client: ',client

    def acquire(testclient):
        if mt.acquire(testclient,onexpire):
            print 'acquired mutex for ',testclient
        else:
            print 'failed to acquire',testclient

    reactor.callLater(1,acquire,client1)
    reactor.callLater(2,acquire,client2)
    reactor.callLater(7,acquire,client2)
    reactor.callLater(11,reactor.stop)
    reactor.run()

if __name__ == "__main__":
    testtimemutex()

