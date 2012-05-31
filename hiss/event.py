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

# Part of 'hiss' the twisted notification library

__all__ = ['Event', 'NotificationEvent']

class Event(object):
    """A generic event."""
    
    def __init__(self):
        self.name = ''
        """The name of the event"""
        
        self.code = -1
        """The integer status code of the event"""
    

class NotificationEvent(Event):
    """Encapsulates an event returning from one of hiss' handlers"""
    
    def __init__(self):
        Event.__init__(self)
        
        self.nid = ''
        """The uid of the notification which generated this event"""

