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

import uuid
from collections import namedtuple

from twisted.internet import defer

from hiss.notification import Notification
from hiss.handler.snp import SNP_SCHEME, SNP
from hiss.handler.gntp import GNTP_SCHEME, GNTP

__all__ = ['Notifier']

SCHEME_HANDLERS = {
    SNP_SCHEME: SNP,
    GNTP_SCHEME: GNTP,
}


NotificationInfo = namedtuple('NotificationInfo', ['name', 'title', 'text',
                                                   'icon', 'sound', 'enabled'])


class Notifier(object):
    def __init__(self, signature, name, icon=None, uid=None):
        """Create a new notifier
        
        :param signature: The MIME style application signature for this notifier
                          of the form :samp:`application/x-vnd.{vendor}.{app}`
        :type signature:  string
        :param name:      The name of this notifier
        :type name:       string
        :param icon:      Notifier icon. Used when registering the notifier and
                          the default icon for notifications
                          (unless overridden.)
        :param uid:       Unique id to use for this notifier. If not specified 
                          one will be provided for you. This will be used as the
                          password for security enabled communications.
        """
        
        self.signature = signature
        self.name = name
        self.icon = icon
        
        if uid is None:
            self.uid = self._unique_id()
        else:
            self.uid = uid
            
        self.notification_classes = {}
        
        self._handlers = {}
        self._notifications = {}

    def register_notification(self, name, default_title='', default_text=None,
                              default_icon=None, default_sound=None,
                              enabled=True):
        """Add a notification class.
        
        :param name:          Notification class name
        :type name:           string
        :param default_title: Default notification title
        :type default_title:  string
        :param default_text:  Default notification text
        :type default_text:   string
        :param default_icon:  Default notification icon
        :type default_icon:   string
        :param default_sound: Default notification sound
        :type default_sound:  string
        :param enabled:       Whether the notification is enabled or not
        :type enabled:        boolean
        :returns:             The class id of the newly added notification
        :rtype:               integer
        """
        
        class_id = len(self.notification_classes) + 1
        self.notification_classes[class_id] = \
            NotificationInfo(name, default_title, default_text, default_icon,
                             default_sound, enabled)
            
        return class_id
 
    def register_target(self, target):
        """Add a target to the list of known targets
        
        :param target: The Target to add.
        :type target:  :class:`hiss.Target`
        """
        
        if target.scheme in self._handlers:
            handler = self._handlers[target.scheme]
        else:
            handler = SCHEME_HANDLERS[target.scheme](self._event_handler)
            self._handlers[target.scheme] = handler
        
        target.handler = handler
        return handler.connect(target)
 
    def unregister_target(self, target):
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
                        If not specified or None then the notifier will be
                        registered with all known targets
        :type targets:  :class:`hiss.Target` or None
        """
        
        for handler in self._handlers.values():
            handler.register(self, targets)

    def create_notification(self, class_id=-1, name='',
                            title=None, text=None,
                            icon=None, sound=None):
        """Create a notification that is ready to send.
        
        Either ``class_id`` or ``name`` can be provided. If ``class_id`` is
        provided it will be used instead of ``name`` to
        lookup the defaults registered in :meth:`.register_notification`
        
        :param class_id:   The notification class id
        :type class_id:    integer
        :param name:       The notification name
        :type name:        string
        :param title:      The title of the notification
        :type title:       string or None to use registered title
        :param text:       The text to display in the notification
        :type text:        string or None to use registered text
        :param icon:       URL of icon to display
        :type icon:        string, Icon or None to use registered icon
        :param sound:      Sound to play when showing notification
        :type sound:       string or None to use registered sound
        """
        
        if class_id != -1:
            if class_id not in self.notification_classes:
                raise ValueError('%d is not a known notification class id' % str(class_id))
            info = self.notification_classes[class_id]
        elif name != '':
            for class_id, info in self.notification_classes.items():
                if info.name == name:
                    break
        else:
            raise ValueError('Either a class id or a name must be specified.')
            
        if title is None:
            title = info.title
            
        if text is None:
            text = info.text
            
        if icon is None:
            icon = info.icon
            
        if sound is None:
            sound = info.sound
            
        n =  Notification(title, text, icon, sound, self.signature)
        n.class_id = class_id
        n.notifier = self
        return n
    
    def notify(self, notification, target=None):
        """Send a notification to a specific target or all targets.
        
        :param notification:   The notification to send
        :type notification:    :class:`hiss.Notification`
        :param target:         The target to send the notification to. If no
                               target is specified then the notification will
                               be sent to all known targets.
        :type target:          :class:`hiss.Target` or None
        """
        
        if target is None:
            handlers = self._handlers
        elif target.handler is not None:
            handlers = [target.handler]
            
        self._notifications[notification.uid] = None
            
        for handler in handlers.values():
            handler.notify(self, notification)

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
                        If not specified or None then the notifier will be
                        registered with all known targets
        :type targets:  :class:`hiss.Target` or None
        """
        
        for handler in self._handlers.values():
            handler.unregister(self, targets)

    def show(self, uid):
        if uid in self._notifications:
            for handler in self._handlers.values():
                handler.show(uid)
    
    def hide(self, uid):
        pass
    
    def event_handler(self, event):
        pass

    def _event_handler(self, event):
        if event.code in [303, 304, 307,308]:
            if event.nid in self._notifications:
                del self._notifications[event.nid]
                
        #self.event_handler(event)

    def _unique_id(self):
        return str(uuid.uuid4())
