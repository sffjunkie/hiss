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

import uuid

from hiss.target import Target
from hiss.resource import Resource
from hiss.notification import Notification

__all__ = ['Notifier']

class Notifier(object):
    def __init__(self, uid=None):
        if uid is None:
            self.nid = uuid.uuid4()
        else:
            self.nid = uid
        
        self.name = ''
        self.icon = None

        self._targets = {}
        self._notifications = {}

    def load_icon(self, url):
        if url is not None and url != '':
            self.icon = Resource(url)
            self.icon.load()

    def add_notification(self, info):
        self._notifications[info[0]] = info

    def get_notification(self, name, title='', text='', icon_url=''):
        if name not in self._notifications:
            raise KeyError('\'%s\' is not a known notification. Must be one of %' % (name, ','.join(self._notifications)))
            
        n =  Notification(name, title, text, enabled=True)

    def remove_notification(self, name):
        del self._notifications[name]

    def add_target(self, target):
        if target not in self._targets:
            self._targets[target] = Target(target)
 
    def remove_target(self, target):
        if target in self._targets:
            del self._targets[target]
 
    def register(self, t):
        """Register ourselves with the targets"""

        for target in self._targets.items():
            msg = target.protocol.RegisterMessage()
        
            for name, enabled in self._notifications.values():
                msg.add_notification(name, enabled)
            
            target.send(msg)
    
    def notify(self, notification, target=None):
        if target is not None:
            if isinstance(target, list):
                send_to = target
            else:
                send_to = [target]
        elif self._targets is not None:
            send_to = self._targets.values()
        else:
            raise ValueError('Valid target not specified. Either specifiy the target parameter or set Notifier.target.')

        for target in send_to:
            if isinstance(target, basestring):
                target = Target(target)
                
            msg = target.protocol.NotifyMessage()
            msg.set_to(notification)
            target.protocol.notify(msg)

