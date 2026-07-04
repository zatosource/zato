# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import contextlib
import ipaddress
import os
import shutil
import socket
import ssl
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Generator

sys.path.insert(0, os.path.dirname(__file__))

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

# pytest
import pytest

# Zato
from zato.common.hl7.mllp.client import HL7MLLPClient

# Zato
from mllp_live_util import end_sequence, start_sequence, start_server, stop_server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
strstrdict     = dict[str, str]
intgen         = Generator[int, None, None]
strstrdict_gen = Generator[strstrdict, None, None]
socketgen      = Generator[socket.socket, None, None]

# ################################################################################################################################
# ################################################################################################################################
# Part 1 - TLS certificate generation
# ################################################################################################################################
# ################################################################################################################################

_cert_validity_days = 1
_ca_common_name     = 'Test-MLLP-CA'
_server_common_name = '127.0.0.1'
_client_common_name = 'test-client'

# ################################################################################################################################

def _generate_test_certs(tmp_dir:'str') -> 'dict[str, str]':
    """ Generates a CA, server cert, and client cert in the given directory.
    Returns a dict mapping logical names to file paths.
    """

    now = datetime.now(timezone.utc)
    validity_end = now + timedelta(days=_cert_validity_days)

    # -- CA key and self-signed certificate --

    ca_key = ec.generate_private_key(ec.SECP256R1())

    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, _ca_common_name)])

    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(validity_end)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(ca_key, hashes.SHA256())
    )

    # -- Server key and certificate signed by CA --

    server_key = ec.generate_private_key(ec.SECP256R1())

    server_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, _server_common_name)])

    server_cert = (
        x509.CertificateBuilder()
        .subject_name(server_name)
        .issuer_name(ca_name)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(validity_end)
        .add_extension(
            x509.SubjectAlternativeName([x509.IPAddress(_ipaddress_from_string('127.0.0.1'))]),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    # -- Client key and certificate signed by CA --

    client_key = ec.generate_private_key(ec.SECP256R1())

    client_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, _client_common_name)])

    client_cert = (
        x509.CertificateBuilder()
        .subject_name(client_name)
        .issuer_name(ca_name)
        .public_key(client_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(validity_end)
        .sign(ca_key, hashes.SHA256())
    )

    # -- Write all PEM files --

    paths:'dict[str, str]' = {}

    paths['ca'] = _write_cert(tmp_dir, 'ca.pem', ca_cert)
    paths['server_cert'] = _write_cert(tmp_dir, 'server-cert.pem', server_cert)
    paths['server_key'] = _write_key(tmp_dir, 'server-key.pem', server_key)
    paths['client_cert'] = _write_cert(tmp_dir, 'client-cert.pem', client_cert)
    paths['client_key'] = _write_key(tmp_dir, 'client-key.pem', client_key)

    return paths

# ################################################################################################################################

def _ipaddress_from_string(address:'str') -> 'ipaddress.IPv4Address':
    """ Converts an IP address string to a Python ipaddress object for x509 SAN.
    """
    return ipaddress.ip_address(address) # type: ignore[return-value]

# ################################################################################################################################

def _write_cert(tmp_dir:'str', filename:'str', cert:'x509.Certificate') -> 'str':
    """ Writes a certificate to a PEM file and returns the path.
    """
    path = os.path.join(tmp_dir, filename)
    cert_bytes = cert.public_bytes(serialization.Encoding.PEM)

    with open(path, 'wb') as file_handle:
        _ = file_handle.write(cert_bytes)

    return path

# ################################################################################################################################

def _write_key(tmp_dir:'str', filename:'str', key:'ec.EllipticCurvePrivateKey') -> 'str':
    """ Writes a private key to a PEM file and returns the path.
    """
    path = os.path.join(tmp_dir, filename)

    key_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    with open(path, 'wb') as file_handle:
        _ = file_handle.write(key_bytes)

    return path

# ################################################################################################################################
# ################################################################################################################################
# Part 2 - Pytest fixtures
# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def mllp_server() -> 'intgen':
    """ Starts an MLLP test server in callback_mode=ok and yields its port.
    """
    process, port = start_server(callback_mode='ok')
    yield port
    stop_server(process)

# ################################################################################################################################

@pytest.fixture(scope='session')
def tls_certs() -> 'strstrdict_gen':
    """ Generates ephemeral TLS certificates and yields a dict of file paths.
    """
    tmp_dir = tempfile.mkdtemp(prefix='mllp-tls-')
    paths = _generate_test_certs(tmp_dir)
    yield paths
    shutil.rmtree(tmp_dir, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture(scope='session')
def mllp_tls_server(tls_certs:'strstrdict') -> 'intgen':
    """ Starts an MLLP test server with TLS (mTLS required) and yields its port.
    """
    process, port = start_server(
        tls_cert=tls_certs['server_cert'],
        tls_key=tls_certs['server_key'],
        tls_ca=tls_certs['ca'],
        tls_verify='required',
    )
    yield port
    stop_server(process)

# ################################################################################################################################
# ################################################################################################################################
# Part 3 - Client factories
# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def make_client() -> 'callable_':
    """ Returns a factory function that creates an HL7MLLPClient for a given port.
    """
    def _factory(port:'int', ssl_context:'ssl.SSLContext | None'=None) -> 'HL7MLLPClient':
        return HL7MLLPClient(
            '127.0.0.1',
            port,
            start_sequence,
            end_sequence,
            receive_timeout=5.0,
            ssl_context=ssl_context,
        )

    return _factory

# ################################################################################################################################

@pytest.fixture
def make_raw_sender() -> 'callable_':
    """ Returns a factory that creates a context manager for a raw TCP socket.
    """

    @contextlib.contextmanager
    def _factory(port:'int') -> 'socketgen':
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', port))
        raw_socket.settimeout(5.0)

        try:
            yield raw_socket
        finally:
            try:
                raw_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            raw_socket.close()

    return _factory

# ################################################################################################################################
# ################################################################################################################################
