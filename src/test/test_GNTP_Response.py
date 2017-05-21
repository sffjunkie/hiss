# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

from hiss.handler.gntp.message import Response


def test_GNTPResponse_Create():
    _r = Response()


def test_GNTPResponse_marshal():
    r = Response()
    r.version = '1.0'
    r.status = 'OK'
    r.command = 'REGISTER'
    r.body['Origin-Machine-Name'] = 'OURAGAN'

    msg = r.marshal()
    # Unable to compare bytes as Response has a variable timestamp
    assert len(msg) == len('GNTP/1.0 -OK NONE\r\nResponse-Action: REGISTER\r\nOrigin-Machine-Name: OURAGAN\r\n') + len('X-Timestamp: YYYY-mm-dd hh:mm:ssZ\r\n')


def test_GNTPResponse_Unmarshal():
    r = Response()
    msg = b'GNTP/1.0 -OK NONE\r\nResponse-Action: REGISTER\r\nOrigin-Machine-Name: OURAGAN\r\n'
    r.unmarshal(msg)

    assert r.status == 'OK'
    assert r.command == 'register'
    