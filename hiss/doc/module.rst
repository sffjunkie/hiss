.. Copyright 2009-2010, Simon Kennedy, python@sffjunkie.co.uk

.. Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

..   http://www.apache.org/licenses/LICENSE-2.0

.. Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

The :mod:`hiss` Module
========================

Target
------

.. autoclass:: hiss.Target
   :members:

Notifier
--------
  
.. py:data:: hiss.USE_REGISTERED
	
	Signifies to use the value provided during
	:meth:`registration <hiss.Notifier.register_notification>`
	of a notification.
    
.. autoclass:: hiss.Notifier
   :members:

Notification
------------

.. autoclass:: hiss.NotificationPriority
   :members:
    
.. autoclass:: hiss.Notification
   :members:
   
   .. py:attribute:: uid
   
      Unique ID generated automatically. This ID can be used to refer to the
      notification when showing or hiding via a :class:`~hiss.Notifier`.

Events
------
   
.. autoclass:: hiss.Event
   :members:
   
.. autoclass:: hiss.NotificationEvent
   :members:
   :show-inheritance:

   
Resources
---------

.. autoclass:: hiss.Icon

