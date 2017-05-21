# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

import pytest
pytestmark = pytest.mark.skipif(True, reason='SNP not installed')

import asyncio
import os.path
from hiss.target import Target
from hiss.notifier import Notifier
from hiss.handler.snp import SNPHandler
from hiss.resource import Icon

HOST = '127.0.0.1'
INVALID_HOST = '10.0.0.1'
REMOTE_HOST = '10.84.23.57'

asyncio.log.logger.setLevel(asyncio.log.logging.INFO)

@pytest.fixture
def notifier():
    n = Notifier('SNP Notifier', '0b57469a-c9dd-451b-8d86-f82ce11ad09f')
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


def test_SNP_Connect_InvalidHost():
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = SNPHandler(loop=loop)
        t = Target('snp://%s' % INVALID_HOST)
        
        with pytest.raises(ConnectionError):
            _protocol = yield from h.connect(t)

    loop.run_until_complete(coro())


def test_SNP_Connect():
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = SNPHandler(loop=loop)
        t = Target('snp://%s' % HOST)
        _protocol = yield from h.connect(t)
        assert t.handler == h

    loop.run_until_complete(coro())


def test_SNP_Register(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = SNPHandler(loop=loop)

        t = Target('snp://%s' % HOST)

        response = yield from h.register(notifier, t)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)


def test_SNP_Unregister(notifier):
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


def test_SNP_Register_WithIcon(notifier, icon):
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


def test_SNP_Notification(notifier):
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


def test_SNP_Notification_WithStringCallback(notifier):
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


def test_SNP_Notification_WithUrlCallback(notifier):
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


def test_SNP_Notification_WithIcon(notifier, icon_inverted):
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


def test_SNP_Subscribe(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = SNPHandler(loop=loop)

        t = Target('snp://%s' % HOST)

        yield from notifier.add_target(t)
        response = yield from h.subscribe(notifier, [], t)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)
   

@pytest.mark.skipif(True, reason='Need a second machine')
def test_SNP_Notification_RemoteHost(notifier, icon_inverted):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = SNPHandler(loop=loop)

        t = Target('snp://%s' % REMOTE_HOST)

        notification = notifier.create_notification(name='New',
                                             title="A brave new world",
                                             text="This notification should have an icon",
                                             icon=icon_inverted)
        response = yield from h.notify(notification, t)
        assert response['status'] == 'OK'

    c = coro()
    loop.run_until_complete(c)
