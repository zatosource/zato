# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Provenance


class TestToDictProvenance:

    def test_to_dict_empty(self):
        resource = Provenance()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Provenance'

    def test_to_dict_with_id(self):
        resource = Provenance()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Provenance()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Provenance)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Provenance()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Provenance()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Provenance()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Provenance()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Provenance()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Provenance()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Provenance()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Provenance()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_target(self):
        resource = Provenance()
        resource.target = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'target' in result

    def test_to_dict_recorded(self):
        resource = Provenance()
        resource.recorded = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recorded' in result

    def test_to_dict_policy(self):
        resource = Provenance()
        resource.policy = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'policy' in result

    def test_to_dict_location(self):
        resource = Provenance()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'location' in result

    def test_to_dict_reason(self):
        resource = Provenance()
        resource.reason = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reason' in result

    def test_to_dict_activity(self):
        resource = Provenance()
        resource.activity = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'activity' in result

    def test_to_dict_agent(self):
        resource = Provenance()
        resource.agent = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'agent' in result

    def test_to_dict_entity(self):
        resource = Provenance()
        resource.entity = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'entity' in result

    def test_to_dict_signature(self):
        resource = Provenance()
        resource.signature = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'signature' in result


class TestFromDictProvenance:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Provenance', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert isinstance(result, Provenance)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Provenance'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert isinstance(result, Provenance)

    def test_from_dict_id(self):
        data = {'resourceType': 'Provenance', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Provenance', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Provenance', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Provenance', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Provenance', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Provenance', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Provenance', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Provenance', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.modifierExtension is not None

    def test_from_dict_target(self):
        data = {'resourceType': 'Provenance', 'target': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.target is not None

    def test_from_dict_recorded(self):
        data = {'resourceType': 'Provenance', 'recorded': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.recorded is not None

    def test_from_dict_policy(self):
        data = {'resourceType': 'Provenance', 'policy': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.policy is not None

    def test_from_dict_location(self):
        data = {'resourceType': 'Provenance', 'location': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.location is not None

    def test_from_dict_reason(self):
        data = {'reason': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                     'text': 'Test concept'}],
         'resourceType': 'Provenance'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.reason is not None

    def test_from_dict_activity(self):
        data = {'activity': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'Provenance'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.activity is not None

    def test_from_dict_agent(self):
        data = {'resourceType': 'Provenance', 'agent': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.agent is not None

    def test_from_dict_entity(self):
        data = {'resourceType': 'Provenance', 'entity': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.entity is not None

    def test_from_dict_signature(self):
        data = {'resourceType': 'Provenance', 'signature': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Provenance)
        assert result.signature is not None


class TestGetPathProvenance:

    def test_get_path_id(self):
        resource = Provenance()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Provenance()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Provenance()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Provenance.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Provenance()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Provenance()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Provenance()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Provenance()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Provenance()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Provenance()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Provenance()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_target(self):
        resource = Provenance()
        resource.target = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'target')
        assert result is not None

    def test_get_path_recorded(self):
        resource = Provenance()
        resource.recorded = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recorded')
        assert result is not None

    def test_get_path_policy(self):
        resource = Provenance()
        resource.policy = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'policy')
        assert result is not None

    def test_get_path_location(self):
        resource = Provenance()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'location')
        assert result is not None

    def test_get_path_reason(self):
        resource = Provenance()
        resource.reason = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reason')
        assert result is not None

    def test_get_path_activity(self):
        resource = Provenance()
        resource.activity = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'activity')
        assert result is not None

    def test_get_path_agent(self):
        resource = Provenance()
        resource.agent = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'agent')
        assert result is not None

    def test_get_path_entity(self):
        resource = Provenance()
        resource.entity = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'entity')
        assert result is not None

    def test_get_path_signature(self):
        resource = Provenance()
        resource.signature = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'signature')
        assert result is not None


class TestSetPathProvenance:

    def test_set_path_id(self):
        resource = Provenance()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Provenance()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Provenance.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Provenance()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Provenance()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Provenance()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Provenance()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Provenance()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Provenance()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Provenance()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_target(self):
        resource = Provenance()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'target', value)
        assert result is True
        assert resource.target is not None

    def test_set_path_recorded(self):
        resource = Provenance()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recorded', value)
        assert result is True
        assert resource.recorded is not None

    def test_set_path_policy(self):
        resource = Provenance()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'policy', value)
        assert result is True
        assert resource.policy is not None

    def test_set_path_location(self):
        resource = Provenance()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'location', value)
        assert result is True
        assert resource.location is not None

    def test_set_path_reason(self):
        resource = Provenance()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reason', value)
        assert result is True
        assert resource.reason is not None

    def test_set_path_activity(self):
        resource = Provenance()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'activity', value)
        assert result is True
        assert resource.activity is not None

    def test_set_path_agent(self):
        resource = Provenance()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'agent', value)
        assert result is True
        assert resource.agent is not None

    def test_set_path_entity(self):
        resource = Provenance()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'entity', value)
        assert result is True
        assert resource.entity is not None

    def test_set_path_signature(self):
        resource = Provenance()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'signature', value)
        assert result is True
        assert resource.signature is not None


class TestParsePathProvenance:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Provenance.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Provenance.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Provenance.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
