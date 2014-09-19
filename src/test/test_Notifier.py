# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

import asyncio

import pytest

from hiss.notifier import Notifier
from hiss.target import Target

asyncio.log.logger.setLevel(asyncio.log.logging.INFO)

HOST = '127.0.0.1'

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

def test_Notifier_AddTarget(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        #target = Target('snp://%s' % HOST)
        target = Target('gntp://%s' % HOST)

        _response = yield from notifier.add_target(target)
        pass

    c = coro()
    loop.run_until_complete(c)

def test_Notifier_RegisterTarget(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        #target = Target('snp://%s' % HOST)
        target = Target('gntp://%s' % HOST)

        _response = yield from notifier.add_target(target)
        _response = yield from notifier.register(target)
        pass

    c = coro()
    loop.run_until_complete(c)

def test_Notifier_Notify(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        #target = Target('snp://%s' % HOST)
        target = Target('gntp://%s' % HOST)

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
        #target = Target('snp://%s' % HOST)
        t1 = Target('gntp://%s' % HOST)
        t2 = Target('xbmc://%s' % HOST)

        notification = notifier.create_notification(name='New',
                                                    title='One notification',
                                                    text='Sent to multiple targets')

        _response = yield from notifier.add_target([t1, t2])
        _response = yield from notifier.notify(notification)
        pass

    c = coro()
    loop.run_until_complete(c)

def test_Notifier_Subscribe(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        target = Target('snp://%s' % HOST)

        _response = yield from notifier.add_target(target)
        _response = yield from notifier.subscribe()
        pass

    c = coro()
    loop.run_until_complete(c)
        