# Copyright 2008, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

# Part of 'hiss' the Python notification library

from distutils.core import setup

long_description="""
hiss is/will be a Python interface to various notification frameworks.
Currently only interfaces to the Snarl application on the local machine.
Growl support will be added later.
"""

setup(name='hiss',
    version='0.1.0',
    description='hiss is a Python interface to various notification frameworks.',
    long_description=long_description,
    author='Simon Kennedy',
    author_email='hiss@sffjunkie.co.uk',
    url='http://www.sffjunkie.co.uk/python/hiss-0.1.0.zip',
    license='MIT',
    package_dir={'': 'src'},
    packages=['hiss', 'hiss.protocol', 'hiss.handler'],
    classifiers=[
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python',
    ],
)

