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

# Part of 'hiss' the Python notification library

import urlparse

SNP_SCHEME = 'snp'
GNTP_SCHEME = 'gntp'
XBMC_SCHEME = 'xbmc'

DEFAULT_SCHEME = SNP_SCHEME

__all__ = ['TargetError', 'Target']

for s in [SNP_SCHEME, GNTP_SCHEME, XBMC_SCHEME]:
    if s not in urlparse.uses_relative:
        urlparse.uses_relative.append(s)
        
    if s not in urlparse.uses_netloc:
        urlparse.uses_netloc.append(s)

    if s not in urlparse.uses_params:
        urlparse.uses_params.append(s)

    if s not in urlparse.uses_query:
        urlparse.uses_query.append(s)


class TargetError(Exception):
    pass


class Target(object):
    def __init__(self, url='', **kwargs):
        """Create a new target for notifications.
        
        Targets are specified using a URL like string of the form ::
        
            scheme://[username@]host[:port]
        
        where scheme is currently one of ``snp`` or ``gntp``.
        
        All values can be overridden using named parameters.
        """ 
        
        if url == '':
            url = '%s:///' % DEFAULT_SCHEME
        
        self.port = -1
        self.username = ''
        
        result = urlparse.urlparse(url)
        if result.scheme != '':
            self.scheme = result.scheme
            
            host = ''
            if result.netloc != '':
                try:
                    self.username, hostport = result.netloc.split('@')
                except:
                    hostport = result.netloc
                        
                try:
                    host, port = hostport.split(':')
                except:
                    host = hostport
                    port = -1
            else:
                host = '127.0.0.1'
                port = -1
                
            self.host = host
            self.port = int(port)
        elif url.startswith(SNP_SCHEME):
            self.scheme = SNP_SCHEME
            self.host = url[len(SNP_SCHEME):].lstrip(':')
        elif url.startswith(GNTP_SCHEME):
            self.scheme = GNTP_SCHEME
            self.host = url[len(GNTP_SCHEME):].lstrip(':')
        elif url.startswith(XBMC_SCHEME):
            self.scheme = XBMC_SCHEME
            self.host = url[len(XBMC_SCHEME):].lstrip(':')
        else:
            self.scheme = url
            
        if self.scheme not in [SNP_SCHEME, GNTP_SCHEME, XBMC_SCHEME]:
            raise TargetError('Unknown protocol %s' % url)

        # Override with any parameters passed
        self.host = kwargs.get('host', self.host)
        self.port = kwargs.get('port', self.port)
        self.username = kwargs.get('username', self.username)
        
        if self.host == '' or self.host == 'localhost':
            self.host = '127.0.0.1'
        
        self.enabled = True
        self.handler = None
        self.protocol_version = ''

    address = property(lambda self: (self.host, self.port))

    def __repr__(self):
        return '%s://%s:%d' % (self.scheme, self.host, self.port)

    def __eq__(self, other):
        """Tests that 2 targets are equal when ignoring username and password.
        """ 
        
        return (self.scheme, self.host, self.port, self.username) == \
               (other.scheme, other.host, other.port, other.username)
