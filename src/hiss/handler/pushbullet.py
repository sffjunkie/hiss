# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

"""Handler for the Pushbullet API (https://docs.pushbullet.com/http/).
"""

import asyncio
import aiohttp
import json

from hiss.handler.aio import Handler


class PushbulletHandler(Handler):
    """:class:`~hiss.handler.Handler` sub-class for Pushbullet notifications"""

    __name__ = 'Pushbullet'

    def __init__(self, loop=None):
        super().__init__(loop)

        self.capabilities = ['notify']

    @asyncio.coroutine
    def connect(self, target):
        """Connect to a :class:`~hiss.target.Target` and return the protocol
        handling the connection.

        Overrides the :class:`~hiss.handler.Handler`\'s version.
        """
        protocol = PushbulletProtocol()

        target.handler = self

        protocol.target = target
        protocol.loop = self.loop
        return protocol


class PushbulletProtocol(asyncio.Protocol):
    """Pushbullet HTTP Protocol."""

    @asyncio.coroutine
    def notify(self, notification, async_notifier):
        """Send a notification

        :param notification: The notification to send
        :type notification: :class:`~hiss.notification.Notification`
        :param async_notifier: The async_notifier to send the notification for or None for
                         the default async_notifier.
        :type async_notifier:  :class:`~hiss.async_notifier.Notifier`
        """
        if notification.actions:
            self.log(async_notifier, 'Pushbullet does not handle notification actions')

        if self.target.port != -1:
            host = ('api.pushbullet.com', self.target.port)
        else:
            host = 'api.pushbullet.com'

        client = aiohttp.HttpClient(host,
                                    ssl=True,
                                    loop=self.loop)

        auth = aiohttp.BasicAuth(self.target.host, '')

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        fields = {
            'title': notification.title,
            'body': notification.text,
        }

        if notification.callback:
            fields['type'] = 'link'
            fields['url'] = notification.callback
        else:
            fields['type'] = 'note'

        data = json.dumps(fields).encode('UTF-8')

        result = {}
        try:
            http_response = yield from client.request(method='POST',
                                                      path='/v2/pushes',
                                                      auth=auth,
                                                      headers=headers,
                                                      data=data)

            response_data = yield from http_response.read()
            http_response.close()

            response_data = response_data.decode('UTF-8')
            response = PushbulletResponse(response_data)

            if http_response.status == 200:
                result['status'] = 'OK'
                result['status_code'] = 0
            else:
                result['status'] = 'ERROR'
                result['status_code'] = http_response.status_code
                result['reason'] = response.reason

        except Exception as exc:
            result['status'] = 'ERROR'
            result['reason'] = exc.args[0]

        result['target'] = str(self.target)
        return result

    def log(self, async_notifier, message):
        text = 'Target {}: {}'.format(self.target, message)
        async_notifier.log(text)


class PushbulletResponse():
    def __init__(self, response_json):
        data = json.loads(response_json)
        if 'error' in data:
            self.status = 'ERROR'
            self.status_code = -1
            self.reason = data['error']['message']
        else:
            self.status = 'OK'
            self.status_code = 0
            self.reason = None
