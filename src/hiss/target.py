# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

from hiss.exception import TargetError
from hiss.utility import local_hosts

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


class Target(object):
    """A target for notifications.

    Targets are specified using a URL like string of the form ::

        scheme://[password@]host[:port]

    where scheme is one of ``snp``, ``gntp`` or ``xbmc``.

    If no port number is specified then the default port for the target type will be used

    All values can be specified using named parameters.
    """

    def __init__(self, url='', **kwargs):
        if url == '':
            url = '%s:///' % DEFAULT_SCHEME

        self.password = None
        self.port = -1

        result = urlparse.urlparse(url)
        if result.scheme != '':
            self.scheme = result.scheme

            host = ''
            if result.netloc != '':
                try:
                    self.password, hostport = result.netloc.split('@')
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
        self.password = kwargs.get('password', self.password)

        if self.host == '' or self.host == 'localhost':
            self.host = '127.0.0.1'

        self.enabled = True
        self.handler = None
        self.protocol_version = ''

    @property
    def address(self):
        """Return the target address as a (host, port) tuple"""
        
        return (self.host, self.port)

    @property    
    def is_remote(self):
        """Return True if host is on a remote machine.

        This is used to determine if the password information needs to be sent with each
        message.
        """

        return self.host not in local_hosts()

    def __repr__(self):
        return '%s://%s:%d' % (self.scheme, self.host, self.port)

    def __eq__(self, other):
        """Tests that 2 targets are equal ignoring the password.
        """ 

        return (self.scheme, self.host, self.port) == \
               (other.scheme, other.host, other.port)
