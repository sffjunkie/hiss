# Copyright 2008, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

# Part of 'hiss' the Python notification library

import os.path
import types
import httplib
import urllib

from enum import *
from exception import *

class Boxer(object):
    XBMC_PORT = 8080

    def __init__(self, host='localhost', port=XBMC_PORT):
        self._version = None
        self._application = None

        self.name = 'boxer'

        self.target = '%s:%d' % (host, port)

    def target():
        def fget(self):
            return self._target

        def fset(self, value):
            self._handle = httplib.HTTPConnection(value)
            self._target = value

        return locals()

    target = property(**target())

    def handle():
        def fget(self):
            return self._handle

        return locals()

    handle = property(**handle())

    ready = property(lambda self: self._handle is not None)

    def version():
        def fget(self):
            if self._version is None:
                self._version = self._get_version()

            return self._version

        return locals()

    version = property(**version())

    def register_app(self, app):
        """Register an application and its notifications"""

        pass

    def deregister_app(self, app=None):
        """De-register an application and its notifications"""

        pass

    def show_notification(self, notification):
        # Note: XBMC does not support a sticky notification

        cmnd = '/xbmcCmds/xbmcHttp?command=ExecBuiltIn&parameter=Notification('

        cmnd += '%s,%s' % (urllib.quote(notification.title), urllib.quote(notification.text))

        if notification.timeout != 0:
            cmnd += ',%s' % (notification.timeout * 1000)

        if notification.icon != '':
            cmnd += ',%s' % notification.icon

        cmnd += ')'

        self._handle.request('GET', cmnd)

        if self._handle.getresponse().status == 200:
            return True
        else:
            return False

    def update_notification(self, notification):
        pass

    def set_timeout(self, notification):
        pass

    def hide_notification(self, notification):
        pass

    def notification_is_visible(self, notification):
        pass

    def get_app_path(self):
        pass

    def get_icon_path(self):
        pass

    def register_notification(self, app_title, name, enabled):
        pass

    def deregister_notification(self, app, name):
        pass

    def _get_version(self):
        pass

