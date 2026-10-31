# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The pub/sub database of a test session - the SQLite file of its environment, or a PostgreSQL container started
# for the session, with or without TLS, whose data directory is under the runtime directory of the tests.

# stdlib
import ipaddress
import os
import shutil
import socket
import ssl
import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import timedelta

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

# pg8000
import pg8000.dbapi

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import anydict, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class PubSubDBMode:
    SQLite          = 'sqlite'
    PostgreSQL      = 'postgresql'
    PostgreSQL_TLS  = 'postgresql-tls'
    PostgreSQL_MTLS = 'postgresql-mtls'

# The modes with a PostgreSQL container and those of them that require TLS.
_postgresql_modes = {PubSubDBMode.PostgreSQL, PubSubDBMode.PostgreSQL_TLS, PubSubDBMode.PostgreSQL_MTLS}
_tls_modes = {PubSubDBMode.PostgreSQL_TLS, PubSubDBMode.PostgreSQL_MTLS}

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

    # The prefix of the containers, which lets a session remove those that an interrupted session left behind
    Container_Prefix = 'zato-pubsub-test-'

# How long a container may take to accept connections, in seconds, and how often it is checked.
_ready_timeout = 120
_ready_poll_interval = 0.5

# How long the throwaway certificates are valid and how large their keys are.
_validity_days = 7
_key_size = 2048

# The certificates are read by the database server in the container, which runs under the same user as the tests.
_certificate_mode = 0o644
_key_mode = 0o600
_directory_mode = 0o755

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
    port: 'int' = 0
    password: 'str' = ''
    work_dir: 'str' = ''
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
# ################################################################################################################################

def _new_key() -> 'rsa.RSAPrivateKey':
    out = rsa.generate_private_key(public_exponent=65537, key_size=_key_size)
    return out

# ################################################################################################################################

def _write_key(path:'str', key:'rsa.RSAPrivateKey') -> 'None':
    data = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption())

    with open(path, 'wb') as key_file:
        _ = key_file.write(data)

    os.chmod(path, _key_mode)

# ################################################################################################################################

def _write_certificate(path:'str', certificate:'x509.Certificate') -> 'None':
    data = certificate.public_bytes(serialization.Encoding.PEM)

    with open(path, 'wb') as certificate_file:
        _ = certificate_file.write(data)

    os.chmod(path, _certificate_mode)

# ################################################################################################################################

def _issue(subject:'str', key:'rsa.RSAPrivateKey', issuer:'str', issuer_key:'rsa.RSAPrivateKey', is_ca:'bool',
    host_names:'strlist') -> 'x509.Certificate':
    """ Issues one certificate, a CA's own or one signed by a CA, valid for the given host names.
    """
    now = utcnow()

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject)]))
    builder = builder.issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, issuer)]))
    builder = builder.public_key(key.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(now - timedelta(days=1))
    builder = builder.not_valid_after(now + timedelta(days=_validity_days))
    builder = builder.add_extension(x509.BasicConstraints(ca=is_ca, path_length=None), critical=True)

    if host_names:
        names:'list' = []
        for host_name in host_names:
            try:
                address = ipaddress.ip_address(host_name)
                names.append(x509.IPAddress(address))
            except ValueError:
                names.append(x509.DNSName(host_name))
        builder = builder.add_extension(x509.SubjectAlternativeName(names), critical=False)

    out = builder.sign(issuer_key, hashes.SHA256())
    return out

# ################################################################################################################################

def generate_certificates(directory:'str', host_names:'strlist') -> 'None':
    """ Writes a CA, a server certificate for the given host names and a client certificate into a directory.
    """
    ca_name = 'Zato pub/sub test CA'

    ca_key = _new_key()
    ca_cert = _issue(ca_name, ca_key, ca_name, ca_key, True, [])

    server_key = _new_key()
    server_cert = _issue('localhost', server_key, ca_name, ca_key, False, host_names)

    client_key = _new_key()
    client_cert = _issue(ModuleCtx.Username, client_key, ca_name, ca_key, False, [])

    _write_certificate(os.path.join(directory, 'ca.crt'), ca_cert)
    _write_certificate(os.path.join(directory, 'server.crt'), server_cert)
    _write_key(os.path.join(directory, 'server.key'), server_key)
    _write_certificate(os.path.join(directory, 'client.crt'), client_cert)
    _write_key(os.path.join(directory, 'client.key'), client_key)

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

def connect(database:'PubSubDatabase', host:'str'='localhost', port:'int'=0) -> 'pg8000.dbapi.Connection':
    """ Opens a pg8000 connection to the database of a session, outside of any engine.
    """
    if not port:
        port = database.port

    if database.mode in _tls_modes:
        ssl_context = build_ssl_context(database)
    else:
        ssl_context = False

    out = pg8000.dbapi.connect(user=ModuleCtx.Username, password=database.password, host=host, port=port,
        database=ModuleCtx.DB_Name, ssl_context=ssl_context, timeout=10)

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

def start_pubsub_database(label:'str', mode:'str', extra_settings:'strlist | None'=None,
    extra_docker_args:'strlist | None'=None) -> 'PubSubDatabase':
    """ Starts the pub/sub database of a session in the given mode. SQLite needs nothing started.
    """
    out = PubSubDatabase(mode=mode)

    if not is_postgresql_mode(mode):
        return out

    out.port = _find_free_port()
    out.password = 'pubsub.' + CryptoManager.generate_hex_string()
    out.container_name = f'{ModuleCtx.Container_Prefix}{label}-{out.port}'

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
        '-e', 'POSTGRES_USER=' + ModuleCtx.Username,
        '-e', 'POSTGRES_PASSWORD=' + out.password,
        '-e', 'POSTGRES_DB=' + ModuleCtx.DB_Name,
        '-v', f'{data_dir}:/var/lib/postgresql/data',
        '-p', f'{out.port}:5432',
    ]

    # .. the TLS modes accept TCP connections over TLS only ..
    if mode in _tls_modes:
        generate_certificates(certs_dir, ['localhost', '127.0.0.1', out.container_name])

        setup_script = os.path.join(certs_dir, 'tls-setup.sh')
        _write_tls_setup_script(setup_script, mode == PubSubDBMode.PostgreSQL_MTLS)

        command.extend(['-v', f'{certs_dir}:/certs-in:ro'])
        command.extend(['-v', f'{setup_script}:/docker-entrypoint-initdb.d/tls-setup.sh:ro'])

    if extra_docker_args:
        command.extend(extra_docker_args)

    command.append(ModuleCtx.PostgreSQL_Image)
    command.append('postgres')

    settings = _postgresql_settings + _postgresql_diagnostics

    if extra_settings:
        settings = settings + extra_settings

    for setting in settings:
        command.extend(['-c', setting])

    _ = subprocess.run(command, check=True, capture_output=True)

    # .. the environment of the server and of the test process point at the container ..
    out.env = {
        'Zato_PubSub_DB_Type': 'postgresql',
        'Zato_PubSub_DB_Host': 'localhost',
        'Zato_PubSub_DB_Port': str(out.port),
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

    # .. and the container is ready once it accepts them.
    _wait_until_ready(out)

    return out

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

    _ = subprocess.run(['docker', 'rm', '-f', database.container_name], capture_output=True, check=False)
    shutil.rmtree(database.work_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
