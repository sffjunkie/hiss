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
import aiohttp
import json
from urllib.parse import quote_plus
from mogul.json.message import Request

from hiss.resource import Icon
from hiss.handler import Handler

XBMC_DEFAULT_PORT = 8080
XBMC_USERNAME = 'xbmc'
XBMC_PASSWORD = 'xbmc'

class XBMCError(Exception):
    pass


class XBMCHandler(Handler):
    """:class:`~hiss.handler.Handler` sub-class for XBMC messages"""

    __handler__ = 'XBMC'

    def __init__(self, username=XBMC_USERNAME, password=XBMC_PASSWORD, loop=None):
        super().__init__(loop)

        self.port = XBMC_DEFAULT_PORT
        self.username = username
        self.password = password
        self.capabilities = ['notify']

    @asyncio.coroutine
    def connect(self, target):
        protocol = XBMC()

        target.handler = self        
        target.port = self.port
        target.username = self.username
        target.password = self.password

        protocol.target = target
        return protocol


class XBMC(asyncio.Protocol):
    """XBMC JSON Protocol."""

    @asyncio.coroutine
    def notify(self, notification, notifier):
        """Send a notification

        :param notification: The notification to send
        :type notification: :class:`~hiss.notification.Notification`
        :param notifier: The notifier to send the notification for or None for
                         the default notifier.
        :type notifier:  :class:`~hiss.notifier.Notifier`
        """

        request = _NotificationRequest(notification)
        response = yield from self.send_request(request, self.target)
        return response

    @asyncio.coroutine
    def send_request(self, request, target):
        request_data = request.marshal()

        auth = (target.username, target.password)

        client = aiohttp.HttpClient([(target.host, target.port)], method='POST',
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

        result['target'] = str(self.target)
        return result


class _NotificationRequest(Request):
    def __init__(self, notification):
        Request.__init__(self, uid=notification.uid,
                             method='GUI.ShowNotification')

        self.append('title', notification.title)
        self.append('message', notification.text)

        if notification.icon is not None:
            if isinstance(notification.icon, Icon):
                image = notification.icon.data
            elif notification.icon.startswith('image://'):
                image = quote_plus('image://%s' % notification.icon[8:])
            else:
                image = notification.icon

            self.append('image', image)

        if notification.timeout != -1:
            self.append('displaytime', notification.timeout*1000)
            