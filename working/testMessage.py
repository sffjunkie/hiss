# Copyright 2009-2011, Simon Kennedy, python@sffjunkie.co.uk
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

# Part of 'hiss' the Python notification library

import types
from nose.tools import raises
from hiss import Notifier, Notification
from hiss.message import *

@raises(MessageError)
def testMessageVersionError():
    m = Message()
    m.version = '2.1'

def testMessageVersion():
    m = Message()
    m.version = '1.0'

@raises(MessageError)
def testMessageMessageTypeError():
    m = Message()
    m.message_type = 'WALLY'
    
def testMessageMessageType():
    m = Message()
    m.message_type = 'REGISTER'
    m.message_type = 'NOTIFY'
    m.message_type = 'SUBSCRIBE'
    m.message_type = '-OK'
    m.message_type = '-ERROR'
    m.message_type = '-CALLBACK'
    assert m.message_type == '-CALLBACK'

@raises(MessageError)
def testMessageEncryptAlgoError():
    m = Message()
    m.encrypt_algorithm = 'WALLY'
    
def testMessageEncryptAlgo():
    m = Message()
    m.encrypt_algorithm = 'NONE'
    m.encrypt_algorithm = 'AES'
    m.encrypt_algorithm = 'DES'
    m.encrypt_algorithm = '3DES'
    assert m.encrypt_algorithm == '3DES'

@raises(MessageError)
def testMessageHashAlgoError():
    m = Message()
    m.hash_algorithm = 'WALLY'
    
def testMessageHashAlgo():
    m = Message()
    m.hash_algorithm = 'MD5'
    assert m.hash_algorithm == 'MD5'
    m.hash_algorithm = 'SHA1'
    assert m.hash_algorithm == 'SHA1'
    m.hash_algorithm = 'SHA256'
    assert m.hash_algorithm == 'SHA256'
    m.hash_algorithm = 'SHA512'
    assert m.hash_algorithm == 'SHA512'

@raises(KeyError)
def testMessageHeadersError():
    m = Message()
    m.headers['An-Invalid-Header'] = 'Test App'

def testMessageHeaders():
    m = Message()
    m.headers['Application-Name'] = 'Test App'

def testMessageClasses():
    m = RegisterMessage()
    m = NotifyMessage()
    m = SubscribeMessage()
    m = OKMessage()
    m = ErrorMessage()
    m = CallbackMessage()
    
def testCustomHeader():
    m = Message()
    m.add_header('X-Hiss-Target', 'gfw@127.0.0.1')
    
def testInfoLine():
    m = Message()
    m.info_line = 'GNTP/1.0 NOTIFY NONE'
    assert m.version == '1.0'
    assert m.encrypt_algorithm == 'NONE'

