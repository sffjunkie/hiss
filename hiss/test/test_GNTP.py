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

import pytest
import asyncio
import os.path
import logging
from hiss.target import Target
from hiss.notifier import Notifier
from hiss.handler.gntp import GNTPHandler
from hiss.resource import Icon

HOST = '127.0.0.1'
REMOTE_HOST = '10.84.23.66'

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

def test_GNTP_Connect():
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)
        t = Target('gntp://%s' % HOST)
        logging.debug('GNTP: connect')
        yield from h.connect(t)
        assert t.handler == h

    loop.run_until_complete(coro())

def test_GNTP_Register(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)

        t = Target('gntp://%s' % HOST)
        notifier.add_target(t)

        logging.debug('GNTP: register')
        response = yield from h.register(notifier, t)
        assert response['status'] == 'OK'

    loop.run_until_complete(coro())

def test_GNTP_Unregister(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)

        t = Target('gntp://%s' % HOST)

        logging.debug('GNTP: unregister')
        response = yield from h.unregister(notifier, t)
        assert response['status'] == 'ERROR'
        assert response['reason'] == 'Unsupported'

    c = coro()
    loop.run_until_complete(c)

def test_GNTP_Register_WithIcon(notifier, icon):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)
        notifier.icon = icon

        t = Target('gntp://%s' % HOST)

        logging.debug('GNTP: register with icon')
        response = yield from h.register(notifier, t)
        assert response['status'] == 'OK'
        assert response['status_code'] == 0

    c = coro()
    loop.run_until_complete(c)

def test_GNTP_Notification(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)

        t = Target('gntp://%s' % HOST)

        notification = notifier.create_notification(name='New',
                                             title="A brave new world",
                                             text="Say hello to Prism")
        logging.debug('GNTP: notify')
        response = yield from h.notify(notification, t)
        assert response['status'] == 'OK'
        assert response['status_code'] == 0

    c = coro()
    loop.run_until_complete(c)

def test_GNTP_Notification_WithStringCallback(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)

        t = Target('gntp://%s' % HOST)

        notification = notifier.create_notification(name='Old',
                                             title="With a string call back",
                                             text="Press me")
        notification.add_callback('callback_test')
        logging.debug('GNTP: notify with string callback')
        response = yield from h.notify(notification, t)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)

def test_GNTP_Notification_WithUrlCallback(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)

        t = Target('gntp://%s' % HOST)

        notification = notifier.create_notification(name='New',
                                             title="With a call back",
                                             text="Press me")
        notification.add_callback('http://news.bbc.co.uk')
        logging.debug('GNTP: notify with url callback')
        response = yield from h.notify(notification, t)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)

def test_GNTP_Notification_WithIcon(notifier, icon_inverted):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)

        t = Target('gntp://%s' % HOST)

        logging.debug('GNTP: notify with icon')
        notification = notifier.create_notification(name='Old',
                                             title="A brave new world",
                                             text="This notification should have an icon",
                                             icon=icon_inverted)
        response = yield from h.notify(notification, t)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)

def test_GNTP_Notification_Multiple(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)

        t = Target('gntp://%s' % HOST)

        n1 = notifier.create_notification(name='New',
                                   title="A brave new world",
                                   text="Say hello to Prism")
        n1.add_callback('callback_test')

        n2 = notifier.create_notification(name='Old',
                                   title="A second Coming",
                                   text="Say hello to the Time Lords")

        logging.debug('GNTP: multiply notify')
        done, pending = yield from asyncio.wait([h.notify(n1, t), h.notify(n2, t)])

        for task in done:
            response = task.result()
            assert response['status'] == 'OK'
            assert response['status_code'] == 0

    c = coro()
    loop.run_until_complete(c)
