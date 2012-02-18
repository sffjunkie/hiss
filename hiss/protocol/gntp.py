# Copyright 2009-2011, Simon Kennedy, python@sffjunkie.co.uk
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

# Part of 'hiss' the Python notification library

__all__ = ['GNTP', 'GNTPMessage']


class MessageError(Exception):
    pass


class MessageHeaders(dict):
    def __init__(self, message):
        self._message = message
    
    def __setitem__(self, item, value):
        if item.startswith('X-') or item in self._message.HEADERS:
            dict.__setitem__(self, item, value)
        else:
            raise KeyError('%s is not a valid header name')


class MessageBlock(dict):
    def __repr__(self):
        pass
    



class MessageResource(object):
    pass


class GNTPMessage(object):
    def __init__(self):
        self.NL = '\r\n'
        self.MESSAGE_TYPE = ['REGISTER', 'NOTIFY', 'SUBSCRIBE', '-OK', '-ERROR', '-CALLBACK']
        self.ENCRYPT_ALGORITHM = ['NONE', 'AES', 'DES', '3DES']
        self.HASH_ALGORITHM = ['MD5', 'SHA1', 'SHA256', 'SHA512']
        self.HEADERS = {'Application-Name': 'Wally',
            'Application-Icon': None,
            'Notifications-Count': None,
            'Notification-ID': None,
            'Notification-Name': None,
            'Notification-Display-Name': None,
            'Notification-Enabled': None,
            'Notification-Icon': None,
            'Notification-Title': None,
            'Notification-Text': None,
            'Notification-Sticky': None,
            'Notification-Priority': None,
            'Notification-Callback-Context': None,
            'Notification-Callback-Context-Type': None,
            'Notification-Callback-Target': None,
            'Connection': None,
            'Subscriber-ID': None,
            'Subscriber-Name': None,
            'Subscriber-Port': None,
            'Origin-Machine-Name': None,
            'Origin-Software-Name': None,
            'Origin-Software-Version': None,
            'Origin-Platform-Name': None,
            'Origin-Platform-Version': None,
            'Response-Action': None,
            'Subscription-TTL': None,
            'Error-Code': None,
            'Error-Description': None
        }
    
        self._magic = ''
        self._version = ''
        self._message_type = ''
        self._encrypt_algorithm = ''
        self._iv = ''
        self._hash_algorithm = ''
        self._key_hash = ''
        self._salt = ''
        self._headers = MessageHeaders(self)
        self._blocks = []
        self._resources = []

    def set_notification(self, notification):
        pass

    def add_header(self, name, value):
        self._headers[name] = value

    def add_block(self, block=None):
        if block is None:
            block = MessageBlock()
        self._blocks.append(block)
        return block

    def add_resource(self, resource=None):
        if resource is None:
            resource = MessageResource()
        self._resources.append(resource)
        return resource

    def marshall(self):
        """"Encode as a GNTP message string."""
    
        m = self.info_line
    
        for block in self.blocks:
            for header, value in block.headers:
                m += '%s:%s%s' % (header, value, self.NL)
            m += '%s%s' % (self.NL, self.NL)
    
        for resource in self.resources:
            m += 'Identifier: %s%s' % (resource.id, self.NL)
            m += 'Length: %s%s%s' % (resource.length, self.NL, self.NL)
            m += resource
    
        return m
    
    def unmarshall(self, msg):
        """"Decode into a GNTP message"""
    
        if isinstance(msg, basestring):
            lines = msg.split(self.NL)
            
        self._parse_info(lines[0])

        return msg
    
    def info_line():
        def fget(self):
            line = '%s/%s %s %s' % \
                (self.magic, self.version, self.message_type, self.encrypt_algo)
        
            if self._encrypt_type != 'NONE':
                line += ':%s %s:%s.%s%s' % (self.iv, self.hash_algo,
                    self.key_hash, self.salt, self.NL)
                
        def fset(self, line):
            items = line.split(' ')
            
            self.magic, self.version = items[0].split('/')
            
            if items[1] not in self.MESSAGE_TYPE:
                raise MessageError('Unknown message type \'%s\' must be one of %s' % \
                    (items[1], ', '.join(self.MESSAGE_TYPE)))
                
            count = len(items)
            if count > 2:
                try:
                    self.encrypt_algorithm, self.iv = items[2].split(':')
                except:
                    self.encrypt_algorithm = items[2]
                
                if count > 3:
                    self.hash_algorithm, hash_salt = items[3].split(':')
                    self.key_hash, self.salt = hash_salt.split('.')
        
        return locals()
        
    info_line = property(**info_line())

    def magic():
        def fget(self):
            return self._magic
            
        def fset(self, magic):
            if magic != 'GNTP':
                raise MessageError('GNTP message must start with \'GNTP\'')
                
            self._magic = magic

        return locals()
        
    magic = property(**magic())

    def version():
        def fget(self):
            return self._version
            
        def fset(self, version):
            if version != '1.0':
                raise MessageError('Unsupported message version %s' % version)
                
            self._version = version

        return locals()
        
    version = property(**version())
        
    def message_type():
        def fget(self):
            return self._message_type
            
        def fset(self, message_type):
            if message_type not in self.MESSAGE_TYPE:
                raise MessageError('Message message_type must be one of %s' % \
                    ', '.join(self.MESSAGE_TYPE))
                
            self._message_type = message_type

        return locals()
        
    message_type = property(**message_type())

    def has_callback():
        def fget(self):
            return \
            ('Notification-Callback-Context' in self.headers) and \
            ('Notification-Callback-Context-Type' in self.headers) and \
            (self.headers.get('Notification-Callback-Target', '') == '')

        return locals()
        
    has_callback = property(**has_callback())

    def encrypt_algorithm():
        def fget(self):
            return self._encrypt_algorithm
            
        def fset(self, encrypt_algorithm):
            if encrypt_algorithm not in self.ENCRYPT_ALGORITHM :
                raise MessageError('Message encrypt_type must be one of %s' % \
                    ', '.join(self.ENCRYPT_ALGORITHM))
                
            self._encrypt_algorithm = encrypt_algorithm

        return locals()
        
    encrypt_algorithm = property(**encrypt_algorithm())
    
    def iv():
        def fget(self):
            return self._iv
            
        def fset(self, value):
            self._iv = value
            
        return locals()
        
    iv = property(**iv())
        
    def hash_algorithm():
        def fget(self):
            return self._hash_algorithm
            
        def fset(self, hash_algorithm):
            if hash_algorithm not in self.HASH_ALGORITHM:
                raise MessageError('Message hash_type must be one of %s' %
                    ', '.join(self.HASH_ALGORITHM))
                
            self._hash_algorithm = hash_algorithm

        return locals()
        
    hash_algorithm = property(**hash_algorithm())
    
    def key_hash():
        def fget(self):
            return self._key_hash
            
        return locals()
        
    key_hash = property(**key_hash())
    
    def salt():
        def fget(self):
            return self._salt
            
        return locals()
        
    salt = property(**salt())

    def headers():
        def fget(self):
            return self._headers

        return locals()
        
    headers = property(**headers())
        
    def blocks():
        def fget(self):
            return self._blocks

        return locals()
        
    blocks = property(**blocks())
        
    def resources():
        def fget(self):
            return self._resources

        return locals()
        
    resources = property(**resources())

    def _app_name(self):
        pass




class GNTP(object):
    pass

class RegisterMessage(GNTPMessage):
    def __init__(self):
        GNTPMessage.__init__(self, 'REGISTER')

    def set_to(self, app):
        print(app)
        self.add_header('Application-Name', app.name)
        self.add_header('Application-Icon', app.icon)
        self.add_header('Notifications-Count', len(app.notifications))

        for n in app.notifications.itervalues():
            block = self.add_block()
            block['Notification-Name'] = n.name
            
            if n.display_name != '':
                block['Notification-Display-Name'] = n.display_name

            block['Notification-Enabled'] = n.enabled


class NotifyMessage(GNTPMessage):
    def __init__(self):
        GNTPMessage.__init__(self, 'NOTIFY')

    def set_to(self, n):
        self.add_header('Application-Name', n.application)
        self.add_header('Notification-Name', n.application)


class SubscribeMessage(GNTPMessage):
    def __init__(self):
        GNTPMessage.__init__(self, 'SUBSCRIBE')

    def set_to(self, n):
        self.add_header('Application-Name', n.application)
        self.add_header('Notification-Name', n.application)


class OKMessage(GNTPMessage):
    def __init__(self):
        GNTPMessage.__init__(self, '-OK')

    def set_to(self, n):
        self.add_header('Application-Name', n.application)
        self.add_header('Notification-Name', n.application)


class ErrorMessage(GNTPMessage):
    def __init__(self):
        GNTPMessage.__init__(self, '-ERROR')

    def set_to(self, n):
        self.add_header('Application-Name', n.application)
        self.add_header('Notification-Name', n.application)


class CallbackMessage(GNTPMessage):
    def __init__(self):
        GNTPMessage.__init__(self, '-CALLBACK')

    def set_to(self, n):
        self.add_header('Application-Name', n.application)
        self.add_header('Notification-Name', n.application)



