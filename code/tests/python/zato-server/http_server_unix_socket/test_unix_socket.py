# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Unix domain socket listener of the HTTP server of zato_server_core, next to its TCP listener.

# stdlib
import os
import socket
import stat

# Zato
from server_common import get_over_tcp, get_over_unix_socket, leave_stale_socket_file, start_server, stop_server
from server_process import ModuleCtx as ServerCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from server_common import SocketDir

    SocketDir = SocketDir

# ################################################################################################################################
# ################################################################################################################################

# The REMOTE_ADDR and REMOTE_PORT of a request over the Unix domain socket
_unix_remote_addr = '127.0.0.1'
_unix_remote_port = '0'

# The REMOTE_ADDR of a request over TCP from this host
_tcp_remote_addr = '127.0.0.1'

# The mode of the socket file
_socket_file_mode = 0o600

# The paths of the requests
_unix_path = '/test/unix-socket'
_tcp_path  = '/test/tcp'

# ################################################################################################################################
# ################################################################################################################################

def test_request_over_unix_socket(socket_dir:'SocketDir') -> 'None':
    """ A request over the Unix domain socket reaches the request handler with the address of the Unix listener.
    """
    server = start_server(socket_dir.socket_path)

    request_ctx = get_over_unix_socket(socket_dir.socket_path, _unix_path)

    _ = stop_server(server)

    assert request_ctx['PATH_INFO'] == _unix_path
    assert request_ctx['REMOTE_ADDR'] == _unix_remote_addr
    assert request_ctx['REMOTE_PORT'] == _unix_remote_port

# ################################################################################################################################

def test_request_over_tcp_with_unix_listener(socket_dir:'SocketDir') -> 'None':
    """ A request over TCP reaches the request handler with the address of the client while the Unix listener is active,
    and both listeners serve requests one after another.
    """
    server = start_server(socket_dir.socket_path)

    tcp_response = get_over_tcp(server.port, _tcp_path)
    unix_request_ctx = get_over_unix_socket(socket_dir.socket_path, _unix_path)

    _ = stop_server(server)

    tcp_request_ctx = tcp_response.request_ctx
    expected_tcp_port = f'{tcp_response.client_port}'

    assert tcp_request_ctx['PATH_INFO'] == _tcp_path
    assert tcp_request_ctx['REMOTE_ADDR'] == _tcp_remote_addr
    assert tcp_request_ctx['REMOTE_PORT'] == expected_tcp_port

    assert unix_request_ctx['PATH_INFO'] == _unix_path
    assert unix_request_ctx['REMOTE_PORT'] == _unix_remote_port

# ################################################################################################################################

def test_request_over_tcp_without_unix_socket() -> 'None':
    """ A server without a Unix socket path listens on TCP only.
    """
    server = start_server(None)

    tcp_response = get_over_tcp(server.port, _tcp_path)

    output = stop_server(server)

    assert tcp_response.request_ctx['PATH_INFO'] == _tcp_path
    assert tcp_response.request_ctx['REMOTE_ADDR'] == _tcp_remote_addr
    assert ServerCtx.Stopped_Line in output

# ################################################################################################################################

def test_socket_file_mode(socket_dir:'SocketDir') -> 'None':
    """ The socket file is readable and writable by its owner only.
    """
    server = start_server(socket_dir.socket_path)

    file_stat = os.stat(socket_dir.socket_path)

    _ = stop_server(server)

    file_mode = stat.S_IMODE(file_stat.st_mode)

    assert stat.S_ISSOCK(file_stat.st_mode)
    assert file_mode == _socket_file_mode

# ################################################################################################################################

def test_stale_socket_file_removed_at_start(socket_dir:'SocketDir') -> 'None':
    """ A socket file that a previous process left at the path is replaced by the socket file of the server.
    """
    leave_stale_socket_file(socket_dir.socket_path)

    # Nothing listens on the stale socket file ..
    stale_stat = os.stat(socket_dir.socket_path)
    assert stat.S_ISSOCK(stale_stat.st_mode)

    # .. the server starts in its place ..
    server = start_server(socket_dir.socket_path)

    # .. and it serves requests over its own socket file.
    request_ctx = get_over_unix_socket(socket_dir.socket_path, _unix_path)

    _ = stop_server(server)

    assert request_ctx['PATH_INFO'] == _unix_path

# ################################################################################################################################

def test_socket_file_removed_at_stop(socket_dir:'SocketDir') -> 'None':
    """ The socket file of the server is removed when the server stops.
    """
    server = start_server(socket_dir.socket_path)

    exists_while_running = os.path.exists(socket_dir.socket_path)

    output = stop_server(server)

    exists_after_stop = os.path.exists(socket_dir.socket_path)

    assert exists_while_running
    assert not exists_after_stop
    assert ServerCtx.Stopped_Line in output

# ################################################################################################################################

def test_socket_file_of_another_process_kept_at_stop(socket_dir:'SocketDir') -> 'None':
    """ A socket file that another process bound at the path after the server started stays in place when the server stops.
    """
    server = start_server(socket_dir.socket_path)

    # Another process replaces the socket file of the server with its own ..
    os.unlink(socket_dir.socket_path)

    other_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    other_socket.bind(socket_dir.socket_path)
    other_stat = os.stat(socket_dir.socket_path)

    # .. the server stops ..
    try:
        _ = stop_server(server)
        stat_after_stop = os.stat(socket_dir.socket_path)
    finally:
        other_socket.close()

    # .. and the socket file of the other process is still there.
    assert stat_after_stop.st_ino == other_stat.st_ino
    assert stat_after_stop.st_dev == other_stat.st_dev

# ################################################################################################################################
# ################################################################################################################################
