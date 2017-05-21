# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

"""
* Subscribe to messages from a set of targets
* Wait for messages to arrive.
* Send out to all others.
"""

import asyncio

from hiss.handler import gntp, snp, xbmc

SCHEME_HANDLERS = {
    'gntp': gntp.GNTPHandler,
    'snp': snp.SNPHandler,
    'xbmc': xbmc.XBMCHandler,
}

class Nub(object):
    """If a message arrives from any of the registered targets then
    send it on to the other targets.
    
    Notifications can be filtered per target.
    """

    def __init__(self, targets=[]):
        self._targets = []
        self._handlers = {}
        
        for target in targets:
            self.add_target(target)
        
    @asyncio.coroutine
    def async_handler(self, target):
        target.handler.subscribe()
    
    def go(self):
        """Connect to all targets
        """
        asyncio.Task
    
    def add_target(self, target):
        if target in self._targets:
            return
        
        scheme = target.scheme
        if scheme not in self._handlers:
            handler = SCHEME_HANDLERS[scheme]()
            self._handlers[scheme] = handler
        
        target.handler = self._handlers[scheme]
        self._targets.append(target)
        