# Copyright 2013-2014, Simon Kennedy, python:sffjunkie.co.uk
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

import pytest
from hiss.target import Target, TargetError

def test_Target_Init_EmptyTarget():
    t = Target()
    assert t.scheme == 'snp'
    assert t.host == '127.0.0.1'
    assert t.port == -1
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

def test_Target_Init_WithPassword():
    t = Target('snp://wally@192.168.1.1')
    assert t.scheme == 'snp'
    assert t.host == '192.168.1.1'
    assert t.password == 'wally'
    assert t.port == -1

def test_Target_Init_WithPasswordAndPort():
    t = Target('snp://wally@192.168.1.1:9000')
    assert t.scheme == 'snp'
    assert t.host == '192.168.1.1'
    assert t.password == 'wally'
    assert t.port == 9000

def test_Target_String_PasswordIsRemoved():
    t = Target('snp://wally@192.168.1.1:9000')
    assert str(t) == 'snp://192.168.1.1:9000'

def test_Traget_IsRemote():
    t = Target('snp://wally@192.168.1.1:9000')
    assert t.is_remote

def test_BadProtocol():
    with pytest.raises(TargetError):
        t = Target('wally')
