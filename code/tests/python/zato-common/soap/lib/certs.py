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

# Zato
from zato.common.typing_ import optional

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.x509 import Certificate
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

# ################################################################################################################################
# ################################################################################################################################

general_name_list = list[x509.GeneralName]
general_name_list_none = optional[general_name_list]

# ################################################################################################################################
# ################################################################################################################################

_rsa_public_exponent = 65537
_rsa_key_size = 2048

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class TLSMaterial:
    """ Every file path a mutual-TLS exchange with the test server needs - the CA that
    signed everything, the server's own certificate and key, and a client certificate
    in both the separate-files and single-combined-file forms tests may present.
    """
    __test__ = False

    ca_path: 'str'

    server_certificate_path: 'str'
    server_key_path: 'str'

    client_certificate_path: 'str'
    client_key_path: 'str'
    client_combined_path: 'str'

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

def _leaf_certificate(
    common_name:'str',
    public_key:'RSAPublicKey',
    ca_key:'RSAPrivateKey',
    ca_name:'x509.Name',
    alternative_names:'general_name_list_none'=None,
    ) -> 'Certificate':
    """ Issues a CA-signed leaf certificate, optionally carrying subject alternative names.
    """
    now = datetime.now(timezone.utc)

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(_name(common_name))
    builder = builder.issuer_name(ca_name)
    builder = builder.public_key(public_key)
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(now - timedelta(days=1))
    builder = builder.not_valid_after(now + timedelta(days=365))
    builder = builder.add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)

    if alternative_names:
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

def _certificate_pem(certificate:'Certificate') -> 'bytes':
    out = certificate.public_bytes(Encoding.PEM)
    return out

# ################################################################################################################################

def _key_pem(key:'RSAPrivateKey') -> 'bytes':
    out = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    return out

# ################################################################################################################################

def _write_temp_pem(pem_bytes:'bytes') -> 'str':
    """ Writes PEM bytes to a new temporary file and returns the file's path.
    """
    file_descriptor, out = tempfile.mkstemp(prefix='soap_test_pem_', suffix='.pem')

    with os.fdopen(file_descriptor, 'wb') as handle:
        _ = handle.write(pem_bytes)

    return out

# ################################################################################################################################

def private_key_pem_path(key:'RSAPrivateKey') -> 'str':
    """ Serializes a private key to a temporary PEM file and returns the file's path -
    the path a WS-Security definition would keep.
    """
    pem_bytes = _key_pem(key)

    out = _write_temp_pem(pem_bytes)
    return out

# ################################################################################################################################

def certificate_pem_path(certificate:'Certificate') -> 'str':
    """ Serializes a certificate to a temporary PEM file and returns the file's path -
    the path a WS-Security definition would keep.
    """
    pem_bytes = _certificate_pem(certificate)

    out = _write_temp_pem(pem_bytes)
    return out

# ################################################################################################################################

def build_tls_material(host:'str') -> 'TLSMaterial':
    """ Builds a CA plus a server certificate for the given host and a client certificate,
    writing every artifact to a fresh temporary directory. The server certificate carries the
    host both as a DNS name and, for numeric hosts, as an IP address, so TLS validation passes.
    """
    directory = tempfile.mkdtemp(prefix='soap_test_tls_')

    ca_key = _new_key()
    ca_name = _name('soap-test-ca')
    ca_certificate = _ca_certificate(ca_key, ca_name)

    # The server certificate must name the host both ways so requests validates it either way.
    alternative_names:'general_name_list' = [x509.DNSName(host), x509.DNSName('localhost')]
    try:
        alternative_names.append(x509.IPAddress(ipaddress.ip_address(host)))
    except ValueError:
        pass

    server_key = _new_key()
    server_certificate = _leaf_certificate('soap-test-server', server_key.public_key(), ca_key, ca_name,
        alternative_names)

    client_key = _new_key()
    client_certificate = _leaf_certificate('soap-test-client', client_key.public_key(), ca_key, ca_name)

    ca_pem = _certificate_pem(ca_certificate)
    server_certificate_pem = _certificate_pem(server_certificate)
    server_key_pem = _key_pem(server_key)
    client_certificate_pem = _certificate_pem(client_certificate)
    client_key_pem = _key_pem(client_key)

    out = TLSMaterial()
    out.directory = directory
    out.ca_path = _write(directory, 'ca.pem', ca_pem)
    out.server_certificate_path = _write(directory, 'server-cert.pem', server_certificate_pem)
    out.server_key_path = _write(directory, 'server-key.pem', server_key_pem)
    out.client_certificate_path = _write(directory, 'client-cert.pem', client_certificate_pem)
    out.client_key_path = _write(directory, 'client-key.pem', client_key_pem)

    # The combined file is the single-PEM form requests accepts as one cert argument.
    out.client_combined_path = _write(directory, 'client-combined.pem', client_certificate_pem + client_key_pem)

    return out

# ################################################################################################################################
# ################################################################################################################################
