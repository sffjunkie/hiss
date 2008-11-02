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

__all__ = ['Priority', 'Notification', 'Application', 'getNotifier', 'setNotifier']

Priority = Enum('Notification Priority',
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
        self._priority = Priority.Normal

        global _notifier
        self._notifier = _notifier

    def _id():
        def fget(self):
            return self._nid

        def fset(self, nid):
            self._nid = nid

        return locals()

    _id = property(**_id())

    def Title():
        doc = """The title of the displayed notification."""

        def fget(self):
            return self._title

        def fset(self, title):
            if len(title) > 1024:
                raise ValueError('Maximum title length (1024) exceeded')

            self._title = title.encode('utf-8')

        return locals()

    Title = property(**Title())

    def Text():
        def fget(self):
            return self._text

        def fset(self, text):
            self._text = text.encode('utf-8')

        return locals()

    Text = property(**Text())

    def Icon():
        def fget(self):
            return self._icon

        def fset(self, icon):
            icon_path = self._notifier.IconPath
            if icon_path != '' and not icon.startswith(icon_path):
                icon = os.path.join(icon_path, icon)

            self._icon = icon

        return locals()

    Icon = property(**Icon())

    def Sound():
        def fget(self):
            return self._sound

        def fset(self, sound):
            self._sound = sound

        return locals()

    Sound = property(**Sound())

    def Timeout():
        def fget(self):
            return self._timeout

        def fset(self, timeout):
            self._timeout = int(timeout)

        return locals()

    Timeout = property(**Timeout())

    def Priority():
        def fget(self):
            return self._priority

        def fset(self, priority):
            self._priority = priority

        return locals()

    Priority = property(**Priority())

    def Sticky():
        def fget(self):
            return self._sticky

        def fset(self, sticky):
            self._sticky = bool(sticky)

        return locals()

    Sticky = property(**Sticky())

    IsValid = property(lambda self: self._title != '' and self._text != '')

    def IsVisible():
        def fget(self):
            return self._notifier.notification_is_visible(self)

        return locals()

    IsVisible = property(**IsVisible())

    def Show(self):
        if self._notifier is None:
            setNotifier()

        return self._notifier.show_notification(self)

    def Update(self):
        if self._notifier is None:
            setNotifier()

        return self._notifier.update_notification(self)

    def Hide(self):
        if self._notifier is None:
            setNotifier()

        return self._notifier.hide_notification(self)


class Application(object):
    def __init__(self, title='', notifications=[]):
        self._handle = 0
        self._title = title.encode('utf-8')
        self._icon = ''
        self._icon_path = ''
        self._count = 0
        self._enabled_count = 0
        self._notifier = _notifier

        self._notifications = {}
        if len(notifications) != 0:
            self._set_notifications(notifications)

    def _set_notifications(self, notifications):
        for item in notifications:
            self.add_notification(item)

    def add_notification(self, notification):
        if type(notification) == types.TupleType:
            name = notification[0].encode('utf-8')
            enabled = notification[1]
        else:
            name = notification.encode('utf-8')
            enabled = True

        if name not in self._notifications:
            self._notifications[name] = enabled

            if enabled:
                self._enabled_count += 1

            self._count += 1

    Notifications = property(lambda self: self._notifications)
    NotificationCount = property(lambda self: self._count)
    NotificationEnabledCount = property(lambda self: self._enabled_count)

    def _get_handle(self):
        return self._handle

    def _set_handle(self, handle):
        self._handle = handle

    Handle = property(_get_handle, _set_handle)

    def _get_title(self):
        return self._title

    def _set_title(self, title):
        self._title = title.encode('utf-8')

    Title = property(_get_title, _set_title)

    def _get_icon_path(self):
        if self._icon_path == '':
            self._icon_path = self._notifier.IconPath

        return self._icon_path

    def _set_icon_path(self, icon_path):
        self._icon_path = icon_path

    IconPath = property(_get_icon_path, _set_icon_path)

    def _get_icon(self):
        return self._icon

    def _set_icon(self, icon):
        if not self._icon.startswith(self._icon_path):
            self._icon = os.path.join(self._icon_path, icon)

        self._icon = icon

    Icon = property(_get_icon, _set_icon)

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

    BackEnd = property(lambda self: self._backend)
    BackEndName = property(lambda self: self._backend.Name)
    BackEndVersion = property(lambda self: self._backend.Version)
    BackEndPath = property(lambda self: self._backend.get_app_path())
    IconPath = property(lambda self: self._backend.get_icon_path())

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
            m.Title = str(i[1])
            m.Text = traceback.format_exc()
            m.Icon = os.path.join(self.IconPath, 'critical.png')
            m.Timeout = timeout
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

