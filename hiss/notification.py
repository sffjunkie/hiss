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

__all__ = ['Notification', 'NotificationPriority']

class NotificationPriority(object):
    """Notification display priority. Valid values are ``VeryLow``,
    ``Moderate``, ``Normal``, ``High`` or ``Emergency``.
    
    .. note::
    
        Not all targets can handle ``VeryLow`` or ``Emergency`` values and will
        be clamped to acceptable limits.  
    """
    
    VeryLow = -2
    Moderate = -1
    Normal = 0
    High = 1
    Emergency = 2


NotificationCommand = namedtuple('NotificationCommand', ['command', 'label'])


class Notification(object):
    def __init__(self, title=None, text=None,
                 icon=None, sound=None,
                 priority=NotificationPriority.Normal,
                 timeout=-1, signature=''):
        """Create a new notification
        
        :param title:      Notification title.
        :type title:       string or None for no title
        :param text:       The text to display below the title
        :type text:        string
        :param icon:       Icon to display
        :type icon:        string or None for no icon
        :param priority:   Notification display priority.
                           Default priority = ``NotificationPriority.Normal``
        :type priority:    :class:`~hiss.NotificationPriority`
        :param timeout:    The duration in seconds to display the notification.
        :type timeout:     integer
        :param signature:  MIME style application signature to use for this
                           notification.
                           
                           Notifications created by a Notifier
                           have this information filled in automatically.
        :type signature:   string
        """
        
        self.title = title
        self.text = text
        self.icon = icon
        self.sound = sound
        self.priority = priority
        self.timeout = timeout
        self.percentage = -1
        self.callback = None
        self.actions = []

        self.signature = signature
        self.uid = self._unique_id()
        self.class_id = ''
        self.notifier = None
        
    def __repr__(self):
        return '%s:%s' % (self.signature, self.uid)

    def title():
        doc = """The title of the displayed notification encoded as UTF-8."""

        def fget(self):
            return self._title

        def fset(self, value):
            if len(value) > 1024:
                raise ValueError('Maximum title length (1024) exceeded')

            self._title = value.encode('utf-8')

        return locals()

    title = property(**title())

    def text():
        doc = """The text displayed below the title encoded as UTF-8."""

        def fget(self):
            return self._text

        def fset(self, value):
            self._text = value.encode('utf-8')

        return locals()

    text = property(**text())
    
    def sticky():
        def fget(self):
            return (self.timeout == 0)
        
        def fset(self, value):
            if value:
                self.timeout = 0
            else:
                self.timeout = -1
                
        return locals()
    
    sticky = property(**sticky())
    
    def add_callback(self, command, label=''):
        """Add a callback for this notification.
        
        :param command: The command to execute.
        :type command:  string
        :param label:   Label to use. If not provided the target will add a
                        defaultlabel.
        :type label:    string
        
        .. note::
        
            Only 1 callback can be added. Calling this multiple times will
            overwrite the existing callback.
        """

        self.callback = NotificationCommand(command, label)
        
    def add_action(self, command, label):
        """Add an action to this notification.
        
        :param command: The command to execute
        :type command:  string
        :param label:   The label to display
        :type label:    string
        
        .. note::
        
            Unlike the :meth:`~hiss.Notification.add_callback` multiple actions
            can be added.
        """
        
        self.actions.append(NotificationCommand(command, label))

    def visible():
        doc = """Determine if the notification is currently being displayed."""

        def fget(self):
            raise NotImplementedError

        return locals()

    visible = property(**visible())

    has_callback = property(lambda self: self.callback is not None)

    def show(self):
        """Show the notification."""

        if self.notifier is not None:
            self.notifier.show(self.uid)

    def hide(self):
        """Hide the notification"""

        if self.notifier is not None:
            self.notifier.hide(self.uid)

    def update(self):
        """Update the title and text of an existing notification."""

        raise NotImplementedError

    def _unique_id(self):
        return str(uuid.uuid4())
