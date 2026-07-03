# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import EnrollmentResponse


class TestToDictEnrollmentResponse:

    def test_to_dict_empty(self):
        resource = EnrollmentResponse()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'EnrollmentResponse'

    def test_to_dict_with_id(self):
        resource = EnrollmentResponse()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = EnrollmentResponse()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, EnrollmentResponse)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = EnrollmentResponse()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = EnrollmentResponse()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = EnrollmentResponse()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = EnrollmentResponse()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = EnrollmentResponse()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = EnrollmentResponse()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = EnrollmentResponse()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = EnrollmentResponse()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = EnrollmentResponse()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = EnrollmentResponse()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_request(self):
        resource = EnrollmentResponse()
        resource.request = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'request' in result

    def test_to_dict_outcome(self):
        resource = EnrollmentResponse()
        resource.outcome = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'outcome' in result

    def test_to_dict_disposition(self):
        resource = EnrollmentResponse()
        resource.disposition = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'disposition' in result

    def test_to_dict_created(self):
        resource = EnrollmentResponse()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'created' in result

    def test_to_dict_organization(self):
        resource = EnrollmentResponse()
        resource.organization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'organization' in result

    def test_to_dict_request_provider(self):
        resource = EnrollmentResponse()
        resource.requestProvider = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'requestProvider' in result


class TestFromDictEnrollmentResponse:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'EnrollmentResponse', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert isinstance(result, EnrollmentResponse)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'EnrollmentResponse'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert isinstance(result, EnrollmentResponse)

    def test_from_dict_id(self):
        data = {'resourceType': 'EnrollmentResponse', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'EnrollmentResponse', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'EnrollmentResponse', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'EnrollmentResponse', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'EnrollmentResponse', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'EnrollmentResponse', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'EnrollmentResponse', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'EnrollmentResponse', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'EnrollmentResponse', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'EnrollmentResponse', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.status is not None

    def test_from_dict_request(self):
        data = {'resourceType': 'EnrollmentResponse', 'request': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.request is not None

    def test_from_dict_outcome(self):
        data = {'resourceType': 'EnrollmentResponse', 'outcome': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.outcome is not None

    def test_from_dict_disposition(self):
        data = {'resourceType': 'EnrollmentResponse', 'disposition': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.disposition is not None

    def test_from_dict_created(self):
        data = {'resourceType': 'EnrollmentResponse', 'created': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.created is not None

    def test_from_dict_organization(self):
        data = {'resourceType': 'EnrollmentResponse', 'organization': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.organization is not None

    def test_from_dict_request_provider(self):
        data = {'resourceType': 'EnrollmentResponse', 'requestProvider': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EnrollmentResponse)
        assert result.requestProvider is not None


class TestGetPathEnrollmentResponse:

    def test_get_path_id(self):
        resource = EnrollmentResponse()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = EnrollmentResponse()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = EnrollmentResponse()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'EnrollmentResponse.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = EnrollmentResponse()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = EnrollmentResponse()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = EnrollmentResponse()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = EnrollmentResponse()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = EnrollmentResponse()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = EnrollmentResponse()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = EnrollmentResponse()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = EnrollmentResponse()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = EnrollmentResponse()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_request(self):
        resource = EnrollmentResponse()
        resource.request = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'request')
        assert result is not None

    def test_get_path_outcome(self):
        resource = EnrollmentResponse()
        resource.outcome = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'outcome')
        assert result is not None

    def test_get_path_disposition(self):
        resource = EnrollmentResponse()
        resource.disposition = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'disposition')
        assert result is not None

    def test_get_path_created(self):
        resource = EnrollmentResponse()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'created')
        assert result is not None

    def test_get_path_organization(self):
        resource = EnrollmentResponse()
        resource.organization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'organization')
        assert result is not None

    def test_get_path_request_provider(self):
        resource = EnrollmentResponse()
        resource.requestProvider = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'requestProvider')
        assert result is not None


class TestSetPathEnrollmentResponse:

    def test_set_path_id(self):
        resource = EnrollmentResponse()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = EnrollmentResponse()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'EnrollmentResponse.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = EnrollmentResponse()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = EnrollmentResponse()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = EnrollmentResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = EnrollmentResponse()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = EnrollmentResponse()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = EnrollmentResponse()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = EnrollmentResponse()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = EnrollmentResponse()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = EnrollmentResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_request(self):
        resource = EnrollmentResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'request', value)
        assert result is True
        assert resource.request is not None

    def test_set_path_outcome(self):
        resource = EnrollmentResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'outcome', value)
        assert result is True
        assert resource.outcome is not None

    def test_set_path_disposition(self):
        resource = EnrollmentResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'disposition', value)
        assert result is True
        assert resource.disposition is not None

    def test_set_path_created(self):
        resource = EnrollmentResponse()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'created', value)
        assert result is True
        assert resource.created is not None

    def test_set_path_organization(self):
        resource = EnrollmentResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'organization', value)
        assert result is True
        assert resource.organization is not None

    def test_set_path_request_provider(self):
        resource = EnrollmentResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'requestProvider', value)
        assert result is True
        assert resource.requestProvider is not None


class TestParsePathEnrollmentResponse:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('EnrollmentResponse.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('EnrollmentResponse.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('EnrollmentResponse.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
