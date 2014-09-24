# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

import asyncio
import aiohttp
import json

from hiss.handler import Handler


class PushoverHandler(Handler):
    """:class:`~hiss.handler.Handler` sub-class for Pushover notifications"""

    __name__ = 'Pushover'

    def __init__(self, apptoken=None, loop=None):
        super().__init__(loop)

        self.token = apptoken
        self.capabilities = ['notify']

    @asyncio.coroutine
    def connect(self, target):
        """Connect to a Target and return the protocol handling the connection.
        
        Overrides the Handler's version.
        """
        protocol = PushoverProtocol()

        target.handler = self

        protocol.target = target
        protocol.loop = self.loop
        protocol.token = self.token
        return protocol


class PushoverProtocol(asyncio.Protocol):
    """Pushover HTTP Protocol."""

    @asyncio.coroutine
    def notify(self, notification, notifier):
        """Send a notification

        :param notification: The notification to send
        :type notification: :class:`~hiss.notification.Notification`
        :param notifier: The notifier to send the notification for or None for
                         the default notifier.
        :type notifier:  :class:`~hiss.notifier.Notifier`
        """
        if notification.actions:
            self.log(notifier, 'Pushover does not handle notification actions')
        
        title = notification.title
        if len(title) > 100:
            title = title[:100]
            self.log(notifier, ('Pushover maximum title length (100) '
                                'exceeded - Truncating'))
            
        message = notification.text
        if len(message) > 512:
            message = message[:512]
            self.log(notifier, ('Pushover maximum message length (512) '
                                'exceeded - Truncating'))

        if self.target.port != -1:
            host = ('api.pushover.net', self.target.port)
        else:
            host = 'api.pushover.net'
            
        client = aiohttp.HttpClient(host,
                                    ssl=True,
                                    loop=self.loop)

        fields = {
            'token': self.token,
            'user': self.target.host,
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

        result['target'] = str(self.target)
        return result
    
    def log(self, notifier, message):
        msg = 'Target {}: {}'.format(self.target, message)
        notifier.log(msg)
        

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
            