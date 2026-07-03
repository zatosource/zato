# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Endpoint


class TestToDictEndpoint:

    def test_to_dict_empty(self):
        resource = Endpoint()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Endpoint'

    def test_to_dict_with_id(self):
        resource = Endpoint()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Endpoint()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Endpoint)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Endpoint()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Endpoint()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Endpoint()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Endpoint()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Endpoint()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Endpoint()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Endpoint()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Endpoint()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Endpoint()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = Endpoint()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_connection_type(self):
        resource = Endpoint()
        resource.connectionType = {'system': 'http://example.org', 'code': 'test-code'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'connectionType' in result

    def test_to_dict_name(self):
        resource = Endpoint()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_managing_organization(self):
        resource = Endpoint()
        resource.managingOrganization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'managingOrganization' in result

    def test_to_dict_contact(self):
        resource = Endpoint()
        resource.contact = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_period(self):
        resource = Endpoint()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'period' in result

    def test_to_dict_payload_type(self):
        resource = Endpoint()
        resource.payloadType = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'payloadType' in result

    def test_to_dict_payload_mime_type(self):
        resource = Endpoint()
        resource.payloadMimeType = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'payloadMimeType' in result

    def test_to_dict_address(self):
        resource = Endpoint()
        resource.address = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'address' in result

    def test_to_dict_header(self):
        resource = Endpoint()
        resource.header = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'header' in result


class TestFromDictEndpoint:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Endpoint', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert isinstance(result, Endpoint)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Endpoint'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert isinstance(result, Endpoint)

    def test_from_dict_id(self):
        data = {'resourceType': 'Endpoint', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Endpoint', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Endpoint', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Endpoint', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Endpoint', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Endpoint', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Endpoint', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Endpoint', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Endpoint', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Endpoint', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.status is not None

    def test_from_dict_connection_type(self):
        data = {'resourceType': 'Endpoint', 'connectionType': {'system': 'http://example.org', 'code': 'test-code'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.connectionType is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'Endpoint', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.name is not None

    def test_from_dict_managing_organization(self):
        data = {'resourceType': 'Endpoint', 'managingOrganization': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.managingOrganization is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'Endpoint', 'contact': [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.contact is not None

    def test_from_dict_period(self):
        data = {'resourceType': 'Endpoint', 'period': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.period is not None

    def test_from_dict_payload_type(self):
        data = {'payloadType': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'}],
         'resourceType': 'Endpoint'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.payloadType is not None

    def test_from_dict_payload_mime_type(self):
        data = {'resourceType': 'Endpoint', 'payloadMimeType': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.payloadMimeType is not None

    def test_from_dict_address(self):
        data = {'resourceType': 'Endpoint', 'address': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.address is not None

    def test_from_dict_header(self):
        data = {'resourceType': 'Endpoint', 'header': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, Endpoint)
        assert result.header is not None


class TestGetPathEndpoint:

    def test_get_path_id(self):
        resource = Endpoint()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Endpoint()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Endpoint()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Endpoint.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Endpoint()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Endpoint()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Endpoint()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Endpoint()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Endpoint()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Endpoint()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Endpoint()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Endpoint()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = Endpoint()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_connection_type(self):
        resource = Endpoint()
        resource.connectionType = {'system': 'http://example.org', 'code': 'test-code'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'connectionType')
        assert result is not None

    def test_get_path_name(self):
        resource = Endpoint()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_managing_organization(self):
        resource = Endpoint()
        resource.managingOrganization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'managingOrganization')
        assert result is not None

    def test_get_path_contact(self):
        resource = Endpoint()
        resource.contact = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_period(self):
        resource = Endpoint()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'period')
        assert result is not None

    def test_get_path_payload_type(self):
        resource = Endpoint()
        resource.payloadType = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'payloadType')
        assert result is not None

    def test_get_path_payload_mime_type(self):
        resource = Endpoint()
        resource.payloadMimeType = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'payloadMimeType')
        assert result is not None

    def test_get_path_address(self):
        resource = Endpoint()
        resource.address = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'address')
        assert result is not None

    def test_get_path_header(self):
        resource = Endpoint()
        resource.header = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'header')
        assert result is not None


class TestSetPathEndpoint:

    def test_set_path_id(self):
        resource = Endpoint()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Endpoint()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Endpoint.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Endpoint()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Endpoint()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Endpoint()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Endpoint()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Endpoint()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Endpoint()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Endpoint()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Endpoint()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = Endpoint()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_connection_type(self):
        resource = Endpoint()
        value = {'system': 'http://example.org', 'code': 'test-code'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'connectionType', value)
        assert result is True
        assert resource.connectionType is not None

    def test_set_path_name(self):
        resource = Endpoint()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_managing_organization(self):
        resource = Endpoint()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'managingOrganization', value)
        assert result is True
        assert resource.managingOrganization is not None

    def test_set_path_contact(self):
        resource = Endpoint()
        value = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_period(self):
        resource = Endpoint()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'period', value)
        assert result is True
        assert resource.period is not None

    def test_set_path_payload_type(self):
        resource = Endpoint()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'payloadType', value)
        assert result is True
        assert resource.payloadType is not None

    def test_set_path_payload_mime_type(self):
        resource = Endpoint()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'payloadMimeType', value)
        assert result is True
        assert resource.payloadMimeType is not None

    def test_set_path_address(self):
        resource = Endpoint()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'address', value)
        assert result is True
        assert resource.address is not None

    def test_set_path_header(self):
        resource = Endpoint()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'header', value)
        assert result is True
        assert resource.header is not None


class TestParsePathEndpoint:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Endpoint.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Endpoint.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Endpoint.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
