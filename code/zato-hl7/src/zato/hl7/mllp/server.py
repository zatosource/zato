# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import DEBUG, getLevelName, getLogger
from socket import timeout as SocketTimeoutException
from time import sleep
from traceback import format_exc

# hl7apy
from hl7apy.core import Message

# Past
from past.builtins import basestring

# Zato
from zato.common.api import GENERIC, HL7
from zato.common.audit_log import DataReceived, DataSent
from zato.common.util.api import new_cid
from zato.common.util.tcp import get_fqdn_by_ip, ZatoStreamServer

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from gevent import socket
    from zato.common.audit_log import DataEvent, AuditLog

    Bunch = Bunch
    DataEvent = DataEvent
    AuditLog = AuditLog
    socket = socket

# ################################################################################################################################
# ################################################################################################################################

conn_type   = GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP
server_type = 'HL7 MLLP'

# ################################################################################################################################

def new_conn_id(pattern='zhc{}', id_len=5, _new_cid=new_cid):
    return pattern.format(_new_cid(id_len))

def new_msg_id(pattern='zhl7{}', id_len=6, _new_cid=new_cid):
    return pattern.format(_new_cid(id_len))

# ################################################################################################################################
# ################################################################################################################################

class ConnCtx:
    """ Details of an individual remote connection to a server.
    """
    __slots__ = ('conn_id', 'conn_name', 'socket', 'peer_ip', 'peer_port', 'peer_fqdn', 'local_ip', \
        'local_port', 'local_fqdn', 'stats_per_msg_type', 'total_message_packets_received', 'total_messages_received')

    def __init__(self, conn_name, socket, peer_address, _new_conn_id=new_conn_id):
        # type: (socket, tuple)

        self.conn_id = _new_conn_id()
        self.conn_name = conn_name
        self.socket = socket
        self.peer_ip = peer_address[0]   # type: str
        self.peer_port = peer_address[1] # type: int

        # Statistics broken down by each message type, e.g. ADT
        self.stats_per_msg_type = {}

        # Total message packets received
        self.total_message_packets_received = 0

        # Total full messages received, no matter their type
        self.total_messages_received = 0

        self.peer_fqdn = get_fqdn_by_ip(self.peer_ip, 'peer', server_type)
        self.local_ip, self.local_port, self.local_fqdn = self._get_local_conn_info('local')

# ################################################################################################################################

    def get_conn_pretty_info(self):
        return '{}; `{}:{}` ({}) to `{}:{}` ({}) ({})'.format(
            self.conn_id, self.peer_ip, self.peer_port, self.peer_fqdn,
            self.local_ip, self.local_port, self.local_fqdn, self.conn_name,
        )

# ################################################################################################################################

    def _get_local_conn_info(self, default_local_fqdn):
        # type: (str) -> tuple
        local_ip, local_port = self.socket.getsockname()
        local_fqdn = get_fqdn_by_ip(local_ip, default_local_fqdn, server_type)

        return local_ip, local_port, local_fqdn

# ################################################################################################################################
# ################################################################################################################################

class RequestCtx:
    """ Details of an individual request message received from a remote connection.
    """
    __slots__ = 'msg_id', 'conn_id', 'msg_size', 'data', 'meta', 'response'

# ################################################################################################################################

    def __init__(self, _new_msg_id=new_msg_id):
        self.conn_id = '<conn-id-not-given>'
        self.msg_id = None   # type: str
        self.msg_size = None # type: int
        self.data = b''
        self.meta = {}
        self.response = None # type: ResponseCtx
        self.reset()

# ################################################################################################################################

    def reset(self, _new_msg_id=new_msg_id):
        self.msg_id = _new_msg_id()
        self.msg_size = 0
        self.data = b''
        self.meta['has_start_seq'] = False
        self.meta['has_end_seq'] = False

# ################################################################################################################################

    def to_dict(self):
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

    # We will never read less than that many bytes from client sockets
    min_read_buffer_size = 2048

    def __init__(self, config, callback_func, audit_log):
        # type: (Bunch, object, AuditLog)
        self.config = config
        self.callback_func = callback_func
        self.object_id = config.id # type: str
        self.audit_log = audit_log
        self.address = config.address
        self.name = config.name
        self.service_name = config.service_name
        self.should_log_messages = config.should_log_messages # type: bool

        self.start_seq     = config.start_seq
        self.start_seq_len = len(config.start_seq)
        self.start_seq_len_eq_one = self.start_seq_len == 1

        self.end_seq     = config.end_seq
        self.end_seq_len = len(config.end_seq)

        self.is_audit_log_sent_active = config.get('is_audit_log_sent_active')
        self.is_audit_log_received_active = config.get('is_audit_log_received_active')

        self.keep_running = True
        self.impl = None # type: ZatoStreamServer

        self.logger_zato = getLogger('zato')

        self.logger_hl7 = getLogger('zato_hl7')
        self.logger_hl7.setLevel(getLevelName(config.logging_level))

        self._logger_info = self.logger_hl7.info
        self._logger_warn = self.logger_hl7.warn
        self._logger_debug = self.logger_hl7.debug
        self._has_debug_log = self.logger_hl7.isEnabledFor(DEBUG)

# ################################################################################################################################

    def _log_start_stop(self, is_start):
        # type: (bool)

        msg = 'Starting' if is_start else 'Stopping'
        pattern = '%s %s connection `%s` (%s)'
        args = (msg, server_type, self.name, self.address)

        self._logger_info(pattern, *args)
        self.logger_zato.info(pattern, *args)

# ################################################################################################################################

    def start(self):

        # Create a new server connection ..
        self.impl = ZatoStreamServer(self.address, self.handle)

        # .. log info that we are starting ..
        self._log_start_stop(True)

        # .. and start to serve.
        self.impl.serve_forever()

# ################################################################################################################################

    def stop(self):

        # Log info that we are stopping ..
        self._log_start_stop(False)

        # .. and actually stop.
        self.keep_running = False
        self.impl.stop()

# ################################################################################################################################

    def handle(self, socket, peer_address):
        try:
            self._handle(socket, peer_address)
        except Exception:
            self.logger_hl7.warn('Exception in %s (%s %s); e:`%s`', self._handle, socket, peer_address, format_exc())
            raise

# ################################################################################################################################

    def _handle(self, socket, peer_address):
        # type: (socket, tuple)

        # Wraps all the metadata about the connection
        conn_ctx = ConnCtx(self.name, socket, peer_address)

        self._logger_info('Waiting for HL7 MLLP data from %s', conn_ctx.get_conn_pretty_info())

        # Current message whose contents we are accumulating
        _buffer = []

        # Details of the current message
        request_ctx = RequestCtx()
        request_ctx.conn_id = conn_ctx.conn_id

        # To indicate if message header is already checked or not
        _needs_header_check = True

        # To make fewer namespace lookups
        _max_msg_size = self.config.max_msg_size         # type: int
        _recv_timeout = self.config.recv_timeout         # type: float

        # We do not want for this to be too small
        _read_buffer_size = max(self.config.read_buffer_size, self.min_read_buffer_size) # type: int

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
        _socket_send = conn_ctx.socket.send
        _socket_settimeout = conn_ctx.socket.settimeout

        _handle_complete_message_args = (_buffer, _buffer_join_func, conn_ctx, request_ctx, _request_ctx_reset,
            _socket_send, _run_callback)

        # Run the main loop
        while self.keep_running:

            try:
                # In each iteration, assume that no data was received
                data = None

                # Check whether reading the data would not exceed our message size limit
                new_size = request_ctx.msg_size + _read_buffer_size
                if new_size > _max_msg_size:
                    reason = 'message would exceed max. size allowed `{}` > `{}`'.format(new_size, _max_msg_size)
                    _close_connection(conn_ctx, reason)
                    return

                # Receive data from the other end
                _socket_settimeout(_recv_timeout)

                # Try to receive some data from the socket ..
                try:

                    # .. read data in ..
                    data = _socket_recv(_read_buffer_size)

                    # .. update counters ..
                    conn_ctx.total_message_packets_received += 1

                    if _has_debug_log:
                        _log_debug('HL7 MLLP data received by `%s` (%d) -> `%s`', conn_ctx.conn_id, len(data), data)

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
                        request_ctx.msg_size += len(data)

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
                                to_check_buffer = []
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
                                reason = 'end bytes `{}` received without a preceeding header `{}` (#1)'.format(
                                    self.end_seq, self.start_seq)
                                self._close_connection(conn_ctx, reason)
                                return

                            # .. it is a match so it means that data was the last part of a message that we can already process ..
                            self._handle_complete_message(True, *_handle_complete_message_args)

                        # .. otherwise, try to check if in combination with the previous segment,
                        # the data received now points to a full message. However, for this to work
                        # we require that there be at least one previous segment - otherwise we are the first one
                        # and if we were the ending one we would have been caught in the if above ..
                        else:

                            if _buffer_len() > 1:

                                # Index -1 is our own segment (data) previously appended,
                                # which is why we use -2 to get the segment preceeding it.
                                last_data = _buffer[-2]
                                concatenated = last_data + data

                                # .. now that we have it concatenated, check if that indicates that a full message
                                # is already received.
                                if self._points_to_full_message(concatenated):

                                    # Again, even if it does but have not received the header yet,
                                    # we need to reject the whole message.
                                    if _needs_header_check:
                                        reason = 'end bytes `{}` received without a preceeding header `{}` (#2)'.format(
                                            self.end_seq, self.start_seq)
                                        self._close_connection(conn_ctx, reason)
                                        return

                                    self._handle_complete_message(True, *_handle_complete_message_args)

                    # No data received = remote end is no longer connected.
                    else:
                        reason = 'remote end disconnected; `{}`'.format(data)
                        _close_connection(conn_ctx, reason)
                        return

            # This covers the whole body of the 'while' block,
            # catching everything that was raised in a given loop's iteration.
            except Exception:

                # Log the exception ..
                exc = format_exc()
                self.logger_hl7.warn(exc)

                # .. and sleep for a while in case we cannot re-enter the loop immediately.
                sleep(2)

# ################################################################################################################################

    def _points_to_full_message(self, data):
        """ Returns True if input bytes indicate that we have a full message from the socket.
        """
        # type: (bytes) -> bool

        # Get as many bytes from data as we expected for our end_seq to be the length of ..
        data_last_bytes = data[-self.end_seq_len:]

        # .. return True if the last bytes point to our having a complete message to process.
        return data_last_bytes == self.end_seq

# ################################################################################################################################

    def _handle_complete_message(self, needs_response, _buffer, _buffer_join_func, conn_ctx, request_ctx, _request_ctx_reset,
            _socket_send, _run_callback, _datetime_utcnow=datetime.utcnow):
        # type: (bool, bytes, object, ConnCtx, RequestCtx, object, object, object, object)

        # Produce the message to invoke the callback with ..
        _buffer_data = _buffer_join_func(_buffer)

        # .. remove the header and trailer ..
        _buffer_data = _buffer_data[self.start_seq_len:-self.end_seq_len]

        # .. asign the actual business data to message ..
        request_ctx.data = _buffer_data

        # .. update our runtime metadata first (data received) ..
        if self.is_audit_log_received_active:
            self._store_data_received(request_ctx)

        # .. update counters ..
        conn_ctx.total_messages_received += 1

        # .. invoke the callback ..
        response = _run_callback(conn_ctx, request_ctx)

        # .. optionally, log what we are about to send ..
        if self.should_log_messages:
            self._logger_info('Sending HL7 MLLP response to `%s` -> `%s` (c:%s; s=%d)',
                request_ctx.msg_id, response, conn_ctx.conn_id, len(response))

        # .. write the response back ..
        _socket_send(response)

        # .. update our runtime metadata first (data sent) ..
        if self.is_audit_log_sent_active:
            self._store_data_sent(request_ctx, response)

        # .. and reset the message to make it possible to handle a new one.
        _request_ctx_reset()

# ################################################################################################################################

    def _store_data(self, request_ctx, _DataEventClass, response=None, _conn_type=conn_type):
        # type: (RequestCtx, DataEvent, str, str) -> None

        # Create and fill out details of the new event ..
        data_event = _DataEventClass()
        data_event.data = response or request_ctx.data
        data_event.type_ = _conn_type
        data_event.object_id = self.object_id
        data_event.conn_id = request_ctx.conn_id
        data_event.msg_id = request_ctx.msg_id

        # .. and store it in our log.
        self.audit_log.store_data(data_event)

# ################################################################################################################################

    def _store_data_received(self, request_ctx, event_class=DataReceived):
        self._store_data(request_ctx, event_class)

# ################################################################################################################################

    def _store_data_sent(self, request_ctx, response, event_class=DataSent):
        self._store_data(request_ctx, event_class, response)

# ################################################################################################################################

    def _run_callback(self, conn_ctx, request_ctx, _hl7_v2=HL7.Const.Version.v2.id):
        # type: (ConnCtx, RequestCtx) -> bytes

        pattern = 'Handling new HL7 MLLP message (%s; m:%s (s=%s), c:%s, p:%s; %s); `%r`'
        log_request = request_ctx.to_dict() if self.should_log_messages else '<masked>'

        self._logger_info(
            pattern,
            conn_ctx.conn_id,
            request_ctx.msg_id,
            request_ctx.msg_size,
            conn_ctx.total_messages_received,
            conn_ctx.total_message_packets_received,
            self.service_name,
            log_request
        )

        try:
            response = self.callback_func(
                self.config.service_name,
                request_ctx.data,
                data_format = _hl7_v2,
                zato_ctx = {'zato.channel_item': {
                    'data_encoding': 'utf8',
                    'hl7_version': _hl7_v2,
                    'json_path': None,
                    'should_parse_on_input': True,
                    'should_validate': True,
                    'hl7_mllp_conn_ctx': conn_ctx,
                }}
            )

        except Exception:
            self._logger_warn('Error while invoking `%s` with msg_id `%s`; e:`%s`',
                self.service_name, request_ctx.msg_id, format_exc())
        else:

            # Convert high-level objects to bytes ..
            if isinstance(response, Message):
                response = response.to_er7()

            # .. and make sure we actually do use bytes objects ..
            if isinstance(response, basestring):
                response = response if isinstance(response, bytes) else response.encode('utf8')

            # .. and return the response to our caller.
            return response

# ################################################################################################################################

    def _close_connection(self, conn_ctx, reason):
        # type: str -> None
        self._logger_info('Closing connection; %s; %s', reason, conn_ctx.get_conn_pretty_info())
        conn_ctx.socket.close()

# ################################################################################################################################

    def _check_meta(self, conn_ctx, request_ctx, data, bytes_to_check, meta_attr, has_meta_attr, meta_seq):
        # type: (ConnCtx, RequestCtx, bytes, bytes, str, bool, bytes) -> bool

        # If we already have the meta element then we do not expect another one
        # while we are still processing the same message and if one is found, we close the connection.
        if request_ctx.meta[has_meta_attr]:
            if bytes_to_check == meta_seq:
                reason = 'unexpected {} found `{!r}` == `{!r}` in data `{!r}`'.format(meta_attr, bytes_to_check, meta_seq, data)
                self._close_connection(conn_ctx, reason)
                return

        # If we do not have the element, it must be a new message that we are receiving.
        # In such a case, we expect for it to begin with a header. Otherwise, we reject the entire connection.
        else:
            if bytes_to_check != meta_seq:
                reason = '{} mismatch `{!r}` != `{!r}` in data `{!r}`'.format(meta_attr, bytes_to_check, meta_seq, data)
                self._close_connection(conn_ctx, reason)
                return

        # If we are here, it means that the meta attribute is correct
        request_ctx.meta[has_meta_attr] = True
        return True

# ################################################################################################################################

    def _check_header(self, conn_ctx, request_ctx, data):

        bytes_to_check = data[:self.start_seq_len]
        meta_attr = 'header'
        has_meta_attr  = 'has_start_seq'
        meta_seq = self.start_seq

        return self._check_meta(conn_ctx, request_ctx, data, bytes_to_check, meta_attr, has_meta_attr, meta_seq)

# ################################################################################################################################
# ################################################################################################################################

def main():

    # Bunch
    from bunch import bunchify

    # Zato
    from zato.common.audit_log import AuditLog, LogContainerConfig

    def on_message(msg):
        # type: (str)
        raise Exception(msg)

    config = bunchify({
        'id': '123',
        'name': 'Hello HL7 MLLP',
        'address': '0.0.0.0:30191',

        'max_msg_size': 1_000_000,
        'read_buffer_size': 2048,
        'recv_timeout': 0.25,

        'logging_level': 'DEBUG',
        'should_log_messages': True,

        'start_seq': b'\x0b',
        'end_seq': b'\x1c\x0d',
    })

    log_container_config = LogContainerConfig()

    audit_log = AuditLog()
    audit_log.create_container(log_container_config)

    reader = HL7MLLPServer(config, audit_log)
    reader.start()

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
