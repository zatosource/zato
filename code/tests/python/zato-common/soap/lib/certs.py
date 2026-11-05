# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ipaddress
import os
import ssl
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256

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
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

general_name_list = list[x509.GeneralName]
general_name_list_none = optional[general_name_list]

# ################################################################################################################################
# ################################################################################################################################

_rsa_public_exponent = 65537
_rsa_key_size = 2048

# What a file is written under before it is renamed into place - a name the TLS material listener ignores
_temporary_suffix = '.tmp'

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

    # The SHA-256 fingerprint of the current client certificate, in lowercase hex.
    client_fingerprint: 'str'

    # The CA's own key and name, with which a replacement client certificate is issued.
    ca_key: 'RSAPrivateKey'
    ca_name: 'x509.Name'

    # The directory holding all of the above, removed on cleanup when it is a temporary one.
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

def get_certificate_fingerprint(certificate_der:'bytes') -> 'str':
    """ Returns the SHA-256 fingerprint of a DER-encoded certificate, in lowercase hex.
    """
    out = sha256(certificate_der).hexdigest()
    return out

# ################################################################################################################################

def get_peer_fingerprint(connection:'any_') -> 'str':
    """ Returns the SHA-256 fingerprint of the certificate that the peer of a server-side
    connection presented, or an empty string when the connection is not TLS or no certificate was presented.
    """
    out = ''

    if isinstance(connection, ssl.SSLSocket):
        if certificate_der := connection.getpeercert(binary_form=True):
            out = get_certificate_fingerprint(certificate_der)

    return out

# ################################################################################################################################

def _write_client_material(material:'TLSMaterial', needs_rename:'bool') -> 'None':
    """ Issues a client certificate and key under the material's CA and writes them to the material's client paths,
    either in place or to a temporary name first, which is then renamed into place.
    """
    client_key = _new_key()
    client_certificate = _leaf_certificate('soap-test-client', client_key.public_key(), material.ca_key, material.ca_name)

    client_certificate_pem = _certificate_pem(client_certificate)
    client_key_pem = _key_pem(client_key)
    client_combined_pem = client_certificate_pem + client_key_pem

    # The key is written first, so that once the certificate is there, its key is too ..
    files = [
        (material.client_key_path, client_key_pem),
        (material.client_certificate_path, client_certificate_pem),
        (material.client_combined_path, client_combined_pem),
    ]

    for path, data in files:

        # .. a renewal tool writes each file in full under another name and renames it over the current one ..
        if needs_rename:
            temporary_path = path + _temporary_suffix
            _ = _write(os.path.dirname(temporary_path), os.path.basename(temporary_path), data)
            os.replace(temporary_path, path)

        # .. while an administrator may overwrite it where it is.
        else:
            _ = _write(os.path.dirname(path), os.path.basename(path), data)

    certificate_der = client_certificate.public_bytes(Encoding.DER)
    material.client_fingerprint = get_certificate_fingerprint(certificate_der)

# ################################################################################################################################

def reissue_client_material(material:'TLSMaterial', needs_rename:'bool') -> 'str':
    """ Issues a new client certificate and key under the same CA, writes them to the same paths
    and returns the new certificate's fingerprint.
    """
    _write_client_material(material, needs_rename)

    out = material.client_fingerprint
    return out

# ################################################################################################################################

def build_tls_material(host:'str', directory:'str'='') -> 'TLSMaterial':
    """ Builds a CA plus a server certificate for the given host and a client certificate,
    writing every artifact to the given directory, or to a fresh temporary one when none is given.
    The server certificate carries the host both as a DNS name and, for numeric hosts,
    as an IP address, so TLS validation passes.
    """
    if not directory:
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

    ca_pem = _certificate_pem(ca_certificate)
    server_certificate_pem = _certificate_pem(server_certificate)
    server_key_pem = _key_pem(server_key)

    out = TLSMaterial()
    out.directory = directory
    out.ca_key = ca_key
    out.ca_name = ca_name
    out.ca_path = _write(directory, 'ca.pem', ca_pem)
    out.server_certificate_path = _write(directory, 'server-cert.pem', server_certificate_pem)
    out.server_key_path = _write(directory, 'server-key.pem', server_key_pem)
    out.client_certificate_path = os.path.join(directory, 'client-cert.pem')
    out.client_key_path = os.path.join(directory, 'client-key.pem')

    # The combined file is the single-PEM form requests accepts as one cert argument.
    out.client_combined_path = os.path.join(directory, 'client-combined.pem')

    _write_client_material(out, needs_rename=False)

    return out

# ################################################################################################################################
# ################################################################################################################################
