# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from shutil import rmtree
from tempfile import mkdtemp

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# pytest
import pytest

# Zato
from live_sql.certificates import generate_certificates
from es_server import start_es, stop_es

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from live_sql.certificates import CertificatePaths
    from es_server import ESServer

    certificatesgen = Iterator[CertificatePaths]
    servergen = Iterator[ESServer]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # HTTP ports the instances listen on
    ES_Port     = 9261
    ES_TLS_Port = 9262

    # The password of the built-in superuser in the TLS instance
    Password = 'test-es-password'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def certificate_paths() -> 'certificatesgen':
    """ Generates the throwaway CA along with server and client certificates once per session,
    plus a combined client pem for mutual TLS tests.
    """
    directory = mkdtemp(prefix='zato-es-certificates-')

    out = generate_certificates(directory)

    # The Elasticsearch client expects the client certificate and its key combined in one pem file
    client_pem = os.path.join(directory, 'client.pem')

    with open(out.client_key, 'rb') as key_file:
        key_data = key_file.read()

    with open(out.client_cert, 'rb') as cert_file:
        cert_data = cert_file.read()

    with open(client_pem, 'wb') as pem_file:
        _ = pem_file.write(key_data + cert_data)

    yield out

    rmtree(directory, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture(scope='session')
def es_server() -> 'servergen':
    """ A plain Elasticsearch instance with security disabled, started on demand.
    """
    server = start_es(
        port=ModuleCtx.ES_Port,
        needs_tls=False,
    )
    yield server

    stop_es(server)

# ################################################################################################################################

@pytest.fixture(scope='session')
def es_tls_server(certificate_paths:'CertificatePaths') -> 'servergen':
    """ An Elasticsearch instance that requires TLS and authentication for all connections.
    """
    server = start_es(
        port=ModuleCtx.ES_TLS_Port,
        needs_tls=True,
        certificates=certificate_paths,
        password=ModuleCtx.Password,
    )
    yield server

    stop_es(server)

# ################################################################################################################################
# ################################################################################################################################
