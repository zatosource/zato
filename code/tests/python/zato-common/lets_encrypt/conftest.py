# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import socket
import sys
from dataclasses import dataclass
from shutil import rmtree
from subprocess import Popen, STDOUT
from tempfile import mkdtemp
from time import sleep, time

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

# pytest
import pytest

# requests
import requests

# Zato
from certificates import generate_certificates
from zato.common.api import Lets_Encrypt

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from pathlib import Path
    from certificates import CertificatePaths
    from zato.common.typing_ import strstrdict

    certificatesgen = Iterator[CertificatePaths]
    pebblegen = Iterator['PebbleServer']

# ################################################################################################################################
# ################################################################################################################################

class PebbleCtx:

    # The name that /etc/hosts points to this host, so that Pebble validates the challenge locally.
    Host = 'zato.test'
    Loopback = '127.0.0.1'

    # The validity periods of the two profiles Pebble offers, in seconds - 90 days and 6 days, as with Let's Encrypt.
    Default_Validity = 7776000
    Short_Lived_Validity = 518400

    # How long to wait for Pebble to become ready, in seconds.
    Ready_Timeout = 30
    Ready_Sleep = 0.1
    Ready_Request_Timeout = 2

    Pebble_Binary_Name = 'pebble'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PebbleServer:

    # The ACME directory that lego is pointed at.
    directory_url: 'str'

    # The address of the endpoints that tests use to control Pebble, e.g. to tell a client to renew a certificate.
    management_url: 'str'

    # The CA that Pebble's own HTTPS certificate is trusted through.
    ca_file: 'str'

    # The port Pebble connects to when it validates a TLS-ALPN-01 challenge.
    challenge_port: 'int'

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Returns a port that nothing listens on at the moment.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((PebbleCtx.Loopback, 0))
        out = sock.getsockname()[1]

    return out

# ################################################################################################################################

def _check_hosts() -> 'None':
    """ Makes sure that the name the certificates are issued for points to this host.
    """
    try:
        address = socket.gethostbyname(PebbleCtx.Host)
    except socket.gaierror:
        raise Exception(f'Add "{PebbleCtx.Loopback} {PebbleCtx.Host}" to /etc/hosts') from None

    if address != PebbleCtx.Loopback:
        raise Exception(f'{PebbleCtx.Host} points to {address} instead of {PebbleCtx.Loopback} in /etc/hosts')

# ################################################################################################################################

def _wait_until_ready(server:'PebbleServer', process:'Popen', log_path:'str') -> 'None':
    """ Polls Pebble until its ACME directory responds, up to a timeout.
    """
    deadline = time() + PebbleCtx.Ready_Timeout

    while time() < deadline:

        # There is no point in waiting further if Pebble already exited, e.g. because a port is taken.
        if process.poll() is not None:
            with open(log_path) as log_file:
                log = log_file.read()
            raise Exception(f'Pebble exited with code {process.returncode}: {log}')

        try:
            response = requests.get(server.directory_url, verify=server.ca_file, timeout=PebbleCtx.Ready_Request_Timeout)
        except requests.RequestException:
            sleep(PebbleCtx.Ready_Sleep)
            continue

        if response.ok:
            return

        sleep(PebbleCtx.Ready_Sleep)

    raise Exception(f'Pebble did not become ready within {PebbleCtx.Ready_Timeout}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def certificate_paths() -> 'certificatesgen':
    """ Generates the throwaway CA and the certificate Pebble serves its ACME API with.
    """
    directory = mkdtemp(prefix='zato-lets-encrypt-certificates-')

    out = generate_certificates(directory)
    yield out

    rmtree(directory, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture(scope='session')
def pebble_server(certificate_paths:'CertificatePaths') -> 'pebblegen':
    """ A local Pebble process that issues certificates the same way that Let's Encrypt does.
    """
    _check_hosts()

    directory = mkdtemp(prefix='zato-lets-encrypt-pebble-')

    listen_port = _find_free_port()
    management_port = _find_free_port()
    http_port = _find_free_port()
    challenge_port = _find_free_port()

    config = {
        'pebble': {
            'listenAddress': f'{PebbleCtx.Loopback}:{listen_port}',
            'managementListenAddress': f'{PebbleCtx.Loopback}:{management_port}',
            'certificate': certificate_paths.server_cert,
            'privateKey': certificate_paths.server_key,
            'httpPort': http_port,
            'tlsPort': challenge_port,
            'ocspResponderURL': '',
            'externalAccountBindingRequired': False,
            'domainBlocklist': [],
            'retryAfter': {
                'authz': 1,
                'order': 1,
            },
            'keyAlgorithm': 'ecdsa',
            'profiles': {
                Lets_Encrypt.DNS_Profile: {
                    'description': 'The default profile',
                    'validityPeriod': PebbleCtx.Default_Validity,
                },
                Lets_Encrypt.IP_Profile: {
                    'description': 'The profile of IP address certificates',
                    'validityPeriod': PebbleCtx.Short_Lived_Validity,
                },
            },
        }
    }

    config_path = os.path.join(directory, 'pebble-config.json')
    with open(config_path, 'w') as config_file:
        json.dump(config, config_file)

    # Pebble would otherwise sleep before each validation and reject a share of nonces on purpose.
    env = dict(os.environ)
    env['PEBBLE_VA_NOSLEEP'] = '1'
    env['PEBBLE_WFE_NONCEREJECT'] = '0'

    pebble_path = os.path.join(os.path.dirname(sys.executable), PebbleCtx.Pebble_Binary_Name)
    log_path = os.path.join(directory, 'pebble.log')

    with open(log_path, 'w') as log_file:
        process = Popen([pebble_path, '-config', config_path], env=env, stdout=log_file, stderr=STDOUT)

    server = PebbleServer()
    server.directory_url = f'https://{PebbleCtx.Loopback}:{listen_port}/dir'
    server.management_url = f'https://{PebbleCtx.Loopback}:{management_port}'
    server.ca_file = certificate_paths.ca_cert
    server.challenge_port = challenge_port

    _wait_until_ready(server, process, log_path)
    yield server

    process.terminate()
    _ = process.wait()

    rmtree(directory, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture
def lets_encrypt_environ(pebble_server:'PebbleServer', tmp_path:'Path') -> 'strstrdict':
    """ The environment variables that point the feature at Pebble, as both the production and the staging server,
    and keep all of its files in a directory of its own.
    """
    out:'strstrdict' = {
        Lets_Encrypt.Env.Use_Lets_Encrypt: 'True',
        Lets_Encrypt.Env.Subject_Alt_Name: f'subjectAltName=DNS:{PebbleCtx.Host},IP:{PebbleCtx.Loopback}',
        Lets_Encrypt.Env.Server: pebble_server.directory_url,
        Lets_Encrypt.Env.Staging_Server: pebble_server.directory_url,
        Lets_Encrypt.Env.CA_File: pebble_server.ca_file,
        Lets_Encrypt.Env.Port: str(pebble_server.challenge_port),
        Lets_Encrypt.Env.SSL_Dir: str(tmp_path),
        Lets_Encrypt.Env.HAProxy_Config: str(tmp_path / 'haproxy.cfg'),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
