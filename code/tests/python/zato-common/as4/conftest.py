# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

# cryptography
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.x509 import BasicConstraints, CertificateBuilder, Name, NameAttribute, random_serial_number
from cryptography.x509.oid import NameOID

# lxml
from lxml import etree

# pytest
import pytest

# Zato
from zato.common.util.xml_.keystore import Keystore, new_keystore

# ################################################################################################################################
# ################################################################################################################################

from zato.common.typing_ import cast_

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# Where the official XSDs and other fixtures live.
Fixtures_Dir = os.path.join(os.path.dirname(__file__), 'fixtures')
Schemas_Dir = os.path.join(Fixtures_Dir, 'schemas')

# RSA parameters for throwaway test keys.
_rsa_public_exponent = 65537
_rsa_key_size = 2048

# ################################################################################################################################
# ################################################################################################################################

def _make_name(common_name:'str') -> 'Name':
    out = Name([NameAttribute(NameOID.COMMON_NAME, common_name)])
    return out

# ################################################################################################################################

def make_certificate(
    common_name:'str',
    public_key:'any_',
    signer_name:'Name',
    signer_key:'any_',
    hash_algorithm:'any_',
    is_ca:'bool'=False,
    ) -> 'any_':
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

    out = builder.sign(signer_key, hash_algorithm)
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
def rsa_parties() -> 'TestParties':
    """ A CA plus a sender and a receiver with CA-issued RSA certificates - the eDelivery 1.x world.
    """
    ca_key = generate_private_key(_rsa_public_exponent, _rsa_key_size)
    ca_name = _make_name('as4-test-ca')

    ca_public_key = ca_key.public_key()
    ca_certificate = make_certificate('as4-test-ca', ca_public_key, ca_name, ca_key, SHA256(), is_ca=True)

    sender_key = generate_private_key(_rsa_public_exponent, _rsa_key_size)
    sender_public_key = sender_key.public_key()
    sender_certificate = make_certificate('as4-sender', sender_public_key, ca_name, ca_key, SHA256())

    receiver_key = generate_private_key(_rsa_public_exponent, _rsa_key_size)
    receiver_public_key = receiver_key.public_key()
    receiver_certificate = make_certificate('as4-receiver', receiver_public_key, ca_name, ca_key, SHA256())

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
def eddsa_parties() -> 'TestParties':
    """ A sender and a receiver for the eDelivery 2.0 world - Ed25519 signing keys
    and X25519 key agreement keys, all certificates issued by an Ed25519 CA.
    """
    ca_key = Ed25519PrivateKey.generate()
    ca_name = _make_name('as4-test-ca-ed')

    ca_public_key = ca_key.public_key()
    ca_certificate = make_certificate('as4-test-ca-ed', ca_public_key, ca_name, ca_key, None, is_ca=True)

    sender_sign_key = Ed25519PrivateKey.generate()
    sender_sign_public_key = sender_sign_key.public_key()
    sender_sign_certificate = make_certificate('as4-sender-ed', sender_sign_public_key, ca_name, ca_key, None)

    sender_key_exchange_key = X25519PrivateKey.generate()
    sender_key_exchange_public_key = sender_key_exchange_key.public_key()
    sender_key_exchange_certificate = make_certificate('as4-sender-x', sender_key_exchange_public_key, ca_name, ca_key, None)

    receiver_sign_key = Ed25519PrivateKey.generate()
    receiver_sign_public_key = receiver_sign_key.public_key()
    receiver_sign_certificate = make_certificate('as4-receiver-ed', receiver_sign_public_key, ca_name, ca_key, None)

    receiver_key_exchange_key = X25519PrivateKey.generate()
    receiver_key_exchange_public_key = receiver_key_exchange_key.public_key()
    receiver_key_exchange_certificate = make_certificate(
        'as4-receiver-x', receiver_key_exchange_public_key, ca_name, ca_key, None)

    sender = new_keystore()
    sender.signing_key = sender_sign_key
    sender.signing_certificate_chain = [sender_sign_certificate]
    sender.decryption_key = sender_key_exchange_key
    sender.peer_encryption_certificate = receiver_key_exchange_certificate
    sender.peer_signing_certificate = receiver_sign_certificate

    receiver = new_keystore()
    receiver.signing_key = receiver_sign_key
    receiver.signing_certificate_chain = [receiver_sign_certificate]
    receiver.decryption_key = receiver_key_exchange_key
    receiver.peer_encryption_certificate = sender_key_exchange_certificate
    receiver.peer_signing_certificate = sender_sign_certificate

    out = TestParties()
    out.ca_certificate = ca_certificate
    out.sender = sender
    out.receiver = receiver

    _ = sender_key_exchange_certificate
    return out

# ################################################################################################################################
# ################################################################################################################################

class _LocalSchemaResolver(etree.Resolver):
    """ Resolves the absolute schemaLocation URLs inside the official XSDs
    to their local fixture copies, keeping schema validation fully offline.
    """
    url_map = {
        'http://www.w3.org/2003/05/soap-envelope': 'soap-envelope-1.2.xsd',
        'http://schemas.xmlsoap.org/soap/envelope/': 'soap-envelope-1.1.xsd',
        'http://www.w3.org/2001/03/xml.xsd': 'xml.xsd',
        'http://www.w3.org/2001/xml.xsd': 'xml.xsd',
        'http://www.w3.org/2009/01/xml.xsd': 'xml.xsd',
        'http://www.w3.org/TR/xmldsig-core/xmldsig-core-schema.xsd': 'xmldsig-core-schema.xsd',
        'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd':
            'oasis-200401-wss-wssecurity-utility-1.0.xsd',
    }

    def resolve(self, url:'str', public_id:'any_', context:'any_') -> 'any_':
        if file_name := self.url_map.get(url):
            path = os.path.join(Schemas_Dir, file_name)

            # The lxml stubs do not expose resolve_filename on Resolver subclasses
            resolver = cast_('any_', self)
            out = resolver.resolve_filename(path, context)
        else:
            out = None

        return out

# ################################################################################################################################

def load_schema(file_name:'str', base_dir:'str'=Schemas_Dir) -> 'etree.XMLSchema':
    """ Loads one of the official XSDs with offline import resolution.
    """
    parser = etree.XMLParser()
    parser.resolvers.add(_LocalSchemaResolver())

    schema_path = os.path.join(base_dir, file_name)
    document = etree.parse(schema_path, parser)

    out = etree.XMLSchema(document)
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def ebms_schema() -> 'etree.XMLSchema':
    """ The official OASIS ebMS 3.0 header schema.
    """
    out = load_schema('ebms-header-3_0-200704.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def sbdh_schema() -> 'etree.XMLSchema':
    """ The official UN/CEFACT SBDH schema.
    """
    sbdh_dir = os.path.join(Schemas_Dir, 'sbdh')

    out = load_schema('StandardBusinessDocumentHeader.xsd', sbdh_dir)
    return out

# ################################################################################################################################
# ################################################################################################################################
