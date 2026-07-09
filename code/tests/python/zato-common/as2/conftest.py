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
from cryptography.x509 import BasicConstraints, CertificateBuilder, Name, NameAttribute, random_serial_number
from cryptography.x509.oid import NameOID

# pytest
import pytest

# Zato
from zato.common.util.xml_.keystore import Keystore, new_keystore

# ################################################################################################################################
# ################################################################################################################################

# RSA parameters for throwaway test keys.
_rsa_public_exponent = 65537
_rsa_key_size = 2048

# ################################################################################################################################
# ################################################################################################################################

def _make_name(common_name):
    out = Name([NameAttribute(NameOID.COMMON_NAME, common_name)])
    return out

# ################################################################################################################################

def make_certificate(common_name, public_key, signer_name, signer_key, is_ca=False):
    """ Issues a test certificate valid around the current moment.
    """
    now = datetime.now(timezone.utc)

    builder = CertificateBuilder()
    builder = builder.subject_name(_make_name(common_name))
    builder = builder.issuer_name(signer_name)
    builder = builder.public_key(public_key)
    builder = builder.serial_number(random_serial_number())
    builder = builder.not_valid_before(now - timedelta(days=1))
    builder = builder.not_valid_after(now + timedelta(days=365))
    builder = builder.add_extension(BasicConstraints(ca=is_ca, path_length=None), critical=True)

    out = builder.sign(signer_key, SHA256())
    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class TestParties:
    """ Two parties with everything needed for exchanges in both directions, plus their CA.
    """
    __test__ = False

    ca_certificate: 'object'
    sender: 'Keystore'
    receiver: 'Keystore'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def parties():
    """ A CA plus a sender and a receiver with CA-issued RSA certificates.
    """
    ca_key = generate_private_key(_rsa_public_exponent, _rsa_key_size)
    ca_name = _make_name('as2-test-ca')
    ca_certificate = make_certificate('as2-test-ca', ca_key.public_key(), ca_name, ca_key, is_ca=True)

    sender_key = generate_private_key(_rsa_public_exponent, _rsa_key_size)
    sender_certificate = make_certificate('as2-sender', sender_key.public_key(), ca_name, ca_key)

    receiver_key = generate_private_key(_rsa_public_exponent, _rsa_key_size)
    receiver_certificate = make_certificate('as2-receiver', receiver_key.public_key(), ca_name, ca_key)

    sender = new_keystore()
    sender.signing_key = sender_key
    sender.signing_certificate_chain = [sender_certificate]
    sender.decryption_key = sender_key
    sender.peer_encryption_certificate = receiver_certificate
    sender.peer_signing_certificate = receiver_certificate

    receiver = new_keystore()
    receiver.signing_key = receiver_key
    receiver.signing_certificate_chain = [receiver_certificate]
    receiver.decryption_key = receiver_key
    receiver.peer_encryption_certificate = sender_certificate
    receiver.peer_signing_certificate = sender_certificate

    out = TestParties()
    out.ca_certificate = ca_certificate
    out.sender = sender
    out.receiver = receiver

    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def unrelated_ca_certificate():
    """ A CA that issued none of the certificates the parties use - for negative trust tests.
    """
    ca_key = generate_private_key(_rsa_public_exponent, _rsa_key_size)
    ca_name = _make_name('as2-unrelated-ca')

    out = make_certificate('as2-unrelated-ca', ca_key.public_key(), ca_name, ca_key, is_ca=True)
    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RotatedPair:
    """ A fresh key with its self-signed certificate - what a certificate rotation introduces.
    """
    key: 'object'
    certificate: 'object'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def make_rotated_pair():
    """ A factory issuing fresh keys with self-signed certificates for rotation tests -
    the rotation lists pin exact certificates, so no CA needs to stand behind them.
    """
    def _make(common_name):

        key = generate_private_key(_rsa_public_exponent, _rsa_key_size)
        name = _make_name(common_name)
        certificate = make_certificate(common_name, key.public_key(), name, key)

        out = RotatedPair()
        out.key = key
        out.certificate = certificate

        return out

    return _make

# ################################################################################################################################
# ################################################################################################################################
