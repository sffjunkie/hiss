# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

"""Handler for the XBMC JSON RPC API
(http://wiki.xbmc.org/index.php?title=JSON_RPC)
"""

import asyncio
import aiohttp
import json
from urllib.parse import quote_plus

from .jsonrpc.message import RPCRequest

from hiss.resource import Icon
from hiss.handler.aio import Handler

XBMC_DEFAULT_PORT = 8080
XBMC_USERNAME = 'xbmc'
XBMC_PASSWORD = 'xbmc'

class XBMCError(Exception):
    pass


class XBMCHandler(Handler):
    """:class:`~hiss.handler.Handler` sub-class for XBMC notifications"""

    __name__ = 'XBMC'

    def __init__(self, username=XBMC_USERNAME, password=XBMC_PASSWORD, loop=None):
        super().__init__(loop)

        self.port = XBMC_DEFAULT_PORT
        self.username = username
        self.password = password
        self.capabilities = ['notify']

    @asyncio.coroutine
    def connect(self, local_target):
        """Connect to a Target and return the protocol handling the connection.
        
        Overrides the :class:`~hiss.handler.Handler`\'s version.
        """
        protocol = XBMCProtocol()

        local_target.handler = self        
        local_target.port = self.port
        local_target.username = self.username
        local_target.password = self.password

        protocol.local_target = local_target
        return protocol


class XBMCProtocol(asyncio.Protocol):
    """XBMC JSON Protocol.
    
    Uses :mod:`aiohttp` to communicate with XBMC"""

    @asyncio.coroutine
    def notify(self, notification, async_notifier):
        """Send a notification

        :param notification: The notification to send
        :type notification: :class:`~hiss.notification.Notification`
        :param async_notifier: The async_notifier to send the notification for or None for
                         the default async_notifier.
        :type async_notifier:  :class:`~hiss.async_notifier.Notifier`
        """

        request = _NotificationRequest(notification)
        response = yield from self._send_request(request, self.local_target)
        return response

    @asyncio.coroutine
    def _send_request(self, request, local_target):
        request_data = request.marshal()

        auth = (local_target.username, local_target.password)

        client = aiohttp.HttpClient([(local_target.host, local_target.port)], method='POST',
                                    path='/jsonrpc')
        headers = {'Content-Type': 'application/json'}

        result = {}
        try:
            http_response = yield from client.request(headers=headers, data=request_data, auth=auth)
            if http_response.status == 200:
                response_data = yield from http_response.read()
                http_response.close()

                data = json.loads(response_data.decode('UTF-8'))

                result['status'] = data['result']
                if data['result'] == 'OK':
                    result['status_code'] = 0
            else:
                result['status'] = 'ERROR'
                result['reason'] = http_response.reason

        except Exception as exc:
            result['status'] = 'ERROR'
            result['reason'] = exc.args[0]

        result['local_target'] = str(self.local_target)
        return result


class _NotificationRequest(RPCRequest):
    def __init__(self, notification):
        super().__init__(method='GUI.ShowNotification',
                         uid=notification.uid,
                         title=notification.title,
                         message=notification.text)

        if notification.icon is not None:
            if isinstance(notification.icon, Icon):
                image = notification.icon.data
            elif notification.icon.startswith('image://'):
                image = quote_plus('image://%s' % notification.icon[8:])
            else:
                image = notification.icon

            self.append('image', image)

        if notification.timeout != -1:
            self.append('displaytime', notification.timeout * 1000)
            