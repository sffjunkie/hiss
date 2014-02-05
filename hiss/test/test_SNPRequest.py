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

from hiss.hash import HashInfo
from hiss.handler.snp import Request

def test_Request_Create():
	m = Request()

def test_Request_Append():
	m = Request()
	m.append('register', signature='sig', uid='1', title='ww')
	
	assert len(m.commands) == 1
	
	assert m.commands[0].name == 'register'
	assert len(m.commands[0].parameters) == 3
	assert m.commands[0].parameters['signature'] == 'sig'
	assert m.commands[0].parameters['uid'] == '1'
	assert m.commands[0].parameters['title'] == 'ww'

	m.append('add_class')
	assert len(m.commands) == 2

	m.append('add_class', name='sig')
	assert len(m.commands) == 3

def test_Request_Marshall2():
	m = Request(version='2.0')
	m.append('register', signature='application/x-vnd-sffjunkie.hiss', uid='1', title='ww')

	cmd = m.marshall()
	assert cmd == b'snp://register?signature=application/x-vnd-sffjunkie.hiss&title=ww&uid=1\r\n'

def test_Request_Marshall3():
	m = Request(version='3.0')
	m.append('register', signature='application/x-vnd-sffjunkie.hiss', uid='1', title='ww')

	cmd = m.marshall()
	assert cmd == b'SNP/3.0\r\nregister?signature=application/x-vnd-sffjunkie.hiss&title=ww&uid=1\r\nEND\r\n'

def test_Request_Unmarshall2():
	cmd = b'snp://register?signature=x-vnd-sffjunkie.hiss&title=ww&uid=1\r\n'
	request = Request()
	request.unmarshall(cmd)
	assert len(request.commands) == 1
	assert request.commands[0][0] == b'register'
	assert request.commands[0].name == b'register'
	assert len(request.commands[0][1]) == 3
	assert len(request.commands[0].parameters) == 3
	
def test_Request_Unmarshall3():
	cmd = (b'SNP/3.0 NONE MD5:b7c903901cab976ee5db15792eb15a03.1A2B3C4D5E6F\r\n'
		   b'register?signature=x-vnd-sffjunkie.hiss&title=ww&uid=1\r\n'
		   b'add_class?signature=x-vnd-sffjunkie.hiss\r\n'
		   b'END\r\n')
	
	request = Request()
	request.unmarshall(cmd)
	
	assert len(request.commands) == 2
	assert request.commands[0].name == b'register'
	assert len(request.commands[0].parameters) == 3
	assert request.commands[1].name == b'add_class'
	
	assert request._hash == HashInfo('md5',
						    'b7c903901cab976ee5db15792eb15a03',
						    '1A2B3C4D5E6F')

if __name__ == '__main__':
	test_Request_Create()
	test_Request_Append()
	test_Request_Marshall2()
	test_Request_Marshall3()
	test_Request_Unmarshall2()
	test_Request_Unmarshall3()
