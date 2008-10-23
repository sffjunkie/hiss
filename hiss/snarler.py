# Copyright 2008, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

import os.path
import types
import struct, array
from ctypes import cast, POINTER, c_byte, windll

from exception import *

WM_COPYDATA = 74

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

    SNARL_CMD_SHOW = 0x01
    SNARL_CMD_HIDE = 0x02
    SNARL_CMD_UPDATE = 0x03
    SNARL_CMD_IS_VISIBLE = 0x04
    SNARL_CMD_GET_VERSION = 0x05
    SNARL_CMD_REGISTER_CONFIG_WINDOW = 0x06
    SNARL_CMD_REVOKE_CONFIG_WINDOW = 0x07
    SNARL_CMD_REGISTER_ALERT = 0x08
    SNARL_CMD_REVOKE_ALERT = 0x09
    SNARL_CMD_REGISTER_CONFIG_WINDOW_2 = 0x0A
    SNARL_CMD_GET_VERSION_EX = 0x0B
    SNARL_CMD_SET_TIMEOUT = 0x0C
    SNARL_CMD_SHOW_EX = 0x20

    SNARL_EVENT_LAUNCHED = 1
    SNARL_EVENT_QUIT = 2
    SNARL_EVENT_ASK_APPLET_VER = 3 # introduced in V36
    SNARL_EVENT_SHOW_APP_UI = 4 # introduced in V37

    SNARL_NOTIFICATION_CLICKED = 32
    SNARL_NOTIFICATION_TIMED_OUT = 33
    SNARL_NOTIFICATION_ACK = 34
    SNARL_NOTIFICATION_CANCELLED = SNARL_NOTIFICATION_CLICKED # introduced in V37

    SNARL_GLOBAL_MSG = 'SnarlGlobalEvent'

    M_OK = 0x00000000
    M_NOT_IMPLEMENTED = 0x80000001
    M_OUT_OF_MEMORY = 0x80000002
    M_INVALID_ARGS = 0x80000003
    M_NO_INTERFACE = 0x80000004
    M_BAD_POINTER = 0x80000005
    M_BAD_HANDLE = 0x80000006
    M_ABORTED = 0x80000007
    M_FAILED = 0x80000008
    M_ACCESS_DENIED = 0x80000009
    M_TIMED_OUT = 0x8000000A
    M_NOT_FOUND = 0x8000000B
    M_ALREADY_EXISTS = 0x8000000C

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
            raise HandlerError('Unable to create Snarl handler.')

    Name = property(lambda self: 'Snarler')
    Ready = property(lambda self: self._hwnd != 0)
    Handle = property(lambda self: self._hwnd)

    def _get_version(self):
        """Get the current version of Snarl as a tuple (Major, Minor)"""
        if self._version is not None:
            self._version = self._getVersionEx()
            if self._version is None:
                self._version = self._getVersion()

        return self._version

    Version = property(_get_version)

    def showMessage(self, msg, new=False):
        """Show the message.

        If new is True the message is not updated but shown again i.e.
        you will have more than one version of the message
        """
        if msg.ID != 0 and not new:
            self.updateMessage(msg)
        else:
            if msg.Sound != '':
                msg.ID = self._sendCommand(Snarler.SNARL_CMD_SHOW_EX, id=0,
                    timeout=msg.Timeout,
                    title=msg.Title, text=msg.Text,
                    icon=msg.Icon, extra=msg.Sound)
            else:
                msg.ID = self._sendCommand(Snarler.SNARL_CMD_SHOW, id=0,
                    timeout=msg.Timeout,
                    title=msg.Title, text=msg.Text,
                    icon=msg.Icon)

    def updateMessage(self, msg):
        self._sendCommand(Snarler.SNARL_CMD_UPDATE, id=msg.ID,
                    title=msg.Title, text=msg.Text,
                    icon=msg.Icon)

    def setTimeout(self, msg):
        self._sendCommand(Snarler.SNARL_CMD_SET_TIMEOUT, id=msg.ID,
                    longdata=msg.Timeout)

    def hideMessage(self, msg):
        self._sendCommand(Snarler.SNARL_CMD_HIDE, id=msg.ID)
        msg.ID = 0

    def msgIsVisible(self, msg):
        return self._sendCommand(Snarler.SNARL_CMD_IS_VISIBLE, id=msg.ID) == -1

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
            self._global_msg = self._u32.RegisterWindowMessageA(Snarler.SNARL_GLOBAL_MSG)

        return self._global_msg

    def registerConfig(self, app, reply):
        if (self._version == (1, 6) or self._version[0] >= 2) and app.Icon != '':
            command = Snarler.SNARL_CMD_REGISTER_CONFIG_WINDOW_2
        else:
            command = Snarler.SNARL_CMD_REGISTER_CONFIG_WINDOW

        return self._sendCommand(command, id=reply,
            longdata=app.Handle, title=app.Title, icon=app.Icon)

    def revokeConfig(self, app):
        return self._sendCommand(Snarler.SNARL_CMD_REVOKE_CONFIG_WINDOW, id=0,
            longdata=app.Handle)

    def registerNotification(self, app_title, alert_title):
        return self._sendCommand(Snarler.SNARL_CMD_REGISTER_ALERT,
            title=app_title, text=alert_title)

    def revokeNotification(self, alert):
        raise NotImplementedError()

    def _getVersion(self):
        hr = self._sendCommand(Snarler.SNARL_CMD_GET_VERSION)
        if hr:
            ver = cast(hr, POINTER(c_byte))
            return (int(ver[0]), int(ver[1]))

        return None

    def _getVersionEx(self):
        ver = self._sendCommand(Snarler.SNARL_CMD_GET_VERSION_EX)
        if ver == 0 or ver >= Snarler.M_NOT_IMPLEMENTED:
            return None
        else:
            return Snarler.SNARL_VERSIONS[ver]

    def _sendCommand(self, command, id=0, timeout=0, longdata=0, title='', text='', icon='',
                     class_=None, extra=None, extra2=None, reserved1=None, reserved2=None):

        if type(title) == types.UnicodeType or type(text) == types.UnicodeType:
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

        return self._u32.SendMessageA(self._hwnd, WM_COPYDATA, 0, cd_info[0])


