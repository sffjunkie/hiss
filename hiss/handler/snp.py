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

import base64
import logging
import random
import string
import hashlib
from collections import namedtuple

from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientFactory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.protocols.basic import LineReceiver

from hiss.resource import Icon
from hiss.event import NotificationEvent

log = logging.getLogger('hiss')
log.setLevel(logging.DEBUG)
console = logging.StreamHandler()
log.addHandler(console)

SNP_SCHEME = 'snp'
SNP_DEFAULT_PORT = 9887
SNP_DEFAULT_VERSION = '3.0'
SNP_VALID_VERSIONS = ['2.0', '3.0']

SNARL_STATUS = {
    0:   'OK',
    101: 'Failed',
    106: 'Bad Socket',
    107: 'Bad Packet',
    108: 'Invalid Argument',
    109: 'Argument Missing',
    121: 'Access Denied',
    301: 'Reserved',
    303: 'TimedOut',
    304: 'Clicked',
    307: 'Closed',
    308: 'ActionSelected',
}

BOOL_MAPPING = {
    1: '1',
    True: '1',
    'true': '1',
    'yes': '1',
    0: '0',
    False: '0',
    'false': '0',
    'no': '0',
}

def snp64(data):
    data = base64.encode(data)
    data = data.replace('\r\n', '#')
    data = data.replace('=', '%')
    return data


class SNPError(Exception):
    pass


SNPCommand = namedtuple('SNPCommand', ['name', 'parameters'])


class SNPRequest(object):
    def __init__(self, version=SNP_DEFAULT_VERSION, password='', use_hash=False):
        self.version = version
        self.commands = []
        self.password = password
        self.use_hash = use_hash
        self.hash = None
        self.cypher = None
        
    def append(self, command, **kwargs):
        """Append a command to the message
        
        :param command:  The command to append
        :type command:   A 2 element tuple containing a name and a dictionary
                         of parameters or
                         A separate command name as a string and keyword 
                         arguments
        """
        
        if self.version == '2.0' and len(self.commands) == 1:
            raise SNPError(("Version 2.0 messages don't "
                              "support multiple commands"))
        
        if len(kwargs) != 0:
            self.commands.append(SNPCommand(command, kwargs))
        else:
            if isinstance(command, tuple):
                self.commands.append(SNPCommand(command[0], command[1]))
            else:
                self.commands.append(SNPCommand(command, {}))
    
    def marshall(self):
        """Marshall the request ready to send over the wire."""
        
        if self.version == '2.0':
            return self._marshall_20()
        elif self.version == '3.0':
            return self._marshall_30()
        elif self.version == '1.0':
            raise SNPError('SNP protocol version 1.0 is unsupported.')
    
    def unmarshall(self, data):
        """Unmarshall data received over the wire into a valid request"""
        
        if data.lower().startswith('snp://'):
            self._unmarshall_20(data)
        elif data.startswith('SNP/3.0'):
            self._unmarshall_30(data)
        else:
            raise SNPError('Invalid SNP Request.')

    def _marshall_20(self):
        data = self._marshall_command(self.commands[0])
        return 'snp://%s\r\n' % data
    
    def _marshall_30(self):
        if self.use_hash and self.password != '':
            data = 'SNP/3.0 %s\r\n' % self._hash()
        else:
            data = 'SNP/3.0\r\n'
            
        for command in self.commands:
            data += '%s\r\n' % self._marshall_command(command)

        data += 'END\r\n'
        return data 

    def _marshall_command(self, command):
        if len(command[1]) == 0:
            return command.name
        else:
            data = ''
    
            names = command.parameters.keys()
            names.sort()
    
            for name in names:
                value = command.parameters[name]
                if isinstance(value, list):
                    for item in value:
                        item = self._escape(self._expand_tuple(item))
                        data += '%s=%s&' % (name, item)
                else:
                    value = self._escape(self._expand_tuple(value))
                    data += '%s=%s&' % (name, value)
                
            data = data[:-1]
            
            if len(data) > 0:
                return '%s?%s' % (command.name, data)
            else:
                return command.name

    def _unmarshall_20(self, data):
        data = data[6:].strip('\r\n')
        command = self._extract_command(data)           
        self.commands = [command]
        self.version = '2.0'

    def _unmarshall_30(self, data):
        if not data.endswith('END\r\n'):
            raise SNPError('Invalid SNP 3.0 request')
        
        data = data[:-2]
        lines = data.split('\r\n')
        header = lines[0]

        try:
            items = header.split(' ')
            if len(items) == 3:
                self.cypher = tuple(items[2].split(':'))
                
            if len(items) >= 2:
                hash_and_salt = items[1]
                htype, rest = hash_and_salt.split(':')
                hkey, hsalt = rest.split('.')
                self.hash = (htype.lower(), hkey, hsalt)
        except:
            raise SNPError('Invalid SNP header format: %s' % str(header))
        
        self.commands = []
        for line in lines[1:-1]:
            self.commands.append(self._extract_command(line))

        self.version = '3.0'

    def _extract_command(self, data):
        try:
            command, rest = data.split('?', 1)
    
            params = {}
            items = rest.split('&')
            for item in items:
                name, value = item.split('=', 1)
                value = self._unescape(value)
                
                params[name] = value
                
            return SNPCommand(command, params)
        except:
            raise SNPError('Invalid command format found: %s', str(data))

    def _expand_tuple(self, t):
        if isinstance(t, tuple):
            return '%s,%s' % (str(t[0]), str(t[1]))
        else:
            return str(t)

    def _escape(self, data):
        data = data.replace('\r\n', '\\n')
        data = data.replace('\n', '\\n')
        data = data.replace('&', '&&')
        data = data.replace('=', '==')
        return data

    def _unescape(self, data):
        data = data.replace('==', '=')
        data = data.replace('&&', '&')
        data = data.replace('\\n', '\r\n')
        return data
        
    def _salt(self):
        # http://stackoverflow.com/a/2257449
        s = ''.join(random.choice(string.ascii_uppercase + \
                                         string.digits) for _x in range(8))
        try:
            return bytes(s, 'UTF-8')
        except TypeError:
            return bytes(s)

    def _password(self):
        try:
            return bytes(self.password, 'UTF-8')
        except TypeError:
            return bytes(self.password)

    def _hash(self):
        if self.password == '':
            raise SNPError('Password not set. Required for hash generation.')

        salt = self._salt()
        h = hashlib.sha256()
        h.update(self._password())
        h.update(salt)
        
        self.hash = ('sha256', h.hexdigest(), salt)

        return '%s:%s.%s' % self.hash


class SNPResponse(object):
    def __init__(self):
        self.version = ''
        """The SNP protocol version number of this response"""
            
        self.max_version = ''
        """The maximum SNP protocol version the SNP receiver can handle"""
            
        self.status_code = 200
        """The status code for the response
        
        100-199 = System or transport error
        200-299 = Application errors
        300-399 = Events
        """
        
        self.data = ''
        self.isevent = False
        self.headers = {}
        
        self._lines = []
        
    def append(self, line):
        """Append a line of data"""
        
        if len(self._lines) == 0:
            if line.count('/') == 1:
                self.version = '3.0'
            else:
                self.version = '2.0'
        
        self._lines.append(line)
        
    def iscomplete():
        doc = """Test if a complete response has been received"""
        
        def fget(self):
            if self.version == '3.0':
                return self._lines[-1] == 'END'
            else:
                return True
            
        return locals()
    
    iscomplete = property(**iscomplete())
    
    def reset(self):
        self._data = []
    
    def unmarshall(self):
        """Unmarshall _data received over the wire into a valid response"""

        if self.version == '2.0':
            self._unmarshall2()
        elif self.version == '3.0':
            self._unmarshall3()
    
    def _unmarshall2(self):
        elems = self._lines[0].split('/')
        self.max_version = elems[1]
        self.status_code = int(elems[2])
        
        try:
            self.status_name = SNARL_STATUS[self.status_code]
        except:
            self.status_name = 'Unknown'
            
        self.isevent = (self.status_code >= 300 and self.status_code <= 399)
        
        if len(elems) > 4:
            self.data = elems[4]
            if self.isevent:
                self.nid = elems[4]
            else:
                self.nid = ''

    def _unmarshall3(self):
        header = self._lines[0]
        items = header.split(' ')
        
        _snp, self.max_version = items[0].split('/')
        
        if len(items) > 1:
            self.status = items[1].lower()
            self.isevent = (self.status == 'callback')
        else:
            self.isevent = False
        
        if len(items) > 2:
            self.hash_type = items[2]
            
        if len(items) > 3:
            self.cypher_type = items[3]

        self.nid = ''
        for line in self._lines[1:-2]:
            name, value = line.split(':', 1)
            value = value.strip()
            
            if name == 'event-code':
                self.status_code = int(value)
            elif name == 'event-name':
                self.status_name = value
            elif name == 'notification-uid':
                self.nid = value
            elif name == 'event-data':
                self.data = value

            if name not in self.headers:
                self.headers[name] = value
            else:
                if not isinstance(self.headers[name], list):
                    self.headers[name] = [self.headers[name]]

                self.headers[name].append(value)
                    

class VersionRequest(object):
    def __init__(self):
        self.commands = [('version', {})]
                    

class RegisterRequest(object):
    def __init__(self, notifier):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = notifier.signature
        parameters['title'] = notifier.name
        parameters['password'] = notifier.uid
        
        icon = notifier.icon
        if icon is not None:
            if isinstance(icon, Icon):
                data = snp64(icon.data)
                parameters['icon-phat64'] = data
            else:
                parameters['icon'] = icon
        
        self.commands.append(('register', parameters))

        for class_id, info in notifier.notification_classes.items():
            parameters = {}
            parameters['app-sig'] = notifier.signature
            parameters['id'] = class_id
            parameters['password'] = notifier.uid
            parameters['name'] = info.name
            parameters['enabled'] = BOOL_MAPPING[info.enabled]

            if info.icon is not None:
                if isinstance(info.icon, Icon):
                    data = snp64(icon.data)
                    parameters['icon-base64'] = data
                else:
                    parameters['icon'] = info.icon
            
            self.commands.append(('addclass', parameters))


class ClearClassesRequest(object):
    def __init__(self, notifier):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = notifier.signature
        parameters['password'] = notifier.uid
        
        self.commands.append(('clearclasses', parameters))


class UnregisterRequest(object):
    def __init__(self, notifier):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = notifier.signature
        parameters['password'] = notifier.uid
        
        self.commands.append(('unregister', parameters))


class NotifyRequest(object):
    def __init__(self, notifier, notification):
        self.commands = []

        parameters = {}
        if notification.notifier is not None:
            parameters['app-sig'] = notification.notifier.signature
            parameters['password'] = notification.notifier.uid
         
        #TODO: What was this for?   
        #if notification.signature != '':
        #    parameters['app-sig'] = notification.signature
        
        if notification.class_id != '':
            parameters['id'] = notification.class_id
            
        parameters['title'] = notification.title
        parameters['text'] = notification.text
        
        if notification.uid != '':
            parameters['uid'] = notification.uid

        if notification.icon is not None:
            if isinstance(notification.icon, Icon):
                data = snp64(notification.icon.data)
                parameters['icon-base64'] = data
            else:
                if notification.icon == '':
                    icon = notifier.icon
                else:
                    icon = notification.icon
                    
                parameters['icon'] = icon
                
        if notification.timeout != -1:
            parameters['timeout'] = notification.timeout
            
        if notification.sticky:
            parameters['timeout'] = 0
            
        if notification.callback is not None:
            parameters['callback'] = notification.callback[0]
            if notification.callback[1] != '':
                parameters['callback-label'] = notification.callback[1]

        # Clamp priority to +-1        
        priority = notification.priority
        if priority < -1:
            priority = -1
        elif priority > 1:
            priority = 1
        parameters['priority'] = priority
        
        if notification.percentage != -1:
            parameters['value-percent'] = notification.percentage
        
        if len(notification.actions) > 0:
            parameters['action'] = []
            for cmd, label in notification.actions:
                parameters['action'].append((label, cmd))
        
        self.commands.append(('notify', parameters))


class SubscribeRequest(object):
    def __init__(self, notifier, signatures):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = signatures
        parameters['password'] = notifier.uid
        
        self.commands.append(('subscribe', parameters))


class AddActionRequest(object):
    def __init__(self, notifier, notification, command, label):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = notifier.signature
        parameters['uid'] = notification.uid
        parameters['password'] = notifier.uid
        parameters['cmd'] = command
        parameters['label'] = label
        
        self.commands.append(('addaction', parameters))


class ClearActionsRequest(object):
    def __init__(self, notifier, notification):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = notifier.signature
        parameters['uid'] = notification.uid
        parameters['password'] = notifier.uid
        
        self.commands.append(('clearactions', parameters))


class IsVisibleRequest(object):
    def __init__(self, notifier, notification):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = notifier.signature
        parameters['uid'] = notification.uid
        parameters['password'] = notifier.uid
        
        self.commands.append(('isvisible', parameters))


class SNP(object):
    """Snarl Network Protocol handler.
    
    :param event_handler: A callable which is provided with an
                          :class:`hiss.NotificationEvent` when an SNP callback
                          event is received.
    :type event_handler:  A callable
    """
    
    def __init__(self, event_handler=None):
        self._targets = []
        self._event_handler = event_handler
        self._factory = SNPFactory(self._snp_event_handler)
    
    def connect(self, target):
        """Connect to a target
        
        :param target: Target to connect to
        :type target:  :class:`hiss.Target`
        """
        
        def version(response):
            target.protocol_version = response.max_version
        
        def connected(response):
            self._targets.append(target)
            
            request = VersionRequest()
            d = self._factory.send_commands(request.commands, [target])
            d.addCallback(version)
            
            return response
        
        if target.port == -1:
            target.port = SNP_DEFAULT_PORT
        
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
        
        if targets is None:
            targets = self._targets
        else:
            targets = self._known_targets(targets)
        
        request = RegisterRequest(notifier)
        return self._factory.send_commands(request.commands, targets)
        
    def notify(self, notifier, notification, targets=None):
        """Send a notification to a list of targets
        
        :param notifier: Notification to send
        :type notifier:  :class:`hiss.Notification`
        :param targets:  list of targets to notify or None to
                         send to all targets
        :type targets:   list of :class:`hiss.Target` or None
        :returns:        A :class:`defer.Deferred` to wait on
        """
        
        if targets is None:
            targets = self._targets
        else:
            targets = self._known_targets(targets)
        
        request = NotifyRequest(notifier, notification)
        return self._factory.send_commands(request.commands, targets)
    
    def add_action(self, notification, targets=None):
        pass
    
    def clear_action(self, notification, targets=None):
        pass
    
    def show(self, uid, targets=None):
        pass
    
    def hide(self, uid, targets=None):
        pass
    
    def is_visible(self, notification, notifier=None, targets=None):
        if targets is None:
            targets = self._targets
        else:
            targets = self._known_targets(targets)
        
        if notifier is None:
            if notification.notifier is not None:
                notifier = notification.notifier
            else:
                raise ValueError('No valid notifier instance available.')
            
        request = IsVisibleRequest(notifier, notification)
        return self._factory.send_commands(request.commands, targets)
    
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
                           
        if targets is None:
            targets = self._targets
        else:
            targets = self._known_targets(targets)
        
        request = SubscribeRequest(notifier, signatures)
        return self._factory.send_commands(request.commands, targets)
    
    def unregister(self, notifier, targets=None):
        """Unregister a notifier with a list of targets
        
        :param notifier: Notifier to unregister
        :type notifier:  hiss.Notifier
        :param targets:  list of targets to unregister with or None to
                         unregister with all targets
        :type targets:   list of :class:`hiss.Target` or None
        :returns:        A :class:`defer.Deferred` to wait on
        """
        
        if targets is None:
            targets = self._targets
        else:
            targets = self._known_targets(targets)
        
        request = UnregisterRequest(notifier)
        return self._factory.send_commands(request.commands, targets)

    def _all_targets(self):
        return self._targets

    def _known_targets(self, targets):
        """Filter out unknown targets"""  
        
        if isinstance(targets, tuple):
            targets = list(targets)
        elif not isinstance(targets, list):
            targets = [targets]
        
        _targets = []
        for target in targets:
            if target in self._targets:
                _targets.append(target)
                
        return _targets
    
    def _snp_event_handler(self, response):
        event = NotificationEvent()
        event.nid = response.nid
        event.name = response.status_name
        event.code = response.status_code
        event.data = response.data
            
        self._event_handler(event)
    

class SNPFactory(ClientFactory):
    def __init__(self, event_handler=None):
        self._protocol_map = []
        self._event_handler = event_handler
        
    def connect(self, target):
        """Connect to a target.
        
        You must use this method to connect to a target otherwise everything
        else will fail."""
        
        protocol = SNPProtocol(self._event_handler)
        protocol.factory = self
        
        self._protocol_map.append((target, protocol))
        
        point = TCP4ClientEndpoint(reactor, target.host, target.port)
        d = point.connect(self)
        return d

    def send_commands(self, request, targets):
        """Send a request to a list of targets
        
        :param commands: Commands to send
        :type commands:  list of commands
        :param targets:  List of targets to send request to
        :type targets:   list of hiss.Target
        :returns:        A defer.Deferred or defer.DeferredList to wait on
        """
        
        def response_received(response, target):
            return response

        ds = []
        commands = request.commands

        for target in targets:
            log.debug('Sending to %s' % str(target))
            
            if target.protocol_version == '':
                #TODO: Replace with constant?
                target.protocol_version = '2.0'
            
            protocol = self._find_protocol_for_target(target)
            if target.protocol_version == '3.0' or len(commands) == 1:
                d = self._send_single_request(commands,
                                              target.protocol_version,
                                              protocol)
            else:
                d = self._send_multiple_requests(commands,
                                                 target.protocol_version,
                                                 protocol)

            d.addCallback(response_received, target)
            ds.append(d)

        if len(ds) == 1:
            return ds[0]
        else:            
            return defer.DeferredList(ds)

    def _send_single_request(self, commands, version, protocol):
        request = SNPRequest(version)
        for command in commands:
            request.append(command)
            
        data = request.marshall()
        deferred = defer.Deferred()

        log.debug('Sending: %s' % data.replace('\r\n', '\r').rstrip('\r'))
        protocol.deferred = deferred
        protocol.send_data(data)
        
        return deferred

    @defer.inlineCallbacks
    def _send_multiple_requests(self, commands, version, protocol):
        for command in commands:
            d = self._send_single_request([command], version, protocol)
            yield d
        
        defer.returnValue('')        

    def buildProtocol(self, address):
        for target, protocol in self._protocol_map:
            if target.host == address.host and target.port == address.port:
                return protocol
            else:
                raise SNPError(('Unable to build protocol for address %s. '
                                'Ensure you use the connect method') % address)
    
    def _find_protocol_for_target(self, target):
        for t, protocol in self._protocol_map:
            if t == target:
                return protocol
        
        return None


class SNPProtocol(LineReceiver):
    """SNPProtocol has 2 responsibilities
    
    1. Sends a single SNPRequest and compiles an SNPResponse as data arrives.
       When a complete response is received it executes the callback on the
       deferred set up when sending the request.
       
    2. Compiles any callback data into an SNPResponse. When a complete response
       is received it calls the registered event handler 
    """
    
    def __init__(self, event_handler=None):
        """Initializes the instance and registers an event handler, if provided,
        called when an SNP callback response is received.
        """
        
        self.deferred = None
        self._response = SNPResponse()
        self._event_handler = event_handler
    
    def lineReceived(self, line):
        """Receive lines of data until a complete response has been received."""
        
        log.debug('Received: %s' % line)
        self._response.append(line)
        
        if self._response.iscomplete:
            self._response.unmarshall()
            
            if self._response.isevent:
                if self._event_handler is not None:
                    self._event_handler(self._response)
            else:
                if self.deferred is not None:
                    self.deferred.callback(self._response)
                    self.deferred = None
            
            # And so it goes around...
            self._response = SNPResponse()
    
    def send_data(self, data):
        """Send a single SNP request."""
        
        self.transport.write(data)
    