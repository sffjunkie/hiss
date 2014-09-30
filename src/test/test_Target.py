# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

import pytest
from hiss.target import Target
from hiss.exception import TargetError

def test_Target_Init_EmptyTarget():
    t = Target()
    assert t.scheme == 'snp'
    assert t.host == '127.0.0.1'
    assert t.port == -1
    assert t.username is None
    assert t.password is None

def test_GNTPTarget_Init_SchemeOnly():
    t = Target('gntp://')
    assert t.scheme == 'gntp'
    assert t.host == '127.0.0.1'

def test_GNTPTarget_Init_Host():
    t = Target('gntp://192.168.1.1')
    assert t.scheme == 'gntp'
    assert t.host == '192.168.1.1'

def test_SNPTarget_Init_Empty():
    t = Target('snp')
    assert t.scheme == 'snp'
    assert t.host == '127.0.0.1'

def test_SNPTarget_Init_HostOnly():
    t = Target('snp://192.168.1.1')
    assert t.scheme == 'snp'
    assert t.host == '192.168.1.1'

def test_Target_Init_WithUsername():
    t = Target('snp://wally@192.168.1.1')
    assert t.scheme == 'snp'
    assert t.host == '192.168.1.1'
    assert t.username == 'wally'
    assert t.port == -1

def test_Target_Init_WithUsernameAndPort():
    t = Target('snp://wally@192.168.1.1:8080')
    assert t.scheme == 'snp'
    assert t.host == '192.168.1.1'
    assert t.username == 'wally'
    assert t.port == 8080

def test_Target_Init_WithPassword():
    t = Target('snp://:wally@192.168.1.1')
    assert t.scheme == 'snp'
    assert t.host == '192.168.1.1'
    assert t.password == 'wally'
    assert t.port == -1

def test_Target_Init_WithPasswordAndPort():
    t = Target('snp://:wally@192.168.1.1:9000')
    assert t.scheme == 'snp'
    assert t.host == '192.168.1.1'
    assert t.password == 'wally'
    assert t.port == 9000

def test_Target_Init_WithUsernamePasswordAndPort():
    t = Target('snp://user:wally@192.168.1.1:9000')
    assert t.scheme == 'snp'
    assert t.host == '192.168.1.1'
    assert t.username == 'user'
    assert t.password == 'wally'
    assert t.port == 9000

def test_Target_String_UsernamePasswordIsRemoved():
    t = Target('snp://wally:wally@192.168.1.1:9000')
    assert str(t) == 'snp://192.168.1.1:9000'

def test_Target_IsRemote():
    t = Target('snp://wally@192.168.1.1:9000')
    assert t.is_remote

def test_BadProtocol():
    with pytest.raises(TargetError):
        t = Target('wally')

def test_ProwlTarget_Init():
    t = Target('prowl://adkhkahs')
    assert t.scheme == 'prowl'
    assert t.host == 'adkhkahs'

def test_PushoverTarget_Init():
    t = Target('po://adkhkahs')
    assert t.scheme == 'po'
    assert t.host == 'adkhkahs'

def test_PushbulletTarget_Init():
    t = Target('pb://adkhkahs')
    assert t.scheme == 'pb'
    assert t.host == 'adkhkahs'
