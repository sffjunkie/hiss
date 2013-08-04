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

HOST = '127.0.0.1'
#HOST = '10.84.23.66'

def test_connect():
    g = GNTP()
    t = Target('gntp://%s' % HOST)
    g.connect(t)

def test_disconnect():
    g = GNTP()
    t = Target('gntp://%s' % HOST)
    g.connect(t)
    g.disconnect(t)

def test_register():
    g = GNTP()
    n = Notifier('GNTP Test', 'application/x-vnd.sffjunkie.hiss')
    n.add_notification('New', 'New email received.')
    t = Target('gntp://%s' % HOST)
    g.connect(t)
    response = g.register(t, n)
    g.disconnect(t)
    assert response['result'] == 'OK'

def test_unregister():
    g = GNTP()
    n = Notifier('GNTP Test', 'application/x-vnd.sffjunkie.hiss')
    t = Target('gntp://%s' % HOST)
    g.connect(t)
    response = g.register(t, n)
    assert response.type == 'OK'

    response = g.unregister(t, n)
    g.disconnect(t)
    assert response['result'] == 'OK'

def test_register_with_icon():
    g = GNTP()
    i = Icon('file:///c:/me_150.png')
    n = Notifier('GNTP Test', 'application/x-vnd.sffjunkie.hiss',
                 icon=i)
    n.add_notification('New', 'New email received.')
    t = Target('gntp://%s' % HOST)
    g.connect(t)
    response = g.register(t, n)
    assert response['result'] == 'OK'

def test_notification():
    g = GNTP()
    
    n = Notifier('GNTP Test', 'application/x-vnd.sffjunkie.hiss')
    class_id = n.add_notification('1984', 'New email received.')
    
    t = Target('gntp://%s' % HOST)
    g.connect(t)
    _response = g.register(t, n)
    
    notification = n.create_notification(class_id,
                                         title="A brave new world",
                                         text="Say hello to Prism")
    response = g.notify(notification, n)
    assert response['result'] == 'OK'
    print(response)

def test_notification_with_url_callback():
    g = GNTP()
    
    n = Notifier('GNTP Test', 'application/x-vnd.sffjunkie.hiss')
    class_id = n.add_notification('1984', 'New email received.')
    
    t = Target('gntp://%s' % HOST)
    g.connect(t)
    _response = g.register(t, n)
    
    notification = n.create_notification(class_id,
                                         title="Cower In Fear Mortal",
                                         text="Prism says 'we're watching you'")
    notification.add_callback('C:\\')
    response = g.notify(notification, n)
    
    assert response['result'] == 'OK'
    print(response)

def test_notification_with_icon():
    g = GNTP()
    n = Notifier('GNTP Test', 'application/x-vnd.sffjunkie.hiss')
    class_id = n.add_notification('1984', 'New email received.')
    t = Target('gntp://%s' % HOST)
    g.connect(t)
    _response = g.register(t, n)
    
    i = Icon('file:///c:/me_150.png')
    notification = n.create_notification(class_id,
                                         title="Icon test",
                                         text="This notification should have an icon",
                                         icon=i)
    response = g.notify(notification, n)
    assert response['result'] == 'OK'
    print(response)
    

if __name__ == '__main__':
    test_connect()
    test_disconnect()
    test_register()
    #test_unregister()
    #test_register_with_icon()
    test_notification()
    #test_notification_with_url_callback()
    test_notification_with_icon()
    