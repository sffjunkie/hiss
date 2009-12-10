# Copyright 2009, Simon Kennedy, sdk@sffjunkie.co.uk.
# Distributed under the terms of the MIT License.

from enum import *

priority = Enum('Notification priority',
    [('VeryLow', -2),
     ('Moderate', -1),
     ('Normal', 0),
     ('High', 1),
     ('Emergency', 2)
    ])

class Notification(object):
    def __init__(self, name, display_name='', enabled=False, title='', text=''):
        self._application = ''
        self._nid = 0
        self._name = name
        self._display_name = display_name
        self._enabled = enabled
        self._title = title.encode('utf-8')
        self._text = text.encode('utf-8')
        self._sticky = False
        self._priority = priority.Normal
        self._icon = None
        self._icon_uri = ''
        self._sound = None
        self._timeout = 0
        self._notifier = None

    def application():
        doc = """The notification ID"""
        
        def fget(self):
            return self._application

        def fset(self, value):
            self._application = value

        return locals()

    application = property(**application())

    def nid():
        doc = """The notification ID"""
        
        def fget(self):
            return self._nid

        def fset(self, value):
            self._nid = value

        return locals()

    nid = property(**nid())

    def name():
        doc = """The name of the displayed notification."""

        def fget(self):
            return self._name

        def fset(self, value):
            self._name = value

        return locals()

    name = property(**name())

    def display_name():
        doc = """The display_name of the displayed notification."""

        def fget(self):
            return self._display_name

        def fset(self, value):
            self._display_name = value

        return locals()

    display_name = property(**display_name())

    def enabled():
        doc = """The enabled of the displayed notification."""

        def fget(self):
            return self._enabled

        def fset(self, value):
            self._enabled = value

        return locals()

    enabled = property(**enabled())

    def title():
        doc = """The title of the displayed notification."""

        def fget(self):
            return self._title

        def fset(self, value):
            if len(value) > 1024:
                raise ValueError('Maximum title length (1024) exceeded')

            self._title = value.encode('utf-8')

        return locals()

    title = property(**title())

    def text():
        doc = """The text displayed below the title."""

        def fget(self):
            return self._text

        def fset(self, value):
            self._text = value.encode('utf-8')

        return locals()

    text = property(**text())

    def icon_uri():
        doc = """The URI of the icon to display."""

        def fget(self):
            return self._icon_uri

        def fset(self, uri):
            self._icon_uri = uri

        return locals()

    icon_uri = property(**icon_uri())

    def icon_from_file():
        self._icon_file = Icon()
        self._icon_file.from_file(filename)

    def icon_file():
        doc = """The URI of the icon to display."""

        def fget(self):
            return self._icon_file

        def fset(self, uri):
            self._icon_file = uri

        return locals()

    icon_file = property(**icon_file())

    def sound():
        doc = """A sound to play when displaying the notification."""

        def fget(self):
            return self._sound

        def fset(self, value):
            self._sound = value

        return locals()

    sound = property(**sound())

    def timeout():
        doc = """Timeout before the notification is hidden."""

        def fget(self):
            return self._timeout

        def fset(self, value):
            self._timeout = int(value)

        return locals()

    timeout = property(**timeout())

    def priority():
        doc = """The priority of the notification."""
        def fget(self):
            return self._priority

        def fset(self, value):
            self._priority = value

        return locals()

    priority = property(**priority())

    def sticky():
        doc = """The 'stickiness' of the notification. A sticky message has an infinite timeout."""
        def fget(self):
            return self._sticky

        def fset(self, value):
            self._sticky = bool(value)

        return locals()

    sticky = property(**sticky())

    def is_visible():
        doc = """Determine if the notification is currently being displayed."""

        def fget(self):
            raise NotImplementedError

        return locals()

    is_visible = property(**is_visible())

    def to_notify_message():
        raise NotImplementedError

    def show(self):
        """Show the notification."""

        raise NotImplementedError

    def update(self):
        """Update the title and text of an existing notification."""

        raise NotImplementedError

    def hide(self):
        """Hide the notification"""

        raise NotImplementedError


