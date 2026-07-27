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
from cryptography.hazmat.primitives.serialization.pkcs12 import serialize_key_and_certificates
from cryptography.x509.oid import NameOID

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

    RSAPrivateKey = RSAPrivateKey
    RSAPublicKey = RSAPublicKey

# ################################################################################################################################
# ################################################################################################################################

# How long the throwaway certificates of one test run are valid for. A run lasts minutes, so a day
# leaves room for a clock that is a little off without ever outliving the temporary directory.
_Validity_Days = 1

# The key size for every throwaway key here - large enough for a TLS handshake to be realistic
# and small enough that generating four of them does not slow the suite's startup down.
_Key_Size = 2048

# HAProxy runs as the user the test runs as, so the material only ever has to be readable by it
_File_Mode = 0o600

# What every subject here says it belongs to
_Organization_Name = 'Zato MLLP Language Tests'

# The common name of the certificate authority the whole test run chains up to
_CA_Common_Name = 'Zato MLLP Language Test CA'

# The name HAProxy's certificate is issued to, matching the address the clients connect to
_Server_Common_Name = 'localhost'

# The common name the Java client's certificate carries. The mTLS channel accepts exactly this
# name, because the common name is the only part of the certificate that reaches the listener.
Java_Client_Common_Name = 'zato-test-java-client'

# The subject distinguished name the enmasse security definition holds, which is where the
# channel takes the accepted common name from.
Java_Client_Subject_DN = f'CN={Java_Client_Common_Name},O={_Organization_Name}'

# The alias the client's own key and certificate are stored under in its keystore
_Java_Keystore_Alias = 'zato-mllp-client'

# How many bits the password protecting the keystore is made of. It is written in hexadecimal so
# that nothing in it has to be escaped by whichever language reads the store.
_Store_Password_Bits = 256

# ################################################################################################################################
# ################################################################################################################################

class TestCertificates(NamedTuple):
    """ Every piece of certificate material one test run needs, already written to disk.
    """

    # Where all of it lives
    directory: 'str'

    # The certificate authority in PEM form. HAProxy verifies client certificates against it and
    # every client trusts what HAProxy presents because of it, so one file serves both ends.
    ca_cert_path: 'str'

    # The server certificate and its key in one PEM file, which is the form HAProxy's crt wants
    haproxy_pem_path: 'str'

    # The Java client's own key and certificate, in the form a Java keystore is loaded from
    java_keystore_path: 'str'

    # The password the Java keystore is protected with
    java_store_password: 'str'

# ################################################################################################################################
# ################################################################################################################################

def _build_name(common_name:'str') -> 'x509.Name':
    """ Builds an X.509 subject out of a common name.
    """
    out = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, _Organization_Name),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    return out

# ################################################################################################################################

def _write_bytes(path:'str', data:'bytes') -> 'None':
    """ Writes one piece of certificate material and locks its permissions down.
    """
    with open(path, 'wb') as file_handle:
        _ = file_handle.write(data)

    os.chmod(path, _File_Mode)

# ################################################################################################################################

def _to_pem(certificate:'x509.Certificate') -> 'bytes':
    """ Renders one certificate in the PEM form every file here is written in.
    """
    out = certificate.public_bytes(serialization.Encoding.PEM)
    return out

# ################################################################################################################################

def _sign(
    common_name:'str',
    public_key:'RSAPublicKey',
    issuer_name:'x509.Name',
    issuer_key:'RSAPrivateKey',
    extension:'x509.ExtensionType | None',
    is_ca:'bool',
) -> 'x509.Certificate':
    """ Issues one certificate under the given issuer, which for the authority itself is the
    authority's own name and key, making it self-signed.
    """
    now = utcnow()

    builder = x509.CertificateBuilder(). \
        subject_name(_build_name(common_name)). \
        issuer_name(issuer_name). \
        public_key(public_key). \
        serial_number(x509.random_serial_number()). \
        not_valid_before(now). \
        not_valid_after(now + timedelta(days=_Validity_Days))

    # Only the authority is allowed to issue anything further down the chain
    if is_ca:
        builder = builder.add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
    else:
        builder = builder.add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)

    # The server certificate carries the addresses it may be presented for
    if extension:
        builder = builder.add_extension(extension, critical=False)

    out = builder.sign(issuer_key, hashes.SHA256())
    return out

# ################################################################################################################################

def generate_certificates(directory:'str') -> 'TestCertificates':
    """ Generates everything one test run needs - an authority, the certificate HAProxy presents
    on its TLS bind and the identity the Java client presents back to it.
    """
    os.makedirs(directory, exist_ok=True)

    # The authority both of the other certificates chain up to ..
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=_Key_Size)
    ca_name = _build_name(_CA_Common_Name)
    ca_cert = _sign(_CA_Common_Name, ca_key.public_key(), ca_name, ca_key, None, is_ca=True)

    # .. what HAProxy presents, covering both names a local client may connect by ..
    server_key = rsa.generate_private_key(public_exponent=65537, key_size=_Key_Size)

    server_alt_names = x509.SubjectAlternativeName([
        x509.DNSName('localhost'),
        x509.IPAddress(ipaddress.ip_address('127.0.0.1')),
    ])

    server_cert = _sign(_Server_Common_Name, server_key.public_key(), ca_name, ca_key, server_alt_names, is_ca=False)

    # .. and the identity the Java client presents, whose common name is what the channel accepts.
    client_key = rsa.generate_private_key(public_exponent=65537, key_size=_Key_Size)
    client_cert = _sign(Java_Client_Common_Name, client_key.public_key(), ca_name, ca_key, None, is_ca=False)

    java_store_password = CryptoManager.generate_hex_string(_Store_Password_Bits)
    password_bytes = java_store_password.encode('utf8')

    # A Java keystore holds the key, the certificate and the chain together, protected by a password.
    # What the client trusts is not kept here - it reads the authority out of the PEM file instead,
    # because a PKCS12 written by anything other than keytool carries no trusted certificate entries.
    java_keystore = serialize_key_and_certificates(
        _Java_Keystore_Alias.encode('utf8'),
        client_key,
        client_cert,
        [ca_cert],
        serialization.BestAvailableEncryption(password_bytes),
    )

    out = TestCertificates(
        directory=directory,
        ca_cert_path=os.path.join(directory, 'ca.pem'),
        haproxy_pem_path=os.path.join(directory, 'haproxy.pem'),
        java_keystore_path=os.path.join(directory, 'java-client.p12'),
        java_store_password=java_store_password,
    )

    _write_bytes(out.ca_cert_path, _to_pem(ca_cert))

    # HAProxy reads the certificate and its key out of one file, in that order
    server_key_pem = server_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )

    _write_bytes(out.haproxy_pem_path, _to_pem(server_cert) + server_key_pem)

    _write_bytes(out.java_keystore_path, java_keystore)

    return out

# ################################################################################################################################
# ################################################################################################################################
