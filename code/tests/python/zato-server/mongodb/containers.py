# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import subprocess
from time import sleep, time
from typing import NamedTuple

# PyMongo
from pymongo import MongoClient

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

    # Docker image the servers run from
    MongoDB_Image = 'mongo:8'

    # The port MongoDB listens on inside the container
    MongoDB_Port = 27017

    # How long to wait for a server to accept connections
    Ready_Timeout = 300

    # How long to sleep between connection attempts
    Ready_Sleep = 1

    # How long a single readiness connection attempt may take, in milliseconds
    Ready_Connect_Timeout_MS = 2000

# ################################################################################################################################
# ################################################################################################################################

class MongoDBServer(NamedTuple):
    container_name: str
    host: str
    port: int
    username: str
    password: str

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

def _wait_until_ready(port:'int', username:'str', password:'str', tls_config:'stranydict') -> 'None':
    """ Retries connecting until the server accepts connections or the timeout is reached.
    """
    deadline = time() + ModuleCtx.Ready_Timeout
    last_error = ''

    while time() < deadline:
        client = MongoClient(
            host=f'localhost:{port}',
            username=username,
            password=password,
            connectTimeoutMS=ModuleCtx.Ready_Connect_Timeout_MS,
            serverSelectionTimeoutMS=ModuleCtx.Ready_Connect_Timeout_MS,
            **tls_config,
        )
        try:
            _ = client.admin.command('ping')
            client.close()
            return
        except Exception as e:
            last_error = str(e)
            client.close()
            sleep(ModuleCtx.Ready_Sleep)

    raise Exception(f'MongoDB at localhost:{port} did not become ready, last error: {last_error}')

# ################################################################################################################################

def start_mongodb(
    *,
    container_name:'str',
    port:'int',
    username:'str',
    password:'str',
    needs_tls:'bool',
    certificates:'certificatepathsnone' = None,
    ) -> 'MongoDBServer':
    """ Starts a MongoDB container, optionally one that requires TLS for all connections.
    Certificates are always given when needs_tls is True - the directory then contains
    a combined server.pem next to the CA certificate - and they are dereferenced only then.
    """
    tls_certificates:'CertificatePaths' = cast_('CertificatePaths', certificates)

    _remove_stale_container(container_name)

    command:'strlist' = [
        'docker', 'run', '-d', '--rm',
        '--name', container_name,
        '-e', 'MONGO_INITDB_ROOT_USERNAME=' + username,
        '-e', 'MONGO_INITDB_ROOT_PASSWORD=' + password,
        '-p', f'{port}:{ModuleCtx.MongoDB_Port}',
    ]

    # The TLS-required variant mounts the certificates and refuses unencrypted connections -
    # clients do not have to present their own certificates but, when they do,
    # the certificates are verified against the same throwaway CA.
    if needs_tls:
        command.extend(['-v', f'{tls_certificates.directory}:/certs-in:ro'])
        command.append(ModuleCtx.MongoDB_Image)
        command.extend([
            'mongod',
            '--tlsMode', 'requireTLS',
            '--tlsCertificateKeyFile', '/certs-in/server.pem',
            '--tlsCAFile', '/certs-in/ca.crt',
            '--tlsAllowConnectionsWithoutCertificates',
        ])
    else:
        command.append(ModuleCtx.MongoDB_Image)

    _ = subprocess.run(command, check=True, capture_output=True)

    # Wait until the server accepts connections from the host
    if needs_tls:
        tls_config:'stranydict' = {'tls': True, 'tlsCAFile': tls_certificates.ca_cert}
    else:
        tls_config = {}

    _wait_until_ready(port, username, password, tls_config)

    out = MongoDBServer(container_name=container_name, host='localhost', port=port, username=username, password=password)
    return out

# ################################################################################################################################
# ################################################################################################################################
