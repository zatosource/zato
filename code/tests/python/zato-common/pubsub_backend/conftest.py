# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the sockets of the database drivers must be cooperative or concurrent
# greenlets serialize on them, so the patching runs before anything else is imported,
# exactly like in the servers whose runtime pattern this suite exercises
from gevent import monkey
_ = monkey.patch_all()

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
from live_sql.certificates import generate_certificates
from live_sql.containers import start_mysql, start_postgresql, stop_container

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from live_sql.certificates import CertificatePaths
    from live_sql.containers import DatabaseServer

    certificatesgen = Iterator[CertificatePaths]
    servergen = Iterator[DatabaseServer]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Host ports the containers listen on
    MySQL_Port          = 23326
    MySQL_SSL_Port      = 23327
    PostgreSQL_Port     = 25452
    PostgreSQL_SSL_Port = 25453

    # Names of the containers so stale ones can be removed
    MySQL_Container          = 'zato-pubsub-backend-test-mysql'
    MySQL_SSL_Container      = 'zato-pubsub-backend-test-mysql-ssl'
    PostgreSQL_Container     = 'zato-pubsub-backend-test-postgresql'
    PostgreSQL_SSL_Container = 'zato-pubsub-backend-test-postgresql-ssl'

    # Database credentials shared by all the containers
    Username = 'zato_pubsub'
    Password = 'test-pubsub-password'
    DB_Name  = 'zato_pubsub'

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
    directory = mkdtemp(prefix='zato-pubsub-backend-certificates-')
    os.chmod(directory, _certificate_dir_mode)

    out = generate_certificates(directory)
    yield out

    rmtree(directory, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture(scope='session')
def mysql_server() -> 'servergen':
    """ A plain MySQL server started on demand in a container.
    """
    server = start_mysql(
        container_name=ModuleCtx.MySQL_Container,
        port=ModuleCtx.MySQL_Port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Password,
        db_name=ModuleCtx.DB_Name,
        needs_ssl=False,
    )
    yield server

    stop_container(server.container_name)

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
def mysql_ssl_server(certificate_paths:'CertificatePaths') -> 'servergen':
    """ A MySQL server that requires TLS for all TCP connections.
    """
    server = start_mysql(
        container_name=ModuleCtx.MySQL_SSL_Container,
        port=ModuleCtx.MySQL_SSL_Port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Password,
        db_name=ModuleCtx.DB_Name,
        needs_ssl=True,
        certificates=certificate_paths,
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
