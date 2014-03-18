# Copyright 2013-2014, Simon Kennedy, code@sffjunkie.co.uk
#
# Part of 'hiss' the asynchronous notification library

import uuid

try:
    from urllib.request import urlopen    
except ImportError:
    from urllib2 import urlopen

class Resource(object):
    def __init__(self, source='', data=None):
        """Provide access to a resource.

        Only one of :attr:`source` or :attr:`data` should be provided.
        If both used :attr:`data` will override :attr:`source`.

        :param source:   URI of the data.
        :type source:    string
        :param data:     Data to use
        :type data:      bytes
        """

        self.uid = str(uuid.uuid4())
        self.source = source
        self._data = data

    @property
    def data(self):
        if self._data is None:
            if self.source[0] == '!':
                self._data = self.source
            else:
                f = urlopen(self.source)
                self._data = f.read(-1)

        return self._data

    def __len__(self):
        if self._data is not None:
            return len(self._data)
        elif self.source != '':
            return len(self.source)
        else:
            return 0


class Icon(Resource):
    pass
