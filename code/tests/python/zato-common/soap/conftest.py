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
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
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

# The official XSDs live in the AS4 fixture tree and are shared by both suites.
Schemas_Dir = os.path.join(os.path.dirname(__file__), '..', 'as4', 'fixtures', 'schemas')

# RSA parameters for throwaway test keys.
_rsa_public_exponent = 65537
_rsa_key_size = 2048

# ################################################################################################################################
# ################################################################################################################################

class _LocalSchemaResolver(etree.Resolver):
    """ Resolves the absolute schemaLocation URLs inside the official XSDs
    to their local fixture copies, keeping schema validation fully offline.
    """
    url_map = {
        'http://www.w3.org/2001/03/xml.xsd': 'xml.xsd',
        'http://www.w3.org/2001/xml.xsd': 'xml.xsd',
        'http://www.w3.org/2009/01/xml.xsd': 'xml.xsd',
        'http://www.w3.org/TR/xmldsig-core/xmldsig-core-schema.xsd': 'xmldsig-core-schema.xsd',
        'http://www.w3.org/TR/2002/REC-xmldsig-core-20020212/xmldsig-core-schema.xsd': 'xmldsig-core-schema.xsd',
        'http://www.w3.org/TR/2002/REC-xmlenc-core-20021210/xenc-schema.xsd': 'xenc-schema.xsd',
        'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd':
            'oasis-200401-wss-wssecurity-utility-1.0.xsd',
        'http://www.oasis-open.org/committees/ebxml-msg/schema/xlink.xsd': 'xlink.xsd',
        'http://www.oasis-open.org/committees/ebxml-msg/schema/envelope.xsd': 'soap-envelope-1.1.xsd',
    }

    def resolve(self, url, public_id, context):
        if url in self.url_map:
            path = os.path.join(Schemas_Dir, self.url_map[url])
            return self.resolve_filename(path, context)
        return None

# ################################################################################################################################

def load_schema(file_name):
    """ Loads one of the official XSDs with offline import resolution.
    """
    parser = etree.XMLParser()
    parser.resolvers.add(_LocalSchemaResolver())

    document = etree.parse(os.path.join(Schemas_Dir, file_name), parser)

    out = etree.XMLSchema(document)
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def soap11_schema():
    """ The official SOAP 1.1 envelope schema.
    """
    out = load_schema('soap-envelope-1.1.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def soap12_schema():
    """ The official SOAP 1.2 envelope schema.
    """
    out = load_schema('soap-envelope-1.2.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def wsse_schema():
    """ The official OASIS WS-Security 1.0 secext schema - it imports the wsu
    and XML Signature schemas, so wsse:Security contents validate strictly too.
    """
    out = load_schema('oasis-200401-wss-wssecurity-secext-1.0.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def wsu_schema():
    """ The official OASIS WS-Security 1.0 utility schema - wsu:Timestamp and friends.
    """
    out = load_schema('oasis-200401-wss-wssecurity-utility-1.0.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def dsig_schema():
    """ The official W3C XML Signature schema.
    """
    out = load_schema('xmldsig-core-schema.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def xenc_schema():
    """ The official W3C XML Encryption schema.
    """
    out = load_schema('xenc-schema.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def xenc11_schema():
    """ The official W3C XML Encryption 1.1 schema - it imports the 1.0 one,
    so elements mixing both namespaces (xenc11:MGF inside xenc:EncryptionMethod)
    validate strictly against this schema set.
    """
    out = load_schema('xenc-schema-11.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def saml_schema():
    """ The official OASIS SAML 2.0 assertion schema.
    """
    out = load_schema('saml-schema-assertion-2.0.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def wsa_schema():
    """ The official W3C WS-Addressing 1.0 schema.
    """
    out = load_schema('ws-addr.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def xop_schema():
    """ The official W3C XOP (XML-binary Optimized Packaging) schema.
    """
    out = load_schema('xop-include.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def ebms2_schema():
    """ The official OASIS ebXML Message Service 2.0 schema - it imports
    the SOAP 1.1 envelope, XLink and XML Signature schemas.

    The Acknowledgment type in the official file has a ds:Reference particle
    followed by a ##other wildcard, which violates the XSD 1.0 deterministic
    content model rule, so libxml2 refuses to compile the schema as published.
    The fixture stays byte-for-byte official and the offending particle is
    dropped here at load time instead - nothing in the suite produces
    eb:Acknowledgment, so no validated element is affected.
    """
    parser = etree.XMLParser()
    parser.resolvers.add(_LocalSchemaResolver())

    document = etree.parse(os.path.join(Schemas_Dir, 'msg-header-2_0.xsd'), parser)

    for element in document.iter('{http://www.w3.org/2001/XMLSchema}element'):
        if element.get('ref') == 'ds:Reference':
            element.getparent().remove(element)

    out = etree.XMLSchema(document)
    return out

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
    """ A CA plus a sender and a receiver with CA-issued RSA certificates -
    the world WS-Security X.509 exchanges live in.
    """
    ca_key = generate_private_key(_rsa_public_exponent, _rsa_key_size)
    ca_name = _make_name('soap-test-ca')
    ca_certificate = make_certificate('soap-test-ca', ca_key.public_key(), ca_name, ca_key, is_ca=True)

    sender_key = generate_private_key(_rsa_public_exponent, _rsa_key_size)
    sender_certificate = make_certificate('soap-sender', sender_key.public_key(), ca_name, ca_key)

    receiver_key = generate_private_key(_rsa_public_exponent, _rsa_key_size)
    receiver_certificate = make_certificate('soap-receiver', receiver_key.public_key(), ca_name, ca_key)

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
# ################################################################################################################################
