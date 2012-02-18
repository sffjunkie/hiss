from hiss import Notifier, Target, Notification

p = Notifier()
p.app_name = 'hiss'
p.app_icon = 'file:///'

t = Target('snarl') # Snarl on local host
t = Target('snarl', host='192.168.0.1') # Snarl on remote host
t = Target('snarl', host='192.168.0.1', password='pass') # Snarl on remote host with security
p.targets += t

t2 = Target('growl')
t2 = Target('growl', host='192.168.0.1')
p.targets += t2

p.register()

n = Notification()
n.title = 'A Notification'
n.text = 'The notification text'
n.icon = ''
n.actions = []

d = p.send(n) # Sends to all targets
d.addCallback(success)
d.addErrback(failure)

d = p.send(n, target=t) # Send to a specific target

t = Target('xbmc', host='127.0.0.1')

