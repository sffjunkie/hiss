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

from hiss.handler.gntp import GNTPRequest

def test_GNTPRequest_Create():
	_r = GNTPRequest()

def test_GNTPRequest_Marshall():
	msg_in = "GNTP/1.0 REGISTER NONE\r\nApplication-Name: SurfWriter\r\nApplication-Icon: http://www.site.org/image.jpg\r\nX-Creator: Apple Software\r\nX-Application-ID: 08d6c05a21512a79a1dfeb9d2a8f262f\r\nNotifications-Count: 2\r\n\r\nNotification-Name: Download Complete\r\nNotification-Display-Name: Download completed\r\nNotification-Icon: x-growl-resource://cb08ca4a7bb5f9683c19133a84872ca7\r\nNotification-Enabled: True\r\nX-Language: English\r\nX-Timezone: PST\r\n\r\nNotification-Name: Document Published\r\nNotification-Display-Name: Document successfully published\r\nNotification-Icon: http://fake.net/image.png\r\nNotification-Enabled: False\r\nX-Sound: http://fake.net/sound.wav\r\nX-Sound-Alt: x-growl-resource://f082d4e3bdfe15f8f5f2450bff69fb17\r\n\r\nIdentifier: cb08ca4a7bb5f9683c19133a84872ca7\r\nLength: 4\r\n\r\nABCD\r\n\r\nIdentifier: f082d4e3bdfe15f8f5f2450bff69fb17\r\nLength: 16\r\n\r\nFGHIJKLMNOPQRSTU\r\n"
	r = GNTPRequest()
	r.unmarshall(msg_in)
	msg_out = r.marshall()
	assert msg_out == msg_in

def test_GNTPRequest_Unmarshall():
	r = GNTPRequest()

	msg = "GNTP/1.0 REGISTER NONE\r\nApplication-Name: SurfWriter\r\nApplication-Icon: http://www.site.org/image.jpg\r\nX-Creator: Apple Software\r\nX-Application-ID: 08d6c05a21512a79a1dfeb9d2a8f262f\r\nNotifications-Count: 2\r\n\r\nNotification-Name: Download Complete\r\nNotification-Display-Name: Download completed\r\nNotification-Icon: x-growl-resource://cb08ca4a7bb5f9683c19133a84872ca7\r\nNotification-Enabled: True\r\nX-Language: English\r\nX-Timezone: PST\r\n\r\nNotification-Name: Document Published\r\nNotification-Display-Name: Document successfully published\r\nNotification-Icon: http://fake.net/image.png\r\nNotification-Enabled: False\r\nX-Sound: http://fake.net/sound.wav\r\nX-Sound-Alt: x-growl-resource://f082d4e3bdfe15f8f5f2450bff69fb17\r\n\r\nIdentifier: cb08ca4a7bb5f9683c19133a84872ca7\r\nLength: 4\r\n\r\nABCD\r\n\r\nIdentifier: f082d4e3bdfe15f8f5f2450bff69fb17\r\nLength: 16\r\n\r\nFGHIJKLMNOPQRSTU\r\n"
	r.unmarshall(msg)
	
	assert r.version == '1.0'
	assert r.command == 'REGISTER'
	assert r.encryption is None
	assert r.hash is None
	
	assert r.header['Application-Name'] == 'SurfWriter'
	
	msg = "GNTP/1.0 REGISTER sha256:adadad md5:eaeaea.ddd\r\n"
	r.unmarshall(msg)
	
	assert r.version == '1.0'
	assert r.command == 'REGISTER'
	assert r.encryption == ('sha256', 'adadad')
	assert r.hash == ('md5', 'eaeaea', 'ddd')

	msg = "GNTP/1.0 REGISTER NONE md5:eaeaea.ddde\r\n"
	r.unmarshall(msg)

	assert r.encryption is None
	assert r.hash == ('md5', 'eaeaea', 'ddde')

if __name__ == '__main__':
	test_GNTPRequest_Create()
	test_GNTPRequest_Marshall()
	test_GNTPRequest_Unmarshall()
	
