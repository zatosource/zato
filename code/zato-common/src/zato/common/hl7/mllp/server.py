# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.hl7.exception import HL7Exception
from zato.common.hl7.mllp.ack import build_ack
from zato.common.hl7.mllp.codec import FrameDecoder, frame_encode
from zato.common.hl7.mllp.dedup import MessageDeduplicator, extract_control_id
from zato.common.hl7.mllp.preprocess import BatchPayload, preprocess_message
from zato.common.hl7.mllp.router import HL7MessageRouter
from zato_hl7v2 import parse_message as hl7_parse_message

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

TTL_Multipliers = {
    'minutes': 60,
    'hours':   3600,
    'days':    86400,
}

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
    the pre-processing pipeline, routes them to the appropriate service via the message router,
    and sends back MLLP-framed ACKs.
    """

    def __init__(
        self,
        address:'str',
        router:'HL7MessageRouter',
        start_sequence:'bytes',
        end_sequence:'bytes',
        *,
        receive_timeout:'float' = _Default_Receive_Timeout_Seconds,
        max_message_size:'int' = _Default_Max_Message_Size,
        read_buffer_size:'int' = _Default_Read_Buffer_Size,
        should_log_messages:'bool' = False,
        should_return_errors:'bool' = False,
        should_parse_on_input:'bool' = True,
        keepalive_idle:'int' = _Default_Keepalive_Idle_Seconds,
        keepalive_interval:'int' = _Default_Keepalive_Interval_Seconds,
        keepalive_probe_count:'int' = _Default_Keepalive_Probe_Count,
        should_normalize_line_endings:'bool' = True,
        should_repair_truncated_msh:'bool' = True,
        should_split_concatenated_messages:'bool' = True,
        should_force_standard_delimiters:'bool' = True,
        should_use_msh18_encoding:'bool' = True,
        default_character_encoding:'str' = 'utf-8',
        should_validate:'bool' = False,
        dedup_ttl_value:'int' = 0,
        dedup_ttl_unit:'str' = '',
        normalize_obx2_value_type:'bool' = True,
        replace_invalid_obx2_value_type:'bool' = True,
        normalize_invalid_escape_sequences:'bool' = True,
        normalize_obx8_abnormal_flags:'bool' = True,
        normalize_quadruple_quoted_empty:'bool' = True,
        allow_short_encoding_characters:'bool' = True,
        fix_off_by_one_field_index:'bool' = False,
        ) -> 'None':

        self.address = address
        self.router  = router
        self.start_sequence = start_sequence
        self.end_sequence   = end_sequence

        self.receive_timeout  = receive_timeout
        self.max_message_size = max_message_size
        self.read_buffer_size = read_buffer_size
        self.should_log_messages   = should_log_messages
        self.should_return_errors  = should_return_errors
        self.should_parse_on_input = should_parse_on_input
        self.should_validate       = should_validate

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

        # Build the Rust-level parser tolerance config from channel settings ..
        from zato_hl7v2_rs import ToleranceConfig
        tolerance_config = ToleranceConfig()
        tolerance_config.normalize_obx2_value_type          = normalize_obx2_value_type
        tolerance_config.replace_invalid_obx2_value_type    = replace_invalid_obx2_value_type
        tolerance_config.normalize_invalid_escape_sequences = normalize_invalid_escape_sequences
        tolerance_config.normalize_obx8_abnormal_flags      = normalize_obx8_abnormal_flags
        tolerance_config.normalize_quadruple_quoted_empty   = normalize_quadruple_quoted_empty
        tolerance_config.allow_short_encoding_characters    = allow_short_encoding_characters
        tolerance_config.fix_off_by_one_field_index         = fix_off_by_one_field_index
        self.tolerance_config = tolerance_config

        # Deduplication - only active when both ttl_value and ttl_unit are provided
        if dedup_ttl_value and dedup_ttl_unit:
            multiplier = TTL_Multipliers[dedup_ttl_unit]
            ttl_seconds = dedup_ttl_value * multiplier
            self._deduplicator = MessageDeduplicator(ttl_seconds)
        else:
            self._deduplicator:'MessageDeduplicator | None' = None

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
                break

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

        # .. set receive timeout ..
        client_socket.settimeout(self.receive_timeout)

        logger.info('HL7 MLLP connection from %s:%d', connection_context.peer_ip, connection_context.peer_port)

        decoder = FrameDecoder(self.start_sequence, self.end_sequence, self.max_message_size)

        try:

            while self._keep_running:

                # Read a chunk of data ..
                try:
                    chunk = client_socket.recv(self.read_buffer_size)
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
                    self._handle_message(client_socket, message_bytes, connection_context)

        finally:

            try:
                client_socket.shutdown(socket.SHUT_WR)
            except OSError:
                pass

            client_socket.close()
            logger.info('HL7 MLLP connection closed from %s:%d (messages: %d)',
                connection_context.peer_ip, connection_context.peer_port,
                connection_context.total_messages_received)

# ################################################################################################################################

    def _extract_first_msh_line(self, data:'str') -> 'str':
        """ Finds the first MSH segment line inside a batch/file payload.
        Used for routing and ACK building when the frame is a batch.
        """

        # .. scan through CR-delimited segments looking for the first MSH ..
        for line in data.split('\r'):
            if line.startswith('MSH|'):
                return line

        return ''

# ################################################################################################################################

    def _handle_batch_payload(
        self,
        active_socket:'socket.socket',
        batch_payload:'BatchPayload',
        connection_context:'ConnectionContext',
        ) -> 'None':
        """ Processes a batch/file payload (BHS|... or FHS|...) as a single unit.
        Routes using the first MSH found inside the batch, then passes the entire
        raw batch string to the matched service callback.
        """

        raw = batch_payload.raw

        # .. extract the first MSH line inside the batch for routing and ACK building,
        # .. because routing is always keyed off MSH fields even for batches ..
        msh_line = self._extract_first_msh_line(raw)

        # .. if the batch contains no MSH at all, there is nothing to route or ACK ..
        if not msh_line:
            logger.warning('Batch payload from %s:%d contains no MSH segment',
                connection_context.peer_ip, connection_context.peer_port)
            return

        if self.should_log_messages:
            logger.info('Processing batch payload (%d bytes) from %s:%d',
                len(raw), connection_context.peer_ip, connection_context.peer_port)

        # .. find the matching route using the first MSH ..
        matched_route = self.router.match(msh_line)

        # .. no route found - reject the entire batch ..
        if matched_route is None:
            logger.warning('No matching MLLP channel for batch from %s:%d (MSH: %s)',
                connection_context.peer_ip, connection_context.peer_port, msh_line[:80])
            ack_code = 'AR'
            error_text = 'No matching channel for this batch'

        # .. route found - pass the entire raw batch to the service callback,
        # .. the service is responsible for calling parse_batch_or_file on it ..
        else:

            if self.should_log_messages:
                logger.info('Routing batch to channel `%s` (service `%s`)',
                    matched_route.channel_name, matched_route.service_name)

            # .. invoke the callback with the raw batch string ..
            try:
                _ = matched_route.callback(raw)
                ack_code = 'AA'
                error_text = ''
            except Exception:
                logger.warning('Service callback error for batch on channel `%s` from %s:%d; e:`%s`',
                    matched_route.channel_name, connection_context.peer_ip, connection_context.peer_port, format_exc())
                ack_code = 'AE'
                error_text = 'Internal processing error'

        # .. suppress error details if the channel is configured to hide them ..
        if not self.should_return_errors:
            error_text = ''

        # .. build the ACK using the first MSH from the batch ..
        ack_string = build_ack(msh_line, ack_code, error_text=error_text)

        # .. encode and frame the ACK for MLLP transport ..
        ack_bytes = ack_string.encode(self.default_character_encoding)
        framed_ack = frame_encode(ack_bytes, self.start_sequence, self.end_sequence)

        # .. send the framed ACK back to the sender ..
        try:
            active_socket.sendall(framed_ack)
        except (BrokenPipeError, ConnectionResetError):
            logger.warning('Could not send ACK to %s:%d - connection lost',
                connection_context.peer_ip, connection_context.peer_port)

# ################################################################################################################################

    def _handle_message(
        self,
        active_socket:'socket.socket',
        raw_message_bytes:'bytes',
        connection_context:'ConnectionContext',
        ) -> 'None':
        """ Processes a single unframed HL7 message: pre-process, route to service, send ACK.
        """

        connection_context.total_messages_received += 1

        if self.should_log_messages:
            logger.info('Received message #%d (%d bytes) from %s:%d',
                connection_context.total_messages_received, len(raw_message_bytes),
                connection_context.peer_ip, connection_context.peer_port)

        # Run the pre-processing pipeline ..
        preprocessed = preprocess_message(
            raw_message_bytes,
            should_normalize_line_endings=self.should_normalize_line_endings,
            should_repair_truncated_msh=self.should_repair_truncated_msh,
            should_split_concatenated_messages=self.should_split_concatenated_messages,
            should_force_standard_delimiters=self.should_force_standard_delimiters,
            should_use_msh18_encoding=self.should_use_msh18_encoding,
            default_character_encoding=self.default_character_encoding,
        )

        # .. if the payload is a batch/file, handle it as a single unit ..
        if isinstance(preprocessed, BatchPayload):
            self._handle_batch_payload(active_socket, preprocessed, connection_context)
            return

        # .. process each message (usually just one, unless concatenated) ..
        for message_text in preprocessed:

            # .. extract the MSH line for routing and ACK building ..
            first_cr = message_text.find('\r')

            if first_cr == -1:
                msh_line = message_text
            else:
                msh_line = message_text[:first_cr]

            # .. if deduplication is enabled, check whether this message was already seen
            # .. within the configured TTL window. Duplicates are acknowledged with AA
            # .. but the service callback is not invoked.
            if self._deduplicator:

                # .. extract the message control ID (MSH-10) which serves as the dedup key ..
                control_id = extract_control_id(msh_line)

                # .. only deduplicate if the message actually has a control ID ..
                if control_id:

                    # .. check the cache - returns True if this control ID was seen before ..
                    if self._deduplicator.is_duplicate(control_id):

                        # .. log the duplicate if message logging is on ..
                        if self.should_log_messages:
                            logger.info('Duplicate message (MSH-10: %s) from %s:%d, skipping',
                                control_id, connection_context.peer_ip, connection_context.peer_port)

                        # .. build an AA ACK so the sender knows we received it ..
                        ack_string = build_ack(msh_line, 'AA')

                        # .. encode using the channel's configured character encoding ..
                        ack_bytes = ack_string.encode(self.default_character_encoding)

                        # .. wrap in MLLP framing before sending ..
                        framed_ack = frame_encode(ack_bytes, self.start_sequence, self.end_sequence)

                        # .. send the ACK back to the sender, ignoring broken connections ..
                        try:
                            active_socket.sendall(framed_ack)
                        except (BrokenPipeError, ConnectionResetError):
                            pass

                        # .. skip routing and service invocation for this duplicate ..
                        continue

            # .. find the matching route for this message ..
            matched_route = self.router.match(msh_line)

            if matched_route is None:
                logger.warning('No matching MLLP channel for message from %s:%d (MSH: %s)',
                    connection_context.peer_ip, connection_context.peer_port, msh_line[:80])
                ack_code = 'AR'
                error_text = 'No matching channel for this message'

            # .. invoke the matched route's callback ..
            else:

                if self.should_log_messages:
                    logger.info('Routing message to channel `%s` (service `%s`)',
                        matched_route.channel_name, matched_route.service_name)

                # .. when should_parse_on_input is enabled, parse the raw ER7 text
                # .. into a structured HL7Message object. If should_validate is also
                # .. enabled, the parser runs validation and raises on errors.
                # .. On success the callback receives the parsed object, otherwise
                # .. it receives the raw ER7 string.
                if self.should_parse_on_input:

                    # .. attempt to parse (and optionally validate) the message ..
                    try:
                        callback_data = hl7_parse_message(
                            message_text, validate=self.should_validate, tolerance=self.tolerance_config)

                    # .. parsing or validation failed - send an AE reject ACK
                    # .. back to the sender and skip this message ..
                    except ValueError:
                        logger.warning('Parse/validation error for channel `%s` from %s:%d; e:`%s`',
                            matched_route.channel_name, connection_context.peer_ip, connection_context.peer_port, format_exc())
                        ack_code = 'AE'
                        error_text = 'Message parsing or validation failed'

                        # .. suppress error details if the channel hides them ..
                        if not self.should_return_errors:
                            error_text = ''

                        # .. build, frame and send the reject ACK ..
                        ack_string = build_ack(msh_line, ack_code, error_text=error_text)
                        ack_bytes = ack_string.encode(self.default_character_encoding)
                        framed_ack = frame_encode(ack_bytes, self.start_sequence, self.end_sequence)

                        try:
                            active_socket.sendall(framed_ack)
                        except (BrokenPipeError, ConnectionResetError):
                            pass

                        # .. skip to the next message in the batch ..
                        continue

                # .. parsing not enabled - pass the raw ER7 string to the callback ..
                else:
                    callback_data = message_text

                # .. invoke the matched route's service callback ..
                try:
                    _ = matched_route.callback(callback_data)
                    ack_code = 'AA'
                    error_text = ''

                # .. service raised an exception - report it as an application error ..
                except Exception:
                    logger.warning('Service callback error for channel `%s` from %s:%d; e:`%s`',
                        matched_route.channel_name, connection_context.peer_ip, connection_context.peer_port, format_exc())
                    ack_code = 'AE'
                    error_text = 'Internal processing error'

            # .. suppress error details if configured to not return errors ..
            if not self.should_return_errors:
                error_text = ''

            # .. build and frame the ACK ..
            ack_string = build_ack(msh_line, ack_code, error_text=error_text)
            ack_bytes = ack_string.encode(self.default_character_encoding)
            framed_ack = frame_encode(ack_bytes, self.start_sequence, self.end_sequence)

            # .. send the framed ACK back.
            try:
                active_socket.sendall(framed_ack)
            except (BrokenPipeError, ConnectionResetError):
                logger.warning('Could not send ACK to %s:%d - connection lost',
                    connection_context.peer_ip, connection_context.peer_port)

# ################################################################################################################################
# ################################################################################################################################
