# Copyright 2009-2011, Simon Kennedy, python:sffjunkie.co.uk
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

from nose.tools import raises
from hiss.target import Target, TargetError

def testCreate():
    t = Target()
    t = Target('growl')
    t = Target('growl:127.0.0.1')
    t = Target('snarl')
    t = Target('snarl:127.0.0.1')

@raises(TargetError)
def testBadProtocol():
    t = Target('wally')

@raises(TargetError)
def testTooShort():
    t = Target('y')

def testSplit():
    t = Target('growl')
    assert t.protocol == 'growl'
    assert t.address == ''

    t = Target('growl:127.0.0.1')
    assert t.protocol == 'growl'
    assert t.address == '127.0.0.1'

    t = Target('snarl')
    assert t.protocol == 'snarl'
    assert t.address == ''

    t = Target('snarl:127.0.0.1')
    assert t.protocol == 'snarl'
    assert t.address == '127.0.0.1'

