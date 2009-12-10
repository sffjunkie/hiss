from hiss.notifier import Notifier
from hiss.notification import Notification

class Application(Notifier):
    notifications = {
        'wally': ('I am a wally', True, ''),
        'dave':  ('I am Dave', False, '')
    }

    def __init__(self):
        self._count = 0
        Notifier.__init__(self)

    def startApp(self):
        """Called automatically by the Notifier class."""
        
        self.call_later(0, self.loop)
        
    def loop(self):
        if self._count < 2:
            print('Sending %d...' % self._count)
            n = Notification('wally%d' % self._count)
            self.send(n)
            self._count += 1
            self.call_later(10, self.loop)
        else:
            print('Stopping...')
            self.stop()

if __name__ == '__main__':
    a = Application()
    a.run()
    