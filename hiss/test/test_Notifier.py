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

import sys
import pytest
import logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s',
                    stream=sys.__stdout__)

from twisted.internet import reactor, defer

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
        _n = Notifier()

def test_Init():
    _n = Notifier('application/x-vnd.sffjunkie.test', 'Test')

def test_Register():
    n = Notifier('application/x-vnd.sffjunkie.test', 'Hiss',
                 uid='b6d92249-b5aa-49de-8c17-75f147ef04dd')
    n.icon = '!reminder'
    
    n.add_notification('General Alert', icon='!dev-ipod')
    _class_id = n.add_notification('Big and beautiful')
    
    t = Target('snp://127.0.0.1')
    #t = Target('gntp://127.0.0.1')
    
    def done():
        print('done')
        
    def callback(value):
        print('callback')
    
    def notify():
        m = n.create_notification(name='General Alert', title='Alert',
                                  text=u'This is an alert')
        d = n.notify(m)
        d.addCallback(done)
        return d
    
    def register():
        d = n.register()
        d.addCallback(notify)
        return d

    def go2():    
        d = n.add_target(t)
        d.addCallback(register)
        return d
    
    m = n.create_notification(name='General Alert', title='Alert',
                              text=u'This is an alert')

    @defer.inlineCallbacks
    def go():
        print('go')
        added = yield n.add_target(t)
        if added:
            print('added target')
        else:
            print('unable to add target')
            
        sys.stdout.flush()
        
        print('registering')
        registered = yield n.register()
        if registered:
            print('registered')
        sys.stdout.flush()
        
        notification_id = yield n.notify(m)
        #print('notified')
        #sys.stdout.flush()
        
        #unregistered = yield n.unregister()
        
        #print('unregistered')
        #sys.stdout.flush()
        
        #defer.returnValue(True)
    
    reactor.callWhenRunning(go)
#    reactor.callWhenRunning(n.add_target, t)
#    reactor.callLater(0.5, n.register)
#    reactor.callLater(2.5, n.notify, m)
#    reactor.callLater(1, n.subscribe)
#    reactor.callLater(9.5, n.unregister)
    reactor.callLater(30, reactor.stop)
    reactor.run()
    
if __name__ == '__main__':
    test_BadInit()
    test_Init()
    test_Register()
    