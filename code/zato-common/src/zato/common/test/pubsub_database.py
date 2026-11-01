# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The pub/sub database of a test session - the SQLite file of its environment, or a PostgreSQL container started
# for the session, with or without TLS, whose data directory is under the runtime directory of the tests.
# The managed modes run the container under the profile of Amazon RDS or of Azure Database for PostgreSQL.

# stdlib
import os
import shutil
import socket
import ssl
import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass, field

# pg8000
import pg8000.dbapi

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.pubsub_bouncer import Bouncer_Port, start_bouncer
from zato.common.test.pubsub_certs import Chain_Plain, generate_certificates
from zato.common.test.pubsub_network import add_round_trip_time
from zato.common.test.pubsub_profile import get_host_name, get_profile_settings, Instance_Port, Managed_Profiles, \
     session_dns, write_roles_script

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import anydict, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class PubSubDBMode:
    SQLite           = 'sqlite'
    PostgreSQL       = 'postgresql'
    PostgreSQL_TLS   = 'postgresql-tls'
    PostgreSQL_MTLS  = 'postgresql-mtls'
    PostgreSQL_RDS   = 'postgresql-rds'
    PostgreSQL_Azure = 'postgresql-azure'

# The managed modes and the names of their profiles.
_managed_modes = {
    PubSubDBMode.PostgreSQL_RDS: 'rds',
    PubSubDBMode.PostgreSQL_Azure: 'azure',
}

# The modes with a PostgreSQL container and those of them that require TLS.
_postgresql_modes = {
    PubSubDBMode.PostgreSQL,
    PubSubDBMode.PostgreSQL_TLS,
    PubSubDBMode.PostgreSQL_MTLS,
    PubSubDBMode.PostgreSQL_RDS,
    PubSubDBMode.PostgreSQL_Azure,
}

_tls_modes = {
    PubSubDBMode.PostgreSQL_TLS,
    PubSubDBMode.PostgreSQL_MTLS,
    PubSubDBMode.PostgreSQL_RDS,
    PubSubDBMode.PostgreSQL_Azure,
}

class ModuleCtx:

    # The environment variable selecting the pub/sub database of a test session
    Env_Mode = 'Zato_Test_PubSub_DB_Mode'

    # The environment variable naming the directory under which the runtime data of the tests is kept
    Env_Runtime_Dir = 'Zato_Test_Runtime_Dir'

    # Where the runtime data is kept unless the environment says otherwise
    Default_Runtime_Dir = '/tmp/zato-pubsub-test'

    # The image of the PostgreSQL containers
    PostgreSQL_Image = 'postgres:16'

    # The credentials and the database of the containers
    Username = 'zato_pubsub'
    DB_Name  = 'zato_pubsub'

    # The superuser of the containers of the managed modes, which stands for the internal superuser of the service
    # and which the tests use for the operations of the service itself, such as replication and promotion
    Service_Username = 'zato_service'

    # The prefix of the containers, which lets a session remove those that an interrupted session left behind
    Container_Prefix = 'zato-pubsub-test-'

    # The environment variables that put PgBouncer in front of the database of a managed mode
    # and that add a round-trip time to the network of a container, in milliseconds
    Env_Bouncer = 'Zato_Test_PubSub_DB_Bouncer'
    Env_Round_Trip_Ms = 'Zato_Test_PubSub_DB_Round_Trip_Ms'

# How long a container may take to accept connections, in seconds, and how often it is checked.
_ready_timeout = 120
_ready_poll_interval = 0.5

# The directories that the database server in the container reads, which runs under the same user as the tests.
_directory_mode = 0o755

# How many characters of a random value make the name of a container of a managed mode unique.
_name_suffix_length = 8

# The settings of the PostgreSQL containers. The WAL is sized for the write volume of pub/sub and compressed,
# backends hand their writes to the kernel every 256 kB, a vacuum reuses a buffer of its ring only after the WAL
# of its page is flushed, and autovacuum is sized for tables in which every row is inserted, updated and deleted.
_postgresql_settings = [
    'max_connections=300',
    'shared_buffers=2GB',
    'wal_buffers=64MB',
    'max_wal_size=16GB',
    'min_wal_size=4GB',
    'wal_compression=lz4',
    'checkpoint_timeout=15min',
    'checkpoint_completion_target=0.9',
    'backend_flush_after=256kB',
    'vacuum_buffer_usage_limit=256MB',
    'autovacuum_max_workers=6',
    'autovacuum_naptime=10s',
    'autovacuum_vacuum_cost_limit=4000',
    'autovacuum_vacuum_cost_delay=1ms',
    'shared_preload_libraries=pg_stat_statements',
    'pg_stat_statements.track=all',
]

# The diagnostics of the containers, which change nothing in how the database writes or commits.
_postgresql_diagnostics = [
    "log_line_prefix=%m [%p] %b %a ",
    'log_checkpoints=on',
    'log_autovacuum_min_duration=0',
    'log_lock_waits=on',
    'log_temp_files=0',
    'log_min_duration_statement=200',
    'log_parameter_max_length=0',
    'track_io_timing=on',
    'track_wal_io_timing=on',
]

# The shared memory of a container, which parallel queries allocate their segments in.
_shm_size = '1g'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class PubSubDatabase:
    mode: 'str'
    container_name: 'str' = ''
    host: 'str' = 'localhost'
    port: 'int' = 0
    password: 'str' = ''
    admin_username: 'str' = ''
    admin_password: 'str' = ''
    endpoint: 'str' = ''
    profile_name: 'str' = ''
    work_dir: 'str' = ''
    certs_dir: 'str' = ''
    bouncer_container: 'str' = ''
    docker_args: 'strlist' = field(default_factory=list)
    settings: 'strlist' = field(default_factory=list)
    env: 'strstrdict' = field(default_factory=dict)

# ################################################################################################################################
# ################################################################################################################################

def get_db_mode() -> 'str':
    """ Returns the pub/sub database mode of this test session.
    """
    if mode := os.environ.get(ModuleCtx.Env_Mode, ''):
        out = mode
    else:
        out = PubSubDBMode.SQLite

    return out

# ################################################################################################################################

def is_postgresql_mode(mode:'str') -> 'bool':
    out = mode in _postgresql_modes
    return out

# ################################################################################################################################

def is_managed_mode(mode:'str') -> 'bool':
    out = mode in _managed_modes
    return out

# ################################################################################################################################

def get_suite_modes(default_modes:'strlist') -> 'strlist':
    """ Returns the modes that a suite covering several PostgreSQL modes runs in - only the managed mode
    of the session if it selects one, and the default modes of the suite otherwise.
    """
    mode = get_db_mode()

    if is_managed_mode(mode):
        out = [mode]
    else:
        out = default_modes

    return out

# ################################################################################################################################

def get_runtime_dir() -> 'str':
    """ Returns the directory under which the runtime data of the tests is kept, creating it if needed.
    """
    if runtime_dir := os.environ.get(ModuleCtx.Env_Runtime_Dir, ''):
        out = runtime_dir
    else:
        out = ModuleCtx.Default_Runtime_Dir

    os.makedirs(out, exist_ok=True)

    return out

# ################################################################################################################################

def _find_free_port() -> 'int':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))
        out = tcp_socket.getsockname()[1]

    return out

# ################################################################################################################################

def get_container_address(container_name:'str') -> 'str':
    """ Returns the IP address of a container on its network.
    """
    command = ['docker', 'inspect', '-f', '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}', container_name]
    result = subprocess.run(command, check=True, capture_output=True, text=True)

    out = result.stdout.strip()
    return out

# ################################################################################################################################

def get_database_address(database:'PubSubDatabase') -> 'str':
    """ Returns the address that a proxy on the host forwards to - the container of a managed mode,
    or the port that the container of any other mode publishes on the host.
    """
    if database.profile_name:
        out = get_container_address(database.container_name)
    else:
        out = '127.0.0.1'

    return out

# ################################################################################################################################

def _write_tls_setup_script(path:'str', needs_client_cert:'bool') -> 'None':
    """ Writes the init script that turns TLS on inside the container and accepts TCP connections over TLS only,
    with a client certificate verified against the CA when the mode requires one.
    """
    if needs_client_cert:
        auth_options = 'scram-sha-256 clientcert=verify-full'
    else:
        auth_options = 'scram-sha-256'

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
        'sed -i "/^host /d" "$PGDATA"/pg_hba.conf',
        f'echo "hostssl all all all {auth_options}" >> "$PGDATA"/pg_hba.conf',
        '',
    ])

    with open(path, 'w') as script_file:
        _ = script_file.write(script)

    os.chmod(path, _directory_mode)

# ################################################################################################################################
# ################################################################################################################################

def build_ssl_context(database:'PubSubDatabase') -> 'ssl.SSLContext':
    """ Builds the client TLS context of a database the way the engine of Zato builds it from the environment.
    """
    env = database.env

    out = ssl.create_default_context(cafile=env['Zato_PubSub_DB_SSL_CA_File'])

    if cert_file := env.get('Zato_PubSub_DB_SSL_Cert_File'):
        out.load_cert_chain(cert_file, env['Zato_PubSub_DB_SSL_Key_File'])

    return out

# ################################################################################################################################

def connect(database:'PubSubDatabase', host:'str'='', port:'int'=0, is_admin:'bool'=False) -> 'pg8000.dbapi.Connection':
    """ Opens a pg8000 connection to the database of a session, outside of any engine, under the pub/sub role
    or under the superuser of the container.
    """
    if not host:
        host = database.host

    if not port:
        port = database.port

    if database.mode in _tls_modes:
        ssl_context = build_ssl_context(database)
    else:
        ssl_context = False

    if is_admin:
        username = database.admin_username
        password = database.admin_password
    else:
        username = ModuleCtx.Username
        password = database.password

    out = pg8000.dbapi.connect(user=username, password=password, host=host, port=port, database=ModuleCtx.DB_Name,
        ssl_context=ssl_context, timeout=10)

    return out

# ################################################################################################################################

def _wait_until_ready(database:'PubSubDatabase') -> 'None':
    """ Waits until the database of a container accepts connections from the host.
    """
    deadline = time.monotonic() + _ready_timeout

    while True:
        try:
            connection = connect(database)
            connection.close()
            return
        except Exception:
            if time.monotonic() > deadline:
                raise
            time.sleep(_ready_poll_interval)

# ################################################################################################################################

def remove_stale_containers() -> 'None':
    """ Removes the containers that interrupted sessions left behind.
    """
    result = subprocess.run(['docker', 'ps', '-aq', '--filter', f'name={ModuleCtx.Container_Prefix}'],
        capture_output=True, text=True, check=True)

    container_ids = result.stdout.split()

    if container_ids:
        _ = subprocess.run(['docker', 'rm', '-f', *container_ids], capture_output=True, check=False)

# ################################################################################################################################
# ################################################################################################################################

def _prepare_database(database:'PubSubDatabase', label:'str') -> 'None':
    """ Gives a new database its credentials, its address and the name of its container.
    """
    database.password = 'pubsub.' + CryptoManager.generate_hex_string()

    # A managed mode has an instance host name and an endpoint host name, and its instance listens on the usual port ..
    if profile_name := _managed_modes.get(database.mode):
        profile = Managed_Profiles[profile_name]

        suffix = CryptoManager.generate_hex_string()
        suffix = suffix[:_name_suffix_length]

        database.profile_name = profile_name
        database.port = Instance_Port
        database.container_name = f'{ModuleCtx.Container_Prefix}{label}-{suffix}'
        database.host = get_host_name(profile, database.container_name)
        database.endpoint = get_host_name(profile, f'{label}-{suffix}-endpoint')
        database.admin_username = ModuleCtx.Service_Username
        database.admin_password = 'service.' + CryptoManager.generate_hex_string()

    # .. while the other modes publish their port on the host and connect under the superuser of the container.
    else:
        database.port = _find_free_port()
        database.container_name = f'{ModuleCtx.Container_Prefix}{label}-{database.port}'
        database.admin_username = ModuleCtx.Username
        database.admin_password = database.password

# ################################################################################################################################

def get_standby_container_name(database:'PubSubDatabase') -> 'str':
    out = f'{database.container_name}-standby'
    return out

# ################################################################################################################################

def get_standby_host(database:'PubSubDatabase') -> 'str':
    """ Returns the host name of the standby of a database of a managed mode.
    """
    profile = Managed_Profiles[database.profile_name]
    standby_container_name = get_standby_container_name(database)

    out = get_host_name(profile, standby_container_name)
    return out

# ################################################################################################################################

def _get_host_names(database:'PubSubDatabase') -> 'strlist':
    """ Returns the names that the server certificate of a database is valid for.
    """
    out = ['localhost', '127.0.0.1', database.container_name]

    if database.profile_name:
        standby_host = get_standby_host(database)
        out.extend([database.host, database.endpoint, standby_host])

    return out

# ################################################################################################################################

def get_container_settings(database:'PubSubDatabase', extra_settings:'strlist | None') -> 'strlist':
    """ Returns the settings of a container, restricted to those that the service of a managed mode allows to change.
    """
    out = _postgresql_settings + _postgresql_diagnostics

    if extra_settings:
        out = out + extra_settings

    if database.profile_name:
        profile = Managed_Profiles[database.profile_name]
        out = get_profile_settings(profile, out)

    return out

# ################################################################################################################################

def _register_names(database:'PubSubDatabase') -> 'None':
    """ Makes the instance host name and the endpoint host name of a managed mode resolve to the container.
    """
    runtime_dir = get_runtime_dir()
    address = get_container_address(database.container_name)

    session_dns.register(runtime_dir, database.host, address)
    session_dns.register(runtime_dir, database.endpoint, address)
    session_dns.check_resolution(database.endpoint, address)

# ################################################################################################################################

def start_pubsub_database(label:'str', mode:'str', extra_settings:'strlist | None'=None,
    extra_docker_args:'strlist | None'=None) -> 'PubSubDatabase':
    """ Starts the pub/sub database of a session in the given mode. SQLite needs nothing started.
    """
    out = PubSubDatabase(mode=mode)

    if not is_postgresql_mode(mode):
        return out

    _prepare_database(out, label)

    # The data directory and the certificates are under the runtime directory of the tests ..
    runtime_dir = get_runtime_dir()
    out.work_dir = os.path.join(runtime_dir, out.container_name)
    shutil.rmtree(out.work_dir, ignore_errors=True)

    data_dir = os.path.join(out.work_dir, 'data')
    certs_dir = os.path.join(out.work_dir, 'certs')

    os.makedirs(data_dir)
    os.makedirs(certs_dir)
    os.chmod(out.work_dir, _directory_mode)
    os.chmod(certs_dir, _directory_mode)

    command:'strlist' = [
        'docker', 'run', '-d',
        '--name', out.container_name,
        '--user', f'{os.getuid()}:{os.getgid()}',
        '--shm-size', _shm_size,
        '-v', f'{data_dir}:/var/lib/postgresql/data',
    ]

    # .. a managed mode creates the pub/sub role and its database under the superuser of the container ..
    if out.profile_name:
        profile = Managed_Profiles[out.profile_name]
        chain = profile.chain

        roles_script = os.path.join(certs_dir, 'roles.sql')
        write_roles_script(roles_script, profile, ModuleCtx.Username, out.password, ModuleCtx.DB_Name)

        command.extend(['-e', 'POSTGRES_USER=' + ModuleCtx.Service_Username])
        command.extend(['-e', 'POSTGRES_PASSWORD=' + out.admin_password])
        command.extend(['-v', f'{roles_script}:/docker-entrypoint-initdb.d/0-roles.sql:ro'])

    # .. whereas the other modes create both as the superuser and publish the port on the host ..
    else:
        chain = Chain_Plain

        command.extend(['-e', 'POSTGRES_USER=' + ModuleCtx.Username])
        command.extend(['-e', 'POSTGRES_PASSWORD=' + out.password])
        command.extend(['-e', 'POSTGRES_DB=' + ModuleCtx.DB_Name])
        command.extend(['-p', f'{out.port}:5432'])

    # .. the TLS modes accept TCP connections over TLS only ..
    if mode in _tls_modes:
        host_names = _get_host_names(out)
        generate_certificates(certs_dir, host_names, ModuleCtx.Username, chain)

        setup_script = os.path.join(certs_dir, 'tls-setup.sh')
        needs_client_cert = mode == PubSubDBMode.PostgreSQL_MTLS
        _write_tls_setup_script(setup_script, needs_client_cert)

        command.extend(['-v', f'{certs_dir}:/certs-in:ro'])
        command.extend(['-v', f'{setup_script}:/docker-entrypoint-initdb.d/tls-setup.sh:ro'])

    if extra_docker_args:
        command.extend(extra_docker_args)

    out.docker_args = command
    out.settings = get_container_settings(out, extra_settings)
    out.certs_dir = certs_dir

    _run_container(out, ModuleCtx.PostgreSQL_Image)

    # .. the host names of a managed mode resolve to the container ..
    if out.profile_name:
        _register_names(out)
        host = out.endpoint
    else:
        host = 'localhost'

    # .. the environment of the server and of the test process point at the container ..
    out.env = {
        'Zato_PubSub_DB_Type': 'postgresql',
        'Zato_PubSub_DB_Host': host,
        'Zato_PubSub_DB_Port': f'{out.port}',
        'Zato_PubSub_DB_Username': ModuleCtx.Username,
        'Zato_PubSub_DB_Password': out.password,
        'Zato_PubSub_DB_Name': ModuleCtx.DB_Name,
    }

    if mode in _tls_modes:
        out.env['Zato_PubSub_DB_SSL'] = 'true'
        out.env['Zato_PubSub_DB_SSL_CA_File'] = os.path.join(certs_dir, 'ca.crt')

    if mode == PubSubDBMode.PostgreSQL_MTLS:
        out.env['Zato_PubSub_DB_SSL_Cert_File'] = os.path.join(certs_dir, 'client.crt')
        out.env['Zato_PubSub_DB_SSL_Key_File'] = os.path.join(certs_dir, 'client.key')

    if out.profile_name:
        dns_env = session_dns.get_env()
        out.env.update(dns_env)

    # .. the container is ready once it accepts them ..
    _wait_until_ready(out)

    # .. and the session may add the round-trip time of a network and, in a managed mode, PgBouncer.
    _add_network(out)

    if out.profile_name:
        if os.environ.get(ModuleCtx.Env_Bouncer, ''):
            _start_bouncer(out)
            out.env['Zato_PubSub_DB_Port'] = f'{Bouncer_Port}'

    return out

# ################################################################################################################################

def _run_container(database:'PubSubDatabase', image:'str') -> 'None':
    """ Runs the container of a database from an image, with its arguments and its settings.
    """
    command = list(database.docker_args)
    command.append(image)
    command.append('postgres')

    for setting in database.settings:
        command.extend(['-c', setting])

    _ = subprocess.run(command, check=True, capture_output=True)

# ################################################################################################################################

def _add_network(database:'PubSubDatabase') -> 'None':
    """ Adds the round-trip time that the session asks for to the network of the container.
    """
    if round_trip_ms := os.environ.get(ModuleCtx.Env_Round_Trip_Ms, ''):
        add_round_trip_time(database.container_name, float(round_trip_ms))

# ################################################################################################################################

def _start_bouncer(database:'PubSubDatabase') -> 'None':
    """ Starts PgBouncer in front of the database of a managed mode and makes the endpoint name resolve to it.
    """
    database.bouncer_container = f'{database.container_name}-bouncer'
    address = get_container_address(database.container_name)

    _ = subprocess.run(['docker', 'rm', '-f', database.bouncer_container], capture_output=True, check=False)

    start_bouncer(database.bouncer_container, database.work_dir, database.certs_dir, address, database.port,
        ModuleCtx.DB_Name, ModuleCtx.Username, database.password)

    runtime_dir = get_runtime_dir()
    bouncer_address = get_container_address(database.bouncer_container)
    session_dns.register(runtime_dir, database.endpoint, bouncer_address)

# ################################################################################################################################

def replace_container(database:'PubSubDatabase', image:'str'='', extra_settings:'strlist | None'=None,
    downtime_seconds:'float'=0) -> 'None':
    """ Shuts the database of a managed mode down and starts it again on the same data, in a new container from
    the given image and with the given settings changed, the way a database service reboots an instance for a minor
    version upgrade, a change of a parameter that requires a restart or a maintenance event. The new container may
    have another address, which its host names, its network and PgBouncer follow.
    """
    if not image:
        image = ModuleCtx.PostgreSQL_Image

    _ = subprocess.run(['docker', 'stop', database.container_name], check=True, capture_output=True)
    time.sleep(downtime_seconds)
    _ = subprocess.run(['docker', 'rm', '-f', database.container_name], check=True, capture_output=True)

    if extra_settings:
        database.settings = database.settings + extra_settings

    _run_container(database, image)
    _register_names(database)
    _wait_until_ready(database)
    _add_network(database)

    if database.bouncer_container:
        _start_bouncer(database)

# ################################################################################################################################

@contextmanager
def pubsub_db_env(env:'strstrdict') -> 'Iterator[None]':
    """ Points the Zato_PubSub_DB_* variables at one database for the duration of a test.
    """
    old_values:'anydict' = {}

    for name, value in env.items():
        old_values[name] = os.environ.get(name)
        os.environ[name] = value

    try:
        yield
    finally:
        for name, old_value in old_values.items():
            if old_value is None:
                _ = os.environ.pop(name, None)
            else:
                os.environ[name] = old_value

# ################################################################################################################################

def stop_pubsub_database(database:'PubSubDatabase') -> 'None':
    """ Removes the container of a session together with its data directory.
    """
    if not database.container_name:
        return

    if database.bouncer_container:
        _ = subprocess.run(['docker', 'rm', '-f', database.bouncer_container], capture_output=True, check=False)

    _ = subprocess.run(['docker', 'rm', '-f', database.container_name], capture_output=True, check=False)
    shutil.rmtree(database.work_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
