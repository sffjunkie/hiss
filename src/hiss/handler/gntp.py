# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

import re
import asyncio
import logging
from os import urandom
from pprint import pformat
from datetime import datetime
from urllib.parse import urlparse
from binascii import unhexlify

from hiss.handler import Handler
from hiss.utility import parse_datetime
from hiss.resource import Icon

from hiss.exception import HissError, MarshalError
from hiss.hash import HashInfo, generate_hash, validate_hash
from hiss.encryption import PY_CRYPTO, encrypt, decrypt

GNTP_SCHEME = 'gntp'
GNTP_DEFAULT_PORT = 23053
GNTP_BASE_VERSION = '1.0'

DEFAULT_HASH_ALGORITHM = 'SHA256'
ENCRYPTION_ALGORITHM = 'AES'

class GNTPError(HissError):
    pass


class GNTPHandler(Handler):
    """:class:`~hiss.handler.Handler` sub-class for GNTP notifications"""

    __name__ = 'GNTP'

    def __init__(self, loop=None):
        super().__init__(loop)

        self.port = GNTP_DEFAULT_PORT
        self.factory = lambda: GNTPProtocol()
        self.async_factory = lambda: GNTPAsyncProtocol()
        self.capabilities = ['register', 'subscribe']


class GNTPBaseProtocol(asyncio.Protocol):
    def __init__(self):
        self._target = None
        self._buffer = None

    def connection_made(self, transport):
        self.response = None
        self._buffer = bytearray()
        self._transport = transport

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = value
        if value.is_remote:
            self.use_hash = True

    def send_request(self, request, target):
        if target.password is not None and (self.use_hash or self.use_encryption):
            request.password = target.password.encode('UTF-8')
            request.use_hash = self.use_hash
            request.use_encryption = self.use_encryption

        request_data = request.marshal()
        self._transport.write(request_data)

    @asyncio.coroutine
    def _wait_for_response(self):
        while True:
            if self.response is not None:
                return
            else:
                yield from asyncio.sleep(0.1)


class GNTPProtocol(GNTPBaseProtocol):
    """Growl Network Transport Protocol."""

    name = 'GNTP'

    def __init__(self):
        self.use_encryption = False
        self.use_hash = False

    def data_received(self, data):
        self._buffer.extend(data)

    def eof_received(self):
        callback_response = None
        items = [i for i in self._buffer.split(b'\r\n\r\n') if len(i) > 0]
        if len(items) > 1:
            response_data = items[0]
            callback_data = items[1]

            callback_response = Response()
            callback_response.unmarshal(callback_data)
        else:
            response_data = items[0]

        response = Response()
        response.unmarshal(response_data)

        result = {}
        result['command'] = response.command
        result['handler'] = 'GNTP'
        result['status'] = response.status
        result['status_code'] = response.status_code
        result['timestamp'] = response.timestamp
        result['target'] = str(self.target)
        if response.status =='ERROR':
            result['reason'] = response.reason

        if callback_response is not None:
            cb_result = {}
            cb_result['nid'] = callback_response.nid
            cb_result['status'] = callback_response.callback_status
            cb_result['timestamp'] = callback_response.callback_timestamp
            result['callback'] = cb_result

        self.response = result

    @asyncio.coroutine
    def register(self, notifier):
        """Register ``notifier`` with a our target 

        :param notifier: The Notifier to register
        :type notifier:  :class:`~hiss.notifier.Notifier`
        """

        request = _RegisterRequest(notifier)
        self.send_request(request, self.target)
        yield from self._wait_for_response()
        logging.debug(pformat(self.response))
        return self.response

    @asyncio.coroutine
    def unregister(self, notifier):
        """Unregister the notifier from the target"""

        request = _UnregisterRequest(notifier)
        self.send_request(request, self.target)
        yield from self._wait_for_response()
        logging.debug(pformat(self.response))
        return self.response

    @asyncio.coroutine
    def notify(self, notification, notifier):
        """Send a notification

        :param notification: The notification to send
        :type notification: :class:`~hiss.notification.Notification`
        """

        request = _NotifyRequest(notification, notifier)
        self.send_request(request, self.target)
        yield from self._wait_for_response()
        logging.debug(pformat(self.response))
        return self.response


class GNTPAsyncProtocol(GNTPBaseProtocol):
    """Growl Network Transport Protocol."""

    name = 'GNTPAsync'

    def data_received(self, data):
        self._buffer.extend(data)

    @asyncio.coroutine
    def subscribe(self, notifier, signatures):
        """Register ``notifier`` with a our target 

        :param notifier: The Notifier to register
        :type notifier:  :class:`~hiss.notifier.Notifier`
        :param signatures:    Application signatures to receive messages from
        :type signatures:     List of string or [] for all
                              applications
        """
        
        self._async_handler = notifier._handler

        request = _SubscribeRequest(notifier)
        self.send_request(request, self.target)
        yield from self._wait_for_response()
        logging.debug(pformat(self.response))
        return self.response


class Request(object):
    def __init__(self, version=GNTP_BASE_VERSION):
        self.version = version
        self.password = None
        self.command = ''
        self.body = {}
        self.sections = []
        self.identifiers = []

        self.use_hash = False
        self.use_encryption = False

        self._hash = None
        self._encryption = None

    def marshal(self, encoding='UTF-8'):
        """marshal the request ready to send over the wire."""

        if self.use_hash or self.use_encryption:
            if self.password is None:
                raise MarshalError('Password required to generate hash for marshaling of request.',
                                    'Request.marshal')

            self._hash = generate_hash(self.password.encode('UTF-8'))

        if self.use_encryption:
            if not PY_CRYPTO:
                raise MarshalError('Unable to encrypt message. PyCrypto not available')

            if ENCRYPTION_ALGORITHM == 'AES':
                iv = urandom(16)
            else:
                iv = urandom(8)

            self._encryption = (ENCRYPTION_ALGORITHM, iv)

        header = 'GNTP/%s %s' % (self.version, self.command)
        if self._encryption is not None:
            header += ' %s:%s' % self._encryption
        else:
            header += ' NONE'

        if self._hash is not None:
            header += ' %s:%s.%s' % self._hash

        header += '\r\n'
        data = bytearray(header.encode(encoding))

        body_data = bytearray()
        for name, value in iter(sorted(self.body.items())):
            body_data.extend(('%s: %s\r\n' % (name, value)).encode(encoding))

        body_data.extend(('\r\n').encode(encoding))

        if self._encryption is not None:
            body_data = self._encrypt(body_data)

        data.extend(body_data)

        for section in self.sections:
            section_data = bytearray()
            for name, value in section.items():
                if isinstance(value, self._IdReference):
                    section_data.extend(('%s: x-growl-resource//%s\r\n' % (name, str(value))).encode(encoding))
                else:
                    section_data.extend(('%s: %s\r\n' % (name, value)).encode(encoding))

            section_data.extend(('\r\n').encode(encoding))

            if self._encryption is not None:
                section_data = self._encrypt(section_data)

            data.extend(section_data)

        for identifier in self.identifiers:
            identifier_data = bytearray()
            identifier_data.extend(('Identifier: %s\r\n' % identifier['Identifier']).encode(encoding))
            idata = identifier['Data']
            identifier_data.extend(('Length: %d\r\n\r\n' % len(idata)).encode(encoding))

            if self._encryption is not None:
                idata = self._encrypt(idata)

            identifier_data.extend(idata)
            identifier_data.extend(('\r\n\r\n').encode(encoding))

            data.extend(identifier_data)

        return data

    def unmarshal(self, data, encoding='UTF-8'):
        """Unmarshal data received over the wire into a valid request"""

        if self._encryption is not None and not PY_CRYPTO:
            raise MarshalError('PyCrypto required to decrypt message')

        sections = data.split(b'\r\n\r\n')

        header_info_re = b'GNTP\/(?P<version>\d\.\d) (?P<command>[A-Z]+)( ((?P<encryptionAlgorithmID>\w+)\:(?P<ivValue>[a-fA-F0-9]+)|NONE)( (?P<keyHashAlgorithmID>\w+)\:(?P<keyHash>[a-fA-F0-9]+)\.(?P<salt>[a-fA-F0-9]+))?)?'
        header_section = sections.pop(0)
        header_info, *headers = header_section.split(b'\r\n')
        m = re.match(header_info_re, header_info)

        if m is not None:
            d = m.groupdict()
            self.version = d['version'].decode(encoding)
            self.command = d['command'].decode(encoding)

            if d['encryptionAlgorithmID'] is None:
                self.use_encryption = False
                self._encryption = None
            else:
                self.use_encryption = True
                self._encryption = (d['encryptionAlgorithmID'].decode(encoding),
                                    unhexlify(d['ivValue']))

            if d['keyHashAlgorithmID'] is None:
                self.use_hash = False
                self._hash = None
            else:
                if self.password is None:
                    raise MarshalError('Password required to validate hash for unmarshal of request.')

                self._hash = HashInfo(d['keyHashAlgorithmID'].decode(encoding),
                                      unhexlify(d['keyHash']),
                                      unhexlify(d['salt']))
                self.use_hash = True
                validate_hash(self.password, self._hash)

            if len(headers[0]) > 0:
                self._unmarshal_section(headers, self.body)

            if len(sections) > 0:
                info = None
                next_section_is_data = False
                for section in sections:
                    if not next_section_is_data:
                        info = {}
                        self._unmarshal_section(section.split(b'\r\n'), info)

                        if 'Identifier' in info:
                            next_section_is_data = True
                            self.identifiers.append(info)
                        else:
                            self.sections.append(info)
                    elif info is not None:
                        length = int(info['Length'])
                        info['Data'] = section[:length]
                        next_section_is_data = False
        else:
            raise MarshalError('Response.unmarshal: Invalid GNTP message')

    def _add_resource(self, key, resource):
        uid = resource.uid
        data = resource.data
        self.body[key] = 'x-growl-resource://%s' % uid

        identifier = {}
        identifier['Identifier'] = uid
        identifier['Data'] = data
        self.identifiers.append(identifier)

    def _unmarshal_section(self, lines, info):
        for line in lines:
            name, value = line.split(b':', 1)
            name = name.decode('UTF-8')
            value = value.decode('UTF-8').strip()

            if value.startswith('x-growl-resource://'):
                info[name] = self._IdReference(value[19:])
            else:
                info[name] = value

    def identifier_data(self, identifier):
        for i in self.identifiers:
            if i['Identifier'] == identifier:
                return i['Data']

        return None

    def _encrypt(self, data):
        encryption_algorithm, iv = self._encryption
        return encrypt(encryption_algorithm, iv, self._hash.key_hash, data)

    def _decrypt(self, data):
        encryption_algorithm, iv = self._encryption
        return decrypt(encryption_algorithm, iv, self._hash.key_hash, data)

    class _IdReference(object):
        def __init__(self, reference):
            self.reference = reference

        def __repr__(self):
            return self.reference


class Response(object):
    """GNTP/1.0 -(OK|ERROR|CALLBACK) <encryptionAlgoritm>
    <body>: <value>
    """

    def __init__(self, version=GNTP_BASE_VERSION):
        self.version = version
        """The GNTP protocol version number of this response"""

        self.status = ''
        self.command = ''
        self.body = {}

        self.use_hash = False
        self.use_encryption = False
        self._hash = None
        self._encryption = None

    def marshal(self, custom_headers=None):
        """marshal the response ready to send over the wire."""

        if self._encryption is not None and not PY_CRYPTO:
            raise Exception('Unable to encrypt message. PyCrypto not available')

        data = bytearray()

        header = 'GNTP/%s -%s' % (self.version, self.status)

        if self._encryption is not None:
            header += ' %s:%s' % self._encryption
        else:
            header += ' NONE\r\n'

        data.extend(header.encode('UTF-8'))

        if self.command != '':
            response_action = 'Response-Action: %s\r\n' % self.command.upper()
            data.extend(response_action.encode('UTF-8'))

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%SZ')
        data.extend(('X-Timestamp: %s\r\n' % str(timestamp)).encode('UTF-8'))

        if custom_headers is not None:
            for key, value in custom_headers:
                data.extend(('%s: %s\r\n' % (key, value)).encode('UTF-8'))

        body_data = bytearray()
        for name, value in self.body.items():
            line = '%s: %s\r\n' % (name.strip(), str(value).strip())
            body_data.extend(line.encode('UTF-8'))

        if self._encryption is not None:
            body_data = self._encrypt(body_data)

        data.extend(body_data)
        return data

    def unmarshal(self, data):
        """Unmarshal data received over the wire into a valid response"""

        if self._encryption is not None and not PY_CRYPTO:
            raise MarshalError('Unable to decrypt message. PyCrypto not available')

        header, data = data.split(b'\r\n', maxsplit=1)

        header_re = ('GNTP\/(?P<version>\d\.\d) (?P<responsetype>\-?[A-Z]+)'
                     ' ((?P<encryptionAlgorithmID>\w+)\:(?P<ivValue>[a-fA-F0-9]+)|NONE)')
        m = re.match(header_re, header.decode('UTF-8'))
        if m is not None:
            d = m.groupdict()
            self.version = d['version']
            self.status = d['responsetype'].lstrip('-')

            if self.status == 'OK':
                self.status_code = 0

            if d['encryptionAlgorithmID'] is None:
                self.use_encryption = False
                self._encryption = None
            else:
                self.use_encryption = True
                self._encryption = (d['encryptionAlgorithmID'],
                                   d['ivValue'])
                data = self._decrypt(data)

            for line in [l for l in data.split(b'\r\n') if len(l) != 0]:
                try:
                    name, value = line.split(b':', 1)
                    name = name.decode('UTF-8').strip()
                    value = value.decode('UTF-8').strip()

                    # All                    
                    if name == 'Response-Action':
                        self.command = value.lower()

                    elif name == 'X-Timestamp':
                        self.timestamp = parse_datetime(value)
                    elif name == 'X-Message-Daemon':
                        self.daemon = value
                    elif name == 'Origin-Machine-Name':
                        self.origin = value
                    elif name == 'Origin-Software-Name':
                        self.origin_software_name = value
                    elif name == 'Origin-Software-Version':
                        self.origin_software_version = value
                    elif name == 'Origin-Platform-Name':
                        self.origin_platform_name = value
                    elif name == 'Origin-Platform-Version':
                        self.origin_platform_version = value

                    elif name == 'Error-Code':
                        self.status_code = int(value)
                    elif name == 'Error-Description':
                        self.reason = value

                    # Notify
                    elif name == 'Application-Name':
                        self.notifier_name = value
                    elif name == 'Notification-ID':
                        self.nid = value
                    elif name == 'Notification-Callback-Result':
                        self.callback_status = value
                    elif name == 'Notification-Callback-Context':
                        self.callback_context = value
                    elif name == 'Notification-Callback-Context-Type':
                        self.callback_context_type = value
                    elif name == 'Notification-Callback-Timestamp':
                        self.callback_timestamp = parse_datetime(value)

                    # Subscribe
                    elif name == 'Subscription-TTL':
                        self.ttl = int(value)

                    else:
                        if name not in self.body:
                            self.body[name] = value
                        else:
                            if not isinstance(self.body[name], list):
                                self.body[name] = [self.body[name]]

                            self.body[name].append(value)
                except ValueError:
                    logging.debug('hiss.handler.GNTP.Response.unmarshal - Error splitting %s' % line)
                    raise

    def _encrypt(self, data):
        pass

    def _decrypt(self, lines):
        pass


class _RegisterRequest(Request):
    def __init__(self, notifier):
        Request.__init__(self)

        self.command = 'REGISTER'
        self.body['Application-Name'] = notifier.name
        self.body['Notifications-Count'] = len(notifier.notification_classes)

        if isinstance(notifier.icon, Icon):
            self._add_resource('Application-Icon', notifier.icon)
        else:
            self.body['Application-Icon'] = notifier.icon

        for info in notifier.notification_classes.values():
            section = {}
            section['Notification-Name'] = info.name
            section['Notification-Enabled'] = info.enabled

            self.sections.append(section)


class _NotifyRequest(Request):
    def __init__(self, notification, notifier):
        Request.__init__(self)

        self.command = 'NOTIFY'
        self.body['Application-Name'] = notifier.name
        self.body['Notification-Name'] = notification.name
        self.body['Notification-ID'] = notification.uid
        self.body['Notification-Title'] = notification.title

        if notification.text is not None:
            self.body['Notification-Text'] = notification.text

        if notification.timeout == 0:
            self.body['Notification-Sticky'] = 'True'

        if notification.sound is not None:
            self.body['X-Sound'] = notification.sound

        if isinstance(notification.icon, Icon):
            self._add_resource('Notification-Icon', notification.icon)
        else:
            self.body['Notification-Icon'] = notification.icon

        callback = notification.callback
        if callback is not None:
            if urlparse(callback.command).scheme != '':
                self.body['Notification-Callback-Target'] = callback.command
            else:
                self.body['Notification-Callback-Context'] = callback.command
                self.body['Notification-Callback-Context-Type'] = 'string'


class _SubscribeRequest(Request):
    def __init__(self, notifier):
        Request.__init__(self)

        self.command = 'SUBSCRIBE'
        self.body['Subscriber-ID'] = notifier.signature
        self.body['Subscriber-Name'] = notifier.name


class _UnregisterRequest(Request):
    def __init__(self, notifier):
        Request.__init__(self)

        self.command = 'REGISTER'
        self.body['Application-Name'] = notifier.name
        self.body['Notifications-Count'] = 0
