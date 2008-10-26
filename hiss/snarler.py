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
    [('Show', 0x01),
     ('Hide', 0x02),
     ('Update', 0x03),
     ('IsVisible', 0x04),
     ('GetVersion', 0x05),
     ('RegisterConfigWindow', 0x06),
     ('RevokeConfigWindow', 0x07),
     ('RegisterAlert', 0x08),
     ('RevokeAlert', 0x09),
     ('RegisterConfigWindow2', 0x0A),
     ('GetVersionEx', 0x0B),
     ('SetTimeout', 0x0C),
     ('ShowEx', 0x20)
    ])

SnarlEvent = Enum('SnarlEvent',
    [('Launched', 1), ('Quit', 2), ('AskAppletVer', 3), ('ShowAppUI', 4)])

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

        if not self._hwnd:
            raise NotifierError('Unable to create Snarl handler.')

    Name = property(lambda self: 'snarl')
    Ready = property(lambda self: self._hwnd != 0)
    Handle = property(lambda self: self._hwnd)

    def _get_version(self):
        """Get the current version of Snarl as a tuple (Major, Minor)"""
        if self._version is None:
            self._version = self._getVersionEx()
            if self._version is None:
                self._version = self._getVersion()

        return self._version

    Version = property(_get_version)

    def registerApp(self, app):
        self.registerConfig(app)

    def deregisterApp(self, app):
        self.deregisterConfig(app)

    def showNotification(self, msg):
        if msg.Sticky:
            timeout = 0
        else:
            timeout = msg.Timeout

        if msg.Sound != '':
            msg.ID = self._sendCommand(SnarlCommand.ShowEx, id=0,
                timeout=timeout,
                title=msg.Title, text=msg.Text,
                icon=msg.Icon, extra=msg.Sound)
        else:
            msg.ID = self._sendCommand(SnarlCommand.Show, id=0,
                timeout=timeout,
                title=msg.Title, text=msg.Text,
                icon=msg.Icon)

    def updateNotification(self, msg):
        if msg.ID != 0:
            self._sendCommand(SnarlCommand.Update, id=msg.ID,
                        title=msg.Title, text=msg.Text,
                        icon=msg.Icon)

    def setTimeout(self, msg):
        self._sendCommand(SnarlCommand.SetTimeout, id=msg.ID,
                    longdata=msg.Timeout)

    def hideNotification(self, msg):
        self._sendCommand(SnarlCommand.Hide, id=msg.ID)
        msg.ID = 0

    def notificationIsVisible(self, msg):
        return self._sendCommand(SnarlCommand.IsVisible, id=msg.ID) == -1

    def getAppPath(self):
        if self._app_path == '':
            hwnd_path = self._u32.FindWindowExA(self._hwnd, 0, 'static', 0)
            if hwnd_path != 0:
                app_path = ' '*1023
                result = self._u32.GetWindowTextA(hwnd_path, app_path, 1024)
                if result > 0:
                    self._app_path = app_path[:result]

        return self._app_path

    def getIconPath(self):
        if self._icon_path == '':
            app_path = self.getAppPath()
            if app_path != '':
                self._icon_path = os.path.join(app_path, 'etc\\icons\\')

        return self._icon_path

    def getGlobalMsg(self):
        if self._global_msg != 0:
            self._global_msg = self._u32.RegisterWindowNotificationA(Snarler.SNARL_GLOBAL_MSG)

        return self._global_msg

    def registerConfig(self, app, reply=0):
        if (self._version == (1, 6) or self._version[0] >= 2) and app.Icon != '':
            command = SnarlCommand.RegisterConfigWindow2
        else:
            command = SnarlCommand.RegisterConfigWindow

        return self._sendCommand(command, id=reply,
            longdata=app.Handle, title=app.Title, icon=app.Icon)

    def deregisterConfig(self, app):
        return self._sendCommand(SnarlCommand.RevokeConfigWindow,
            longdata=app.Handle)

    def registerNotification(self, app, name, enabled):
        return self._sendCommand(SnarlCommand.RegisterAlert,
            title=app, text=name)

    def deregisterNotification(self, app, name):
        pass

    def _getVersion(self):
        hr = self._sendCommand(SnarlCommand.GetVersion)
        if hr:
            ver = cast(hr, POINTER(c_byte))
            return (int(ver[0]), int(ver[1]))

        return None

    def _getVersionEx(self):
        ver = self._sendCommand(SnarlCommand.GetVersionEx)
        if ver == 0 or ver >= SnarlResult.NotImplemented:
            return None
        else:
            return Snarler.SNARL_VERSIONS[ver]

    def _sendCommand(self, command, id=0, timeout=0, longdata=0, title='', text='', icon='',
                     class_=None, extra=None, extra2=None, reserved1=None, reserved2=None):

        title = title.encode('utf-8')
        text = text.encode('utf-8')

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


