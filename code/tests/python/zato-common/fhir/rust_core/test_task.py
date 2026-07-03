# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Task


class TestToDictTask:

    def test_to_dict_empty(self):
        resource = Task()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Task'

    def test_to_dict_with_id(self):
        resource = Task()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Task()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Task)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Task()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Task()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Task()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Task()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Task()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Task()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Task()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Task()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Task()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_instantiates_canonical(self):
        resource = Task()
        resource.instantiatesCanonical = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesCanonical' in result

    def test_to_dict_instantiates_uri(self):
        resource = Task()
        resource.instantiatesUri = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesUri' in result

    def test_to_dict_based_on(self):
        resource = Task()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_group_identifier(self):
        resource = Task()
        resource.groupIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'groupIdentifier' in result

    def test_to_dict_part_of(self):
        resource = Task()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'partOf' in result

    def test_to_dict_status(self):
        resource = Task()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_status_reason(self):
        resource = Task()
        resource.statusReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'statusReason' in result

    def test_to_dict_business_status(self):
        resource = Task()
        resource.businessStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'businessStatus' in result

    def test_to_dict_intent(self):
        resource = Task()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'intent' in result

    def test_to_dict_priority(self):
        resource = Task()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priority' in result

    def test_to_dict_code(self):
        resource = Task()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_description(self):
        resource = Task()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_focus(self):
        resource = Task()
        resource.focus = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'focus' in result

    def test_to_dict_for(self):
        resource = Task()
        resource.for_ = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'for' in result

    def test_to_dict_encounter(self):
        resource = Task()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_execution_period(self):
        resource = Task()
        resource.executionPeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'executionPeriod' in result

    def test_to_dict_authored_on(self):
        resource = Task()
        resource.authoredOn = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'authoredOn' in result

    def test_to_dict_last_modified(self):
        resource = Task()
        resource.lastModified = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lastModified' in result

    def test_to_dict_requester(self):
        resource = Task()
        resource.requester = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'requester' in result

    def test_to_dict_performer_type(self):
        resource = Task()
        resource.performerType = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performerType' in result

    def test_to_dict_owner(self):
        resource = Task()
        resource.owner = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'owner' in result

    def test_to_dict_location(self):
        resource = Task()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'location' in result

    def test_to_dict_reason_code(self):
        resource = Task()
        resource.reasonCode = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonCode' in result

    def test_to_dict_reason_reference(self):
        resource = Task()
        resource.reasonReference = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonReference' in result

    def test_to_dict_insurance(self):
        resource = Task()
        resource.insurance = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'insurance' in result

    def test_to_dict_note(self):
        resource = Task()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_relevant_history(self):
        resource = Task()
        resource.relevantHistory = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relevantHistory' in result

    def test_to_dict_restriction(self):
        resource = Task()
        resource.restriction = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'restriction' in result

    def test_to_dict_input(self):
        resource = Task()
        resource.input = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'input' in result

    def test_to_dict_output(self):
        resource = Task()
        resource.output = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'output' in result


class TestFromDictTask:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Task', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert isinstance(result, Task)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Task'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert isinstance(result, Task)

    def test_from_dict_id(self):
        data = {'resourceType': 'Task', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Task', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Task', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Task', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Task', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Task', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Task', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Task', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Task', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.identifier is not None

    def test_from_dict_instantiates_canonical(self):
        data = {'resourceType': 'Task', 'instantiatesCanonical': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.instantiatesCanonical is not None

    def test_from_dict_instantiates_uri(self):
        data = {'resourceType': 'Task', 'instantiatesUri': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.instantiatesUri is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'Task', 'basedOn': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.basedOn is not None

    def test_from_dict_group_identifier(self):
        data = {'resourceType': 'Task', 'groupIdentifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.groupIdentifier is not None

    def test_from_dict_part_of(self):
        data = {'resourceType': 'Task', 'partOf': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.partOf is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Task', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.status is not None

    def test_from_dict_status_reason(self):
        data = {'resourceType': 'Task',
         'statusReason': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.statusReason is not None

    def test_from_dict_business_status(self):
        data = {'businessStatus': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                            'text': 'Test concept'},
         'resourceType': 'Task'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.businessStatus is not None

    def test_from_dict_intent(self):
        data = {'resourceType': 'Task', 'intent': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.intent is not None

    def test_from_dict_priority(self):
        data = {'resourceType': 'Task', 'priority': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.priority is not None

    def test_from_dict_code(self):
        data = {'resourceType': 'Task', 'code': {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.code is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'Task', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.description is not None

    def test_from_dict_focus(self):
        data = {'resourceType': 'Task', 'focus': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.focus is not None

    def test_from_dict_for(self):
        data = {'resourceType': 'Task', 'for': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.for_ is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'Task', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.encounter is not None

    def test_from_dict_execution_period(self):
        data = {'resourceType': 'Task', 'executionPeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.executionPeriod is not None

    def test_from_dict_authored_on(self):
        data = {'resourceType': 'Task', 'authoredOn': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.authoredOn is not None

    def test_from_dict_last_modified(self):
        data = {'resourceType': 'Task', 'lastModified': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.lastModified is not None

    def test_from_dict_requester(self):
        data = {'resourceType': 'Task', 'requester': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.requester is not None

    def test_from_dict_performer_type(self):
        data = {'performerType': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                            'text': 'Test concept'}],
         'resourceType': 'Task'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.performerType is not None

    def test_from_dict_owner(self):
        data = {'resourceType': 'Task', 'owner': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.owner is not None

    def test_from_dict_location(self):
        data = {'resourceType': 'Task', 'location': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.location is not None

    def test_from_dict_reason_code(self):
        data = {'reasonCode': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                        'text': 'Test concept'},
         'resourceType': 'Task'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.reasonCode is not None

    def test_from_dict_reason_reference(self):
        data = {'resourceType': 'Task', 'reasonReference': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.reasonReference is not None

    def test_from_dict_insurance(self):
        data = {'resourceType': 'Task', 'insurance': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.insurance is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'Task', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.note is not None

    def test_from_dict_relevant_history(self):
        data = {'resourceType': 'Task', 'relevantHistory': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.relevantHistory is not None

    def test_from_dict_restriction(self):
        data = {'resourceType': 'Task', 'restriction': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.restriction is not None

    def test_from_dict_input(self):
        data = {'resourceType': 'Task', 'input': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.input is not None

    def test_from_dict_output(self):
        data = {'resourceType': 'Task', 'output': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Task)
        assert result.output is not None


class TestGetPathTask:

    def test_get_path_id(self):
        resource = Task()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Task()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Task()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Task.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Task()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Task()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Task()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Task()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Task()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Task()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Task()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Task()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_instantiates_canonical(self):
        resource = Task()
        resource.instantiatesCanonical = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesCanonical')
        assert result is not None

    def test_get_path_instantiates_uri(self):
        resource = Task()
        resource.instantiatesUri = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesUri')
        assert result is not None

    def test_get_path_based_on(self):
        resource = Task()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_group_identifier(self):
        resource = Task()
        resource.groupIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'groupIdentifier')
        assert result is not None

    def test_get_path_part_of(self):
        resource = Task()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'partOf')
        assert result is not None

    def test_get_path_status(self):
        resource = Task()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_status_reason(self):
        resource = Task()
        resource.statusReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'statusReason')
        assert result is not None

    def test_get_path_business_status(self):
        resource = Task()
        resource.businessStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'businessStatus')
        assert result is not None

    def test_get_path_intent(self):
        resource = Task()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'intent')
        assert result is not None

    def test_get_path_priority(self):
        resource = Task()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priority')
        assert result is not None

    def test_get_path_code(self):
        resource = Task()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_description(self):
        resource = Task()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_focus(self):
        resource = Task()
        resource.focus = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'focus')
        assert result is not None

    def test_get_path_for(self):
        resource = Task()
        resource.for_ = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'for')
        assert result is not None

    def test_get_path_encounter(self):
        resource = Task()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_execution_period(self):
        resource = Task()
        resource.executionPeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'executionPeriod')
        assert result is not None

    def test_get_path_authored_on(self):
        resource = Task()
        resource.authoredOn = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'authoredOn')
        assert result is not None

    def test_get_path_last_modified(self):
        resource = Task()
        resource.lastModified = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lastModified')
        assert result is not None

    def test_get_path_requester(self):
        resource = Task()
        resource.requester = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'requester')
        assert result is not None

    def test_get_path_performer_type(self):
        resource = Task()
        resource.performerType = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performerType')
        assert result is not None

    def test_get_path_owner(self):
        resource = Task()
        resource.owner = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'owner')
        assert result is not None

    def test_get_path_location(self):
        resource = Task()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'location')
        assert result is not None

    def test_get_path_reason_code(self):
        resource = Task()
        resource.reasonCode = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonCode')
        assert result is not None

    def test_get_path_reason_reference(self):
        resource = Task()
        resource.reasonReference = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonReference')
        assert result is not None

    def test_get_path_insurance(self):
        resource = Task()
        resource.insurance = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'insurance')
        assert result is not None

    def test_get_path_note(self):
        resource = Task()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_relevant_history(self):
        resource = Task()
        resource.relevantHistory = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relevantHistory')
        assert result is not None

    def test_get_path_restriction(self):
        resource = Task()
        resource.restriction = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'restriction')
        assert result is not None

    def test_get_path_input(self):
        resource = Task()
        resource.input = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'input')
        assert result is not None

    def test_get_path_output(self):
        resource = Task()
        resource.output = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'output')
        assert result is not None


class TestSetPathTask:

    def test_set_path_id(self):
        resource = Task()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Task()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Task.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Task()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Task()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Task()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Task()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Task()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Task()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Task()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Task()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_instantiates_canonical(self):
        resource = Task()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesCanonical', value)
        assert result is True
        assert resource.instantiatesCanonical is not None

    def test_set_path_instantiates_uri(self):
        resource = Task()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesUri', value)
        assert result is True
        assert resource.instantiatesUri is not None

    def test_set_path_based_on(self):
        resource = Task()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_group_identifier(self):
        resource = Task()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'groupIdentifier', value)
        assert result is True
        assert resource.groupIdentifier is not None

    def test_set_path_part_of(self):
        resource = Task()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'partOf', value)
        assert result is True
        assert resource.partOf is not None

    def test_set_path_status(self):
        resource = Task()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_status_reason(self):
        resource = Task()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'statusReason', value)
        assert result is True
        assert resource.statusReason is not None

    def test_set_path_business_status(self):
        resource = Task()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'businessStatus', value)
        assert result is True
        assert resource.businessStatus is not None

    def test_set_path_intent(self):
        resource = Task()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'intent', value)
        assert result is True
        assert resource.intent is not None

    def test_set_path_priority(self):
        resource = Task()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priority', value)
        assert result is True
        assert resource.priority is not None

    def test_set_path_code(self):
        resource = Task()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_description(self):
        resource = Task()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_focus(self):
        resource = Task()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'focus', value)
        assert result is True
        assert resource.focus is not None

    def test_set_path_for(self):
        resource = Task()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'for', value)
        assert result is True
        assert resource.for_ is not None

    def test_set_path_encounter(self):
        resource = Task()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_execution_period(self):
        resource = Task()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'executionPeriod', value)
        assert result is True
        assert resource.executionPeriod is not None

    def test_set_path_authored_on(self):
        resource = Task()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'authoredOn', value)
        assert result is True
        assert resource.authoredOn is not None

    def test_set_path_last_modified(self):
        resource = Task()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lastModified', value)
        assert result is True
        assert resource.lastModified is not None

    def test_set_path_requester(self):
        resource = Task()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'requester', value)
        assert result is True
        assert resource.requester is not None

    def test_set_path_performer_type(self):
        resource = Task()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performerType', value)
        assert result is True
        assert resource.performerType is not None

    def test_set_path_owner(self):
        resource = Task()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'owner', value)
        assert result is True
        assert resource.owner is not None

    def test_set_path_location(self):
        resource = Task()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'location', value)
        assert result is True
        assert resource.location is not None

    def test_set_path_reason_code(self):
        resource = Task()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonCode', value)
        assert result is True
        assert resource.reasonCode is not None

    def test_set_path_reason_reference(self):
        resource = Task()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonReference', value)
        assert result is True
        assert resource.reasonReference is not None

    def test_set_path_insurance(self):
        resource = Task()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'insurance', value)
        assert result is True
        assert resource.insurance is not None

    def test_set_path_note(self):
        resource = Task()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_relevant_history(self):
        resource = Task()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relevantHistory', value)
        assert result is True
        assert resource.relevantHistory is not None

    def test_set_path_restriction(self):
        resource = Task()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'restriction', value)
        assert result is True
        assert resource.restriction is not None

    def test_set_path_input(self):
        resource = Task()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'input', value)
        assert result is True
        assert resource.input is not None

    def test_set_path_output(self):
        resource = Task()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'output', value)
        assert result is True
        assert resource.output is not None


class TestParsePathTask:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Task.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Task.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Task.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
