# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ipaddress
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat
from cryptography.x509.oid import NameOID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.x509 import Certificate
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

# ################################################################################################################################
# ################################################################################################################################

_rsa_public_exponent = 65537
_rsa_key_size = 2048

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class TLSMaterial:
    """ Every file path a TLS exchange with a test server needs - the CA that signed everything
    plus the server's own certificate and key.
    """
    __test__ = False

    ca_path: 'str'

    server_certificate_path: 'str'
    server_key_path: 'str'

    # The temporary directory holding all of the above, removed on cleanup.
    directory: 'str'

# ################################################################################################################################
# ################################################################################################################################

def _new_key() -> 'RSAPrivateKey':
    out = rsa.generate_private_key(public_exponent=_rsa_public_exponent, key_size=_rsa_key_size)
    return out

# ################################################################################################################################

def _name(common_name:'str') -> 'x509.Name':
    out = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    return out

# ################################################################################################################################

def _ca_certificate(key:'RSAPrivateKey', name:'x509.Name') -> 'Certificate':
    """ Issues a self-signed CA certificate.
    """
    now = datetime.now(timezone.utc)

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(name)
    builder = builder.issuer_name(name)
    builder = builder.public_key(key.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(now - timedelta(days=1))
    builder = builder.not_valid_after(now + timedelta(days=365))
    builder = builder.add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)

    out = builder.sign(key, hashes.SHA256())
    return out

# ################################################################################################################################

def _server_certificate(
    common_name:'str',
    public_key:'object',
    ca_key:'RSAPrivateKey',
    ca_name:'x509.Name',
    host:'str',
    ) -> 'Certificate':
    """ Issues a CA-signed server certificate that names the host both as a DNS name and,
    for numeric hosts, as an IP address, so hostname validation passes either way.
    """
    now = datetime.now(timezone.utc)

    alternative_names = [x509.DNSName(host), x509.DNSName('localhost')]

    try:
        alternative_names.append(x509.IPAddress(ipaddress.ip_address(host)))
    except ValueError:
        pass

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(_name(common_name))
    builder = builder.issuer_name(ca_name)
    builder = builder.public_key(public_key)
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(now - timedelta(days=1))
    builder = builder.not_valid_after(now + timedelta(days=365))
    builder = builder.add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
    builder = builder.add_extension(x509.SubjectAlternativeName(alternative_names), critical=False)

    out = builder.sign(ca_key, hashes.SHA256())
    return out

# ################################################################################################################################

def _write(directory:'str', file_name:'str', data:'bytes') -> 'str':
    path = os.path.join(directory, file_name)
    with open(path, 'wb') as handle:
        _ = handle.write(data)
    return path

# ################################################################################################################################

def build_tls_material(host:'str') -> 'TLSMaterial':
    """ Builds a CA plus a server certificate for the given host,
    writing every artifact to a fresh temporary directory.
    """
    directory = tempfile.mkdtemp(prefix='sql_cloud_test_tls_')

    ca_key = _new_key()
    ca_name = _name('sql-cloud-test-ca')
    ca_certificate = _ca_certificate(ca_key, ca_name)

    server_key = _new_key()
    server_certificate = _server_certificate('sql-cloud-test-server', server_key.public_key(), ca_key, ca_name, host)

    ca_pem = ca_certificate.public_bytes(Encoding.PEM)
    server_certificate_pem = server_certificate.public_bytes(Encoding.PEM)
    server_key_pem = server_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())

    out = TLSMaterial()
    out.directory = directory
    out.ca_path = _write(directory, 'ca.pem', ca_pem)
    out.server_certificate_path = _write(directory, 'server-cert.pem', server_certificate_pem)
    out.server_key_path = _write(directory, 'server-key.pem', server_key_pem)

    return out

# ################################################################################################################################
# ################################################################################################################################
