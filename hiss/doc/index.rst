.. Hiss documentation master file, created by
   sphinx-quickstart on Mon May 21 15:12:36 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Hiss |version|
==============

.. toctree::
   :hidden:
   :maxdepth: 4

   module
   handlers

Introduction
------------
   
Hiss is a notification library which allows you to send notifications to
multiple targets using multiple protocols.

The following protocols are supported...

* `Snarl`_ Network Protocol (`SNP`_)
* `Growl`_ Network Transfer Protocols (`GNTP`_)


It uses `Twisted`_ to provide the network plumbing to send and receive messages.

Installation
------------

Hiss is available from `PyPi`_ and can be installed using `pip`_::
    
    sudo pip install hiss

Usage
-----

The normal order of events to send a notification is to...
    
* create a :class:`~hiss.Notifier`
* register a set of notifications with
  :meth:`~hiss.Notifier.register_notification`
* register a :class:`~hiss.Target` to send notifications to with
  :meth:`~hiss.Notifier.add_target`
* create a new :class:`.Notification` with
  :meth:`~hiss.Notifier.create_notification`
* and finally :meth:`~hiss.Notifier.notify` the
  targets with the notification

.. code-block:: python

   from hiss import Notifier, Target
   
   notifier = Notifier('application/x-vnd.joe.bloggs')
   class_id = notifier.register_notification('Alert')
   
   target = Target('snp://127.0.0.1')
   notifier.add_target(target)
   
   notification = notifier.create_notification(class_id, 'Important',
                                               'Who let the snake out!')
   
   notifier.notify(notification)
   

.. _Twisted: http://twistedmatrix.com/trac/
.. _Snarl: http://snarl.fullphat.net/
.. _Growl: http://growl.info/
.. _SNP: https://sites.google.com/site/snarlapp/developers/api-reference
.. _GNTP: http://www.growlforwindows.com/gfw/help/gntp.aspx
.. _PyPi: http://pypi.python.org
.. _pip: http://www.pip-installer.org/en/latest/index.html

