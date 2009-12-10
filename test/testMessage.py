import types
from nose.tools import raises
from hiss import Notifier, Notification
from hiss.message import *

@raises(ValueError)
def testMessageVersionError():
    m = Message()
    m.version = '2.1'

def testMessageVersion():
    m = Message()
    m.version = '1.0'

@raises(ValueError)
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

@raises(ValueError)
def testMessageEncryptTypeError():
    m = Message()
    m.encrypt_type = 'WALLY'
    
def testMessageEncryptType():
    m = Message()
    m.encrypt_type = 'NONE'
    m.encrypt_type = 'AES'
    m.encrypt_type = 'DES'
    m.encrypt_type = '3DES'
    assert m.encrypt_type == '3DES'

@raises(ValueError)
def testMessageHashTypeError():
    m = Message()
    m.hash_type = 'WALLY'
    
def testMessageHashType():
    m = Message()
    m.hash_type = 'MD5'
    m.hash_type = 'SHA1'
    m.hash_type = 'SHA256'
    m.hash_type = 'SHA512'
    assert m.hash_type == 'SHA512'

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

