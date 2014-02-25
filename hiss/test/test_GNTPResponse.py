# Copyright 2013-2014, Simon Kennedy, code@sffjunkie.co.uk
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

from hiss.handler.gntp import Response

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
    