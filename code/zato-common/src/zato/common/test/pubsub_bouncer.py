# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# PgBouncer in transaction mode in front of the pub/sub database of a managed mode, the way Azure Database
# for PostgreSQL offers it on port 6432 and the way a connection pooler is placed in front of Amazon RDS.
# Each transaction of a client may run on another server connection, and the prepared statements of the clients
# are tracked by PgBouncer, which prepares them again on whichever server connection a transaction runs on.

# stdlib
import os
import subprocess

# ################################################################################################################################
# ################################################################################################################################

# The image of the PgBouncer containers.
_bouncer_image = 'zato-pubsub-test-bouncer:1'
_bouncer_dockerfile = 'FROM alpine:latest\nRUN apk add --no-cache pgbouncer\n'

# The port that PgBouncer listens on.
Bouncer_Port = 6432

# The defaults of the built-in PgBouncer of Azure, and the prepared statements that each server connection keeps.
_default_pool_size = 50
_max_client_conn = 5000
_max_prepared_statements = 200

# Where the configuration and the certificates are in the container.
_config_dir = '/bouncer'
_certs_dir = '/certs'

# ################################################################################################################################
# ################################################################################################################################

def _ensure_image() -> 'None':
    """ Builds the image of PgBouncer unless it exists already.
    """
    result = subprocess.run(['docker', 'image', 'inspect', _bouncer_image], capture_output=True, check=False)

    if result.returncode != 0:
        dockerfile = _bouncer_dockerfile.encode('utf8')
        _ = subprocess.run(['docker', 'build', '-t', _bouncer_image, '-'], input=dockerfile, capture_output=True, check=True)

# ################################################################################################################################

def _write_config(config_dir:'str', address:'str', port:'int', db_name:'str', username:'str', password:'str') -> 'None':
    """ Writes the configuration of PgBouncer and the credentials that it accepts and uses for the server connections.
    """
    config = '\n'.join([
        '[databases]',
        f'{db_name} = host={address} port={port} dbname={db_name}',
        '',
        '[pgbouncer]',
        'listen_addr = 0.0.0.0',
        f'listen_port = {Bouncer_Port}',
        'unix_socket_dir =',
        'auth_type = scram-sha-256',
        f'auth_file = {_config_dir}/userlist.txt',
        'pool_mode = transaction',
        f'default_pool_size = {_default_pool_size}',
        f'max_client_conn = {_max_client_conn}',
        f'max_prepared_statements = {_max_prepared_statements}',
        'ignore_startup_parameters = extra_float_digits',
        'client_tls_sslmode = require',
        f'client_tls_cert_file = {_certs_dir}/server.crt',
        f'client_tls_key_file = {_certs_dir}/server.key',
        'server_tls_sslmode = verify-ca',
        f'server_tls_ca_file = {_certs_dir}/ca.crt',
        '',
    ])

    config_path = os.path.join(config_dir, 'pgbouncer.ini')
    userlist_path = os.path.join(config_dir, 'userlist.txt')

    with open(config_path, 'w') as config_file:
        _ = config_file.write(config)

    with open(userlist_path, 'w') as userlist_file:
        _ = userlist_file.write(f'"{username}" "{password}"\n')

# ################################################################################################################################

def start_bouncer(container_name:'str', work_dir:'str', certs_dir:'str', address:'str', port:'int', db_name:'str',
    username:'str', password:'str') -> 'None':
    """ Starts PgBouncer in a container of its own, in front of the database at the given address.
    """
    _ensure_image()

    config_dir = os.path.join(work_dir, 'bouncer')
    os.makedirs(config_dir, exist_ok=True)

    _write_config(config_dir, address, port, db_name, username, password)

    config_path = f'{_config_dir}/pgbouncer.ini'

    command = [
        'docker', 'run', '-d',
        '--name', container_name,
        '--user', f'{os.getuid()}:{os.getgid()}',
        '-v', f'{config_dir}:{_config_dir}:ro',
        '-v', f'{certs_dir}:{_certs_dir}:ro',
        '--entrypoint', 'pgbouncer',
        _bouncer_image,
        config_path,
    ]

    _ = subprocess.run(command, check=True, capture_output=True)

# ################################################################################################################################
# ################################################################################################################################
