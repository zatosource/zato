# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import subprocess
from shutil import copy2, copytree, rmtree
from tempfile import mkdtemp
from time import sleep, time
from typing import NamedTuple

# Elasticsearch
from elasticsearch import Elasticsearch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from subprocess import Popen
    from live_sql.certificates import CertificatePaths
    from zato.common.typing_ import optional, stranydict

    CertificatePaths = CertificatePaths
    certificatepathsnone = optional[CertificatePaths]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The environment variable pointing to an unpacked Elasticsearch distribution
    Env_Key_ES_Dir = 'Zato_Test_ElasticSearch_Dir'

    # The built-in superuser that Elasticsearch creates when security is enabled
    Superuser = 'elastic'

    # How long to wait for a server to accept connections - a cold JVM start takes a while
    Ready_Timeout = 300

    # How long to sleep between connection attempts
    Ready_Sleep = 1

    # How long a single readiness connection attempt may take, in seconds
    Ready_Connect_Timeout = 2

    # The readiness loop below is the retry mechanism - the client must not retry on its own
    # within a single poll attempt, which the default transport would do three times.
    Ready_Max_Retries = 0

    # The loggers that would otherwise report each expected connection failure
    # while the server is still starting - they are silenced for the poll only.
    Ready_Quiet_Loggers = ['elastic_transport.node_pool', 'elastic_transport.transport']

    # The heap is capped so the tests do not take half of the machine's memory
    Java_Opts = '-Xms512m -Xmx512m'

    # How far apart the internal transport port is from the HTTP port of each instance
    Transport_Port_Offset = 100

    # How long to wait for the server process to exit after it was told to stop
    Stop_Timeout = 60

# ################################################################################################################################
# ################################################################################################################################

class ESServer(NamedTuple):
    process: 'Popen'
    host: str
    port: int
    scheme: str
    username: str
    password: str
    work_dir: str

# ################################################################################################################################
# ################################################################################################################################

def _build_config_yaml(*, port:'int', data_dir:'str', logs_dir:'str', has_tls:'bool') -> 'str':
    """ Builds the contents of elasticsearch.yml for one throwaway test instance.
    """
    # The internal transport port must not clash with other instances either
    transport_port = port + ModuleCtx.Transport_Port_Offset

    lines = [
        'cluster.name: zato-test-es',
        f'node.name: node-{port}',
        'discovery.type: single-node',
        'network.host: 127.0.0.1',
        f'http.port: {port}',
        f'transport.port: {transport_port}',
        f'path.data: {data_dir}',
        f'path.logs: {logs_dir}',

        # Machine learning and the geoip downloader are not needed and only slow the start down
        'xpack.ml.enabled: false',
        'ingest.geoip.downloader.enabled: false',

        # Disk watermarks are disabled because a nearly full disk on a developer machine
        # would otherwise leave the cluster red and make every write hang.
        'cluster.routing.allocation.disk.threshold_enabled: false',
    ]

    # The TLS variant enables security - which is what enforces authentication too -
    # whereas the plain variant disables it wholesale so no credentials are needed.
    # The certificate paths are relative because the server's entitlements only
    # let it read SSL resources from inside its own config directory.
    if has_tls:
        lines.extend([
            'xpack.security.enabled: true',
            'xpack.security.http.ssl.enabled: true',
            'xpack.security.http.ssl.key: certs-zato/server.key',
            'xpack.security.http.ssl.certificate: certs-zato/server.crt',
            'xpack.security.http.ssl.certificate_authorities: certs-zato/ca.crt',

            # Clients may present their own certificates for mutual TLS but do not have to
            'xpack.security.http.ssl.client_authentication: optional',

            # The transport layer needs its own TLS configuration once security is on
            'xpack.security.transport.ssl.enabled: true',
            'xpack.security.transport.ssl.key: certs-zato/server.key',
            'xpack.security.transport.ssl.certificate: certs-zato/server.crt',
            'xpack.security.transport.ssl.certificate_authorities: certs-zato/ca.crt',
        ])
    else:
        lines.append('xpack.security.enabled: false')

    out = '\n'.join(lines) + '\n'
    return out

# ################################################################################################################################

def _set_bootstrap_password(es_home:'str', env:'stranydict', password:'str') -> 'None':
    """ Stores the password of the built-in superuser in the instance's keystore,
    which is how a fresh server learns it before its first start.
    """
    keystore_command = os.path.join(es_home, 'bin', 'elasticsearch-keystore')

    # The pristine distribution's config directory has no keystore yet
    _ = subprocess.run([keystore_command, 'create'], env=env, check=True, capture_output=True)

    _ = subprocess.run(
        [keystore_command, 'add', '-x', 'bootstrap.password'],
        env=env,
        input=password.encode('utf-8'),
        check=True,
        capture_output=True,
    )

# ################################################################################################################################

def _wait_until_ready(server:'ESServer', ca_cert:'str') -> 'None':
    """ Retries connecting until the server accepts requests or the timeout is reached.
    """
    deadline = time() + ModuleCtx.Ready_Timeout
    last_error = ''

    client_config:'stranydict' = {
        'hosts': [f'{server.scheme}://{server.host}:{server.port}'],
        'request_timeout': ModuleCtx.Ready_Connect_Timeout,

        # This loop is the retry mechanism - without this setting, the transport would retry
        # each failed attempt three more times on its own, multiplying the connection attempts
        # against a server that is expectedly not up yet.
        'max_retries': ModuleCtx.Ready_Max_Retries,
    }

    if server.username:
        client_config['basic_auth'] = (server.username, server.password)

    if ca_cert:
        client_config['ca_certs'] = ca_cert

    # These loggers report each refused connection at warning level, including full tracebacks,
    # which is pure noise while the server is still starting - they are raised to error level
    # for the duration of the poll and restored afterwards.
    quiet_loggers = [logging.getLogger(name) for name in ModuleCtx.Ready_Quiet_Loggers]
    original_levels = [quiet_logger.level for quiet_logger in quiet_loggers]

    for quiet_logger in quiet_loggers:
        quiet_logger.setLevel(logging.ERROR)

    try:
        while time() < deadline:

            # A dead process will never become ready - fail fast with its output
            if server.process.poll() is not None:
                raise Exception(f'Elasticsearch process exited prematurely with rc={server.process.returncode}')

            client = Elasticsearch(**client_config)
            try:
                _ = client.info()
                client.close()
                return
            except Exception as e:
                last_error = str(e)
                client.close()
                sleep(ModuleCtx.Ready_Sleep)
    finally:
        for quiet_logger, original_level in zip(quiet_loggers, original_levels):
            quiet_logger.setLevel(original_level)

    raise Exception(f'Elasticsearch at {server.host}:{server.port} did not become ready, last error: {last_error}')

# ################################################################################################################################

def start_es(
    *,
    port:'int',
    needs_tls:'bool',
    certificates:'certificatepathsnone' = None,
    password:'str' = '',
    ) -> 'ESServer':
    """ Starts an Elasticsearch instance from the distribution that Zato_Test_ElasticSearch_Dir points to,
    optionally one that requires TLS and authentication for all connections. Certificates and a password
    are always given when needs_tls is True.
    """
    es_home = os.environ[ModuleCtx.Env_Key_ES_Dir]

    # Every instance gets its own writable directories so parallel instances never clash
    work_dir = mkdtemp(prefix='zato-test-es-')

    config_dir = os.path.join(work_dir, 'config')
    data_dir = os.path.join(work_dir, 'data')
    logs_dir = os.path.join(work_dir, 'logs')

    os.makedirs(data_dir)
    os.makedirs(logs_dir)

    # Start from the distribution's own config directory - it has the JVM options
    # and logging configuration that the server needs - and only replace elasticsearch.yml.
    copytree(os.path.join(es_home, 'config'), config_dir)

    # The server may only read SSL resources from inside its config directory,
    # which is why the throwaway certificates are copied there.
    if needs_tls:
        certs_dir = os.path.join(config_dir, 'certs-zato')
        os.makedirs(certs_dir)
        for path in [certificates.server_key, certificates.server_cert, certificates.ca_cert]:
            _ = copy2(path, certs_dir)

    config_yaml = _build_config_yaml(port=port, data_dir=data_dir, logs_dir=logs_dir, has_tls=needs_tls)
    with open(os.path.join(config_dir, 'elasticsearch.yml'), 'w') as config_file:
        _ = config_file.write(config_yaml)

    # The instance-specific config directory is passed through the environment
    env = dict(os.environ)
    env['ES_PATH_CONF'] = config_dir
    env['ES_JAVA_OPTS'] = ModuleCtx.Java_Opts

    # The superuser's initial password has to be in the keystore before the first start
    if needs_tls:
        _set_bootstrap_password(es_home, env, password)

    # The console output goes to a file so it can be inspected when startup fails
    stdout_path = os.path.join(work_dir, 'stdout.log')
    stdout_file = open(stdout_path, 'wb')

    process = subprocess.Popen(
        [os.path.join(es_home, 'bin', 'elasticsearch')],
        env=env,
        stdout=stdout_file,
        stderr=subprocess.STDOUT,
    )

    scheme = 'https' if needs_tls else 'http'
    username = ModuleCtx.Superuser if needs_tls else ''

    out = ESServer(
        process=process,
        host='localhost',
        port=port,
        scheme=scheme,
        username=username,
        password=password,
        work_dir=work_dir,
    )

    # Wait until the server accepts requests from the host
    ca_cert = certificates.ca_cert if certificates else ''
    _wait_until_ready(out, ca_cert)

    return out

# ################################################################################################################################

def stop_es(server:'ESServer') -> 'None':
    """ Stops an Elasticsearch instance and removes its working directory.
    """
    server.process.terminate()
    _ = server.process.wait(timeout=ModuleCtx.Stop_Timeout)

    rmtree(server.work_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
