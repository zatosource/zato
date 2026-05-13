# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import contextlib
import ipaddress
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Generator

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

# colorama
from colorama import Fore, Style, init as colorama_init

# pytest
import pytest

# Zato
from zato.common.hl7.mllp.client import HL7MLLPClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

colorama_init(autoreset=True)

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
strstrdict     = dict[str, str]
intgen         = Generator[int, None, None]
strstrdict_gen = Generator[strstrdict, None, None]
socketgen      = Generator[socket.socket, None, None]

# ################################################################################################################################
# ################################################################################################################################

# Standard MLLP framing bytes
_start_sequence = b'\x0b'
_end_sequence   = b'\x1c\x0d'

# Path to the test server script
_test_server_script = str(Path(__file__).parent / 'mllp_test_server.py')

# How long to wait for the server to print READY
_server_startup_timeout_seconds = 10

# How long to wait for the server process to terminate after SIGTERM
_server_shutdown_timeout_seconds = 5

# ################################################################################################################################
# ################################################################################################################################
# Part 1 - Server process helpers
# ################################################################################################################################
# ################################################################################################################################

def start_server(**overrides:'object') -> 'tuple[subprocess.Popen, int]':
    """ Starts the MLLP test server as a subprocess and waits for the READY signal.
    Returns (process, port).
    """

    command = [sys.executable, _test_server_script, '--port', '0']

    for key, value in overrides.items():

        # Convert Python snake_case kwarg to CLI --kebab-case arg
        cli_key = '--' + key.replace('_', '-')

        # Boolean toggles use --no- prefix for False
        if isinstance(value, bool):
            if not value:
                cli_key = '--no-' + key.replace('_', '-')
            command.append(cli_key)
        else:
            command.append(cli_key)
            command.append(str(value))

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Read stdout until we see the READY line
    deadline = time.monotonic() + _server_startup_timeout_seconds
    port = 0

    for line in process.stdout: # type: ignore[union-attr]

        stripped_line = line.strip()
        match = re.match(r'^READY:(\d+)$', stripped_line)

        if match:
            port = int(match.group(1))
            break

        if time.monotonic() > deadline:
            process.kill()
            raise RuntimeError(f'MLLP test server did not print READY within {_server_startup_timeout_seconds}s')

    if port == 0:
        process.kill()
        raise RuntimeError('MLLP test server exited before printing READY')

    return process, port

# ################################################################################################################################

def stop_server(process:'subprocess.Popen') -> 'None':
    """ Sends SIGTERM to the server process and waits for it to exit.
    Falls back to SIGKILL if it does not exit in time.
    """
    process.terminate()

    try:
        process.wait(timeout=_server_shutdown_timeout_seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()

# ################################################################################################################################
# ################################################################################################################################
# Part 2 - TLS certificate generation
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

    with open(path, 'wb') as file_handle:
        file_handle.write(cert.public_bytes(serialization.Encoding.PEM))

    return path

# ################################################################################################################################

def _write_key(tmp_dir:'str', filename:'str', key:'ec.EllipticCurvePrivateKey') -> 'str':
    """ Writes a private key to a PEM file and returns the path.
    """
    path = os.path.join(tmp_dir, filename)

    with open(path, 'wb') as file_handle:
        file_handle.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    return path

# ################################################################################################################################
# ################################################################################################################################
# Part 3 - Pytest fixtures
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
# Part 4 - Client factories and sample messages
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
            _start_sequence,
            _end_sequence,
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
# Sample HL7 messages
# ################################################################################################################################
# ################################################################################################################################

def sample_adt_a01(control_id:'str'='CTRL001') -> 'bytes':
    """ Returns a well-formed ADT^A01 message as bytes.
    """
    message = (
        f'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|{control_id}|P|2.5\r'
        f'PID|||12345^^^MRN||Doe^John||19800101|M\r'
        f'PV1||I|ICU^Room1'
    )
    return message.encode('utf-8')

# ################################################################################################################################

def sample_oru_r01(control_id:'str'='CTRL002') -> 'bytes':
    """ Returns a well-formed ORU^R01 message as bytes.
    """
    message = (
        f'MSH|^~\\&|LabSys|LabFac|OrderSys|OrderFac|20230101130000||ORU^R01|{control_id}|P|2.5\r'
        f'PID|||67890^^^MRN||Smith^Jane||19900515|F\r'
        f'OBR|1||LAB001|CBC^Complete Blood Count\r'
        f'OBX|1|NM|WBC^White Blood Count||7.5|10*3/uL|4.5-11.0|N|||F'
    )
    return message.encode('utf-8')

# ################################################################################################################################
# ################################################################################################################################
# Performance logging helper
# ################################################################################################################################
# ################################################################################################################################

_perf_label_width = 40

def perf_log(label:'str', value:'float', unit:'str', threshold:'float'=0.0) -> 'None':
    """ Prints a colorama-formatted performance result line.

    Format: [PERF] Label ............. Value unit [PASS/FAIL]
    """

    # Build the dot-padded label
    dots_needed = _perf_label_width - len(label)

    if dots_needed < 3:
        dots_needed = 3

    dots = '.' * dots_needed

    prefix = f'{Fore.CYAN}{Style.BRIGHT}[PERF]{Style.RESET_ALL}'
    padded_label = f' {label} {Fore.WHITE}{Style.DIM}{dots}{Style.RESET_ALL} '

    # Color the value green or red depending on threshold
    if threshold > 0.0 and value < threshold:
        colored_value = f'{Fore.RED}{Style.BRIGHT}{value:,.1f}{Style.RESET_ALL}'
        suffix = f' {Fore.RED}{Style.BRIGHT}[FAIL]{Style.RESET_ALL}'
    elif threshold > 0.0:
        colored_value = f'{Fore.GREEN}{Style.BRIGHT}{value:,.1f}{Style.RESET_ALL}'
        suffix = f' {Fore.GREEN}{Style.BRIGHT}[PASS]{Style.RESET_ALL}'
    else:
        colored_value = f'{Fore.GREEN}{Style.BRIGHT}{value:,.1f}{Style.RESET_ALL}'
        suffix = ''

    unit_display = f' {Fore.WHITE}{unit}{Style.RESET_ALL}'

    print(f'{prefix}{padded_label}{colored_value}{unit_display}{suffix}')

# ################################################################################################################################
# ################################################################################################################################
# Re-exports for convenience in test files
# ################################################################################################################################
# ################################################################################################################################

# These are re-exported so test files can import from conftest without reaching
# into the production code directly for framing constants.

start_sequence = _start_sequence
end_sequence   = _end_sequence
