# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import ssl
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.hl7.exception import HL7Exception
from zato.common.hl7.mllp.ack import build_ack
from zato.common.hl7.mllp.codec import FrameDecoder, frame_encode
from zato.common.hl7.mllp.preprocess import preprocess_message

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Default_Receive_Timeout_Seconds    = 30.0
_Default_Max_Message_Size           = 2_000_000
_Default_Read_Buffer_Size           = 4096
_Default_Keepalive_Idle_Seconds     = 60
_Default_Keepalive_Interval_Seconds = 10
_Default_Keepalive_Probe_Count      = 6

# ################################################################################################################################
# ################################################################################################################################

class ConnectionContext:
    """ Per-connection metadata.
    """
    def __init__(self, peer_address:'tuple[str, int]') -> 'None':
        self.peer_ip   = peer_address[0]
        self.peer_port = peer_address[1]
        self.total_messages_received = 0

# ################################################################################################################################
# ################################################################################################################################

class HL7MLLPServer:
    """ A gevent-based HL7 MLLP TCP server.
    Accepts connections, reads MLLP-framed messages, runs them through
    the pre-processing pipeline, invokes a callback, and sends back MLLP-framed ACKs.
    """

    def __init__(
        self,
        address:'str',
        callback_func:'callable_',
        start_sequence:'bytes',
        end_sequence:'bytes',
        *,
        receive_timeout:'float' = _Default_Receive_Timeout_Seconds,
        max_message_size:'int' = _Default_Max_Message_Size,
        read_buffer_size:'int' = _Default_Read_Buffer_Size,
        should_log_messages:'bool' = False,
        should_parse_on_input:'bool' = True,
        ssl_context:'ssl.SSLContext | None' = None,
        keepalive_idle:'int' = _Default_Keepalive_Idle_Seconds,
        keepalive_interval:'int' = _Default_Keepalive_Interval_Seconds,
        keepalive_probe_count:'int' = _Default_Keepalive_Probe_Count,
        should_normalize_line_endings:'bool' = True,
        should_repair_truncated_msh:'bool' = True,
        should_split_concatenated_messages:'bool' = True,
        should_force_standard_delimiters:'bool' = True,
        should_use_msh18_encoding:'bool' = True,
        default_character_encoding:'str' = 'utf-8',
        ) -> 'None':

        self.address        = address
        self.callback_func  = callback_func
        self.start_sequence = start_sequence
        self.end_sequence   = end_sequence

        self.receive_timeout  = receive_timeout
        self.max_message_size = max_message_size
        self.read_buffer_size = read_buffer_size
        self.should_log_messages    = should_log_messages
        self.should_parse_on_input  = should_parse_on_input
        self.ssl_context = ssl_context

        self.keepalive_idle        = keepalive_idle
        self.keepalive_interval    = keepalive_interval
        self.keepalive_probe_count = keepalive_probe_count

        # Pre-processing toggles
        self.should_normalize_line_endings      = should_normalize_line_endings
        self.should_repair_truncated_msh        = should_repair_truncated_msh
        self.should_split_concatenated_messages = should_split_concatenated_messages
        self.should_force_standard_delimiters   = should_force_standard_delimiters
        self.should_use_msh18_encoding          = should_use_msh18_encoding
        self.default_character_encoding         = default_character_encoding

        self._keep_running    = True
        self._server_socket:'socket.socket | None' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Binds and starts listening for MLLP connections.
        """

        # Parse host:port from the address string ..
        host, port_string = self.address.rsplit(':', 1)
        port = int(port_string)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(128)

        self._server_socket = server_socket

        logger.info('HL7 MLLP server listening on %s', self.address)

        while self._keep_running:

            try:
                server_socket.settimeout(1.0)
                client_socket, peer_address = server_socket.accept()
            except socket.timeout:
                continue
            except OSError:
                # Socket was closed during shutdown
                break

            # Handle the connection (in a real Zato deployment this would be a greenlet)
            try:
                self._handle_connection(client_socket, peer_address)
            except Exception:
                logger.warning('Error handling connection from %s:%s; e:`%s`', peer_address[0], peer_address[1], format_exc())

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Signals the server to stop accepting new connections and closes the listener.
        """
        self._keep_running = False

        if self._server_socket:
            self._server_socket.close()

        logger.info('HL7 MLLP server stopped')

# ################################################################################################################################

    def _handle_connection(self, client_socket:'socket.socket', peer_address:'tuple[str, int]') -> 'None':
        """ Handles a single persistent MLLP connection.
        Reads framed messages in a loop until the remote end disconnects.
        """

        connection_context = ConnectionContext(peer_address)

        # Set TCP keepalive ..
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, self.keepalive_idle)
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, self.keepalive_interval)
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, self.keepalive_probe_count)

        # .. wrap with TLS if configured ..
        if self.ssl_context:
            active_socket = self.ssl_context.wrap_socket(client_socket, server_side=True)
        else:
            active_socket = client_socket

        # .. set receive timeout ..
        active_socket.settimeout(self.receive_timeout)

        logger.info('HL7 MLLP connection from %s:%d', connection_context.peer_ip, connection_context.peer_port)

        decoder = FrameDecoder(self.start_sequence, self.end_sequence, self.max_message_size)

        try:

            while self._keep_running:

                # Read a chunk of data ..
                try:
                    chunk = active_socket.recv(self.read_buffer_size)
                except socket.timeout:
                    continue
                except (ConnectionResetError, BrokenPipeError):
                    break

                # .. remote end disconnected ..
                if not chunk:
                    break

                decoder.feed(chunk)

                # .. extract all complete messages from the buffer ..
                while True:

                    try:
                        message_bytes = decoder.next_message()
                    except HL7Exception as exception:
                        logger.warning('Frame error from %s:%d - %s',
                            connection_context.peer_ip, connection_context.peer_port, exception)
                        break

                    if message_bytes is None:
                        break

                    # .. process each extracted message ..
                    self._handle_message(active_socket, message_bytes, connection_context)

        finally:

            try:
                active_socket.shutdown(socket.SHUT_WR)
            except OSError:
                pass

            active_socket.close()
            logger.info('HL7 MLLP connection closed from %s:%d (messages: %d)',
                connection_context.peer_ip, connection_context.peer_port,
                connection_context.total_messages_received)

# ################################################################################################################################

    def _handle_message(
        self,
        active_socket:'socket.socket',
        raw_message_bytes:'bytes',
        connection_context:'ConnectionContext',
        ) -> 'None':
        """ Processes a single unframed HL7 message: pre-process, invoke callback, send ACK.
        """

        connection_context.total_messages_received += 1

        if self.should_log_messages:
            logger.info('Received message #%d (%d bytes) from %s:%d',
                connection_context.total_messages_received, len(raw_message_bytes),
                connection_context.peer_ip, connection_context.peer_port)

        # Run the pre-processing pipeline ..
        cleaned_messages = preprocess_message(
            raw_message_bytes,
            should_normalize_line_endings=self.should_normalize_line_endings,
            should_repair_truncated_msh=self.should_repair_truncated_msh,
            should_split_concatenated_messages=self.should_split_concatenated_messages,
            should_force_standard_delimiters=self.should_force_standard_delimiters,
            should_use_msh18_encoding=self.should_use_msh18_encoding,
            default_character_encoding=self.default_character_encoding,
        )

        # .. process each message (usually just one, unless concatenated) ..
        for message_text in cleaned_messages:

            # .. extract the MSH line for ACK building ..
            first_cr = message_text.find('\r')

            if first_cr == -1:
                msh_line = message_text
            else:
                msh_line = message_text[:first_cr]

            # .. invoke the callback and build an ACK based on the outcome ..
            try:
                _ = self.callback_func(message_text)
                ack_code = 'AA'
                error_text = ''
            except Exception:
                logger.warning('Service callback error for message from %s:%d; e:`%s`',
                    connection_context.peer_ip, connection_context.peer_port, format_exc())
                ack_code = 'AE'
                error_text = 'Internal processing error'

            # .. build and frame the ACK ..
            ack_string = build_ack(msh_line, ack_code, error_text=error_text)
            ack_bytes = ack_string.encode('utf-8')
            framed_ack = frame_encode(ack_bytes, self.start_sequence, self.end_sequence)

            # .. send the framed ACK back (sendall prevents partial writes) ..
            try:
                active_socket.sendall(framed_ack)
            except (BrokenPipeError, ConnectionResetError):
                logger.warning('Could not send ACK to %s:%d - connection lost',
                    connection_context.peer_ip, connection_context.peer_port)

# ################################################################################################################################
# ################################################################################################################################
