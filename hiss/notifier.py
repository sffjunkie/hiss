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
from hiss.resource import Icon
from hiss.notification import Notification, NotificationInfo

__all__ = ['Notifier']


class Notifier(object):
    def __init__(self, uid=None):
        if uid is None:
            self.nid = uuid.uuid4()
        else:
            self.nid = uid
        
        self.name = ''
        self._icon = None
        self._targets= {}
        self._notifications= {}

    def icon():
        def fset(self, icon):
            if isinstance(icon, Icon):
                self._icon = icon
            else:
                if icon != '':
                    self._icon = Icon(icon)
                    
        def fget(self):
            return self._icon
        
        return locals()
        
    icon = property(**icon())

    def add_notification(self, name, description, icon, enabled):
        self._notifications[name] = NotificationInfo(name, description, icon, enabled)

    def notification(self, name, title='', text='', icon_url=''):
        if name not in self._notifications:
            raise KeyError('\'%s\' is not a known notification. Must be one of %' % (name, ','.join(self._notifications)))
            
        n =  Notification(name, title, text, enabled=True)
        return n

    def remove_notification(self, name):
        del self._notifications[name]

    def add_target(self, target):
        self._targets[target] = Target(target)
 
    def remove_target(self, target):
        if target in self._targets:
            del self._targets[target]
 
    def register(self):
        """Register ourselves with the targets"""

        for target in self._targets.items():
            msg = target.handler.RegisterMessage()
        
            for info in self._notifications.values():
                msg.append(info)
            
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

    def send(self, notification):
        def success(result):
            pass
        
        def fail(failure):
            pass
        
        d = self._protocol_handler.send(notification, self._host)
        d.addCallback(success)
        d.addErrback(fail)

