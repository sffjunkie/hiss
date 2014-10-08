# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Part of 'hiss' the asynchronous notification library

import uuid
import asyncio
import logging
from itertools import product
from collections import namedtuple

from hiss.target import Target
from hiss.exception import NotifierError
from hiss.notification import Notification
from hiss.handler.gntp import GNTPHandler
from hiss.handler.snp import SNPHandler
from hiss.handler.xbmc import XBMCHandler

__all__ = ['Notifier', 'USE_NOTIFIER', 'USE_REGISTERED']

NotificationInfo = namedtuple('NotificationInfo', ['name', 'title', 'text',
                                                   'icon', 'sound', 'enabled'])

USE_NOTIFIER = object()
USE_REGISTERED = object()
    

class Notifier(object):
    """Maintains a list of targets to handle notifications for.

    :param name:      The name of this notifier
    :type name:       str
    :param signature: Application signature for this notifier.
    :type signature:  str
    :param icon:      Notifier icon. Used when registering the notifier and
                      as the default icon for notifications.
    :type icon:       :class:`~hiss.resource.Icon` or str
    :param sound:     Sound to play when displaying the notification.
    :type sound:      str
    :param response_handler: Coroutine that is called whenever a response
                             is received.
    :type response_handler:  asyncio coroutine
    :param event_handler: Coroutine that is called whenever an asynchronous
                          event arrives.
    :type event_handler:  asyncio coroutine
    :param loop:      :mod:`asyncio` event loop to use.
    :type loop:       :class:`asyncio.BaseEventLoop`
    """
    #TODO: standardised icon and sound handling between handler types
    def __init__(self, name, signature,
                 icon=None, sound=None,
                 response_handler=None,
                 event_handler=None,
                 loop=None):
        self.name = name
        self.signature = signature
        self.icon = icon
        self.sound = sound
        
        self.notification_classes = {}
        self.targets = TargetList()
        
        if response_handler and not asyncio.iscoroutinefunction(response_handler):
            raise ValueError('response_handler must be an asyncio coroutine')
        self._response_handler = response_handler
        
        if event_handler and not asyncio.iscoroutinefunction(event_handler):
            raise ValueError('event_handler must be an asyncio coroutine')
        self._event_handler = event_handler

        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop

        self._handlers = {}
        self._notifications = {}

    def add_notification(self, name, title=None, text=None,
                         icon=None, sound=None,
                         enabled=True, class_id=None):
        """Add a notification class.

        :param name:          Notification class name
        :type name:           str
        :param title:         Default notification title
        :type title:          str or None
        :param text:          Default notification text
        :type text:           str or None
        :param icon:          Default notification icon
        :type icon:           str or None
        :param sound:         Default notification sound
        :type sound:          str or None
        :param enabled:       Whether the notification is enabled or not
        :type enabled:        bool
        :param class_id:      The class id to use. If not provided one will be
                              generated.
        :type class_id:       int
        :returns:             The class id of the newly added notification
        :rtype:               int
        
        Default values will be used when creating a notification with
        :meth:`~hiss.notifier.Notifier.create_notification`
        """
        ni = NotificationInfo(name, title, text, icon, sound, enabled)

        if class_id is None or class_id in self.notification_classes:
            if len(self.notification_classes) == 0:
                class_id = 1
            else:
                class_id = max(self.notification_classes.keys()) + 1

        self.notification_classes[class_id] = ni

        return class_id

    def create_notification(self, class_id=-1, name='',
                            title=USE_REGISTERED,
                            text=USE_REGISTERED,
                            icon=USE_REGISTERED,
                            sound=USE_REGISTERED):
        """Create a notification that is ready to send.

        Either ``class_id`` or ``name`` can be provided. If ``class_id`` is
        provided it will be used instead of ``name`` to
        lookup the defaults registered in
        :meth:`~hiss.notifier.Notifier.add_notification`

        :param class_id:   The notification class id
        :type class_id:    int
        :param name:       The notification name
        :type name:        str
        :param title:      The title of the notification
        :type title:       str, None for no title or
                           :data:`~hiss.notifier.USE_REGISTERED` (default)
                           to use title provided during registration,
                           :data:`~hiss.notifier.USE_NOTIFIER` to the use the
                           Notifier's name 
        :param text:       The text to display in the notification
        :type text:        str, None for no text or
                           :data:`~hiss.notifier.USE_REGISTERED` (default)
                           to use text provided during registration
        :param icon:       Icon to display
        :type icon:        str, :class:`~hiss.resource.Icon`, None for no
                           icon or
                           :data:`~hiss.notifier.USE_REGISTERED` (default)
                           to use icon provided during registration
        :param sound:      Sound to play when showing notification
        :type sound:       str, None (default) for no sound or
                           :data:`~hiss.notifier.USE_REGISTERED`
                           to use sound provided during registration
        """
        if class_id != -1:
            if class_id not in self.notification_classes:
                raise NotifierError('%d is not a known notification class id' % \
                                 str(class_id))
            registration_info = self.notification_classes[class_id]
        elif name != '':
            registration_info = self.find_notification(name)
        else:
            raise NotifierError('Either a class id or name must be specified.',
                                'hiss.notifier.Notifier')

        if title is USE_REGISTERED:
            title = registration_info.title
        elif title is USE_NOTIFIER:
            title = self.name

        if text is USE_REGISTERED:
            text = registration_info.text

        if icon is None:
            if registration_info.icon is not None:
                icon = registration_info.icon
            else:
                icon = self.icon

        if registration_info.sound is None:
            sound = None
        elif sound == USE_REGISTERED:
            sound = registration_info.sound

        uid = self._unique_id()

        n =  Notification(title, text, icon, sound, uid=uid)
        n.name = registration_info.name
        n.class_id = class_id
        n.notifier = self
        return n

    def find_notification(self, name):
        for value in self.notification_classes.values():
            if value.name == name:
                return value
            
        raise NotifierError('Notification name %s not found.' % name)

    @asyncio.coroutine
    def add_target(self, targets):
        """Add a single target or list of targets to the known targets
        and connects to them

        :param targets: The Target or list of Targets to add.
        :type targets:  :class:`~hiss.target.Target`
        :returns:       Result dict or list of dict if more than one target added.
        """
        if isinstance(targets, Target):
            targets = [targets]

        wait_for = []
        for target in targets:
            if target.scheme in self._handlers:
                handler = self._handlers[target.scheme]
            elif target.scheme == 'snp':
                handler = SNPHandler(self.loop)
                self._handlers[target.scheme] = handler
            elif target.scheme == 'gntp':
                handler = GNTPHandler(self.loop)
                self._handlers[target.scheme] = handler
            elif target.scheme == 'xbmc':
                handler = XBMCHandler()
                self._handlers[target.scheme] = handler

            wait_for.append(handler.connect(target))

        done, _pending = yield from asyncio.wait(wait_for)

        results = []
        for task in done:
            tr = task.result()

            result = {}
            result['target'] = tr.target
            if result is None:
                result['status'] = 'ERROR'
                result['reason'] = 'Unable to connect to target'
            else:
                result['status'] = 'OK'            
                self.targets.append(tr.target)

            results.append(result)

        if len(results) == 1:
            return results[0]
        else:
            return results

    def remove_target(self, target):
        """Remove a target from the known targets.

        :param target: The Target to remove.
        :type target:  :class:`~hiss.target.Target`
        """
        self.targets.remove(target)
        
    def log(self, message):
        logging.log(logging.DEBUG, message)

    @asyncio.coroutine
    def register(self, targets=None):
        """Register this notifier with the target specified.

        :param targets: The target or targets to register with or ``None``
                        to register with all known target
        :type targets:  :class:`~hiss.target.Target`,
                        [:class:`~hiss.target.Target`] or ``None``
        """
        targets = self.targets.valid_targets(targets)

        wait_for = []
        for target in targets:
            wait_for.append(target.handler.register(self, target))

        done, _pending = yield from asyncio.wait(wait_for)

        results = []
        for task in done:
            result = task.result()

            response = {}
            response.update(result)
            results.append(response)

        if len(results) == 1:
            return results[0]
        else:
            return results

    @asyncio.coroutine
    def notify(self, notifications, targets=None):
        """Send a notification to a specific targets or all targets.

        :param notifications: A notification or list of notifications to send
        :type notifications:  :class:`hiss.notification.Notification`
        :param targets:       The targets to send the notification to. If no
                              targets is specified then the notification will
                              be sent to all known targets.
        :type targets:        :class:`hiss.target.Target` or ``None``
        """
        if isinstance(notifications, Notification):
            notifications = [notifications]

        for notification in notifications:
            notification.notifier = self

        targets = self.targets.valid_targets(targets)

        wait_for = []
        combos = product(notifications, targets)
        for notification, target in combos:
            wait_for.append(target.handler.notify(notification, target))

        done, _pending = yield from asyncio.wait(wait_for)

        #TODO: Handling of sticky notifications for show/hide
        responses = []
        for task in done:
            result = task.result()

            response = {}
            response.update(result)
            responses.append(response)

        if len(responses) == 1:
            return responses[0]
        else:
            return responses

    @asyncio.coroutine
    def subscribe(self, signatures=[], targets=None):
        """Subscribe to notifications from a list of signatures.

        :param signatures: List of signatures to listen to events from. If an
                           empty list is specified then subscribe to events
                           from all applications.
        :type signatures:  List of strings or empty list.
        """
        targets = self.targets.valid_targets(targets)

        responses = []
        for target in targets:
            response = yield from target.handler.subscribe(self, signatures,
                                                           target)

            response['handler'] = target.handler.__name__
            responses.append(response)

        if len(responses) == 1:
            return responses[0]
        else:
            return responses

    @asyncio.coroutine
    def unregister(self, targets=None):
        """Unregister this notifier with all targets

        :param targets: The targets to register with
                        If not specified or ``None`` then the notifier
                        will be registered with all known targets
        :type targets:  :class:`hiss.Target` or ``None``
        """
        for handler in self._handlers.values():
            if handler.capabilities['unregister']:
                handler.unregister(targets, notifier=self)

    @asyncio.coroutine
    def show(self, uid):
        """If ``uid`` is in the list of current notifications then show it."""

        if uid in self._notifications:
            for handler in self._handlers.values():
                if 'show' in handler.capabilities:
                    handler.show(self, uid)

    @asyncio.coroutine
    def hide(self, uid):
        """If ``uid`` is in the list of current notifications then hide it."""

        if uid in self._notifications:
            for handler in self._handlers.values():
                if 'hide' in handler.capabilities:
                    handler.hide(self, uid)

    @asyncio.coroutine
    def responses_received(self, responses):
        """Event handler for callback events.
        
        Default handler calls the response handler provided to `init`.

        :param responses: The event
        :type responses:  :class:`hiss.NotificationEvent`
        """
        if self._response_handler:
            yield from self._response_handler(responses)

    @asyncio.coroutine
    def events_received(self, events):
        """Event handler for callback events.
        
        Default handler calls the event handler provided to `init`.

        :param responses: The event
        :type responses:  :class:`hiss.NotificationEvent`
        """
        if self._event_handler:
            yield from self._event_handler(events)

    @asyncio.coroutine
    def _handler(self, responses):
        logging.debug(responses)
        self.responses_received(responses)

    def _unique_id(self):
        return str(uuid.uuid4())


class TargetList(object):
    def __init__(self):
        self.targets = []

    def __contains__(self, target):
        for t in self.targets:
            if target == t:
                return True

        return False

    def __iter__(self):
        return self.targets.__iter__()

    def append(self, target):
        self.targets.append(target)

    def remove(self, target):
        index_to_delete = -1
        for idx, t in enumerate(self.targets):
            if target == t:
                index_to_delete = idx
                break

        if index_to_delete != -1:
            del self.targets[index_to_delete]

    def valid_targets(self, target_or_targets):        
        if target_or_targets is None:
            target_or_targets = self.targets
        else:
            target_or_targets = self._known_targets(target_or_targets)

        return target_or_targets

    def _known_targets(self, target_or_targets):
        """Filter out unknown target_or_targets"""  

        if isinstance(target_or_targets, Target) and target_or_targets in self.targets:
            return [target_or_targets]

        _targets = []
        for target in target_or_targets:
            if target in self.targets:
                _targets.append(target)

        return _targets

    