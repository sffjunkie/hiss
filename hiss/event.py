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

__all__ = ['Event', 'NotificationEvent']

EVENT_CODES = {
    0: 'Clicked',
    1: 'TimedOut',
    2: 'Closed',
    3: 'ActionSelected',
}

class Event(object):
    """A generic event."""

    def __init__(self):
        self.code = -1
        """The integer status code of the event"""

        self.data = ''
        """Any data returned. Normally the value associated with the
        callback/action selected that was provided when sending the
        notification.
        """

        self.timestamp = ''
        """Timestamp of event on host"""

        self.host = ''
        """Hostname on the network where the event originated"""

        self.daemon = ''
        """The name of the daemon on the host which generated this event."""

    @property
    def name(self):
        """"Friendly name for the :attr:`code` (Read only)"""

        if self.code in EVENT_CODES:
            return EVENT_CODES[self.code]
        else:
            return 'Unknown'


class NotificationEvent(Event):
    """Encapsulates a notification event returning from one of hiss' handlers"""

    def __init__(self):
        Event.__init__(self)

        self.nid = ''
        """The uid of the notification which generated this event"""

