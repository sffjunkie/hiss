import socket
from hiss.handler.gntp.message import Response

class GNTPHandler():
    def register(self, notifier, target, **kwargs):
        pass

    def notify(self, notification, target):
        pass

    def unregister(self, notifier, target):
        pass

def send_request(request, target, wait_for_response=True):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(target.address)
    s.sendall(request.marshal())

    if wait_for_response:
        response_data = bytearray()
        while True:
            data = s.recv(1024)
            if not data:
                break
            response_data.extend(data)
        response = Response()
        response.unmarshal(response_data)
    else:
        response = None

    s.close()
    return response
