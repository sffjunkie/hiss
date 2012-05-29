# Copyright 2009-2012, Simon Kennedy, code@sffjunkie.co.uk
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

from twisted.internet import reactor

from hiss.target import Target
from hiss.protocol.snp import SNP, SNPRequest

def test_Connection():
    target = Target('snp://192.168.3.111')    
    factory = SNP()
    factory.add_target(target)
    reactor.callLater(5, reactor.stop)
    reactor.run()

def test_BadConnection():
    target = Target('snp://192.168.3.111')    
    factory = SNP()
    factory.add_target(target)
    reactor.callLater(5, reactor.stop)
    reactor.run()

def test_Hello():
    target = Target()
    factory = SNP()
    factory.add_target(target)
    
    reactor.connectTCP(target.host, target.port, factory)

if __name__ == '__main__':
    test_BadConnection()
    test_Hello()
