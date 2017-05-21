# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

"""Handler for the Pushover API (https://pushover.net/api)
"""

import asyncio
import aiohttp
import json

from hiss.handler.aio import Handler


class PushoverHandler(Handler):
    """:class:`~hiss.handler.Handler` sub-class for Pushover notifications"""

    __name__ = 'Pushover'

    def __init__(self, loop=None):
        super().__init__(loop)

        self.capabilities = ['notify']

    @asyncio.coroutine
    def connect(self, local_target):
        """Connect to a :class:`~hiss.local_target.Target` and return the protocol
        handling the connection.
        
        Overrides the :class:`~hiss.handler.Handler`\'s version.
        """
        protocol = PushoverProtocol()

        local_target.handler = self

        protocol.local_target = local_target
        protocol.loop = self.loop
        return protocol


class PushoverProtocol(asyncio.Protocol):
    """Pushover HTTP Protocol."""

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
            self.log(async_notifier, 'Pushover does not handle notification actions')
        
        if notification.callback:
            self.log(async_notifier, 'Pushover does not handle notification callbacks')
        
        title = notification.title
        if len(title) > 100:
            title = title[:100]
            self.log(async_notifier, ('Pushover maximum title length (100) '
                                'exceeded - Truncating'))
            
        message = notification.text
        if len(message) > 512:
            message = message[:512]
            self.log(async_notifier, ('Pushover maximum message length (512) '
                                'exceeded - Truncating'))

        if self.local_target.port != -1:
            host = ('api.pushover.net', self.local_target.port)
        else:
            host = 'api.pushover.net'
            
        client = aiohttp.HttpClient(host,
                                    ssl=True,
                                    loop=self.loop)

        fields = {
            'token': async_notifier.signature,
            'user': self.local_target.host,
            'title': title.encode('UTF-8'),
            'message': notification.text.encode("utf-8"),
            'priority': notification.priority
        }
        
        if notification.callback:
            fields['url'] = notification.callback.command
            fields['url_title'] = notification.callback.label
        
        data = aiohttp.helpers.FormData(fields)
        
        result = {}
        try:
            http_response = yield from client.request(method='POST',
                                                      path='/1/messages.json',
                                                      data=data)
            
            response_data = yield from http_response.read()
            http_response.close()

            response_data = response_data.decode('UTF-8')
            response = PushoverResponse(response_data)

            if http_response.status == 200:
                result['status'] = 'OK'
                result['status_code'] = 0
            else:
                result['status'] = 'ERROR'
                result['status_code'] = response.status_code
                result['reason'] = response.reason

        except Exception as exc:
            result['status'] = 'ERROR'
            result['reason'] = exc.args[0]

        result['local_target'] = str(self.local_target)
        return result
    
    def log(self, async_notifier, message):
        msg = 'Target {}: {}'.format(self.local_target, message)
        async_notifier.log(msg)
        

class PushoverResponse():
    def __init__(self, response_json):
        data = json.loads(response_json)
        if data['status'] == 1:
            self.status = 'OK'
            self.status_code = 0
            self.reason = None
        else:
            self.status = 'ERROR'
            self.status_code = -1
            self.reason = data['errors'][0]
            