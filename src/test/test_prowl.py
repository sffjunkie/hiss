# -*- coding: utf-8 -*-
# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

import os
import sys
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hiss.handler.prowl import ProwlResponse

SUCCESS_STR = """<?xml version="1.0" encoding="UTF-8"?>
<prowl>
    <success code="200" remaining="REMAINING" resetdate="TIMESTAMP"
        />
</prowl>"""

FAILURE_STR = """<?xml version="1.0" encoding="UTF-8"?>
<prowl>
    <error code="400">ERRORMESSAGE</error>
</prowl>"""


def test_ProwlResponse_Success():
    r = ProwlResponse(SUCCESS_STR)

    assert r.status_code == 200
    assert r.remaining == 'REMAINING'
    assert r.resetdate == 'TIMESTAMP'


def test_ProwlResponse_Failure():
    r = ProwlResponse(FAILURE_STR)

    assert r.status_code == 400
    assert r.reason == 'ERRORMESSAGE'
