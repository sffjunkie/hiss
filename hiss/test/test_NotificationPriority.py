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

from hiss.notification import NotificationPriority

def test_NotificationPriority_VeryLow():
    p = NotificationPriority.very_low
    assert p.value == -2

def test_NotificationPriority_Moderate():
    p = NotificationPriority.moderate
    assert p.value == -1

def test_NotificationPriority_Normal():
    p = NotificationPriority.normal
    assert p.value == 0

def test_NotificationPriority_High():
    p = NotificationPriority.high
    assert p.value == 1

def test_NotificationPriority_Emergency():
    p = NotificationPriority.emergency
    assert p.value == 2
    