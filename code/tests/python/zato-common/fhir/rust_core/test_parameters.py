# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Parameters


class TestToDictParameters:

    def test_to_dict_empty(self):
        resource = Parameters()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Parameters'

    def test_to_dict_with_id(self):
        resource = Parameters()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Parameters()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Parameters)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Parameters()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Parameters()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Parameters()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Parameters()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_parameter(self):
        resource = Parameters()
        resource.parameter = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'parameter' in result


class TestFromDictParameters:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Parameters', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Parameters)
        assert isinstance(result, Parameters)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Parameters'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Parameters)
        assert isinstance(result, Parameters)

    def test_from_dict_id(self):
        data = {'resourceType': 'Parameters', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Parameters)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Parameters', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Parameters)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Parameters', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Parameters)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Parameters', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Parameters)
        assert result.language is not None

    def test_from_dict_parameter(self):
        data = {'resourceType': 'Parameters', 'parameter': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Parameters)
        assert result.parameter is not None


class TestGetPathParameters:

    def test_get_path_id(self):
        resource = Parameters()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Parameters()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Parameters()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Parameters.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Parameters()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Parameters()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Parameters()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_parameter(self):
        resource = Parameters()
        resource.parameter = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'parameter')
        assert result is not None


class TestSetPathParameters:

    def test_set_path_id(self):
        resource = Parameters()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Parameters()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Parameters.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Parameters()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Parameters()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Parameters()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_parameter(self):
        resource = Parameters()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'parameter', value)
        assert result is True
        assert resource.parameter is not None


class TestParsePathParameters:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Parameters.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Parameters.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Parameters.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
