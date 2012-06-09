# Copyright 2009-2011, Simon Kennedy, code@sffjunkie.co.uk
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

import re
import logging

from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientFactory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.protocols.basic import LineReceiver
from twisted.internet.error import ConnectionDone

from hiss.handler import TargetList
from hiss.resource import Icon
from hiss.event import NotificationEvent

logging.basicConfig(level=logging.DEBUG, format='%(message)s')

GNTP_SCHEME = 'gntp'
GNTP_DEFAULT_PORT = 23053
GNTP_DEFAULT_VERSION = '1.0'

EVENT_MAPPING = {
    'CLICK': 0,
    'CLICKED': 0,
    'TIMEDOUT': 1,
    'TIMEOUT': 1,
    'CLOSED': 2,
    'CLOSE': 2,
}

class GNTPError(Exception):
    pass
        

class GNTP(object):
    def __init__(self, event_handler=None):
        """Growl Network Transfer Protocol handler
        
        :param event_handler: A callable which is provided with an
                              :class:`hiss.NotificationEvent` when an SNP callback
                              event is received.
        :type event_handler:  A callable
        """
    
        self._targets = TargetList()
        self._event_handler = event_handler
        self._factory = GNTPFactory(self._gtnp_event_handler)
    
    def connect(self, target):
        """Connect to a target
        
        :param target: Target to connect to
        :type target:  :class:`hiss.Target`
        """
        
        def connected(response):
            self._targets.append(target)
            return response
        
        if target.port == -1:
            target.port = GNTP_DEFAULT_PORT
        
        if target not in self._targets:
            d = self._factory.connect(target)
            d.addCallback(connected)
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
        
        request = RegisterRequest(notifier)
        targets = self._targets.valid_targets(targets)
        return self._factory.send_request(request, targets)
        
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
        
        request = NotifyRequest(notifier, notification)
        targets = self._targets.valid_targets(targets)
        return self._factory.send_request(request, targets)
    
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
                           
        request = SubscribeRequest(notifier)
        targets = self._targets.valid_targets(targets)
        return self._factory.send_request(request, targets)
    
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
            
        self._event_handler(event)


class GNTPRequest(object):
    def __init__(self, version=GNTP_DEFAULT_VERSION, password=''):
        self.version = version
        self.command = ''
        self.header = {}
        self.sections = []
        self.identifiers = []
        self.password = password
        self.hash = None
        self.encryption = None
    
    def marshall(self):
        """Marshall the request ready to send over the wire."""
        
        data = 'GNTP/%s %s' % (self.version, self.command)
        if self.encryption is not None:
            data += ' %s:%s' % self.encryption
        else:
            data += ' NONE'
        
        if self.hash is not None:
            data += ' %s:%s.%s' % self.hash
            
        data += '\r\n'
        
        for name, value in self.header.items():
            data += '%s: %s\r\n' % (name, value)
        
        data += '\r\n'
        
        for section in self.sections:
            for name, value in section.items():
                data += '%s: %s\r\n' % (name, value)
        
            data += '\r\n'
            
        for identifier in self.identifiers:
            data += 'Identifier: %s\r\n' % identifier['Identifier']
            idata = identifier['data'] 
            data += 'Length: %d\r\n\r\n%s\r\n\r\n' % (len(idata), idata)
            
        return data
            
    def unmarshall(self, data):
        """Unmarshall data received over the wire into a valid request"""
        
        sections = data.split('\r\n\r\n')
        
        header_re = r'GNTP\/(?P<version>\d\.\d) (?P<command>[A-Z]+)( ((?P<encryptionAlgorithmID>\w+)\:(?P<ivValue>[a-fA-F0-9]+)|NONE)( (?P<keyHashAlgorithmID>\w+)\:(?P<keyHash>[a-fA-F0-9]+)\.(?P<salt>[a-fA-F0-9]+))?)?'
        header = sections[0]
        m = re.match(header_re, header)
            
        if m is not None:
            d = m.groupdict()
            self.version = d['version']
            self.command = d['command']
            
            if d['encryptionAlgorithmID'] is None:
                self.encryption = None
            else:
                self.use_encryption = True
                self.encryption = (d['encryptionAlgorithmID'],
                                   d['ivValue'])
            
            if d['keyHashAlgorithmID'] is None:
                self.hash = None
            else:
                self.use_hash = True
                self.hash = (d['keyHashAlgorithmID'],
                             d['keyHash'],
                             d['salt'])
                
            self._unmarshall_section(header.split('\r\n')[1:], self.header)
            
            info = None
            next_is_id = False
            for section in sections[1:]:
                if not next_is_id:
                    info = {}
                    self._unmarshall_section(section.split('\r\n'), info)
                    
                    if 'Identifier' in info:
                        next_is_id = True
                        self.identifiers.append(info)
                    else:
                        self.sections.append(info)
                elif info is not None:
                    info['data'] = section
                    next_is_id = False

            #for section in self.sections:
            #    for name, value in section.items():
            #        if value.startswith('x-growl-resource://'):
            #            value = value[19:]
            #            d = self.identifier_data(value)
            #            raise GNTPError('unmarshall: Unable to find data for identifier %s' % value)
            #            section[name] = d
        else:
            raise GNTPError('unmarshall: Invalid GNTP message')

    def _unmarshall_section(self, lines, info):
        for line in lines:
            try:
                name, value = line.split(':', 1)
                info[name] = value.strip()
            except:
                pass
            
    def identifier_data(self, identifier):
        for i in self.identifiers:
            if i['Identifier'] == identifier:
                return i['data']
        
        return ''

    def _encrypt(self):
        pass

    def _decrypt(self):
        pass


class GNTPResponse(object):
    """GNTP/1.0 -OK|-ERROR|-CALLBACK <encryptionAlgoritm>
    <header>: <value>
    """
    
    def __init__(self):
        self.version = '1.0'
        """The GNTP protocol version number of this response"""
        
        self.response_type = ''
        self.command = ''
        self.header = {}
        self.use_encryption = False
        self.encryption = None
        self.isevent = False

        self._lines = []
        
    def append(self, line):
        self._lines.append(line)
    
    def marshall(self):
        """Marshall the request ready to send over the wire."""
        
        data = 'GNTP/%s -%s' % (self.version, self.response_type)
        
        if self.use_encryption:
            self._encrypt()
            data += ' %s:%s' % self.encryption
        else:
            data += ' NONE\r\n'
        
        if self.command != '':
            data += 'Response-Action: %s\r\n' % self.command
        
        for name, value in self.header.items():
            data += '%s: %s\r\n' % (name.strip(), str(value).strip())
            
        return data
    
    def unmarshall(self, data=None):
        """Unmarshall data received over the wire into a valid request"""
        
        if data is not None:
            lines = data.split('\r\n')
        else:
            lines = self._lines
            
        header_re = ('GNTP\/(?P<version>\d\.\d) (?P<responsetype>\-?[A-Z]+)'
                     ' ((?P<encryptionAlgorithmID>\w+)\:(?P<ivValue>[a-fA-F0-9]+)|NONE)')
        m = re.match(header_re, lines[0])
        if m is not None:
            d = m.groupdict()
            self.version = d['version']
            self.response_type = d['responsetype'].lstrip('-')
            
            if self.response_type == 'ERROR':
                self.status_code = 1
            
            self.isevent = (self.response_type == 'CALLBACK')
            
            if d['encryptionAlgorithmID'] is None:
                self.encryption = None
            else:
                self.use_encryption = True
                self.encryption = (d['encryptionAlgorithmID'],
                                   d['ivValue'])
            
            for line in lines[1:]:
                if line != '':
                    try:
                        name, value = line.split(':', 1)
                        
                        value = str(value).strip()
                        if name == 'Response-Action':
                            self.command = value
                        elif name == 'Notification-ID':
                            self.nid = value
                        elif name == 'Notification-Callback-Result':
                            self.status_name = value
                        elif name == 'Notification-Callback-Context':
                            self.data = value
                        elif name == 'X-Timestamp':
                            self.timestamp = value
                        elif name == 'X-Message-Daemon':
                            self.daemon = value
                        elif name == 'Origin-Machine-Name':
                            self.host = value
                        elif name == 'Error-Code':
                            self.status_code = int(value)
                        elif name == 'Error-Description':
                            self.status_name = value
                        else:
                            if name not in self.header:
                                self.header[name] = value
                            else:
                                if not isinstance(self.header[name], list):
                                    self.header[name] = [self.header[name]]
                
                                self.header[name].append(value)
                    except ValueError:
                        logging.debug('GTNP::Unmarshall - Error splitting %s' % line)

    def _encrypt(self):
        pass

    def _decrypt(self):
        pass


class RegisterRequest(object):
    def __init__(self, notifier):
        request = GNTPRequest()
        request.command = 'REGISTER'
        request.header['Application-Name'] = notifier.name
        request.header['Notifications-Count'] = len(notifier.notification_classes)
            
        if notifier.icon is not None:
            if isinstance(notifier.icon, Icon):
                uid = notifier.icon.uid
                data = notifier.icon.data
            else:
                request.header['Application-Icon'] = notifier.icon
        
        for info in notifier.notification_classes.values():
            section = {}
            section['Notification-Name'] = info.name
            section['Notification-Enabled'] = info.enabled
                    
            request.sections.append(section)
        
        self.request = request


class NotifyRequest(object):
    def __init__(self, notifier, notification):
        request = GNTPRequest()
        request.command = 'NOTIFY'
        request.header['Application-Name'] = notifier.name
        request.header['Notification-Name'] = notification.name
        request.header['Notification-ID'] = notification.uid
        request.header['Notification-Title'] = notification.title
        
        if notification.text is not None:
            request.header['Notification-Text'] = notification.text
        
        if notification.callback is not None:
            request.header['Notification-Callback-Context'] = \
                notification.callback.command
            request.header['Notification-Callback-Context-Type'] = \
                'string'
        
        self.request = request
        
        
class SubscribeRequest(object):
    def __init__(self, notifier):
        request = GNTPRequest()
        request.command = 'SUBSCRIBE'
        request.header['Subscriber-ID'] = notifier.uid
        request.header['Subscriber-Name'] = notifier.name
        
        self.request = request
        

class GNTPFactory(ClientFactory):
    def __init__(self, event_handler=None):
        self._protocol_map = []
        self._event_handler = event_handler
        
    def connect(self, target):
        """Connect to a target.
        
        You must use this method to connect to a target otherwise everything
        else will fail."""
        
        protocol = GNTPProtocol(self._event_handler)
        protocol.factory = self
        
        self._protocol_map.append((target, protocol))
        
        point = TCP4ClientEndpoint(reactor, target.host, target.port)
        protocol.endpoint = point
        d = point.connect(self)
        return d
    
    def send_request(self, request, targets):
        """Send a request to a list of targets
        
        :param request:  Request to send
        :type request:   :class:`hiss.Request`
        :param targets:  List of targets to send request to
        :type targets:   list of :class:`hiss.Target`
        :returns:        A :class:`defer.Deferred` or
                         :class:`defer.DeferredList` to wait on
        """
        
        ds = []
        for target in targets:
            logging.debug('Sending to %s' % str(target))
            
            data = request.request.marshall()
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
    
    1. Sends a single GNTPRequest and compiles a GNTPResponse as data arrives.
       When a complete response is received it executes the callback on the
       deferred set up when sending the request.
       
    2. Compiles any callback data into an GNTPResponse. When a complete response
       is received it calls the registered event handler 
    """
    
    def __init__(self, event_handler=None):
        """Initializes the instance and registers an event handler, if provided,
        called when an GNTP callback response is received.
        """
        
        self._data = ''
        self.deferred = None
        self._response = GNTPResponse()
        self._event_handler = event_handler
    
    def lineReceived(self, line):
        """Receive lines of data"""
        
        logging.debug('Received: %s' % line)
        self._data += ('%s\r\n' % line)
    
    def connectionLost(self, reason):
        if issubclass(reason.type, ConnectionDone):
            responses = self._data.split('\r\n\r\n')
            self._data = ''
            
            for response in [r for r in responses if len(r)>0]:
                r = GNTPResponse()
                r.unmarshall(response)
            
                if r.isevent:
                    if self._event_handler is not None:
                        self._event_handler(r)
                else:
                    if self.deferred is not None:
                        self.deferred.callback(r)
                        self.deferred = None
            
            # And so it goes around...
            self.endpoint.connect(self.factory)
            
    def send_data(self, data):
        """Send a single GNTP request."""
        
        self.transport.write(data)
    