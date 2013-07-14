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

import re
import socket
import logging
from collections import Callable

from hiss.target import Target
from hiss.handler import TargetList
from hiss.resource import Resource

GNTP_SCHEME = 'gntp'
GNTP_DEFAULT_PORT = 23053
GNTP_BASE_VERSION = '1.0'

class GNTPError(Exception):
    pass
        
class GNTP(object):
    def __init__(self, notifier=None, handler=None):
        self._notifier = notifier
        self._handler = handler
        self._targets = TargetList()
    
    def connect(self, target):
        """Connect to a target
        
        :param target: Target to connect to
        :type target:  :class:`hiss.Target`
        """
            
        target.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #target.socket.settimeout(0.5)
        target.socket.connect((target.host, GNTP_DEFAULT_PORT))
        target.port = GNTP_DEFAULT_PORT
        target.handler = self
        self._targets.append(target)

    def disconnect(self, target):
        """Disconnect from a target
        
        :param target: Target to disconnect from
        :type target:  :class:`hiss.Target`
        """
        
        if target in self._targets:
            if target.socket is not None:
                target.socket.close()
                target.socket = None
            target.handler = None
            self._targets.remove(target)
        else:
            raise ValueError('GNTP: disconnect - Not connected to target')

    def register(self, target, notifier=None):
        """Register a ``notifier`` with a ``target`` 
        
        :param target: The target to register the notifier with
        :type target:  :class:`~hiss.target.Target`
        :param notifier: The Notifier to register or the default notifier
                         if None
        :type notifier:  :class:`~hiss.notifier.Notifier` or None
        """
        
        notifier = self._get_notifier(notifier)

        request = RegisterRequest(notifier)
        response = self._send_request(request, target)
        
        if isinstance(self._handler, Callable):
            self._handler(response)
        return response

    def unregister(self, target, notifier=None):
        """Unregister a notifier with a target
        
        :param target: The target to unregister the notifier with
        :type target:  :class:`~hiss.target.Target`
        :param notifier: The Notifier to unregister or the default notifier
                         if None
        :type notifier:  :class:`~hiss.notifier.Notifier` or None
        """
        
        notifier = self._get_notifier(notifier)

        request = UnregisterRequest(notifier)
        response = self._send_request(request, target)

        if isinstance(self._handler, Callable):
            self._handler(response)
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
            request = NotifyRequest(notifier, notification)
            response = self._send_request(request, target,
                                          notification.has_callback)
            responses.append(response)
        
        if len(responses) == 1:
            responses = responses[0]

        if isinstance(self._handler, Callable):
            self._handler(response)
            
        return responses

    def _get_targets(self, targets):
        if targets is None:
            targets = self._targets
        elif isinstance(targets, Target):
            if targets not in self._targets:
                raise ValueError('hiss.GNTP: Unable to send request - Target unknown')
            else:
                targets = [targets]
        elif isinstance(targets, list):
            targets = []
            for t in targets:
                if isinstance(t, Target):
                    if t.port == -1:
                        t.port = GNTP_DEFAULT_PORT
                        
                    if t in self._targets:
                        targets.append(t)
            
            if len(targets) == 0:
                raise ValueError('hiss.GNTP: Unable to send request - No valid targets specified')
        return targets

    def _get_notifier(self, notifier):
        if notifier is None:
            notifier = self._notifier
        if notifier is None:
            raise ValueError('hiss.GNTP: No notifier specified')
        return notifier

    def _send_request(self, request, target, with_callback=False):
        request_data = request.marshall()
        target.socket.send(request_data)
        
        response_data = ''
        
        while True:
            data = target.socket.recv(1024)
            
            if not data:
                break
            
            response_data += data
        
        if with_callback:
            items = response_data.split('\r\n\r\n')
            response_data = items[0]
            callback_data = items[1] 
            
            callback_response = GNTPResponse()
            callback_response.unmarshall(callback_data)
    
        response = GNTPResponse()
        response.unmarshall(response_data)
        
        if with_callback:
            return (response, callback_response)
        else:
            return response


class GNTPRequest(object):
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
        identifier['identifier'] = uid
        identifier['data'] = data
        self.identifiers.append(identifier)
    
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
            data += 'Identifier: %s\r\n' % identifier['identifier']
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
            raise GNTPError('hiss.GNTP.unmarshall: Invalid GNTP message')

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
        
        self.type = ''
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
        
        data = 'GNTP/%s -%s' % (self.version, self.type)
        
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
            self.type = d['responsetype'].lstrip('-')
            
            if self.type == 'ERROR':
                self.status_code = 1
            
            self.isevent = (self.type == 'CALLBACK')
            
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


class RegisterRequest(GNTPRequest):
    def __init__(self, notifier):
        GNTPRequest.__init__(self)
        
        self.command = 'REGISTER'
        self.header['Application-Name'] = notifier.name
        self.header['Notifications-Count'] = len(notifier.notification_classes)
            
        if isinstance(notifier.icon, Resource):
            self.add_resource('Application-Icon', notifier.icon)
        else:
            self.header['Application-Icon'] = notifier.icon
        
        for info in notifier.notification_classes.values():
            section = {}
            section['Notification-Name'] = info.name
            section['Notification-Enabled'] = info.enabled
                    
            self.sections.append(section)


class NotifyRequest(GNTPRequest):
    def __init__(self, notifier, notification):
        GNTPRequest.__init__(self)
        
        self.command = 'NOTIFY'
        self.header['Application-Name'] = notifier.name
        self.header['Notification-Name'] = notification.name
        self.header['Notification-ID'] = notification.uid
        self.header['Notification-Title'] = notification.title
        
        if notification.text is not None:
            self.header['Notification-Text'] = notification.text
            
        if notification.timeout == 0:
            self.header['Notification-Sticky'] = 'True'
            
        if notification.sound is not None:
            self.header['X-Sound'] = notification.sound
            
        if isinstance(notification.icon, Resource):
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
        
        
class SubscribeRequest(GNTPRequest):
    def __init__(self, notifier):
        GNTPRequest.__init__(self)
        
        self.command = 'SUBSCRIBE'
        self.header['Subscriber-ID'] = notifier.uid
        self.header['Subscriber-Name'] = notifier.name
        
        
class UnregisterRequest(GNTPRequest):
    def __init__(self, notifier):
        GNTPRequest.__init__(self)
        
        self.command = 'REGISTER'
        self.header['Application-Name'] = notifier.name
        self.header['Notifications-Count'] = 0

