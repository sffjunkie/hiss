# Copyright 2009-2011, Simon Kennedy, python@sffjunkie.co.uk
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

# Part of 'hiss' the Python notification library

import hashlib
import urllib2
import base64

class Resource(object):
    def __init__(self, uri='', data=None):
        self.uri = uri
        self.data = data

    def load(self):
        f = urllib2.urlopen(self.uri)
        self.data = f.read(-1)
        
    def res_id(self):
        if self.uri != '':
            return self.uri
        elif self.data is not None:
            return hashlib.md5().hexdigest()
        else:
            return ''

    def md5(self):
        if self.data is not None:
            return hashlib.md5(self.data)
        else:
            raise ValueError('Cannot compute md5: No data available')

    def base64(self):
        if self.data is not None:
            return base64.b64encode(self.data)
        else:
            raise ValueError('Cannot encode base 64: No data available')

    def __len__(self):
        return len(self.data)
        

class Icon(Resource):
    pass
