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

def test_notification(notifier):
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


if __name__ == '__main__':
    test_notification()
    