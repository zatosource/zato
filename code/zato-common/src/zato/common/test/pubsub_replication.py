# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A replicated pub/sub database of a test session - a PostgreSQL primary, a streaming standby built from a base backup
# of the primary, and a TCP proxy that the processes of the test connect through. A failover promotes the standby
# and repoints the proxy, the way a managed database service moves its endpoint to the promoted server.

# stdlib
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from urllib.request import urlopen

# Zato
from zato.common.test.pubsub_database import _find_free_port, _directory_mode, _postgresql_diagnostics, \
     _postgresql_settings, _shm_size, connect, ModuleCtx, PubSubDBMode, PubSubDatabase, start_pubsub_database, \
     stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The name under which the standby connects to the primary, which synchronous replication waits for.
_standby_name = 'standby1'

# How long the standby may take to be built and to stream from the primary, in seconds, and how often it is checked.
_ready_timeout = 300
_ready_poll_interval = 0.5

# How long a promotion may take, in seconds.
_promote_timeout = 60

# How long the proxy may take to listen, in seconds.
_proxy_ready_timeout = 30

# How long a command of the proxy may take, in seconds.
_proxy_command_timeout = 10

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ReplicatedDatabase:
    mode: 'str'
    is_sync: 'bool'
    primary: 'PubSubDatabase'
    standby_container: 'str' = ''
    standby_port: 'int' = 0
    standby_dir: 'str' = ''
    proxy_port: 'int' = 0
    control_port: 'int' = 0
    proxy_process: 'any_' = None
    proxy_log: 'str' = ''
    is_promoted: 'bool' = False
    env: 'strstrdict' = field(default_factory=dict)

# ################################################################################################################################
# ################################################################################################################################

def _write_replication_script(path:'str', mode:'str') -> 'None':
    """ Writes the init script that admits replication connections, over TLS only in the TLS modes.
    """
    if mode == PubSubDBMode.PostgreSQL:
        line = 'host replication all all scram-sha-256'
    else:
        line = 'hostssl replication all all scram-sha-256'

    script = '\n'.join([
        '#!/bin/bash',
        'set -e',
        f'echo "{line}" >> "$PGDATA"/pg_hba.conf',
        '',
    ])

    with open(path, 'w') as script_file:
        _ = script_file.write(script)

    os.chmod(path, _directory_mode)

# ################################################################################################################################

def _primary_settings() -> 'strlist':
    """ Returns the replication settings of the primary. Synchronous replication is turned on only once the standby
    streams, because the initialization of the container commits before any standby exists.
    """
    out = [
        'wal_level=replica',
        'max_wal_senders=10',
        'max_replication_slots=10',
        'hot_standby=on',
    ]

    return out

# ################################################################################################################################

def _run_on_primary(database:'ReplicatedDatabase', statements:'strlist') -> 'None':
    """ Runs statements outside of a transaction on the primary, connecting to it directly.
    """
    connection = connect(database.primary)
    connection.autocommit = True
    cursor = connection.cursor()

    for statement in statements:
        cursor.execute(statement)

    connection.close()

# ################################################################################################################################

def _standby_conninfo(database:'ReplicatedDatabase') -> 'str':
    primary = database.primary

    if database.mode == PubSubDBMode.PostgreSQL:
        ssl_mode = 'disable'
    else:
        ssl_mode = 'require'

    out = f'host=127.0.0.1 port={primary.port} user={ModuleCtx.Username} password={primary.password} ' + \
          f'application_name={_standby_name} sslmode={ssl_mode}'

    return out

# ################################################################################################################################

def _start_standby(database:'ReplicatedDatabase') -> 'None':
    """ Builds the standby from a base backup of the primary and starts it streaming from the primary.
    """
    primary = database.primary

    database.standby_port = _find_free_port()
    database.standby_container = f'{primary.container_name}-standby'
    database.standby_dir = os.path.join(primary.work_dir, 'standby')

    os.makedirs(database.standby_dir)
    os.chmod(database.standby_dir, 0o700)

    conninfo = _standby_conninfo(database)
    data_dir = '/var/lib/postgresql/data'

    settings = _postgresql_settings + _postgresql_diagnostics + [
        f'port={database.standby_port}',
        'hot_standby=on',
        f'primary_conninfo={conninfo}',
        f'primary_slot_name={_standby_name}',
    ]

    postgres_command = ['postgres', '-D', data_dir]
    for setting in settings:
        postgres_command.append(f'-c "{setting}"')

    script = ' && '.join([
        f'pg_basebackup -d "{conninfo}" -D {data_dir} -X stream -C -S {_standby_name} -R',
        'exec ' + ' '.join(postgres_command),
    ])

    command:'strlist' = [
        'docker', 'run', '-d',
        '--name', database.standby_container,
        '--network', 'host',
        '--user', f'{os.getuid()}:{os.getgid()}',
        '--shm-size', _shm_size,
        '-v', f'{database.standby_dir}:{data_dir}',
        '--entrypoint', 'bash',
        ModuleCtx.PostgreSQL_Image,
        '-c', script,
    ]

    _ = subprocess.run(command, check=True, capture_output=True)

# ################################################################################################################################

def _wait_until_streaming(database:'ReplicatedDatabase', expected_state:'str') -> 'None':
    """ Waits until the primary reports the standby as streaming in the expected synchronization state.
    """
    deadline = time.monotonic() + _ready_timeout

    while True:
        connection = connect(database.primary)
        cursor = connection.cursor()
        cursor.execute('select state, sync_state from pg_stat_replication where application_name = %s', (_standby_name,))
        rows = cursor.fetchall()
        connection.close()

        for state, sync_state in rows:
            if state == 'streaming' and sync_state == expected_state:
                return

        if time.monotonic() > deadline:
            raise Exception(f'Standby {database.standby_container} is not streaming, rows `{rows}`')

        time.sleep(_ready_poll_interval)

# ################################################################################################################################
# ################################################################################################################################

def _start_proxy(database:'ReplicatedDatabase') -> 'None':
    """ Starts the TCP proxy in a process of its own, pointed at the primary.
    """
    database.proxy_port = _find_free_port()
    database.control_port = _find_free_port()
    database.proxy_log = os.path.join(database.primary.work_dir, 'proxy.log')

    command = [
        sys.executable, '-m', 'zato.common.test.tcp_proxy',
        '--listen-port', str(database.proxy_port),
        '--control-port', str(database.control_port),
        '--upstream-port', str(database.primary.port),
    ]

    with open(database.proxy_log, 'wb') as log_file:
        database.proxy_process = subprocess.Popen(command, stdout=log_file, stderr=subprocess.STDOUT)

    deadline = time.monotonic() + _proxy_ready_timeout

    while True:
        try:
            _ = proxy_command(database, 'release')
            return
        except OSError:
            if time.monotonic() > deadline:
                raise
            time.sleep(_ready_poll_interval)

# ################################################################################################################################

def proxy_command(database:'ReplicatedDatabase', command:'str') -> 'int':
    """ Sends one command to the control endpoint of the proxy and returns its numeric result.
    """
    with urlopen(f'http://127.0.0.1:{database.control_port}/{command}', timeout=_proxy_command_timeout) as response:
        out = int(response.read())

    return out

# ################################################################################################################################
# ################################################################################################################################

def start_replicated_database(label:'str', mode:'str', is_sync:'bool') -> 'ReplicatedDatabase':
    """ Starts a primary, a standby streaming from it and the proxy that the processes of the test connect through.
    """
    primary_label = f'{label}-primary'
    primary = start_pubsub_database(primary_label, mode, extra_settings=_primary_settings())

    out = ReplicatedDatabase(mode=mode, is_sync=is_sync, primary=primary)

    # The init scripts ran when the primary was created, so replication connections are admitted from here on ..
    script_path = os.path.join(primary.work_dir, 'replication-setup.sh')
    _write_replication_script(script_path, mode)
    _ = subprocess.run(['docker', 'cp', script_path, f'{primary.container_name}:/tmp/replication-setup.sh'],
        check=True, capture_output=True)
    _ = subprocess.run(['docker', 'exec', '-e', 'PGDATA=/var/lib/postgresql/data', primary.container_name,
        'bash', '/tmp/replication-setup.sh'], check=True, capture_output=True)

    _run_on_primary(out, ['select pg_reload_conf()'])

    # .. the standby is built from a base backup of the primary ..
    _start_standby(out)
    _wait_until_streaming(out, 'async')

    # .. in synchronous mode, a commit returns only once the standby has the WAL of the transaction ..
    if is_sync:
        _run_on_primary(out, [
            f"alter system set synchronous_standby_names = '{_standby_name}'",
            "alter system set synchronous_commit = 'on'",
            'select pg_reload_conf()',
        ])
        _wait_until_streaming(out, 'sync')

    # .. and the processes of the test connect through the proxy.
    _start_proxy(out)

    out.env = dict(primary.env)
    out.env['Zato_PubSub_DB_Port'] = str(out.proxy_port)

    return out

# ################################################################################################################################

def kill_primary(database:'ReplicatedDatabase') -> 'None':
    """ Ends the primary at once, the way a crash of its host would.
    """
    _ = subprocess.run(['docker', 'kill', database.primary.container_name], check=True, capture_output=True)

# ################################################################################################################################

def stop_primary(database:'ReplicatedDatabase') -> 'None':
    """ Shuts the primary down, the way a restart or a maintenance event of the database service does.
    """
    _ = subprocess.run(['docker', 'stop', database.primary.container_name], check=True, capture_output=True)

# ################################################################################################################################

def start_primary(database:'ReplicatedDatabase') -> 'None':
    """ Starts the primary again and waits until it accepts connections.
    """
    _ = subprocess.run(['docker', 'start', database.primary.container_name], check=True, capture_output=True)

    deadline = time.monotonic() + _ready_timeout

    while True:
        try:
            connection = connect(database.primary)
            connection.close()
            return
        except Exception:
            if time.monotonic() > deadline:
                raise
            time.sleep(_ready_poll_interval)

# ################################################################################################################################

def promote_standby(database:'ReplicatedDatabase') -> 'float':
    """ Promotes the standby, repoints the proxy at it and returns how long the promotion took, in seconds.
    """
    start = time.monotonic()

    connection = connect(database.primary, port=database.standby_port)
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute('select pg_promote(true, %s)', (_promote_timeout,))
    row:'any_' = cursor.fetchone()
    is_promoted = row[0]
    connection.close()

    if not is_promoted:
        raise Exception(f'Standby {database.standby_container} was not promoted')

    database.is_promoted = True
    _ = proxy_command(database, f'upstream/{database.standby_port}')

    out = time.monotonic() - start
    return out

# ################################################################################################################################

def connect_active(database:'ReplicatedDatabase') -> 'any_':
    """ Opens a pg8000 connection to whichever server is the primary now, bypassing the proxy.
    """
    if database.is_promoted:
        port = database.standby_port
    else:
        port = database.primary.port

    out = connect(database.primary, port=port)
    return out

# ################################################################################################################################

def stop_replicated_database(database:'ReplicatedDatabase') -> 'None':
    """ Stops the proxy and removes the standby, the primary and their data directories.
    """
    database.proxy_process.kill()
    _ = database.proxy_process.wait()

    _ = subprocess.run(['docker', 'rm', '-f', database.standby_container], capture_output=True, check=False)
    stop_pubsub_database(database.primary)

# ################################################################################################################################
# ################################################################################################################################
