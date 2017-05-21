import logging
import pytest

from hiss.target import Target
from hiss.notifier import Notifier
from hiss.notification import Notification
from hiss.handler.gntp.message import RegisterRequest, NotifyRequest

from hiss.handler.gntp import GNTP_DEFAULT_PORT
from hiss.handler.gntp.sync import send_request

HOST = '127.0.0.1'


@pytest.fixture
def local_target():
    return Target('gntp://%s:%d' % (HOST, GNTP_DEFAULT_PORT))


@pytest.fixture(scope='module')
def notifier():
    n = Notifier('GNTP Notifier', '0b57469a-c9dd-451b-8d86-f82ce11ad09g',
                 asynchronous=False)
    n.add_notification('New', 'New email received.')
    n.add_notification('Old', 'Old as an old thing.')
    return n


def test_GNTP_Synchronous_Register(local_target, notifier):
    request = RegisterRequest(notifier)
    response = send_request(request, local_target)
    assert response.status == 'OK'


def test_GNTP_Synchronous_Notification(local_target, notifier):
    request = RegisterRequest(notifier)
    _response = send_request(request, local_target)

    notification = Notification(title='A brave new world',
                                text='Say hello to Prism')
    notification.name = 'New'
    logging.debug('GNTP: notify')
    request = NotifyRequest(notification, notifier)
    response = send_request(request, local_target)
    assert response.status == 'OK'
    assert response.status_code == 0
