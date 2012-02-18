Hiss - The Python Notification Framework
========================================

a = hiss.Application(name) - Finds a free port
a.register()
a.send_notification(notification)
a.callback_received(notification)

Classes
-------

Notifier
    A local application

    set_target    
    register(notifications)
    send(notification or message)

Notification
    Created by an Application and sent to the Nub
    title
    from = IP address
    target = IP address

NotificationProtocol(twisted.Protocol)
    
Notification Hub (Nub)
    Listen on port 23053
    Determines the correct Handler
    handlers += Handler(endpoint)
    
Handler
    Sends a Notification to an Endpoint using a Protocol
    One Handler per target machine
    Receives Responses and Callbacks
    Runs in its own loop
    Maintains a list of endpoints
    endpoints += Endpoint(name, protocol)
    
Protocol
    Packages a Notification into a Message
    Encoder + Decoder

    native/network
    
    GNTProtocol - Growl Network Transfer Protocol
    SNProtocol - Snarl

Encoder/Decoder

Message
    Register
    Notify
    Subscribe
    Response
    Callback

Target
    Accepts Notifications packaged using a Protocol



class MyApp(Notifier):

i1 = Icon('icon.png')
n1 = Notification('n1', display_name='Notification 1', enabled=True, icon=i1)
n2 = Notification('n2')

a = MyApp()
a.notifications = [n1, n2]
a.register()
a.set_target('snarl')
a.set_target('snarl@127.0.0.1')
a.set_target('growl')
a.set_target('growl@127.0.0.1')
a.send(n1)
a.send('n1name')

m = SnarlMessage(notification)
m.set_to(msg)
m.send()

    
    
Future
------

Change notifier next function into a generator. NotifierProtocol will need to
keep track of messages sent.

