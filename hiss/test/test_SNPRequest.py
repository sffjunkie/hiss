from hiss.protocol.snp import SNPRequest

def test_SNPRequest_Blank():
	m = SNPRequest('x-vnd-sffjunkie.hiss')

def test_SNPRequest_Append():
	m = SNPRequest('x-vnd-sffjunkie.hiss')
	m.append('register', signature='sig', uid='1', title='ww')
	
	assert len(m.commands) == 1
	
	assert m.commands[0].name == 'register'
	assert len(m.commands[0].parameters) == 3
	assert m.commands[0].parameters['signature'] == 'sig'
	assert m.commands[0].parameters['uid'] == '1'
	assert m.commands[0].parameters['title'] == 'ww'

def test_SNPRequest_Marshall2():
	m = SNPRequest('x-vnd-sffjunkie.hiss')
	m.append('register', signature='sig', uid='1', title='ww')

	assert m.marshall() == 'snp://register?signature=sig&title=ww&uid=1\r'

def test_SNPRequest_Marshall3():
	m = SNPRequest('x-vnd-sffjunkie.hiss', version='3.0')
	m.append('register', signature='sig', uid='1', title='ww')

	assert m.marshall() == 'SNP/3.0\r\nregister?signature=sig&title=ww&uid=1\r\nEND\r\n'

if __name__ == '__main__':
	test_SNPRequest_Blank()
	test_SNPRequest_Append()
	test_SNPRequest_Marshall2()
	test_SNPRequest_Marshall3()
