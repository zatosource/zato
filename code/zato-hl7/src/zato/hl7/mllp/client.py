# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from logging import getLogger
from traceback import format_exc

# Bunch
from bunch import bunchify

# Zato
from zato.common.util.api import new_cid
from zato.common.util.tcp import parse_address, read_from_socket, SocketReaderCtx

# ################################################################################################################################

if 0:
    from bunch import Bunch

    Bunch = Bunch

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class HL7MLLPClient:
    """ An HL7 MLLP client for sending data to remote endpoints.
    """
    __slots__ = 'config', 'name', 'address', 'max_wait_time', 'max_msg_size', 'read_buffer_size', 'recv_timeout', \
        'should_log_messages', 'start_seq', 'end_seq', 'host', 'port', 'reader'

    def __init__(self, config):
        # type: (Bunch) -> None
        self.config = config
        self.name = config.name
        self.address = config.address
        self.max_wait_time = config.max_wait_time # type: float
        self.max_msg_size = config.max_msg_size # type: int
        self.read_buffer_size = config.read_buffer_size # type: int
        self.recv_timeout = config.recv_timeout # type: int
        self.should_log_messages = config.should_log_messages # type: bool

        self.start_seq = config.start_seq
        self.end_seq   = config.end_seq

        self.host, self.port = parse_address(self.address) # type (str, int)

    def send(self, data):
        # type: (bytes) -> bytes

        try:

            # Wrap the message in an MLLP envelope
            msg = self.start_seq + data + self.end_seq

            # This will auto-close the socket ..
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

                # .. connect to the remote end ..
                sock.connect((self.host, self.port))

                # .. send our data ..
                sock.send(msg)

                # .. encapsulate configuration for our socket reader function ..
                ctx = SocketReaderCtx(
                    new_cid(),
                    sock,
                    self.max_wait_time,
                    self.max_msg_size,
                    self.read_buffer_size,
                    self.recv_timeout,
                    self.should_log_messages
                )

                # .. wait for the response ..
                response = read_from_socket(ctx)

                if self.should_log_messages:
                    logger.info('Response received `%s`', response)

                return response

        except Exception:
            logger.warn('Client caught an exception while sending HL7 MLLP data to `%s (%s)`; e:`%s`',
                self.name, self.address, format_exc())
            raise

# ################################################################################################################################
# ################################################################################################################################

def send_data(data, config):
    """ Sends input data to a remote address by its configuration.
    """
    # type: (bytes, dict) -> bytes

    '''
    config = bunchify({
        'name': 'My HL7MLLPClient',
        'address': address,
        'start_seq': b'\x0b',
        'end_seq': b'\x1c\x0d',
        'max_wait_time': 3,
        'max_msg_size': 2_000_000,
        'read_buffer_size': 2048,
        'recv_timeout': 0.25,
        'should_log_messages': True,
    })
    '''

    client = HL7MLLPClient(config)
    response = client.send(data)

    return response

# ################################################################################################################################
