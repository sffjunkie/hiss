# Copyright 2008, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

# Part of 'hiss' the Python notification library

import md5
import socket
import struct
import types

from enum import *
from exception import *

GROWL_UDP_PORT = 9887

GrowlProtocol = Enum('Growl Protocol',
    [('Base', 1), ('AES128', 2)])

GrowlType = Enum('Growl Type',
    [('Registration', 0),
     ('Notification', 1),
     ('Registration256', 2),
     ('Notification256', 3),
     ('RegistrationNoAuth', 4),
     ('NotificationNoAuth', 5)
    ])

class Growler(object):
    def __init__(self, hostname, password):
        self._handler = 0
        self._hostname = hostname
        self._password = password
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    Name = property(lambda self: 'growl')
    Ready = property(lambda self: self._handler != 0)
    Handle = property(lambda self: self._handler)

    def _get_version(self):
        """Get the current version of Growl as a tuple (Major, Minor)"""
        if self._version is None:
            self._version = (0, 7)

        return self._version

    Version = property(_get_version)

    def registerApp(self, app):
        packet = struct.pack('!BBHBB',
            GrowlProtocol.Base,
            GrowlType.NotificationNoAuth,
            len(app.Title),
            app.NotificationCount,
            app.NotificationEnabledCount)

        packet += app.Title

        enables = []
        for name, enabled in app.Notifications.iteritems():
            name = name.encode('utf-8')
            packet += struct.pack('!H', len(name))
            packet += name
            enables.append(enabled)

        index = 0
        for enabled in enables:
            if enabled:
                packet += struct.pack('!B', index)

            index += 1

        self.send(packet)

    def deregisterApp(self, app):
        pass

    def showNotification(self, notification):
        pass

    def updateNotification(self, notification):
        pass

    def hideNotification(self, notification):
        pass

    def notificationIsVisible(self, notification):
        pass

    def getAppPath(self):
        return ''

    def getIconPath(self):
        return ''

    def send(self, data):
        self._socket.sendto(data, (self._hostname, GROWL_UDP_PORT))

