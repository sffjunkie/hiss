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

from hiss.target import Target
from hiss.notifier import Notifier
from hiss.handler.gntp import GNTP
from hiss.resource import Icon

def test_connect():
    n = Notifier('application/x-vnd.sffjunkie.hiss', 'Register Test')
    g = GNTP(n)
    
    t = Target('gntp://127.0.0.1')
    connected = g.connect(t)
    assert connected == True

def test_register():
    g = GNTP()
    
    n = Notifier('application/x-vnd.sffjunkie.hiss', 'Register Test')
    n.add_notification('New', 'New email received.')
    
    t = Target('gntp://127.0.0.1')
    _connected = g.connect(t)
    response = g.register(t, n)
    assert response.type == 'OK'

def test_register_with_icon():
    g = GNTP()
    
    i = Icon('file:///c:/me_150.png')
    n = Notifier('application/x-vnd.sffjunkie.hiss', 'Register Test',
                 icon=i)
    n.add_notification('New', 'New email received.')
    
    t = Target('gntp://127.0.0.1')
    _connected = g.connect(t)
    response = g.register(t, n)
    assert response.type == 'OK'

def test_notification():
    g = GNTP()
    
    i = Icon('file:///c:/me_150.png')
    n = Notifier('application/x-vnd.sffjunkie.hiss', 'Register Test',
                 icon=i)
    class_id = n.add_notification('1984', 'New email received.')
    
    t = Target('gntp://127.0.0.1')
    _connected = g.connect(t)
    _response = g.register(t, n)
    
    notification = n.create_notification(class_id,
                                         title="A brave new world",
                                         text="Say hello to Prism")
    response = g.notify(notification, n)
    assert response.type == 'OK'

def test_notification_with_url_callback():
    g = GNTP()
    
    n = Notifier('application/x-vnd.sffjunkie.hiss', 'Register Test')
    class_id = n.add_notification('1984', 'New email received.')
    
    t = Target('gntp://127.0.0.1')
    _connected = g.connect(t)
    _response = g.register(t, n)
    
    notification = n.create_notification(class_id,
                                         title="Cower In Fear Mortal",
                                         text="Prism says 'we're watching you'")
    notification.add_callback('C:\\')
    response = g.notify(notification, n)
    
    if notification.has_callback:
        assert response[0].type == 'OK'
        assert response[1].type == 'CALLBACK'
    else:
        assert response.type == 'OK'

def test_notification_with_icon():
    g = GNTP()
    
    n = Notifier('application/x-vnd.sffjunkie.hiss', 'Register Test')
    class_id = n.add_notification('1984', 'New email received.')
    
    t = Target('gntp://127.0.0.1')
    _connected = g.connect(t)
    _response = g.register(t, n)
    
    i = Icon('file:///c:/me_150.png')
    notification = n.create_notification(class_id,
                                         title="Icon test",
                                         text="This notification should have an icon",
                                         icon=i)
    response = g.notify(notification, n)
    assert response.type == 'OK'
    

if __name__ == '__main__':
    #test_connect()
    #test_register()
    #test_register_with_icon()
    test_notification()
    #test_notification_with_url_callback()
    #test_notification_with_icon()
    