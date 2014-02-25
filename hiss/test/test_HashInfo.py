import hashlib
from binascii import hexlify

from hiss.hash import HashInfo, generate_hash

def test_HashInfo_Init():
    key_hash = b'aabbccdd'
    salt = b'11223344'

    _h = HashInfo('SHA256', key_hash, salt)

def test_HashInfo_Str():
    key_hash = b'aabbccdd'
    salt = b'11223344'

    h = HashInfo('SHA256', key_hash, salt)

    expected = 'SHA256:%s.%s' % (hexlify(key_hash).decode('UTF-8'), hexlify(salt).decode('UTF-8'))
    assert str(h) == expected

def test_HashInfo_HashCalculation():
    password = 'testtest'
    h = generate_hash(password)

    key_basis = password.encode('UTF-8') + h.salt
    key = hashlib.sha256(key_basis).digest()
    key_hash = hashlib.sha256(key).digest()

    assert key_hash == h.key_hash
    