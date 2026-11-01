# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A replicated pub/sub database of a test session - a PostgreSQL primary, a streaming standby built from a base backup
# of the primary, and a TCP proxy that the processes of the test connect through. A failover promotes the standby
# and repoints the proxy, the way a managed database service moves its endpoint to the promoted server.
#
# In the managed modes, the processes resolve the endpoint host name through the DNS server of the session, which
# points it at the proxy, and a failover points it at the standby instead, the way the DNS of Amazon RDS and of Azure
# moves the endpoint of a Multi-AZ or zone-redundant instance. The standby listens on the port of the proxy, so that
# the port of the endpoint stays the same.

# stdlib
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from urllib.request import urlopen

# Zato
from zato.common.test.pubsub_database import _find_free_port, _directory_mode, _shm_size, connect, get_container_address, \
     get_container_settings, get_runtime_dir, get_standby_container_name, get_standby_host, ModuleCtx, PubSubDBMode, \
     PubSubDatabase, start_pubsub_database, stop_pubsub_database
from zato.common.test.pubsub_profile import session_dns

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

# The address that the proxy listens on.
_proxy_host = '127.0.0.1'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ReplicatedDatabase:
    mode: 'str'
    is_sync: 'bool'
    primary: 'PubSubDatabase'
    standby_container: 'str' = ''
    standby_host: 'str' = 'localhost'
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
    """ Runs statements outside of a transaction on the primary, connecting to it directly as its superuser.
    """
    connection = connect(database.primary, is_admin=True)
    connection.autocommit = True
    cursor = connection.cursor()

    for statement in statements:
        cursor.execute(statement)

    connection.close()

# ################################################################################################################################

def _standby_conninfo(database:'ReplicatedDatabase') -> 'str':
    """ Returns how the standby connects to the primary - through the port the primary publishes on the host,
    or to the address of the primary on the network of the containers in the managed modes.
    """
    primary = database.primary

    if database.mode == PubSubDBMode.PostgreSQL:
        ssl_mode = 'disable'
    else:
        ssl_mode = 'require'

    if primary.profile_name:
        host = get_container_address(primary.container_name)
    else:
        host = '127.0.0.1'

    out = f'host={host} port={primary.port} user={primary.admin_username} password={primary.admin_password} ' + \
          f'application_name={_standby_name} sslmode={ssl_mode}'

    return out

# ################################################################################################################################

def _start_standby(database:'ReplicatedDatabase') -> 'None':
    """ Builds the standby from a base backup of the primary and starts it streaming from the primary.
    """
    primary = database.primary

    database.standby_container = get_standby_container_name(primary)
    database.standby_dir = os.path.join(primary.work_dir, 'standby')

    os.makedirs(database.standby_dir)
    os.chmod(database.standby_dir, 0o700)

    conninfo = _standby_conninfo(database)
    data_dir = '/var/lib/postgresql/data'

    replication_settings = [
        f'port={database.standby_port}',
        'hot_standby=on',
        f'primary_conninfo={conninfo}',
        f'primary_slot_name={_standby_name}',
    ]

    settings = get_container_settings(primary, replication_settings)

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
        '--user', f'{os.getuid()}:{os.getgid()}',
        '--shm-size', _shm_size,
        '-v', f'{database.standby_dir}:{data_dir}',
        '--entrypoint', 'bash',
    ]

    # The standby of the managed modes is an instance of its own on the network of the containers ..
    if primary.profile_name:
        database.standby_host = get_standby_host(primary)

    # .. whereas the standby of the other modes listens on the host.
    else:
        command.extend(['--network', 'host'])

    command.append(ModuleCtx.PostgreSQL_Image)
    command.extend(['-c', script])

    _ = subprocess.run(command, check=True, capture_output=True)

    if primary.profile_name:
        runtime_dir = get_runtime_dir()
        address = get_container_address(database.standby_container)
        session_dns.register(runtime_dir, database.standby_host, address)

# ################################################################################################################################

def _wait_until_streaming(database:'ReplicatedDatabase', expected_state:'str') -> 'None':
    """ Waits until the primary reports the standby as streaming in the expected synchronization state.
    """
    deadline = time.monotonic() + _ready_timeout

    while True:
        connection = connect(database.primary, is_admin=True)
        cursor = connection.cursor()
        cursor.execute('select state, sync_state from pg_stat_replication where application_name = %s', (_standby_name,))
        rows = cursor.fetchall()
        connection.close()

        for state, sync_state in rows:
            if state == 'streaming':
                if sync_state == expected_state:
                    return

        if time.monotonic() > deadline:
            raise Exception(f'Standby {database.standby_container} is not streaming, rows `{rows}`')

        time.sleep(_ready_poll_interval)

# ################################################################################################################################
# ################################################################################################################################

def _get_primary_address(database:'ReplicatedDatabase') -> 'str':
    """ Returns the address of the primary that the proxy forwards to.
    """
    primary = database.primary

    if primary.profile_name:
        out = get_container_address(primary.container_name)
    else:
        out = _proxy_host

    return out

# ################################################################################################################################

def _start_proxy(database:'ReplicatedDatabase') -> 'None':
    """ Starts the TCP proxy in a process of its own, pointed at the primary.
    """
    database.control_port = _find_free_port()
    database.proxy_log = os.path.join(database.primary.work_dir, 'proxy.log')

    upstream_host = _get_primary_address(database)

    command = [
        sys.executable, '-m', 'zato.common.test.tcp_proxy',
        '--listen-port', f'{database.proxy_port}',
        '--control-port', f'{database.control_port}',
        '--upstream-host', upstream_host,
        '--upstream-port', f'{database.primary.port}',
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
    primary_settings = _primary_settings()
    primary = start_pubsub_database(primary_label, mode, extra_settings=primary_settings)

    out = ReplicatedDatabase(mode=mode, is_sync=is_sync, primary=primary)

    # The standby of the managed modes listens on the port of the proxy, which the endpoint keeps after a failover ..
    out.proxy_port = _find_free_port()

    if primary.profile_name:
        out.standby_port = out.proxy_port
    else:
        out.standby_port = _find_free_port()

    # .. the init scripts ran when the primary was created, so replication connections are admitted from here on ..
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

    # .. and the processes of the test connect through the proxy, under the endpoint name in the managed modes.
    _start_proxy(out)

    out.env = dict(primary.env)
    out.env['Zato_PubSub_DB_Port'] = f'{out.proxy_port}'

    if primary.profile_name:
        runtime_dir = get_runtime_dir()
        session_dns.register(runtime_dir, primary.endpoint, _proxy_host)

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
    """ Starts the primary again and waits until it accepts connections. A primary of a managed mode may receive
    another address, which its host name and the proxy follow.
    """
    primary = database.primary

    _ = subprocess.run(['docker', 'start', primary.container_name], check=True, capture_output=True)

    if primary.profile_name:
        runtime_dir = get_runtime_dir()
        address = get_container_address(primary.container_name)
        session_dns.register(runtime_dir, primary.host, address)
        _ = proxy_command(database, f'upstream/{address}/{primary.port}')

    deadline = time.monotonic() + _ready_timeout

    while True:
        try:
            connection = connect(primary)
            connection.close()
            return
        except Exception:
            if time.monotonic() > deadline:
                raise
            time.sleep(_ready_poll_interval)

# ################################################################################################################################

def promote_standby(database:'ReplicatedDatabase') -> 'float':
    """ Promotes the standby, repoints the endpoint at it and returns how long the promotion took, in seconds.
    """
    primary = database.primary
    start = time.monotonic()

    connection = connect(primary, host=database.standby_host, port=database.standby_port, is_admin=True)
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute('select pg_promote(true, %s)', (_promote_timeout,))
    row:'any_' = cursor.fetchone()
    is_promoted = row[0]
    connection.close()

    if not is_promoted:
        raise Exception(f'Standby {database.standby_container} was not promoted')

    database.is_promoted = True

    # The endpoint name of a managed mode resolves to the standby from now on ..
    if primary.profile_name:
        runtime_dir = get_runtime_dir()
        address = get_container_address(database.standby_container)
        session_dns.register(runtime_dir, primary.endpoint, address)

    # .. whereas in the other modes, the proxy forwards to it.
    else:
        _ = proxy_command(database, f'upstream/{_proxy_host}/{database.standby_port}')

    out = time.monotonic() - start
    return out

# ################################################################################################################################

def connect_active(database:'ReplicatedDatabase') -> 'any_':
    """ Opens a pg8000 connection to whichever server is the primary now, bypassing the proxy.
    """
    primary = database.primary

    if database.is_promoted:
        host = database.standby_host
        port = database.standby_port
    else:
        host = primary.host
        port = primary.port

    out = connect(primary, host=host, port=port)
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
