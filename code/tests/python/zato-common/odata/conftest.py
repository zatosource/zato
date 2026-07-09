# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The test server library uses flat imports, the way the soap suite's lib does,
# and the TLS material builder is shared with the soap suite.
_here = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(_here, 'lib'))
sys.path.insert(0, os.path.join(_here, '..', 'soap', 'lib'))

# lxml
from lxml import etree

# pytest
import pytest

# ################################################################################################################################

from odata_test_server import ODataTestServer, Profile

# ################################################################################################################################
# ################################################################################################################################

# The official CSDL XSDs and the real-world metadata documents live in the fixture tree.
Fixtures_Dir = os.path.join(_here, 'fixtures')
Schemas_Dir = os.path.join(Fixtures_Dir, 'schemas')
Metadata_Fixtures_Dir = os.path.join(Fixtures_Dir, 'metadata')
ABNF_Dir = os.path.join(Fixtures_Dir, 'abnf')
Payloads_Dir = os.path.join(Fixtures_Dir, 'payloads')

# The documents the test server profiles serve.
Server_Metadata_Dir = os.path.join(_here, 'lib', 'metadata')

# ################################################################################################################################
# ################################################################################################################################

def load_schema(file_name:'str') -> 'etree.XMLSchema':
    """ Loads one of the official XSDs from the fixture tree.
    """
    document = etree.parse(os.path.join(Schemas_Dir, file_name))

    out = etree.XMLSchema(document)
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def edmx_v4_schema():
    """ The official OASIS EDMX 4.0 schema - it imports the CSDL 4.0 one.
    """
    out = load_schema('edmx.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def csdl_v2_schema():
    """ The Microsoft CSDL 2.0 schema V2 metadata embeds its Schema elements in.
    """
    out = load_schema('System.Data.Resources.CSDLSchema_2.xsd')
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def csdl_v3_schema():
    """ The Microsoft CSDL 3.0 schema - the public Northwind V2 service uses it.
    """
    out = load_schema('System.Data.Resources.CSDLSchema_3.xsd')
    return out

# ################################################################################################################################
# ################################################################################################################################

# The namespace-qualified Schema tag of a V2 (CSDL 2.0) metadata document.
_v2_schema_tag = '{http://schemas.microsoft.com/ado/2008/09/edm}Schema'

# ################################################################################################################################

@pytest.fixture(scope='session')
def validated_server_metadata():
    """ Validates every $metadata document the test server serves against the official
    XSDs before any test consumes it - the V4 documents against the OASIS EDMX 4.0
    schema, the V2 ones against the Microsoft CSDL 2.0 schema their Schema elements
    are defined in. The simulations themselves are proven schema-valid this way.
    """
    edmx_v4 = load_schema('edmx.xsd')
    csdl_v2 = load_schema('System.Data.Resources.CSDLSchema_2.xsd')

    documents = {
        's4hana.xml': '2.0',
        'successfactors.xml': '2.0',
        'd365fo.xml': '4.0',
        'business_central.xml': '4.0',
    }

    for file_name, version in documents.items():
        document = etree.parse(os.path.join(Server_Metadata_Dir, file_name))

        if version == '4.0':
            edmx_v4.assertValid(document)
        else:

            # The EDMX 1.0 wrapper is a plain envelope - what CSDL 2.0 governs
            # is the Schema element embedded in it.
            schema_element = document.getroot().find('.//' + _v2_schema_tag)
            csdl_v2.assertValid(schema_element)

# ################################################################################################################################

def _make_server(profile:'str', tls:'bool'=False) -> 'ODataTestServer':
    server = ODataTestServer(profile, tls=tls)
    server.start()

    out = server
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def s4hana_server(validated_server_metadata):
    """ A live server simulating SAP S/4HANA - OData V2, CSRF tokens, sap-client checks.
    """
    server = _make_server(Profile.S4HANA)

    yield server

    server.stop()

# ################################################################################################################################

@pytest.fixture(scope='session')
def successfactors_server(validated_server_metadata):
    """ A live server simulating SAP SuccessFactors - OData V2, basic credentials.
    """
    server = _make_server(Profile.SUCCESSFACTORS)

    yield server

    server.stop()

# ################################################################################################################################

@pytest.fixture(scope='session')
def d365fo_server(validated_server_metadata):
    """ A live server simulating Dynamics 365 Finance and Operations - OData V4, OAuth2.
    """
    server = _make_server(Profile.DYNAMICS_365_FO)

    yield server

    server.stop()

# ################################################################################################################################

@pytest.fixture(scope='session')
def business_central_server(validated_server_metadata):
    """ A live server simulating Business Central - OData V4, ETag concurrency.
    """
    server = _make_server(Profile.BUSINESS_CENTRAL)

    yield server

    server.stop()

# ################################################################################################################################

@pytest.fixture(scope='session')
def business_central_tls_server(validated_server_metadata):
    """ A live HTTPS Business Central server, for TLS verification tests.
    """
    server = _make_server(Profile.BUSINESS_CENTRAL, tls=True)

    yield server

    server.stop()

# ################################################################################################################################
# ################################################################################################################################
