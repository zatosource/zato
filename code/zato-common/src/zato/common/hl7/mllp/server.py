# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import spawn
from gevent.lock import BoundedSemaphore

# Zato
from zato.common.hl7.audit import audit_ack_sent, get_wire_attrs
from zato.common.hl7.exception import HL7Exception
from zato.common.hl7.mllp.ack import build_ack, Condition_Data_Type_Error, ErrorCondition
from zato.common.hl7.mllp.codec import FrameReader, frame_encode
from zato.common.hl7.mllp.connection import ConnectionContext
from zato.common.hl7.mllp.dedup import extract_control_id
from zato.common.hl7.mllp.message import handle_message
from zato.common.hl7.mllp.proxy_protocol import read_optional_proxy_header
from zato.common.hl7.mllp.reply import Application_Error_Ack_Code, Rejection_Ack_Code
from zato.common.hl7.mllp.router import HL7MessageRouter
from zato.common.hl7.mllp.settings import ListenerConfig, RouteSettings, is_address_allowed
from zato.common.hl7.mllp.state import ChannelState
from zato.common.util.api import new_cid_server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.hl7.mllp.router import ChannelRoute

    AuditLog = AuditLog
    ChannelRoute = ChannelRoute

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How long the accept loop waits before checking whether it has been told to stop
_Accept_Poll_Interval = 1.0

# What the sender is told when its frame left the stream with no known boundary
_Unreadable_Frame_Error_Text = 'Message could not be read'

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

    def send_framed(
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
                    self._reject_frame(client_socket, msh_line, settings, connection_context,
                        Application_Error_Ack_Code, _Unreadable_Frame_Error_Text, Condition_Data_Type_Error)
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
        self.send_framed(active_socket, ack_string, settings, connection_context)

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
        ack_string = build_ack(msh_line, Rejection_Ack_Code, error_text='')

        self.state.on_nack_sent()
        channel_state.on_nack_sent()

        if self.audit_log and route.is_audit_log_active:

            audit_cid = new_cid_server()
            control_id = extract_control_id(msh_line)
            wire_attrs = get_wire_attrs(msh_line)

            _ = audit_ack_sent(
                self.audit_log, route.channel_name, Rejection_Ack_Code, ack_string,
                cid=audit_cid, msg_id=control_id, facility=wire_attrs['facility'])

        self.send_framed(active_socket, ack_string, settings, connection_context)

# ################################################################################################################################

    def _handle_message(
        self,
        active_socket:'socket.socket',
        raw_message_bytes:'bytes',
        connection_context:'ConnectionContext',
        matched_route:'ChannelRoute | None',
        settings:'RouteSettings',
        ) -> 'None':
        """ Processes a single unframed HL7 message under the settings of the channel it matched.
        """
        handle_message(self, active_socket, raw_message_bytes, connection_context, matched_route, settings)

# ################################################################################################################################
# ################################################################################################################################
