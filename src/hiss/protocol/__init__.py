# Copyright 2009, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

from hiss.protocol.growl import GrowlProtocol
from hiss.protocol.gntp import GrowlNetworkProtocol
from hiss.protocol.snarl import SnarlProtocol
from hiss.protocol.snp import SnarlNetworkProtocol

__all__ = ['GrowlProtocol', 'GrowlNetworkProtocol',
    'SnarlProtocol', 'SnarlNetworkProtocol',
    'get_protocol']
    
def get_protocol(name):
    name = name.lower()
    
    if name == 'growl':
        return GrowlProtocol
    elif name == 'gntp':
        return GrowlNetworkProtocol
    elif name == 'snarl':
        return SnarlProtocol
    elif name == 'sp':
        return SnarlNetworkProtocol
    else:
        raise NotImplementedError

