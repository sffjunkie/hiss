from nose.tools import raises
from hiss.target import Target
from hiss.protocol.gntp import GNTPMessage
from hiss.protocol.growl import GrowlMessage
from hiss.protocol.snarl import SnarlMessage
from hiss.protocol.snp import SNPMessage

def testCreate():
    t = Target('growl')
    t = Target('growl@127.0.0.1')
    t = Target('snarl')
    t = Target('snarl@127.0.0.1')

@raises(ValueError)
def testCreateFail():
    t = Target('wally')

def testSplit():
    t = Target('growl')
    assert t.protocol == 'growl'
    assert t.address == ''

    t = Target('growl@127.0.0.1')
    assert t.protocol == 'growl'
    assert t.address == '127.0.0.1'

    t = Target('snarl')
    assert t.protocol == 'snarl'
    assert t.address == ''

    t = Target('snarl@127.0.0.1')
    assert t.protocol == 'snarl'
    assert t.address == '127.0.0.1'

def testMessage():
    t = Target('growl')
    assert issubclass(t.message, GrowlMessage)

    t = Target('growl@127.0.0.1')
    assert issubclass(t.message, GNTPMessage)

    t = Target('snarl')
    assert issubclass(t.message, SnarlMessage)

    t = Target('snarl@127.0.0.1')
    assert issubclass(t.message, SNPMessage)
    
