# Copyright 2013-2014, Simon Kennedy, code@sffjunkie.co.uk
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

# Part of 'hiss' the asynchronous notification library

import uuid
from enum import Enum
from collections import namedtuple

from hiss.exception import HissError

__all__ = ['Notification', 'NotificationPriority']

class NotificationPriority(Enum):
    """Notification display priority. Valid values are ``very_low``,
    ``moderate``, ``normal``, ``high`` or ``emergency``.

    .. note::

        Not all targets can handle ``very_low`` or ``emergency`` values and will
        be clamped to acceptable limits.  
    """

    very_low = -2
    moderate = -1
    normal = 0
    high = 1
    emergency = 2


NotificationCommand = namedtuple('NotificationCommand', ['command', 'label'])


class Notification():
    """Manages the data necessary to display a notification

    :param title:      Notification title.
    :type title:       string or None for no title
    :param text:       The text to display below the title
    :type text:        string or None for no text
    :param icon:       Icon to display
    :type icon:        string or None for no icon
    :param priority:   Notification display priority.
                       Default priority = ``NotificationPriority.normal``
    :type priority:    :class:`~hiss.NotificationPriority`
    :param timeout:    The duration in seconds to display the notification. A value of 0 for some
                       targets means the notification will be displayed until acted on by the user.
    :type timeout:     integer
    :param uid:        UUID for this notification. Notifications created by a :class:`Notifier`
                       have this information filled in automatically.
    :type uid:         string

    Even though *title*, *text* and *icon* are optional at least one of these must be specified or
    a :class:`~hiss.exception.HissError` will be raised.
    """

    def __init__(self, title=None, text=None,
                 icon=None, sound=None,
                 priority=NotificationPriority.normal,
                 timeout=-1, uid=None):

        if title is None and text is None and icon is None:
            raise HissError('One of title, text or icon must be used.') 

        self._title = None
        self.title = title
        self.text = text
        self.icon = icon
        self.sound = sound
        self.priority = priority
        self.timeout = timeout
        self.percentage = -1
        self.callback = None
        self.actions = []

        self.uid = self._unique_id()
        self.class_id = ''
        self.notifier = None

    def __repr__(self):
        return self.uid

    @property
    def title(self):
        """The title of the displayed notification."""

        return self._title

    @title.setter
    def title(self, value):
        if len(value.encode('UTF-8')) > 1024:
            raise ValueError('Maximum title length (1024) exceeded')

        self._title = value

    @property
    def sticky(self):
        return (self.timeout == 0)

    @sticky.setter        
    def sticky(self, value):
        if isinstance(value, int):
            self.timeout = value
        elif value:
            self.timeout = 0
        else:
            self.timeout = -1

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

    @property
    def visible(self):
        """Determine if the notification is currently being displayed."""
        raise NotImplementedError

    has_callback = property(lambda self: self.callback is not None)

    def show(self):
        """Show the notification."""

        if self.notifier is not None:
            self.notifier.show(self.uid)
        else:
            raise HissError(('Unable to show notification. '
                             'Notification has not been sent to a notifier'))

    def hide(self):
        """Hide the notification"""

        if self.notifier is not None:
            self.notifier.hide(self.uid)
        else:
            raise HissError(('Unable to hide notification. '
                             'Notification has not been sent to a notifier'))

    def update(self):
        """Update the title and text of an existing notification."""

        raise NotImplementedError

    def _unique_id(self):
        return str(uuid.uuid4())
