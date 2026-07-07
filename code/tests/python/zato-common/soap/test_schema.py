# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# lxml
from lxml import etree

# pytest
import pytest

# Zato
from zato.common.soap.addressing import add_addressing, AddressingInfo
from zato.common.soap.common import FaultCode, SOAPVersion
from zato.common.soap.envelope import attach_body, build_envelope, build_fault, to_bytes
from zato.common.soap.message import SOAPMessage

# ################################################################################################################################
# ################################################################################################################################

# The official XSDs already live in the AS4 fixture tree - they are shared test-only oracles.
_schemas_dir = os.path.join(os.path.dirname(__file__), '..', 'as4', 'fixtures', 'schemas')

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
    }

    def resolve(self, url, public_id, context):
        if url in self.url_map:
            path = os.path.join(_schemas_dir, self.url_map[url])
            return self.resolve_filename(path, context)
        return None

# ################################################################################################################################

def _load_schema(file_name):
    """ Loads one of the official XSDs with offline import resolution.
    """
    parser = etree.XMLParser()
    parser.resolvers.add(_LocalSchemaResolver())

    document = etree.parse(os.path.join(_schemas_dir, file_name), parser)

    out = etree.XMLSchema(document)
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def soap11_schema():
    """ The official SOAP 1.1 envelope schema.
    """
    out = _load_schema('soap-envelope-1.1.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def soap12_schema():
    """ The official SOAP 1.2 envelope schema.
    """
    out = _load_schema('soap-envelope-1.2.xsd')
    return out

# ################################################################################################################################
# ################################################################################################################################

def _cdc_request():
    """ A CDC IIS submission message.
    """

    # Our response to produce
    out = SOAPMessage()

    out.namespace = 'urn:cdc:iisb:2011'
    out.username = 'MYUSERNAME'
    out.password = 'MYPASSWORD'
    out.hl7Message = 'MSH|^~\\&|MYEHR|MYCLINIC'

    return out

# ################################################################################################################################

def _reparse(envelope):
    out = etree.fromstring(to_bytes(envelope))
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSchemaConformance:
    """ Everything the library produces must validate against the official W3C schemas -
    proven here so that no schema machinery is ever needed at runtime.
    """

    def test_soap12_envelope_validates(self, soap12_schema):
        envelope = build_envelope(SOAPVersion.V12)
        _ = attach_body(envelope, _cdc_request(), 'submitSingleMessage')

        soap12_schema.assertValid(_reparse(envelope))

    def test_soap11_envelope_validates(self, soap11_schema):
        envelope = build_envelope(SOAPVersion.V11)
        _ = attach_body(envelope, _cdc_request(), 'submitSingleMessage')

        soap11_schema.assertValid(_reparse(envelope))

    def test_soap12_envelope_with_addressing_validates(self, soap12_schema):
        envelope = build_envelope(SOAPVersion.V12)

        info = AddressingInfo()
        info.action = 'urn:cdc:iisb:2011:submitSingleMessage'
        info.to = 'https://iis.example.gov/soap'

        add_addressing(envelope, info)
        _ = attach_body(envelope, _cdc_request(), 'submitSingleMessage')

        soap12_schema.assertValid(_reparse(envelope))

    def test_soap12_fault_validates(self, soap12_schema):
        envelope = build_fault(SOAPVersion.V12, FaultCode.Sender, 'Invalid credentials')

        soap12_schema.assertValid(_reparse(envelope))

    def test_soap11_fault_validates(self, soap11_schema):
        envelope = build_fault(SOAPVersion.V11, FaultCode.Receiver, 'Internal error')

        soap11_schema.assertValid(_reparse(envelope))

# ################################################################################################################################
# ################################################################################################################################
