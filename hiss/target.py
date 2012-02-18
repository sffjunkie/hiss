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

# Part of 'hiss' the Python notification library

from hiss.protocol.snp import SNP
from hiss.protocol.gtnp import GNTP

class Target(object):
    def __init__(self, protocol='snarl', *args, **kwargs):
        if protocol == 'snarl': 
            self._protocol = SNP()
        elif protocol == 'gntp':
            self._protocol = GNTP()

        self._host = ''
        self._password = ''
        self._options = {}
        
        for name, value in kwargs.items():
            if name == 'host':
                self._host = value
            elif name == 'password':
                self._password = value
            else:
                self._options[name] = value

    def send(self, notification):
        def success(result):
            pass
        
        def fail(failure):
            pass
        
        d = self._protocol.send(notification, self._host)
        d.addCallback(success)
        d.addErrback(fail)

