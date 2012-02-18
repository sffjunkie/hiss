# Copyright 2009-2012, Simon Kennedy, python@sffjunkie.co.uk
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

import base64
from collections import namedtuple

from twisted.internet.defer import Deferred
from twisted.protocols.basic import LineReceiver

SNP_PORT = 5233

class SNPError(Exception):
	pass


class SNPMessage(object):
	def __init__(self, signature):
		self.signature= signature
		self.commands = []
		self.response = False
	
	_Command = namedtuple('Command', 'name, parameters')

	def append(self, name, **kwargs):
		"""Append a command to the message
		
		SNPMessage.append('register', signature='sig', uid='1', title='ww')"""
		
		self.commands.append(self._Command(name, kwargs))
	
	def marshall(self):
		data = 'SNP/3.0\r\n'
		for command in self.commands:
			data += '%s?' % command.name

			names = []
			for name in command.parameters.keys():
				names.append(name)
			names.sort()

			params = ''			
			for name in names:
				value = command.parameters[name]
				value = value.replace('\r\n', '\\n')
				value = value.replace('\n', '\\n')
				value = value.replace('&', '&&')
				value = value.replace('=', '==')
				params += '&%s=%s' % (name, value)
				
			data += params[1:]
			data += '\r\n'

		data += 'END\r\n'

		return data

	def unmarshall(self, data):
		lines = data.split('\r\n')
		
		header = lines[0]
		if header[:3] != 'SNP':
			raise SNPError('Invalid SNP message format')

		try:
			items = header.split(' ')
			if len(items) == 3:
				self.response = True
				status = items[1]
			
			signature = items[0]
	
			format_, version = signature.split('/')
			if not(format_ == 'SNP' or version == '3.0'):
				raise SNPError('Unable to handle version %s messages' % items[1])
		except:
			raise SNPError('Invalid header format: %s' % header)
		

	def encode64(self, data):
		data = base64.encode(data)
		data = data.replace('\r\n', '#')
		data = data.replace('=', '%')
		return data
	

class SNP(LineReceiver):
	def __init__(self):
		self._success = False
		
	def register(self):
		pass

	def send(self, message, host):
		self.d = Deferred()
		self.response = {}
		self.transport.write(message.marshall(), (host, SNP_PORT))
		return self.d

	def lineReceived(self, data):
		if data.startswith('SNP/3.0'):
			items = data.split(' ')
			self._success = (items[1].trim('\r\n') == 'OK')
		elif data == 'END\r\n':
			if self._success:
				self.d.callback(self.response)
			else:
				self.d.errback(self.response)
		else:
			items = data.split(':')
			self.response[items[0]] = items[1]
	
	