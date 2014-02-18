# Copyright 2013-2014, Simon Kennedy, code@sffjunkie.co.uk
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

# Part of 'hiss' the asynchronous notification library

import asyncio
import base64
import logging
from pprint import pformat
from collections import namedtuple
from os import urandom
from binascii import unhexlify
from operator import attrgetter

from hiss.hash import HashInfo, generate_hash, validate_hash
from hiss.encryption import PY_CRYPTO, encrypt, decrypt
from hiss.exception import HissError, MarshallError
from hiss.handler import Handler, Factory
from hiss.utility import parse_datetime
from hiss.resource import Icon
from hiss.notification import NotificationPriority

SNP_SCHEME = 'snp'
SNP_DEFAULT_PORT = 9887
SNP_BASE_VERSION = '2.0'
SNP_DEFAULT_VERSION = '3.0'
SNP_VALID_VERSIONS = ['2.0', '3.0']

DEFAULT_HASH_ALGORITHM = 'SHA256'
ENCRYPTION_ALGORITHM = 'AES'

SNARL_STATUS = {
    0:   'OK',
    101: 'Failed',
    102: 'Unknown Command',
    103: 'Timed Out',
    106: 'Bad Socket',
    107: 'Bad Packet',
    108: 'Invalid Argument',
    109: 'Argument Missing',
    110: 'System Error',
    121: 'Access Denied',
    201: 'Not Running',
    202: 'Not Registered',
    203: 'Already Registered',
    204: 'Class Already Exists',
    205: 'Class Blocked',
    206: 'Class Not Found',
    207: 'Notification Not Found',
    208: 'Flooding',
    209: 'Do Not Disturb',
    210: 'Could Not Display',
    211: 'Authentification Failure',
    212: 'Discarded',
    213: 'Not Subscribed',
    301: 'Reserved',
    303: 'TimedOut',
    304: 'Clicked',
    307: 'Closed',
    308: 'ActionSelected',
}

# The following error codes do not constitute a failed response  
ACCEPTABLE_ERRORS = [203, 204]

EVENT_MAPPING = {
    '304': 0,
    '303': 1,
    '307': 2,
    '308': 3,
}

ATTR_MAPPING = {
    b'event-code': 'status_code',
    b'event-name': 'status',
    b'notification-uid': 'nid',
    b'event-data': 'data',
    b'x-timestamp': 'timestamp',
    b'x-daemon': 'daemon',
    b'x-host': 'host',
}

BOOL_MAPPING = {
    1: '1', True: '1',  'true': '1',  'yes': '1',
    0: '0', False: '0', 'false': '0', 'no': '0',
}

class SNPError(HissError):
    pass


class SNPHandler(Handler):
    """:class:`~hiss.handler.Handler` sub-class for SNP messages"""

    __handler__ = 'SNP'

    def __init__(self, loop=None):
        super().__init__(loop)

        self.port = SNP_DEFAULT_PORT
        self.factory = Factory(SNP)
        self.async_factory = Factory(SNPAsync)
        self.capabilities = ['register', 'unregister', 'subscribe', 'show', 'hide']

    @asyncio.coroutine
    def connect(self, target, factory=None):
        """Override the :meth:`hiss.handler.Handler.connect` to call the
        :meth:`get_version` method."""

        protocol = yield from super().connect(target, factory)

        if not hasattr(target, 'api_version'):
            response = yield from protocol.get_version()
            target.api_version = int(response.result.decode('UTF-8'))
            target.protocol_version = response.max_version

        return protocol


class SNPBaseProtocol(asyncio.Protocol):
    def __init__(self):
        self._target = None
        self._buffer = None

    def connection_made(self, transport):
        self.response = None
        self._buffer = bytearray()
        self._transport = transport

    @property
    def target(self):
        """The :class:`hiss.target.Target` to send notifications to."""
        
        return self._target

    @target.setter
    def target(self, value):
        self._target = value
        if value.is_remote:
            self.use_hash = True

    @asyncio.coroutine
    def send_request(self, request_info):
        """Send a request_info to a list of targets

        :param request_info:  Info for request to send
        """

        if self.target.protocol_version == '':
            self.target.protocol_version = SNP_BASE_VERSION

        if self.target.protocol_version == '3.0' or \
                len(request_info.commands) == 1:
            response = yield from self._send_single(request_info,
                self.target.protocol_version)
        else:
            response = yield from self._send_multiple(request_info,
                self.target.protocol_version)

        return response

    @asyncio.coroutine
    def _send_single(self, request_info, version):
        request = Request(version)
        for command in request_info.commands:
            request.append(command)

        data = request.marshall()
        self._transport.write(data)
        yield from self._wait_for_response()
        return self.response

    @asyncio.coroutine
    def _send_multiple(self, commands, version):
        responses = []
        for command in commands:
            response = yield from self._send_single([command], version)
            responses.append(response)
        return responses

    @asyncio.coroutine
    def _wait_for_response(self):
        while True:
            if self.response is not None:
                return
            else:
                yield from asyncio.sleep(0.1)

    def _build_result(self, command):        
        result = {}
        result['handler'] = 'SNP'
        result['command'] = command
        result['status'] = self.response.status
        result['status_code'] = self.response.status_code
        result['result'] = self.response.result

        if hasattr(self.response, 'timestamp'):
            result['timestamp'] = parse_datetime(self.response.timestamp)

        if hasattr(self.response, 'daemon'):
            result['daemon'] = self.response.daemon

        return result


class SNP(SNPBaseProtocol):
    """Snarl Network Protocol."""

    def __init__(self):
        self.use_encryption = False
        self.use_hash = False
        
        super().__init__()

    def data_received(self, data):
        self._buffer.extend(data)

        version = self.target.protocol_version
        if version == '2.0':
            end_of_response_marker = b'\r\n'
        else:
            end_of_response_marker = b'END\r\n'

        end = self._buffer.find(end_of_response_marker)
        if end != -1:
            if version == '2.0':
                data = self._buffer[:end]
                del self._buffer[:end + 2]
            else:
                data = self._buffer[:end + 3]
                del self._buffer[:end + 5]

            response = Response()
            response.version = version
            response.unmarshall(data)
            self.response = response

    @asyncio.coroutine
    def get_version(self):
        """Get details of the SNP version that the target can handle."""

        request_info = _VersionRequestInfo()

        yield from self.send_request(request_info)
        return self.response

    @asyncio.coroutine
    def register(self, notifier, **kwargs):
        """Register ``notifier`` with a our target 

        :param notifier: Notifier to register
        :type notifier:  :class:`hiss.notifier.Notifier`
        """

        assert self.target.protocol_version != ''

        request_info = _RegisterRequestInfo(notifier, **kwargs)
        yield from self.send_request(request_info)

        result = self._build_result('register')
        logging.debug(pformat(result))
        return result

    @asyncio.coroutine
    def unregister(self, notifier):
        """Unregister a notifier

        :param notifier: Notifier to unregister
        :type notifier:  hiss.Notifier
        """

        request_info = _UnregisterRequestInfo(notifier)
        yield from self.send_request(request_info)

        result = self._build_result('unregister')
        logging.debug(pformat(result))
        return result

    @asyncio.coroutine
    def notify(self, notification, notifier):
        """Send a notification to a target

        :param notification: Notification to send
        :type notification:  :class:`hiss.Notification`
        :param notifier: Notifier to use 
        :type notifier:  :class:`hiss.notifier.Notifier`
        """

        assert self.target.protocol_version != ''

        request_info = _NotifyRequestInfo(notification, notifier)
        yield from self.send_request(request_info)

        result = self._build_result('notify')
        logging.debug(pformat(result))
        return result

    @asyncio.coroutine
    def add_action(self, notification):
        raise NotImplementedError

    @asyncio.coroutine
    def clear_action(self, notification):
        raise NotImplementedError

    @asyncio.coroutine
    def show(self, notification):
        """Show a hidden notification 

        :param notification: Notification to show
        :type notification:  :class:`hiss.notification.Notification`
        """

        request_info = _ShowRequestInfo(notification.uid)
        yield from self.send_request(request_info)

        result = self._build_result('show')
        logging.debug(pformat(result))
        return result

    @asyncio.coroutine
    def hide(self, uid, targets=None):
        """Hide a notification 

        :param notification: Notification to show
        :type notification:  :class:`hiss.notification.Notification`
        """

        request_info = _HideRequestInfo(uid)
        yield from self.send_request(request_info)

        result = self._build_result('hide')
        logging.debug(pformat(result))
        return result

    @asyncio.coroutine
    def isvisible(self, notification, notifier=None, targets=None):
        def response():
            return True

        if notifier is None:
            if notification.notifier is not None:
                notifier = notification.notifier
            else:
                raise ValueError('No valid notifier instance available.')

        request_info = _IsVisibleRequestInfo(notifier, notification)
        yield from self.send_request(request_info)

        result = self._build_result('isvisible')
        logging.debug(pformat(result))
        return result


class SNPAsync(SNPBaseProtocol):
    """Handling for asynchronous SNP responses."""

    def __init__(self):
        self._async_handler = None
        super().__init__()

    def data_received(self, data):
        self._buffer.extend(data)

        version = self.target.protocol_version
        if version == '2.0':
            end_of_response_marker = b'\r\n'
        else:
            end_of_response_marker = b'END\r\n'

        responses = []
        end = self._buffer.find(end_of_response_marker)
        while end != -1:
            if version == '2.0':
                data = self._buffer[:end]
                del self._buffer[:end + 2]
            else:
                data = self._buffer[:end + 3]
                del self._buffer[:end + 5]

            response = Response()
            response.version = version
            response.unmarshall(data)
            responses.append(response)

            end = self._buffer.find(end_of_response_marker)

        if self.response is None:
            self.response = responses.pop(0)
        else:
            asyncio.async(self._async_handler(responses))

    @asyncio.coroutine
    def subscribe(self, notifier, signatures):
        """Subscribe to notifications from a list of signatures

        :param notifier:      Notifier to use.
        :type notifier:       :class:`hiss.Notifier`
        :param signatures:    Application signatures to receive messages from
        :type signatures:     List of string or [] for all
                              applications
        :returns:             The Response received.
        """
        
        if not callable(notifier._handler):
            raise ValueError('%s: async_handler must be callable' % 
                             self.__class__.__qualname__)
        
        self._async_handler = notifier._handler

        request_info = _SubscribeRequestInfo(notifier, signatures)
        yield from self.send_request(request_info)

        result = self._build_result('subscribe')
        logging.debug(pformat(result))
        return result


SNPCommand = namedtuple('SNPCommand', 'name parameters')
SNPResult = namedtuple('SNPResult', 'command status_code reason')


class Request(object):
    def __init__(self, version=SNP_DEFAULT_VERSION):
        self.version = version
        self.password = None
        self.commands = []

        self.use_hash = False
        self.use_encryption = False

        self._hash = None
        self._encryption = None

    def append(self, command, **kwargs):
        """Append a command to the message

        :param command:  The command to append
        :type command:   A 2 element tuple containing a name and a dictionary
                         of parameters or
                         A separate command name as a string and keyword 
                         arguments
        """

        if self.version == '2.0' and len(self.commands) > 1:
            raise SNPError(("Version 2.0 messages do not "
                            "support multiple commands"),
                           'Request.append')

        if len(kwargs) != 0:
            self.commands.append(SNPCommand(command, kwargs))
        else:
            if isinstance(command, tuple):
                self.commands.append(SNPCommand(command[0], command[1]))
            else:
                self.commands.append(SNPCommand(command, {}))

    def marshall(self):
        """Marshall the request ready to send over the wire."""

        if self.use_hash or self.use_encryption:
            if self.password is None:
                raise MarshallError('Password required to generate hash for marshall of request.',
                                    'Request.marshall')

            self._hash = generate_hash(self.password.encode('UTF-8'))

        if self.use_encryption:
            if not PY_CRYPTO:
                raise MarshallError('Unable to encrypt message. PyCrypto not available',
                                    'Request.marshall')

            if ENCRYPTION_ALGORITHM == 'AES':
                iv = urandom(16)
            else:
                iv = urandom(8)

            self._encryption = (ENCRYPTION_ALGORITHM, iv)

        if self.version == '2.0':
            return self._marshall_20()
        elif self.version == '3.0':
            return self._marshall_30()
        elif self.version == '1.0':
            raise MarshallError('SNP protocol version 1.0 is unsupported.',
                                'Request.marshall')

    def unmarshall(self, data):
        """Unmarshall data received over the wire into a valid request"""

        if data.startswith(b'snp://'):
            self._unmarshall_20(data)
        elif data.startswith(b'SNP/3.0'):
            self._unmarshall_30(data)
        else:
            raise MarshallError('Invalid SNP Request.',
                                'Request.unmarshall')

    def _marshall_20(self):
        data = self._marshall_command(self.commands[0]).encode('UTF-8')
        data = b'snp://' + data + b'\r\n' 
        return data

    def _marshall_30(self):
        data = 'SNP/3.0'
        if self.password != '':
            if self.use_encryption:
                data += ' %s' % self._encryption
            else:
                data += ' NONE'

            if self.use_hash:
                data += ' %s' % str(self._hash)
        else:
            data += 'NONE'
            
        data += '\r\n'

        for command in self.commands:
            data += '%s\r\n' % self._marshall_command(command)

        data += 'END\r\n'
        return data.encode('UTF-8') 

    def _marshall_command(self, command):
        if len(command.parameters) == 0:
            return command.name
        else:
            data = ''

            names = list(command.parameters.keys())
            names.sort()

            for name in names:
                value = command.parameters[name]
                if isinstance(value, list):
                    for item in value:
                        item = self._escape(self._expand_tuple(item))
                        data += '%s=%s&' % (name, item)
                elif isinstance(value, (bytearray, bytes)):
                    data += '%s=%s&' % (name, value.decode('ascii'))
                else:
                    value = self._escape(self._expand_tuple(value))
                    data += '%s=%s&' % (name, value)

            data = data[:-1]

            if len(data) > 0:
                data = '%s?%s' % (command.name, data)
                return data
            else:
                return command.name

    def _unmarshall_20(self, data):
        data = data[6:].strip(b'\r\n')
        command = self._extract_command(data)           
        self.commands = [command]
        self.version = '2.0'

    def _unmarshall_30(self, data):
        if not data.endswith(b'END\r\n'):
            raise MarshallError('Invalid SNP 3.0 request',
                                'Request.unmarshall')

        data = data[:-2]
        lines = data.split(b'\r\n')
        header = lines[0]

        try:
            items = header.split(b' ')
            if len(items) >= 2:
                if items[1] != b'NONE':
                    self._encryption = tuple(items[1].split(b':'))
                    self.use_encryption = True

            if len(items) >= 3:
                hash_and_salt = items[2]
                htype, rest = hash_and_salt.split(b':')
                hkey, hsalt = rest.split(b'.')
                self._hash = HashInfo(htype.upper(), unhexlify(hkey), unhexlify(hsalt))
                
                if self.password is not None:
                    validate_hash(self.password, self._hash)
                    
                self.use_hash = True
        except ValueError:
            raise MarshallError('Invalid SNP body format: %s' % str(header),
                                'Request.unmarshall')

        self.commands = []
        for line in lines[1:-1]:
            self.commands.append(self._extract_command(line))

        self.version = '3.0'

    def _extract_command(self, data):
        try:
            command, rest = data.split(b'?', 1)

            params = {}
            items = rest.split(b'&')
            for item in items:
                name, value = item.split(b'=', 1)
                value = self._unescape(value)

                params[name] = value

            return SNPCommand(command, params)
        except ValueError:
            raise MarshallError('Invalid command format found: %s', str(data),
                                'Request.unmarshall')

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
        data = data.replace(b'==', b'=')
        data = data.replace(b'&&', b'&')
        data = data.replace(b'\\n', b'\r\n')
        return data

    def _encrypt(self, data):
        encryption_algorithm, iv = self._encryption
        return encrypt(encryption_algorithm, iv, self._hash.key_hash, data)

    def _decrypt(self, data):
        encryption_algorithm, iv = self._encryption
        return decrypt(encryption_algorithm, iv, self._hash.key_hash, data)


class Response(object):
    def __init__(self, version=SNP_DEFAULT_VERSION):
        self.version = version
        """The SNP protocol version number of this response"""

        self.max_version = ''
        """The maximum SNP protocol version the SNP receiver can handle"""

        self.status_code = 0
        """The status code for the response

        0       = OK
        100-199 = System or transport error
        200-299 = Application errors
        300-399 = Events
        """

        self.data = b''
        self.body = {}

    def clear(self):
        self.data = b''

    @property
    def is_ok(self):
        return self.status_code == 0

    @property
    def is_error(self):
        return self.status_code > 100 and self.status_code < 300

    @property
    def is_event(self):
        return self.status_code > 300 and self.status_code < 400

    def unmarshall(self, data):
        """Unmarshall data received over the wire into a valid response"""

        lines = data.split(b'\r\n')
        if self.version == '2.0':
            self._unmarshall2(lines)
        elif self.version == '3.0':
            self._unmarshall3(lines)

    def _unmarshall2(self, lines):
        elems = lines[0].split(b'/')
        self.max_version = elems[1].decode('UTF-8')
        self.status_code = int(elems[2].decode('UTF-8'))

        try:
            self.status = SNARL_STATUS[self.status_code]
        except:
            self.status = 'Unknown'

        self.isevent = (self.status_code >= 300 and self.status_code <= 399)

        if len(elems) > 4:
            if self.isevent:
                self.nid = elems[4]
            else:
                self.result = elems[4]
                self.nid = ''
        else:
            self.result = None

    def _unmarshall3(self, lines):
        results = []

        header = lines[0]
        items = header.split(b' ')

        _snp, self.max_version = items[0].split(b'/')

        if len(items) > 1:
            status = items[1].upper()
            self.isevent = (status == 'callback')
        else:
            self.isevent = False

        if len(items) > 2:
            self.hash_type = items[2]

        if len(items) > 3:
            self.cypher_type = items[3]

        self.nid = ''
        for line in lines[1:-1]:
            key, value = line.split(b':', 1)
            key = bytes(key)
            value = value.decode('UTF-8').strip()

            if key == b'result':
                command, status_code, reason = value.split(' ')
                status_code = int(status_code)
                results.append(SNPResult(command, status_code, reason))
            elif key in ATTR_MAPPING:
                attr = ATTR_MAPPING[key]
                self.__setattr__(attr, value)
            else:
                if key not in self.body:
                    self.body[key] = value
                else:
                    if not isinstance(self.body[key], list):
                        self.body[key] = [self.body[key]]

                    self.body[key].append(value)

        status_ok = True
        for result in results:
            if result.status_code != 0 and result.status_code not in ACCEPTABLE_ERRORS:
                status_ok = False

        # Compute an overall status
        if status_ok:
            self.status = 'OK'
            self.status_code = 0
        else:
            self.status = 'ERROR'
            result = max(results, key=attrgetter('status_code'))
            self.status_code = result.status_code
            self.reason = result.reason

        if len(results) == 1:
            self.result = results[0]
        else:
            self.result = results

    def _encrypt(self):
        pass

    def _decrypt(self):
        pass


class _VersionRequestInfo(object):
    def __init__(self):
        self.commands = [('version', {})]


class _RegisterRequestInfo(object):
    def __init__(self, notifier, **kwargs):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = notifier.signature
        parameters['title'] = notifier.name
        parameters['password'] = notifier.uid
        
        keep_alive = kwargs.get('keep_alive', False)
        if keep_alive:
            parameters['keep-alive'] = '1'

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
            parameters['name'] = info.name
            parameters['enabled'] = BOOL_MAPPING[info.enabled]
            parameters['password'] = notifier.uid

            if info.icon is not None:
                if isinstance(info.icon, Icon):
                    data = snp64(icon.data)
                    parameters['icon-base64'] = data
                else:
                    parameters['icon'] = info.icon

            self.commands.append(('addclass', parameters))


class _ClearClassesRequestInfo(object):
    def __init__(self, notifier):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = notifier.signature
        parameters['password'] = notifier.uid

        self.commands.append(('clearclasses', parameters))


class _UnregisterRequestInfo(object):
    def __init__(self, notifier):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = notifier.signature
        parameters['password'] = notifier.uid

        self.commands.append(('unregister', parameters))


class _NotifyRequestInfo(object):
    def __init__(self, notification, notifier):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = notifier.signature
        parameters['password'] = notifier.uid

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

        if notification.sound is not None:
            parameters['sound'] = notification.sound

        if notification.timeout != -1:
            parameters['timeout'] = notification.timeout

        if notification.sticky:
            parameters['timeout'] = 0

        if notification.callback is not None:
            parameters['callback'] = notification.callback[0]
            if notification.callback[1] != '':
                parameters['callback-label'] = notification.callback[1]

        # Clamp priority to +-1        
        if notification.priority == NotificationPriority.very_low:
            priority = NotificationPriority.moderate
        elif notification.priority == NotificationPriority.emergency:
            priority = NotificationPriority.high
        else:
            priority = notification.priority

        parameters['priority'] = priority.value

        if notification.percentage != -1:
            parameters['value-percent'] = notification.percentage

        if len(notification.actions) > 0:
            parameters['action'] = []
            for cmd, label in notification.actions:
                parameters['action'].append((label, cmd))

        self.commands.append(('notify', parameters))


class _AddActionRequestInfo(object):
    def __init__(self, notifier, notification, command, label):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = notifier.signature
        parameters['uid'] = notification.uid
        parameters['password'] = notifier.uid
        parameters['cmd'] = command
        parameters['label'] = label

        self.commands.append(('addaction', parameters))


class _ClearActionsRequestInfo(object):
    def __init__(self, notifier, notification):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = notifier.signature
        parameters['uid'] = notification.uid
        parameters['password'] = notifier.uid

        self.commands.append(('clearactions', parameters))


class _IsVisibleRequestInfo(object):
    def __init__(self, notifier, notification):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = notifier.signature
        parameters['uid'] = notification.uid
        parameters['password'] = notifier.uid

        self.commands.append(('isvisible', parameters))


class _ShowRequestInfo(object):
    def __init__(self, notifier, uid):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = notifier.signature
        parameters['password'] = notifier.uid
        parameters['uid'] = uid

        self.commands.append(('show', parameters))


class _HideRequestInfo(object):
    def __init__(self, notifier, uid):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = notifier.signature
        parameters['password'] = notifier.uid
        parameters['uid'] = uid

        self.commands.append(('hide', parameters))


class _SubscribeRequestInfo(object):
    def __init__(self, notifier, signatures):
        self.commands = []

        parameters = {}
        parameters['app-sig'] = signatures
        parameters['password'] = notifier.uid

        self.commands.append(('subscribe', parameters))


def snp64(data):
    data = bytearray(base64.b64encode(data))
    data = data.replace(b'\r\n', b'#')

    # Replace trailing = with %
    pos = -1
    while data[pos] == 61:
        data[pos] = 37
        pos -= 1

    return data
    