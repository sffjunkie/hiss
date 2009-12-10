from hiss import Notifier

def testConnect():
    n = Notifier()
    n.connect()

def testRegistration():
    n = Notifier()
    n.notifications = { 'a_class': ('a_title', True) }
    
    n.connect()
    n.register()
    n.disconnect()
    