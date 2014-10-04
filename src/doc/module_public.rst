.. Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com

Public Parts
============

Target
~~~~~~

.. autoclass:: hiss.target.Target
   :members:

Notifier
~~~~~~~~

.. py:data:: hiss.USE_REGISTERED
	
	Signifies to use the value provided during
	:meth:`addition <hiss.notifier.Notifier.add_notification>`
	of a notification.
    
.. autoclass:: hiss.notifier.Notifier
   :members:
   :member-order: bysource

Notification
~~~~~~~~~~~~

.. autoclass:: hiss.notification.NotificationPriority
   :members:
    
.. autoclass:: hiss.notification.Notification
   :members:
   
   .. py:attribute:: uid
   
      Unique ID generated automatically. This ID can be used to refer to the
      notification when showing or hiding via a :class:`~hiss.Notifier`.

Events
~~~~~~

Events are generated in response to asynchronous messages arriving.

.. autoclass:: hiss.event.Event
   :members:
   
.. autoclass:: hiss.event.NotificationEvent
   :members:
   :show-inheritance:

   
Resources
~~~~~~~~~

.. autoclass:: hiss.resource.Icon

