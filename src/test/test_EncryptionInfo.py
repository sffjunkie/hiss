# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

import pytest

from hiss.encryption import EncryptionInfo

def test_EncryptionInfo_Init_BadInit():
    with pytest.raises(TypeError):
        _ei = EncryptionInfo()


def test_EncryptionInfo_Init_GoodInit():
    _ei = EncryptionInfo('AES', b'1111111111')


def test_EncryptionInfo_Init_BadAlgorithm():
    with pytest.raises(ValueError):
        _ei = EncryptionInfo('WALLY', b'1111111111')


def test_EncryptionInfo_Init_Algorithm_IsUpperCase():
    ei = EncryptionInfo('AES', b'1111111111')
    assert ei.algorithm == 'AES'


def test_EncryptionInfo_Init_Algorithm_AnyCase():
    ei = EncryptionInfo('aEs', b'1111111111')
    assert ei.algorithm == 'AES'


def test_EncryptionInfo_Init_ivBytes():
    ei = EncryptionInfo('aEs', b'1111111111')
    assert ei.iv == b'1111111111'


def test_EncryptionInfo_Init_ivStr():
    ei = EncryptionInfo('aEs', '1111111111')
    assert ei.iv == b'\x11\x11\x11\x11\x11'
    