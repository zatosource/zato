# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from logging import getLogger
from traceback import format_exc

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

        # Zato
        from zato.common.util.api import hex_sequence_to_bytes

        self.config = config
        self.name = config.name
        self.address = config.address
        self.max_wait_time = int(config.max_wait_time) # type: float
        self.max_msg_size = int(config.max_msg_size) # type: int
        self.read_buffer_size = int(config.read_buffer_size) # type: int
        self.recv_timeout = int(config.recv_timeout) / 1000.0 # type: float
        self.should_log_messages = config.should_log_messages # type: bool

        self.start_seq = hex_sequence_to_bytes(config.start_seq)
        self.end_seq   = hex_sequence_to_bytes(config.end_seq)

        self.host, self.port = parse_address(self.address) # type (str, int)

    def send(self, data, _socket_socket=socket.socket, _family=socket.AF_INET, _type=socket.SOCK_STREAM):
        # type: (bytes) -> bytes

        try:

            data = data if isinstance(data, bytes) else data.encode('utf8')

            # Wrap the message in an MLLP envelope
            msg = self.start_seq + data + self.end_seq

            # This will auto-close the socket ..
            with _socket_socket(_family, _type) as sock:

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

def send_data(address, data):
    """ Sends input data to a remote address by its configuration.
    """
    # type: (bytes, str) -> bytes

    # Bunch
    from bunch import bunchify

    config = bunchify({
        'name': 'My HL7MLLPClient',
        'address': address,
        'start_seq': '0b',
        'end_seq': '1c 0d',
        'max_wait_time': 3,
        'max_msg_size': 2_000_000,
        'read_buffer_size': 2048,
        'recv_timeout': 250,
        'should_log_messages': True,
    })

    client = HL7MLLPClient(config)
    response = client.send(data)

    return response

# ################################################################################################################################
