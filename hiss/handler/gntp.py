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

from __future__ import unicode_literals

import re
import socket
import logging
from os import urandom
from hashlib import sha256
from binascii import hexlify
from collections import Callable

from hiss.handler import Handler
from hiss.resource import Icon

GNTP_SCHEME = 'gntp'
GNTP_DEFAULT_PORT = 23053
GNTP_BASE_VERSION = '1.0'

class GNTPError(Exception):
    pass


class GNTP(Handler):
    """Send GNTP messages synchronously."""
    
    name = 'GNTP'
    
    def __init__(self, notifier=None, port=GNTP_DEFAULT_PORT,
                 response_handler=None):
        Handler.__init__(self, notifier, port)
        
        self.capabilities = {
            'show_hide': False,
            'register': True,
            'unregister': False
        }
        
        self.response_handler = response_handler

    def register(self, target, notifier=None):
        """Register a ``notifier`` with a ``target`` 
        
        :param target: The target to register the notifier with
        :type target:  :class:`~hiss.target.Target`
        :param notifier: The Notifier to register or the default notifier
                         if None
        :type notifier:  :class:`~hiss.notifier.Notifier` or None
        """
        
        target = self._get_targets(target)
        notifier = self._get_notifier(notifier)

        responses = []
        for target in target:
            request = _RegisterRequest(notifier)
            response_data = self._send_request(request, target)
            response = self._handle_response(response_data)
            responses.append(response)
        
        if len(responses) == 1:
            responses = responses[0]
        
        if isinstance(self.response_handler, Callable):
            self.response_handler(response)
        return response

    def unregister(self, targets, notifier=None):
        """Unregister a notifier with a target
        
        :param target: The target to unregister the notifier with
        :type target:  :class:`~hiss.target.Target`
        :param notifier: The Notifier to unregister or the default notifier
                         if None
        :type notifier:  :class:`~hiss.notifier.Notifier` or None
        """
        
        targets = self._get_targets(targets)
        notifier = self._get_notifier(notifier)

        responses = []
        for target in targets:
            request = _UnregisterRequest(notifier)
            response_data = self._send_request(request, target)
            response = self._handle_response(response_data)
            responses.append(response)
        
        if len(responses) == 1:
            responses = responses[0]

        if isinstance(self.response_handler, Callable):
            self.response_handler(response)
        return response

    def notify(self, notification, notifier=None, targets=None, handler=None):
        """Send a notification
        
        Send to either to all known targets or a specific target or list of
        targets
        
        :param notification: The notification to send
        :type notification: :class:`~hiss.notification.Notification`
        :param notifier: The notifier to send the notification for or None for
                         the default notifier.
        :type notifier:  :class:`~hiss.notifier.Notifier`
        :param targets:  The target or list of targets to send the notification
                         to or None for all targets
        :type targets:   :class:`~hiss.target.Target` or list of Target
        """
        
        targets = self._get_targets(targets)
        notifier = self._get_notifier(notifier)
        
        responses = []
        for target in targets:
            request = _NotifyRequest(notifier, notification)
            response_data = self._send_request(request, target)
            response = self._handle_response(response_data,
                                            notification.has_callback)
            response['id'] = request.header['Notification-ID']
            responses.append(response)
        
        if len(responses) == 1:
            responses = responses[0]

        if isinstance(self.response_handler, Callable):
            self.response_handler(responses)
            
        return responses

    def _send_request(self, request, target):
        if target.password is not None:
            password = target.password.encode(encoding)
            salt = urandom(16)
            key_basis = password + salt
            
            key = sha256(key_basis).digest()
            key_hash = sha256(key)
            
            request.hash = ('SHA256', hexlify(key_hash), hexlify(salt))

        request_data = request.marshall()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target.host, target.port))
        s.send(request_data)
        
        response_data = ''
        
        while True:
            data = s.recv(1024)
            
            if not data:
                break
            
            response_data += data
        
        s.close()
        return response_data

    def _handle_response(self, response_data, with_callback=False):
        callback_response = None
        if with_callback:
            items = response_data.split('\r\n\r\n')
            response_data = items[0]
            callback_data = items[1] 
            
            callback_response = Response()
            callback_response.unmarshall(callback_data)
    
        response = Response()
        response.unmarshall(response_data)
        
        result = {}
        result['result'] = response.result
        if callback_response is not None:
            result['callback_result'] = callback_response.status_name
            result['callback_data'] = callback_response.data
        return result


class Request(object):
    def __init__(self, version=GNTP_BASE_VERSION, password=''):
        self.version = version
        self.command = ''
        self.header = {}
        self.sections = []
        self.identifiers = []
        self.password = password
        self.hash = None
        self.encryption = None
    
    def add_resource(self, key, resource):
        uid = resource.uid
        data = resource.data
        self.header[key] = 'x-growl-resource://%s' % uid
        
        identifier = {}
        identifier['Identifier'] = uid
        identifier['Data'] = data
        self.identifiers.append(identifier)
    
    def marshall(self, encoding='UTF-8'):
        """Marshall the request ready to send over the wire."""
        
        header = 'GNTP/%s %s' % (self.version, self.command)
        if self.encryption is not None:
            header += ' %s:%s' % self.encryption
        else:
            header += ' NONE'
        
        if self.hash is not None:
            header += ' %s:%s.%s' % self.hash
            
        header += '\r\n'
        data = header.encode(encoding)
        
        for name, value in self.header.items():
            data += ('%s: %s\r\n' % (name, value)).encode(encoding)
        
        data += ('\r\n').encode(encoding)
        
        for section in self.sections:
            for name, value in section.items():
                data += ('%s: %s\r\n' % (name, value)).encode(encoding)
        
            data += ('\r\n').encode(encoding)
            
        for identifier in self.identifiers:
            data += ('Identifier: %s\r\n' % identifier['Identifier']).encode(encoding)
            idata = identifier['Data']
            data += ('Length: %d\r\n\r\n' % len(idata)).encode(encoding)
            data += idata
            data += ('\r\n\r\n').encode(encoding)
            
        return data
            
    def unmarshall(self, data, encoding='UTF-8'):
        """Unmarshall data received over the wire into a valid request"""
        
        sections = data.split(b'\r\n\r\n')
        
        header_re = b'GNTP\/(?P<version>\d\.\d) (?P<command>[A-Z]+)( ((?P<encryptionAlgorithmID>\w+)\:(?P<ivValue>[a-fA-F0-9]+)|NONE)( (?P<keyHashAlgorithmID>\w+)\:(?P<keyHash>[a-fA-F0-9]+)\.(?P<salt>[a-fA-F0-9]+))?)?'.encode(encoding)
        header = sections[0]
        m = re.match(header_re, header)
            
        if m is not None:
            d = m.groupdict()
            self.version = d[b'version']
            self.command = d[b'bcommand']
            
            if d['encryptionAlgorithmID'] is None:
                self.encryption = None
            else:
                self.use_encryption = True
                self.encryption = (d[b'encryptionAlgorithmID'],
                                   d[b'ivValue'])
            
            if d['keyHashAlgorithmID'] is None:
                self.hash = None
            else:
                self.use_hash = True
                self.hash = (d[b'keyHashAlgorithmID'],
                             d[b'keyHash'],
                             d[b'salt'])
                
            self._unmarshall_section(header.split(b'\r\n'.encode(encoding))[1:], self.header)
            
            info = None
            next_is_id = False
            for section in sections[1:]:
                if not next_is_id:
                    info = {}
                    self._unmarshall_section(section.split(b'\r\n'.encode(encoding)), info)
                    
                    if 'Identifier' in info:
                        next_is_id = True
                        self.identifiers.append(info)
                    else:
                        self.sections.append(info)
                elif info is not None:
                    info['Data'] = section
                    next_is_id = False

            for section in self.sections:
                for name, value in section.items():
                    if value.startswith(b'x-growl-resource://'):
                        value = value[19:]
                        d = self.identifier_data(value)
                        
                        if d is None:
                            raise GNTPError('unmarshall: Unable to find data for identifier %s' % value)
                        
                        section[name] = d
        else:
            raise GNTPError('hiss.GNTP.unmarshall: Invalid GNTP message')

    def _unmarshall_section(self, lines, info):
        for line in lines:
            try:
                name, value = line.split(':', 1)
                info[name.decode('UTF-8')] = value.strip()
            except:
                pass
            
    def identifier_data(self, identifier):
        for i in self.identifiers:
            if i['Identifier'] == identifier:
                return i['Data']
        
        return None

    def _encrypt(self):
        pass

    def _decrypt(self):
        pass


class Response(object):
    """GNTP/1.0 -OK|-ERROR|-CALLBACK <encryptionAlgoritm>
    <header>: <value>
    """
    
    def __init__(self):
        self.version = '1.0'
        """The GNTP protocol version number of this response"""
        
        self.result = ''
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
        
        data = 'GNTP/%s -%s' % (self.version, self.result)
        
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
            self.result = d['responsetype'].lstrip('-')
            
            if self.result == 'ERROR':
                self.status_code = 1
            
            self.isevent = (self.result == 'CALLBACK')
            
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
                        logging.debug('hiss.GTNP.unmarshall - Error splitting %s' % line)

    def _encrypt(self):
        pass

    def _decrypt(self):
        pass


class _RegisterRequest(Request):
    def __init__(self, notifier):
        Request.__init__(self)
        
        self.command = 'REGISTER'
        self.header['Application-Name'] = notifier.title
        self.header['Notifications-Count'] = len(notifier.notification_classes)
            
        if isinstance(notifier.icon, Icon):
            self.add_resource('Application-Icon', notifier.icon)
        else:
            self.header['Application-Icon'] = notifier.icon
        
        for info in notifier.notification_classes.values():
            section = {}
            section['Notification-Name'] = info.name
            section['Notification-Enabled'] = info.enabled
                    
            self.sections.append(section)


class _NotifyRequest(Request):
    def __init__(self, notifier, notification):
        Request.__init__(self)
        
        self.command = 'NOTIFY'
        self.header['Application-Name'] = notifier.title
        self.header['Notification-Name'] = notification.name
        self.header['Notification-ID'] = notification.uid
        self.header['Notification-Title'] = notification.title
        
        if notification.text is not None:
            self.header['Notification-Text'] = notification.text
            
        if notification.timeout == 0:
            self.header['Notification-Sticky'] = 'True'
            
        if notification.sound is not None:
            self.header['X-Sound'] = notification.sound
            
        if isinstance(notification.icon, Icon):
            self.add_resource('Notification-Icon', notification.icon)
        else:
            self.header['Notification-Icon'] = notification.icon
        
        callback = notification.callback
        if callback is not None:
            if callback.command.startswith('http://'):
                self.header['Notification-Callback-Target'] = callback.command
            else:
                self.header['Notification-Callback-Context'] = callback.command
                self.header['Notification-Callback-Context-Type'] = 'string'
        
        
class _SubscribeRequest(Request):
    def __init__(self, notifier):
        Request.__init__(self)
        
        self.command = 'SUBSCRIBE'
        self.header['Subscriber-ID'] = notifier.uid
        self.header['Subscriber-Name'] = notifier.title
        
        
class _UnregisterRequest(Request):
    def __init__(self, notifier):
        Request.__init__(self)
        
        self.command = 'REGISTER'
        self.header['Application-Name'] = notifier.title
        self.header['Notifications-Count'] = 0

