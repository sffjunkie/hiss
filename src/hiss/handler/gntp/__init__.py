from hiss.exception import HissError

class GNTPError(HissError):
    pass

GNTP_SCHEME = 'gntp'
GNTP_DEFAULT_PORT = 23053
GNTP_BASE_VERSION = '1.0'

DEFAULT_HASH_ALGORITHM = 'SHA256'
ENCRYPTION_ALGORITHM = 'AES'
