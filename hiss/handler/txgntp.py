# Copyright 2009-2012, Simon Kennedy, code@sffjunkie.co.uk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Part of 'hiss' the twisted notification library

import logging

from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientFactory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.protocols.basic import LineReceiver
from twisted.internet.error import ConnectionDone

from hiss.resource import Icon
from hiss.event import NotificationEvent

from hiss.handler import TargetList
from hiss.handler.gntp import GNTPError
from hiss.handler.gntp import GNTP_BASE_VERSION, GNTP_DEFAULT_PORT
from hiss.handler.gntp import Response
from hiss.handler.gntp import _SubscribeRequest, _RegisterRequest, _NotifyRequest
EVENT_MAPPING = {
    'CLICK': 0,
    'CLICKED': 0,
    'TIMEDOUT': 1,
    'TIMEOUT': 1,
    'CLOSED': 2,
    'CLOSE': 2,
}


class txGNTP(object):
    def __init__(self, response_handler=None):
        """Twisted Growl Network Transfer Protocol handler
        
        :param response_handler: A callable which is provided with an
                              :class:`hiss.NotificationEvent` when an GNTP
                              callback event is received.
        :type response_handler:  A callable
        """
    
        self._targets = TargetList()
        self._handler = response_handler
        self._factory = GNTPFactory(self._gtnp_event_handler)
    
    def connect(self, target):
        """Connect to a target
        
        :param target: Target to connect to
        :type target:  :class:`hiss.Target`
        """
        
        def connected(response):
            self._targets.append(target)
            return response
        
        def failed(failure):
            raise GNTPError('GNTP: Connection Failure')
        
        if target.port == -1:
            target.port = GNTP_DEFAULT_PORT
            
        if target.protocol_version == '':
            target.protocol_version = GNTP_BASE_VERSION
        
        if target not in self._targets:
            d = self._factory.connect(target)
            d.addCallback(connected)
            d.addErrback(failed)
            return d
        else:
            return defer.succeed(True)

    def disconnect(self, target):
        """Disconnect from a target
        
        :param target: Target to disconnect from
        :type target:  :class:`hiss.Target`
        :returns:      A :class:`defer.Deferred` which fires when
                       disconnected from the target 
        """
        
        if target in self._targets:
            protocol = self._factory.find_protocol(target.host, target.port)
            if protocol is not None:
                protocol.loseConnection()
            
            target.handler = None
            del self._targets[target]
            
            return defer.succeed(True)
        else:
            return defer.fail(False)
        
    def register(self, notifier, targets=None):
        """Register a notifier with a list of targets
        
        :param notifier: Notifier to register
        :type notifier:  :class:`hiss.Notifier`
        :param targets:  list of targets to register with or None to
                         register with all targets
        :type targets:   list of :class:`hiss.Target` or None
        :returns:        A :class:`defer.Deferred` to wait on
        """
        
        request = _RegisterRequest(notifier)
        targets = self._targets.valid_targets(targets)
        return self._factory._send_request(request, targets)
        
    def notify(self, notifier, notification, targets=None):
        """Send a notification to a list of targets
        
        :param notifier: Notification to send
        :type notifier:  :class:`hiss.Notification`
        :param targets:  list of targets to notify or None to
                         send to all targets
        :type targets:   list of :class:`hiss.Target` or None
        :returns:        A :class:`defer.Deferred` which fires when a response
                         has been received.
        """
        
        request = _NotifyRequest(notifier, notification)
        targets = self._targets.valid_targets(targets)
        return self._factory._send_request(request, targets)
    
    def subscribe(self, notifier, signatures=[], targets=None):
        """Subscribe to notifications from a list of signatures
        
        :param notifier:   Notifier to use.
        :type notifier:    :class:`hiss.Notifier`
        :param signatures: Application signatures to receive messages from
        :type signatures:  List of string or [] for all
                           applications
        :param targets:    list of targets to notify or None to
                           send to all targets
        :type targets:     list of :class:`hiss.Target` or None
        """
                           
        request = _SubscribeRequest(notifier)
        targets = self._targets.valid_targets(targets)
        return self._factory._send_request(request, targets)
    
    def unregister(self, notifier, targets=None):
        """Unregister a notifier with a list of targets
        
        :param notifier: Notifier to unregister
        :type notifier:  hiss.Notifier
        :param targets:  list of targets to unregister with or None to
                         unregister with all targets
        :type targets:   list of :class:`hiss.Target` or None
        :returns:        A :class:`defer.Deferred` which fires when a response
                         has been received.
        """
        
        return defer.succeed(True)
        
    def _gtnp_event_handler(self, response):
        event = NotificationEvent()
        event.nid = response.nid
        event.code = EVENT_MAPPING[response.status_name]
        event.data = response.data
            
        self._handler(event)


class GNTPFactory(ClientFactory):
    def __init__(self, response_handler=None):
        self._protocol_map = []
        self._handler = response_handler
        
    def connect(self, target):
        """Connect to a target.
        
        You must use this method to connect to a target otherwise everything
        else will fail."""
        
        def connected(value):
            logging.debug('GNTPFactory: Connected')
        
        protocol = GNTPProtocol(self._handler)
        protocol.factory = self
        
        self._protocol_map.append((target, protocol))
        
        point = TCP4ClientEndpoint(reactor, target.host, target.port)
        protocol.endpoint = point
        d = point.connect(self)
        d.addCallback(connected)
        return d
    
    def _send_request(self, request, targets):
        """Send a request to a list of targets
        
        :param request:  Request to send
        :type request:   :class:`hiss.Request`
        :param targets:  List of targets to send request to
        :type targets:   list of :class:`hiss.Target`
        :returns:        A :class:`defer.Deferred` or
                         :class:`defer.DeferredList` to wait on
        """

        data = request.request.marshall()
        
        ds = []
        for target in targets:
            logging.debug('Sending %s to %s' % (request.request.command, str(target)))
            logging.debug('%s' % data.replace('\r\n', '\n'))
            
            protocol = self._find_protocol_for_target(target)
            if protocol is not None:
                deferred = defer.Deferred()
                protocol.deferred = deferred
                protocol.send_data(data)
                
                ds.append(deferred)
        
        if len(ds) == 1:
            return ds[0]
        else:
            return defer.DeferredList(ds)

    def buildProtocol(self, address):
        for target, protocol in self._protocol_map:
            if target.host == address.host and target.port == address.port:
                return protocol
            else:
                raise GNTPError(('Unable to build protocol for address %s. '
                                'Ensure you use the connect method') % address)
    
    def _find_protocol_for_target(self, target):
        for t, protocol in self._protocol_map:
            if t == target:
                return protocol
        
        return None
    
    def clientConnectionLost(self, connector, reason):
        if issubclass(reason.type, ConnectionDone):
            connector.connect()


class GNTPProtocol(LineReceiver):
    """GNTPProtocol has 2 responsibilities
    
    1. Sends a single GNTPRequest and compiles a Response as data arrives.
       When a complete response is received it executes the callback on the
       deferred set up when sending the request.
       
    2. Compiles any callback data into an Response. When a complete response
       is received it calls the registered event handler 
    """
    
    def __init__(self, response_handler=None):
        """Initializes the instance and registers an event handler, if provided,
        called when an GNTP callback response is received.
        """
        
        self._data = ''
        self.deferred = None
        self._response = Response()
        self._handler = response_handler
    
    def lineReceived(self, line):
        """Receive lines of data"""
        
        logging.debug('Received: %s' % line)
        self._data += ('%s\r\n' % line)
        if self._data.endswith('\r\n\r\n'):
            logging.debug('GNTPProtocol: End of message marker')
            self._complete_response()
    
    def connectionLost(self, reason):
        if issubclass(reason.type, ConnectionDone):
            logging.debug('GNTPProtocol: connection Lost')
            if self._data != '':
                self._complete_response()
            self.endpoint.connect(self.factory)
            
    def _complete_response(self):
        logging.debug('GNTPProtocol: Complete response')
        
        responses = self._data.split('\r\n\r\n')
        self._data = ''
        
        for response in [r for r in responses if len(r)>0]:
            r = Response()
            r.unmarshall(response)
            
            logging.debug('GNTPProtocol: Command %s' % r.command)
        
            if r.isevent:
                if self._handler is not None:
                    self._handler(r)
            else:
                if self.deferred is not None:
                    self.deferred.callback(r)
                    self.deferred = None
            
    def send_data(self, data):
        """Send a single GNTP request."""
        
        self.transport.write(data)
    