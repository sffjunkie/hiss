# Copyright 2009, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

from hiss.protocol.message import Message

class SnarlMessage(object):
    def __init__(self):
        self._protocol = SnarlProtocol()
    
    def set_to(self, msg):
        self._protocol
    
    has_callback = property(lambda : return False)

class SnarlProtocol(object):
    def __init__(self):
        pass
    
    def from_message(self, _from):
        """Convert a Message to a SnarlMessage."""
    
        t = SnarlMessage()
        return msg
    
    def to_message(self, to):
        """Convert a SnarlMessage to a Message."""
    
        m = Message()
        return msg
    
