# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

import pytest
pytestmark = pytest.mark.skipif(True, reason='pushbullet not available')

import asyncio
import logging
import os.path

from hiss.handler.pushbullet import PushbulletHandler
from hiss.notifier import Notifier
from hiss.resource import Icon
from hiss.target import Target

asyncio.log.logger.setLevel(asyncio.log.logging.INFO)


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


def test_Pushbullet_BadUserToken(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = PushbulletHandler(loop=loop)

        t = Target('pb://gBfoLoTocaLSQJtM7rWEJaEAPf5Pf')

        notification = notifier.create_notification(name='New',
                                             title="A brave new world",
                                             text="Say hello to Prism")
        logging.debug('Pushbullet: notify bad app token')
        response = yield from h.notify(notification, t)
        assert response['status'] == 'ERROR'
        #assert response['status_code'] == 0

    c = coro()
    loop.run_until_complete(c)


def test_Pushbullet_Notification(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = PushbulletHandler(loop=loop)

        t = Target('pb://gBfoLoTocaLSQJtM7rWEJaEAPf5PXsdf')

        notification = notifier.create_notification(name='New',
                                             title="A brave new world",
                                             text="Say hello to Prism")
        logging.debug('Pushbullet: notify')
        response = yield from h.notify(notification, t)
        assert response['status'] == 'OK'
        assert response['status_code'] == 0

    c = coro()
    loop.run_until_complete(c)
