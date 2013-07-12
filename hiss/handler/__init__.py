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

class TargetList(object):
    def __init__(self):
        self._targets = []

    def __contains__(self, target):
        for t in self._targets:
            if target.scheme == t.scheme and target.host == t.host:
                return True
            
        return False
        
    def append(self, target):
        self._targets.append(target)
        
    def __getitem__(self, s):
        return self._targets[s]
    
    def __setitem__(self, index, value):
        self._targets[index] = value
        
    def __delitem__(self, s):
        del self._targets[s]

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

