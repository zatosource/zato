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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

# pytest
import pytest

# Zato
from certificates import generate_certificates
from live_sql.containers import start_postgresql, stop_container

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from certificates import CertificatePaths
    from live_sql.containers import DatabaseServer

    certificatesgen = Iterator[CertificatePaths]
    servergen = Iterator[DatabaseServer]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Host ports the containers listen on
    PostgreSQL_Port     = 25432
    PostgreSQL_SSL_Port = 25433

    # Names of the containers so stale ones can be removed
    PostgreSQL_Container     = 'zato-audit-log-test-postgresql'
    PostgreSQL_SSL_Container = 'zato-audit-log-test-postgresql-ssl'

    # Database credentials shared by both containers
    Username = 'zato_audit_log'
    Password = 'test-audit-log-password'
    DB_Name  = 'zato_audit_log'

# ################################################################################################################################
# ################################################################################################################################

# The database users inside the containers must be able to traverse into the certificate directory
_certificate_dir_mode = 0o755

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def certificate_paths() -> 'certificatesgen':
    """ Generates the throwaway CA along with server and client certificates once per session.
    The directory lives directly under the system temporary directory because the certificates
    are mounted into containers whose database users cannot traverse pytest's own 0700 directories.
    """
    directory = mkdtemp(prefix='zato-audit-log-certificates-')
    os.chmod(directory, _certificate_dir_mode)

    out = generate_certificates(directory)
    yield out

    rmtree(directory, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture(scope='session')
def postgresql_server() -> 'servergen':
    """ A plain PostgreSQL server started on demand in a container.
    """
    server = start_postgresql(
        container_name=ModuleCtx.PostgreSQL_Container,
        port=ModuleCtx.PostgreSQL_Port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Password,
        db_name=ModuleCtx.DB_Name,
        needs_ssl=False,
    )
    yield server

    stop_container(server.container_name)

# ################################################################################################################################

@pytest.fixture(scope='session')
def postgresql_ssl_server(certificate_paths:'CertificatePaths') -> 'servergen':
    """ A PostgreSQL server that requires TLS for all TCP connections.
    """
    server = start_postgresql(
        container_name=ModuleCtx.PostgreSQL_SSL_Container,
        port=ModuleCtx.PostgreSQL_SSL_Port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Password,
        db_name=ModuleCtx.DB_Name,
        needs_ssl=True,
        certificates=certificate_paths,
    )
    yield server

    stop_container(server.container_name)

# ################################################################################################################################
# ################################################################################################################################
