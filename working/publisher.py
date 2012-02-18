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

class Publisher(object):
    def __init__(self):
        self._targets = self.Targets()
        self._notifications = {}
        self._notifiers = {}
    
    def register(self, target):
        pass
    
    def send(self, notification, target=None):
        pass

    class Targets(object):
        def __init__(self):
            self._targets = {}
            
        def __iadd__(self, target):
            t = str(target)
            if t in self._targets:
                return self._targets[t]
            else:
                self._targets[t] = {}
                self._targets[t]['registered'] = False
    
        def __isub__(self, target):
            return self.remove_target(target)
        

