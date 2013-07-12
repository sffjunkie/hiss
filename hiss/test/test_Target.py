# Copyright 2009-2012, Simon Kennedy, python:sffjunkie.co.uk
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

def test_Create():
    t = Target()
    assert t.scheme == 'snp'
    assert t.host == '127.0.0.1'
    assert t.port == -1
    assert t.username == ''
    
    t = Target('gntp://')
    assert t.scheme == 'gntp'
    assert t.host == '127.0.0.1'
    
    t = Target('gntp://192.168.1.1')
    assert t.scheme == 'gntp'
    assert t.host == '192.168.1.1'
    
    t = Target('snp')
    assert t.scheme == 'snp'
    assert t.host == '127.0.0.1'

    t = Target('snp://192.168.1.1')
    assert t.scheme == 'snp'
    assert t.host == '192.168.1.1'

    t = Target('snp://wally@192.168.1.1')
    assert t.scheme == 'snp'
    assert t.host == '192.168.1.1'
    assert t.username == 'wally'
    assert t.port == -1

    t = Target('snp://wally@192.168.1.1:9000')
    assert t.scheme == 'snp'
    assert t.host == '192.168.1.1'
    assert t.username == 'wally'
    assert t.port == 9000

def test_String():
    t = Target('snp://wally@192.168.1.1:9000')
    assert str(t) == 'snp://192.168.1.1:9000'
    
def test_BadProtocol():
    with pytest.raises(TargetError):
        t = Target('wally')

if __name__ == '__main__':
    test_Create()
    test_String()
    test_BadProtocol()
