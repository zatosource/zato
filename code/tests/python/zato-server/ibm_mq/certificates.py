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

# The certificates are mounted into the queue manager container whose user needs to read them
_file_mode = 0o644

# The queue manager container needs to traverse into the mounted key directory
_directory_mode = 0o755

# ################################################################################################################################
# ################################################################################################################################

class CertificatePaths(NamedTuple):
    directory: str
    ca_cert: str
    server_keys_directory: str

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
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Zato IBM MQ Tests'),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    return out

# ################################################################################################################################

def generate_certificates(directory:'str') -> 'CertificatePaths':
    """ Generates a throwaway CA and a server certificate for the queue manager, laid out the way
    the IBM MQ container expects them - a keys directory with tls.crt and tls.key files.
    The server certificate covers localhost and 127.0.0.1 so hostname verification passes.
    """
    now = utcnow()
    not_valid_after = now + timedelta(days=_validity_days)

    # The CA the server certificate chains up to ..
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=_key_size)
    ca_name = _build_name('Zato IBM MQ Test CA')

    ca_cert = x509.CertificateBuilder(). \
        subject_name(ca_name). \
        issuer_name(ca_name). \
        public_key(ca_key.public_key()). \
        serial_number(x509.random_serial_number()). \
        not_valid_before(now). \
        not_valid_after(not_valid_after). \
        add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True). \
        sign(ca_key, hashes.SHA256())

    # .. and the server certificate, with subject alternative names for local connections.
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

    # The container mounts the keys directory at /etc/mqm/pki/keys/default,
    # which enables TLS on the developer channels with ANY_TLS12_OR_HIGHER.
    server_keys_directory = os.path.join(directory, 'keys')
    os.makedirs(server_keys_directory)
    os.chmod(server_keys_directory, _directory_mode)

    out = CertificatePaths(
        directory=directory,
        ca_cert=os.path.join(directory, 'ca.crt'),
        server_keys_directory=server_keys_directory,
    )

    # The bridge verifies the queue manager against the CA certificate in PEM format
    _write_certificate(out.ca_cert, ca_cert)

    # The queue manager reads its certificate and key from fixed file names,
    # with the CA alongside them so it can build the certificate chain.
    server_cert_path = os.path.join(server_keys_directory, 'tls.crt')
    server_key_path = os.path.join(server_keys_directory, 'tls.key')
    server_ca_path = os.path.join(server_keys_directory, 'ca.crt')

    _write_certificate(server_cert_path, server_cert)
    _write_private_key(server_key_path, server_key)
    _write_certificate(server_ca_path, ca_cert)

    return out

# ################################################################################################################################
# ################################################################################################################################
