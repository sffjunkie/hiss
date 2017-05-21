# -*- coding: utf-8 -*-
# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

import os
import sys
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
pytestmark = pytest.mark.skipif(True, reason='pushover not available')

import asyncio
import os.path
import logging
from hiss.target import Target
from hiss.notifier import Notifier
from hiss.handler.pushover import PushoverHandler
from hiss.resource import Icon

asyncio.log.logger.setLevel(asyncio.log.logging.INFO)

@pytest.fixture
def notifier():
    n = Notifier('GNTP Notifier', 'a23MprXQ5P4weDkKWLXR3swDjGa68q')
    n.add_notification('New', 'New email received.')
    n.add_notification('Old', 'Old as an old thing.')
    return n


@pytest.fixture
def bad_notifier():
    n = Notifier('GNTP Notifier', 'a23MprXQ5P4weDkKWLXR3swDjGa6aa')
    n.add_notification('New', 'New email received.')
    n.add_notification('Old', 'Old as an old thing.')
    return n


@pytest.fixture
def icon():
    fname = os.path.abspath(os.path.join(os.path.dirname(__file__),
         'python-powered-h-50x65.png'))

    fname = fname.replace('\\', '/')
    return Icon('file:///%s' % fname)


def test_Pushover_BadAppToken(bad_notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = PushoverHandler(loop=loop)

        t = Target('po://uDyCFupvhfxXcC5GSCvYw7ZUwzeoYe')

        notification = notifier.create_notification(name='New',
                                             title="A brave new world",
                                             text="Say hello to Prism")
        logging.debug('Pushover: notify bad app token')
        response = yield from h.notify(notification, t)
        assert response['status'] == 'ERROR'
        #assert response['status_code'] == 0

    c = coro()
    loop.run_until_complete(c)


def test_Pushover_BadUserToken(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = PushoverHandler(apptoken='a23MprXQ5P4weDkKWLXR3swDjGa68q', loop=loop)

        t = Target('po://uDyCFupvhfxXcC5GSCvYw7ZUwzeoYa')

        notification = notifier.create_notification(name='New',
                                             title="A brave new world",
                                             text="Say hello to Prism")
        logging.debug('Pushover: notify bad app token')
        response = yield from h.notify(notification, t)
        assert response['status'] == 'ERROR'
        #assert response['status_code'] == 0

    c = coro()
    loop.run_until_complete(c)


def test_Pushover_Notification(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = PushoverHandler(apptoken='a23MprXQ5P4weDkKWLXR3swDjGa68q', loop=loop)

        t = Target('po://uDyCFupvhfxXcC5GSCvYw7ZUwzeoYe')

        notification = notifier.create_notification(name='New',
                                             title="A brave new world",
                                             text="Say hello to Prism")
        logging.debug('Pushover: notify')
        response = yield from h.notify(notification, t)
        assert response['status'] == 'OK'
        assert response['status_code'] == 0

    c = coro()
    loop.run_until_complete(c)
