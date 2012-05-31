# Copyright 2009-2011, Simon Kennedy, code@sffjunkie.co.uk
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

from hiss.notifier import Notifier
from hiss.notification import Notification
from hiss.target import Target
from hiss.resource import Icon
from hiss.event import Event, NotificationEvent
from hiss.exception import *

__all__ = ['Notifier', 'Notification', 'Target',  'Icon',
           'Event', 'NotificationEvent',
           'HissError', 'MessageError', 'NotifierError']
