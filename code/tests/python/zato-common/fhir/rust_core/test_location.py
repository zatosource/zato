# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Location


class TestToDictLocation:

    def test_to_dict_empty(self):
        resource = Location()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Location'

    def test_to_dict_with_id(self):
        resource = Location()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Location()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Location)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Location()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Location()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Location()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Location()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Location()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Location()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Location()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Location()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Location()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = Location()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_operational_status(self):
        resource = Location()
        resource.operationalStatus = {'system': 'http://example.org', 'code': 'test-code'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'operationalStatus' in result

    def test_to_dict_name(self):
        resource = Location()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_alias(self):
        resource = Location()
        resource.alias = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'alias' in result

    def test_to_dict_description(self):
        resource = Location()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_mode(self):
        resource = Location()
        resource.mode = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'mode' in result

    def test_to_dict_type(self):
        resource = Location()
        resource.type_ = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_telecom(self):
        resource = Location()
        resource.telecom = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'telecom' in result

    def test_to_dict_address(self):
        resource = Location()
        resource.address = {'use': 'home', 'line': ['123 Main St'], 'city': 'Boston', 'state': 'MA', 'postalCode': '02101', 'country': 'USA'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'address' in result

    def test_to_dict_physical_type(self):
        resource = Location()
        resource.physicalType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'physicalType' in result

    def test_to_dict_position(self):
        resource = Location()
        resource.position = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'position' in result

    def test_to_dict_managing_organization(self):
        resource = Location()
        resource.managingOrganization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'managingOrganization' in result

    def test_to_dict_part_of(self):
        resource = Location()
        resource.partOf = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'partOf' in result

    def test_to_dict_hours_of_operation(self):
        resource = Location()
        resource.hoursOfOperation = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'hoursOfOperation' in result

    def test_to_dict_availability_exceptions(self):
        resource = Location()
        resource.availabilityExceptions = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'availabilityExceptions' in result

    def test_to_dict_endpoint(self):
        resource = Location()
        resource.endpoint = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'endpoint' in result


class TestFromDictLocation:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Location', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert isinstance(result, Location)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Location'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert isinstance(result, Location)

    def test_from_dict_id(self):
        data = {'resourceType': 'Location', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Location', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Location', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Location', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Location', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Location', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Location', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Location', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Location', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Location', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.status is not None

    def test_from_dict_operational_status(self):
        data = {'resourceType': 'Location', 'operationalStatus': {'system': 'http://example.org', 'code': 'test-code'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.operationalStatus is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'Location', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.name is not None

    def test_from_dict_alias(self):
        data = {'resourceType': 'Location', 'alias': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.alias is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'Location', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.description is not None

    def test_from_dict_mode(self):
        data = {'resourceType': 'Location', 'mode': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.mode is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'Location',
         'type': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                   'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.type_ is not None

    def test_from_dict_telecom(self):
        data = {'resourceType': 'Location', 'telecom': [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.telecom is not None

    def test_from_dict_address(self):
        data = {'address': {'city': 'Boston',
                     'country': 'USA',
                     'line': ['123 Main St'],
                     'postalCode': '02101',
                     'state': 'MA',
                     'use': 'home'},
         'resourceType': 'Location'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.address is not None

    def test_from_dict_physical_type(self):
        data = {'physicalType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'},
         'resourceType': 'Location'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.physicalType is not None

    def test_from_dict_position(self):
        data = {'resourceType': 'Location', 'position': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.position is not None

    def test_from_dict_managing_organization(self):
        data = {'resourceType': 'Location', 'managingOrganization': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.managingOrganization is not None

    def test_from_dict_part_of(self):
        data = {'resourceType': 'Location', 'partOf': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.partOf is not None

    def test_from_dict_hours_of_operation(self):
        data = {'resourceType': 'Location', 'hoursOfOperation': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.hoursOfOperation is not None

    def test_from_dict_availability_exceptions(self):
        data = {'resourceType': 'Location', 'availabilityExceptions': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.availabilityExceptions is not None

    def test_from_dict_endpoint(self):
        data = {'resourceType': 'Location', 'endpoint': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Location)
        assert result.endpoint is not None


class TestGetPathLocation:

    def test_get_path_id(self):
        resource = Location()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Location()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Location()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Location.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Location()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Location()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Location()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Location()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Location()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Location()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Location()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Location()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = Location()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_operational_status(self):
        resource = Location()
        resource.operationalStatus = {'system': 'http://example.org', 'code': 'test-code'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'operationalStatus')
        assert result is not None

    def test_get_path_name(self):
        resource = Location()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_alias(self):
        resource = Location()
        resource.alias = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'alias')
        assert result is not None

    def test_get_path_description(self):
        resource = Location()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_mode(self):
        resource = Location()
        resource.mode = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'mode')
        assert result is not None

    def test_get_path_type(self):
        resource = Location()
        resource.type_ = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_telecom(self):
        resource = Location()
        resource.telecom = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'telecom')
        assert result is not None

    def test_get_path_address(self):
        resource = Location()
        resource.address = {'use': 'home', 'line': ['123 Main St'], 'city': 'Boston', 'state': 'MA', 'postalCode': '02101', 'country': 'USA'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'address')
        assert result is not None

    def test_get_path_physical_type(self):
        resource = Location()
        resource.physicalType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'physicalType')
        assert result is not None

    def test_get_path_position(self):
        resource = Location()
        resource.position = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'position')
        assert result is not None

    def test_get_path_managing_organization(self):
        resource = Location()
        resource.managingOrganization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'managingOrganization')
        assert result is not None

    def test_get_path_part_of(self):
        resource = Location()
        resource.partOf = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'partOf')
        assert result is not None

    def test_get_path_hours_of_operation(self):
        resource = Location()
        resource.hoursOfOperation = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'hoursOfOperation')
        assert result is not None

    def test_get_path_availability_exceptions(self):
        resource = Location()
        resource.availabilityExceptions = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'availabilityExceptions')
        assert result is not None

    def test_get_path_endpoint(self):
        resource = Location()
        resource.endpoint = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'endpoint')
        assert result is not None


class TestSetPathLocation:

    def test_set_path_id(self):
        resource = Location()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Location()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Location.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Location()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Location()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Location()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Location()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Location()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Location()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Location()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Location()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = Location()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_operational_status(self):
        resource = Location()
        value = {'system': 'http://example.org', 'code': 'test-code'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'operationalStatus', value)
        assert result is True
        assert resource.operationalStatus is not None

    def test_set_path_name(self):
        resource = Location()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_alias(self):
        resource = Location()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'alias', value)
        assert result is True
        assert resource.alias is not None

    def test_set_path_description(self):
        resource = Location()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_mode(self):
        resource = Location()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'mode', value)
        assert result is True
        assert resource.mode is not None

    def test_set_path_type(self):
        resource = Location()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_telecom(self):
        resource = Location()
        value = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'telecom', value)
        assert result is True
        assert resource.telecom is not None

    def test_set_path_address(self):
        resource = Location()
        value = {'use': 'home', 'line': ['123 Main St'], 'city': 'Boston', 'state': 'MA', 'postalCode': '02101', 'country': 'USA'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'address', value)
        assert result is True
        assert resource.address is not None

    def test_set_path_physical_type(self):
        resource = Location()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'physicalType', value)
        assert result is True
        assert resource.physicalType is not None

    def test_set_path_position(self):
        resource = Location()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'position', value)
        assert result is True
        assert resource.position is not None

    def test_set_path_managing_organization(self):
        resource = Location()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'managingOrganization', value)
        assert result is True
        assert resource.managingOrganization is not None

    def test_set_path_part_of(self):
        resource = Location()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'partOf', value)
        assert result is True
        assert resource.partOf is not None

    def test_set_path_hours_of_operation(self):
        resource = Location()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'hoursOfOperation', value)
        assert result is True
        assert resource.hoursOfOperation is not None

    def test_set_path_availability_exceptions(self):
        resource = Location()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'availabilityExceptions', value)
        assert result is True
        assert resource.availabilityExceptions is not None

    def test_set_path_endpoint(self):
        resource = Location()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'endpoint', value)
        assert result is True
        assert resource.endpoint is not None


class TestParsePathLocation:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Location.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Location.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Location.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
