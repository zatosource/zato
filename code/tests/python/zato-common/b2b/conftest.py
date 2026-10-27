# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# lxml
import lxml.etree as etree

# pytest
import pytest

# Zato
from zato.common.test.b2b_interoperability import FixtureDirectory
from zato.common.test.b2b_pki import rsa_parties
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.b2b_pki import TestParties
    from zato.common.typing_ import any_
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# Local copies of the official XSDs
Schemas_Dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'schemas')

# The SOAP parts of the interoperability tests
Messages_Dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'messages')

_xsd = 'http://www.w3.org/2001/XMLSchema'

# The wildcard of eb:Acknowledgment that follows its ds:Reference elements.
_acknowledgment_wildcard = f"{{{_xsd}}}element[@name='Acknowledgment']/{{{_xsd}}}complexType/{{{_xsd}}}sequence/{{{_xsd}}}any"

# ################################################################################################################################
# ################################################################################################################################

class _LocalSchemaResolver(cast_('any_', etree.Resolver)):
    """ Resolves the absolute schemaLocation URLs inside the official XSDs to their local fixture copies,
    which keeps schema validation offline.
    """
    url_map = {
        'http://www.w3.org/2001/03/xml.xsd': 'xml.xsd',
        'http://www.w3.org/2001/xml.xsd': 'xml.xsd',
        'http://www.w3.org/2009/01/xml.xsd': 'xml.xsd',
        'http://www.w3.org/TR/xmldsig-core/xmldsig-core-schema.xsd': 'xmldsig-core-schema.xsd',
        'http://www.oasis-open.org/committees/ebxml-msg/schema/xlink.xsd': 'xlink.xsd',
        'http://www.oasis-open.org/committees/ebxml-msg/schema/envelope.xsd': 'soap-envelope-1.1.xsd',
    }

    def resolve(self, url:'any_', public_id:'any_', context:'any_'):
        if file_name := self.url_map.get(url):
            path = os.path.join(Schemas_Dir, file_name)
            return cast_('any_', self).resolve_filename(path, context)
        return None

# ################################################################################################################################

def _remove_acknowledgment_wildcard(document:'any_') -> 'None':
    """ The official message header schema violates the Unique Particle Attribution rule - in eb:Acknowledgment,
    a wildcard for any other namespace follows the ds:Reference elements and matches them too, and libxml2 rejects
    the schema. The wildcard is removed, which leaves every Acknowledgment without extension elements valid.
    """
    root = document.getroot()
    wildcard = root.find(_acknowledgment_wildcard)
    wildcard.getparent().remove(wildcard)

# ################################################################################################################################

def load_schema(file_name:'str', adjust:'any_'=None) -> 'any_':
    """ Loads one of the official XSDs with offline import resolution, adjusted in memory if it has to be.
    """
    parser = etree.XMLParser()
    parser.resolvers.add(_LocalSchemaResolver())

    path = os.path.join(Schemas_Dir, file_name)
    document = etree.parse(path, parser)

    if adjust:
        adjust(document)

    out = etree.XMLSchema(document)
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def cpa_schema() -> 'any_':
    """ The official CPP/A 2.0 schema.
    """
    out = load_schema('cpp-cpa-2_0.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def msg_header_schema() -> 'any_':
    """ The official ebMS 2.0 message header schema.
    """
    out = load_schema('msg-header-2_0.xsd', _remove_acknowledgment_wildcard)
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def soap11_schema() -> 'any_':
    """ The SOAP 1.1 envelope schema.
    """
    out = load_schema('soap-envelope-1.1.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def parties() -> 'TestParties':
    """ The certificate authority and the two parties the agreements of a session are between.
    """
    out = rsa_parties()
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def messages() -> 'FixtureDirectory':
    """ The SOAP parts that the interoperability tests exchange.
    """
    out = FixtureDirectory(Messages_Dir)
    return out

# ################################################################################################################################
# ################################################################################################################################
