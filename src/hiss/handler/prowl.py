# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

import asyncio
import aiohttp
import xml.dom.minidom

from hiss.handler import Handler


class ProwlHandler(Handler):
    """:class:`~hiss.handler.Handler` sub-class for Prowl notifications"""

    __name__ = 'Prowl'

    def __init__(self, apptoken=None, loop=None):
        super().__init__(loop)

        self.token = apptoken
        self.port = 443
        self.capabilities = ['notify']

    @asyncio.coroutine
    def connect(self, target):
        """Connect to a :class:`~hiss.target.Target` and return the protocol handling
        the connection.
        
        Overrides the :class:`~hiss.handler.Handler`\'s version.
        """
        protocol = ProwlProtocol()

        target.handler = self

        protocol.target = target
        protocol.loop = self.loop
        protocol.token = self.token
        return protocol


class ProwlProtocol(asyncio.Protocol):
    """Prowl HTTP Protocol."""

    @asyncio.coroutine
    def notify(self, notification, notifier):
        """Send a notification

        :param notification: The notification to send
        :type notification: :class:`~hiss.notification.Notification`
        :param notifier: The notifier to send the notification for or None for
                         the default notifier.
        :type notifier:  :class:`~hiss.notifier.Notifier`
        """

        if self.target.port != -1:
            host = ('api.prowlapp.com', self.target.port)
        else:
            host = 'api.prowlapp.com'
            
        client = aiohttp.HttpClient(host,
                                    ssl=True,
                                    loop=self.loop)

        data = {
            'apikey': self.target.host,
            'application': 'Hiss',
            'event': notification.title,
            'description': notification.text.encode("utf-8"),
            'priority': notification.priority
        }
        
        if self.token:
            data['developerkey'] = self.token
        
        result = {}
        try:
            http_response = yield from client.request(method='POST',
                                                      path='/publicapi/add',
                                                      params=data)
            
            response_data = yield from http_response.read()
            http_response.close()

            response_data = response_data.decode('UTF-8')
            response = ProwlResponse(response_data)

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


class ProwlResponse():
    def __init__(self, response_xml):
        dom = xml.dom.minidom.parseString(response_xml)

        try:
            success_node = dom.getElementsByTagName('success')[0]
            self.status = 'OK'
            self.status_code = int(success_node.getAttribute('code'))
            self.reason = None
            self.remaining = success_node.getAttribute('remaining')
            self.resetdate = success_node.getAttribute('resetdate')
        except:
            error_node = dom.getElementsByTagName('error')[0]
            self.status = 'ERROR'
            self.status_code = int(error_node.getAttribute('code'))
            self.reason = error_node.childNodes[0].nodeValue
            self.remaining = None
            self.resetdate = None
            
            