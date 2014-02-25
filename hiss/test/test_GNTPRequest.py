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

from hiss.hash import generate_hash
from hiss.handler.gntp import Request

def test_GNTPRequest_Create():
	_r = Request()

def test_GNTPRequest_marshal():
	msg_in = bytearray(("GNTP/1.0 REGISTER NONE\r\n"
			  "Application-Icon: http://www.site.org/image.jpg\r\n"
			  "Application-Name: SurfWriter\r\n"
			  "X-Application-ID: 08d6c05a21512a79a1dfeb9d2a8f262f\r\n"
			  "Notifications-Count: 2\r\n"
			  "X-Creator: Apple Software\r\n\r\n"
			  "Notification-Display-Name: Download completed\r\n"
			  "Notification-Enabled: True\r\n"
			  "Notification-Icon: x-growl-resource://cb08ca4a7bb5f9683c19133a84872ca7\r\n"
			  "Notification-Name: Download Complete\r\n"
			  "X-Language: English\r\n"
			  "X-Timezone: PST\r\n\r\n"
			  "Notification-Display-Name: Document successfully published\r\n"
			  "Notification-Enabled: False\r\n"
			  "Notification-Icon: http://fake.net/image.png\r\n"
			  "Notification-Name: Document Published\r\n"
			  "X-Sound: http://fake.net/sound.wav\r\n"
			  "X-Sound-Alt: x-growl-resource://f082d4e3bdfe15f8f5f2450bff69fb17\r\n\r\n"
			  "Identifier: cb08ca4a7bb5f9683c19133a84872ca7\r\n"
			  "Length: 4\r\n\r\nABCD\r\n\r\n"
			  "Identifier: f082d4e3bdfe15f8f5f2450bff69fb17\r\n"
			  "Length: 16\r\n\r\nFGHIJKLMNOPQRSTU\r\n").encode('UTF-8'))

	r = Request()
	r.unmarshal(msg_in)
	msg_out = r.marshal()
	assert len(msg_out) == len(msg_in)

def test_GNTPRequest_Unmarshal():
	r = Request()

	msg = bytearray(("GNTP/1.0 REGISTER NONE\r\nApplication-Name: SurfWriter\r\n"
		   "Application-Icon: http://www.site.org/image.jpg\r\n"
		   "X-Creator: Apple Software\r\n"
		   "X-Application-ID: 08d6c05a21512a79a1dfeb9d2a8f262f\r\n"
		   "Notifications-Count: 2\r\n\r\n"
		   "Notification-Name: Download Complete\r\n"
		   "Notification-Display-Name: Download completed\r\n"
		   "Notification-Icon: x-growl-resource://cb08ca4a7bb5f9683c19133a84872ca7\r\n"
		   "Notification-Enabled: True\r\nX-Language: English\r\n"
		   "X-Timezone: PST\r\n\r\nNotification-Name: Document Published\r\n"
		   "Notification-Display-Name: Document successfully published\r\n"
		   "Notification-Icon: http://fake.net/image.png\r\n"
		   "Notification-Enabled: False\r\n"
		   "X-Sound: http://fake.net/sound.wav\r\n"
		   "X-Sound-Alt: x-growl-resource://f082d4e3bdfe15f8f5f2450bff69fb17\r\n\r\n"
		   "Identifier: cb08ca4a7bb5f9683c19133a84872ca7\r\n"
		   "Length: 4\r\n\r\nABCD\r\n\r\n"
		   "Identifier: f082d4e3bdfe15f8f5f2450bff69fb17\r\n"
		   "Length: 16\r\n\r\nFGHIJKLMNOPQRSTU\r\n").encode('UTF-8'))

	r.unmarshal(msg)

	assert r.version == '1.0'
	assert r.command == 'REGISTER'
	assert r._encryption is None
	assert r._hash is None

	assert r.body['Application-Name'] == 'SurfWriter'

def test_GNTPRequest_Unmarshal_WithHash():
	password = 'testtest'
	hash_ = generate_hash(password.encode('UTF-8'))

	r = Request()
	r.password = password
	msg = ("GNTP/1.0 REGISTER NONE %s\r\n" % hash_).encode('UTF-8')
	r.unmarshal(msg)

	assert r.version == '1.0'
	assert r.command == 'REGISTER'
	assert r._hash == hash_
