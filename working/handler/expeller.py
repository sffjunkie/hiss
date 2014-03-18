# Copyright 2013-2014, Simon Kennedy, code@sffjunkie.co.uk
#
# Part of 'hiss' the asynchronous notification library

from expel.xplmessage import xPLMessage

class Expeller(object):
    def __init__(self):
        self._handle = 0
        self.vendor = 'sffj'
        self.device = 'expeller'

    name = property(lambda self: 'expel')
    ready = property(lambda self: self._handle != 0)
    handle = property(lambda self: self._handle)

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

