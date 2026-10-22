# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

# cryptography
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat
from cryptography.x509 import BasicConstraints, CertificateBuilder, Name, NameAttribute, random_serial_number
from cryptography.x509.oid import NameOID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
    from cryptography.x509 import Certificate
    from zato.common.typing_ import any_
    any_ = any_
    Certificate = Certificate
    RSAPrivateKey = RSAPrivateKey

# ################################################################################################################################
# ################################################################################################################################

# RSA parameters for test keys.
_rsa_public_exponent = 65537
_rsa_key_size = 2048

# For how long a test certificate is valid unless a test asks for another period.
_default_days_valid = 365

# How far back a test certificate's validity begins, so that clock differences between hosts do not matter.
_backdate_days = 1

# The common names of the test parties.
Common_Name_CA = 'b2b-test-ca'
Common_Name_Unrelated_CA = 'b2b-unrelated-ca'
Common_Name_Sender = 'b2b-sender'
Common_Name_Receiver = 'b2b-receiver'

# The size of the RSA keys that are too small to sign with.
Weak_RSA_Key_Size = 1024

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class TestParty:
    """ One party's private key with its certificate.
    """
    __test__ = False

    key: 'RSAPrivateKey'
    certificate: 'Certificate'

# ################################################################################################################################

@dataclass(init=False)
class TestParties:
    """ Two parties with certificates issued by one CA, for exchanges in both directions.
    """
    __test__ = False

    ca_key: 'RSAPrivateKey'
    ca_certificate: 'Certificate'
    sender: 'TestParty'
    receiver: 'TestParty'

# ################################################################################################################################
# ################################################################################################################################

def make_name(common_name:'str') -> 'Name':
    attribute = NameAttribute(NameOID.COMMON_NAME, common_name)
    out = Name([attribute])

    return out

# ################################################################################################################################

def make_key(key_size:'int'=_rsa_key_size) -> 'RSAPrivateKey':
    out = generate_private_key(_rsa_public_exponent, key_size)
    return out

# ################################################################################################################################

def make_certificate(
    common_name:'str',
    public_key:'any_',
    signer_name:'Name',
    signer_key:'any_',
    *,
    is_ca:'bool'=False,
    not_before:'datetime | None'=None,
    not_after:'datetime | None'=None,
    ) -> 'Certificate':
    """ Issues a test certificate, valid around the current moment unless its dates are given.
    """
    now = datetime.now(timezone.utc)

    if not_before is None:
        not_before = now - timedelta(days=_backdate_days)

    if not_after is None:
        not_after = now + timedelta(days=_default_days_valid)

    subject_name = make_name(common_name)
    serial_number = random_serial_number()
    basic_constraints = BasicConstraints(ca=is_ca, path_length=None)
    hash_algorithm = SHA256()

    builder = CertificateBuilder()
    builder = builder.subject_name(subject_name)
    builder = builder.issuer_name(signer_name)
    builder = builder.public_key(public_key)
    builder = builder.serial_number(serial_number)
    builder = builder.not_valid_before(not_before)
    builder = builder.not_valid_after(not_after)
    builder = builder.add_extension(basic_constraints, critical=True)

    out = builder.sign(signer_key, hash_algorithm)
    return out

# ################################################################################################################################

def make_ca(common_name:'str') -> 'TestParty':
    """ Issues a self-signed CA certificate with its key.
    """
    key = make_key()
    name = make_name(common_name)
    public_key = key.public_key()

    out = TestParty()
    out.key = key
    out.certificate = make_certificate(common_name, public_key, name, key, is_ca=True)

    return out

# ################################################################################################################################

def issue_party(common_name:'str', ca:'TestParty', key_size:'int'=_rsa_key_size) -> 'TestParty':
    """ Issues a key of the given size with a certificate signed by the given CA.
    """
    key = make_key(key_size)
    public_key = key.public_key()
    ca_name = ca.certificate.subject

    out = TestParty()
    out.key = key
    out.certificate = make_certificate(common_name, public_key, ca_name, ca.key)

    return out

# ################################################################################################################################

def rsa_parties() -> 'TestParties':
    """ A CA with a sender and a receiver whose RSA certificates it issued.
    """
    ca = make_ca(Common_Name_CA)

    out = TestParties()
    out.ca_key = ca.key
    out.ca_certificate = ca.certificate
    out.sender = issue_party(Common_Name_Sender, ca)
    out.receiver = issue_party(Common_Name_Receiver, ca)

    return out

# ################################################################################################################################

def ca_party(parties:'TestParties') -> 'TestParty':
    """ Returns the CA of the test parties, for issuing further certificates from it.
    """
    out = TestParty()
    out.key = parties.ca_key
    out.certificate = parties.ca_certificate

    return out

# ################################################################################################################################

def unrelated_ca_certificate() -> 'Certificate':
    """ A CA certificate that issued none of the certificates the test parties use.
    """
    ca = make_ca(Common_Name_Unrelated_CA)

    out = ca.certificate
    return out

# ################################################################################################################################

def make_dated_pair(common_name:'str', not_before:'datetime', not_after:'datetime') -> 'TestParty':
    """ Issues a key with a self-signed certificate whose validity dates are given.
    """
    key = make_key()
    name = make_name(common_name)
    public_key = key.public_key()

    out = TestParty()
    out.key = key
    out.certificate = make_certificate(common_name, public_key, name, key, not_before=not_before, not_after=not_after)

    return out

# ################################################################################################################################

def certificate_pem(certificate:'Certificate') -> 'bytes':
    out = certificate.public_bytes(Encoding.PEM)
    return out

# ################################################################################################################################

def private_key_pem(key:'RSAPrivateKey') -> 'bytes':
    encryption = NoEncryption()

    out = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, encryption)
    return out

# ################################################################################################################################
# ################################################################################################################################
