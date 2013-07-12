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

import uuid
from collections import namedtuple

import logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

from twisted.internet import defer

from hiss.handler.snp import SNP
from hiss.handler.gntp import GNTP
from hiss.notification import Notification

__all__ = ['Notifier', 'USE_NOTIFIER', 'USE_REGISTERED']

NotificationInfo = namedtuple('NotificationInfo', ['name', 'title', 'text',
                                                   'icon', 'sound', 'enabled'])

USE_NOTIFIER = -1
USE_REGISTERED = -2

class Notifier(object):
    def __init__(self, signature, name, icon=None, sound=None, uid=None):
        """Create a new default_notifier
        
        :param signature: The MIME style application signature for this default_notifier
                          of the form :samp:`application/x-vnd.{vendor}.{app}`
        :type signature:  string
        :param name:      The name of this default_notifier
        :type name:       string
        :param icon:      Notifier icon. Used when registering the notifier and
                          as the default icon for notifications.
        :type icon:       :class:`~hiss.resource.Icon` or string
        :param uid:       Unique id to use for this default_notifier. If not specified, 
                          one will be provided for you. The ``uid`` will
                          be used as the password for 'secured' communications.
        """
        
        self.signature = signature
        self.name = name
        self.icon = icon
        self.sound = sound
        
        if uid is None:
            self.uid = self._unique_id()
        else:
            self.uid = uid
            
        self.notification_classes = {}
        
        self._handlers = {}
        self._notifications = {}

    def add_notification(self, name, title=None, text=None,
                              icon=None, sound=None,
                              enabled=True):
        """Add a notification class.
        
        :param name:          Notification class name
        :type name:           string
        :param title:         Default notification title
        :type title:          string or ``None`` for no default
        :param text:          Default notification text
        :type text:           string or ``None`` for no default
        :param icon:          Default notification icon
        :type icon:           string or ``None`` for no default
        :param sound:         Default notification sound
        :type sound:          string or ``None`` for no default
        :param enabled:       Whether the notification is enabled or not
        :type enabled:        boolean
        :returns:             The class id of the newly added notification
        :rtype:               integer
        """
        
        class_id = len(self.notification_classes) + 1
        self.notification_classes[class_id] = \
            NotificationInfo(name, title, text, icon,
                             sound, enabled)
            
        return class_id
 
    def add_target(self, target):
        """Add a target to the list of known targets
        
        :param target: The Target to add.
        :type target:  :class:`hiss.Target`
        :returns:      A :class:`.defer.Deferred`
                       which fires when connected.
        """
        
        if target.scheme in self._handlers:
            handler = self._handlers[target.scheme]
        elif target.scheme == 'snp':
            handler = SNP(notifier=self, event_handler=self._handler)
            self._handlers[target.scheme] = handler
        elif target.scheme == 'gntp':
            handler = GNTP(notifier=self, event_handler=self._handler)
            self._handlers[target.scheme] = handler
        
        target.handler = handler
        return handler.connect(target)
 
    def remove_target(self, target):
        """Remove a previously added target.
        
        :param target: The Target to add.
        :type target:  :class:`hiss.Target`
        """
        
        if target.handler is not None:
            return target.handler.disconnect(target)
        else:
            return defer.fail(False)

    def register(self, targets=None):
        """Register this notifier with the targets specified.
        
        :param targets: The targets to register with.
                        If not specified or ``None`` then the notifier
                        will be registered with all known targets
        :type targets:  :class:`hiss.Target` or ``None``
        """
        
        if targets is None:
            handlers = self._handlers
        elif targets.handler is not None:
            handlers = [targets.handler]
        
        ds = []
        for handler in handlers.values():
            d = handler.register(self, targets)
            ds.append(d)
        
        if len(ds) == 1:
            return ds[0]
        else:
            return ds

    def create_notification(self, class_id=-1, name='',
                            title=None, text=None,
                            icon=None, sound=None):
        """Create a notification that is ready to send.
        
        Either ``class_id`` or ``name`` can be provided. If ``class_id`` is
        provided it will be used instead of ``name`` to
        lookup the defaults registered in
        :meth:`~Notifier.add_notification`
        
        :param class_id:   The notification class id
        :type class_id:    integer
        :param name:       The notification name
        :type name:        string
        :param title:      The title of the notification
        :type title:       string, ``None`` for no title or
                           :data:`~hiss.USE_REGISTERED` to use
                           title provided during registration
        :param text:       The text to display in the notification
        :type text:        string, ``None`` for no text or
                           :data:`~hiss.USE_REGISTERED` to use
                           text provided during registration
        :param icon:       URL of icon to display
        :type icon:        string, :class:`~hiss.Icon`, ``None`` for no
                           icon or :data:`~hiss.USE_REGISTERED` 
                           to use icon provided during registration
        :param sound:      Sound to play when showing notification
        :type sound:       string, ``None`` for no sound or
                           :data:`~hiss.USE_REGISTERED` 
                           to use sound provided during registration
        """
        
        if class_id != -1:
            if class_id not in self.notification_classes:
                raise ValueError('%d is not a known notification class id' % \
                                 str(class_id))
        elif name != '':
            for class_id, info in self.notification_classes.items():
                if info.name == name:
                    break
        else:
            raise ValueError('hiss.Notifier: Either a class id or name must be specified.')

        info = self.notification_classes[class_id]
            
        if title is USE_REGISTERED:
            title = info.title
            
        if text is USE_REGISTERED:
            text = info.text
            
        if icon is None:
            if info.icon is not None:
                icon = info.icon
            else:
                icon = self.icon
            
        if sound is None:
            if sound.icon is not None:
                sound = info.sound
            else:
                sound = self.sound
            
        n =  Notification(title, text, icon, sound, signature=self.signature)
        n.name = info.name
        n.class_id = class_id
        n.notifier = self
        return n
    
    def notify(self, notification, targets=None):
        """Send a notification to a specific targets or all targets.
        
        :param notification:   The notification to send
        :type notification:    :class:`hiss.Notification`
        :param targets:         The targets to send the notification to. If no
                               targets is specified then the notification will
                               be sent to all known targets.
        :type targets:          :class:`hiss.Target` or ``None``
        """
        
        if targets is None:
            handlers = self._handlers
        elif targets.handler is not None:
            handlers = [targets.handler]
            
        self._notifications[notification.uid] = None
        
        ds = []
        for handler in handlers.values():
            d = handler.notify(self, notification)
            ds.append(d)
        
        if len(ds) == 1:
            return ds[0]
        else:
            return ds

    def subscribe(self, signatures=[], targets=None):
        """Subscribe to notifications from a list of signatures.
        
        :param signatures: List of signatures to listen to events from. If an
                           empty list is specified then subscribe to events
                           from all applications.
        :type signatures:  List of strings or empty list.
        """
        
        for handler in self._handlers.values():
            handler.subscribe(self, signatures, targets)

    def unregister(self, targets=None):
        """Unregister this notifier with all targets
        
        :param targets: The targets to register with
                        If not specified or ``None`` then the notifier
                        will be registered with all known targets
        :type targets:  :class:`hiss.Target` or ``None``
        """
        
        for handler in self._handlers.values():
            handler.unregister(self, targets)

    def show(self, uid):
        """If ``uid`` is in the list of current notifications then show it."""
        
        if uid in self._notifications:
            for handler in self._handlers.values():
                handler.show(self, uid)
    
    def hide(self, uid):
        """If ``uid`` is in the list of current notifications then hide it."""
        
        if uid in self._notifications:
            for handler in self._handlers.values():
                handler.show(self, uid)
    
    def event_handler(self, event):
        """Event handler for callback events. Default handler does nothing.
        
        :param event: The event
        :type event:  :class:`hiss.NotificationEvent`
        """

    def _handler(self, event):
        # If event is for a notification closing
        if event.code >= 0 and event.code <= 2:
            if event.nid in self._notifications:
                del self._notifications[event.nid]
                
        self.event_handler(event)

    def _unique_id(self):
        return str(uuid.uuid4())
