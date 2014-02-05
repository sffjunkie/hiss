import os
import socket

from twisted.application import service, internet
from twisted.internet.protocol import Protocol, Factory

from hiss.utility import find_open_port

class NubProtocol(Protocol, object):
    pass

class Nub(Factory, object):
    def __init__(self, port=49999):
        self.protocol = NubProtocol
        self._notifiers = []
        self.targets = []
        self._hostname = socket.gethostname()
        self._ip = socket.gethostbyname(self._hostname)
        self.port = find_open_port(from_port=port)
        
        print(self._hostname, self._ip)

    def startFactory(self):
        self.handlers = []
    
    def stopFactory(self):
        pass
    
    def connectionMade(self):
        print('Connection made')
    
    def buildProtocol(self, addr):
        pass
        #print('%s:%s <%s>' % (addr.host, addr.port, addr.type))

    def addr_is_local(self, addr):
        return addr in [self._ip, '127.0.0.1']

    def port():
        def fget(self):
            return self.port
            
        return locals()
        
    port = property(**port())

nub = Nub()
application = service.Application("nub")
internet.TCPServer(nub.port, nub).setServiceParent(service.IServiceCollection(application))

