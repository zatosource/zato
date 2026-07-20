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
from certificates import generate_certificates
from containers import start_mongodb, stop_container

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from certificates import CertificatePaths
    from containers import MongoDBServer

    certificatesgen = Iterator[CertificatePaths]
    servergen = Iterator[MongoDBServer]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Host ports the containers listen on
    MongoDB_Port     = 27117
    MongoDB_TLS_Port = 27118

    # Names of the containers so stale ones can be removed
    MongoDB_Container     = 'zato-test-mongodb'
    MongoDB_TLS_Container = 'zato-test-mongodb-tls'

    # Credentials shared by all the containers
    Username = 'zato_mongodb'
    Password = 'test-mongodb-password'

# ################################################################################################################################
# ################################################################################################################################

# The database user inside the container must be able to traverse into the certificate directory
_certificate_dir_mode = 0o755

# The combined pem files are mounted into the container whose user needs to read them
_certificate_file_mode = 0o644

# ################################################################################################################################
# ################################################################################################################################

def _write_combined_pem(path:'str', key_path:'str', cert_path:'str') -> 'None':
    """ Writes one pem file combining a private key and its certificate, as pymongo 4 and mongod expect.
    """
    with open(key_path, 'rb') as key_file:
        key_data = key_file.read()

    with open(cert_path, 'rb') as cert_file:
        cert_data = cert_file.read()

    with open(path, 'wb') as pem_file:
        _ = pem_file.write(key_data + cert_data)

    os.chmod(path, _certificate_file_mode)

# ################################################################################################################################

@pytest.fixture(scope='session')
def certificate_paths() -> 'certificatesgen':
    """ Generates the throwaway CA along with server and client certificates once per session,
    plus the combined server and client pem files that MongoDB and pymongo expect.
    The directory lives directly under the system temporary directory because the certificates
    are mounted into a container whose user cannot traverse pytest's own 0700 directories.
    """
    directory = mkdtemp(prefix='zato-mongodb-certificates-')
    os.chmod(directory, _certificate_dir_mode)

    out = generate_certificates(directory)

    # MongoDB and pymongo both expect the private key and the certificate combined in one pem file
    server_pem = os.path.join(directory, 'server.pem')
    client_pem = os.path.join(directory, 'client.pem')

    _write_combined_pem(server_pem, out.server_key, out.server_cert)
    _write_combined_pem(client_pem, out.client_key, out.client_cert)

    yield out

    rmtree(directory, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture(scope='session')
def mongodb_server() -> 'servergen':
    """ A plain MongoDB server started on demand in a container.
    """
    server = start_mongodb(
        container_name=ModuleCtx.MongoDB_Container,
        port=ModuleCtx.MongoDB_Port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Password,
        needs_tls=False,
    )
    yield server

    stop_container(server.container_name)

# ################################################################################################################################

@pytest.fixture(scope='session')
def mongodb_tls_server(certificate_paths:'CertificatePaths') -> 'servergen':
    """ A MongoDB server that requires TLS for all connections.
    """
    server = start_mongodb(
        container_name=ModuleCtx.MongoDB_TLS_Container,
        port=ModuleCtx.MongoDB_TLS_Port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Password,
        needs_tls=True,
        certificates=certificate_paths,
    )
    yield server

    stop_container(server.container_name)

# ################################################################################################################################
# ################################################################################################################################
