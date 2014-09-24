# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

SNP_SCHEME = 'snp'
GNTP_SCHEME = 'gntp'
XBMC_SCHEME = 'xbmc'

PROWL_SCHEME = 'prowl'
PUSHOVER_SCHEME = 'po'
PUSHBULLET_SCHEME = 'pb'

DEFAULT_SCHEME = SNP_SCHEME
URL_SCHEMES = [SNP_SCHEME, GNTP_SCHEME, XBMC_SCHEME]
TOKEN_SCHEMES = [PROWL_SCHEME, PUSHOVER_SCHEME, PUSHBULLET_SCHEME]
ALL_SCHEMES = URL_SCHEMES + TOKEN_SCHEMES
