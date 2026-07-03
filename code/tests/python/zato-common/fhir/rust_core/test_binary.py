# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Binary


class TestToDictBinary:

    def test_to_dict_empty(self):
        resource = Binary()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Binary'

    def test_to_dict_with_id(self):
        resource = Binary()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Binary()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Binary)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Binary()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Binary()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Binary()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Binary()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_content_type(self):
        resource = Binary()
        resource.contentType = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contentType' in result

    def test_to_dict_security_context(self):
        resource = Binary()
        resource.securityContext = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'securityContext' in result

    def test_to_dict_data(self):
        resource = Binary()
        resource.data = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'data' in result


class TestFromDictBinary:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Binary', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Binary)
        assert isinstance(result, Binary)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Binary'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Binary)
        assert isinstance(result, Binary)

    def test_from_dict_id(self):
        data = {'resourceType': 'Binary', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Binary)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Binary', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Binary)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Binary', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Binary)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Binary', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Binary)
        assert result.language is not None

    def test_from_dict_content_type(self):
        data = {'resourceType': 'Binary', 'contentType': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Binary)
        assert result.contentType is not None

    def test_from_dict_security_context(self):
        data = {'resourceType': 'Binary', 'securityContext': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Binary)
        assert result.securityContext is not None

    def test_from_dict_data(self):
        data = {'resourceType': 'Binary', 'data': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Binary)
        assert result.data is not None


class TestGetPathBinary:

    def test_get_path_id(self):
        resource = Binary()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Binary()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Binary()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Binary.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Binary()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Binary()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Binary()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_content_type(self):
        resource = Binary()
        resource.contentType = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contentType')
        assert result is not None

    def test_get_path_security_context(self):
        resource = Binary()
        resource.securityContext = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'securityContext')
        assert result is not None

    def test_get_path_data(self):
        resource = Binary()
        resource.data = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'data')
        assert result is not None


class TestSetPathBinary:

    def test_set_path_id(self):
        resource = Binary()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Binary()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Binary.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Binary()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Binary()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Binary()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_content_type(self):
        resource = Binary()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contentType', value)
        assert result is True
        assert resource.contentType is not None

    def test_set_path_security_context(self):
        resource = Binary()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'securityContext', value)
        assert result is True
        assert resource.securityContext is not None

    def test_set_path_data(self):
        resource = Binary()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'data', value)
        assert result is True
        assert resource.data is not None


class TestParsePathBinary:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Binary.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Binary.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Binary.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
