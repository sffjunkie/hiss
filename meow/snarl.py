import win32gui, win32api, win32con

from exception import *

class Snarler(object):
    def __init__(self):
        self._hwnd = win32gui.FindWindow(None, 'Snarl')

        if not self._hwnd:
            raise HandlerError()

    def show(self, msg):
        pass

    def sendMessage(self, message, timeout=0):
        pass

    def getVersion(self):
        pass

    def _sendData(self, data):
        return win32api.SendMessage(self._hwnd, win32con.WM_COPYDATA, 0, data)


