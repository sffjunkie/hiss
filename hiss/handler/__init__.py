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

# Part of 'hiss' the twisted notification library

import socket

from hiss.target import Target


class Handler(object):
    def __init__(self, notifier, port):
        self._notifier = notifier
        self._default_port = port
        self._targets = TargetList()
    
    def connect(self, target):
        """Connect to a target
        
        :param target: Target to connect to
        :type target:  :class:`hiss.target.Target`
        """
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target.host, self._default_port))
            
            target.port = self._default_port
            target.handler = self
            self._targets.append(target)
        finally:
            s.close()

    def disconnect(self, target):
        """Disconnect from a target
        
        :param target: Target to disconnect from
        :type target:  :class:`hiss.Target`
        """
        
        if target in self._targets:
            target.handler = None
            self._targets.remove(target)
        else:
            raise ValueError('hiss.Handler: disconnect - Not connected to target')

    def _get_targets(self, targets):
        if targets is None:
            targets = self._targets
        elif isinstance(targets, Target):
            if targets not in self._targets:
                raise ValueError('hiss.Handler: Unable to send request - Target unknown')
            else:
                targets = [targets]
        elif isinstance(targets, list):
            targets = []
            for t in targets:
                if isinstance(t, Target):
                    if t.port == -1:
                        t.port = self._default_port
                        
                    if t in self._targets:
                        targets.append(t)
            
            if len(targets) == 0:
                raise ValueError('hiss.Handler: Unable to send request - No valid targets specified')
        return targets

    def _get_notifier(self, notifier):
        if notifier is None:
            notifier = self._notifier
        if notifier is None:
            raise ValueError('hiss.Handler: No notifier specified')
        return notifier


class txHandler(Handler):
    def __init__(self, notifier):
        Handler.__init__(self, notifier)
    
    def connect(self, target, connected_handler):
        """Connect to a target
        
        :param target: Target to connect to
        :type target:  :class:`hiss.target.Target`
        """

    def disconnect(self, target):
        """Disconnect from a target
        
        :param target: Target to disconnect from
        :type target:  :class:`hiss.Target`
        """


class TargetList(object):
    def __init__(self):
        self._targets = []

    def __contains__(self, target):
        for t in self._targets:
            if target == t:
                return True
            
        return False
        
    def __iter__(self):
        return self._targets.__iter__()
        
    def append(self, target):
        self._targets.append(target)

    def remove(self, target):
        index_to_delete = -1
        for idx, t in enumerate(self._targets):
            if target == t:
                index_to_delete = idx
                break
        
        if index_to_delete != -1:
            del self._targets[index_to_delete]

    def valid_targets(self, targets):        
        if targets is None:
            targets = self._targets
        else:
            targets = self._known_targets(targets)
            
        return targets

    def _known_targets(self, targets):
        """Filter out unknown targets"""  
        
        if isinstance(targets, tuple):
            targets = list(targets)
        elif not isinstance(targets, list):
            targets = [targets]
        
        _targets = []
        for target in targets:
            if target in self._targets:
                _targets.append(target)
                
        return _targets
        
    