# Copyright 2008, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

# The Python Snarl library

import os
import os.path
import sys
import traceback

import snarler
import growler

from enum import *
from exception import *

__all__ = ['Message', 'Application', 'Sid']

MessagePriority = Enum('Priority',
    [('VeryLow', -2),
     ('Moderate', -1),
     ('Normal', 0),
     ('High', 1),
     ('Emergency', 2)
    ])

class Message(object):
    def __init__(self):
        self._id = 0
        self._title = ''
        self._text = ''
        self._icon = ''
        self._sound = ''
        self._timeout = 0
        self._priority = MessagePriority.Normal

        self._handler = None

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

        self._title = title

    Title = property(_get_title, _set_title)

    def _get_text(self):
        return self._text

    def _set_text(self, text):
        self._text = text

    Text = property(_get_text, _set_text)

    def _get_icon(self):
        return self._icon

    def _set_icon(self, icon):
        self._icon = icon

    Icon = property(_get_icon, _set_icon)

    def _get_sound(self):
        return self._sound

    def _set_sound(self, sound):
        self._sound = sound

    Sound = property(_get_sound, _set_sound)

    def _get_handler(self):
        return self._handler

    def _set_handler(self, handler):
        self._handler = handler

    Handler = property(_get_handler, _set_handler)

    def _get_timeout(self):
        return self._timeout

    def _set_timeout(self, timeout):
        self._timeout = timeout

        if self._handler is not None and self._handler != 0:
            self._handler.setTimeout(self)

    Timeout = property(_get_timeout, _set_timeout)

    def _get_priority(self):
        return self._priority

    def _set_priority(self, priority):
        self._priority = priority

    Priority = property(_get_priority, _set_priority)

    def Show(self, timeout=0):
        if self._handler is None:
            raise HandlerError('No handler set.')

        self._handler.showMessage(self)

    def Hide(self):
        if self._handler is None:
            raise HandlerError('No handler set.')

        self._handler.hideMessage(self)

    IsValid = property(lambda self: self._title != '' and self._text != '')

    def _get_is_visible(self):
        if self._handler is None:
            raise HandlerError('No handler set.')

        return self._handler.msgIsVisible(self)

    IsVisible = property(_get_is_visible)


class Application(object):
    def __init__(self, notifications=[]):
        self._handle = 0
        self._title = ''
        self._icon = ''
        self._notifications = notifications

    def _get_handle(self):
        return self._handle

    def _set_handle(self, handle):
        self._handle = handle

    Handle = property(_get_handle, _set_handle)

    def _get_title(self):
        return self._title

    def _set_title(self, title):
        self._title = title

    Title = property(_get_title, _set_title)

    def _get_icon(self):
        return self._icon

    def _set_icon(self, icon):
        self._icon = icon

    Icon = property(_get_icon, _set_icon)

    def RegisterAlerts(self, title, handler):
        if title not in self._alerts:
            handler.registerAlert(self._title, title)
            self._alerts.append(title)

    def RevokeAlerts(self, title, handler):
        if title in self._alerts:
            handler.revokeAlert(self._title, title)
            self._alerts.remove(title)


class Sid(object):
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

    def ShowMessage(self, msg, timeout=0):
        msg.Handler = self._handler
        msg.Timeout = timeout
        msg.Show()

    def HideMessage(self, msg):
        msg.Hide()

    def RegisterApp(self, app):
        self._handler.registerConfig(app)

    def RevokeApp(self, app):
        self._handler.revokeConfig(app)

    def ShowException(self, timeout=0):
        m = Message()
        i = sys.exc_info()

        if i != (None, None, None):
            m.Title = str(i[1])
            m.Text = traceback.format_exc()
            m.Icon = os.path.join(self.IconPath, 'critical.png')
            m.Timeout = timeout
            self.ShowMessage(m)

