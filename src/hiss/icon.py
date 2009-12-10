# Copyright 2009, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

import hashlib
import urlparse

class Icon(object):
    def __init__(self, resource=''):
        self._resource = resource
        if resource != '':
            self._load_resource(resource)
        self._uri = ''
        self._data = None
        
    def id(self):
        if self._uri != '':
            return self._uri
        else:
            return hashlib.md5(self._data)
        
    def _load_resource(self, resource):
        elems = urlparse.urlparse(resource)
        
        if elems[0] == 'file':
            e = elems[1]
        elif elems[0] == '':
            f = open(elems[2], 'rb')
            self._data = f.read(-1)
    