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

# gevent
from gevent import sleep, socket, Timeout

# hl7apy
from hl7apy.mllp import AbstractHandler as hl7apy_AbstractHandler, MLLPServer as hl7apy_MLLPServer

# Zato
from zato.common.util.api import new_cid
from zato.common.util.tcp import get_fqdn_by_ip, ZatoStreamServer

# ################################################################################################################################

if 0:
    from gevent._socket3 import socket

    socket = socket

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ################################################################################################################################

logger = getLogger('zato')
logger_hl7 = getLogger('zato_hl7')

# ################################################################################################################################

_server_type = 'HL7 MLLP'

# ################################################################################################################################

_stats_attrs = 'total_bytes', 'total_messages', 'avg_msg_size', 'first_transferred', 'last_transferred'

# ################################################################################################################################
# ################################################################################################################################

class _MsgTypeStats:
    """ Represents transfer statistics for each message type.
    """
    __slots__ = ('msg_type',) + _stats_attrs

# ################################################################################################################################
# ################################################################################################################################

class ConnCtx:
    """ Details of an individual remote connection to a server.
    """
    __slots__ = ('conn_id', 'conn_name', 'socket', 'peer_ip', 'peer_port', 'peer_fqdn', 'local_ip', \
        'local_port', 'local_fqdn', 'stats_per_msg_type') + _stats_attrs

    def __init__(self, conn_name, socket, peer_address):
        # type: (socket, tuple)

        self.conn_id = 'z7m.{}'.format(new_cid(5))
        self.conn_name = conn_name
        self.socket = socket
        self.peer_ip = peer_address[0]   # type: str
        self.peer_port = peer_address[1] # type: int

        # Total bytes transferred via this connections
        self.total_bytes = 0

        # How many messages this connection transported
        self.total_messages = 0

        # Average message size
        self.avg_msg_size = 0

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
        return '{}; `{}:{}` ({}) to `{}:{}` ({}) ({})'.format(
            self.conn_id, self.peer_ip, self.peer_port, self.peer_fqdn,
            self.local_ip, self.local_port, self.local_fqdn, self.conn_name)

# ################################################################################################################################

    def _get_local_conn_info(self, default_local_fqdn):
        # type: (str) -> tuple
        local_ip, local_port = self.socket.getsockname()
        local_fqdn = get_fqdn_by_ip(local_ip, default_local_fqdn, _server_type)

        return local_ip, local_port, local_fqdn

# ################################################################################################################################
# ################################################################################################################################

class MsgCtx:
    """ Details of an individual message received from a remote connection.
    """
    __slots__ = 'msg_size', 'data', 'meta'

# ################################################################################################################################

    def __init__(self):
        self.msg_size = None # type: int
        self.data = b''
        self.meta = {}
        self.reset()

# ################################################################################################################################

    def reset(self):
        self.msg_size = 0
        self.data = b''
        self.meta['has_header'] = False
        self.meta['has_footer'] = False

# ################################################################################################################################

    def to_dict(self):
        return {
            'msg_size': self.msg_size,
            'meta': self.meta,
            'data': self.data,
        }

# ################################################################################################################################
# ################################################################################################################################

class HL7MLLPServer:
    """ Each instance of this class handles an individual HL7 MLLP connection in handle_connection.
    """
    header_seq = b'\x0b'
    footer_seq   = b'\x1c\x0d'

# ################################################################################################################################

    def __init__(self, address, name):
        # type: (str, str)
        self.address = address
        self.name = name
        self.keep_running = True
        self.impl = None # type: ZatoStreamServer
        self.max_msg_size = 1_000_000 # In bytes
        self.read_buffer_size = 20#48

# ################################################################################################################################

    def start(self):

        logger.info('IMPL #1')

        self.impl = ZatoStreamServer(self.address, self.handle)

        logger.info('IMPL #2')

        self.impl.serve_forever()

# ################################################################################################################################

    def handle(self, socket, peer_address):
        # type: (socket, tuple)

        # Wraps all the metadata about the connection
        conn_ctx = ConnCtx(self.name, socket, peer_address)

        logger.info('New HL7 MLLP connection; %s', conn_ctx.get_conn_pretty_info())

        # Current message whose contents we are accumulating
        _buffer = []

        # Details of the current message
        msg_ctx = MsgCtx()

        # Indicates whether the last .recv call indicated that the remote end disconnected,
        # and if so, this tells us to enter a short sleep period.
        has_timeout = False

        # To make fewer namespace lookups
        _sleep = sleep
        _max_msg_size = self.max_msg_size

        _run_callback = self._run_callback
        _read_buffer_size = self.read_buffer_size
        _check_header = self._check_header
        _check_footer = self._check_footer
        _close_connection = self._close_connection
        _msg_ctx_reset = msg_ctx.reset
        _buffer_append = _buffer.append
        _buffer_join_func = b''.join

        _socket_recv = conn_ctx.socket.recv
        _socket_send = conn_ctx.socket.send
        _socket_settimeout = conn_ctx.socket.settimeout

        # Run the main loop
        while self.keep_running:

            # In each iteration, assume that no data was received
            data = None

            # Check whether reading the data would not exceed our message size limit
            new_size = msg_ctx.msg_size + _read_buffer_size
            if new_size > _max_msg_size:
                reason = 'message would exceed max. size allowed `{}` > `{}`'.format(new_size, _max_msg_size)
                _close_connection(conn_ctx, reason)
                return

            # Receive data from the other end
            _socket_settimeout(0.1)

            # Try to receive some data from the socket ..
            try:

                # .. read data in ..
                data = _socket_recv(_read_buffer_size)

                # if data was received, it means that there was no timeout ..
                if data:
                    has_timeout = False

                # .. otherwise, since we did not time out but there is not data,
                # it means that the remote end disconnected.
                else:
                    reason = 'remote end disconnected; `{}`'.format(data)
                    _close_connection(conn_ctx, reason)
                    return

            # .. catch timeouts here but no other exception type ..
            except SocketTimeoutException as e:
                has_timeout = True

            else:
                # Receiving an empty string means that the client disconnected
                # in which case we close the connection too.
                needs_sleep = False

            #
            # If a timeout occurred, it means that we have potentially received the whole message already.
            #
            if has_timeout:

                # Confirm if we already have received the whole message, as indicated by the presence of its footer.
                # Note that at this point we still do not know if the header was received so we must check it too.
                if msg_ctx.meta['has_header']:
                    if not _check_footer(conn_ctx, msg_ctx, data, _buffer):
                        return

                    # If we have a footer, this means that the message is complete and our callback can process it
                    if msg_ctx.meta['has_footer']:

                        self._handle_complete_message(_buffer, _buffer_join_func, msg_ctx, _msg_ctx_reset,
                            _socket_send, _run_callback)

            #
            # No timeout and some data was received means that we are still receiving the message from the socket.
            #
            else:

                # If we are here, it means that the recv call succeeded so we can increase the message size
                # by how many bytes were actually read from the socket.
                msg_ctx.msg_size += len(data)

                # The first byte may be a header and we need to check whether we require it or not at this stage of parsing.
                # This method will close the connection if anything to do with header parsing is invalid.
                if not _check_header(conn_ctx, msg_ctx, data):
                    return

                # This is a valid message so we can append data to our current buffer
                _buffer_append(data)

# ################################################################################################################################

    def _handle_complete_message(self, _buffer, _buffer_join_func, msg_ctx, _msg_ctx_reset, _socket_send, _run_callback):

        # Produce the message to invoke the callback with ..
        _buffer_data = _buffer_join_func(_buffer)

        # .. remove the header and footer ..
        _buffer_data = _buffer_data[1:-2]

        # .. asign the actual business data to message ..
        msg_ctx.data = _buffer_data

        # .. invoke the callback ..
        response = _run_callback(msg_ctx)

        # .. write the response back ..
        _socket_send(response)

        # .. and reset the message to make it possible to handle a new one.
        _msg_ctx_reset()

# ################################################################################################################################

    def _run_callback(self, msg_ctx):
        # type: MsgCtx -> None
        logger.info('Handling new message `%r`', msg_ctx.to_dict())

        return b'BBB'

# ################################################################################################################################

    def _close_connection(self, conn_ctx, reason):
        # type: str -> None
        logger.info('Closing connection; %s; %s', reason, conn_ctx.get_conn_pretty_info())
        conn_ctx.socket.close()

# ################################################################################################################################

    def _check_meta(self, conn_ctx, msg_ctx, data, bytes_to_check, meta_attr, has_meta_attr, meta_seq):
        # type: (ConnCtx, MsgCtx, bytes, bytes, str, bool, bytes) -> bool

        # If we already have the meta element then we do not expect another one
        # while we are still processing the same message and if one is found, we close the connection.
        if msg_ctx.meta[has_meta_attr]:
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
        msg_ctx.meta[has_meta_attr] = True
        return True

# ################################################################################################################################

    def _check_header(self, conn_ctx, msg_ctx, data):

        bytes_to_check = data[:1]
        meta_attr = 'header'
        has_meta_attr  = 'has_header'
        meta_seq = self.header_seq

        return self._check_meta(conn_ctx, msg_ctx, data, bytes_to_check, meta_attr, has_meta_attr, meta_seq)

# ################################################################################################################################

    def _check_footer(self, conn_ctx, msg_ctx, data, buffer):
        # type: (ConnCtx, MsgCtx, list) -> bool

        #
        # The last two bytes will possibly contain the footer.
        #
        # [-1] -> last data element in the buffer (possibly the only one)
        # [2:] -> two last bytes of the last data element above
        #
        bytes_to_check = buffer[-1][-2:] # type: bytes

        meta_attr = 'footer'
        has_meta_attr  = 'has_footer'
        meta_seq = self.footer_seq

        return self._check_meta(conn_ctx, msg_ctx, data, bytes_to_check, meta_attr, has_meta_attr, meta_seq)

# ################################################################################################################################
# ################################################################################################################################

def main():

    name = 'Hello HL7 MLLP'
    host = '0.0.0.0'
    port = 30191
    address = '{}:{}'.format(host, port)

    def on_message(msg):
        # type: (str)
        logger.info('MSG RECEIVED %s', msg)

    server = HL7MLLPServer(address, name)
    server.start()

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
