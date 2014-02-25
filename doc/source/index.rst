.. Hiss documentation master file, created by
   sphinx-quickstart on Mon May 21 15:12:36 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Hiss |version|
==============

.. toctree::
   :hidden:
   :maxdepth: 4

   module_public
   module_private
   hashinfo

Introduction
~~~~~~~~~~~~
   
Hiss is an asynchronous notification library which allows you to send
notifications to multiple targets using multiple protocols.

The following protocols are supported...

* `Snarl`_ Network Protocol (`SNP`_)
* `Growl`_ Network Transfer Protocols (`GNTP`_)
* `XBMC`_ Displays notifications on XBMC using the `JSON api`_

It uses the `asyncio`_ module (introduced in Python 3.4) to provide the network
plumbing to send and receive messages.
    
Dependencies
~~~~~~~~~~~~

Python 3.3 with the asyncio backport or Python versions > 3.4.

Installation
~~~~~~~~~~~~

Hiss is available from `PyPi`_ and can be installed using `pip`_::
    
    sudo pip install hiss

Usage
~~~~~

The normal order of events to send a notification is to...
    
* create a :class:`~hiss.notifier.Notifier`
* register a set of notifications with
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
   notifier.add_notification('Alert')
   
   target = Target('snp://127.0.0.1')
   notifier.add_target(target)
   
   notification = notifier.create_notification('Alert', 'Important',
                                               'Who let the snake out!')
   
   notifier.notify(notification)
    
License
~~~~~~~

This module is licensed under the terms of the `Apache V2.0 license`_.
    
Version History
~~~~~~~~~~~~~~~

======== =======================================================================
Version  Description
======== =======================================================================
0.1a     First Release
======== =======================================================================
   

.. _Apache V2.0 license: http://www.opensource.org/licenses/apache2.0.php
.. _asyncio: http://docs.python.org/3.4/library/asyncio.html
.. _Snarl: http://snarl.fullphat.net/
.. _Growl: http://growl.info/
.. _SNP: https://sites.google.com/site/snarlapp/developers/api-reference
.. _GNTP: http://www.growlforwindows.com/gfw/help/gntp.aspx
.. _XBMC: http://www.xbmc.org
.. _JSON api: http://wiki.xbmc.org/index.php?title=JSON-RPC_API/v6
.. _PyPi: http://pypi.python.org
.. _pip: http://www.pip-installer.org/en/latest/index.html

