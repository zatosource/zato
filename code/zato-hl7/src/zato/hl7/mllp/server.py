# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from datetime import datetime
from logging import getLogger
from socket import timeout as SocketTimeoutException
from traceback import format_exc

# Zato
from zato.common.util.api import new_cid
from zato.common.util.tcp import get_fqdn_by_ip, ZatoStreamServer

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from gevent import socket

    Bunch = Bunch
    socket = socket

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ################################################################################################################################

_server_type = 'HL7 MLLP'
_stats_attrs = 'total_bytes', 'total_messages', 'avg_msg_size', 'first_transferred', 'last_transferred'

# ################################################################################################################################

def new_conn_id(pattern='zhc{}', id_len=5, _new_cid=new_cid):
    return pattern.format(_new_cid(id_len))

def new_msg_id(pattern='zhm{}', id_len=6, _new_cid=new_cid):
    return pattern.format(_new_cid(id_len))

# ################################################################################################################################
# ################################################################################################################################

class _MsgTypeStats:
    """ Represents transfer statistics for each message type.
    """
    __slots__ = ('msg_type',) + _stats_attrs

    def __init__(self):
        self.msg_type = None
        self.total_bytes = -1
        self.total_messages = -1
        self.avg_msg_size = -1
        self.first_transferred = None
        self.last_transferred = None

    def to_dict(self):
        out = {}
        for name in self.__slots__:
            out[name] = getattr(self, name)

# ################################################################################################################################
# ################################################################################################################################

class ConnCtx:
    """ Details of an individual remote connection to a server.
    """
    __slots__ = ('conn_id', 'conn_name', 'socket', 'peer_ip', 'peer_port', 'peer_fqdn', 'local_ip', \
        'local_port', 'local_fqdn', 'stats_per_msg_type') + _stats_attrs

    def __init__(self, conn_name, socket, peer_address, _new_conn_id=new_conn_id):
        # type: (socket, tuple)

        self.conn_id = _new_conn_id()
        self.conn_name = conn_name
        self.socket = socket
        self.peer_ip = peer_address[0]   # type: str
        self.peer_port = peer_address[1] # type: int

        # Total bytes transferred via this connection
        self.total_bytes = 0

        # How many messages this connection transported
        self.total_messages = 0

        # When the connection was started
        self.first_transferred = datetime.utcnow()

        # When the connection was last used
        self.last_transferred = self.first_transferred

        # Statistics broken down by each message type, e.g. ADT
        self.stats_per_msg_type = {}

        self.peer_fqdn = get_fqdn_by_ip(self.peer_ip, 'peer', _server_type)
        self.local_ip, self.local_port, self.local_fqdn = self._get_local_conn_info('local')

# ################################################################################################################################

    def get_conn_pretty_info(self):
        return '{}; `{}:{}` ({}) to `{}:{}` ({}) ({}) (c:{}; b:{})'.format(
            self.conn_id, self.peer_ip, self.peer_port, self.peer_fqdn,
            self.local_ip, self.local_port, self.local_fqdn, self.conn_name, self.total_messages, self.total_bytes)

# ################################################################################################################################

    def _get_local_conn_info(self, default_local_fqdn):
        # type: (str) -> tuple
        local_ip, local_port = self.socket.getsockname()
        local_fqdn = get_fqdn_by_ip(local_ip, default_local_fqdn, _server_type)

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

class SocketReader:
    """ Each instance of this class handles an individual HL7 MLLP connection in handle_connection.
    """

    def __init__(self, config):
        # type: (Bunch)
        self.config = config
        self.address = config.address
        self.name = config.name
        self.should_log_messages = config.should_log_messages # type: bool

        self.start_seq   = config.start_seq
        self.end_seq     = config.end_seq
        self.end_seq_len = len(config.end_seq)

        self.keep_running = True
        self.impl = None # type: ZatoStreamServer

        self.logger = getLogger('zato')
        self.logger.setLevel(config.logging_level)

        self._logger_info = self.logger.info
        self._logger_debug = self.logger.debug
        self._has_debug_log = self.logger.isEnabledFor(logging.DEBUG)

# ################################################################################################################################

    def start(self):

        # Create a new server connection ..
        self.impl = ZatoStreamServer(self.address, self.handle)

        # .. log info that we are starting ..
        self._logger_info('Starting %s connection `%s` (%s)', _server_type, self.name, self.address)

        # .. and start to serve.
        self.impl.serve_forever()

# ################################################################################################################################

    def handle(self, socket, peer_address):
        try:
            self._handle(socket, peer_address)
        except Exception:
            self.logger.warn('Exception in %s (%s %s); e:`%s`', self._handle, socket, peer_address, format_exc())
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

        # To make fewer namespace lookups
        _max_msg_size = self.config.max_msg_size         # type: int
        _read_buffer_size = self.config.read_buffer_size # type: int
        _recv_timeout = self.config.recv_timeout         # type: float

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

                    # The first byte may be a header and we need to check whether we require it or not at this stage of parsing.
                    # This method will close the connection if anything to do with header parsing is invalid.
                    if not _check_header(conn_ctx, request_ctx, data):
                        return

                    # This is a valid message so we can append data to our current buffer ..
                    _buffer_append(data)

                    # .. the line that have just received may have been part of a footer
                    # or the footer itself so we need to check it ..

                    # .. but we need to take into account the fact that the footer has been split into two or more
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
                                self._handle_complete_message(True, *_handle_complete_message_args)

                # No data received = remote end is no longer connected.
                else:
                    reason = 'remote end disconnected; `{}`'.format(data)
                    _close_connection(conn_ctx, reason)
                    return

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

        # Update our runtime metadata first.
        conn_ctx.total_bytes += request_ctx.msg_size
        conn_ctx.total_messages += 1
        conn_ctx.last_transferred = _datetime_utcnow()

        # Produce the message to invoke the callback with ..
        _buffer_data = _buffer_join_func(_buffer)

        # .. remove the header and footer ..
        _buffer_data = _buffer_data[1:-2]

        # .. asign the actual business data to message ..
        request_ctx.data = _buffer_data

        # .. invoke the callback ..
        response = _run_callback(conn_ctx, request_ctx)

        if self.should_log_messages:
            self._logger_info('Sending HL7 MLLP response to `%s` -> `%s` (c:%s; s=%d)',
                request_ctx.msg_id, response, conn_ctx.conn_id, len(response))

        # .. write the response back ..
        _socket_send(response)

        # .. and reset the message to make it possible to handle a new one.
        _request_ctx_reset()

# ################################################################################################################################

    def _run_callback(self, conn_ctx, request_ctx):
        # type: (ConnCtx, RequestCtx) -> None
        if self.should_log_messages:
            self._logger_info('Handling new HL7 MLLP message (c:%s; %s; %s; s=%d); `%r`',
                conn_ctx.total_messages, conn_ctx.conn_id, request_ctx.msg_id, request_ctx.msg_size, request_ctx.to_dict())
        else:
            self._logger_info('Handling new HL7 MLLP message (c:%s; %s; %s; s=%d)',
                conn_ctx.total_messages, conn_ctx.conn_id, request_ctx.msg_id, request_ctx.msg_size)

        return b'BBB'

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

        bytes_to_check = data[:1]
        meta_attr = 'header'
        has_meta_attr  = 'has_start_seq'
        meta_seq = self.start_seq

        return self._check_meta(conn_ctx, request_ctx, data, bytes_to_check, meta_attr, has_meta_attr, meta_seq)

# ################################################################################################################################

    def _check_footer(self, conn_ctx, request_ctx, data, buffer):
        # type: (ConnCtx, RequestCtx, list) -> bool

        #
        # The last two bytes will possibly contain the footer.
        #
        # [-1] -> last data element in the buffer (possibly the only one)
        # [2:] -> two last bytes of the last data element above
        #
        bytes_to_check = buffer[-1][-2:] # type: bytes

        meta_attr = 'footer'
        has_meta_attr  = 'has_end_seq'
        meta_seq = self.end_seq

        return self._check_meta(conn_ctx, request_ctx, data, bytes_to_check, meta_attr, has_meta_attr, meta_seq)

# ################################################################################################################################
# ################################################################################################################################

def main():

    # Bunch
    from bunch import bunchify

    def on_message(msg):
        # type: (str)
        raise Exception(msg)

    config = bunchify({
        'name': 'Hello HL7 MLLP',
        'address': '0.0.0.0:30191',
        'max_msg_size': 1_000_000,
        'read_buffer_size': 291,
        'recv_timeout': 0.25,
        'logging_level': 'DEBUG',
        'should_log_messages': True,
        'last_msg_log_size': 10,
        'start_seq': b'\x0b',
        'end_seq': b'\x1c\x0d'
    })

    reader = SocketReader(config)
    reader.start()

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
