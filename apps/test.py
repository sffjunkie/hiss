from twisted.internet import reactor

from hiss.notification import Notification

class App(object):
    def __init__(self):
        self._reactor = reactor()
        self._notifier = Notifier(self._reactor)

        self._notifications = [
            Notification('aname', 'A notification', enabled=True)
        ]

        for n in self._notifications:
            self._notifier.add_notification_class(n)

        target = NotificationTarget('snarl') # Snarl on local machine
        target = NotificationTarget('snarl@127.0.0.1') # Snarl Network Protocol
        target = NotificationTarget('growl') # Growl on local machine
        target = NotificationTarget('growl@127.0.0.1') # Growl UDP
        target = NotificationTarget('gntp@127.0.0.1') # Growl Network Transfer Protocol
        self._notifier.set_target(target)
        self._notifier.register()
        self._reactor.callLater(1, loop)
        
    def run(self):
        self._reactor.run()

    def loop(self):
        self._notifier.send('aname')

