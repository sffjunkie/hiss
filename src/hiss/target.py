# Copyright 2009, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

from hiss.protocol.gntp import GNTPMessage
from hiss.protocol.growl import GrowlMessage
from hiss.protocol.snarl import SnarlMessage
from hiss.protocol.snp import SNPMessage

class Target(object):
    PROTOCOLS = ['growl', 'snarl', 'gntp', 'snp']
    GROWL_PORT = 23053
    SNARL_PORT = 9989
    
    def __init__(self, target):
        """Set the target to either a string of the form
        
            protocol:address[options]
            
        where `options` is of the form :samp:`{option}={value}`
        
        or target is a Target instance
        """
        
        if isinstance(target, basestring):
            split = target.find('@')
            if split == -1:
                self._protocol = target
                self._address = ''
            else:
                self._protocol = target[:split]
                self._address = target[split+1:]
            
            split = self._address.find('[')
            if split != -1:
                if self._address[-1] != ']':
                    raise ValueError('Invalid options specified')
                    
                self._options = self._address[split+1:-2]
                self._address = self._address[:split]
            
            if self._protocol not in Target.PROTOCOLS:
                raise ValueError('%s is not a valid protocol currently one of %s' % (self._protocol, ', '.join(self.PROTOCOLS)))
    
            if self._address != '':
                if self._protocol == 'growl':
                    self._port = Target.GROWL_PORT
                elif self._protocol == 'snarl':
                    self._port = Target.SNARL_PORT
            else:
                self._port = -1
        elif isinstance(target, target):
            self._protocol = target.protocol
            self._address = target.address
            self._port = target.port
        else:
            raise TypeError('target must be either a string or a Target instance')

    def protocol():
        doc = """The protocol"""
        
        def fget(self):
            return self._protocol

        def fset(self, value):
            self._protocol = value

        return locals()

    protocol = property(**protocol())

    def address():
        doc = """The target IP address"""
        
        def fget(self):
            return self._address

        def fset(self, value):
            self._address = value

        return locals()

    address = property(**address())

    def port():
        doc = """The target port number"""
        
        def fget(self):
            return self._port

        def fset(self, value):
            self._port = value

        return locals()

    port = property(**port())

    def message():
        """The message class to fill in."""
        
        def fget(self):
            if self._address == '':
                if self._protocol == 'growl':
                    return GrowlMessage
                elif self._protocol == 'snarl':
                    return SnarlMessage
            else:
                if self._protocol == 'growl':
                    return GNTPMessage
                elif self._protocol == 'snarl':
                    return SNPMessage
            
        return locals()
        
    message = property(**message())
    
