# Copyright 2008, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

from exception import *

class Growler(object):
    def __init__(self):
        raise HandlerError('Unable to create Snarl handler.')

    def sendMessage(self, message, timeout=0):
        pass

