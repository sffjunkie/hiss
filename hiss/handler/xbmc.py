# Copyright 2009-2012, Simon Kennedy, code@sffjunkie.co.uk
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

from __future__ import unicode_literals

import json
import httplib
from urllib import quote_plus
from mogul.json import rpc, buffer

from hiss.resource import Icon
from hiss.handler import Handler

XBMC_DEFAULT_PORT = 8080

class XBMCError(Exception):
    pass


class XBMC(Handler):
    name = 'XBMC'

    def __init__(self, notifier=None, response_handler=None,
                 port=XBMC_DEFAULT_PORT):
        Handler.__init__(self, notifier, port)
        
        self.capabilities = {
            'show_hide': False,
            'register': False,
            'unregister': False
        }
        
        self.response_handler = response_handler
        
    def notify(self, notification, notifier=None, targets=None, handler=None):
        """Send a notification
        
        Send to either to all known targets or a specific target or list of
        targets
        
        :param notification: The notification to send
        :type notification: :class:`~hiss.notification.Notification`
        :param notifier: The notifier to send the notification for or None for
                         the default notifier.
        :type notifier:  :class:`~hiss.notifier.Notifier`
        :param targets:  The target or list of targets to send the notification
                         to or None for all targets
        :type targets:   :class:`~hiss.target.Target` or list of Target
        """

        targets = self._get_targets(targets)
        notifier = self._get_notifier(notifier)
        
        request = _Request(notification)
        responses = []
        for target in targets:
            response_data = self.send_request(request, target)
            response = self.handle_response(response_data)
            responses.append(response)
        
        if len(responses) == 1:
            responses = responses[0]
            
        return responses

    def send_request(self, request, target):
        request_data = request.marshall()
        conn = httplib.HTTPConnection(target.host, target.port)
        headers = {'Content-Type': 'application/json'}
        conn.request('POST', '/jsonrpc', request_data, headers)
        response = conn.getresponse()
        return response.read()
    
    def handle_response(self, response_data):
        response = json.loads(response_data)
        return {'id': response['id'], 'result': response['result']}


class _Request(rpc.Request):
    def __init__(self, notification):
        rpc.Request.__init__(self, uid=notification.uid,
                             method='GUI.ShowNotification')
        
        self.append('title', notification.title)
        self.append('message', notification.text)
        
        if notification.icon is not None:
            if isinstance(notification.icon, Icon):
                raise ValueError('XBMC is unable to handle icon image data')
            elif notification.icon.startswith('image://'):
                image = 'image://%s' % quote_plus(notification.icon[8:])
            else:
                image = notification.icon
                
            self.append('image', image)

        if notification.timeout != -1:
            self.append('displaytime', notification.timeout*1000)
            