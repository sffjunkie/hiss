# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

import pytest
pytestmark = pytest.mark.skipif(True, reason='XBMC not installed')

import asyncio
from hiss.target import Target
from hiss.notifier import Notifier
from hiss.handler.xbmc import XBMCHandler

HOST = '127.0.0.1'
#HOST = '10.84.23.66'

asyncio.log.logger.setLevel(asyncio.log.logging.INFO)

@pytest.fixture
def notifier():
    n = Notifier('Notifier Test', 'application/x-vnd.sffjunkie.hiss')
    n.add_notification('New', 'New email received.')
    n.add_notification('Old', 'Old as an old thing.')
    return n


def test_XBMC_Notification(notifier):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def coro():
        h = XBMCHandler(loop=loop)

        t = Target('xbmc://%s' % HOST)

        notification = notifier.create_notification(name='New',
                                                    title="A brave new world",
                                                    text="Say hello to Prism",
                                                    icon='info')
        response = yield from h.notify(notification, t)
        if response['status'] == 'ERROR':
            assert response['reason'] == 'All hosts are unreachable.'
        else:
            assert response['status_code'] == 0

    c = coro()
    loop.run_until_complete(c)
