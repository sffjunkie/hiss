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

# Part of 'hiss' the Python notification library

import pytest
import asyncio
import os.path
from hiss.target import Target
from hiss.notifier import Notifier
from hiss.handler.snp import SNPHandler
from hiss.resource import Icon

HOST = '127.0.0.1'
#HOST = '10.84.23.66'
NOTIFIER_UID = 'a4327658-f020-4065-b5c7-5fd4c5dd1fc0'

asyncio.log.logger.setLevel(asyncio.log.logging.INFO)

@pytest.fixture
def notifier():
    n = Notifier('A Notifier', 'application/x-vnd.sffjunkie.hiss',
                 uid='0b57469a-c9dd-451b-8d86-f82ce11ad09f')
    n.add_notification('New', 'New email received.')
    n.add_notification('Old', 'Old as an old thing.')
    return n

@pytest.fixture
def icon():
    fname = os.path.abspath(os.path.join(os.path.dirname(__file__), 'python-powered-h-50x65.png'))
    fname = fname.replace('\\', '/')
    return Icon('file:///%s' % fname)

@pytest.fixture
def icon_inverted():
    fname = os.path.abspath(os.path.join(os.path.dirname(__file__), 'python-powered-h-50x65-inverted.png'))
    fname = fname.replace('\\', '/')
    return Icon('file:///%s' % fname)

def test_connect():
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = SNPHandler(loop=loop)
        t = Target('snp://%s' % HOST)
        _protocol = yield from h.connect(t)
        assert t.handler == h

    loop.run_until_complete(coro())

def test_register(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = SNPHandler(loop=loop)

        t = Target('snp://%s' % HOST)

        response = yield from h.register(notifier, t)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)

def test_unregister(notifier):
    loop = asyncio.get_event_loop()

    def coro():
        h = SNPHandler(loop=loop)
        t = Target('snp://%s' % HOST)

        response = yield from h.register(notifier, t)
        assert response['status'] == 'OK'

        response = yield from h.unregister(notifier, t)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)

def test_register_with_icon(notifier, icon):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = SNPHandler(loop=loop)

        notifier.icon = icon

        t = Target('snp://%s' % HOST)

        response = yield from h.register(notifier, t)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)

def test_notification(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = SNPHandler(loop=loop)

        t = Target('snp://%s' % HOST)

        notification = notifier.create_notification(name='New',
                                             title="A brave new world",
                                             text="Say hello to Prism")
        response = yield from h.notify(notification, t)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)

def test_notification_with_string_callback(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = SNPHandler(loop=loop)

        t = Target('snp://%s' % HOST)

        notification = notifier.create_notification(name='New',
                                             title="With a call back",
                                             text="Press me")
        notification.add_callback('callback_test')
        response = yield from h.notify(notification, t)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)

def test_notification_with_url_callback(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = SNPHandler(loop=loop)

        t = Target('snp://%s' % HOST)

        notification = notifier.create_notification(name='New',
                                             title="With URL call back",
                                             text="Press me")
        notification.add_callback('http://news.bbc.co.uk/sport')
        response = yield from h.notify(notification, t)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)

def test_notification_with_icon(notifier, icon_inverted):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = SNPHandler(loop=loop)

        t = Target('snp://%s' % HOST)

        notification = notifier.create_notification(name='Old',
                                             title="A brave new world",
                                             text="This notification should have an icon",
                                             icon=icon_inverted)
        response = yield from h.notify(notification, t)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)
