# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import RequestGroup


class TestToDictRequestGroup:

    def test_to_dict_empty(self):
        resource = RequestGroup()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'RequestGroup'

    def test_to_dict_with_id(self):
        resource = RequestGroup()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = RequestGroup()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, RequestGroup)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = RequestGroup()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = RequestGroup()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = RequestGroup()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = RequestGroup()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = RequestGroup()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = RequestGroup()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = RequestGroup()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = RequestGroup()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = RequestGroup()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_instantiates_canonical(self):
        resource = RequestGroup()
        resource.instantiatesCanonical = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesCanonical' in result

    def test_to_dict_instantiates_uri(self):
        resource = RequestGroup()
        resource.instantiatesUri = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesUri' in result

    def test_to_dict_based_on(self):
        resource = RequestGroup()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_replaces(self):
        resource = RequestGroup()
        resource.replaces = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'replaces' in result

    def test_to_dict_group_identifier(self):
        resource = RequestGroup()
        resource.groupIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'groupIdentifier' in result

    def test_to_dict_status(self):
        resource = RequestGroup()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_intent(self):
        resource = RequestGroup()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'intent' in result

    def test_to_dict_priority(self):
        resource = RequestGroup()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priority' in result

    def test_to_dict_code(self):
        resource = RequestGroup()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_subject(self):
        resource = RequestGroup()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_encounter(self):
        resource = RequestGroup()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_authored_on(self):
        resource = RequestGroup()
        resource.authoredOn = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'authoredOn' in result

    def test_to_dict_author(self):
        resource = RequestGroup()
        resource.author = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_reason_code(self):
        resource = RequestGroup()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonCode' in result

    def test_to_dict_reason_reference(self):
        resource = RequestGroup()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonReference' in result

    def test_to_dict_note(self):
        resource = RequestGroup()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_action(self):
        resource = RequestGroup()
        resource.action = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'action' in result


class TestFromDictRequestGroup:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'RequestGroup', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert isinstance(result, RequestGroup)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'RequestGroup'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert isinstance(result, RequestGroup)

    def test_from_dict_id(self):
        data = {'resourceType': 'RequestGroup', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'RequestGroup', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'RequestGroup', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'RequestGroup', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'RequestGroup', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'RequestGroup', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'RequestGroup', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'RequestGroup', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'RequestGroup', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.identifier is not None

    def test_from_dict_instantiates_canonical(self):
        data = {'resourceType': 'RequestGroup', 'instantiatesCanonical': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.instantiatesCanonical is not None

    def test_from_dict_instantiates_uri(self):
        data = {'resourceType': 'RequestGroup', 'instantiatesUri': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.instantiatesUri is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'RequestGroup', 'basedOn': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.basedOn is not None

    def test_from_dict_replaces(self):
        data = {'resourceType': 'RequestGroup', 'replaces': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.replaces is not None

    def test_from_dict_group_identifier(self):
        data = {'resourceType': 'RequestGroup', 'groupIdentifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.groupIdentifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'RequestGroup', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.status is not None

    def test_from_dict_intent(self):
        data = {'resourceType': 'RequestGroup', 'intent': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.intent is not None

    def test_from_dict_priority(self):
        data = {'resourceType': 'RequestGroup', 'priority': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.priority is not None

    def test_from_dict_code(self):
        data = {'code': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'RequestGroup'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.code is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'RequestGroup', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.subject is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'RequestGroup', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.encounter is not None

    def test_from_dict_authored_on(self):
        data = {'resourceType': 'RequestGroup', 'authoredOn': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.authoredOn is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'RequestGroup', 'author': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.author is not None

    def test_from_dict_reason_code(self):
        data = {'reasonCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}],
         'resourceType': 'RequestGroup'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.reasonCode is not None

    def test_from_dict_reason_reference(self):
        data = {'resourceType': 'RequestGroup', 'reasonReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.reasonReference is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'RequestGroup', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.note is not None

    def test_from_dict_action(self):
        data = {'resourceType': 'RequestGroup', 'action': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RequestGroup)
        assert result.action is not None


class TestGetPathRequestGroup:

    def test_get_path_id(self):
        resource = RequestGroup()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = RequestGroup()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = RequestGroup()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'RequestGroup.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = RequestGroup()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = RequestGroup()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = RequestGroup()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = RequestGroup()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = RequestGroup()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = RequestGroup()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = RequestGroup()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = RequestGroup()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_instantiates_canonical(self):
        resource = RequestGroup()
        resource.instantiatesCanonical = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesCanonical')
        assert result is not None

    def test_get_path_instantiates_uri(self):
        resource = RequestGroup()
        resource.instantiatesUri = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesUri')
        assert result is not None

    def test_get_path_based_on(self):
        resource = RequestGroup()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_replaces(self):
        resource = RequestGroup()
        resource.replaces = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'replaces')
        assert result is not None

    def test_get_path_group_identifier(self):
        resource = RequestGroup()
        resource.groupIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'groupIdentifier')
        assert result is not None

    def test_get_path_status(self):
        resource = RequestGroup()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_intent(self):
        resource = RequestGroup()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'intent')
        assert result is not None

    def test_get_path_priority(self):
        resource = RequestGroup()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priority')
        assert result is not None

    def test_get_path_code(self):
        resource = RequestGroup()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_subject(self):
        resource = RequestGroup()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_encounter(self):
        resource = RequestGroup()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_authored_on(self):
        resource = RequestGroup()
        resource.authoredOn = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'authoredOn')
        assert result is not None

    def test_get_path_author(self):
        resource = RequestGroup()
        resource.author = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_reason_code(self):
        resource = RequestGroup()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonCode')
        assert result is not None

    def test_get_path_reason_reference(self):
        resource = RequestGroup()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonReference')
        assert result is not None

    def test_get_path_note(self):
        resource = RequestGroup()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_action(self):
        resource = RequestGroup()
        resource.action = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'action')
        assert result is not None


class TestSetPathRequestGroup:

    def test_set_path_id(self):
        resource = RequestGroup()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = RequestGroup()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'RequestGroup.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = RequestGroup()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = RequestGroup()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = RequestGroup()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = RequestGroup()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = RequestGroup()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = RequestGroup()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = RequestGroup()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = RequestGroup()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_instantiates_canonical(self):
        resource = RequestGroup()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesCanonical', value)
        assert result is True
        assert resource.instantiatesCanonical is not None

    def test_set_path_instantiates_uri(self):
        resource = RequestGroup()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesUri', value)
        assert result is True
        assert resource.instantiatesUri is not None

    def test_set_path_based_on(self):
        resource = RequestGroup()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_replaces(self):
        resource = RequestGroup()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'replaces', value)
        assert result is True
        assert resource.replaces is not None

    def test_set_path_group_identifier(self):
        resource = RequestGroup()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'groupIdentifier', value)
        assert result is True
        assert resource.groupIdentifier is not None

    def test_set_path_status(self):
        resource = RequestGroup()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_intent(self):
        resource = RequestGroup()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'intent', value)
        assert result is True
        assert resource.intent is not None

    def test_set_path_priority(self):
        resource = RequestGroup()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priority', value)
        assert result is True
        assert resource.priority is not None

    def test_set_path_code(self):
        resource = RequestGroup()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_subject(self):
        resource = RequestGroup()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_encounter(self):
        resource = RequestGroup()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_authored_on(self):
        resource = RequestGroup()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'authoredOn', value)
        assert result is True
        assert resource.authoredOn is not None

    def test_set_path_author(self):
        resource = RequestGroup()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_reason_code(self):
        resource = RequestGroup()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonCode', value)
        assert result is True
        assert resource.reasonCode is not None

    def test_set_path_reason_reference(self):
        resource = RequestGroup()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonReference', value)
        assert result is True
        assert resource.reasonReference is not None

    def test_set_path_note(self):
        resource = RequestGroup()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_action(self):
        resource = RequestGroup()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'action', value)
        assert result is True
        assert resource.action is not None


class TestParsePathRequestGroup:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('RequestGroup.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('RequestGroup.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('RequestGroup.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
