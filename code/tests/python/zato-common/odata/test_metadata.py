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
from zato.common.odata.client import ODataClient
from zato.common.odata.common import ODataSyntaxError, ODataVersion
from zato.common.odata.metadata import parse_metadata

# ################################################################################################################################
# ################################################################################################################################

# The real published $metadata documents live in the fixture tree.
Metadata_Fixtures_Dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'metadata')

# ################################################################################################################################
# ################################################################################################################################

def _load_fixture(file_name):
    """ Reads one golden $metadata document from the fixture tree.
    """
    path = os.path.join(Metadata_Fixtures_Dir, file_name)

    with open(path, 'rb') as fixture_file:
        out = fixture_file.read()

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestTripPin:
    """ The odata.org TripPin V4 reference service - the golden file is the real,
    publicly served $metadata document.
    """

    def test_shape(self):
        metadata = parse_metadata(_load_fixture('trippin-v4.xml'))

        assert metadata.edmx_version == '4.0'

        assert sorted(metadata.entity_sets) == ['Airlines', 'Airports', 'People']

        assert len(metadata.entity_types) == 10
        for name in ('Person', 'Airline', 'Airport', 'Trip', 'Flight'):
            assert name in metadata.entity_types

    def test_person(self):
        metadata = parse_metadata(_load_fixture('trippin-v4.xml'))

        person = metadata.entity_type_of('People')

        assert person.key == ['UserName']
        assert len(person.properties) == 11

        assert person.properties['UserName'].type == 'Edm.String'
        assert person.properties['UserName'].is_nullable is False
        assert person.properties['MiddleName'].is_nullable is True

        assert sorted(person.navigation_properties) == ['BestFriend', 'Friends', 'Trips']
        assert person.navigation_properties['Friends'].target == 'Collection(Trippin.Person)'
        assert person.navigation_properties['BestFriend'].target == 'Trippin.Person'

    def test_operations(self):
        metadata = parse_metadata(_load_fixture('trippin-v4.xml'))

        assert sorted(metadata.functions) == [
            'GetFavoriteAirline', 'GetFriendsTrips', 'GetInvolvedPeople', 'GetNearestAirport', 'GetPersonWithMostFriends',
        ]
        assert sorted(metadata.actions) == ['ResetDataSource', 'ShareTrip', 'UpdateLastName']

        nearest = metadata.functions['GetNearestAirport']

        assert nearest.return_type == 'Trippin.Airport'
        assert len(nearest.parameters) == 2
        assert nearest.parameters[0].name == 'lat'
        assert nearest.parameters[0].type == 'Edm.Double'

# ################################################################################################################################
# ################################################################################################################################

class TestNorthwind:
    """ The odata.org Northwind V2 reference service - the golden file is the real,
    publicly served $metadata document.
    """

    def test_shape(self):
        metadata = parse_metadata(_load_fixture('northwind-v2.xml'))

        # Northwind predates V2 labeling - its EDMX wrapper says 1.0.
        assert metadata.edmx_version == '1.0'

        assert len(metadata.entity_sets) == 26
        assert len(metadata.entity_types) == 26

        for name in ('Customers', 'Orders', 'Products', 'Employees'):
            assert name in metadata.entity_sets

    def test_customer(self):
        metadata = parse_metadata(_load_fixture('northwind-v2.xml'))

        customer = metadata.entity_type_of('Customers')

        assert customer.key == ['CustomerID']
        assert len(customer.properties) == 11

        assert customer.properties['CustomerID'].type == 'Edm.String'
        assert customer.properties['CustomerID'].is_nullable is False

        # V2 navigation properties point at their relationship, not a type.
        assert sorted(customer.navigation_properties) == ['CustomerDemographics', 'Orders']
        assert customer.navigation_properties['Orders'].target == 'NorthwindModel.FK_Orders_Customers'

    def test_composite_key(self):
        metadata = parse_metadata(_load_fixture('northwind-v2.xml'))

        order_detail = metadata.entity_types['Order_Detail']

        assert order_detail.key == ['OrderID', 'ProductID']

# ################################################################################################################################
# ################################################################################################################################

class TestServedMetadata:
    """ The documents the four simulation profiles serve, retrieved live through the client.
    """

    def test_s4hana(self, s4hana_server):
        s4hana_server.reset()

        config = {
            'address': s4hana_server.service_root + '/',
            'odata_version': ODataVersion.V2,
            'auth_type': 'none',
        }
        client = ODataClient(config)
        metadata = client.metadata()
        client.close()

        assert metadata.edmx_version == '1.0'
        assert sorted(metadata.entity_sets) == ['A_SalesOrder', 'A_SalesOrderItem']

        order = metadata.entity_type_of('A_SalesOrder')
        assert order.key == ['SalesOrder']
        assert order.navigation_properties['to_Item'].target == 'API_SALES_ORDER_SRV.assoc_to_Item'

        item = metadata.entity_type_of('A_SalesOrderItem')
        assert item.key == ['SalesOrder', 'SalesOrderItem']

        # The V2 function import is marked POST, so it surfaces as an action.
        assert sorted(metadata.actions) == ['ReleaseApprovalRequest']

    def test_successfactors(self, successfactors_server):
        successfactors_server.reset()

        config = {
            'address': successfactors_server.service_root + '/',
            'odata_version': ODataVersion.V2,
            'auth_type': 'none',
        }
        client = ODataClient(config)
        metadata = client.metadata()
        client.close()

        assert sorted(metadata.entity_sets) == ['PerPerson', 'PerPersonal']

        personal = metadata.entity_type_of('PerPersonal')
        assert personal.key == ['personIdExternal', 'startDate']

        # The V2 function import is a GET, so it surfaces as a function.
        assert sorted(metadata.functions) == ['getUserRolesByUserId']

    def test_d365fo(self, d365fo_server):
        d365fo_server.reset()
        d365fo_server.set_oauth_client('client-1', 'secret-1')

        config = {
            'address': d365fo_server.service_root + '/',
            'odata_version': ODataVersion.V4,
            'auth_type': 'oauth2',
            'client_id': 'client-1',
            'client_secret': 'secret-1',
            'token_url': d365fo_server.token_url,
        }
        client = ODataClient(config)
        metadata = client.metadata()
        client.close()

        assert metadata.edmx_version == '4.0'
        assert sorted(metadata.entity_sets) == ['CustomersV3', 'VendorsV2']

        customer = metadata.entity_type_of('CustomersV3')
        assert customer.key == ['dataAreaId', 'CustomerAccount']

        assert sorted(metadata.functions) == ['GetKeys']
        assert sorted(metadata.actions) == ['calculateBalance']

    def test_business_central(self, business_central_server):
        business_central_server.reset()

        config = {
            'address': business_central_server.service_root + '/',
            'odata_version': ODataVersion.V4,
            'auth_type': 'none',
        }
        client = ODataClient(config)
        metadata = client.metadata()
        client.close()

        assert sorted(metadata.entity_sets) == ['companies', 'customers', 'salesInvoices']

        company = metadata.entity_type_of('companies')
        assert company.key == ['id']
        assert company.navigation_properties['customers'].target == 'Collection(Microsoft.NAV.customer)'

        assert sorted(metadata.actions) == ['post']

# ################################################################################################################################
# ################################################################################################################################

class TestGoldenFilesAreSchemaValid:
    """ The golden files themselves validate against the official XSDs, so the parser
    is only ever proven against schema-valid documents.
    """

    def test_trippin(self, edmx_v4_schema):
        document = etree.fromstring(_load_fixture('trippin-v4.xml'))

        edmx_v4_schema.assertValid(document)

    def test_northwind(self, csdl_v3_schema):
        document = etree.fromstring(_load_fixture('northwind-v2.xml'))

        # The EDMX 1.0 wrapper is a plain envelope - what the CSDL schema governs
        # is the Schema element embedded in it, and Northwind publishes CSDL 3.0.
        schema_element = document.find('.//{http://schemas.microsoft.com/ado/2009/11/edm}Schema')
        csdl_v3_schema.assertValid(schema_element)

# ################################################################################################################################
# ################################################################################################################################

class TestParserErrors:
    """ Documents that are not EDMX at all surface as syntax errors.
    """

    def test_invalid_xml(self):
        with pytest.raises(ODataSyntaxError):
            _ = parse_metadata(b'this is not xml')

# ################################################################################################################################
# ################################################################################################################################
