from hiss.protocol.snp import SNPMessage

def test_SNPMessage_Blank():
	m = SNPMessage('x-vnd-sffjunkie.hiss')

def test_SNPMessage_Append():
	m = SNPMessage('x-vnd-sffjunkie.hiss')
	m.append('register', signature='sig', uid='1', title='ww')
	
	assert len(m.commands) == 1
	
	assert m.commands[0].name == 'register'
	assert len(m.commands[0].parameters) == 3
	assert m.commands[0].parameters['signature'] == 'sig'
	assert m.commands[0].parameters['uid'] == '1'
	assert m.commands[0].parameters['title'] == 'ww'

def test_SNPMessage_Marshall():
	m = SNPMessage('x-vnd-sffjunkie.hiss')
	m.append('register', signature='sig', uid='1', title='ww')

	assert m.marshall() == 'SNP/3.0\r\nregister?signature=sig&title=ww&uid=1\r\nEND\r\n'

if __name__ == '__main__':
	test_SNPMessage_Blank()
	test_SNPMessage_Append()
	test_SNPMessage_Marshall()
