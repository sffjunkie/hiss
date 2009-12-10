import types
from nose.tools import raises

from hiss import Notifier, Notification
from hiss.target import Target

def testCreate():
    ns = [Notification('wally')]
    n = Notifier(ns)

def testRegister():
    ns = [Notification('wally')]
    n = Notifier(notifications=ns)
    n.register()
    
def testCreate():
    ns = [Notification('wally')]
    a = Notifier(ns)

def testSend():
    ns = [Notification('wally')]
    n = Notifier(notifications=ns)
    t = Target('growl@127.0.0.1')
    n.send('wally', t)
    
