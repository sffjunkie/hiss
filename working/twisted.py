# Copyright 2009-2011, Simon Kennedy, python@sffjunkie.co.uk
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

# Part of 'hiss' the Python notification library

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory, connectionDone

class NotifierProtocol(object, Protocol):
    def connectionMade(self):
        """Send a message to the Nub
        
        Called by the twisted framework
        """

        # Get the next notification and deferred from the queue
        self.msg, self.result = self.factory.next()
        self.transport.write(self.msg.to_raw())
        
        if not self.msg.has_callback:
            self.transport.loseConnection()
            self.result(None)

    def dataReceived(self, data):
        msg = Message()
        msg.from_raw(data)

        self.transport.loseConnection()
        self.result(msg)


class TwistedNotifier(object, ClientFactory):
    protocol = NotifierProtocol

    def __init__(self, reactor=None, uid=None):
        self._reactor = reactor
        self._queue = []        
        self._port = find_open_port(from_port=50000)

    def next(self):
        if len(self._queue) != 0:
            return self._queue.pop(0)
        else:
            return None

    def callback(self, *args, **kwargs):
        msg = args[0]
        print('callback')


