# Copyright 2009, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

import uuid
import types

from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientFactory, connectionDone

from hiss.notification import Notification
from hiss.protocol.message import Message, RegisterMessage, NotifyMessage
from utility import find_open_port

class NotifierProtocol(Protocol, object):
    def connectionMade(self):
        """Send a message to the Nub
        
        Called by the twisted framework
        """

        # Get the next notification and deferred from the queue
        self.msg, self.result = self.factory.next()
        self.transport.write(self.msg.to_raw())
        
        if not self.msg.has_callback:
            self.transport.loseConnection()
            self.result(None)

    def dataReceived(self, data):
        msg = Message()
        msg.from_raw(data)

        self.transport.loseConnection()
        self.result(msg)


class Notifier(ClientFactory, object):
    protocol = NotifierProtocol

    def __init__(self, reactor, uid=None, notifications=[]):
        if uid is None:
            self._id = uuid.uuid4()
        else:
            self._id = uid
        
        self._reactor = reactor
            
        self._name = ''
        self._icon = None
        
        self._nub = None
        self._queue = []        
        self._port = find_open_port(from_port=50000)

        self._notifications = {}
        for n in notifications:
            self._notifications[n.name] = n

    def name():
        def fget(self):
            return self._name
            
        def fset(self, name):
            self._name = name
            
        return locals()
        
    name = property(**name())
        
    def icon():
        def fget(self):
            return self._icon
            
        def fset(self, icon):
            self._icon = icon
            
        return locals()
        
    icon = property(**icon())
        
    def notifications():
        def fget(self):
            return self._notifications
            
        def fset(self, notifications):
            if type(notifications) == types.DictType:
                self._notifications = notifications
            else:
                raise TypeError('You must supply a dictionary type to notifications')  
            
        return locals()
        
    notifications = property(**notifications())

    def set_target(self, target):
        self._target = Target(target)

    def connected():
        def fget(self):
            return self._nub is not None
            
        return locals()
        
    connected = property(**connected())

    def run(self):
        #self._reactor.callInThread(
        pass
            
    def loop(self):
        pass

    def stop(self):
        pass

    def add_notification(self, notification):
        self._notifications[notification.name] = notification
    
    def get_notification(self, name):
        return self._notifications[name]

    def register(self, target=None):
        msg = RegisterMessage()
        msg.set_to(self)
        self.send(msg, target)
    
    def send(self, obj, target=None):
        if isinstance(obj, basestring):
            obj = self._notifications[obj]
            m = NotifyMessage()
            m.set_to(obj)
        elif isinstance(obj, Notification):
            m = NotifyMessage()
            m.set_to(obj)
        else:
            raise TypeError('You must either pass a Notification object or the name of a Notification object.')

        if target is not None:
            send_to = target
        elif self._target is not None:
            send_to = self._target
        else:
            raise ValueError('Valid target not specified. Either specifiy the target parameter or set Notifier.target.')
            
        msg = target.message()
        msg.set_to(m)
        msg.add_header('X-Hiss-Target', target)

        self._queue.append((msg, self.callback))
        self._reactor.connectTCP(send_to.address, send_to.port, self)

    def next(self):
        if len(self._queue) != 0:
            return self._queue.pop(0)
        else:
            return None

    def callback(self, *args, **kwargs):
        msg = args[0]
        print('callback')

