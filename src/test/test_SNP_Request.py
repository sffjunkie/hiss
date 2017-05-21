# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

from hiss.hash import HashInfo
from hiss.handler.snp import Request


def test_SNP_Request_Create():
	_m = Request()


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


def test_SNP_Request_marshal2():
	m = Request(version='2.0')
	m.append('register', signature='application/x-vnd-sffjunkie.hiss', uid='1', title='ww')

	cmd = m.marshal()
	assert cmd == b'snp://register?signature=application/x-vnd-sffjunkie.hiss&title=ww&uid=1\r\n'


def test_SNP_Request_marshal3():
	m = Request(version='3.0')
	m.append('register', signature='application/x-vnd-sffjunkie.hiss', uid='1', title='ww')

	cmd = m.marshal()
	assert cmd == b'SNP/3.0 NONE\r\nregister?signature=application/x-vnd-sffjunkie.hiss&title=ww&uid=1\r\nEND\r\n'


def test_SNP_Request_Unmarshal2():
	cmd = b'snp://register?signature=x-vnd-sffjunkie.hiss&title=ww&uid=1\r\n'
	request = Request()
	request.unmarshal(cmd)
	assert len(request.commands) == 1
	assert request.commands[0][0] == b'register'
	assert request.commands[0].name == b'register'
	assert len(request.commands[0][1]) == 3
	assert len(request.commands[0].parameters) == 3


def test_SNP_Request_Unmarshal3():
	cmd = (b'SNP/3.0 NONE MD5:b7c903901cab976ee5db15792eb15a03.1A2B3C4D5E6F\r\n'
		   b'register?signature=x-vnd-sffjunkie.hiss&title=ww&uid=1\r\n'
		   b'add_class?signature=x-vnd-sffjunkie.hiss\r\n'
		   b'END\r\n')

	request = Request()
	request.unmarshal(cmd)

	assert len(request.commands) == 2
	assert request.commands[0].name == b'register'
	assert len(request.commands[0].parameters) == 3
	assert request.commands[1].name == b'add_class'

	assert request._hash == HashInfo('md5',
						    'b7c903901cab976ee5db15792eb15a03',
						    '1A2B3C4D5E6F')
