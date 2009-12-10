# Copyright 2009, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

__all__ = ['Message', 'RegisterMessage', 'NotifyMessage', 'SubscribeMessage',
    'OKMessage', 'ErrorMessage', 'CallbackMessage']

class Message(object):
    nl = '\r\n'
    TYPES = ['REGISTER', 'NOTIFY', 'SUBSCRIBE', '-OK', '-ERROR', '-CALLBACK']
    ENCRYPT_TYPES = ['NONE', 'AES', 'DES', '3DES']
    HASH_TYPES = ['MD5', 'SHA1', 'SHA256', 'SHA512']
    HEADERS = ['Application-Name', 'Application-Icon',
        'Notifications-Count', 'Notification-ID',
        'Notification-Name', 'Notification-Display-Name',
        'Notification-Enabled', 'Notification-Icon',
        'Notification-Title', 'Notification-Text',
        'Notification-Sticky', 'Notification-Priority',
        'Notification-Callback-Context', 'Notification-Callback-Context-Type',
        'Notification-Callback-Target',
        'Connection',
        'Subscriber-ID', 'Subscriber-Name', 'Subscriber-Port',
        'Origin-Machine-Name', 'Origin-Software-Name', 'Origin-Software-Version',
        'Origin-Platform-Name', 'Origin-Platform-Version',
        'Response-Action', 'Subscription-TTL',
        'Error-Code', 'Error-Description']
    
    def __init__(self, type=None):
        self._version = '1.0'
        self._message_type = ''
        self._encrypt_type = ''
        self._hash_type = ''
        self._key_hash = ''
        self._iv = ''
        self._salt = ''
        self._headers = MessageHeaders()
        self._blocks = []
        self._resources = []

    def add_header(self, name, value):
        self._headers[name] = value

    def add_block(self):
        block = MessageBlock()
        self._blocks.append(block)
        return block

    def add_resource(self):
        resource = MessageResource()
        self._resources.append(resource)
        return resource

    def add_notification(self, notification):
        pass

    def to_raw(self):
        """"Encode as a GNTP message string."""
    
        crlf = '\r\n'
        
        m = self._info_line()
    
        for block in self.blocks:
            for header, value in block.headers:
                m += '%s:%s%s' % (header, value, crlf)
            m += '%s%s' % (crlf, crlf)
    
        for resource in self.resources:
            m += 'Identifier: %s%s' % (resource.id, crlf)
            m += 'Length: %s%s%s' % (resource.length, crlf, crlf)
            m += res
    
        return m
    
    def from_raw(self, string):
        """"Decode into a GNTP message"""
    
        msg = message
        return msg
    
    def _info_line(self):
        line = 'GNTP/%s %s %s' % (self._version, self._message_type, self._encrypt_type)
        
        if self._encrypt_type != 'NONE':
            line += ':%s %s:%s.%s%s' % (self._iv, self._hash_type, self._key_hash, self._salt, Message.nl)

    def version():
        def fget(self):
            return self._version
            
        def fset(self, version):
            if version != '1.0':
                raise ValueError('Message version must be 1.0')
                
            self._version = version

        return locals()
        
    version = property(**version())
        
    def message_type():
        def fget(self):
            return self._message_type
            
        def fset(self, message_type):
            if message_type not in Message.TYPES:
                raise ValueError('Message message_type must be one of %s' % ', '.join(Message.TYPES))
                
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

    def encrypt_type():
        def fget(self):
            return self._encrypt_type
            
        def fset(self, encrypt_type):
            if encrypt_type not in Message.ENCRYPT_TYPES:
                raise ValueError('Message encrypt_type must be one of %s' % ', '.join(Message.ENCRYPT_TYPES))
                
            self._encrypt_type = encrypt_type

        return locals()
        
    encrypt_type = property(**encrypt_type())
    
    def iv():
        def fget(self):
            return self._iv
            
        return locals()
        
    iv = property(**iv())
        
    def hash_type():
        def fget(self):
            return self._hash_type
            
        def fset(self, hash_type):
            if hash_type not in Message.HASH_TYPES:
                raise ValueError('Message hash_type must be one of %s' % ', '.join(Message.HASH_TYPES))
                
            self._hash_type = hash_type

        return locals()
        
    hash_type = property(**hash_type())
    
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

    @staticmethod
    def create(notification):
        pass

class RegisterMessage(Message):
    def __init__(self):
        Message.__init__(self, 'REGISTER')

    def set_to(self, a):
        print(a)
        self.add_header('Application-Name', a.name)
        self.add_header('Application-Icon', a.icon)
        self.add_header('Notifications-Count', len(a.notifications))

        for n in a.notifications.itervalues():
            block = self.add_block()
            block['Notification-Name'] = n.name
            
            if n.display_name != '':
                block['Notification-Display-Name'] = n.display_name

            block['Notification-Enabled'] = n.enabled

class NotifyMessage(Message):
    def __init__(self):
        Message.__init__(self, 'NOTIFY')

    def set_to(self, n):
        self.add_header('Application-Name', n.application)
        self.add_header('Notification-Name', n.application)

class SubscribeMessage(Message):
    def __init__(self):
        Message.__init__(self, 'SUBSCRIBE')

    def set_to(self, n):
        self.add_header('Application-Name', n.application)
        self.add_header('Notification-Name', n.application)

class OKMessage(Message):
    def __init__(self):
        Message.__init__(self, '-OK')

    def set_to(self, n):
        self.add_header('Application-Name', n.application)
        self.add_header('Notification-Name', n.application)

class ErrorMessage(Message):
    def __init__(self):
        Message.__init__(self, '-ERROR')

    def set_to(self, n):
        self.add_header('Application-Name', n.application)
        self.add_header('Notification-Name', n.application)

class CallbackMessage(Message):
    def __init__(self):
        Message.__init__(self, '-CALLBACK')

    def set_to(self, n):
        self.add_header('Application-Name', n.application)
        self.add_header('Notification-Name', n.application)

class MessageHeaders(dict):
    def __setitem__(self, item, value):
        if item.startswith('X-') or item in Message.HEADERS:
            dict.__setitem__(self, item, value)
        else:
            raise KeyError('%s is not a valid header name')
        
class MessageBlock(dict):
    def __repr__(self):
        pass
    
    def hash(self):
        pass

class MessageResource(object):
    def __init__(self):
        self._resource_uri = ''
    
    def resource_uri():
        def fget(self):
            return self._resource_uri

class Icon(MessageResource):
    pass

