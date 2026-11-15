# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import time
from subprocess import DEVNULL, Popen

# pytest
import pytest

# Redis
from redis import Redis
from redis.exceptions import RedisError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import generator_

    Path = Path
    redisgen = generator_[Redis, None, None]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Host = '127.0.0.1'

    # How long a started Redis server has to accept connections, in seconds
    Ready_Timeout = 30.0

    # How long to wait between two checks of a starting Redis server, in seconds
    Ready_Sleep = 0.05

# ################################################################################################################################
# ################################################################################################################################

def _get_free_port() -> 'int':
    """ Returns a TCP port that no process listens on at the time of the call.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((ModuleCtx.Host, 0))
        out = sock.getsockname()[1]

    return out

# ################################################################################################################################

def _wait_until_ready(conn:'Redis', process:'Popen') -> 'None':
    """ Polls a starting Redis server until it answers a ping, up to a timeout.
    """
    deadline = time.monotonic() + ModuleCtx.Ready_Timeout

    while time.monotonic() < deadline:

        # A server that exited, for instance because its port was taken in the meantime, is not waited for ..
        if process.poll() is not None:
            raise Exception(f'Redis server exited with code {process.returncode}')

        # .. a server that answers is ready ..
        try:
            _ = conn.ping()
            return

        # .. and any other one is still starting.
        except RedisError:
            time.sleep(ModuleCtx.Ready_Sleep)

    raise Exception(f'Redis server did not become ready within {ModuleCtx.Ready_Timeout}s')

# ################################################################################################################################

@pytest.fixture
def redis_conn(tmp_path:'Path') -> 'redisgen':
    """ A connection to a Redis server of the test's own, on a free port, without persistence.
    """
    port = _get_free_port()

    command = [
        'redis-server',
        '--bind', ModuleCtx.Host,
        '--port', str(port),
        '--save', '',
        '--appendonly', 'no',
        '--dir', str(tmp_path),
    ]

    process = Popen(command, stdout=DEVNULL, stderr=DEVNULL)
    conn = Redis(host=ModuleCtx.Host, port=port, decode_responses=True)

    _wait_until_ready(conn, process)
    yield conn

    conn.close()
    process.terminate()
    _ = process.wait()

# ################################################################################################################################
# ################################################################################################################################
