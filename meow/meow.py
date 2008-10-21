import os

import snarl
import growl

from exception import *

class Message(object):
    def __init__(self, handler):
        self._title = ''
        self._text = ''
        self._icon = ''

        self._handler = handler

    def _get_title(self):
        return self._title

    def _set_title(self, title):
        if len(title) > 1024:
            raise ValueError('Maximum title length (1024) exceeded')

        self._title = title

    Title = property(_get_title, _set_title)

    def _get_text(self):
        return self._text

    def _set_text(self, text):
        self._text = text

    Text = property(_get_text, _set_text)

    def _get_icon(self):
        return self._icon

    def _set_icon(self, icon):
        self._icon = icon

    Icon = property(_get_icon, _set_icon)

    def _get_sound(self):
        return self._sound

    def _set_sound(self, sound):
        self._sound = sound

    Sound = property(_get_sound, _set_sound)

    def _get_handler(self):
        return self._handler

    def _set_handler(self, handler):
        self._handler = handler

    Handler = property(_get_handler, _set_handler)

    def Show():
        self._handler.show(self)

    def Hide():
        self._handler.hide(self)

    IsValid = property(lambda self: self._title != '' and self._text != '')

class Tiddles(object):
    def __init__(self, handler=None):
        if handler is None:
            if os.name == 'osx':
                handler = 'growl'
            else:
                handler = 'snarl'

        try:
            if handler == 'snarl':
                self._handler = snarl.Snarler()
            elif handler == 'growl':
                self._handler = growl.Growler()
            else:
                raise ValueError('Unknown handler %s specified' % handler)
        except:
            raise HandlerError('Unable to create %s handler.' % handler)

    def handlerVersion(self):
        pass

    def meow(self, msg, timeout=0)
        msg.Handler = self._handler

    def Show():
        self._handler.show(self)

    def Hide():
        self._handler.hide(self)

