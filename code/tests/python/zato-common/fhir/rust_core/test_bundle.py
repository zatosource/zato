# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Bundle


class TestToDictBundle:

    def test_to_dict_empty(self):
        resource = Bundle()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Bundle'

    def test_to_dict_with_id(self):
        resource = Bundle()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Bundle()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Bundle)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Bundle()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Bundle()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Bundle()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Bundle()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_identifier(self):
        resource = Bundle()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_type(self):
        resource = Bundle()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_timestamp(self):
        resource = Bundle()
        resource.timestamp = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'timestamp' in result

    def test_to_dict_total(self):
        resource = Bundle()
        resource.total = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'total' in result

    def test_to_dict_link(self):
        resource = Bundle()
        resource.link = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'link' in result

    def test_to_dict_entry(self):
        resource = Bundle()
        resource.entry = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'entry' in result

    def test_to_dict_signature(self):
        resource = Bundle()
        resource.signature = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'signature' in result


class TestFromDictBundle:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Bundle', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Bundle)
        assert isinstance(result, Bundle)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Bundle'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Bundle)
        assert isinstance(result, Bundle)

    def test_from_dict_id(self):
        data = {'resourceType': 'Bundle', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Bundle)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Bundle', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Bundle)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Bundle', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Bundle)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Bundle', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Bundle)
        assert result.language is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Bundle', 'identifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Bundle)
        assert result.identifier is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'Bundle', 'type': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Bundle)
        assert result.type_ is not None

    def test_from_dict_timestamp(self):
        data = {'resourceType': 'Bundle', 'timestamp': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Bundle)
        assert result.timestamp is not None

    def test_from_dict_total(self):
        data = {'resourceType': 'Bundle', 'total': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, Bundle)
        assert result.total is not None

    def test_from_dict_link(self):
        data = {'resourceType': 'Bundle', 'link': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Bundle)
        assert result.link is not None

    def test_from_dict_entry(self):
        data = {'resourceType': 'Bundle', 'entry': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Bundle)
        assert result.entry is not None

    def test_from_dict_signature(self):
        data = {'resourceType': 'Bundle', 'signature': {'value': 'test'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Bundle)
        assert result.signature is not None


class TestGetPathBundle:

    def test_get_path_id(self):
        resource = Bundle()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Bundle()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Bundle()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Bundle.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Bundle()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Bundle()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Bundle()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Bundle()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_type(self):
        resource = Bundle()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_timestamp(self):
        resource = Bundle()
        resource.timestamp = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'timestamp')
        assert result is not None

    def test_get_path_total(self):
        resource = Bundle()
        resource.total = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'total')
        assert result is not None

    def test_get_path_link(self):
        resource = Bundle()
        resource.link = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'link')
        assert result is not None

    def test_get_path_entry(self):
        resource = Bundle()
        resource.entry = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'entry')
        assert result is not None

    def test_get_path_signature(self):
        resource = Bundle()
        resource.signature = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'signature')
        assert result is not None


class TestSetPathBundle:

    def test_set_path_id(self):
        resource = Bundle()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Bundle()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Bundle.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Bundle()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Bundle()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Bundle()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_identifier(self):
        resource = Bundle()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_type(self):
        resource = Bundle()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_timestamp(self):
        resource = Bundle()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'timestamp', value)
        assert result is True
        assert resource.timestamp is not None

    def test_set_path_total(self):
        resource = Bundle()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'total', value)
        assert result is True
        assert resource.total is not None

    def test_set_path_link(self):
        resource = Bundle()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'link', value)
        assert result is True
        assert resource.link is not None

    def test_set_path_entry(self):
        resource = Bundle()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'entry', value)
        assert result is True
        assert resource.entry is not None

    def test_set_path_signature(self):
        resource = Bundle()
        value = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'signature', value)
        assert result is True
        assert resource.signature is not None


class TestParsePathBundle:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Bundle.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Bundle.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Bundle.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
