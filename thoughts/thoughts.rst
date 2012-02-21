from hiss import Notifier, Target, Notification

no = Notifier()
no.name = 'hiss'
no.icon = 'file:///'

t = Target('snarl') # Snarl on local host
t = Target('snarl', host='192.168.0.1') # Snarl on remote host
t = Target('snarl', host='192.168.0.1', password='pass') # Snarl on remote host with security
no.targets += t

t2 = Target('growl')
t2 = Target('growl', host='192.168.0.1')
no.targets += t2

no.register()

n = Notification()
n.title = 'A Notification'
n.text = 'The notification text'
n.icon = ''
n.actions = []

d = no.send(n) # Sends to all targets
d.addCallback(success)
d.addErrback(failure)

d = no.send(n, target=t) # Send to a specific target

t = Target('xbmc', host='127.0.0.1')

