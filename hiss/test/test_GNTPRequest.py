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

from hiss.handler.gntp import Request

def test_GNTPRequest_Create():
	_r = Request()

def test_GNTPRequest_Marshall():
	msg_in = ("GNTP/1.0 REGISTER NONE\r\nApplication-Name: SurfWriter\r\n"
			  "Application-Icon: http://www.site.org/image.jpg\r\n"
			  "X-Creator: Apple Software\r\n"
			  "X-Application-ID: 08d6c05a21512a79a1dfeb9d2a8f262f\r\n"
			  "Notifications-Count: 2\r\n\r\n"
			  "Notification-Name: Download Complete\r\n"
			  "Notification-Display-Name: Download completed\r\n"
			  "Notification-Icon: x-growl-resource://cb08ca4a7bb5f9683c19133a84872ca7\r\n"
			  "Notification-Enabled: True\r\n"
			  "X-Language: English\r\n"
			  "X-Timezone: PST\r\n\r\n"
			  "Notification-Name: Document Published\r\n"
			  "Notification-Display-Name: Document successfully published\r\n"
			  "Notification-Icon: http://fake.net/image.png\r\n"
			  "Notification-Enabled: False\r\n"
			  "X-Sound: http://fake.net/sound.wav\r\n"
			  "X-Sound-Alt: x-growl-resource://f082d4e3bdfe15f8f5f2450bff69fb17\r\n\r\n"
			  "Identifier: cb08ca4a7bb5f9683c19133a84872ca7\r\n"
			  "Length: 4\r\n\r\nABCD\r\n\r\n"
			  "Identifier: f082d4e3bdfe15f8f5f2450bff69fb17\r\n"
			  "Length: 16\r\n\r\nFGHIJKLMNOPQRSTU\r\n").encode('UTF-8')

	r = Request()
	r.unmarshall(msg_in)
	msg_out = r.marshall()
	assert msg_out == msg_in

def test_GNTPRequest_Unmarshall():
	r = Request()

	msg = ("GNTP/1.0 REGISTER NONE\r\nApplication-Name: SurfWriter\r\n"
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
		   "Length: 16\r\n\r\nFGHIJKLMNOPQRSTU\r\n").encode('UTF-8')
		   
	r.unmarshall(msg)
	
	assert r.version == '1.0'.encode('UTF-8')
	assert r.command == 'REGISTER'.encode('UTF-8')
	assert r.encryption is None
	assert r.hash is None
	
	assert r.header['Application-Name'] == 'SurfWriter'.encode('UTF-8')
	
	msg = "GNTP/1.0 REGISTER sha256:adadad md5:eaeaea.ddd\r\n".encode('UTF-8')
	r.unmarshall(msg)
	
	assert r.version == '1.0'.encode('UTF-8')
	assert r.command == 'REGISTER'.encode('UTF-8')
	assert r.encryption == ('sha256'.encode('UTF-8'), 'adadad'.encode('UTF-8'))
	assert r.hash == ('md5'.encode('UTF-8'), 'eaeaea'.encode('UTF-8'), 'ddd'.encode('UTF-8'))

	msg = "GNTP/1.0 REGISTER NONE md5:eaeaea.ddde\r\n".encode('UTF-8')
	r.unmarshall(msg)

	assert r.encryption is None
	assert r.hash == ('md5'.encode('UTF-8'), 'eaeaea'.encode('UTF-8'), 'ddde'.encode('UTF-8'))

if __name__ == '__main__':
	test_GNTPRequest_Create()
	test_GNTPRequest_Marshall()
	test_GNTPRequest_Unmarshall()
	
