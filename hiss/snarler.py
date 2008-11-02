# Copyright 2008, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

# Part of 'hiss' the Python notification library

import os.path
import types
import struct, array
from ctypes import cast, POINTER, c_byte, windll

from enum import *
from exception import *

WM_COPYDATA = 74

SnarlCommand = Enum('SnarlCommand',
    [('show', 0x01),
     ('hide', 0x02),
     ('update', 0x03),
     ('is_visible', 0x04),
     ('GetVersion', 0x05),
     ('RegisterConfigWindow', 0x06),
     ('RevokeConfigWindow', 0x07),
     ('RegisterAlert', 0x08),
     ('RevokeAlert', 0x09),
     ('RegisterConfigWindow2', 0x0A),
     ('GetVersionEx', 0x0B),
     ('Settimeout', 0x0C),
     ('showEx', 0x20)
    ])

SnarlEvent = Enum('SnarlEvent',
    [('Launched', 1), ('Quit', 2), ('AskAppletVer', 3), ('showAppUI', 4)])

SnarlNotification = Enum('SnarlNotification',
    [('Clicked', 32),
     ('TimedOut', 33),
     ('Ack', 34),
     ('Cancelled', 32)
    ], False)

SnarlResult = Enum('SnarlResult',
    [('OK', 0x00000000), ('NotImplemented', 0x80000001),
     ('OutOfMemory', 0x80000002), ('SnarlResult.InvalidArgs', 0x80000003),
     ('NoInterface', 0x80000004), ('BadPointer', 0x80000005),
     ('BadHandle', 0x80000006), ('Aborted', 0x80000007),
     ('Failed', 0x80000008), ('AccessDenied', 0x80000009),
     ('TimedOut', 0x8000000A), ('NotFound', 0x8000000B),
     ('AlreadyExists', 0x8000000C)
    ])

class Snarler(object):
    SNARL_VERSIONS = {
        30: (0, 0),
        31: (0, 1),
        32: (0, 3),
        33: (0, 7),
        34: (1, 0),
        35: (1, 1),
        36: (1, 5),
        37: (1, 6),
        38: (2, 0)
    }

    SNARL_GLOBAL_MSG = 'SnarlGlobalEvent'

    SNARL_STRUCT = 'ILLL1024s1024s1024s'
    SNARL_STRUCT_EX = SNARL_STRUCT + '1024s1024s1024sLL'

    def __init__(self):
        self._u32 = windll.user32
        self._hwnd = self._u32.FindWindowA(None, 'Snarl')
        self._global_msg = 0
        self._version = None
        self._app_path = ''
        self._icon_path = ''
        self._application = None

        if not self._hwnd:
            raise NotifierError('Unable to create Snarl handler.')

    name = property(lambda self: 'snarl')
    ready = property(lambda self: self._hwnd != 0)
    handle = property(lambda self: self._hwnd)

    def Version():
        doc = """The current version of Snarl as a tuple (Major, Minor)"""
        def fget(self):
            if self._version is None:
                self._version = self._get_version_ex()
                if self._version is None:
                    self._version = self._get_version()

            return self._version

        return locals()

    Version = property(**Version())

    def register_app(self, app):
        """Register an application and its notifications"""

        self._application = app

        if (self.Version == (1, 6) or self.Version[0] >= 2) and app.icon != '':
            command = SnarlCommand.RegisterConfigWindow2
        else:
            command = SnarlCommand.RegisterConfigWindow

        ret = self._send_command(command, id=reply,
            longdata=app.Handle, title=app.title, icon=app.icon)

        if ret != SnarlResult.OK:
            return ret

        for name, enabled in app.notifications.iteritems():
            ret = self.register_notification(self._title, name, enabled)

            if ret != SnarlResult.OK:
                return ret

        return SnarlResult.OK

    def deregister_app(self):
        """De-register an application and its notifications"""

        ret = self._send_command(SnarlCommand.RevokeConfigWindow,
            longdata=self._application.Handle)

        self._application = None

        return ret

    def show_notification(self, notification):
        if notification.sticky:
            timeout = 0
        else:
            timeout = notification.timeout

        if self._application is None:
            handle = 0
        else:
            handle = self._application.Handle

        if notification.sound != '':
            notification._id = self._send_command(SnarlCommand.showEx, id=0,
                timeout=timeout,
                longdata=handle,
                title=notification.title, text=notification.text,
                icon=notification.icon, extra=notification.sound)
        else:
            notification._id = self._send_command(SnarlCommand.show, id=0,
                timeout=timeout,
                longdata=handle,
                title=notification.title, text=notification.text,
                icon=notification.icon)

        return notification._id

    def update_notification(self, notification):
        if notification._id != 0:
            ret = self._send_command(SnarlCommand.update, id=notification._id,
                        title=notification.title, text=notification.text,
                        icon=notification.icon)

            return ret
        else:
            return SnarlResult.NotFound

    def set_timeout(self, notification):
        self._send_command(SnarlCommand.Settimeout, id=notification._id,
                    longdata=notification.timeout)

    def hide_notification(self, notification):
        ret = self._send_command(SnarlCommand.hide, id=notification._id)
        notification._id = 0

        return ret

    def notification_is_visible(self, notification):
        return self._send_command(SnarlCommand.is_visible, id=notification._id) == -1

    def get_app_path(self):
        if self._app_path == '':
            hwnd_path = self._u32.FindWindowExA(self._hwnd, 0, 'static', 0)
            if hwnd_path != 0:
                app_path = ' '*1024
                result = self._u32.GetWindowTextA(hwnd_path, app_path, 1023)
                if result > 0:
                    self._app_path = app_path[:result]

        return self._app_path

    def get_icon_path(self):
        if self._icon_path == '':
            app_path = self.get_app_path()
            if app_path != '':
                self._icon_path = os.path.join(app_path, 'etc\\icons\\')

        return self._icon_path

    def get_global_msg(self):
        if self._global_msg != 0:
            self._global_msg = self._u32.RegisterWindowNotificationA(Snarler.SNARL_GLOBAL_MSG)

        return self._global_msg

    def register_notification(self, app_title, name, enabled):
        return self._send_command(SnarlCommand.RegisterAlert,
            title=app_title, text=name)

    def deregister_notification(self, app, name):
        pass

    def _get_version(self):
        hr = self._send_command(SnarlCommand.GetVersion)
        if hr:
            ver = cast(hr, POINTER(c_byte))
            return (int(ver[0]), int(ver[1]))

        return None

    def _get_version_ex(self):
        ver = self._send_command(SnarlCommand.GetVersionEx)
        if ver == 0 or ver >= SnarlResult.NotImplemented:
            return None
        else:
            return Snarler.SNARL_VERSIONS[ver]

    def _send_command(self, command, id=0, timeout=0, longdata=0, title='', text='', icon='',
                     class_=None, extra=None, extra2=None, reserved1=None, reserved2=None):

        if class_ is None and extra is None and extra2 is None and reserved1 is None and reserved2 is None:
            command = struct.pack(Snarler.SNARL_STRUCT,
                                  command, id,
                                  timeout, longdata,
                                  title, text, icon)
        else:
            if class_ is None:
                class_ = 0
            if reserved1 is None:
                reserved1 = 0
            if reserved2 is None:
                reserved2 = 0
            if extra is None:
                extra = ''
            if extra2 is None:
                extra2 = ''

            command = struct.pack(SNARL_STRUCT_EX,
                                  command, id,
                                  timeout, longdata,
                                  title, text, icon,
                                  array.array('B', class_).tostring(),
                                  array.array('B', extra).tostring(),
                                  array.array('B', extra2).tostring(),
                                  reserved1,
                                  reserved2)

        command_pack = array.array('B', command)
        command_info = command_pack.buffer_info()

        cd = struct.pack('LLP', 2, command_info[1], command_info[0])
        cd_pack = array.array('B', cd)
        cd_info = cd_pack.buffer_info()

        self._hwnd = self._u32.FindWindowA(None, 'Snarl')
        return self._u32.SendMessageA(self._hwnd, WM_COPYDATA, 0, cd_info[0])


