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

log = logging.getLogger('hiss')
log.setLevel(logging.DEBUG)
console = logging.StreamHandler()
log.addHandler(console)

GNTP_SCHEME = 'gntp'
GNTP_DEFAULT_PORT = 23053
GNTP_DEFAULT_VERSION = '1.0'

class GNTPError(Exception):
    pass


class GNTPRequest(object):
    def __init__(self, version=GNTP_DEFAULT_VERSION, password='',
                 use_hash=False, use_encryption=False):
        self.command = ''
        self.version = version
        self.header = {}
        self.sections = []
        self.password = password
        self.use_hash = use_hash
        self.use_encryption = use_encryption
    
    def marshall(self):
        """Marshall the request ready to send over the wire."""
        
        data = 'GNTP/%s %s' % (self.version, self.command)
        if self.use_encryption:
            pass
        
        if self.use_hash:
            data += '%s' % self._hash
        
    
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
                    self.sections.append(info)
                    
                    if 'Identifier' in info:
                        next_is_id = True
                elif info is not None:
                    info['data'] = section
                    next_is_id = False
        else:
            raise GNTPError('Invalid GNTP message passed to unmarshall()')

    def _unmarshall_section(self, lines, info):
        for line in lines:
            try:
                name, value = line.split(':', 1)
                info[name] = value.strip()
            except:
                pass


class GNTPResponse(object):
    def __init__(self):
        self.version = ''
        """The GNTP protocol version number of this response"""
    
    def marshall(self):
        """Marshall the request ready to send over the wire."""
    
    def unmarshall(self, data):
        """Unmarshall _data received over the wire into a valid request"""


class RegisterRequest(object):
    def __init__(self, notifier):
        self.commands = []
        
        self.commands.append(('Application-Name', notifier.name))
        self.commands.append(('notifications-Count', len(notifier.notification_classes)))
        
        self.id_sections = []
        if isinstance(notifier.icon, Icon):
            res_id = notifier.icon.res_id()
        else:
            self.commands.append(('Application-Icon', notifier.icon))


class NotifyRequest(object):
    def __init__(self, notifier):
        self.commands = []
        
        
class SubscribeRequest(object):
    def __init__(self, notifier):
        self.commands = []
        

class GNTP(object):
    """Growl Network Transfer Protocol handler"""
    
    def __init__(self, event_handler=None):
        self._targets = []
        self._event_handler = event_handler
        self._factory = GNTPFactory(self._snp_event_handler)
    

class GNTPFactory(ClientFactory):
    def __init__(self, event_handler=None):
        self._protocol_map = []
        self._event_handler = event_handler


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
        
        self.deferred = None
        self._response = GNTPResponse()
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
            self._response = GNTPResponse()
    
    def send_data(self, data):
        """Send a single GNTP request."""
        
        self.transport.write(data)
    