# Copyright 2008, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

# The Python notification library

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

__all__ = ['Priority', 'Notification', 'Application']

Priority = Enum('Notification Priority',
    [('VeryLow', -2),
     ('Moderate', -1),
     ('Normal', 0),
     ('High', 1),
     ('Emergency', 2)
    ])

class Notification(object):
    def __init__(self, title='', text=''):
        self._id = 0
        self._title = title.encode('utf-8')
        self._text = text.encode('utf-8')
        self._icon = ''
        self._sound = ''
        self._timeout = 0
        self._sticky = False
        self._priority = Priority.Normal
        self._notifier = _notifier

    def _get_id(self):
        return self._id

    def _set_id(self, id):
        self._id = id

    ID = property(_get_id, _set_id)

    def _get_title(self):
        return self._title

    def _set_title(self, title):
        if len(title) > 1024:
            raise ValueError('Maximum title length (1024) exceeded')

        self._title = title.encode('utf-8')

    Title = property(_get_title, _set_title)

    def _get_text(self):
        return self._text

    def _set_text(self, text):
        self._text = text.encode('utf-8')

    Text = property(_get_text, _set_text)

    def _get_icon(self):
        return self._icon

    def _set_icon(self, icon):
        icon_path = self._notifier.IconPath
        if icon_path != '' and not icon.startswith(icon_path):
            icon = os.path.join(icon_path, icon)

        self._icon = icon

    Icon = property(_get_icon, _set_icon)

    def _get_sound(self):
        return self._sound

    def _set_sound(self, sound):
        self._sound = sound

    Sound = property(_get_sound, _set_sound)

    def _get_timeout(self):
        return self._timeout

    def _set_timeout(self, timeout):
        self._timeout = int(timeout)

    Timeout = property(_get_timeout, _set_timeout)

    def _get_priority(self):
        return self._priority

    def _set_priority(self, priority):
        self._priority = priority

    Priority = property(_get_priority, _set_priority)

    def _get_sticky(self):
        return self._sticky

    def _set_sticky(self, sticky):
        self._sticky = bool(sticky)

    Sticky = property(_get_sticky, _set_sticky)

    def Show(self):
        if self._notifier is None:
            raise NotifierError('No notifier available.')

        return self._notifier.showNotification(self)

    def Update(self):
        if self._notifier is None:
            raise NotifierError('No notifier available.')

        return self._notifier.updateNotification(self)

    def Hide(self):
        if self._notifier is None:
            raise NotifierError('No notifier available.')

        return self._notifier.hideNotification(self)

    IsValid = property(lambda self: self._title != '' and self._text != '')

    def _get_is_visible(self):
        if self._notifier is None:
            raise NotifierError('No notifier available.')

        return self._notifier.notificationIsVisible(self)

    IsVisible = property(_get_is_visible)


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
            if type(item) == types.TupleType:
                name = item[0].encode('utf-8')
                enabled = item[1]
            else:
                name = item.encode('utf-8')
                enabled = False

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

    Notifications = property(lambda self: self._notifications)

    def register(self):
        self._notifier.registerApp(self)
        for name, enabled in self._notifications.iteritems():
            self._notifier.registerNotification(self._title, name, enabled)

    def deregister(self):
        self._notifier.deregisterApp(self)


class Notifier(object):
    def __init__(self, handler=None):
        if handler is None:
            if os.name == 'osx':
                handler = 'growl'
            else:
                handler = 'snarl'

        if handler == 'snarl':
            self._handler = snarler.Snarler()
        elif handler == 'growl':
            self._handler = growler.Growler()
        else:
            raise ValueError('Unknown handler %s specified' % handler)

        self._handler_name = handler

    Handler = property(lambda self: self._handler)
    HandlerName = property(lambda self: self._handler.Name)
    HandlerVersion = property(lambda self: self._handler.Version)
    HandlerPath = property(lambda self: self._handler.getAppPath())
    IconPath = property(lambda self: self._handler.getIconPath())

    def showNotification(self, msg):
        msg.Handler = self._handler
        self._handler.showNotification(msg)

    def updateNotification(self, msg):
        self._handler.updateNotification(msg)

    def hideNotification(self, msg):
        self._handler.hideNotification(msg)

    def registerApp(self, app):
        self._handler.registerApp(app)

    def deregisterApp(self, app):
        self._handler.deregisterApp(app)

    def registerNotification(self, app, name):
        pass

    def showException(self, timeout=10):
        m = Notification()
        i = sys.exc_info()

        if i != (None, None, None):
            m.Title = str(i[1])
            m.Text = traceback.format_exc()
            m.Icon = os.path.join(self.IconPath, 'critical.png')
            m.Timeout = timeout
            self.showNotification(m)

global _notifier
_notifier = Notifier()

def getNotifier():
    return _notifier

