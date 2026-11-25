# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The processes of the HTTP server of zato_server_core and the HTTP clients that the tests of its Unix domain socket share.

# stdlib
import os
import select
import shutil
import signal
import socket
import sys
import tempfile
from http.client import HTTPConnection
from json import loads
from subprocess import PIPE, Popen
from typing import NamedTuple

# Zato
from zato.common.test.reservation import PortInUse, reserve_name, start_on_reserved_port

from server_process import ModuleCtx as ServerCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.reservation import NameReservation, PortReservation
    from zato.common.typing_ import anydict, list_, strnone

    NameReservation = NameReservation
    PortReservation = PortReservation

    popenlist = list_['Popen[str]']

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The script that runs the server
    Server_Script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server_process.py')

    # The purpose of the reserved ports and the prefix of the reserved socket directories
    Port_Purpose      = 'http-server-unix-socket'
    Socket_Dir_Prefix = 'zato-http-unix'

    # The mode of a socket directory and the name of the socket file in it
    Socket_Dir_Mode  = 0o700
    Socket_File_Name = 'server.sock'

    # The host name that the HTTP clients send, whichever listener they connect to
    Client_Host = 'localhost'

    # How long a server takes to start and to stop, and how long a request takes, in seconds
    Start_Timeout   = 30.0
    Stop_Timeout    = 30.0
    Request_Timeout = 10.0

# ################################################################################################################################
# ################################################################################################################################

# The processes that the current test started, which a failed test leaves running
_started_processes:'popenlist' = []

# ################################################################################################################################
# ################################################################################################################################

class ServerProcess:
    """ A process of the HTTP server that a test started, with the reservation of its TCP port.
    """

    def __init__(self, process:'Popen[str]', reservation:'PortReservation') -> 'None':
        self.process = process
        self.reservation = reservation
        self.port = reservation.port

# ################################################################################################################################
# ################################################################################################################################

class TCPResponse(NamedTuple):
    """ The request context that the server reported for a request over TCP, with the local port of the client.
    """
    request_ctx: 'anydict'
    client_port: int

# ################################################################################################################################
# ################################################################################################################################

class UnixHTTPConnection(HTTPConnection):
    """ An HTTP connection over a Unix domain socket.
    """

    def __init__(self, unix_socket_path:'str') -> 'None':
        super().__init__(ModuleCtx.Client_Host, timeout=ModuleCtx.Request_Timeout)
        self.unix_socket_path = unix_socket_path

    def connect(self) -> 'None':
        unix_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        unix_socket.settimeout(ModuleCtx.Request_Timeout)
        unix_socket.connect(self.unix_socket_path)
        self.sock = unix_socket

# ################################################################################################################################
# ################################################################################################################################

class SocketDir:
    """ A directory reserved for the socket file of one test.
    """

    def __init__(self, reservation:'NameReservation', path:'str') -> 'None':
        self.reservation = reservation
        self.path = path
        self.socket_path = os.path.join(path, ModuleCtx.Socket_File_Name)

# ################################################################################################################################

def new_socket_dir() -> 'SocketDir':
    """ Creates a directory under a reserved name for the socket file of a test, with a path short enough for AF_UNIX.
    """
    reservation = reserve_name(ModuleCtx.Socket_Dir_Prefix)

    temp_dir = tempfile.gettempdir()
    path = os.path.join(temp_dir, reservation.name)
    os.mkdir(path, ModuleCtx.Socket_Dir_Mode)

    out = SocketDir(reservation, path)
    return out

# ################################################################################################################################

def remove_socket_dir(socket_dir:'SocketDir') -> 'None':
    """ Removes the directory of a test and releases its name.
    """
    shutil.rmtree(socket_dir.path)
    socket_dir.reservation.release()

# ################################################################################################################################
# ################################################################################################################################

def _read_ready_line(process:'Popen[str]') -> 'str':
    """ Returns the first line of the output of a server process, or an empty string if the process printed none in time.
    """
    stdout = process.stdout
    if stdout is None:
        raise Exception('Server process has no stdout pipe')

    readable, _, _ = select.select([stdout], [], [], ModuleCtx.Start_Timeout)

    if readable:
        out = stdout.readline()
    else:
        out = ''

    out = out.strip()
    return out

# ################################################################################################################################

def _start_process(port:'int', unix_socket_path:'strnone') -> 'Popen[str]':
    """ Starts a server process on the port and waits until both of its listeners accept connections.
    """
    command = [sys.executable, ModuleCtx.Server_Script, f'{port}']

    if unix_socket_path:
        command.append(unix_socket_path)

    process = Popen(command, stdout=PIPE, stderr=PIPE, text=True)
    _started_processes.append(process)

    ready_line = _read_ready_line(process)

    # The process is ready ..
    if ready_line == ServerCtx.Ready_Line:
        return process

    # .. or it did not start in time or it exited, in which case its error is reported.
    process.kill()
    _, stderr = process.communicate(timeout=ModuleCtx.Stop_Timeout)
    _started_processes.remove(process)

    bind_error = f'bind({ServerCtx.Host}:{port}) failed'
    if bind_error in stderr:
        raise PortInUse(stderr)
    else:
        raise Exception(f'Server process did not start -> {stderr}')

# ################################################################################################################################

def start_server(unix_socket_path:'strnone') -> 'ServerProcess':
    """ Starts a server process on a reserved port, with a Unix domain socket when a path is given.
    """
    def start(port:'int') -> 'Popen[str]':
        out = _start_process(port, unix_socket_path)
        return out

    started = start_on_reserved_port(ModuleCtx.Port_Purpose, start)

    out = ServerProcess(started.result, started.reservation)
    return out

# ################################################################################################################################

def stop_server(server:'ServerProcess') -> 'str':
    """ Stops a server process with SIGTERM, waits until it exits and returns its output.
    """
    server.process.send_signal(signal.SIGTERM)

    try:
        stdout, stderr = server.process.communicate(timeout=ModuleCtx.Stop_Timeout)
    finally:
        server.reservation.release()

    _started_processes.remove(server.process)

    if server.process.returncode != 0:
        raise Exception(f'Server process exited with {server.process.returncode} -> {stderr}')

    return stdout

# ################################################################################################################################

def terminate_started_servers() -> 'None':
    """ Kills the server processes that a failed test left running.
    """
    for process in _started_processes:
        process.kill()
        _ = process.communicate(timeout=ModuleCtx.Stop_Timeout)

    _started_processes.clear()

# ################################################################################################################################
# ################################################################################################################################

def _get_response(connection:'HTTPConnection', path:'str') -> 'anydict':
    """ Sends a GET request over a connection and returns the request context that the server reported.
    """
    connection.request('GET', path, headers={'Connection': 'close'})
    response = connection.getresponse()
    data = response.read()

    if response.status != ServerCtx.Response_Status_Code:
        raise Exception(f'Unexpected status {response.status} -> {data!r}')

    out = loads(data)
    return out

# ################################################################################################################################

def get_over_tcp(port:'int', path:'str') -> 'TCPResponse':
    """ Sends a GET request over TCP and returns the request context that the server reported,
    together with the local port of the client.
    """
    connection = HTTPConnection(ServerCtx.Host, port, timeout=ModuleCtx.Request_Timeout)

    try:
        connection.connect()
        client_address = connection.sock.getsockname()
        client_port = client_address[1]
        request_ctx = _get_response(connection, path)
    finally:
        connection.close()

    out = TCPResponse(request_ctx, client_port)
    return out

# ################################################################################################################################

def get_over_unix_socket(unix_socket_path:'str', path:'str') -> 'anydict':
    """ Sends a GET request over a Unix domain socket and returns the request context that the server reported.
    """
    connection = UnixHTTPConnection(unix_socket_path)

    try:
        out = _get_response(connection, path)
    finally:
        connection.close()

    return out

# ################################################################################################################################

def leave_stale_socket_file(unix_socket_path:'str') -> 'None':
    """ Binds a socket to the path and closes it without removing its file, as a process that was killed leaves it.
    """
    stale_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    stale_socket.bind(unix_socket_path)
    stale_socket.close()

# ################################################################################################################################
# ################################################################################################################################
