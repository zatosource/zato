# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from shutil import rmtree
from subprocess import DEVNULL, Popen
from tempfile import mkdtemp
from time import sleep, time

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

# pytest
import pytest

# Redis
from redis import Redis
from redis.exceptions import RedisError

# Zato
from live_sql.certificates import generate_certificates

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from live_sql.certificates import CertificatePaths
    from zato.common.typing_ import stranydict

    certificatesgen = Iterator[CertificatePaths]
    servergen = Iterator[stranydict]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The port the TLS-only server listens on - a non-default one so neither the plain
    # localhost server the plain tests use nor a Sentinel on its default port is ever affected
    TLS_Port = 26479

    # How long to wait for the TLS server to become ready, in seconds
    Ready_Timeout = 30

    # How long to sleep between readiness checks, in seconds
    Ready_Sleep = 0.1

    # How long each readiness check may take before it is abandoned, in seconds -
    # without it, a handshake against a port held by an unrelated process would hang forever
    Ready_Socket_Timeout = 2

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def certificate_paths() -> 'certificatesgen':
    """ Generates the throwaway CA along with server and client certificates once per session.
    """
    directory = mkdtemp(prefix='zato-redis-certificates-')

    out = generate_certificates(directory)
    yield out

    rmtree(directory, ignore_errors=True)

# ################################################################################################################################

def _wait_until_ready(details:'stranydict', process:'Popen') -> 'None':
    """ Polls the TLS server until it accepts encrypted connections, up to a timeout.
    """
    deadline = time() + ModuleCtx.Ready_Timeout

    while time() < deadline:

        # There is no point in waiting further if the server already exited,
        # e.g. because its port is taken or the certificates are unreadable.
        if process.poll() is not None:
            raise Exception(f'Redis TLS server exited with code {process.returncode}')

        conn = Redis(
            host=details['host'],
            port=details['port'],
            ssl=True,
            ssl_ca_certs=details['ssl_ca_file'],
            socket_connect_timeout=ModuleCtx.Ready_Socket_Timeout,
            socket_timeout=ModuleCtx.Ready_Socket_Timeout,
        )
        try:
            # A successful ping means the server is up and TLS works ..
            _ = conn.ping()
            conn.close()
            return
        except RedisError:
            # .. otherwise, the server is still starting up.
            conn.close()
            sleep(ModuleCtx.Ready_Sleep)

    raise Exception(f'Redis TLS server did not become ready within {ModuleCtx.Ready_Timeout}s')

# ################################################################################################################################

@pytest.fixture(scope='session')
def redis_tls_server(certificate_paths:'CertificatePaths') -> 'servergen':
    """ A local redis-server process that accepts TLS connections only -
    started directly as the current user, not in a container.
    """
    command = [
        'redis-server',
        '--port', '0',
        '--tls-port', str(ModuleCtx.TLS_Port),
        '--tls-cert-file', certificate_paths.server_cert,
        '--tls-key-file', certificate_paths.server_key,
        '--tls-ca-cert-file', certificate_paths.ca_cert,
        '--tls-auth-clients', 'no',
        '--save', '',
        '--appendonly', 'no',
    ]

    process = Popen(command, stdout=DEVNULL, stderr=DEVNULL)

    # The connection details the tests point the environment at
    details:'stranydict' = {
        'host': 'localhost',
        'port': ModuleCtx.TLS_Port,
        'db': 0,
        'ssl': True,
        'ssl_ca_file': certificate_paths.ca_cert,
        'ssl_verify': True,
    }

    _wait_until_ready(details, process)
    yield details

    process.terminate()
    _ = process.wait()

# ################################################################################################################################
# ################################################################################################################################
