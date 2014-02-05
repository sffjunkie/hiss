# Copyright 2013-2014, Simon Kennedy, code@sffjunkie.co.uk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

