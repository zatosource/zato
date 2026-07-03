# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Goal


class TestToDictGoal:

    def test_to_dict_empty(self):
        resource = Goal()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Goal'

    def test_to_dict_with_id(self):
        resource = Goal()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Goal()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Goal)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Goal()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Goal()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Goal()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Goal()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Goal()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Goal()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Goal()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Goal()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Goal()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_lifecycle_status(self):
        resource = Goal()
        resource.lifecycleStatus = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lifecycleStatus' in result

    def test_to_dict_achievement_status(self):
        resource = Goal()
        resource.achievementStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'achievementStatus' in result

    def test_to_dict_category(self):
        resource = Goal()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_priority(self):
        resource = Goal()
        resource.priority = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priority' in result

    def test_to_dict_description(self):
        resource = Goal()
        resource.description = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_subject(self):
        resource = Goal()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_target(self):
        resource = Goal()
        resource.target = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'target' in result

    def test_to_dict_status_date(self):
        resource = Goal()
        resource.statusDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'statusDate' in result

    def test_to_dict_status_reason(self):
        resource = Goal()
        resource.statusReason = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'statusReason' in result

    def test_to_dict_expressed_by(self):
        resource = Goal()
        resource.expressedBy = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'expressedBy' in result

    def test_to_dict_addresses(self):
        resource = Goal()
        resource.addresses = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'addresses' in result

    def test_to_dict_note(self):
        resource = Goal()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_outcome_code(self):
        resource = Goal()
        resource.outcomeCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'outcomeCode' in result

    def test_to_dict_outcome_reference(self):
        resource = Goal()
        resource.outcomeReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'outcomeReference' in result


class TestFromDictGoal:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Goal', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert isinstance(result, Goal)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Goal'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert isinstance(result, Goal)

    def test_from_dict_id(self):
        data = {'resourceType': 'Goal', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Goal', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Goal', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Goal', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Goal', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Goal', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Goal', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Goal', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Goal', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.identifier is not None

    def test_from_dict_lifecycle_status(self):
        data = {'resourceType': 'Goal', 'lifecycleStatus': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.lifecycleStatus is not None

    def test_from_dict_achievement_status(self):
        data = {'achievementStatus': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                               'text': 'Test concept'},
         'resourceType': 'Goal'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.achievementStatus is not None

    def test_from_dict_category(self):
        data = {'category': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'Goal'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.category is not None

    def test_from_dict_priority(self):
        data = {'priority': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'Goal'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.priority is not None

    def test_from_dict_description(self):
        data = {'description': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'},
         'resourceType': 'Goal'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.description is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'Goal', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.subject is not None

    def test_from_dict_target(self):
        data = {'resourceType': 'Goal', 'target': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.target is not None

    def test_from_dict_status_date(self):
        data = {'resourceType': 'Goal', 'statusDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.statusDate is not None

    def test_from_dict_status_reason(self):
        data = {'resourceType': 'Goal', 'statusReason': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.statusReason is not None

    def test_from_dict_expressed_by(self):
        data = {'resourceType': 'Goal', 'expressedBy': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.expressedBy is not None

    def test_from_dict_addresses(self):
        data = {'resourceType': 'Goal', 'addresses': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.addresses is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'Goal', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.note is not None

    def test_from_dict_outcome_code(self):
        data = {'outcomeCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'}],
         'resourceType': 'Goal'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.outcomeCode is not None

    def test_from_dict_outcome_reference(self):
        data = {'resourceType': 'Goal', 'outcomeReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Goal)
        assert result.outcomeReference is not None


class TestGetPathGoal:

    def test_get_path_id(self):
        resource = Goal()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Goal()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Goal()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Goal.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Goal()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Goal()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Goal()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Goal()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Goal()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Goal()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Goal()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Goal()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_lifecycle_status(self):
        resource = Goal()
        resource.lifecycleStatus = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lifecycleStatus')
        assert result is not None

    def test_get_path_achievement_status(self):
        resource = Goal()
        resource.achievementStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'achievementStatus')
        assert result is not None

    def test_get_path_category(self):
        resource = Goal()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_priority(self):
        resource = Goal()
        resource.priority = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priority')
        assert result is not None

    def test_get_path_description(self):
        resource = Goal()
        resource.description = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_subject(self):
        resource = Goal()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_target(self):
        resource = Goal()
        resource.target = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'target')
        assert result is not None

    def test_get_path_status_date(self):
        resource = Goal()
        resource.statusDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'statusDate')
        assert result is not None

    def test_get_path_status_reason(self):
        resource = Goal()
        resource.statusReason = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'statusReason')
        assert result is not None

    def test_get_path_expressed_by(self):
        resource = Goal()
        resource.expressedBy = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'expressedBy')
        assert result is not None

    def test_get_path_addresses(self):
        resource = Goal()
        resource.addresses = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'addresses')
        assert result is not None

    def test_get_path_note(self):
        resource = Goal()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_outcome_code(self):
        resource = Goal()
        resource.outcomeCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'outcomeCode')
        assert result is not None

    def test_get_path_outcome_reference(self):
        resource = Goal()
        resource.outcomeReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'outcomeReference')
        assert result is not None


class TestSetPathGoal:

    def test_set_path_id(self):
        resource = Goal()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Goal()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Goal.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Goal()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Goal()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Goal()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Goal()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Goal()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Goal()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Goal()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Goal()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_lifecycle_status(self):
        resource = Goal()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lifecycleStatus', value)
        assert result is True
        assert resource.lifecycleStatus is not None

    def test_set_path_achievement_status(self):
        resource = Goal()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'achievementStatus', value)
        assert result is True
        assert resource.achievementStatus is not None

    def test_set_path_category(self):
        resource = Goal()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_priority(self):
        resource = Goal()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priority', value)
        assert result is True
        assert resource.priority is not None

    def test_set_path_description(self):
        resource = Goal()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_subject(self):
        resource = Goal()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_target(self):
        resource = Goal()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'target', value)
        assert result is True
        assert resource.target is not None

    def test_set_path_status_date(self):
        resource = Goal()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'statusDate', value)
        assert result is True
        assert resource.statusDate is not None

    def test_set_path_status_reason(self):
        resource = Goal()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'statusReason', value)
        assert result is True
        assert resource.statusReason is not None

    def test_set_path_expressed_by(self):
        resource = Goal()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'expressedBy', value)
        assert result is True
        assert resource.expressedBy is not None

    def test_set_path_addresses(self):
        resource = Goal()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'addresses', value)
        assert result is True
        assert resource.addresses is not None

    def test_set_path_note(self):
        resource = Goal()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_outcome_code(self):
        resource = Goal()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'outcomeCode', value)
        assert result is True
        assert resource.outcomeCode is not None

    def test_set_path_outcome_reference(self):
        resource = Goal()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'outcomeReference', value)
        assert result is True
        assert resource.outcomeReference is not None


class TestParsePathGoal:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Goal.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Goal.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Goal.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
