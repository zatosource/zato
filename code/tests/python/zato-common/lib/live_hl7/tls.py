# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The certificates of one live suite - an authority of its own and the identities it issues, each written in
# every form a party to the suite reads, PEM together and apart, PKCS12 key store and trust store.

# stdlib
import ipaddress
import os
from datetime import timedelta
from typing import NamedTuple

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization.pkcs12 import PKCS12Certificate, serialize_java_truststore
from cryptography.hazmat.primitives.serialization.pkcs12 import serialize_key_and_certificates
from cryptography.x509.oid import NameOID

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# How long the throwaway certificates of one run are valid for - a run lasts minutes, a day leaves room
# for a clock that is a little off
_Validity_Days = 1

# Large enough for a handshake to be realistic, small enough that a handful of keys does not slow a suite down
_Key_Size = 2048

# Nothing other than the user the suite runs as ever has to read the material
_File_Mode = 0o600

# What every subject here says it belongs to
_Organization_Name = 'Zato HL7 Live Tests'

# How many bits the password protecting a key store is made of - written in hexadecimal so nothing in it
# has to be escaped by whichever system reads the store
_Store_Password_Bits = 128

# The alias a key and its certificate are stored under in a key store
_Store_Alias = 'zato-hl7-live'

# ################################################################################################################################
# ################################################################################################################################

class Identity(NamedTuple):
    """ One party's certificate and key, in every form a party reads them in.
    """

    # The name the certificate is issued to
    common_name: 'str'

    # The certificate and the key, apart
    cert_path: 'str'
    key_path: 'str'

    # The certificate followed by the key in one file, as HAProxy reads them
    combined_pem_path: 'str'

    # The key, the certificate and the chain in one PKCS12 store, as a Java system reads them
    keystore_path: 'str'

    # What the store is protected with
    store_password: 'str'

# ################################################################################################################################
# ################################################################################################################################

def _name(common_name:'str') -> 'x509.Name':
    out = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, _Organization_Name),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    return out

# ################################################################################################################################

def _write(path:'str', data:'bytes') -> 'None':
    with open(path, 'wb') as file_handle:
        _ = file_handle.write(data)

    os.chmod(path, _File_Mode)

# ################################################################################################################################

def _cert_pem(certificate:'x509.Certificate') -> 'bytes':
    out = certificate.public_bytes(serialization.Encoding.PEM)
    return out

# ################################################################################################################################

def _key_pem(key:'RSAPrivateKey') -> 'bytes':
    """ The key unencrypted, since it lives for the length of one run in a directory of that run's own.
    """
    out = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )

    return out

# ################################################################################################################################

def _new_key() -> 'RSAPrivateKey':
    out = rsa.generate_private_key(public_exponent=65537, key_size=_Key_Size)
    return out

# ################################################################################################################################

def _alt_names(host_names:'strlist') -> 'x509.SubjectAlternativeName':
    """ The names a certificate may be presented for - each given name as a DNS name, or as an address
    when it is one.
    """
    names:'list[x509.GeneralName]' = []

    for host_name in host_names:
        try:
            address = ipaddress.ip_address(host_name)
        except ValueError:
            names.append(x509.DNSName(host_name))
        else:
            names.append(x509.IPAddress(address))

    out = x509.SubjectAlternativeName(names)
    return out

# ################################################################################################################################
# ################################################################################################################################

class Authority:
    """ The certificate authority of one suite - everything it issues chains up to it, and what it wrote
    is under its directory.
    """

    def __init__(self, directory:'str', common_name:'str') -> 'None':
        self.directory = directory
        self.common_name = common_name

        os.makedirs(directory, exist_ok=True)

        self.key = _new_key()
        self.name = _name(common_name)

        now = utcnow()

        builder = x509.CertificateBuilder(). \
            subject_name(self.name). \
            issuer_name(self.name). \
            public_key(self.key.public_key()). \
            serial_number(x509.random_serial_number()). \
            not_valid_before(now). \
            not_valid_after(now + timedelta(days=_Validity_Days)). \
            add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)

        self.certificate = builder.sign(self.key, hashes.SHA256())

        # The authority in PEM, which is what everything other than a Java system trusts it through ..
        self.ca_cert_path = os.path.join(directory, 'ca.pem')
        _write(self.ca_cert_path, _cert_pem(self.certificate))

        # .. and in a trust store of the kind keytool writes, which is what a Java system trusts it through.
        self.truststore_password = CryptoManager.generate_hex_string(_Store_Password_Bits)
        self.truststore_path = os.path.join(directory, 'truststore.p12')

        truststore = serialize_java_truststore(
            [PKCS12Certificate(self.certificate, _Store_Alias.encode('utf8'))],
            serialization.BestAvailableEncryption(self.truststore_password.encode('utf8')),
        )

        _write(self.truststore_path, truststore)

# ################################################################################################################################

    def _sign(self, common_name:'str', key:'RSAPrivateKey', host_names:'strlist') -> 'x509.Certificate':
        now = utcnow()

        builder = x509.CertificateBuilder(). \
            subject_name(_name(common_name)). \
            issuer_name(self.name). \
            public_key(key.public_key()). \
            serial_number(x509.random_serial_number()). \
            not_valid_before(now). \
            not_valid_after(now + timedelta(days=_Validity_Days)). \
            add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)

        if host_names:
            builder = builder.add_extension(_alt_names(host_names), critical=False)

        out = builder.sign(self.key, hashes.SHA256())
        return out

# ################################################################################################################################

    def issue(self, label:'str', common_name:'str', *, host_names:'strlist | None'=None) -> 'Identity':
        """ One identity, its files named after the label. A server's identity carries the names it is
        connected by, a client's carries none.
        """
        if host_names is None:
            host_names = []

        key = _new_key()
        certificate = self._sign(common_name, key, host_names)

        cert_pem = _cert_pem(certificate)
        key_pem = _key_pem(key)

        store_password = CryptoManager.generate_hex_string(_Store_Password_Bits)

        keystore = serialize_key_and_certificates(
            _Store_Alias.encode('utf8'),
            key,
            certificate,
            [self.certificate],
            serialization.BestAvailableEncryption(store_password.encode('utf8')),
        )

        out = Identity(
            common_name=common_name,
            cert_path=os.path.join(self.directory, f'{label}-cert.pem'),
            key_path=os.path.join(self.directory, f'{label}-key.pem'),
            combined_pem_path=os.path.join(self.directory, f'{label}.pem'),
            keystore_path=os.path.join(self.directory, f'{label}.p12'),
            store_password=store_password,
        )

        _write(out.cert_path, cert_pem)
        _write(out.key_path, key_pem)
        _write(out.combined_pem_path, cert_pem + key_pem)
        _write(out.keystore_path, keystore)

        return out

# ################################################################################################################################
# ################################################################################################################################

def new_stranger(directory:'str', label:'str', common_name:'str') -> 'Identity':
    """ An identity no authority of the suite issued - what a party that is not to be trusted presents.
    """
    stranger = Authority(os.path.join(directory, label), f'{common_name} Authority')

    out = stranger.issue(label, common_name)
    return out

# ################################################################################################################################
# ################################################################################################################################
