# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
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
    from socket import AddressFamily, socket as Socket, SocketKind
    from bunch import Bunch
    from zato.common.typing_ import any_, type_
    type_ = type_
    AddressFamily = AddressFamily
    Socket = Socket
    SocketKind = SocketKind

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class HL7MLLPClient:
    """ An HL7 MLLP client for sending data to remote endpoints.
    """
    config: 'Bunch'
    name: 'str'
    address: 'str'
    max_wait_time: 'int'
    max_msg_size: 'int'
    read_buffer_size: 'int'
    recv_timeout: 'float'
    should_log_messages: 'bool'

    host: 'str'
    port: 'str'

    def __init__(self, config:'any_') -> 'None':

        # Zato
        from zato.common.util.api import hex_sequence_to_bytes

        self.config = config
        self.name = config.name
        self.address = config.address
        self.max_wait_time = int(config.max_wait_time)
        self.max_msg_size = int(config.max_msg_size)
        self.read_buffer_size = int(config.read_buffer_size)
        self.recv_timeout = int(config.recv_timeout) / 1000.0
        self.should_log_messages = config.should_log_messages

        self.start_seq = hex_sequence_to_bytes(config.start_seq)
        self.end_seq   = hex_sequence_to_bytes(config.end_seq)

        self.host, self.port = parse_address(self.address)

# ################################################################################################################################

    def send(
        self,
        data, # type: bytes | str
        _socket_socket=socket.socket, # type: type_[Socket]
        _family=socket.AF_INET,       # type: AddressFamily
        _type=socket.SOCK_STREAM      # type: SocketKind
    ) -> 'bytes':

        try:

            data = data if isinstance(data, bytes) else data.encode('utf8')

            # Wrap the message in an MLLP envelope
            msg = self.start_seq + data + self.end_seq

            # This will auto-close the socket ..
            with _socket_socket(_family, _type) as sock:

                # .. connect to the remote end ..
                sock.connect((self.host, self.port))

                # .. send our data ..
                _ = sock.send(msg)

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
            logger.warning('Client caught an exception while sending HL7 MLLP data to `%s (%s)`; e:`%s`',
                self.name, self.address, format_exc())
            raise

# ################################################################################################################################
# ################################################################################################################################

def send_data(address:'str', data:'bytes') -> 'bytes':
    """ Sends input data to a remote address by its configuration.
    """
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
# ################################################################################################################################

if __name__ == '__main__':

    import logging
    from zato.common.api import HL7
    from zato.common.test.hl7_ import test_data

    log_level = logging.DEBUG
    log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=log_level, format=log_format)

    logger = logging.getLogger(__name__)

    channel_port = HL7.Default.channel_port
    address = f'localhost:{channel_port}'

    logger.info('Sending HL7v2 to %s', address)

    _ = send_data(address, test_data)

# ################################################################################################################################
# ################################################################################################################################
