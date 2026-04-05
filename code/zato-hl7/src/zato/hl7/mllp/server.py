# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket as socket_mod
from logging import DEBUG, getLevelName, getLogger
from socket import timeout as SocketTimeoutException
from time import monotonic
from traceback import format_exc

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
    from zato.common.typing_ import any_, anydict, anylist, anytuple, boolnone, byteslist, callable_
    byteslist = byteslist

# ################################################################################################################################
# ################################################################################################################################

conn_type   = GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP
server_type = 'HL7 MLLP'

# HL7 Table 0211 character set names mapped to Python codec names.
# Single-byte encodings and UTF-8 are safe over MLLP.
# UTF-16 and UTF-32 are prohibited because their byte values conflict with MLLP framing bytes (0x0B, 0x1C, 0x0D).
_msh18_to_codec = {
    b'':               'iso-8859-1',
    b'ASCII':          'ascii',
    b'8859/1':         'iso-8859-1',
    b'8859/2':         'iso-8859-2',
    b'8859/3':         'iso-8859-3',
    b'8859/4':         'iso-8859-4',
    b'8859/5':         'iso-8859-5',
    b'8859/6':         'iso-8859-6',
    b'8859/7':         'iso-8859-7',
    b'8859/8':         'iso-8859-8',
    b'8859/9':         'iso-8859-9',
    b'8859/15':        'iso-8859-15',
    b'UNICODE UTF-8':  'utf-8',
    b'UNICODE':        'utf-8',
    b'ISO IR87':       'iso2022_jp',
    b'ISO IR159':      'iso2022_jp',
    b'GB 18030-2000':  'gb18030',
    b'KS X 1001':      'euc_kr',
    b'CNS 11643-1992': 'big5',
}

_default_codec = 'iso-8859-1'

# ################################################################################################################################

def _detect_encoding_from_msh18(raw_payload:'bytes') -> 'str':
    """ Reads MSH-18 (Character Set) from the raw HL7 payload bytes to determine the message encoding.
    The field separator and segment positions are always single-byte ASCII regardless of encoding,
    so this is safe to do on raw bytes before any character decoding.
    """
    # The first segment is MSH, terminated by 0x0D ..
    cr_idx = raw_payload.find(b'\x0d')
    if cr_idx == -1:
        return _default_codec

    msh_segment = raw_payload[:cr_idx]

    # MSH-1 (field separator) is always the 4th byte (index 3) ..
    if len(msh_segment) < 4:
        return _default_codec

    field_sep = msh_segment[3:4]

    # .. split MSH on the field separator and read field index 17 (zero-indexed,
    # because MSH-1 is the field separator itself, so MSH-2 is index 0 after the first split) ..
    fields = msh_segment.split(field_sep)
    len_fields = len(fields)

    # fields[0] is 'MSH', fields[1] is encoding chars, ... fields[17] is MSH-18
    if len_fields <= 17:
        return _default_codec

    msh18 = fields[17].strip()

    # MSH-18 may contain multiple character sets separated by the repetition separator (e.g. ASCII~ISO IR87),
    # in which case we use the first one that we recognize ..
    rep_sep = msh_segment[5:6] if len(msh_segment) > 5 else b'~'
    for charset in msh18.split(rep_sep):
        charset = charset.strip()
        codec = _msh18_to_codec.get(charset)
        if codec:
            return codec

    return _default_codec

# ################################################################################################################################

def _build_ack(raw_payload:'bytes', ack_code:'bytes', err_text:'bytes'=b'') -> 'bytes':
    """ Builds a minimal HL7 v2 ACK message from the inbound raw payload.
    Swaps sender/receiver fields from the inbound MSH and sets MSA-1 to ack_code (AA, AE, or AR).
    """
    cr = b'\x0d'

    # Extract MSH fields from the raw payload ..
    cr_idx = raw_payload.find(cr)
    if cr_idx == -1:
        msh_segment = raw_payload
    else:
        msh_segment = raw_payload[:cr_idx]

    if len(msh_segment) < 4:
        field_sep = b'|'
    else:
        field_sep = msh_segment[3:4]

    fields = msh_segment.split(field_sep)
    len_fields = len(fields)

    # fields layout: [0]=MSH, [1]=encoding chars, [2]=sending app, [3]=sending facility,
    # [4]=receiving app, [5]=receiving facility, [6]=datetime, [7]=security,
    # [8]=message type, [9]=message control id, ...

    encoding_chars = fields[1] if len_fields > 1 else b'^~\\&'
    sending_app    = fields[2] if len_fields > 2 else b''
    sending_fac    = fields[3] if len_fields > 3 else b''
    receiving_app  = fields[4] if len_fields > 4 else b''
    receiving_fac  = fields[5] if len_fields > 5 else b''
    msg_control_id = fields[9] if len_fields > 9 else b'0'
    version        = fields[11] if len_fields > 11 else b'2.5'

    # Build the ACK MSH with sender/receiver swapped ..
    ack_msh = field_sep.join([
        b'MSH', encoding_chars,
        receiving_app, receiving_fac,
        sending_app, sending_fac,
        b'', b'',
        b'ACK', msg_control_id,
        b'P', version,
    ])

    # .. build the MSA segment ..
    ack_msa = field_sep.join([b'MSA', ack_code, msg_control_id])

    parts = [ack_msh, ack_msa]

    # .. optionally add an ERR segment with the error text ..
    if err_text:
        ack_err = field_sep.join([b'ERR', err_text])
        parts.append(ack_err)

    out = cr.join(parts) + cr
    return out

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

    idle_timeout: 'float'

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

        self.idle_timeout = float(config.idle_timeout)

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
        _recv_timeout:'float' = self.config.recv_timeout
        _idle_timeout:'float' = self.idle_timeout
        _last_activity:'float' = monotonic()

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
                        _has_complete = self._points_to_full_message(data)

                        # .. if not, try combining with previous segment to catch end_seq split across recv boundaries ..
                        if not _has_complete and _buffer_len() > 1:
                            last_data:'bytes' = _buffer[-2]
                            concatenated = last_data + data
                            _has_complete = self._points_to_full_message(concatenated)

                        if _has_complete:

                            # .. make sure we have a header already and reject the message otherwise ..
                            if _needs_header_check:
                                end_seq = self.end_seq
                                start_seq = self.start_seq
                                reason = f'end bytes `{end_seq}` received without a preceeding header `{start_seq}`'
                                self._close_connection(conn_ctx, reason, raw_payload=data)
                                return

                            # .. process the complete message and then drain any further complete messages
                            # that may already be sitting in the residual buffer from pipelining ..
                            self._handle_complete_message(_handle_complete_message_args)

                            while _buffer:
                                combined = _buffer_join_func(_buffer)
                                if combined.find(self.end_seq) == -1:
                                    break
                                self._handle_complete_message(_handle_complete_message_args)

                            # .. reset idle timer after successfully processing messages ..
                            _last_activity = monotonic()

                    # No data received = remote end is no longer connected.
                    else:
                        reason = f'remote end disconnected; `{data}`'
                        _close_connection(conn_ctx, reason)
                        return

            # This covers the whole body of the 'while' block ..
            except SocketTimeoutException:
                # Check application-level idle timeout, 0 means no timeout ..
                if _idle_timeout > 0:
                    idle_elapsed = monotonic() - _last_activity
                    if idle_elapsed > _idle_timeout:
                        reason = f'idle timeout ({idle_elapsed:.1f}s > {_idle_timeout:.1f}s)'
                        _close_connection(conn_ctx, reason)
                        return

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
        # A bare 0x1C inside the HL7 payload is not a concern here because the MLLP end sequence
        # is 0x1C followed by 0x0D, and 0x0D is the HL7 segment terminator. An isolated 0x1C byte
        # inside payload data will never be immediately followed by 0x0D in a position that could be
        # mistaken for end-of-message framing, because 0x0D always starts a new segment in valid HL7.
        # In other words, the two-byte end_seq (0x1C 0x0D) is unambiguous within well-formed HL7 content.

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

        # .. invoke the callback, which always returns bytes (AA ACK if callback returned nothing, AE NAK on error) ..
        response = args._run_callback(args.conn_ctx, args.request_ctx)

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
        try:
            args._socket_sendall(response)
        except ConnectionError:
            conn_info = args.conn_ctx.get_conn_pretty_info()
            msg = f'Connection lost while sending response to `{conn_info}`'
            self._logger_warn(msg)
            return

        # .. reset the buffer, retaining any residual bytes from the next message ..
        args._buffer_reset(residual_list)

        # .. re-enable header validation for the next message ..
        args._needs_header_check_setter(True)

        # .. and reset the request context to make it possible to handle a new one.
        args._request_ctx_reset()

# ################################################################################################################################

    def _run_callback(self, conn_ctx:'ConnCtx', request_ctx:'RequestCtx', _hl7_v2:'str'=HL7.Const.Version.v2.id) -> 'bytes':

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

        raw_payload = request_ctx.data
        encoding = _detect_encoding_from_msh18(raw_payload)

        try:
            response = self.callback_func(
                self.config.service_name,
                request_ctx.data,
                data_format = _hl7_v2,
                zato_ctx = {
                    'zato.channel_item': {
                    'conn_id': conn_id,
                    'msg_id': msg_id,
                    'msg_size': msg_size,
                    'data_encoding': encoding,
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

            # Return an AE (Application Error) NAK so the sender knows the message was not processed ..
            err_text = f'Callback error for msg_id {msg_id}'.encode(encoding)
            return _build_ack(raw_payload, b'AE', err_text)

        else:

            # If the callback returned nothing, auto-generate an AA (Application Accept) ACK ..
            if not response:
                return _build_ack(raw_payload, b'AA')

            # Convert high-level objects to bytes ..
            if hasattr(response, 'serialize'):
                response = response.serialize()

            # .. and make sure we actually do use bytes objects ..
            if not isinstance(response, bytes):
                response = response.encode(encoding)

            # .. and return the response to our caller.
            return response

# ################################################################################################################################

    def _close_connection(self, conn_ctx:'ConnCtx', reason:'str', raw_payload:'bytes'=b'') -> 'None':
        conn_info = conn_ctx.get_conn_pretty_info()
        msg = f'Closing connection; {reason}; {conn_info}'
        self._logger_info(msg)

        # Best-effort attempt to send an AR (Application Reject) NAK before closing,
        # so the remote end knows we are rejecting the conversation rather than silently dropping it ..
        if raw_payload:
            try:
                err_text = reason.encode('utf-8')
                nak = _build_ack(raw_payload, b'AR', err_text)
                framed = self.start_seq + nak + self.end_seq
                conn_ctx.socket.sendall(framed)
            except Exception:
                pass

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
                self._close_connection(conn_ctx, reason, raw_payload=data)
                return

        # If we do not have the element, it must be a new message that we are receiving.
        # In such a case, we expect for it to begin with a header. Otherwise, we reject the entire connection.
        else:
            if bytes_to_check != meta_seq:
                reason = f'{meta_attr} mismatch `{bytes_to_check!r}` != `{meta_seq!r}` in data `{data!r}`'
                self._close_connection(conn_ctx, reason, raw_payload=data)
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

        'read_buffer_size': 2048,
        'recv_timeout': 30,
        'idle_timeout': 300,

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
