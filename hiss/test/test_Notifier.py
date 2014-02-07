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

# Part of 'hiss' the async notification library

import asyncio

import pytest

from hiss.notifier import Notifier
from hiss.target import Target

asyncio.log.logger.setLevel(asyncio.log.logging.INFO)

@pytest.fixture
def notifier():
    n = Notifier('A Notifier', 'application/x-vnd.sffjunkie.hiss',
                 uid='0b57469a-c9dd-451b-8d86-f82ce11ad09f')
    n.add_notification('New', 'New email received.')
    n.add_notification('Old', 'Old as an old thing.')
    return n

def test_Notifier_BadInit():
    with pytest.raises(TypeError):
        _n = Notifier()

def test_Notifier_Init():
    _n = Notifier('application/x-vnd.sffjunkie.test', 'Test')

def test_Notifier_RegisterTarget(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        #target = Target('snp://127.0.0.1')
        target = Target('gntp://127.0.0.1')

        _response = yield from notifier.add_target(target)
        _response = yield from notifier.register(target)
        pass

    c = coro()
    loop.run_until_complete(c)

def test_Notifier_Notify(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        #target = Target('snp://127.0.0.1')
        target = Target('gntp://127.0.0.1')

        notification = notifier.create_notification(name='Old',
                                                    title='A notification',
                                                    text='This is a wonderful notification')

        _response = yield from notifier.add_target(target)
        _response = yield from notifier.notify(notification, target)
        pass

    c = coro()
    loop.run_until_complete(c)

def test_Notifier_Notify_MultipleTargets(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        #target = Target('snp://127.0.0.1')
        t1 = Target('gntp://127.0.0.1')
        t2 = Target('xbmc://127.0.0.1')

        notification = notifier.create_notification(name='New',
                                                    title='One notification',
                                                    text='Sent to multiple targets')

        _response = yield from notifier.add_target([t1, t2])
        _response = yield from notifier.notify(notification)
        pass

    c = coro()
    loop.run_until_complete(c)
        