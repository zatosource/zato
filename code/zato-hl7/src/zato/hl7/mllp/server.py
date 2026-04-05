# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket as socket_mod
from logging import DEBUG, getLevelName, getLogger
from socket import timeout as SocketTimeoutException
from traceback import format_exc

# hl7apy
from hl7apy.core import Message

# Zato
from zato.common.api import GENERIC, HL7
from zato.common.typing_ import cast_
from zato.common.util.api import new_cid
from zato.common.util.tcp import ZatoStreamServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from logging import Logger
    from socket import socket as Socket
    from bunch import Bunch
    from zato.common.typing_ import any_, anydict, anylist, anytuple, boolnone, byteslist, bytesnone, callable_
    byteslist = byteslist

# ################################################################################################################################
# ################################################################################################################################

conn_type   = GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP
server_type = 'HL7 MLLP'

# ################################################################################################################################

def new_conn_id(
    pattern:'str'='zhc{}',
    id_len:'int'=5,
    _new_cid:'callable_'=new_cid,
    ) -> 'str':
    return pattern.format(_new_cid(id_len))

# ################################################################################################################################

def new_msg_id(
    pattern:'str'='zhl7{}',
    id_len:'int'=6,
    _new_cid:'callable_'=new_cid,
    ) -> 'str':
    return pattern.format(_new_cid(id_len))

class HandleCompleteMessageArgs:

    _buffer:           'anylist'
    _buffer_join_func: 'callable_'

    conn_ctx:    'ConnCtx'
    request_ctx: 'RequestCtx'

    _socket_sendall:    'callable_'
    _run_callback:      'callable_'
    _request_ctx_reset: 'callable_'

    _start_seq:    'bytes'
    _end_seq:      'bytes'
    _start_seq_len:'int'
    _end_seq_len:  'int'

    _needs_header_check_setter: 'callable_'
    _buffer_reset:              'callable_'

# ################################################################################################################################
# ################################################################################################################################

class ConnCtx:
    """ Details of an individual remote connection to a server.
    """
    conn_id:    'str'
    conn_name:  'str'
    socket:     'Socket'

    peer_ip:    'str'
    peer_port:  'str'
    peer_fqdn:  'str'

    local_ip:   'str'
    local_port: 'int'
    local_fqdn: 'str'

    stats_per_msg_type: 'anydict'
    total_message_packets_received: 'int'
    total_messages_received: 'int'

    def __init__(
        self,
        conn_name:'str',
        socket:'Socket',
        peer_address:'anytuple',
        tcp_keepalive_idle:'int',
        tcp_keepalive_interval:'int',
        tcp_keepalive_count:'int',
        _new_conn_id:'callable_'=new_conn_id,
        ) -> 'None':

        self.conn_id = _new_conn_id()
        self.conn_name = conn_name
        self.socket = socket
        self.peer_ip = peer_address[0]
        self.peer_port = peer_address[1]

        # Statistics broken down by each message type, e.g. ADT
        self.stats_per_msg_type = {}

        # Total message packets received
        self.total_message_packets_received = 0

        # Total full messages received, no matter their type
        self.total_messages_received = 0

        # Log IP directly rather than calling a blocking DNS reverse lookup
        # which can freeze the entire gevent event loop for up to 30 seconds.
        self.peer_fqdn = self.peer_ip

        local_ip, local_port = self.socket.getsockname()
        self.local_ip   = local_ip
        self.local_port = local_port
        self.local_fqdn = local_ip

        # Enable TCP keepalive to detect zombie connections behind firewalls ..
        self.socket.setsockopt(socket_mod.SOL_SOCKET, socket_mod.SO_KEEPALIVE, 1)

        # .. idle time before first probe ..
        if hasattr(socket_mod, 'TCP_KEEPIDLE'):
            self.socket.setsockopt(socket_mod.IPPROTO_TCP, socket_mod.TCP_KEEPIDLE, tcp_keepalive_idle)

        # .. interval between probes ..
        if hasattr(socket_mod, 'TCP_KEEPINTVL'):
            self.socket.setsockopt(socket_mod.IPPROTO_TCP, socket_mod.TCP_KEEPINTVL, tcp_keepalive_interval)

        # .. failed probes before declaring connection dead.
        if hasattr(socket_mod, 'TCP_KEEPCNT'):
            self.socket.setsockopt(socket_mod.IPPROTO_TCP, socket_mod.TCP_KEEPCNT, tcp_keepalive_count)

# ################################################################################################################################

    def get_conn_pretty_info(self) -> 'str':
        conn_id   = self.conn_id
        peer_ip   = self.peer_ip
        peer_port = self.peer_port
        peer_fqdn = self.peer_fqdn
        local_ip   = self.local_ip
        local_port = self.local_port
        local_fqdn = self.local_fqdn
        conn_name  = self.conn_name
        out = f'{conn_id}; `{peer_ip}:{peer_port}` ({peer_fqdn}) to `{local_ip}:{local_port}` ({local_fqdn}) ({conn_name})'
        return out

# ################################################################################################################################
# ################################################################################################################################

class RequestCtx:
    """ Details of an individual request message received from a remote connection.
    """
    __slots__ = 'msg_id', 'conn_id', 'msg_size', 'data', 'meta', 'response'

    msg_id: 'str'
    conn_id: 'str'
    msg_size: 'int'
    data: 'bytes'
    meta: 'anydict'
    response: 'ResponseCtx'

# ################################################################################################################################

    def __init__(self) -> 'None':
        self.conn_id = '<conn-id-not-given>'
        self.data = b''
        self.meta = {}
        self.reset()

# ################################################################################################################################

    def reset(
        self,
        _new_msg_id:'callable_'=new_msg_id,
        ) -> 'None':
        self.msg_id = _new_msg_id()
        self.msg_size = 0
        self.data = b''
        self.meta['has_start_seq'] = False
        self.meta['has_end_seq'] = False

# ################################################################################################################################

    def to_dict(self) -> 'anydict':
        return {
            'conn_id': self.conn_id,
            'msg_id': self.msg_id,
            'msg_size': self.msg_size,
            'data': self.data,
        }

# ################################################################################################################################
# ################################################################################################################################

class ResponseCtx:
    pass

# ################################################################################################################################
# ################################################################################################################################

class HL7MLLPServer:
    """ Each instance of this class handles an individual HL7 MLLP connection in handle_connection.
    """
    config: 'Bunch'
    callback_func: 'callable_'

    # We will never read less than that many bytes from client sockets
    min_read_buffer_size: 'int' = 2048

    # This is configurable by users
    read_buffer_size: 'int'

    object_id: 'str'
    name: 'str'
    address: 'str'
    service_name: 'str'

    should_log_messages: 'bool'

    start_seq: 'bytes'
    start_seq_len: 'int'
    start_seq_len_eq_one: 'bool'

    end_seq: 'bytes'
    end_seq_len: 'int'

    tcp_keepalive_idle:  'int'
    tcp_keepalive_interval: 'int'
    tcp_keepalive_count:   'int'

    keep_running: 'bool'
    impl: 'ZatoStreamServer'

    logger_zato: 'Logger'
    logger_hl7:  'Logger'

    _logger_info:   'callable_'
    _logger_warn:   'callable_'
    _logger_debug:  'callable_'
    _has_debug_log: 'bool'

    def __init__(
        self,
        config:'Bunch',
        callback_func:'callable_',
        ) -> 'None':

        self.config = config
        self.callback_func = callback_func
        self.object_id = config.id
        self.address = config.address
        self.name = config.name
        self.service_name = config.service_name
        self.should_log_messages = config.should_log_messages
        self.read_buffer_size = int(cast_('str', config.read_buffer_size))

        self.start_seq     = cast_('bytes', config.start_seq)
        self.start_seq_len = len(self.start_seq)
        self.start_seq_len_eq_one = self.start_seq_len == 1

        self.end_seq     = cast_('bytes', config.end_seq)
        self.end_seq_len = len(self.end_seq)

        self.tcp_keepalive_idle  = config.tcp_keepalive_idle
        self.tcp_keepalive_interval = config.tcp_keepalive_interval
        self.tcp_keepalive_count   = config.tcp_keepalive_count

        self.keep_running = True

        self.logger_zato = getLogger('zato')
        self.logger_hl7 = getLogger('zato_hl7')
        self.logger_hl7.setLevel(getLevelName(cast_('str', config.logging_level)))

        self._logger_info = self.logger_hl7.info
        self._logger_warn = self.logger_hl7.warn
        self._logger_debug = self.logger_hl7.debug
        self._has_debug_log = self.logger_hl7.isEnabledFor(DEBUG)

# ################################################################################################################################

    def _log_start_stop(self, is_start:'bool') -> 'None':

        action = 'Starting' if is_start else 'Stopping'
        name = self.name
        address = self.address
        msg = f'{action} {server_type} connection `{name}` ({address})'

        self._logger_info(msg)
        self.logger_zato.info(msg)

# ################################################################################################################################

    def start(self) -> 'None':

        # Create a new server connection ..
        self.impl = ZatoStreamServer(self.address, self.handle)

        # .. log info that we are starting ..
        self._log_start_stop(True)

        # .. and start to serve.
        self.impl.serve_forever()

# ################################################################################################################################

    def stop(self) -> 'None':

        # Log info that we are stopping ..
        self._log_start_stop(False)

        # .. signal the main loops to stop accepting new data ..
        self.keep_running = False

        # .. and stop the underlying server.
        self.impl.stop()

# ################################################################################################################################

    def handle(self, socket:'Socket', peer_address:'anytuple') -> 'None':
        try:
            self._handle(socket, peer_address)
        except Exception:
            exc = format_exc()
            msg = f'Exception in {self._handle} ({socket} {peer_address}); e:`{exc}`'
            self.logger_hl7.warning(msg)
            raise

# ################################################################################################################################

    def _handle(self, socket:'Socket', peer_address:'anytuple') -> 'None':

        # Wraps all the metadata about the connection
        conn_ctx = ConnCtx(
            self.name, socket, peer_address,
            self.tcp_keepalive_idle, self.tcp_keepalive_interval, self.tcp_keepalive_count,
        )

        conn_info = conn_ctx.get_conn_pretty_info()
        msg = f'Waiting for HL7 MLLP data from {conn_info}'
        self._logger_info(msg)

        # Current message whose contents we are accumulating
        _buffer:'byteslist' = []

        # Details of the current message
        request_ctx = RequestCtx()
        request_ctx.conn_id = conn_ctx.conn_id

        # To indicate if message header is already checked or not
        _needs_header_check = True

        # To make fewer namespace lookups
        _max_msg_size = int(cast_('str', self.config.max_msg_size))
        _recv_timeout:'float' = self.config.recv_timeout

        # We do not want for this to be too small
        _read_buffer_size = max(self.read_buffer_size, self.min_read_buffer_size)

        _has_debug_log = self._has_debug_log
        _log_debug = self._logger_debug

        _run_callback = self._run_callback
        _check_header = self._check_header
        _close_connection = self._close_connection
        _request_ctx_reset = request_ctx.reset
        _buffer_append = _buffer.append
        _buffer_len    = _buffer.__len__
        _buffer_join_func = b''.join

        _socket_recv = conn_ctx.socket.recv
        _socket_sendall = conn_ctx.socket.sendall
        _socket_settimeout = conn_ctx.socket.settimeout

        # Closures to reset per-message state from inside _handle_complete_message ..
        def _set_needs_header_check(value:'bool') -> 'None':
            nonlocal _needs_header_check
            _needs_header_check = value

        def _buffer_reset(residual:'byteslist') -> 'None':
            _buffer.clear()
            _buffer.extend(residual)

        _handle_complete_message_args = HandleCompleteMessageArgs()
        _handle_complete_message_args._buffer = _buffer
        _handle_complete_message_args._buffer_join_func = _buffer_join_func
        _handle_complete_message_args.conn_ctx = conn_ctx
        _handle_complete_message_args.request_ctx = request_ctx
        _handle_complete_message_args._socket_sendall = _socket_sendall
        _handle_complete_message_args._run_callback = _run_callback
        _handle_complete_message_args._request_ctx_reset = _request_ctx_reset
        _handle_complete_message_args._start_seq = self.start_seq
        _handle_complete_message_args._end_seq = self.end_seq
        _handle_complete_message_args._start_seq_len = self.start_seq_len
        _handle_complete_message_args._end_seq_len = self.end_seq_len
        _handle_complete_message_args._needs_header_check_setter = _set_needs_header_check
        _handle_complete_message_args._buffer_reset = _buffer_reset

        # Run the main loop
        while self.keep_running:

            try:
                # In each iteration, assume that no data was received
                data = None

                # Receive data from the other end
                _socket_settimeout(_recv_timeout)

                # Try to receive some data from the socket ..
                try:

                    # .. read data in ..
                    data = _socket_recv(_read_buffer_size)

                    # .. update counters ..
                    conn_ctx.total_message_packets_received += 1

                    if _has_debug_log:
                        conn_id = conn_ctx.conn_id
                        data_len_debug = len(data)
                        msg = f'HL7 MLLP data received by `{conn_id}` ({data_len_debug}) -> `{data}`'
                        _log_debug(msg)

                # .. catch timeouts here but no other exception type ..
                except SocketTimeoutException:
                    # That is fine, we simply did not get any data in this iteration
                    pass

                # .. no timeout = we may have received some data from the socket ..
                else:

                    # .. something was received so we can append it to our buffer ..
                    if data:

                        # If we are here, it means that the recv call succeeded so we can increase the message size
                        # by how many bytes were actually read from the socket.
                        data_len = len(data)
                        request_ctx.msg_size += data_len

                        # Check whether receiving this data exceeded our message size limit
                        if request_ctx.msg_size > _max_msg_size:
                            reason = f'message exceeds max. size allowed `{request_ctx.msg_size}` > `{_max_msg_size}`'
                            _close_connection(conn_ctx, reason)
                            return

                        # At this point we either do not have all the bytes required to check the header
                        # or the header is already checked, so we can just append data to our current buffer ..
                        _buffer_append(data)

                        # The first byte may be a header and we need to check whether we require it or not at this stage of parsing.
                        # This method will close the connection if anything to do with header parsing is invalid.
                        if _needs_header_check:

                            # If we have a single-byte header, we can check it immediately. This is because
                            # we received some data, which means one byte at the very least, so we can go ahead
                            # with checking the header ..
                            if self.start_seq_len_eq_one:
                                if not _check_header(conn_ctx, request_ctx, data):
                                    return
                                else:
                                    _needs_header_check = False

                            # .. but if we have a multi-byte header, we need to ensure we have already
                            # read as many bytes as there are in the expected header. We do it by iterating
                            # over the buffer of bytes received so far and concatenating them until we have
                            # at least as many bytes as there are in the header to check.
                            else:
                                to_check_buffer:'byteslist' = []
                                to_check_len = 0

                                # Go through each, potentially multi-byte, element in the buffer so far ..
                                for elem in _buffer:

                                    # .. break if we have already all the bytes that we need ..
                                    if to_check_len >= self.start_seq_len:
                                        break

                                    # .. otherwise, append bytes from the current element
                                    # and increase the bytes read so far counter.
                                    else:
                                        to_check_buffer.append(elem)
                                        to_check_len += len(elem)

                                # We still need to check if we have the full header worth of bytes already ..
                                if to_check_len >= self.start_seq_len:

                                    # .. and if we do, we can look up the header now.
                                    to_check = b''.join(to_check_buffer)

                                    if not _check_header(conn_ctx, request_ctx, to_check):
                                        return
                                    else:
                                        _needs_header_check = False

                                else:
                                    # .. otherwise, if we do not have enough bytes,
                                    # we do nothing and this block is added to make it explicit that it is the case.
                                    pass

                        # .. the line that have just received may have been part of a trailer
                        # or the trailer itself so we need to check it ..

                        # .. but we need to take into account the fact that the trailer has been split into two or more
                        # segments. For instance, the previous segment of bytes returned by _socket_recv
                        # ended with the first byte of end_seq and now we have received the second byte.
                        # E.g. our _read_buffer_size is 2048 and if the overall message happens to be 2049 bytes
                        # then the first byte of end_seq will be in the buffer already and the data currently
                        # received contains the second byte. Note that if someone uses end_seq longer than two bytes
                        # this will still work because our _read_buffer_size is always at least 2048 bytes
                        # so end_seq may be split across two segments at most (unless someone uses a multi-kilobyte end_seq,
                        # which is not something to be expected).

                        # First, try to check if data currently received ends in end_seq ..
                        if self._points_to_full_message(data):

                            # .. even if it does, make sure we have a header already and reject the message otherwise ..
                            if _needs_header_check:
                                end_seq = self.end_seq
                                start_seq = self.start_seq
                                reason = f'end bytes `{end_seq}` received without a preceeding header `{start_seq}` (#1)'
                                self._close_connection(conn_ctx, reason)
                                return

                            # .. it is a match so it means that data was the last part of a message that we can already process ..
                            self._handle_complete_message(_handle_complete_message_args)

                        # .. otherwise, try to check if in combination with the previous segment,
                        # the data received now points to a full message. However, for this to work
                        # we require that there be at least one previous segment - otherwise we are the first one
                        # and if we were the ending one we would have been caught in the if above ..
                        else:

                            if _buffer_len() > 1:

                                # Index -1 is our own segment (data) previously appended,
                                # which is why we use -2 to get the segment preceeding it.
                                last_data:'bytes' = _buffer[-2]
                                concatenated = last_data + data

                                # .. now that we have it concatenated, check if that indicates that a full message
                                # is already received.
                                if self._points_to_full_message(concatenated):

                                    # Again, even if it does but have not received the header yet,
                                    # we need to reject the whole message.
                                    if _needs_header_check:
                                        end_seq = self.end_seq
                                        start_seq = self.start_seq
                                        reason = f'end bytes `{end_seq}` received without a preceeding header `{start_seq}` (#2)'
                                        self._close_connection(conn_ctx, reason)
                                        return

                                    self._handle_complete_message(_handle_complete_message_args)

                    # No data received = remote end is no longer connected.
                    else:
                        reason = f'remote end disconnected; `{data}`'
                        _close_connection(conn_ctx, reason)
                        return

            # This covers the whole body of the 'while' block ..
            except SocketTimeoutException:
                pass

            except Exception:
                conn_info = conn_ctx.get_conn_pretty_info()
                exc = format_exc()
                msg = f'Exception in MLLP recv loop for `{conn_info}`; e:`{exc}`'
                self.logger_hl7.warning(msg)
                _close_connection(conn_ctx, 'unrecoverable error in recv loop')
                return

# ################################################################################################################################

    def _points_to_full_message(self, data:'bytes') -> 'bool':
        """ Returns True if input bytes indicate that we have a full message from the socket.
        """
        # Get as many bytes from data as we expected for our end_seq to be the length of ..
        data_last_bytes = data[-self.end_seq_len:]

        # .. return True if the last bytes point to our having a complete message to process.
        return data_last_bytes == self.end_seq

# ################################################################################################################################

    def _handle_complete_message(self, args:'HandleCompleteMessageArgs') -> 'None':

        # Produce the message to invoke the callback with ..
        _buffer_data = args._buffer_join_func(args._buffer)

        # Find the end of the first complete message (SB + payload + EB + CR) ..
        end_idx = _buffer_data.find(args._end_seq)
        message_end = end_idx + args._end_seq_len

        # .. retain any bytes after the complete message, these may be the start of the next message ..
        residual = _buffer_data[message_end:]
        residual_list:'byteslist' = [residual] if residual else []

        # .. extract just the payload, stripping the SB header and EB+CR trailer ..
        _buffer_data = _buffer_data[args._start_seq_len:end_idx]

        # .. assign the actual business data to message ..
        args.request_ctx.data = _buffer_data

        # .. update counters ..
        args.conn_ctx.total_messages_received += 1

        # .. invoke the callback ..
        response = args._run_callback(args.conn_ctx, args.request_ctx) or b''

        # .. wrap the response in MLLP framing (SB + payload + EB + CR) ..
        response = args._start_seq + response + args._end_seq

        # .. optionally, log what we are about to send ..
        if self.should_log_messages:
            msg_id = args.request_ctx.msg_id
            conn_id = args.conn_ctx.conn_id
            response_len = len(response)
            msg = f'Sending HL7 MLLP response to `{msg_id}` -> `{response}` (c:{conn_id}, s={response_len})'
            self._logger_info(msg)

        # .. write the response back, using sendall to guarantee complete delivery ..
        args._socket_sendall(response)

        # .. reset the buffer, retaining any residual bytes from the next message ..
        args._buffer_reset(residual_list)

        # .. re-enable header validation for the next message ..
        args._needs_header_check_setter(True)

        # .. and reset the request context to make it possible to handle a new one.
        args._request_ctx_reset()

# ################################################################################################################################

    def _run_callback(self, conn_ctx:'ConnCtx', request_ctx:'RequestCtx', _hl7_v2:'str'=HL7.Const.Version.v2.id) -> 'bytesnone':

        conn_id = conn_ctx.conn_id
        msg_id = request_ctx.msg_id
        msg_size = request_ctx.msg_size
        total_messages = conn_ctx.total_messages_received
        total_packets = conn_ctx.total_message_packets_received
        service_name = self.service_name
        log_request = request_ctx.to_dict() if self.should_log_messages else '<masked>'

        msg = f'Handling new HL7 MLLP message ({conn_id}; m:{msg_id} (s={msg_size}),' + \
              f' c:{total_messages}, p:{total_packets}; {service_name}); `{log_request!r}`'
        self._logger_info(msg)

        try:
            response = self.callback_func(
                self.config.service_name,
                request_ctx.data,
                data_format = _hl7_v2,
                zato_ctx = {
                    'zato.channel_item': {
                    'data_encoding': 'utf8',
                    'hl7_version': _hl7_v2,
                    'json_path': None,
                    'should_parse_on_input': True,
                    'should_validate': True,
                    'hl7_mllp_conn_ctx': conn_ctx,
                    }
                }
            )

        except Exception:
            service_name = self.service_name
            msg_id = request_ctx.msg_id
            exc = format_exc()
            msg = f'Error while invoking `{service_name}` with msg_id `{msg_id}`; e:`{exc}`'
            self._logger_warn(msg)
        else:

            # Convert high-level objects to bytes ..
            if isinstance(response, Message):
                response = response.to_er7()

            # .. and make sure we actually do use bytes objects ..
            if not isinstance(response, bytes):
                response = response.encode('utf8')

            # .. and return the response to our caller.
            return response

# ################################################################################################################################

    def _close_connection(self, conn_ctx:'ConnCtx', reason:'str') -> 'None':
        conn_info = conn_ctx.get_conn_pretty_info()
        msg = f'Closing connection; {reason}; {conn_info}'
        self._logger_info(msg)
        conn_ctx.socket.close()

# ################################################################################################################################

    def _check_meta(
        self,
        conn_ctx:'ConnCtx',
        request_ctx:'RequestCtx',
        data:'bytes',
        bytes_to_check:'bytes',
        meta_attr:'str',
        has_meta_attr:'str',
        meta_seq:'bytes',
        ) -> 'boolnone':

        # If we already have the meta element then we do not expect another one
        # while we are still processing the same message and if one is found, we close the connection.
        if request_ctx.meta[has_meta_attr]:
            if bytes_to_check == meta_seq:
                reason = f'unexpected {meta_attr} found `{bytes_to_check!r}` == `{meta_seq!r}` in data `{data!r}`'
                self._close_connection(conn_ctx, reason)
                return

        # If we do not have the element, it must be a new message that we are receiving.
        # In such a case, we expect for it to begin with a header. Otherwise, we reject the entire connection.
        else:
            if bytes_to_check != meta_seq:
                reason = f'{meta_attr} mismatch `{bytes_to_check!r}` != `{meta_seq!r}` in data `{data!r}`'
                self._close_connection(conn_ctx, reason)
                return

        # If we are here, it means that the meta attribute is correct
        request_ctx.meta[has_meta_attr] = True
        return True

# ################################################################################################################################

    def _check_header(self, conn_ctx:'ConnCtx', request_ctx:'RequestCtx', data:'bytes') -> 'boolnone':

        bytes_to_check = data[:self.start_seq_len]
        meta_attr = 'header'
        has_meta_attr  = 'has_start_seq'
        meta_seq = self.start_seq

        return self._check_meta(conn_ctx, request_ctx, data, bytes_to_check, meta_attr, has_meta_attr, meta_seq)

# ################################################################################################################################
# ################################################################################################################################

def main():

    # stdlib
    import logging
    from time import sleep

    # Bunch
    from bunch import bunchify

    # Zato
    from zato.common.api import HL7

    log_level = logging.DEBUG
    log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=log_level, format=log_format)

    logger = logging.getLogger(__name__)

    def on_message(*args:'any_', **kwargs:'any_') -> 'str':

        msg = f'Args: {args}'
        logger.info(msg)

        msg = f'Kwargs: {kwargs}'
        logger.info(msg)

        return 'Hello from HL7v2'

    channel_port = HL7.Default.channel_port
    address = f'0.0.0.0:{channel_port}'

    config = bunchify({
        'id': '123',
        'name': 'Hello HL7 MLLP',
        'address': address,

        'service_name': 'pub.zato.ping',

        'max_msg_size': 1_000_000,
        'read_buffer_size': 2048,
        'recv_timeout': 30,

        'logging_level': 'DEBUG',
        'should_log_messages': True,

        'start_seq': b'\x0b',
        'end_seq': b'\x1c\x0d',

        'tcp_keepalive_idle': 60,
        'tcp_keepalive_interval': 10,
        'tcp_keepalive_count': 6,
    })

    server = HL7MLLPServer(config, on_message)
    server.start()

    while True:
        print(1)
        sleep(1)

# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
