# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ipaddress
import os
from datetime import timedelta
from typing import NamedTuple

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

# Zato
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

# How many days the throwaway test certificates are valid for
_validity_days = 7

# The key size for all the throwaway test keys
_key_size = 2048

# The certificates are read by servers running under other users, e.g. in containers
_file_mode = 0o644

# ################################################################################################################################
# ################################################################################################################################

class CertificatePaths(NamedTuple):
    directory: str
    ca_cert: str
    server_cert: str
    server_key: str
    client_cert: str
    client_key: str

# ################################################################################################################################
# ################################################################################################################################

def _write_private_key(path:'str', key:'rsa.RSAPrivateKey') -> 'None':
    """ Writes one private key in PEM format.
    """
    data = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )

    with open(path, 'wb') as file_:
        _ = file_.write(data)

    os.chmod(path, _file_mode)

# ################################################################################################################################

def _write_certificate(path:'str', certificate:'x509.Certificate') -> 'None':
    """ Writes one certificate in PEM format.
    """
    data = certificate.public_bytes(serialization.Encoding.PEM)

    with open(path, 'wb') as file_:
        _ = file_.write(data)

    os.chmod(path, _file_mode)

# ################################################################################################################################

def _build_name(common_name:'str') -> 'x509.Name':
    """ Builds an X.509 subject out of a common name.
    """
    out = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Zato Live Tests'),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    return out

# ################################################################################################################################

def generate_certificates(directory:'str') -> 'CertificatePaths':
    """ Generates a throwaway CA along with server and client certificates for TLS tests.
    The server certificate covers localhost and 127.0.0.1 so hostname verification passes.
    """
    now = utcnow()
    not_valid_after = now + timedelta(days=_validity_days)

    # The CA that both the server and the client certificates chain up to ..
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=_key_size)
    ca_name = _build_name('Zato Live Test CA')

    ca_cert = x509.CertificateBuilder(). \
        subject_name(ca_name). \
        issuer_name(ca_name). \
        public_key(ca_key.public_key()). \
        serial_number(x509.random_serial_number()). \
        not_valid_before(now). \
        not_valid_after(not_valid_after). \
        add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True). \
        sign(ca_key, hashes.SHA256())

    # .. the server certificate, with subject alternative names for local connections ..
    server_key = rsa.generate_private_key(public_exponent=65537, key_size=_key_size)

    server_alt_names = x509.SubjectAlternativeName([
        x509.DNSName('localhost'),
        x509.IPAddress(ipaddress.ip_address('127.0.0.1')),
    ])

    server_cert = x509.CertificateBuilder(). \
        subject_name(_build_name('localhost')). \
        issuer_name(ca_name). \
        public_key(server_key.public_key()). \
        serial_number(x509.random_serial_number()). \
        not_valid_before(now). \
        not_valid_after(not_valid_after). \
        add_extension(server_alt_names, critical=False). \
        sign(ca_key, hashes.SHA256())

    # .. and the client certificate for mutual TLS.
    client_key = rsa.generate_private_key(public_exponent=65537, key_size=_key_size)

    client_cert = x509.CertificateBuilder(). \
        subject_name(_build_name('zato-live-test-client')). \
        issuer_name(ca_name). \
        public_key(client_key.public_key()). \
        serial_number(x509.random_serial_number()). \
        not_valid_before(now). \
        not_valid_after(not_valid_after). \
        sign(ca_key, hashes.SHA256())

    out = CertificatePaths(
        directory=directory,
        ca_cert=os.path.join(directory, 'ca.crt'),
        server_cert=os.path.join(directory, 'server.crt'),
        server_key=os.path.join(directory, 'server.key'),
        client_cert=os.path.join(directory, 'client.crt'),
        client_key=os.path.join(directory, 'client.key'),
    )

    _write_certificate(out.ca_cert, ca_cert)
    _write_certificate(out.server_cert, server_cert)
    _write_private_key(out.server_key, server_key)
    _write_certificate(out.client_cert, client_cert)
    _write_private_key(out.client_key, client_key)

    return out

# ################################################################################################################################
# ################################################################################################################################
