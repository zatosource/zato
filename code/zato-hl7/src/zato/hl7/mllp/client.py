# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import socket
from socket import timeout as SocketTimeoutException

# Bunch
from bunch import bunchify

# Zato
from zato.common.util.api import parse_tcp_address

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from gevent._socket3 import socket

    Bunch = Bunch
    socket = socket

# ################################################################################################################################
# ################################################################################################################################

class Client:
    """ An HL7 MLLP client for sending data to remote endpoints.
    """
    __slots__ = 'config', 'address', 'start_seq', 'end_seq', 'host', 'port'

    def __init__(self, config):
        # type: (Bunch) -> None
        self.config = config
        self.address = config.address

        self.start_seq = config.start_seq
        self.end_seq   = config.end_seq

        self.host, self.port = parse_tcp_address(self.address) # type (str, int)

    def send(self, data):
        # type: (bytes) -> bytes

        # Wrap the message in an MLLP envelope
        msg = self.start_seq + data + self.end_seq

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        sock.send(msg)

# ################################################################################################################################
# ################################################################################################################################

def send_data(address, data):
    """ Sends input data to a remote address.
    """
    # type: (bytes, str) -> bytes

    config = bunchify({
        'address': address,
        'start_seq': b'\x0b',
        'end_seq': b'\x1c\x0d'
    })

    client = Client(config)
    response = client.send(data)

    return response

# ################################################################################################################################
