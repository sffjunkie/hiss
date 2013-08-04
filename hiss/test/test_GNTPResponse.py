# Copyright 2009-2012, Simon Kennedy, code@sffjunkie.co.uk
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

from hiss.handler.gntp import _Response

def test_GNTPResponse_Create():
    _r = _Response()

def test_GNTPResponse_Marshall():
    r = _Response()
    r.version = '1.0'
    r.type = 'OK'
    r.command = 'REGISTER'
    r.header['Origin-Machine-Name'] = 'OURAGAN'
    
    msg = r.marshall()
    assert msg == 'GNTP/1.0 -OK NONE\r\nResponse-Action: REGISTER\r\nOrigin-Machine-Name: OURAGAN\r\n'


def test_GNTPResponse_Unmarshall():
    r = _Response()
    msg = 'GNTP/1.0 -OK NONE\r\nResponse-Action: REGISTER\r\nOrigin-Machine-Name: OURAGAN\r\n'
    r.unmarshall(msg)
    
    assert r.type == 'OK'
    assert r.command == 'REGISTER'


if __name__ == '__main__':
    test_GNTPResponse_Create()
    test_GNTPResponse_Marshall()
    test_GNTPResponse_Unmarshall()
    