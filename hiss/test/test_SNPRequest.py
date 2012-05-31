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

from hiss.handler.snp import SNPRequest

def test_SNPRequest_Create():
	m = SNPRequest()

def test_SNPRequest_Append():
	m = SNPRequest()
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

def test_SNPRequest_Marshall2():
	m = SNPRequest()
	m.append('register', signature='application/x-vnd-sffjunkie.hiss', uid='1', title='ww')

	cmd = m.marshall()
	assert cmd == 'snp://register?signature=application/x-vnd-sffjunkie.hiss&title=ww&uid=1\r\n'

def test_SNPRequest_Marshall3():
	m = SNPRequest(version='3.0')
	m.append('register', signature='application/x-vnd-sffjunkie.hiss', uid='1', title='ww')

	cmd = m.marshall()
	assert cmd == 'SNP/3.0\r\nregister?signature=application/x-vnd-sffjunkie.hiss&title=ww&uid=1\r\nEND\r\n'

def test_SNPRequest_Unmarshall2():
	cmd = 'snp://register?signature=x-vnd-sffjunkie.hiss&title=ww&uid=1\r\n'
	request = SNPRequest()
	request.unmarshall(cmd)
	assert len(request.commands) == 1
	assert request.commands[0][0] == 'register'
	assert request.commands[0].name == 'register'
	assert len(request.commands[0][1]) == 3
	assert len(request.commands[0].parameters) == 3
	
def test_SNPRequest_Unmarshall3():
	cmd = ('SNP/3.0 MD5:b7c903901cab976ee5db15792eb15a03.1A2B3C4D5E6F\r\n'
		   'register?signature=x-vnd-sffjunkie.hiss&title=ww&uid=1\r\n'
		   'add_class?signature=x-vnd-sffjunkie.hiss\r\n'
		   'END\r\n')
	
	request = SNPRequest()
	request.unmarshall(cmd)
	
	assert len(request.commands) == 2
	assert request.commands[0].name == 'register'
	assert len(request.commands[0].parameters) == 3
	assert request.commands[1].name == 'add_class'
	
	assert request.hash == ('md5',
						    'b7c903901cab976ee5db15792eb15a03',
						    '1A2B3C4D5E6F')

if __name__ == '__main__':
	test_SNPRequest_Create()
	test_SNPRequest_Append()
	test_SNPRequest_Marshall2()
	test_SNPRequest_Marshall3()
	test_SNPRequest_Unmarshall2()
	test_SNPRequest_Unmarshall3()
