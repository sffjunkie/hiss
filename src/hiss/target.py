# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

import hiss.schemes
import hiss.exception
import hiss.utility

__all__ = ['Target']

for s in hiss.schemes.ALL_SCHEMES:
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
    
    Currently the following target schemes are supported
    
    =========  ================================
    ``snp``    Snarl Network Protocol
    ``gtnp``   Growl Network Transfer Protocol
    ``xbmc``   XBMC
    ``prowl``  Prowl
    ``po``     Pushover
    =========  ================================

    For the ``snp``, ``gntp`` and ``xbmc`` schemes, targets are specified
    using a URL like string of the form ::

        scheme://[username:[password@]]host[:port]

    If no port number is specified then the default port for the target type
    will be used.
    
    For the ``prowl`` and ``po`` schemes, targets are specified using
    an API Key with an optional filter
    
        scheme://apikey[:filter]
    """
    def __init__(self, url='', **kwargs):
        if url == '':
            url = '%s:///' % hiss.schemes.DEFAULT_SCHEME

        self.username = None
        self.password = None
        self.port = -1

        result = urlparse.urlparse(url)
        if result.scheme != '':
            self.scheme = result.scheme

            host = ''
            if result.netloc != '':
                try:
                    userpass, hostport = result.netloc.split('@')
                    
                    try:
                        self.username, self.password = userpass.split(':', maxsplit=1)
                    except:
                        self.username = None
                        self.password = userpass
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
        else:
            for scheme in hiss.schemes.ALL_SCHEMES:
                if url.startswith(scheme):
                    self.scheme = scheme
                    self.host = url[len(scheme):].lstrip(':')
                    break
            else:
                self.scheme = url
                self.host = ''

        if self.scheme not in hiss.schemes.ALL_SCHEMES:
            raise hiss.exception.TargetError('Unknown protocol scheme %s' % url)

        # Override with any parameters passed
        self.host = kwargs.get('host', self.host)
        self.port = kwargs.get('port', self.port)
        self.username = kwargs.get('username', self.username)
        self.password = kwargs.get('password', self.password)

        if self.host == '' or self.host == 'localhost':
            self.host = '127.0.0.1'

        self.handler = None
        self.protocol_version = ''

    @property
    def address(self):
        """Return the target address as a (host, port) tuple"""
        
        return (self.host, self.port)

    @property
    def auth(self):
        """Return the target authorisation info as a
        (username, password) tuple
        """
        return (self.username, self.password)

    @property    
    def is_remote(self):
        """Return True if host is on a remote machine.

        This is used to determine if the password information needs to be
        sent with each message.
        """

        return self.host not in hiss.utility.local_hosts()

    def __repr__(self):
        if self.scheme in hiss.schemes.URL_SCHEMES:
            return '%s://%s:%d' % (self.scheme, self.host, self.port)
        else:
            return '%s://%s' % (self.scheme, self.host)

    def __eq__(self, other):
        """Tests that 2 targets are equal ignoring the password.""" 

        return (self.scheme, self.host, self.port) == \
               (other.scheme, other.host, other.port)
