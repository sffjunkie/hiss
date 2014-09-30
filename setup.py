# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
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

import sys
from setuptools import setup

install_requires = ['aiohttp']
if sys.version_info.minor == 3:
    install_requires.append('asyncio')

long_description="""Hiss is a Python interface to various notification
frameworks. It currently supports sending notifications to

* Growl using the Growl Network Transfer Protocol
* Snarl using the Snarl Network Protocol
* XBMC using JSON RPC

and uses the asyncio module supplied with Python version 3.4 (or Python 3.3
with asyncio from PyPi.) 
"""

setup(name='hiss',
    version='0.1.0',
    description='Hiss: a Python interface to various notification frameworks.',
    long_description=long_description,
    author='Simon Kennedy',
    author_email='sffjunkie+code@gmail.com',
    url='http://www.sffjunkie.co.uk/python/hiss-0.1.0.zip',
    license='Apache License 2.0',
    package_dir={'': 'src'},
    packages=['hiss', 'hiss.handler'],
    install_requires=install_requires,
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',
      'License :: OSI Approved :: Apache Software License',
    ],
)
