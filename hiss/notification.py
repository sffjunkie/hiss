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

from collections import namedtuple

class priority(object):
    VeryLow = -2
    Moderate = -1
    Normal = 0
    High = 1
    Emergency = 2

NotificationInfo = namedtuple('NotificationInfo',['name', 'description', 'icon', 'enabled'])

class Notification(object):
    def __init__(self, name, title='', text='', enabled=False, icon_url=''):
        self.nid = self._unique_id()
        self.application = ''
        self.name = name
        self.description = ''
        self._title = title.encode('utf-8')
        self._text = text.encode('utf-8')
        self._sticky = False
        self._priority = priority.Normal
        self._icon = None

        self._nid_coalescing = 0
        self._callback_context = ''
        self._callback_context_type = ''
        self._callback_target = ''
        self._notifier = None

    def display_name():
        doc = """The display_name of the displayed notification."""

        def fget(self):
            return self._display_name

        def fset(self, value):
            self._display_name = value

        return locals()

    display_name = property(**display_name())

    def enabled():
        doc = """Whether the notification is enabled."""

        def fget(self):
            return self._enabled

        def fset(self, value):
            self._enabled = value

        return locals()

    enabled = property(**enabled())

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
    
    def icon():
        def fget(self):
            return self._icon
            
        def fset(self, value):
            self._icon = value

        return locals()

    icon = property(**icon())

    def sound():
        doc = """A sound to play when displaying the notification."""

        def fget(self):
            return self._sound

        def fset(self, value):
            self._sound = value

        return locals()

    sound = property(**sound())

    def timeout():
        doc = """Timeout before the notification is hidden."""

        def fget(self):
            return self._timeout

        def fset(self, value):
            self._timeout = int(value)

        return locals()

    timeout = property(**timeout())

    def priority():
        doc = """The priority of the notification."""
        def fget(self):
            return self._priority

        def fset(self, value):
            self._priority = value

        return locals()

    priority = property(**priority())

    def sticky():
        doc = """The 'stickiness' of the notification. A sticky message has an infinite timeout."""
        def fget(self):
            return self._sticky

        def fset(self, value):
            self._sticky = bool(value)

        return locals()

    sticky = property(**sticky())

    def is_visible():
        doc = """Determine if the notification is currently being displayed."""

        def fget(self):
            raise NotImplementedError

        return locals()

    is_visible = property(**is_visible())

    def to_notify_message():
        raise NotImplementedError

    def show(self):
        """Show the notification."""

        raise NotImplementedError

    def update(self):
        """Update the title and text of an existing notification."""

        raise NotImplementedError

    def hide(self):
        """Hide the notification"""

        raise NotImplementedError

    def _unique_id(self):
        return uuid.uuid3(uuid.NAMESPACE_URL, 'http://www.sffjunkie.co.uk/python-hiss.html')
        

