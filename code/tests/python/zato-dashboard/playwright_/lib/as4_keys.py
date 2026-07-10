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

# RSA parameters for throwaway test keys
_rsa_public_exponent = 65537
_rsa_key_size = 2048

# How long the throwaway certificates stay valid
_default_validity_days = 365

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PartyPEM:
    """ One party's key material, all in PEM, ready to be pasted into the Dashboard forms.
    """
    key: 'str'
    certificate: 'str'

# ################################################################################################################################
# ################################################################################################################################

def _make_self_signed(common_name:'str', validity_days:'int'=_default_validity_days) -> 'PartyPEM':
    """ Generates one throwaway RSA key with a self-signed certificate, both as PEM text.
    """
    key = generate_private_key(_rsa_public_exponent, _rsa_key_size)
    name = Name([NameAttribute(NameOID.COMMON_NAME, common_name)])
    now = datetime.now(timezone.utc)

    builder = CertificateBuilder()
    builder = builder.subject_name(name)
    builder = builder.issuer_name(name)
    builder = builder.public_key(key.public_key())
    builder = builder.serial_number(random_serial_number())
    builder = builder.not_valid_before(now - timedelta(days=1))
    builder = builder.not_valid_after(now + timedelta(days=validity_days))
    builder = builder.add_extension(BasicConstraints(ca=False, path_length=None), critical=True)

    certificate = builder.sign(key, SHA256())

    out = PartyPEM()
    out.key = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode('utf8')
    out.certificate = certificate.public_bytes(Encoding.PEM).decode('utf8')

    return out

# ################################################################################################################################

def new_test_parties() -> 'tuple[PartyPEM, PartyPEM]':
    """ Two parties for exchanges in both directions - the sender and the receiver.
    """
    sender = _make_self_signed('as4-test-sender')
    receiver = _make_self_signed('as4-test-receiver')

    out = (sender, receiver)
    return out

# ################################################################################################################################

def new_party(common_name:'str', validity_days:'int'=_default_validity_days) -> 'PartyPEM':
    """ One party with a certificate of the given validity - a short one exercises
    the expiry warnings the Dashboard shows.
    """
    out = _make_self_signed(common_name, validity_days)
    return out

# ################################################################################################################################
# ################################################################################################################################
