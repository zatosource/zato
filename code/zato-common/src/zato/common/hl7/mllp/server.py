# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket
from logging import getLogger
from time import monotonic
from traceback import format_exc

# gevent
from gevent import spawn
from gevent.lock import BoundedSemaphore

# Zato
from zato.common.hl7.audit import audit_ack_sent, audit_batch_received, audit_message_received, get_audit_attrs, \
    get_control_id, get_wire_attrs
from zato.common.hl7.exception import HL7Exception
from zato.common.hl7.mllp.ack import build_ack, Condition_Data_Type_Error, Condition_Unsupported_Message, ErrorCondition
from zato.common.hl7.mllp.codec import FrameReader, frame_encode
from zato.common.hl7.mllp.dedup import extract_control_id
from zato.common.hl7.mllp.preprocess import BatchPayload, preprocess_message
from zato.common.hl7.mllp.proxy_protocol import read_optional_proxy_header
from zato.common.hl7.mllp.router import HL7MessageRouter
from zato.common.hl7.mllp.settings import ListenerConfig, RouteSettings, is_address_allowed
from zato.common.hl7.mllp.state import ChannelState
from zato.common.util.api import new_cid_server

from zato.hl7v2 import HL7ValidationError, parse_hl7

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.hl7.mllp.router import ChannelRoute
    from zato.common.typing_ import any_

    AuditLog = AuditLog
    ChannelRoute = ChannelRoute
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How many milliseconds one second holds - used when converting callback durations
_ms_per_second = 1000

# Per-message trace diagnostics - opt-in through the environment because they log
# multiple lines per message, which is noise everywhere except a diagnostic run.
_is_trace_enabled = bool(os.environ.get('Zato_HL7_Trace'))

def _trace(message:'str', *args:'object') -> 'None':
    if _is_trace_enabled:
        logger.info('TRACE ' + message, *args)

# ################################################################################################################################
# ################################################################################################################################

# How long the accept loop waits before checking whether it has been told to stop
_Accept_Poll_Interval = 1.0

# What a sender is told when its connection is refused before any message was read
_Rejection_Ack_Code = 'AR'

# Where MSH-9, the message type, sits when the header is split on the field separator -
# a header with nothing there cannot be identified as any message at all
_MSH9_Field_Index = 8

# What a channel's own answer has to begin with to be sent back in place of a locally built
# acknowledgment. A channel that replies from one of its destinations answers with the
# acknowledgment that destination gave it, and everything else is not an answer at all.
_Reply_Segment_Prefix = 'MSH'

# What a message that matched no channel is filed under in the audit log - there is no channel
# whose name it could carry, yet a turned-away message is still worth finding afterwards
Unmatched_Object_Name = 'unmatched'

# ################################################################################################################################
# ################################################################################################################################

def _resolve_reply(callback_response:'any_', msh_line:'str', ack_code:'str', error_text:'str') -> 'str':
    """ Returns what the sender is answered with - the message the channel itself produced when it
    produced one, and otherwise an acknowledgment built here from the outcome of the delivery.
    """
    if isinstance(callback_response, str):
        if callback_response.startswith(_Reply_Segment_Prefix):
            return callback_response

    out = build_ack(msh_line, ack_code, error_text=error_text)
    return out

# ################################################################################################################################
# ################################################################################################################################

class ConnectionContext:
    """ Who is on one connection and what has come down it so far.
    """
    def __init__(self, client_ip:'str', client_port:'int', client_common_name:'str') -> 'None':

        # The sender's own address, as reported by the load balancer that accepted the connection
        self.client_ip = client_ip
        self.client_port = client_port

        # The common name of the client certificate that was verified, empty when there was none
        self.client_common_name = client_common_name

        self.total_messages_received = 0

    @property
    def endpoint(self) -> 'str':
        out = f'{self.client_ip}:{self.client_port}'
        return out

# ################################################################################################################################
# ################################################################################################################################

class HL7MLLPServer:
    """ A gevent-based HL7 MLLP TCP server.

    One listener serves every MLLP channel, with a greenlet per accepted connection. The listener
    owns only what a socket can have one of - where it binds, how many connections it serves at
    once, and the bounds that apply before a message has been matched to a channel. Everything
    about how a message is framed, read and interpreted belongs to the channel it matched and is
    derived per message rather than for the life of the connection.
    """

    def __init__(
        self,
        config:'ListenerConfig',
        router:'HL7MessageRouter',
        *,
        audit_log:'AuditLog | None' = None,
        ) -> 'None':

        self.config = config
        self.router = router

        # The shared audit log all audited channels write through -
        # whether a given message is audited is each route's own flag.
        self.audit_log = audit_log

        self._keep_running = True
        self._server_socket:'socket.socket | None' = None

        # What caps how many connections are served at once, the rest being refused rather than queued
        self._connection_semaphore = BoundedSemaphore(config.max_concurrent_connections)

        # The live state of the whole listener - counters and listener condition
        self.state = ChannelState(config.address)

        # The live state of each channel routed through this listener, keyed by channel name -
        # what zato.channel.hl7.get-current-state reads per channel.
        self.channel_states:'dict[str, ChannelState]' = {}

# ################################################################################################################################

    def start(self) -> 'None':
        """ Binds and starts listening for MLLP connections.
        """

        # Parse host:port from the address string ..
        host, port_string = self.config.address.rsplit(':', 1)
        port = int(port_string)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Every worker process of one server binds the same port and the kernel spreads
        # connections across them, which is what makes the port follow from the server's identity
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        server_socket.bind((host, port))
        server_socket.listen(self.config.accept_backlog)

        self._server_socket = server_socket
        self.state.on_listener_up()

        # Every channel shares the one listener, so its condition is theirs too
        for channel_state in self.channel_states.values():
            channel_state.on_listener_up()

        logger.info('HL7 MLLP server listening on %s', self.config.address)

        while self._keep_running:

            try:
                server_socket.settimeout(_Accept_Poll_Interval)
                client_socket, peer_address = server_socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            # One greenlet per connection, so that the second sender to connect is served
            # alongside the first rather than after it
            _ = spawn(self._serve_connection, client_socket, peer_address)

        # The accept loop is over, so nothing is listening anymore
        self.state.on_listener_down()

        for channel_state in self.channel_states.values():
            channel_state.on_listener_down()

# ################################################################################################################################

    def _serve_connection(self, client_socket:'socket.socket', peer_address:'tuple[str, int]') -> 'None':
        """ Runs one connection to completion under the concurrency limit, refusing it outright
        when the listener is already serving as many as it is allowed to.
        """

        # Waiting for a slot would leave the sender with an accepted connection nothing is reading,
        # which is worse than being told at once that there is no room
        if not self._connection_semaphore.acquire(blocking=False):

            logger.warning('Refused MLLP connection from %s:%s - at the %d connection limit',
                peer_address[0], peer_address[1], self.config.max_concurrent_connections)

            client_socket.close()
            return

        try:
            self._handle_connection(client_socket, peer_address)
        except Exception:
            logger.warning('Error handling connection from %s:%s; e:`%s`',
                peer_address[0], peer_address[1], format_exc())
        finally:
            _ = self._connection_semaphore.release()

# ################################################################################################################################

    def get_channel_state(self, channel_name:'str') -> 'ChannelState':
        """ Returns the live state of one channel, creating it on first use -
        a new channel inherits the listener's current condition.
        """
        if channel_name not in self.channel_states:

            channel_state = ChannelState(channel_name)

            if self.state.is_listening:
                channel_state.on_listener_up()

            self.channel_states[channel_name] = channel_state

        out = self.channel_states[channel_name]
        return out

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Signals the server to stop accepting new connections and closes the listener.
        """
        self._keep_running = False
        self.state.on_listener_down()

        for channel_state in self.channel_states.values():
            channel_state.on_listener_down()

        if self._server_socket:
            self._server_socket.close()

        logger.info('HL7 MLLP server stopped')

# ################################################################################################################################

    def _read_connection_identity(self, client_socket:'socket.socket', peer_address:'tuple[str, int]') -> 'tuple':
        """ Reads who is on the connection, along with whatever of its first message had to be
        read to find that out.

        A connection that came through the load balancer is announced by the header it is
        prefixed with, and one made straight to this socket is whoever the socket says it is.
        """

        # An opening that has not arrived within the listener's own deadline is not going to
        client_socket.settimeout(self.config.first_line_timeout)

        proxy_header, initial_bytes = read_optional_proxy_header(client_socket)

        # The load balancer reports the sender it accepted the connection from ..
        if proxy_header:
            out = ConnectionContext(proxy_header.client_ip, proxy_header.client_port, proxy_header.client_common_name)

        # .. and without one the sender is the peer of this socket, with no certificate to name
        # .. because there was no load balancer to verify one.
        else:
            out = ConnectionContext(peer_address[0], peer_address[1], '')

        return out, initial_bytes

# ################################################################################################################################

    def _apply_keepalive(self, client_socket:'socket.socket', settings:'RouteSettings') -> 'None':
        """ Applies the matched channel's keepalive settings, which is how often the kernel probes
        a connection that has gone quiet and how many unanswered probes end it.
        """
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, settings.keepalive_idle)
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, settings.keepalive_interval)
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, settings.keepalive_probe_count)

# ################################################################################################################################

    def _is_sender_allowed(self, route:'ChannelRoute', connection_context:'ConnectionContext') -> 'bool':
        """ Returns whether the channel a message matched accepts the connection it arrived on.
        """
        settings = route.settings

        # A channel with a security definition takes only the certificate that definition names,
        # and a connection that carried none has nothing to be matched
        if settings.security_common_name:
            if settings.security_common_name != connection_context.client_common_name:
                return False

        if not is_address_allowed(connection_context.client_ip, settings.allowed_networks):
            return False

        return True

# ################################################################################################################################

    def _send_framed(
        self,
        active_socket:'socket.socket',
        text:'str',
        settings:'RouteSettings',
        connection_context:'ConnectionContext',
        ) -> 'None':
        """ Frames a reply the way the matched channel frames its own and sends it back.
        """
        payload = text.encode(settings.default_character_encoding)
        framed = frame_encode(payload, settings.start_sequence, settings.end_sequence)

        try:
            active_socket.sendall(framed)
        except (BrokenPipeError, ConnectionResetError):
            logger.warning('Could not send ACK to %s - connection lost', connection_context.endpoint)

# ################################################################################################################################

    def _handle_connection(self, client_socket:'socket.socket', peer_address:'tuple[str, int]') -> 'None':
        """ Handles a single persistent MLLP connection.

        Each message is routed on its own first line and then read under the bounds of the channel
        it matched, so one message that matched a permissive channel never governs what is read
        after it down the same connection.
        """

        try:
            connection_context, initial_bytes = self._read_connection_identity(client_socket, peer_address)

        # A connection that ends before it opens is a health check on the port rather than a fault
        except HL7Exception as exception:
            logger.info('HL7 MLLP connection from %s:%s ended before it opened - %s',
                peer_address[0], peer_address[1], exception)
            client_socket.close()
            return

        logger.info('HL7 MLLP connection from %s', connection_context.endpoint)

        config = self.config

        # Whatever was read while identifying the sender belongs to its first message,
        # so the reader starts with it rather than with an empty buffer
        reader = FrameReader(client_socket, self.router.get_start_sequences(), config.read_buffer_size, initial_bytes)

        # Default settings for a frame that matched nothing, whose channel is by definition unknown
        unmatched_settings = RouteSettings()

        # Until a message matches a route the wait between messages is the listener's own,
        # because there is no channel yet whose idle deadline could apply instead
        idle_timeout = config.idle_timeout

        try:

            while self._keep_running:

                try:
                    msh_line = reader.read_first_line(
                        config.max_first_line_size, idle_timeout, config.first_line_timeout)

                except HL7Exception as exception:
                    self.state.on_error()
                    logger.warning('Framing error from %s - %s', connection_context.endpoint, exception)
                    break

                # .. the remote end disconnected between messages, which is how a feed ends ..
                except (ConnectionResetError, BrokenPipeError, socket.timeout):
                    break

                if msh_line is None:
                    break

                matched_route = self.router.match(msh_line)

                if matched_route is None:
                    settings = unmatched_settings
                    end_sequences = self.router.get_end_sequences()
                else:
                    settings = matched_route.settings
                    end_sequences = [settings.end_sequence]
                    self._apply_keepalive(client_socket, settings)

                    # From here on the wait between messages down this connection
                    # is the matched channel's own idle deadline
                    idle_timeout = settings.idle_timeout

                # .. the rest of the frame is read under whatever the matched channel allows,
                # .. which is what makes two senders down one connection read differently ..
                try:
                    message_bytes = reader.read_rest_of_frame(
                        end_sequences, settings.max_message_size, settings.recv_timeout)

                except HL7Exception as exception:

                    # An oversized or unterminated frame leaves the stream with no known boundary,
                    # so the sender is answered and the connection ends rather than resynchronising
                    self.state.on_error()
                    logger.warning('Frame error from %s - %s', connection_context.endpoint, exception)
                    self._reject_frame(client_socket, msh_line, settings, connection_context, 'AE',
                        'Message could not be read', Condition_Data_Type_Error)
                    break

                except (ConnectionResetError, BrokenPipeError):
                    break

                # .. a sender the matched channel does not accept is told so and nothing is invoked ..
                if matched_route is not None:
                    if not self._is_sender_allowed(matched_route, connection_context):
                        self._on_sender_refused(client_socket, msh_line, matched_route, connection_context)
                        continue

                self._handle_message(client_socket, message_bytes, connection_context, matched_route, settings)

        finally:

            try:
                client_socket.shutdown(socket.SHUT_WR)
            except OSError:
                pass

            client_socket.close()
            logger.info('HL7 MLLP connection closed from %s (messages: %d)',
                connection_context.endpoint, connection_context.total_messages_received)

# ################################################################################################################################

    def _reject_frame(
        self,
        active_socket:'socket.socket',
        msh_line:'str',
        settings:'RouteSettings',
        connection_context:'ConnectionContext',
        ack_code:'str',
        error_text:'str',
        error_condition:'ErrorCondition',
        ) -> 'None':
        """ Answers a frame that was never delivered anywhere, which is what a sender waiting on
        an acknowledgment needs rather than a connection that simply goes quiet.
        """
        self.state.on_nack_sent()

        if not settings.should_return_errors:
            error_text = ''

        ack_string = build_ack(msh_line, ack_code, error_text=error_text, error_condition=error_condition)
        self._send_framed(active_socket, ack_string, settings, connection_context)

# ################################################################################################################################

    def _on_sender_refused(
        self,
        active_socket:'socket.socket',
        msh_line:'str',
        route:'ChannelRoute',
        connection_context:'ConnectionContext',
        ) -> 'None':
        """ Records and answers a message whose channel does not accept the connection it came on.
        The refusal is attributed to the channel that matched, so it lands in that channel's
        counters and audit trail rather than nowhere.
        """
        channel_state = self.get_channel_state(route.channel_name)
        channel_state.on_message_received()
        self.state.on_message_received()

        logger.warning('Channel `%s` refused a message from %s', route.channel_name, connection_context.endpoint)

        settings = route.settings
        ack_string = build_ack(msh_line, _Rejection_Ack_Code, error_text='')

        self.state.on_nack_sent()
        channel_state.on_nack_sent()

        if self.audit_log and route.is_audit_log_active:
            _ = audit_ack_sent(
                self.audit_log, route.channel_name, _Rejection_Ack_Code, ack_string,
                cid=new_cid_server(), msg_id=extract_control_id(msh_line))

        self._send_framed(active_socket, ack_string, settings, connection_context)

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
        matched_route:'ChannelRoute | None',
        settings:'RouteSettings',
        ) -> 'None':
        """ Processes a batch/file payload (BHS|... or FHS|...) as a single unit.
        The whole batch belongs to the channel its frame matched, and the entire raw batch string
        is passed to that channel's callback.
        """

        raw = batch_payload.raw

        # .. the ACK is built from the first MSH inside the batch, the routing decision
        # .. having already been made on the frame's own first line ..
        msh_line = self._extract_first_msh_line(raw)

        # .. if the batch contains no MSH at all, there is nothing to ACK ..
        if not msh_line:
            self.state.on_error()
            logger.warning('Batch payload from %s contains no MSH segment', connection_context.endpoint)
            return

        if settings.should_log_messages:
            logger.info('Processing batch payload (%d bytes) from %s', len(raw), connection_context.endpoint)

        # .. a matched batch counts on its channel's own state too ..
        if matched_route:
            channel_state = self.get_channel_state(matched_route.channel_name)
            channel_state.on_message_received()
        else:
            channel_state = None

        # .. a batch is audited when its channel says so - with no route there is no channel to ask,
        # .. and the channel it is filed under is what says afterwards whether it was audited ..
        audit_log = self.audit_log
        audit_channel_name = ''

        # .. all the batch's audit events share one correlation id ..
        if audit_log and matched_route and matched_route.is_audit_log_active:

            audit_cid = new_cid_server()
            audit_channel_name = matched_route.channel_name

            # .. the parent row for the batch plus a child row per contained message ..
            _ = audit_batch_received(
                audit_log, audit_channel_name, raw,
                cid=audit_cid, endpoint=connection_context.endpoint)
        else:
            audit_cid = ''

        # .. no route found - reject the entire batch ..
        if matched_route is None:
            logger.warning('No matching MLLP channel for batch from %s (MSH: %s)',
                connection_context.endpoint, msh_line)
            callback_response = None
            ack_code = 'AR'
            error_text = 'No matching channel for this batch'

        # .. route found - pass the entire raw batch to the service callback,
        # .. the service is responsible for calling parse_batch_or_file on it ..
        else:

            if settings.should_log_messages:
                logger.info('Routing batch to channel `%s` (%s)',
                    matched_route.channel_name, matched_route.get_target())

            # .. invoke the callback with the raw batch string, under the correlation id the
            # .. batch's own rows were written with, so everything it leads to shares them ..
            try:
                callback_response = matched_route.callback(raw, audit_cid)
                ack_code = 'AA'
                error_text = ''
            except Exception:
                logger.warning('Service callback error for batch on channel `%s` from %s; e:`%s`',
                    matched_route.channel_name, connection_context.endpoint, format_exc())
                callback_response = None
                ack_code = 'AE'
                error_text = 'Internal processing error'

        # .. suppress error details if the channel is configured to hide them ..
        if not settings.should_return_errors:
            error_text = ''

        # .. the batch's acknowledgment outcome feeds the live state, the channel's own included ..
        if ack_code == 'AA':
            self.state.on_ack_sent()
            if channel_state:
                channel_state.on_ack_sent()
        else:
            self.state.on_nack_sent()
            if channel_state:
                channel_state.on_nack_sent()

        # .. build the ACK using the first MSH from the batch, unless the channel already
        # .. answered with a message of its own ..
        ack_string = _resolve_reply(callback_response, msh_line, ack_code, error_text)

        # .. one acknowledgment covers the entire batch, on the same cid as its rows ..
        if audit_log and audit_channel_name:
            _ = audit_ack_sent(
                audit_log, audit_channel_name, ack_code, ack_string,
                cid=audit_cid, msg_id=extract_control_id(msh_line))

        self._send_framed(active_socket, ack_string, settings, connection_context)

# ################################################################################################################################

    def _handle_duplicate(
        self,
        active_socket:'socket.socket',
        msh_line:'str',
        control_id:'str',
        settings:'RouteSettings',
        connection_context:'ConnectionContext',
        channel_name:'str',
        ) -> 'None':
        """ Answers a message the matched channel has already seen within its own TTL window.
        A duplicate is acknowledged positively and its callback is not invoked.
        """
        if settings.should_log_messages:
            logger.info('Duplicate message (MSH-10: %s) from %s, skipping', control_id, connection_context.endpoint)

        # A duplicate's acknowledgment feeds the live state, the channel's own included
        self.state.on_ack_sent()

        channel_state = self.get_channel_state(channel_name)
        channel_state.on_ack_sent()

        ack_string = build_ack(msh_line, 'AA')
        self._send_framed(active_socket, ack_string, settings, connection_context)

# ################################################################################################################################

    def _handle_message(
        self,
        active_socket:'socket.socket',
        raw_message_bytes:'bytes',
        connection_context:'ConnectionContext',
        matched_route:'ChannelRoute | None',
        settings:'RouteSettings',
        ) -> 'None':
        """ Processes a single unframed HL7 message under the settings of the channel it matched:
        pre-process, deliver, send ACK.
        """

        connection_context.total_messages_received += 1
        self.state.on_message_received()

        # Trace point 1: the message arrived and processing begins
        message_start = monotonic()
        _trace('message #%d in (%d bytes)', connection_context.total_messages_received, len(raw_message_bytes))

        if settings.should_log_messages:
            logger.info('Received message #%d (%d bytes) from %s',
                connection_context.total_messages_received, len(raw_message_bytes), connection_context.endpoint)

        # Run the pre-processing pipeline under the matched channel's own settings ..
        preprocessed = preprocess_message(
            raw_message_bytes,
            should_normalize_line_endings=settings.should_normalize_line_endings,
            should_restore_truncated_msh=settings.should_restore_truncated_msh,
            should_split_concatenated_messages=settings.should_split_concatenated_messages,
            should_force_standard_delimiters=settings.should_force_standard_delimiters,
            should_use_msh18_encoding=settings.should_use_msh18_encoding,
            default_character_encoding=settings.default_character_encoding,
        )

        # .. if the payload is a batch/file, handle it as a single unit ..
        if isinstance(preprocessed, BatchPayload):
            self._handle_batch_payload(active_socket, preprocessed, connection_context, matched_route, settings)
            return

        # .. process each message (usually just one, unless concatenated) ..
        for message_text in preprocessed:

            # .. extract the MSH line for ACK building ..
            first_cr = message_text.find('\r')

            if first_cr == -1:
                msh_line = message_text
            else:
                msh_line = message_text[:first_cr]

            # .. a channel with deduplication on answers a control id it has already seen
            # .. without invoking anything - only a matched route carries a deduplicator ..
            if matched_route:
                if settings.deduplicator:

                    control_id = extract_control_id(msh_line)

                    # .. only deduplicate if the message actually has a control ID ..
                    if control_id:
                        if settings.deduplicator.is_duplicate(control_id):
                            self._handle_duplicate(active_socket, msh_line, control_id, settings,
                                connection_context, matched_route.channel_name)
                            continue

            # .. a matched message counts on its channel's own state too ..
            if matched_route:
                channel_state = self.get_channel_state(matched_route.channel_name)
                channel_state.on_message_received()
            else:
                channel_state = None

            # .. a matched message is audited when its channel says so, and one that matched
            # .. nothing is always audited, filed under a reserved name of its own, since there
            # .. is no channel whose audit setting could be consulted ..
            audit_log = self.audit_log
            audit_channel_name = ''

            if audit_log:
                if matched_route is None:
                    audit_channel_name = Unmatched_Object_Name
                elif matched_route.is_audit_log_active:
                    audit_channel_name = matched_route.channel_name

            # .. the received event and its acknowledgment share one correlation id,
            # .. with the wire-level attributes as the fallback the parsed ones replace ..
            if audit_channel_name:
                audit_cid = new_cid_server()
                audit_msg_id = extract_control_id(msh_line)
                audit_attrs = get_wire_attrs(msh_line)
                peer_endpoint = connection_context.endpoint
            else:
                audit_cid = ''
                audit_msg_id = ''
                audit_attrs = {}
                peer_endpoint = ''

            # .. how long the service callback ran, reported on the acknowledgment's row ..
            callback_duration_ms = 0

            # .. what the channel answered with itself, when it answered at all ..
            callback_response = None

            if matched_route is None:
                logger.warning('No matching MLLP channel for message from %s (MSH: %s)',
                    connection_context.endpoint, msh_line)
                ack_code = 'AR'
                error_text = 'No matching channel for this message'

                # .. a turned-away message still leaves its receipt behind, the acknowledgment
                # .. that answers it landing on the same correlation id further below ..
                if audit_log and audit_channel_name:
                    _ = audit_message_received(
                        audit_log, audit_channel_name, message_text,
                        cid=audit_cid, msg_id=audit_msg_id, attrs=audit_attrs, endpoint=peer_endpoint)

            # .. invoke the matched route's callback ..
            else:

                if settings.should_log_messages:
                    logger.info('Routing message to channel `%s` (%s)',
                        matched_route.channel_name, matched_route.get_target())

                # .. when should_parse_on_input is enabled, parse the raw ER7 text
                # .. into a structured HL7Message object. If should_validate is also
                # .. enabled, the parser runs validation and raises on errors.
                # .. On success the callback receives the parsed object, otherwise
                # .. it receives the raw ER7 string.
                if settings.should_parse_on_input:

                    # .. a header with no message type cannot be identified as any message at all,
                    # .. so it is turned away here rather than handed to a parser that can only
                    # .. refuse it - the sender is told exactly what was missing ..
                    msh_fields = msh_line.split('|')

                    if len(msh_fields) > _MSH9_Field_Index:
                        message_type = msh_fields[_MSH9_Field_Index]
                    else:
                        message_type = ''

                    if not message_type:
                        logger.warning('No message type in MSH-9 from %s, rejecting (MSH: %s)',
                            connection_context.endpoint, msh_line)

                        ack_code = 'AR'
                        error_text = 'No message type in MSH-9'

                        # .. suppress error details if the channel hides them ..
                        if not settings.should_return_errors:
                            error_text = ''

                        # .. a reject is a negative acknowledgment in the channel's live state,
                        # .. the matched channel's own included ..
                        self.state.on_nack_sent()
                        if channel_state:
                            channel_state.on_nack_sent()

                        ack_string = build_ack(msh_line, ack_code, error_text=error_text,
                            error_condition=Condition_Unsupported_Message)

                        # .. a rejected message still leaves its audit trail - the receipt
                        # .. and the negative acknowledgment that answered it ..
                        if audit_log and audit_channel_name:
                            _ = audit_message_received(
                                audit_log, audit_channel_name, message_text,
                                cid=audit_cid, msg_id=audit_msg_id, attrs=audit_attrs, endpoint=peer_endpoint)
                            _ = audit_ack_sent(
                                audit_log, audit_channel_name, ack_code, ack_string,
                                cid=audit_cid, msg_id=audit_msg_id)

                        self._send_framed(active_socket, ack_string, settings, connection_context)

                        # .. skip to the next message in the batch ..
                        continue

                    # .. attempt to parse (and optionally validate) the message ..
                    try:
                        # Trace point 2: how long the parse took
                        parse_start = monotonic()

                        callback_data = parse_hl7(
                            message_text, validate=settings.should_validate, tolerance=settings.tolerance_config)

                        _trace('parse done %.1fms (%s)', (monotonic() - parse_start) * _ms_per_second, audit_msg_id)

                        # .. a parsed message contributes richer searchable attributes,
                        # .. including the patient's medical record number ..
                        if audit_channel_name:
                            audit_attrs = get_audit_attrs(callback_data)
                            audit_msg_id = get_control_id(callback_data)

                    # .. parsing or validation failed - send an AE reject ACK
                    # .. back to the sender and skip this message. A malformed message is the
                    # .. sender's error rather than an internal one, so one line says what was
                    # .. wrong without a traceback ..
                    except (ValueError, HL7ValidationError) as e:
                        logger.warning('Parse/validation error for channel `%s` from %s; e:`%s`',
                            matched_route.channel_name, connection_context.endpoint, e)
                        ack_code = 'AE'
                        error_text = 'Message parsing or validation failed'

                        # .. suppress error details if the channel hides them ..
                        if not settings.should_return_errors:
                            error_text = ''

                        # .. a reject is a negative acknowledgment in the channel's live state,
                        # .. the matched channel's own included ..
                        self.state.on_nack_sent()
                        if channel_state:
                            channel_state.on_nack_sent()

                        ack_string = build_ack(msh_line, ack_code, error_text=error_text,
                            error_condition=Condition_Data_Type_Error)

                        # .. a rejected message still leaves its audit trail - the receipt
                        # .. and the negative acknowledgment that answered it ..
                        if audit_log and audit_channel_name:
                            _ = audit_message_received(
                                audit_log, audit_channel_name, message_text,
                                cid=audit_cid, msg_id=audit_msg_id, attrs=audit_attrs, endpoint=peer_endpoint)
                            _ = audit_ack_sent(
                                audit_log, audit_channel_name, ack_code, ack_string,
                                cid=audit_cid, msg_id=audit_msg_id)

                        self._send_framed(active_socket, ack_string, settings, connection_context)

                        # .. skip to the next message in the batch ..
                        continue

                # .. parsing not enabled - pass the raw ER7 string to the callback ..
                else:
                    callback_data = message_text

                # .. the receipt is recorded before the service runs, so a message
                # .. that crashes its service is still visibly received ..
                if audit_log and audit_channel_name:

                    # Trace point 3: how long the received-event audit write took
                    audit_received_start = monotonic()

                    _ = audit_message_received(
                        audit_log, audit_channel_name, message_text,
                        cid=audit_cid, msg_id=audit_msg_id, attrs=audit_attrs, endpoint=peer_endpoint)

                    _trace('audit received done %.1fms (%s)',
                        (monotonic() - audit_received_start) * _ms_per_second, audit_msg_id)

                # .. invoke the matched route's service callback ..
                callback_start = monotonic()

                # The correlation id goes along with the message, so what the channel does with it
                # next - the service it runs and the destinations it fans out to - is recorded
                # under the very id the receipt was
                try:
                    callback_response = matched_route.callback(callback_data, audit_cid)
                    ack_code = 'AA'
                    error_text = ''

                # .. service raised an exception - report it as an application error ..
                except Exception:
                    logger.warning('Service callback error for channel `%s` from %s; e:`%s`',
                        matched_route.channel_name, connection_context.endpoint, format_exc())
                    ack_code = 'AE'
                    error_text = 'Internal processing error'

                callback_duration_ms = int((monotonic() - callback_start) * _ms_per_second)

                # Trace point 4: how long the service callback ran
                _trace('callback done %dms (%s)', callback_duration_ms, audit_msg_id)

            # .. suppress error details if configured to not return errors ..
            if not settings.should_return_errors:
                error_text = ''

            # .. the acknowledgment outcome feeds the live state, the channel's own included ..
            if ack_code == 'AA':
                self.state.on_ack_sent()
                if channel_state:
                    channel_state.on_ack_sent()
            else:
                self.state.on_nack_sent()
                if channel_state:
                    channel_state.on_nack_sent()

            # .. a channel that answered with a message of its own is answered with,
            # .. and everything else is acknowledged by an acknowledgment built here ..
            ack_string = _resolve_reply(callback_response, msh_line, ack_code, error_text)

            # .. the acknowledgment lands on the same cid as the receipt it answers ..
            if audit_log and audit_channel_name:

                # Trace point 5: how long the acknowledgment audit write took
                audit_ack_start = monotonic()

                _ = audit_ack_sent(
                    audit_log, audit_channel_name, ack_code, ack_string,
                    cid=audit_cid, msg_id=audit_msg_id, duration_ms=callback_duration_ms)

                _trace('audit ack done %.1fms (%s)', (monotonic() - audit_ack_start) * _ms_per_second, audit_msg_id)

            self._send_framed(active_socket, ack_string, settings, connection_context)

            # Trace point 6: the ACK left and the message is fully processed
            _trace('message done %.1fms total (%s %s)',
                (monotonic() - message_start) * _ms_per_second, ack_code, audit_msg_id)

# ################################################################################################################################
# ################################################################################################################################
