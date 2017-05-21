# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

import asyncio
import logging
from pprint import pformat

from hiss.handler.aio import AIOHandler
from hiss.handler.gntp import GNTP_DEFAULT_PORT
from .message import (RegisterRequest, UnregisterRequest,
                      NotifyRequest, SubscribeRequest,
                      Response)


class GNTPHandler(AIOHandler):
    """:class:`~hiss.handler.Handler` sub-class for GNTP notifications"""

    __name__ = 'GNTP'

    def __init__(self, loop=None):
        super().__init__(loop)

        self.port = GNTP_DEFAULT_PORT
        self.factory = lambda: GNTPProtocol()
        self.capabilities = ['register', 'subscribe']


class GNTPProtocol(asyncio.Protocol):
    def __init__(self):
        self._target = None
        self._buffer = None
        self.use_encryption = False
        self.use_hash = False

    def connection_made(self, transport):
        self.response = None
        self._buffer = bytearray()
        self._transport = transport

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = value
        if value.is_remote:
            self.use_hash = True

    def send_request(self, request, target):
        if target.password is not None and (self.use_hash or self.use_encryption):
            request.password = target.password.encode('UTF-8')
            request.use_hash = self.use_hash
            request.use_encryption = self.use_encryption

        request_data = request.marshal()
        self._transport.write(request_data)

    @asyncio.coroutine
    def _wait_for_response(self):
        while True:
            if self.response is not None:
                return
            else:
                yield from asyncio.sleep(0.1)

    def data_received(self, data):
        self._buffer.extend(data)
        
        callback_response = None
        items = [i for i in self._buffer.split(b'\r\n\r\n') if len(i) > 0]
        if len(items) > 1:
            response_data = items[0]
            callback_data = items[1]

            callback_response = Response()
            callback_response.unmarshal(callback_data)
        else:
            response_data = items[0]

        response = Response()
        response.unmarshal(response_data)

        result = {}
        result['command'] = response.command
        result['handler'] = 'GNTP'
        result['status'] = response.status
        result['status_code'] = response.status_code
        result['timestamp'] = response.timestamp
        result['target'] = str(self.target)
        if response.status =='ERROR':
            result['reason'] = response.reason

        if callback_response is not None:
            cb_result = {}
            cb_result['nid'] = callback_response.nid
            cb_result['status'] = callback_response.callback_status
            cb_result['timestamp'] = callback_response.callback_timestamp
            result['callback'] = cb_result

        self.response = result

    @asyncio.coroutine
    def register(self, async_notifier):
        """Register ``async_notifier`` with a our target 

        :param async_notifier: The Notifier to register
        :type async_notifier:  :class:`~hiss.async_notifier.Notifier`
        """

        request = RegisterRequest(async_notifier)
        self.send_request(request, self.target)
        yield from self._wait_for_response()
        logging.debug(pformat(self.response))
        return self.response

    @asyncio.coroutine
    def unregister(self, async_notifier):
        """Unregister the async_notifier from the target"""

        request = UnregisterRequest(async_notifier)
        self.send_request(request, self.target)
        yield from self._wait_for_response()
        logging.debug(pformat(self.response))
        return self.response

    @asyncio.coroutine
    def notify(self, notification, async_notifier):
        """Send a notification

        :param notification: The notification to send
        :type notification: :class:`~hiss.notification.Notification`
        """

        request = NotifyRequest(notification, async_notifier)
        self.send_request(request, self.target)
        yield from self._wait_for_response()
        logging.debug(pformat(self.response))
        return self.response

    @asyncio.coroutine
    def subscribe(self, async_notifier, signatures):
        """Register ``async_notifier`` with a our target 

        :param async_notifier: The Notifier to register
        :type async_notifier:  :class:`~hiss.async_notifier.Notifier`
        :param signatures:    Application signatures to receive messages from
        :type signatures:     List of string or [] for all
                              applications
        """
        
        self._async_handler = async_notifier._handler

        request = SubscribeRequest(async_notifier)
        self.send_request(request, self.target)
        yield from self._wait_for_response()
        logging.debug(pformat(self.response))
        return self.response

