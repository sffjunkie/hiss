# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

"""
    Currently the following schemes are supported

    =========  ================================
    ``gtnp``   Growl Network Transfer Protocol
    ``pb``     Pushbullet
    ``po``     Pushover
    ``prowl``  Prowl
    ``snp``    Snarl Network Protocol
    ``kodi``   KODI
    =========  ================================

    For the ``snp``, ``gntp`` and ``kodi`` schemes, targets are specified
    using a URL like string of the form ::

        scheme://[username:[password@]]host[:port]

    If no port number is specified then the default port for the target type
    will be used.

    For the Prowl, Pushbullet and Pushover schemes, targets are specified using
    an API Key with an optional filter to target specific devices ::

        scheme://apikey[:filter]
"""

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

SNP_SCHEME = 'snp'
GNTP_SCHEME = 'gntp'
KODI_SCHEME = 'kodi'

PROWL_SCHEME = 'prowl'
PUSHBULLET_SCHEME = 'pb'
PUSHOVER_SCHEME = 'po'

DEFAULT_SCHEME = SNP_SCHEME
URL_SCHEMES = [SNP_SCHEME, GNTP_SCHEME, KODI_SCHEME]
TOKEN_SCHEMES = [PROWL_SCHEME, PUSHOVER_SCHEME, PUSHBULLET_SCHEME]
ALL_SCHEMES = URL_SCHEMES + TOKEN_SCHEMES

def add_urlparse_schemes():
    """Allow urlparse to understand our protocol schemes"""

    for s in hiss.schemes.ALL_SCHEMES:
        if s not in urlparse.uses_relative:
            urlparse.uses_relative.append(s)

        if s not in urlparse.uses_netloc:
            urlparse.uses_netloc.append(s)

        if s not in urlparse.uses_params:
            urlparse.uses_params.append(s)

        if s not in urlparse.uses_query:
            urlparse.uses_query.append(s)
