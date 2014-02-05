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

import asyncio
import logging

class Handler():
    def __init__(self, loop):
        self._loop = loop
    
    @asyncio.coroutine
    def connect(self, target):
        """Connect to a Target and return the protocol handling the connection.
        
        :param target: The target to connect to
        :type target:  :class:`~hiss.target.Target`
        
        The target is added to the protocol instance"""
        
        if self._loop is None:
            self._loop = asyncio.get_event_loop()
        
        target.handler = self
        target.port = self.port
        
        logging.debug('Handler: Connecting to %s' % target)

        (transport, protocol) = yield from self._loop.create_connection(self.factory,
            target.host, target.port)

        protocol.target = target
        
        return protocol
        
    @asyncio.coroutine
    def register(self, notifier, target):
        """Connect to a target and register the notifier.
        
        :param notifier: Notifier to register
        :type notifier:  :class:`~hiss.notifier.Notifier`
        :param target:   Target to register notifier with
        :type target:    :class:`~hiss.target.Target`
        """
        
        if 'register' in self.capabilities:
            protocol = yield from self.connect(target)
            response = yield from protocol.register(notifier)
        else:
            response = self._unsupported()

        return response
        
    @asyncio.coroutine
    def notify(self, notification, target):
        """Send a notification to a target.
                        
        :param notification: Notification to display
        :type notification:  :class:`~hiss.notifier.Notifier`
        :param target:       Target to display notification on
        :type target:        :class:`~hiss.target.Target`
        """

        protocol = yield from self.connect(target)
        response = yield from protocol.notify(notification, notification.notifier)
        return response
        
    @asyncio.coroutine
    def unregister(self, notifier, target):
        """Unregister a notifier with a target.
        
        :param notifier: Notifier to unregister
        :type notifier:  :class:`~hiss.notifier.Notifier`
        :param target:   Target to unregister notifier with
        :type target:    :class:`~hiss.target.Target`
        """
        
        if 'unregister' in self.capabilities:
            protocol = yield from self.connect(target)
            response = yield from protocol.unregister(notifier)
        else:
            response = self._unsupported()

        return response
        
    @asyncio.coroutine
    def show(self, uid, target):
        """Show a notification
        
        :param uid:      uid of Notification to show
        :type uid:       str
        :param target:   Target to show notification on
        :type target:    :class:`~hiss.target.Target`
        """
        
        if 'show' in self.capabilities:
            protocol = yield from self.connect(target)
            response = yield from protocol.show(uid)
        else:
            response = self._unsupported()

        return response
        
    @asyncio.coroutine
    def hide(self, uid, target):
        """Hide a notification
        
        :param uid:      uid of Notification to hide
        :type uid:       str
        :param target:   Target to hide notification on
        :type target:    :class:`~hiss.target.Target`
        """
        
        if 'hide' in self.capabilities:
            protocol = yield from self.connect(target)
            response = yield from protocol.hide(uid)
        else:
            response = self._unsupported()

        return response
        
    @asyncio.coroutine
    def isvisible(self, uid, target):
        """Determine if a notification is visible
        
        :param uid:      uid of Notification to check
        :type uid:       str
        :param target:   Target to ask if notification is visible
        :type target:    :class:`~hiss.target.Target`
        """
        
        if 'isvisible' in self.capabilities:
            protocol = yield from self.connect(target)
            response = yield from protocol.isvisible(uid)
        else:
            response = self._unsupported()

        return response

    def _unsupported(self):
        return {'status': 'ERROR', 'reason': 'Unsupported'}


class Factory():
    def __init__(self, cls):
        self._protocol_class = cls
    
    def __call__(self):
        protocol = self._protocol_class()
        protocol.factory = self
        return protocol
    