# -*- coding: utf-8 -*-
# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

import os
import sys
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import asyncio
import os.path
import logging
from hiss.target import Target
from hiss.notifier import Notifier
from hiss.handler.gntp import GNTP_DEFAULT_PORT
from hiss.handler.gntp.async import GNTPHandler
from hiss.resource import Icon

HOST = '127.0.0.1'
INVALID_HOST = '10.0.0.1'
REMOTE_HOST = '10.84.23.66'

asyncio.log.logger.setLevel(asyncio.log.logging.INFO)


@pytest.fixture
def local_target():
    return Target('gntp://%s:%d' % (HOST, GNTP_DEFAULT_PORT))


@pytest.fixture
def remote_target():
    return Target('gntp://%s:%d' % (REMOTE_HOST, GNTP_DEFAULT_PORT))


@pytest.fixture
def notifier():
    n = Notifier('GNTP Notifier', '0b57469a-c9dd-451b-8d86-f82ce11ad09g')
    n.add_notification('New', 'New email received.')
    n.add_notification('Old', 'Old as an old thing.')
    return n


@pytest.fixture
def icon():
    fname = os.path.abspath(os.path.join(os.path.dirname(__file__),
         'python-powered-h-50x65.png'))

    fname = fname.replace('\\', '/')
    return Icon('file:///%s' % fname)


@pytest.fixture
def icon_inverted():
    fname = os.path.abspath(os.path.join(os.path.dirname(__file__),
         'python-powered-h-50x65-inverted.png'))

    fname = fname.replace('\\', '/')
    return Icon('file:///%s' % fname)


def test_GNTP_Aio_Connect_InvalidHost():
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)
        t = Target('gntp://%s' % INVALID_HOST)

        with pytest.raises((ConnectionError, TimeoutError)):
            _protocol = yield from h.connect(t)

    loop.run_until_complete(coro())


def test_GNTP_Aio_Connect(local_target):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)
        logging.debug('GNTP: connect')
        yield from h.connect(local_target)
        assert local_target.handler == h

    loop.run_until_complete(coro())


def test_GNTP_Aio_Register(notifier, local_target):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)

        notifier.add_target(local_target)

        logging.debug('GNTP: register')
        response = yield from h.register(notifier, local_target)
        assert response['status'] == 'OK'

    loop.run_until_complete(coro())


def test_GNTP_Aio_Unregister(notifier, local_target):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)

        logging.debug('GNTP: unregister')
        response = yield from h.unregister(notifier, local_target)
        assert response['status'] == 'ERROR'
        assert response['reason'] == 'Unsupported'

    c = coro()
    loop.run_until_complete(c)


def test_GNTP_Aio_Register_WithIcon(notifier, local_target, icon):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)
        notifier.icon = icon

        logging.debug('GNTP: register with icon')
        response = yield from h.register(notifier, local_target)
        assert response['status'] == 'OK'
        assert response['status_code'] == 0

    c = coro()
    loop.run_until_complete(c)


def test_GNTP_Aio_Notification(notifier, local_target):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)

        notification = notifier.create_notification(name='New',
                                                    title="A brave new world",
                                                    text="Say hello to Prism")
        logging.debug('GNTP: notify')
        response = yield from h.register(notifier, local_target)
        print(response)
        response = yield from h.notify(notification, local_target)
        print(response)
        assert response['status'] == 'OK'
        assert response['status_code'] == 0

    c = coro()
    loop.run_until_complete(c)


def test_GNTP_Aio_Notification_WithStringCallback(notifier, local_target):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)

        notification = notifier.create_notification(name='Old',
                                             title="With a string call back",
                                             text="Press me")
        notification.add_callback('callback_test')
        logging.debug('GNTP: notify with string callback')
        response = yield from h.notify(notification, local_target)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)


def test_GNTP_Aio_Notification_WithUrlCallback(notifier, local_target):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)

        notification = notifier.create_notification(name='New',
                                             title="With a call back",
                                             text="Press me")
        notification.add_callback('http://news.bbc.co.uk')
        logging.debug('GNTP: notify with url callback')
        response = yield from h.notify(notification, local_target)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)


def test_GNTP_Aio_Notification_WithIcon(notifier, icon_inverted, local_target):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)

        logging.debug('GNTP: notify with icon')
        notification = notifier.create_notification(name='Old',
                                             title="A brave new world",
                                             text=("This notification should "
                                             "have an icon"),
                                             icon=icon_inverted)
        response = yield from h.notify(notification, local_target)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)


def test_GNTP_Aio_Notification_Multiple(notifier, local_target):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)

        n1 = notifier.create_notification(name='New',
                                   title="A brave new world",
                                   text="Say hello to Prism")
        n1.add_callback('callback_test')

        n2 = notifier.create_notification(name='Old',
                                   title="A second Coming",
                                   text="Say hello to the Time Lords")

        logging.debug('GNTP: multiply notify')
        done, pending = yield from asyncio.wait([h.notify(n1, local_target),
                                                 h.notify(n2, local_target)])

        for task in done:
            response = task.result()
            assert response['status'] == 'OK'
            assert response['status_code'] == 0

    c = coro()
    loop.run_until_complete(c)


@pytest.mark.skipif(True, reason='Need a second machine')
def test_GNTP_Aio_Notification_RemoteHost(notifier, icon_inverted, remote_target):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = GNTPHandler(loop=loop)

        notification = notifier.create_notification(name='New',
                                                    title="A brave new world",
                                                    text=("This notification should "
                                                    "have an icon"),
                                                    icon=icon_inverted)
        response = yield from h.notify(notification, local_target)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)
