# Copyright 2008, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

# Part of 'hiss' the Python notification library

import os
import os.path
import sys
import types
import traceback

import snarler
import growler
import expeller

from enum import *
from exception import *

__all__ = ['priority', 'Notification', 'Application', 'getNotifier', 'setNotifier']

priority = Enum('Notification priority',
    [('VeryLow', -2),
     ('Moderate', -1),
     ('Normal', 0),
     ('High', 1),
     ('Emergency', 2)
    ])

class Notification(object):
    def __init__(self, title='', text=''):
        self._nid = 0
        self._title = title.encode('utf-8')
        self._text = text.encode('utf-8')
        self._icon = ''
        self._sound = ''
        self._timeout = 0
        self._sticky = False
        self._priority = priority.Normal

        global _notifier
        self._notifier = _notifier

    def _id():
        def fget(self):
            return self._nid

        def fset(self, value):
            self._nid = value

        return locals()

    _id = property(**_id())

    def title():
        doc = """The title of the displayed notification."""

        def fget(self):
            return self._title

        def fset(self, value):
            if len(value) > 1024:
                raise ValueError('Maximum title length (1024) exceeded')

            self._title = value.encode('utf-8')

        return locals()

    title = property(**title())

    def text():
        doc = """The text displayed below the title."""

        def fget(self):
            return self._text

        def fset(self, value):
            self._text = value.encode('utf-8')

        return locals()

    text = property(**text())

    def icon():
        doc = """The filename of the icon to display."""

        def fget(self):
            return self._icon

        def fset(self, value):
            icon_path = self._notifier.icon_path
            if icon_path != '' and not value.startswith(icon_path):
                icon = os.path.join(icon_path, value)

            self._icon = icon

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
        """The 'stickiness' of the notification. A sticky message has an infinite timeout."""
        def fget(self):
            return self._sticky

        def fset(self, value):
            self._sticky = bool(value)

        return locals()

    sticky = property(**sticky())

    def is_visible():
        doc = """Determine if the notification is currently being displayed."""

        def fget(self):
            return self._notifier.notification_is_visible(self)

        return locals()

    is_visible = property(**is_visible())

    def show(self):
        """Show the notification."""

        if self._notifier is None:
            setNotifier()

        return self._notifier.show_notification(self)

    def update(self):
        """Update the title and text of an existing notification."""

        if self._notifier is None:
            setNotifier()

        return self._notifier.update_notification(self)

    def hide(self):
        """Hide the notification"""

        if self._notifier is None:
            setNotifier()

        return self._notifier.hide_notification(self)


class Application(object):
    def __init__(self, title='', notifications=[]):
        self._handle = 0
        self._title = title.encode('utf-8')
        self._icon = ''
        self._icon_path = ''
        self._notifier = _notifier

        self._notifications = self.Notifications(notifications)

    class Notifications(object):
        def __init__(self, items):
            self._items = []

            for item in items:
                self.append(item)

        def __setitem__(self, notification, enabled):
            for item in self._items:
                if item[0] == notification:
                    item[1] = enabled
                    return

            self._items.append((notification, enabled))

        def __getitem__(self, notification):
            for name, enabled in self._items:
                if name == notification:
                    return enabled

            raise KeyError('Unable to find notification')

        def iteritems():
            return self._items.iteritems()

        def append(self, item):
            if type(item) == types.TupleType:
                name = item[0].encode('utf-8')
                enabled = bool(item[1])
            else:
                name = item.encode('utf-8')
                enabled = True

            self._items.append((name, enabled))

        def count(self):
            return len(self._items)

        def enabled_count(self):
            count = 0
            for name, enabled in self._items:
                if enabled:
                    count += 1

            return count

    notifications = property(lambda self: self._notifications)

    def handle():
        def fget(self):
            return self._handle

        def fset(self, handle):
            self._handle = handle

        return locals()

    handle = property(**handle())

    def title():
        def fget(self):
            return self._title

        def fset(self, title):
            self._title = title.encode('utf-8')

        return locals()

    title = property(**title())

    def icon_path():
        def fget(self):
            if self._icon_path == '':
                self._icon_path = self._notifier.iconPath

            return self._icon_path

        def fset(self, icon_path):
            self._icon_path = icon_path

        return locals()

    icon_path = property(**icon_path())

    def icon():
        def fget(self):
            return self._icon

        def fset(self, icon):
            if not self._icon.startswith(self._icon_path):
                self._icon = os.path.join(self._icon_path, icon)

            self._icon = icon

        return locals()

    icon = property(**icon())

    def register(self):
        self._notifier.register_app(self)

    def deregister(self):
        self._notifier.deregister_app(self)


class Notifier(object):
    def __init__(self, backend=None):
        if backend is None:
            if os.name == 'osx':
                backend = 'growl'
            else:
                backend = 'snarl'

        if backend == 'snarl':
            self._backend = snarler.Snarler()
        elif backend == 'growl':
            self._backend = growler.Growler()
        elif backend == 'expel':
            self._backend = expeller.Expeller()
        else:
            raise ValueError('Unknown backend %s specified' % backend)

        self._backend_name = backend

    backend = property(lambda self: self._backend)
    backend_name = property(lambda self: self._backend.name)
    backend_version = property(lambda self: self._backend.Version)
    backend_path = property(lambda self: self._backend.get_app_path())
    icon_path = property(lambda self: self._backend.get_icon_path())

    def show_notification(self, notification):
        return self._backend.show_notification(notification)

    def update_notification(self, notification):
        return self._backend.update_notification(notification)

    def hide_notification(self, notification):
        return self._backend.hide_notification(notification)

    def register_app(self, app):
        return self._backend.register_app(app)

    def deregister_app(self, app):
        return self._backend.deregister_app(app)

    def show_exception(self, timeout=10):
        m = Notification()
        i = sys.exc_info().copy()

        if i != (None, None, None):
            m.title = str(i[1])
            m.text = traceback.format_exc()
            m.icon = os.path.join(self.iconPath, 'critical.png')
            m.timeout = timeout
            self.show_notification(m)

global _notifier
_notifier = Notifier()

def getNotifier():
    global _notifier
    return _notifier

def setNotifier(name=None):
    global _notifier
    if name is not None and _notifier.Handler.Name != name:
        del _notifier
        _notifier = Notifier(name)

