# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import ssl
import subprocess
from time import sleep, time
from typing import NamedTuple

# SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from certificates import CertificatePaths
    from zato.common.typing_ import optional, stranydict, strlist

    CertificatePaths = CertificatePaths
    certificatepathsnone = optional[CertificatePaths]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Docker images the databases run from
    MySQL_Image      = 'mysql:8.4'
    PostgreSQL_Image = 'postgres:16'

    # Host ports the containers listen on
    MySQL_Port          = 23306
    MySQL_SSL_Port      = 23307
    PostgreSQL_Port     = 25432
    PostgreSQL_SSL_Port = 25433

    # Names of the containers so stale ones can be removed
    MySQL_Container          = 'zato-audit-log-test-mysql'
    MySQL_SSL_Container      = 'zato-audit-log-test-mysql-ssl'
    PostgreSQL_Container     = 'zato-audit-log-test-postgresql'
    PostgreSQL_SSL_Container = 'zato-audit-log-test-postgresql-ssl'

    # Database credentials shared by all the containers
    Username = 'zato_audit_log'
    Password = 'test-audit-log-password'
    DB_Name  = 'zato_audit_log'

    # How long to wait for a database to accept connections
    Ready_Timeout = 300

    # How long to sleep between connection attempts
    Ready_Sleep = 1

# ################################################################################################################################
# ################################################################################################################################

class DatabaseServer(NamedTuple):
    container_name: str
    env: 'stranydict'

# ################################################################################################################################
# ################################################################################################################################

def _remove_stale_container(name:'str') -> 'None':
    """ Removes a container left over from a previous, possibly interrupted, run.
    """
    _ = subprocess.run(['docker', 'rm', '-f', name], capture_output=True, check=False)

# ################################################################################################################################

def stop_container(name:'str') -> 'None':
    """ Stops a container - it removes itself because it was started with --rm.
    """
    _ = subprocess.run(['docker', 'stop', name], capture_output=True, check=False)

# ################################################################################################################################

def _wait_until_ready(engine_url:'str', connect_args:'stranydict') -> 'None':
    """ Retries connecting until the database accepts connections or the timeout is reached.
    """
    deadline = time() + ModuleCtx.Ready_Timeout
    last_error = ''

    while time() < deadline:
        engine = create_engine(engine_url, connect_args=connect_args, poolclass=NullPool)
        try:
            with engine.connect() as connection:
                _ = connection.execute(text('select 1'))
            engine.dispose()
            return
        except Exception as e:
            last_error = str(e)
            engine.dispose()
            sleep(ModuleCtx.Ready_Sleep)

    raise Exception(f'Database at {engine_url} did not become ready, last error: {last_error}')

# ################################################################################################################################

def _get_ssl_connect_args(certificates:'CertificatePaths') -> 'stranydict':
    """ Builds the SSL context that readiness checks use with TLS-required databases.
    """
    ssl_context = ssl.create_default_context(cafile=certificates.ca_cert)

    out:'stranydict' = {'ssl': ssl_context}
    return out

# ################################################################################################################################

def _base_env(db_type:'str', port:'int') -> 'stranydict':
    """ Returns the Zato_Audit_Log_DB_* variables pointing at one of our containers.
    """
    out:'stranydict' = {
        AuditLogCtx.Env_Type:     db_type,
        AuditLogCtx.Env_Host:     'localhost',
        AuditLogCtx.Env_Port:     str(port),
        AuditLogCtx.Env_Username: ModuleCtx.Username,
        AuditLogCtx.Env_Password: ModuleCtx.Password,
        AuditLogCtx.Env_Name:     ModuleCtx.DB_Name,
    }

    return out

# ################################################################################################################################

def _ssl_env(certificates:'CertificatePaths') -> 'stranydict':
    """ Returns the Zato_Audit_Log_DB_SSL_* variables pointing at the generated certificates.
    """
    out:'stranydict' = {
        AuditLogCtx.Env_SSL:           'on',
        AuditLogCtx.Env_SSL_CA_File:   certificates.ca_cert,
        AuditLogCtx.Env_SSL_Cert_File: certificates.client_cert,
        AuditLogCtx.Env_SSL_Key_File:  certificates.client_key,
    }

    return out

# ################################################################################################################################

def start_mysql(*, needs_ssl:'bool', certificates:'certificatepathsnone' = None) -> 'DatabaseServer':
    """ Starts a MySQL container, optionally one that requires TLS for all TCP connections.
    Certificates are always given when needs_ssl is True and they are dereferenced only then.
    """
    ssl_certificates:'CertificatePaths' = cast_('CertificatePaths', certificates)

    if needs_ssl:
        container_name = ModuleCtx.MySQL_SSL_Container
        port = ModuleCtx.MySQL_SSL_Port
    else:
        container_name = ModuleCtx.MySQL_Container
        port = ModuleCtx.MySQL_Port

    _remove_stale_container(container_name)

    command:'strlist' = [
        'docker', 'run', '-d', '--rm',
        '--name', container_name,
        '-e', 'MYSQL_ROOT_PASSWORD=' + ModuleCtx.Password,
        '-e', 'MYSQL_DATABASE=' + ModuleCtx.DB_Name,
        '-e', 'MYSQL_USER=' + ModuleCtx.Username,
        '-e', 'MYSQL_PASSWORD=' + ModuleCtx.Password,
        '-p', f'{port}:3306',
    ]

    # The TLS-required variant mounts the certificates and refuses unencrypted TCP connections
    if needs_ssl:
        command.extend(['-v', f'{ssl_certificates.directory}:/certs-in:ro'])
        command.append(ModuleCtx.MySQL_Image)
        command.extend([
            '--ssl-ca=/certs-in/ca.crt',
            '--ssl-cert=/certs-in/server.crt',
            '--ssl-key=/certs-in/server.key',
            '--require-secure-transport=ON',
        ])
    else:
        command.append(ModuleCtx.MySQL_Image)

    _ = subprocess.run(command, check=True, capture_output=True)

    # Wait until the database accepts connections from the host
    engine_url = 'mysql+pymysql://{}:{}@localhost:{}/{}'.format(
        ModuleCtx.Username, ModuleCtx.Password, port, ModuleCtx.DB_Name)

    if needs_ssl:
        connect_args = _get_ssl_connect_args(ssl_certificates)
    else:
        connect_args = {}

    _wait_until_ready(engine_url, connect_args)

    env = _base_env(AuditLogCtx.Type_MySQL, port)

    if needs_ssl:
        env.update(_ssl_env(ssl_certificates))

    out = DatabaseServer(container_name=container_name, env=env)
    return out

# ################################################################################################################################

def start_postgresql(*, needs_ssl:'bool', certificates:'certificatepathsnone' = None) -> 'DatabaseServer':
    """ Starts a PostgreSQL container, optionally one that requires TLS for all TCP connections.
    Certificates are always given when needs_ssl is True and they are dereferenced only then.
    """
    ssl_certificates:'CertificatePaths' = cast_('CertificatePaths', certificates)

    if needs_ssl:
        container_name = ModuleCtx.PostgreSQL_SSL_Container
        port = ModuleCtx.PostgreSQL_SSL_Port
    else:
        container_name = ModuleCtx.PostgreSQL_Container
        port = ModuleCtx.PostgreSQL_Port

    _remove_stale_container(container_name)

    command:'strlist' = [
        'docker', 'run', '-d', '--rm',
        '--name', container_name,
        '-e', 'POSTGRES_USER=' + ModuleCtx.Username,
        '-e', 'POSTGRES_PASSWORD=' + ModuleCtx.Password,
        '-e', 'POSTGRES_DB=' + ModuleCtx.DB_Name,
        '-p', f'{port}:5432',
    ]

    # The TLS-required variant copies the certificates in through an init script
    # which also rewrites pg_hba.conf so only TLS connections are accepted over TCP.
    if needs_ssl:
        setup_script = os.path.join(ssl_certificates.directory, 'postgresql-ssl-setup.sh')
        _write_postgresql_setup_script(setup_script)

        command.extend(['-v', f'{ssl_certificates.directory}:/certs-in:ro'])
        command.extend(['-v', f'{setup_script}:/docker-entrypoint-initdb.d/postgresql-ssl-setup.sh:ro'])

    command.append(ModuleCtx.PostgreSQL_Image)

    _ = subprocess.run(command, check=True, capture_output=True)

    # Wait until the database accepts connections from the host
    engine_url = 'postgresql+pg8000://{}:{}@localhost:{}/{}'.format(
        ModuleCtx.Username, ModuleCtx.Password, port, ModuleCtx.DB_Name)

    if needs_ssl:
        connect_args = _get_ssl_connect_args(ssl_certificates)
    else:
        connect_args = {}

    _wait_until_ready(engine_url, connect_args)

    env = _base_env(AuditLogCtx.Type_PostgreSQL, port)

    if needs_ssl:
        env.update(_ssl_env(ssl_certificates))

    out = DatabaseServer(container_name=container_name, env=env)
    return out

# ################################################################################################################################

def _write_postgresql_setup_script(path:'str') -> 'None':
    """ Writes the init script that enables TLS inside the PostgreSQL container.
    The mounted certificates belong to the host user so they are copied and re-owned
    to the postgres user, whose init process runs this script.
    """
    script = '\n'.join([
        '#!/bin/bash',
        'set -e',
        'cp /certs-in/server.crt /certs-in/server.key /certs-in/ca.crt "$PGDATA"/',
        'chmod 600 "$PGDATA"/server.key',
        'cat >> "$PGDATA"/postgresql.conf <<CONF',
        'ssl = on',
        "ssl_cert_file = 'server.crt'",
        "ssl_key_file = 'server.key'",
        "ssl_ca_file = 'ca.crt'",
        'CONF',
        'sed -i "s/^host /hostssl /" "$PGDATA"/pg_hba.conf',
        '',
    ])

    with open(path, 'w') as file_:
        _ = file_.write(script)

    os.chmod(path, 0o755)

# ################################################################################################################################
# ################################################################################################################################
