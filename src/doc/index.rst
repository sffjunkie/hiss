.. Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com

Hiss |version|
==============

.. toctree::
   :maxdepth: 2

   module_public
   module_private
   hashinfo

Introduction
~~~~~~~~~~~~
   
Hiss is a Python 3 asyncio based notification library which allows you to send
notifications to multiple targets using multiple protocols.

The following protocols are supported...

* `Snarl`_ Network Protocol (`SNP`_)
* `Growl`_ Network Transfer Protocols (`GNTP`_)
* `Pushbullet HTTPS API`_
* `Pushover HTTPS API`_
* XBMC using the `JSON RPC API`_

It uses the `asyncio`_ module (introduced in Python 3.4) to provide the network
plumbing to send and receive messages.

Usage
~~~~~

The normal order of events to send a notification is to...
    
* create a :class:`~hiss.notifier.Notifier`
* define a set of notifications with
  :meth:`~hiss.notifier.Notifier.add_notification`
* register a :class:`~hiss.target.Target` to send notifications to with
  :meth:`~hiss.notifier.Notifier.add_target`
* create a new :class:`~hiss.notification.Notification` with
  :meth:`~hiss.notifier.Notifier.create_notification`
* and finally :meth:`~hiss.notifier.Notifier.notify` the
  targets with the notification

.. code-block:: python

   from hiss import Notifier, Target
   
   notifier = Notifier('A Notifier', 'application/x-vnd.joe.bloggs')
   notifier.add_notification(name='Alert')
   
   target = Target('snp://127.0.0.1')
   notifier.add_target(target)
   
   notification = notifier.create_notification(name='Alert', title='Important',
                                               text='Who let the snake out!')
   
   notifier.notify(notification)
    
Dependencies
~~~~~~~~~~~~

Python 3.3 with the `asyncio module`_ on PyPi or Python versions >= 3.4

Installation
~~~~~~~~~~~~

Hiss is available from `PyPi`_ and can be installed using `pip`_::
    
    sudo pip install hiss
    
License
~~~~~~~

This module is licensed under the terms of the `Apache V2.0 license`_.
    
Version History
~~~~~~~~~~~~~~~

======== =======================================================================
Version  Description
======== =======================================================================
0.1      First Release
======== =======================================================================
   

.. _Apache V2.0 license: http://www.opensource.org/licenses/apache2.0.php
.. _asyncio: http://docs.python.org/3.4/library/asyncio.html
.. _Snarl: http://snarl.fullphat.net/
.. _Growl: http://growl.info/
.. _SNP: https://sites.google.com/site/snarlapp/developers/api-reference
.. _GNTP: http://www.growlforwindows.com/gfw/help/gntp.aspx
.. _XBMC: http://www.xbmc.org
.. _JSON RPC API: http://wiki.xbmc.org/index.php?title=JSON-RPC_API/v6
.. _PyPi: http://pypi.python.org
.. _pip: https://pip.pypa.io/en/latest/index.html
.. _Pushbullet: https://www.pushbullet.com/
.. _Pushbullet HTTPS API: https://docs.pushbullet.com/
.. _Pushover: https://pushover.net/
.. _Pushover HTTPS API: https://pushover.net/api
.. _asyncio module: https://pypi.python.org/pypi/asyncio
