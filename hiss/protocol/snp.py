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
from urllib import quote
from collections import namedtuple

from twisted.internet.defer import Deferred
from twisted.protocols.basic import LineReceiver

SNP_SCHEME = 'snp'
SNP_DEFAULT_PORT = 5233
SNP_DEFAULT_VERSION = '2.0'

class SNPError(Exception):
	pass


class SNPRequest(object):
	def __init__(self, command, version=SNP_DEFAULT_VERSION, **kwargs):
		self.command = command
		self.version = version
		self.commands = []
		self.response = False
		self.port = SNP_DEFAULT_PORT
	
	_Command = namedtuple('Command', 'name, parameters')

	def append(self, name, **kwargs):
		"""Append a command to the message
		
		SNPRequest.append('register', signature='sig', uid='1', title='ww')"""
		
		if self.version == '2.0' and len(self.commands) == 1:
			raise ValueError('Version 2.0 messages don\'t support multiple commands')
		
		self.commands.append(self._Command(name, kwargs))
	
	def marshall(self):
		if self.version == '2.0':
			return self._marshall_20()
		elif self.version == '3.0':
			return self._marshall_30()
		elif self.version == '1.0':
			raise ValueError('SNP protocol version 1.0 is unsupported.')
	
	def unmarshall(self, data):
		if data.startswith('SNP/2.0'):
			return self._unmarshall_20(data)
		elif data.startswith('SNP/3.0'):
			return self._unmarshall_30(data)
		else:
			raise ValueError('Unsupported response version.')

	def _marshall_20(self):
		command = self.commands[0]
		
		parameters = ''
		for parameter, value in command.parameters.items():
			parameters += '?%s=%s' % (parameter, quote(value))
			
		return 'snp://%s%s\r' % (command.name, parameters)
	
	def _marshall_30(self):
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

		return data + 'END\r\n'

	def _unmarshall_20(self, data):
		pass

	def _unmarshall_30(self, data):
		lines = data.split('\r\n')
		
		header = lines[0]
		if header[:3] != 'SNP':
			raise SNPError('Invalid SNP message format')

		try:
			items = header.split('/')
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

class RegisterRequest(SNPRequest):
	def __init__(self):
		SNPRequest.__init__(self)
	
	def append(self, info):
		pass

class SNP(LineReceiver):
	def __init__(self):
		self._success = False
		
	def register(self):
		pass

	def send(self, message, host):
		self.d = Deferred()
		self.response = {}
		self.transport.write(message.marshall(), (host, SNP_DEFAULT_PORT))
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
	
	