# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import ssl
from logging import getLogger

# Zato
from zato.common.hl7.exception import HL7Exception
from zato.common.hl7.mllp.ack import AckResult, validate_ack
from zato.common.hl7.mllp.codec import FrameDecoder, frame_encode

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Default_Connect_Timeout_Seconds   = 5
_Default_Receive_Timeout_Seconds   = 30.0
_Default_Max_Message_Size          = 2_000_000
_Default_Read_Buffer_Size          = 4096

# ################################################################################################################################
# ################################################################################################################################

class HL7MLLPClient:
    """ An HL7 MLLP client for sending framed messages to remote endpoints
    and receiving validated ACK responses.
    """

    def __init__(
        self,
        host:'str',
        port:'int',
        start_sequence:'bytes',
        end_sequence:'bytes',
        *,
        connect_timeout:'int' = _Default_Connect_Timeout_Seconds,
        receive_timeout:'float' = _Default_Receive_Timeout_Seconds,
        max_message_size:'int' = _Default_Max_Message_Size,
        read_buffer_size:'int' = _Default_Read_Buffer_Size,
        should_log_messages:'bool' = False,
        ssl_context:'ssl.SSLContext | None' = None,
        server_hostname:'str' = '',
        ) -> 'None':

        self.host = host
        self.port = port
        self.start_sequence = start_sequence
        self.end_sequence   = end_sequence

        self.connect_timeout   = connect_timeout
        self.receive_timeout   = receive_timeout
        self.max_message_size  = max_message_size
        self.read_buffer_size  = read_buffer_size
        self.should_log_messages = should_log_messages

        self.ssl_context     = ssl_context
        self.server_hostname = server_hostname

# ################################################################################################################################

    def send(self, data:'bytes', control_id:'str' = '') -> 'AckResult':
        """ Sends a framed HL7 message and returns a validated AckResult.
        """

        # Frame the outbound message ..
        framed_message = frame_encode(data, self.start_sequence, self.end_sequence)

        if self.should_log_messages:
            logger.info('Sending %d bytes to %s:%d', len(framed_message), self.host, self.port)

        # .. open a TCP connection with a connect timeout ..
        raw_socket = socket.create_connection(
            (self.host, self.port),
            timeout=self.connect_timeout,
        )

        try:

            # .. disable Nagle to avoid 200-500ms phantom latency ..
            raw_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            # .. wrap with TLS if configured ..
            if self.ssl_context:
                hostname = self.server_hostname if self.server_hostname else self.host
                active_socket = self.ssl_context.wrap_socket(raw_socket, server_hostname=hostname)
            else:
                active_socket = raw_socket

            # .. set the receive timeout for reading the ACK ..
            active_socket.settimeout(self.receive_timeout)

            # .. send the full framed message (sendall prevents silent truncation) ..
            active_socket.sendall(framed_message)

            # .. read the ACK response using FrameDecoder to handle TCP fragmentation ..
            ack_bytes = self._receive_ack(active_socket)

            if self.should_log_messages:
                logger.info('Received ACK: %d bytes', len(ack_bytes))

            # .. decode and validate the ACK ..
            ack_string = ack_bytes.decode('utf-8', errors='replace')

            if control_id:
                out = validate_ack(ack_string, control_id)
            else:
                out = AckResult()
                out.is_accepted = True
                out.ack_code = 'AA'

            return out

        finally:
            raw_socket.close()

# ################################################################################################################################

    def _receive_ack(self, active_socket:'socket.socket') -> 'bytes':
        """ Reads from the socket until a complete MLLP-framed ACK is received.
        Uses FrameDecoder to handle TCP fragmentation across multiple recv calls.
        """

        decoder = FrameDecoder(self.start_sequence, self.end_sequence, self.max_message_size)

        while True:

            try:
                chunk = active_socket.recv(self.read_buffer_size)
            except socket.timeout:
                raise HL7Exception('Timed out waiting for ACK response')

            # .. remote closed the connection without sending a complete ACK ..
            if not chunk:
                raise HL7Exception('Connection closed before receiving a complete ACK')

            decoder.feed(chunk)
            message = decoder.next_message()

            if message is not None:
                return message

# ################################################################################################################################
# ################################################################################################################################
