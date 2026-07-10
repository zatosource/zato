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
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.certificates import CertificatePaths
    from zato.common.typing_ import optional, stranydict, strlist

    CertificatePaths = CertificatePaths
    certificatepathsnone = optional[CertificatePaths]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Docker images the databases run from
    MySQL_Image      = 'mysql:8.4'
    PostgreSQL_Image = 'postgres:16'

    # Database types the servers report in their connection details
    Type_MySQL      = 'mysql'
    Type_PostgreSQL = 'postgresql'

    # How long to wait for a database to accept connections
    Ready_Timeout = 300

    # How long to sleep between connection attempts
    Ready_Sleep = 1

# ################################################################################################################################
# ################################################################################################################################

class DatabaseServer(NamedTuple):
    container_name: str
    details: 'stranydict'

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

def _base_details(db_type:'str', port:'int', username:'str', password:'str', db_name:'str') -> 'stranydict':
    """ Returns the connection details pointing at one of our containers.
    """
    out:'stranydict' = {
        'type':     db_type,
        'host':     'localhost',
        'port':     str(port),
        'username': username,
        'password': password,
        'name':     db_name,
    }

    return out

# ################################################################################################################################

def _ssl_details(certificates:'CertificatePaths') -> 'stranydict':
    """ Returns the SSL connection details pointing at the generated certificates.
    """
    out:'stranydict' = {
        'ssl':           'on',
        'ssl_ca_file':   certificates.ca_cert,
        'ssl_cert_file': certificates.client_cert,
        'ssl_key_file':  certificates.client_key,
    }

    return out

# ################################################################################################################################

def start_mysql(
    *,
    container_name:'str',
    port:'int',
    username:'str',
    password:'str',
    db_name:'str',
    needs_ssl:'bool',
    certificates:'certificatepathsnone' = None,
    ) -> 'DatabaseServer':
    """ Starts a MySQL container, optionally one that requires TLS for all TCP connections.
    Certificates are always given when needs_ssl is True and they are dereferenced only then.
    """
    ssl_certificates:'CertificatePaths' = cast_('CertificatePaths', certificates)

    _remove_stale_container(container_name)

    command:'strlist' = [
        'docker', 'run', '-d', '--rm',
        '--name', container_name,
        '-e', 'MYSQL_ROOT_PASSWORD=' + password,
        '-e', 'MYSQL_DATABASE=' + db_name,
        '-e', 'MYSQL_USER=' + username,
        '-e', 'MYSQL_PASSWORD=' + password,
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
    engine_url = f'mysql+pymysql://{username}:{password}@localhost:{port}/{db_name}'

    if needs_ssl:
        connect_args = _get_ssl_connect_args(ssl_certificates)
    else:
        connect_args = {}

    _wait_until_ready(engine_url, connect_args)

    details = _base_details(ModuleCtx.Type_MySQL, port, username, password, db_name)

    if needs_ssl:
        details.update(_ssl_details(ssl_certificates))

    out = DatabaseServer(container_name=container_name, details=details)
    return out

# ################################################################################################################################

def start_postgresql(
    *,
    container_name:'str',
    port:'int',
    username:'str',
    password:'str',
    db_name:'str',
    needs_ssl:'bool',
    certificates:'certificatepathsnone' = None,
    ) -> 'DatabaseServer':
    """ Starts a PostgreSQL container, optionally one that requires TLS for all TCP connections.
    Certificates are always given when needs_ssl is True and they are dereferenced only then.
    """
    ssl_certificates:'CertificatePaths' = cast_('CertificatePaths', certificates)

    _remove_stale_container(container_name)

    command:'strlist' = [
        'docker', 'run', '-d', '--rm',
        '--name', container_name,
        '-e', 'POSTGRES_USER=' + username,
        '-e', 'POSTGRES_PASSWORD=' + password,
        '-e', 'POSTGRES_DB=' + db_name,
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
    engine_url = f'postgresql+pg8000://{username}:{password}@localhost:{port}/{db_name}'

    if needs_ssl:
        connect_args = _get_ssl_connect_args(ssl_certificates)
    else:
        connect_args = {}

    _wait_until_ready(engine_url, connect_args)

    details = _base_details(ModuleCtx.Type_PostgreSQL, port, username, password, db_name)

    if needs_ssl:
        details.update(_ssl_details(ssl_certificates))

    out = DatabaseServer(container_name=container_name, details=details)
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
