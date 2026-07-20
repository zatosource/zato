# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from llm_test_server import LLMTestServer

# How long to wait for the test-managed Redis to accept connections
_Redis_Wait_Timeout = 30
_Redis_Poll_Interval = 0.1

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Binds to an ephemeral port and returns its number.
    """

    # Open a TCP socket ..
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))

        # .. extract the assigned port ..
        address = tcp_socket.getsockname()
        out = address[1]

    return out

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_tcp_port(port:'int', timeout:'int'=_Redis_Wait_Timeout) -> 'None':
    """ Polls a TCP port until it accepts connections, or raises after timeout.
    """

    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=1):
                return
        except OSError:
            time.sleep(_Redis_Poll_Interval)

    raise Exception(f'Port {port} did not accept connections within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def llm_test_server() -> 'any_':
    """ A session-scoped live LLM provider simulator over plain HTTP.
    """
    server = LLMTestServer()
    server.start()

    yield server

    server.stop()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def clear_llm_test_server(llm_test_server:'any_') -> 'any_':
    """ Starts every test with no recorded requests and no per-path configuration.
    """
    llm_test_server.clear_requests()
    yield

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def redis_server() -> 'anydict':
    """ A session-scoped, test-managed Redis on its own port - started here and stopped when the session ends.
    """
    port = _find_free_port()

    process = subprocess.Popen(
        ['redis-server', '--port', str(port), '--save', '', '--appendonly', 'no'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    _wait_for_tcp_port(port)

    yield {'host': '127.0.0.1', 'port': port}

    process.terminate()
    _ = process.wait(timeout=5)

# ################################################################################################################################
# ################################################################################################################################
