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

from twisted.internet.defer import Deferred, DeferredList
from twisted.protocols.basic import LineReceiver

SNP_SCHEME = 'snp'
SNP_DEFAULT_PORT = 5233
SNP_DEFAULT_VERSION = '2.0'

SNARL_ERROR_FAILED = 101                # miscellaneous failure
#SNARL_ERROR_UNKNOWN_COMMAND            # specified command not recognised
#SNARL_ERROR_TIMED_OUT                  # Snarl took too long to respond
SNARL_ERROR_BAD_SOCKET = 106            # invalid socket (or some other socket-related error)
SNARL_ERROR_BAD_PACKET = 107            # badly formed request
SNARL_ERROR_INVALID_ARG = 108           # R2.4B4: arg supplied was invalid
SNARL_ERROR_ARG_MISSING = 109           # required argument missing
#SNARL_ERROR_SYSTEM                     # internal system error
SNARL_ERROR_ACCESS_DENIED = 121

BOOL_MAPPING = {
	True: '1',
	'true': '1',
	'yes': '1',
	False: '0',
	'false': '0',
	'no': '0',
}

class SNPError(Exception):
	pass


class Command(object):
	def __init__(self, name='', parameters={}):
		self.name = name
		self.parameters = parameters


class SNPRequest(object):
	def __init__(self, version=SNP_DEFAULT_VERSION, **kwargs):
		self.version = version
		self.commands = []
		self.response = False
		self.port = SNP_DEFAULT_PORT
	
	def append(self, name, **kwargs):
		"""Append a command to the message
		
		SNPRequest.append('register', signature='sig', uid='1', title='ww')"""
		
		if self.version == '2.0' and len(self.commands) == 1:
			raise ValueError('Version 2.0 messages don\'t support multiple commands')
		
		self.commands.append(Command(name, kwargs))
	
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

	def _marshall_command(self, command):
		data = ''

		names = command.parameters.keys()
		names.sort()

		for name in names:
			value = command.parameters[name]
			value = value.replace('\r\n', '\\n')
			value = value.replace('\n', '\\n')
			value = value.replace('&', '&&')
			value = value.replace('=', '==')
			data += '%s=%s&' % (name, value)
			
		data = data[:-1]
		return '%s?%s' % (command.name, data)

	def _marshall_20(self):
		data = self._marshall_command(self.commands[0])
		return 'snp://%s\r' % data
	
	def _marshall_30(self):
		data = 'SNP/3.0\r\n'
		for command in self.commands:
			data += '%s\r\n' % self._marshall_command(command)

		data += 'END\r\n'
		return data 

	def _unmarshall_20(self, data):
		pass

	def _unmarshall_30(self, data):
		pass

	def encode64(self, data):
		data = base64.encode(data)
		data = data.replace('\r\n', '#')
		data = data.replace('=', '%')
		return data


class SNPResponse(object):
	def __init__(self):
		self.version = SNP_DEFAULT_VERSION
		self.status_code = 200
		self.description = ''
		self.data = ''
	
	def unmarshall(self, data):
		if data.startswith('SNP/2.0'):
			self._unmarshall2(data)
		elif data.startswith('SNP/3.0'):
			self._unmarshall3(data)
	
	def _unmarshall2(self, data):
		elems = data.split('/')
		self.version = elems[1]
		self.status_code = int(elems[2])
		self.description = elems[3]
		
		if len(elems) == 5:
			self.data = elems[4]

	def _unmarshall3(self, data):
		lines = data.split('\r\n')
		
		header = lines[0]
		if header[:3] != 'SNP':
			raise SNPError('Invalid SNP message format')

		try:
			items = header.split('/')
			if len(items) == 3:
				self.response = True
				self.status_code = int(items[1])
			
			signature = items[0]
	
			format_, version = signature.split('/')
			if not(format_ == 'SNP' or version == '3.0'):
				raise SNPError('Unable to handle version %s messages' % items[1])
		except:
			raise SNPError('Invalid header format: %s' % header)


class RegisterRequest(object):
	def __init__(self, notifier, version=SNP_DEFAULT_VERSION):
		commands = []

		parameters = {}
		parameters['app-sig'] = notifier.signature
		parameters['password'] = notifier.nid
		c = Command('register', parameters)
		commands.append(c)

		for notification in notifier.notifications:
			parameters = {}
			parameters['app-sig'] = notifier.signature
			parameters['password'] = notifier.nid
			parameters['id'] = notification.class_id
			parameters['name'] = notification.name
			parameters['enabled'] = BOOL_MAPPING[notification.enabled]
				
			c = Command('addClass', parameters)
			commands.append(c)
		
		if version == '2.0':
			self._requests = []
			request = SNPRequest(version)

			
			request.commands.append(c)


class SNP(LineReceiver):
	def __init__(self):
		self._success = False
		
	def register(self, notifier, target):
		request = SNPRequest(notifier)
		message = request.marshall()
		return self._send(message, target)

	def _send(self, message, target):
		self.d = Deferred()
		self.response = {}
		self.transport.write(message, (target.host, target.port))
		return self.d

	def lineReceived(self, data):
		msg = SNPResponse()
		msg.unmarshall(data)

	