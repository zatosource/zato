# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# One process of the load generator of the scaling measurement. The process runs on one CPU of its own, keeps
# a fixed number of HTTP/1.1 connections to the server, each of which sends its next request when the response
# to the previous one arrives, and records the latency of each response that completes within the measurement window.
# The configuration arrives as JSON in the first argument, the latencies are written to the file that it names
# as signed 64-bit nanoseconds, and the counts are printed as JSON.

# stdlib
import json
import os
import selectors
import socket
import sys
from array import array
from time import monotonic_ns, time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The size of one read from a connection
    Read_Size = 65536

    # The separator of the headers and the body of a response, and of the lines of the headers
    Header_End = b'\r\n\r\n'
    Line_End = b'\r\n'

    # The headers that a response is parsed for, in lower case
    Content_Length = b'content-length:'
    Connection_Close = b'connection: close'

    # The status line prefix of a successful response
    Status_OK = b'HTTP/1.1 200'

    # The type code of the array of latencies, signed 64-bit integers
    Latency_Type = 'q'

    Nanoseconds_Per_Second = 1_000_000_000

# ################################################################################################################################
# ################################################################################################################################

class Connection:
    """ One connection of the load generator and the response that it is receiving.
    """

    def __init__(self, host:'str', port:'int') -> 'None':
        self.socket = socket.create_connection((host, port))
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.socket.setblocking(False)

        self.buffer = b''
        self.sent_at = 0

# ################################################################################################################################
# ################################################################################################################################

class LoadProcess:
    """ Sends requests over all the connections of the process until the end of the measurement window.
    """

    def __init__(self, config:'anydict') -> 'None':
        self.host = config['host']
        self.port = config['port']
        self.request = config['request'].encode('ascii')
        self.connection_count = config['connections']

        # The window is given in wall-clock time, which every process of the generator shares,
        # and converted to the monotonic clock of this process
        offset = monotonic_ns() - int(time() * ModuleCtx.Nanoseconds_Per_Second)
        self.window_start = int(config['window_start'] * ModuleCtx.Nanoseconds_Per_Second) + offset
        self.window_end = int(config['window_end'] * ModuleCtx.Nanoseconds_Per_Second) + offset

        self.latencies = array(ModuleCtx.Latency_Type)
        self.errors = 0
        self.reconnects = 0

        self.selector = selectors.DefaultSelector()

# ################################################################################################################################

    def _open(self) -> 'None':
        """ Opens one connection and sends its first request.
        """
        connection = Connection(self.host, self.port)
        _ = self.selector.register(connection.socket, selectors.EVENT_READ, connection)
        self._send(connection)

# ################################################################################################################################

    def _send(self, connection:'Connection') -> 'None':
        connection.sent_at = monotonic_ns()
        connection.socket.sendall(self.request)

# ################################################################################################################################

    def _reopen(self, connection:'Connection') -> 'None':
        """ Replaces a connection that the server closed, which it does after a fixed number of requests.
        """
        _ = self.selector.unregister(connection.socket)
        connection.socket.close()
        self.reconnects += 1
        self._open()

# ################################################################################################################################

    def _on_response(self, connection:'Connection', headers:'bytes') -> 'None':
        """ Records a complete response and sends the next request, or closes the connection after the window.
        """
        completed_at = monotonic_ns()

        if self.window_start <= completed_at <= self.window_end:
            self.latencies.append(completed_at - connection.sent_at)

            if not headers.startswith(ModuleCtx.Status_OK):
                self.errors += 1

        if completed_at > self.window_end:
            _ = self.selector.unregister(connection.socket)
            connection.socket.close()
            return

        if ModuleCtx.Connection_Close in headers.lower():
            self._reopen(connection)
        else:
            self._send(connection)

# ################################################################################################################################

    def _on_readable(self, connection:'Connection') -> 'None':
        data = connection.socket.recv(ModuleCtx.Read_Size)

        # The server closed the connection before a response, so the request is sent again on a new one
        if not data:
            self._reopen(connection)
            return

        connection.buffer += data

        header_end = connection.buffer.find(ModuleCtx.Header_End)
        if header_end < 0:
            return

        headers = connection.buffer[:header_end]
        content_length = _get_content_length(headers)
        response_end = header_end + len(ModuleCtx.Header_End) + content_length

        if len(connection.buffer) < response_end:
            return

        connection.buffer = connection.buffer[response_end:]
        self._on_response(connection, headers)

# ################################################################################################################################

    def run(self) -> 'anydict':

        for _ in range(self.connection_count):
            self._open()

        while self.selector.get_map():
            for key, _ in self.selector.select():
                self._on_readable(key.data)

        out = {
            'count': len(self.latencies),
            'errors': self.errors,
            'reconnects': self.reconnects,
        }

        return out

# ################################################################################################################################
# ################################################################################################################################

def _get_content_length(headers:'bytes') -> 'int':
    """ Returns the value of the Content-Length header of a response.
    """
    for line in headers.split(ModuleCtx.Line_End):
        if line.lower().startswith(ModuleCtx.Content_Length):
            _, value = line.split(b':', 1)
            out = int(value)
            return out

    raise Exception(f'No Content-Length in {headers!r}')

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    config = json.loads(sys.argv[1])

    os.sched_setaffinity(0, [config['cpu']])

    process = LoadProcess(config)
    out = process.run()

    with open(config['latency_path'], 'wb') as latency_file:
        process.latencies.tofile(latency_file)

    print(json.dumps(out), flush=True)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
