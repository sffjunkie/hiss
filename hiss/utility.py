# Copyright 2013-2014, Simon Kennedy, code@sffjunkie.co.uk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Part of 'hiss' the asynchronous notification library

import socket
import logging
from datetime import datetime

DATETIME_FORMATS = ['%d %b %Y %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%m-%d-%Y %H:%M:%S %p',
                    '%Y-%m-%d %H:%M:%SZ']

__all__ = ['find_local_address', 'xpl_format_source', 'xap_format_source',
    'format_ip_address', 'indent_text', 'indent_print', 'find_open_port',
    'ip_to_int', 'int_to_ip', 'find_broadcast', 'netmask_valid', 'guess_broadcast',
    'parse_datetime']

def indent_text(text, indent=4):
    out = ''
    for line in str(text).split('\n'):
        out = out + ' '*indent + line + '\n'

    return out


def indent_print(text, indent=4):
    print(indent_text(text, indent))


def find_hostname():
    return socket.gethostname()


def find_local_address():
    return socket.gethostbyname(socket.gethostname())


def find_open_port(from_port, interface='0.0.0.0'):
    UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for port in range(from_port, from_port + 512):
        try:
            addr = (interface, port)
            UDPSock.bind(addr)
            break
        except:
            port += 1

    UDPSock.close()
    return port


def netmask_valid(netmask):
    elems = netmask.split('.')
    if len(elems) != 4:
        return False

    mask = 0
    for i in range(4):
        mask |= (int(elems[i]) << ((3 - i) * 8))

    neg = ~mask & 0xFFFFFFFF

    return (((neg + 1) & neg) == 0)


def ip_to_int(ip):
    elems = ip.split('.')

    num = 0
    for i in range(4):
        num |= (int(elems[i]) << ((3 - i) * 8))

    return num


def int_to_ip(num):
    ip = []
    for i in range(4):
        ip.append(str((num >> ((3 - i) * 8)) & 255))

    return '.'.join(ip)


def find_broadcast(ip, netmask):
    i = ip_to_int(str(ip))
    n = ip_to_int(str(netmask))

    return int_to_ip((n & i) | ~n)


def guess_broadcast(ip):
    elems = ip.split('.')

    if ip == '0.0.0.0':
        return '255.255.255.255'
    elif int(elems[0]) == 10:
        return '10.255.255.255'
    elif int(elems[0]) == 192 and int(elems[1]) == 168:
        return '192.168.%s.255' % elems[2]
    elif int(elems[0]) == 172 and int(elems[1]) == 16:
        return '172.31.255.255'
    elif int(elems[0]) == 169 and int(elems[1]) == 254:
        return '169.254.255.255'
    else:
        return find_broadcast(ip, '255.255.255.0')


def xpl_format_source(vendor, device, instance):
    return '%s-%s.%s' % (vendor, device, instance)


def xap_format_source(vendor, device, instance):
    return '%s.%s.%s' % (vendor, device, instance)


def format_ip_address(address):
    return ''.join(map(lambda n: "%03d" % int(n), address.split('.')))

           
def parse_datetime(string):
    for df in DATETIME_FORMATS:
        try:
            dt = datetime.strptime(string, df)
            return dt
        except:
            pass
    
    logging.debug('parse_datetime: Unable to parse datetime string %s' % string)
    return string
