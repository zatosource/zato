# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import AuditEvent


class TestToDictAuditEvent:

    def test_to_dict_empty(self):
        resource = AuditEvent()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'AuditEvent'

    def test_to_dict_with_id(self):
        resource = AuditEvent()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = AuditEvent()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, AuditEvent)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = AuditEvent()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = AuditEvent()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = AuditEvent()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = AuditEvent()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = AuditEvent()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = AuditEvent()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = AuditEvent()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = AuditEvent()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_type(self):
        resource = AuditEvent()
        resource.type_ = {'system': 'http://example.org', 'code': 'test-code'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_subtype(self):
        resource = AuditEvent()
        resource.subtype = [{'system': 'http://example.org', 'code': 'test-code'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subtype' in result

    def test_to_dict_action(self):
        resource = AuditEvent()
        resource.action = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'action' in result

    def test_to_dict_period(self):
        resource = AuditEvent()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'period' in result

    def test_to_dict_recorded(self):
        resource = AuditEvent()
        resource.recorded = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recorded' in result

    def test_to_dict_outcome(self):
        resource = AuditEvent()
        resource.outcome = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'outcome' in result

    def test_to_dict_outcome_desc(self):
        resource = AuditEvent()
        resource.outcomeDesc = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'outcomeDesc' in result

    def test_to_dict_purpose_of_event(self):
        resource = AuditEvent()
        resource.purposeOfEvent = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purposeOfEvent' in result

    def test_to_dict_agent(self):
        resource = AuditEvent()
        resource.agent = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'agent' in result

    def test_to_dict_source(self):
        resource = AuditEvent()
        resource.source = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'source' in result

    def test_to_dict_entity(self):
        resource = AuditEvent()
        resource.entity = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'entity' in result


class TestFromDictAuditEvent:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'AuditEvent', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert isinstance(result, AuditEvent)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'AuditEvent'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert isinstance(result, AuditEvent)

    def test_from_dict_id(self):
        data = {'resourceType': 'AuditEvent', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'AuditEvent', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'AuditEvent', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'AuditEvent', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'AuditEvent', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'AuditEvent', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'AuditEvent', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'AuditEvent', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.modifierExtension is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'AuditEvent', 'type': {'system': 'http://example.org', 'code': 'test-code'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.type_ is not None

    def test_from_dict_subtype(self):
        data = {'resourceType': 'AuditEvent', 'subtype': [{'system': 'http://example.org', 'code': 'test-code'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.subtype is not None

    def test_from_dict_action(self):
        data = {'resourceType': 'AuditEvent', 'action': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.action is not None

    def test_from_dict_period(self):
        data = {'resourceType': 'AuditEvent', 'period': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.period is not None

    def test_from_dict_recorded(self):
        data = {'resourceType': 'AuditEvent', 'recorded': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.recorded is not None

    def test_from_dict_outcome(self):
        data = {'resourceType': 'AuditEvent', 'outcome': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.outcome is not None

    def test_from_dict_outcome_desc(self):
        data = {'resourceType': 'AuditEvent', 'outcomeDesc': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.outcomeDesc is not None

    def test_from_dict_purpose_of_event(self):
        data = {'purposeOfEvent': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                             'text': 'Test concept'}],
         'resourceType': 'AuditEvent'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.purposeOfEvent is not None

    def test_from_dict_agent(self):
        data = {'resourceType': 'AuditEvent', 'agent': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.agent is not None

    def test_from_dict_source(self):
        data = {'resourceType': 'AuditEvent', 'source': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.source is not None

    def test_from_dict_entity(self):
        data = {'resourceType': 'AuditEvent', 'entity': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AuditEvent)
        assert result.entity is not None


class TestGetPathAuditEvent:

    def test_get_path_id(self):
        resource = AuditEvent()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = AuditEvent()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = AuditEvent()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'AuditEvent.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = AuditEvent()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = AuditEvent()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = AuditEvent()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = AuditEvent()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = AuditEvent()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = AuditEvent()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = AuditEvent()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_type(self):
        resource = AuditEvent()
        resource.type_ = {'system': 'http://example.org', 'code': 'test-code'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_subtype(self):
        resource = AuditEvent()
        resource.subtype = [{'system': 'http://example.org', 'code': 'test-code'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subtype')
        assert result is not None

    def test_get_path_action(self):
        resource = AuditEvent()
        resource.action = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'action')
        assert result is not None

    def test_get_path_period(self):
        resource = AuditEvent()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'period')
        assert result is not None

    def test_get_path_recorded(self):
        resource = AuditEvent()
        resource.recorded = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recorded')
        assert result is not None

    def test_get_path_outcome(self):
        resource = AuditEvent()
        resource.outcome = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'outcome')
        assert result is not None

    def test_get_path_outcome_desc(self):
        resource = AuditEvent()
        resource.outcomeDesc = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'outcomeDesc')
        assert result is not None

    def test_get_path_purpose_of_event(self):
        resource = AuditEvent()
        resource.purposeOfEvent = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purposeOfEvent')
        assert result is not None

    def test_get_path_agent(self):
        resource = AuditEvent()
        resource.agent = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'agent')
        assert result is not None

    def test_get_path_source(self):
        resource = AuditEvent()
        resource.source = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'source')
        assert result is not None

    def test_get_path_entity(self):
        resource = AuditEvent()
        resource.entity = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'entity')
        assert result is not None


class TestSetPathAuditEvent:

    def test_set_path_id(self):
        resource = AuditEvent()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = AuditEvent()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'AuditEvent.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = AuditEvent()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = AuditEvent()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = AuditEvent()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = AuditEvent()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = AuditEvent()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = AuditEvent()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = AuditEvent()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_type(self):
        resource = AuditEvent()
        value = {'system': 'http://example.org', 'code': 'test-code'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_subtype(self):
        resource = AuditEvent()
        value = [{'system': 'http://example.org', 'code': 'test-code'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subtype', value)
        assert result is True
        assert resource.subtype is not None

    def test_set_path_action(self):
        resource = AuditEvent()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'action', value)
        assert result is True
        assert resource.action is not None

    def test_set_path_period(self):
        resource = AuditEvent()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'period', value)
        assert result is True
        assert resource.period is not None

    def test_set_path_recorded(self):
        resource = AuditEvent()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recorded', value)
        assert result is True
        assert resource.recorded is not None

    def test_set_path_outcome(self):
        resource = AuditEvent()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'outcome', value)
        assert result is True
        assert resource.outcome is not None

    def test_set_path_outcome_desc(self):
        resource = AuditEvent()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'outcomeDesc', value)
        assert result is True
        assert resource.outcomeDesc is not None

    def test_set_path_purpose_of_event(self):
        resource = AuditEvent()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purposeOfEvent', value)
        assert result is True
        assert resource.purposeOfEvent is not None

    def test_set_path_agent(self):
        resource = AuditEvent()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'agent', value)
        assert result is True
        assert resource.agent is not None

    def test_set_path_source(self):
        resource = AuditEvent()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'source', value)
        assert result is True
        assert resource.source is not None

    def test_set_path_entity(self):
        resource = AuditEvent()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'entity', value)
        assert result is True
        assert resource.entity is not None


class TestParsePathAuditEvent:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('AuditEvent.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('AuditEvent.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('AuditEvent.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
