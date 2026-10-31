# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A TCP proxy between the processes of a test and a database, run as a process of its own. It stands for the endpoint
# of a managed database service or a virtual IP address, which a failover moves to another server. A control endpoint
# repoints it, ends its connections, refuses new ones, delays the data, or holds the data of open connections.

# gevent
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import socket
import struct
import sys
from argparse import ArgumentParser
from logging import basicConfig, getLogger, INFO

# gevent
from gevent import sleep, spawn
from gevent.event import Event
from gevent.pywsgi import WSGIServer
from gevent.server import StreamServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, callable_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato.test.tcp_proxy')

# ################################################################################################################################
# ################################################################################################################################

# The host of the upstream server and of the listening sockets.
_host = '127.0.0.1'

# How much data one read takes from a socket.
_read_size = 65536

# A linger of zero seconds makes closing a socket send a reset rather than a regular end of the connection.
_linger_reset = struct.pack('ii', 1, 0)

# ################################################################################################################################
# ################################################################################################################################

class _Connection:
    """ One client connection and the upstream connection that it is paired with.
    """
    def __init__(self, client_socket:'socket.socket', upstream_socket:'socket.socket') -> 'None':
        self.client_socket = client_socket
        self.upstream_socket = upstream_socket

    def reset(self) -> 'None':
        for item in (self.client_socket, self.upstream_socket):
            try:
                item.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, _linger_reset)
                item.close()
            except OSError:
                pass

# ################################################################################################################################
# ################################################################################################################################

class Proxy:
    """ Forwards each client connection to the current upstream port, under the conditions the control endpoint sets.
    """

    def __init__(self, upstream_port:'int') -> 'None':
        self.upstream_port = upstream_port
        self.is_blocked = False
        self.latency_seconds = 0.0
        self.connections:'set[_Connection]' = set()

        # Set while the data of open connections flows, cleared while it is held.
        self.is_flowing = Event()
        self.is_flowing.set()

# ################################################################################################################################

    def _pipe(self, connection:'_Connection', source:'socket.socket', target:'socket.socket') -> 'None':
        """ Copies the data of one direction of a connection until either side ends it.
        """
        try:
            while True:
                data = source.recv(_read_size)
                if not data:
                    break

                _ = self.is_flowing.wait()

                if self.latency_seconds:
                    sleep(self.latency_seconds)

                target.sendall(data)

        except OSError:
            pass

        finally:
            self.connections.discard(connection)
            connection.reset()

# ################################################################################################################################

    def handle(self, client_socket:'socket.socket', address:'any_') -> 'None':
        """ Pairs a new client connection with an upstream connection, unless new connections are refused.
        """
        if self.is_blocked:
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, _linger_reset)
            client_socket.close()
            return

        try:
            upstream_socket = socket.create_connection((_host, self.upstream_port))
        except OSError:
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, _linger_reset)
            client_socket.close()
            return

        connection = _Connection(client_socket, upstream_socket)
        self.connections.add(connection)

        _ = spawn(self._pipe, connection, upstream_socket, client_socket)
        self._pipe(connection, client_socket, upstream_socket)

# ################################################################################################################################

    def reset_all(self) -> 'int':
        """ Ends every open connection with a reset and returns how many there were.
        """
        connections = list(self.connections)
        self.connections.clear()

        for connection in connections:
            connection.reset()

        out = len(connections)
        return out

# ################################################################################################################################

    def control(self, environ:'anydict', start_response:'callable_') -> 'anylist':
        """ The control endpoint - each path is one command, with its argument as the last part of the path.
        """
        parts = environ['PATH_INFO'].strip('/').split('/')
        command = parts[0]

        if command == 'upstream':
            self.upstream_port = int(parts[1])
            result = self.reset_all()

        elif command == 'reset':
            result = self.reset_all()

        elif command == 'block':
            self.is_blocked = True
            result = self.reset_all()

        elif command == 'unblock':
            self.is_blocked = False
            result = 0

        elif command == 'latency':
            self.latency_seconds = int(parts[1]) / 1000
            result = 0

        elif command == 'hold':
            self.is_flowing.clear()
            result = len(self.connections)

        elif command == 'release':
            self.is_flowing.set()
            result = len(self.connections)

        else:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [command.encode()]

        logger.info('Command %s -> %s', environ['PATH_INFO'], result)

        start_response('200 OK', [('Content-Type', 'text/plain')])
        out = [str(result).encode()]

        return out

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':

    basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', stream=sys.stdout)

    parser = ArgumentParser()
    _ = parser.add_argument('--listen-port', type=int, required=True)
    _ = parser.add_argument('--control-port', type=int, required=True)
    _ = parser.add_argument('--upstream-port', type=int, required=True)
    args = parser.parse_args()

    proxy = Proxy(args.upstream_port)

    control_server = WSGIServer((_host, args.control_port), proxy.control, log=None)
    control_server.start()

    logger.info('Proxy on port %s to port %s, control on port %s', args.listen_port, args.upstream_port, args.control_port)

    server = StreamServer((_host, args.listen_port), proxy.handle)
    server.serve_forever()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
