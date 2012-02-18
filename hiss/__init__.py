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

#from hiss.notifier import Notifier
#from hiss.notification import Notification
#from hiss.target import Target
#from hiss.message import Message
#from hiss.icon import Icon
#from hiss.exception import *

__all__ = ['PROTOCOLS', 'Notifier', 'Notification', 'Target',  'Message', 'Icon']

PROTOCOLS = {
    'gntp': [('hiss.protocol.gntp', 'GNTPProtocol'), None],
    'snp': [('hiss.protocol.snp', 'SNPProtocol'), None],
    #'growl': [('hiss.protocol.growl', 'GrowlProtocol'), None],
    #'snarl': [('hiss.protocol.snarl', 'SnarlProtocol'), None],
}

GROWL_PORT = 23053
SNARL_PORT = 9989

class ProtocolFactory(object):
    def __init__(self):
        pass

    def __getattr__(self, key):
        try:
            info  = PROTOCOLS[key]
            if info[1] is not None:
                return info[1]
                
            module = __import__(info[0][0], globals(), locals(), [info[0][1]], 0)
            info[1] = getattr(module, info[0][1])
            return info[1]
        except KeyError:
            raise Exception('Unknown protocol \'%s\' specified' % key)
        
