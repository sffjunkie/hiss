# Copyright 2009-2012, Simon Kennedy, code@sffjunkie.co.uk
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

# Part of 'hiss' the twisted notification library

from twisted.internet import reactor

import pytest
try:
    from nose.tools import nottest
except ImportError:
    def nottest(fn):
        return fn

from hiss.notifier import Notifier
from hiss.target import Target

@nottest
def test_BadInit():
    with pytest.raises(TypeError):
        n = Notifier()

def test_Init():
    n = Notifier('application/x-vnd.sffjunkie.test', 'Test')

def test_Register():
    n = Notifier('application/x-vnd.sffjunkie.test', 'Hiss',
                 uid='b6d92249-b5aa-49de-8c17-75f147ef04dd')
    n.icon = '!reminder'
    
    n.register_notification('General Alert', default_icon='!dev-ipod')
    class_id = n.register_notification('Big and beautiful')
    
    t = Target('snp://10.84.23.87')
    
    def send_notification():
        m = n.create_notification(name='General Alert', title='Alert',
                                  text=u'This is an alert')
#        m.add_action('@900a', 'test')
#        m.add_action('@600', 'tester')
#        m.add_action('@300', 'testing')
        m.add_callback('!system run', 'News')
        m.icon = '!dev-media-cd'
#        m.percentage = 50
#        m.sound = 'C:\WINDOWS\Media\tada.wav'
        n.notify(m)
    
    reactor.callWhenRunning(n.add_target, t)
    reactor.callLater(0.5, n.register)
    reactor.callLater(1.5, send_notification)
#    reactor.callLater(1, n.subscribe)
#    reactor.callLater(19.5, n.unregister)
    reactor.callLater(20, reactor.stop)
    reactor.run()
    
if __name__ == '__main__':
    test_BadInit()
    test_Init()
    test_Register()
    