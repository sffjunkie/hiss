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

These are the public facing classes to use for sending notifications. The normal
order of events is to...
	
* create a :class:`.Notifier`
* register a set of notifications with :meth:`.register_notification`
* register a :class:`.Target` to send notifications to with
  :meth:`.register_target`
* create a new :class:`.Notification` with :meth:`.create_notification`
* and finally :meth:`notify() <hiss.Notifier.notify>` the
  targets of the notification


Target
------

.. autoclass:: hiss.Target
   :members:

Notifier
--------
    
.. autoclass:: hiss.Notifier
   :members:

Notification
------------
    
.. autoclass:: hiss.Notification
   :members:

Events
------
   
.. autoclass:: hiss.Event
   :members:
   
.. autoclass:: hiss.NotificationEvent
   :members:
   :inherited-members:

   
Resources
---------
    
.. autoclass:: hiss.resource.Resource

.. autoclass:: hiss.resource.Icon

