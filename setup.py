from distutils.core import setup

long_description="""
hiss will be a Python interface to various notification frameworks.
Currently only interfaces to the Snarl application on the local machine.
Growl and xPL support will be added later.
"""

setup(name='hiss',
    version='0.1.0',
    description='hiss is a Python interface to notification frameworks.',
    long_description=long_description,
    author='Simon Kennedy',
    author_email='hiss@sffjunkie.co.uk',
    url='http://www.sffjunkie.co.uk/python/hiss-0.1.0.zip',
    license='MIT',
    packages=['hiss'],
    classifiers=[
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: MIT License',
      'Operating System :: Microsoft :: Windows',
      'Programming Language :: Python',
    ],
)

