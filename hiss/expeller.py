# Copyright 2008, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

# Part of 'hiss' the Python notification library

from expel.xplmessage import xPLMessage

class Expeller(object):
    def __init__(self):
        self._handle = 0
        self.vendor = 'sffj'
        self.device = 'expeller'

    Name = property(lambda self: 'expel')
    Ready = property(lambda self: self._handle != 0)
    Handle = property(lambda self: self._handle)

    Version = property(lambda self: (0, 0))

    def registerApp(self, app):
        pass

    def deregisterApp(self):
        pass

    def showNotification(self, notification):
        pass

    def updateNotification(self, notification):
        pass

    def hideNotification(self, notification):
        # Send and osd.basic message with 'command=clear'
        pass

    def notificationIsVisible(self, notification):
        pass

    def setTimeout(self, notification):
        pass

    def getAppPath(self):
        return ''

    def getIconPath(self):
        return ''

