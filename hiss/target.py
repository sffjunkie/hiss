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

import urlparse

from hiss.protocol.snp import SNP, SNP_SCHEME
from hiss.protocol.gntp import GNTP, GNTP_SCHEME

for s in [SNP_SCHEME, GNTP_SCHEME]:
    if s not in urlparse.uses_relative:
        urlparse.uses_relative.append(s)
        
    if s not in urlparse.uses_netloc:
        urlparse.uses_netloc.append(s)

    if s not in urlparse.uses_params:
        urlparse.uses_params.append(s)

    if s not in urlparse.uses_query:
        urlparse.uses_query.append(s)

class Target(object):
    def __init__(self, protocol='', **kwargs):
        if protocol == '':
            protocol = '%s:///' % SNP_SCHEME
        
        self.port = -1
        self.username = ''
        self.password = ''
        
        result = urlparse.urlparse(protocol)
        if result.scheme != '':
            self.protocol = result.scheme
            
            host = ''
            if result.netloc != '':
                try:
                    userpass, host = result.netloc.split('@')
                    try:
                        self.username, self.password = userpass.split(':')
                    except:
                        self.username = userpass
                        self.password = ''
                        
                    try:
                        host, port = host.split(':')
                    except:
                        host = host
                        port = -1
                except:
                    host = result.netloc
                    port = -1
                    
                host = host
            else:
                host = '127.0.0.1'
                port = -1
                
            self.host = host
            self.port = int(port)
        elif protocol.startswith(SNP_SCHEME):
            self.protocol = SNP_SCHEME
            self.host = protocol[len(SNP_SCHEME):].lstrip(':')
        elif protocol.startswith(GNTP_SCHEME):
            self.protocol = GNTP_SCHEME
            self.host = protocol[len(GNTP_SCHEME):].lstrip(':')
        else:
            self.protocol = protocol
            
        if self.protocol not in [SNP_SCHEME, GNTP_SCHEME]:
            raise TargetError('Unknown protocol %s' % protocol)

        if self.protocol == SNP_SCHEME:
            self.handler = SNP()
        elif self.protocol == GNTP_SCHEME:
            self.handler = GNTP()
        
        self.host = kwargs.get('host', self.host)
        self.port = kwargs.get('port', self.port)
        self.username = kwargs.get('username', self.username)
        self.password = kwargs.get('password', self.password)
        
        if self.host == '':
            self.host = '127.0.0.1'

    def __repr__(self):
        return '%s://%s:%d' % (self.protocol, self.host, self.port)

class TargetError(Exception):
    pass
