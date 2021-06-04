# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import errno
from datetime import datetime, timedelta
from logging import getLogger
from socket import timeout as SocketTimeoutException
from time import sleep
from traceback import format_exc

# gevent
from gevent import socket
from gevent.server import StreamServer

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class SocketReaderCtx:
    """ Configuration and context used to read that from sockets via read_from_socket.
    """
    __slots__ = 'conn_id', 'socket', 'max_wait_time', 'max_msg_size', 'read_buffer_size', 'recv_timeout', \
        'should_log_messages', 'buffer', 'is_ok', 'reason'

    def __init__(self, conn_id, socket, max_wait_time, max_msg_size, read_buffer_size, recv_timeout, should_log_messages):
        # type: (str, socket, int, int, int, int, object)
        self.conn_id = conn_id
        self.socket = socket
        self.max_wait_time = max_wait_time
        self.max_msg_size = max_msg_size
        self.read_buffer_size = read_buffer_size
        self.recv_timeout = recv_timeout
        self.should_log_messages = should_log_messages
        self.buffer = []
        self.is_ok = False
        self.reason = ''

# ################################################################################################################################
# ################################################################################################################################

def get_free_port(start=30000):
    port = start
    while is_port_taken(port):
        port += 1
    return port

# ################################################################################################################################

# Taken from http://grodola.blogspot.com/2014/04/reimplementing-netstat-in-cpython.html
def is_port_taken(port):

    # psutil
    import psutil

    # Zato
    from .platform_ import is_linux

    # Shortcut for Linux so as not to bind to a socket which in turn means waiting until it's closed by OS
    if is_linux:
        for conn in psutil.net_connections(kind='tcp'):
            if conn.laddr[1] == port and conn.status == psutil.CONN_LISTEN:
                return True
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('', port))
            sock.close()
        except socket.error as e:
            if e.args[0] == errno.EADDRINUSE:
                return True
            raise

# ################################################################################################################################

def _is_port_ready(port, needs_taken):
    taken = is_port_taken(port)
    return taken if needs_taken else not taken

# ################################################################################################################################

def _wait_for_port(port, timeout, interval, needs_taken):
    port_ready = _is_port_ready(port, needs_taken)

    if not port_ready:
        start = datetime.utcnow()
        wait_until = start + timedelta(seconds=timeout)

        while not port_ready:
            sleep(interval)
            port_ready = _is_port_ready(port, needs_taken)
            if datetime.utcnow() > wait_until:
                break

    return port_ready

# ################################################################################################################################

def wait_for_zato(address, url_path, timeout=60, interval=0.1):
    """ Waits until a Zato server responds.
    """

    # Requests
    from requests import get as requests_get

    # Imported here to avoid circular imports
    from zato.common.util.api import wait_for_predicate

    # Full URL to check a Zato server under
    url = address + url_path

    def _predicate_zato_ping(*ignored_args, **ignored_kwargs):
        try:
            requests_get(url, timeout=interval)
        except Exception as e:
            logger.warn('Waiting for `%s` (%s)', url, e)
        else:
            return True

    return wait_for_predicate(_predicate_zato_ping, timeout, interval, address)

# ################################################################################################################################

def wait_for_zato_ping(address, timeout=60, interval=0.1):
    """ Waits for timeout seconds until address replies to a request sent to /zato/ping.
    """
    wait_for_zato(address, '/zato/ping', timeout, interval)

# ################################################################################################################################

def wait_until_port_taken(port, timeout=2, interval=0.1):
    """ Waits until a given TCP port becomes taken, i.e. a process binds to a TCP socket.
    """
    return _wait_for_port(port, timeout, interval, True)

# ################################################################################################################################

def wait_until_port_free(port, timeout=2, interval=0.1):
    """ Waits until a given TCP port becomes free, i.e. a process releases a TCP socket.
    """
    return _wait_for_port(port, timeout, interval, False)

# ################################################################################################################################

def get_fqdn_by_ip(ip_address, default, log_msg_prefix):
    # type: (str, str) -> str
    try:
        host = socket.gethostbyaddr(ip_address)[0]
        return socket.getfqdn(host)
    except Exception:
        logger.warn('%s exception in FQDN lookup `%s`', log_msg_prefix, format_exc())
        return '(unknown-{}-fqdn)'.format(default)

# ################################################################################################################################

def read_from_socket(ctx, _utcnow=datetime.utcnow, _timedelta=timedelta):
    """ Reads data from an already connected TCP socket.
    """
    # type: (SocketReaderCtx) -> bytes

    # Local aliases
    _should_log_messages = ctx.should_log_messages

    _log_info = logger.warn
    _log_debug = logger.warn

    _conn_id          = ctx.conn_id
    _max_msg_size     = ctx.max_msg_size
    _read_buffer_size = ctx.read_buffer_size
    _recv_timeout     = ctx.recv_timeout

    _socket_recv       = ctx.socket.recv
    _socket_settimeout = ctx.socket.settimeout

    # Wait for that many seconds
    wait_until = _utcnow() + timedelta(seconds=ctx.max_wait_time)

    # How many bytes have we read so far
    msg_size = 0

    # Buffer to accumulate data in
    buffer = []

    # No data received yet
    data = '<initial-no-data>'

    # Run the main loop
    while _utcnow() < wait_until:

        # Check whether reading the data would not exceed our message size limit
        new_size = msg_size + _read_buffer_size
        if new_size > _max_msg_size:
            reason = 'Message would exceed max. size allowed `{}` > `{}`'.format(new_size, _max_msg_size)
            raise ValueError(reason)

        try:

            _socket_settimeout(_recv_timeout)
            data = _socket_recv(_read_buffer_size)

            if _should_log_messages:
                _log_debug('Data received by `%s` (%d) -> `%s`', _conn_id, len(data), data)

        except SocketTimeoutException:
            # This is fine, we just iterate until wait_until time.
            pass
        else:
            # Some data was received ..
            if data:
                buffer.append(data)

            # .. otherwise, the remote end disconnected so we can end.
            break

    # If we are here, it means that we have all the data needed so we can just return it now
    result = b''.join(buffer)

    if _should_log_messages:
        _log_info('Returning result from `%s` (%d) -> `%s`', _conn_id, len(result), result)

    return result

# ################################################################################################################################

def parse_address(address):
    # type: (str) -> (str, int)

    # First, let's reverse it in case input contains an IPv6 address ..
    address = address[::-1] # type: str

    # .. now, split on the first colon to give the information we seek ..
    port, host = address.split(':', 1)

    # .. reverse the values back
    host = host[::-1]
    port = port[::-1]

    # .. port needs to be an integer ..
    port = int(port)

    # .. and now we can return the result.
    return host, port

# ################################################################################################################################
# ################################################################################################################################

class ZatoStreamServer(StreamServer):

# ################################################################################################################################

    def shutdown(self):
        self.close()

# ################################################################################################################################

    # These two methods are reimplemented from gevent.server to make it possible to use SO_REUSEPORT.

    @classmethod
    def get_listener(self, address, backlog=None, family=None):
        if backlog is None:
            backlog = self.backlog
        return ZatoStreamServer._make_socket(address, backlog=backlog, reuse_addr=self.reuse_addr, family=family)

    @staticmethod
    def _make_socket(address, backlog=50, reuse_addr=None, family=socket.AF_INET):
        sock = socket.socket(family=family)
        if reuse_addr is not None:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, reuse_addr)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        try:
            sock.bind(address)
        except socket.error as e:
            strerror = getattr(e, 'strerror', None)
            if strerror is not None:
                e.strerror = strerror + ': ' + repr(address)
            raise
        sock.listen(backlog)
        sock.setblocking(0)
        return sock

# ################################################################################################################################
# ################################################################################################################################
