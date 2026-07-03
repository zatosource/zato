# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import CommunicationRequest


class TestToDictCommunicationRequest:

    def test_to_dict_empty(self):
        resource = CommunicationRequest()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'CommunicationRequest'

    def test_to_dict_with_id(self):
        resource = CommunicationRequest()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = CommunicationRequest()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, CommunicationRequest)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = CommunicationRequest()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = CommunicationRequest()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = CommunicationRequest()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = CommunicationRequest()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = CommunicationRequest()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = CommunicationRequest()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = CommunicationRequest()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = CommunicationRequest()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = CommunicationRequest()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_based_on(self):
        resource = CommunicationRequest()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_replaces(self):
        resource = CommunicationRequest()
        resource.replaces = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'replaces' in result

    def test_to_dict_group_identifier(self):
        resource = CommunicationRequest()
        resource.groupIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'groupIdentifier' in result

    def test_to_dict_status(self):
        resource = CommunicationRequest()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_status_reason(self):
        resource = CommunicationRequest()
        resource.statusReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'statusReason' in result

    def test_to_dict_category(self):
        resource = CommunicationRequest()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_priority(self):
        resource = CommunicationRequest()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priority' in result

    def test_to_dict_do_not_perform(self):
        resource = CommunicationRequest()
        resource.doNotPerform = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'doNotPerform' in result

    def test_to_dict_medium(self):
        resource = CommunicationRequest()
        resource.medium = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'medium' in result

    def test_to_dict_subject(self):
        resource = CommunicationRequest()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_about(self):
        resource = CommunicationRequest()
        resource.about = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'about' in result

    def test_to_dict_encounter(self):
        resource = CommunicationRequest()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_payload(self):
        resource = CommunicationRequest()
        resource.payload = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'payload' in result

    def test_to_dict_authored_on(self):
        resource = CommunicationRequest()
        resource.authoredOn = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'authoredOn' in result

    def test_to_dict_requester(self):
        resource = CommunicationRequest()
        resource.requester = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'requester' in result

    def test_to_dict_recipient(self):
        resource = CommunicationRequest()
        resource.recipient = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recipient' in result

    def test_to_dict_sender(self):
        resource = CommunicationRequest()
        resource.sender = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'sender' in result

    def test_to_dict_reason_code(self):
        resource = CommunicationRequest()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonCode' in result

    def test_to_dict_reason_reference(self):
        resource = CommunicationRequest()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonReference' in result

    def test_to_dict_note(self):
        resource = CommunicationRequest()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result


class TestFromDictCommunicationRequest:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'CommunicationRequest', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert isinstance(result, CommunicationRequest)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'CommunicationRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert isinstance(result, CommunicationRequest)

    def test_from_dict_id(self):
        data = {'resourceType': 'CommunicationRequest', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'CommunicationRequest', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'CommunicationRequest', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'CommunicationRequest', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'CommunicationRequest', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'CommunicationRequest', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'CommunicationRequest', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'CommunicationRequest', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'CommunicationRequest', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.identifier is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'CommunicationRequest', 'basedOn': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.basedOn is not None

    def test_from_dict_replaces(self):
        data = {'resourceType': 'CommunicationRequest', 'replaces': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.replaces is not None

    def test_from_dict_group_identifier(self):
        data = {'resourceType': 'CommunicationRequest', 'groupIdentifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.groupIdentifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'CommunicationRequest', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.status is not None

    def test_from_dict_status_reason(self):
        data = {'resourceType': 'CommunicationRequest',
         'statusReason': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.statusReason is not None

    def test_from_dict_category(self):
        data = {'category': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'CommunicationRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.category is not None

    def test_from_dict_priority(self):
        data = {'resourceType': 'CommunicationRequest', 'priority': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.priority is not None

    def test_from_dict_do_not_perform(self):
        data = {'resourceType': 'CommunicationRequest', 'doNotPerform': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.doNotPerform is not None

    def test_from_dict_medium(self):
        data = {'medium': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                     'text': 'Test concept'}],
         'resourceType': 'CommunicationRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.medium is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'CommunicationRequest', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.subject is not None

    def test_from_dict_about(self):
        data = {'resourceType': 'CommunicationRequest', 'about': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.about is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'CommunicationRequest', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.encounter is not None

    def test_from_dict_payload(self):
        data = {'resourceType': 'CommunicationRequest', 'payload': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.payload is not None

    def test_from_dict_authored_on(self):
        data = {'resourceType': 'CommunicationRequest', 'authoredOn': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.authoredOn is not None

    def test_from_dict_requester(self):
        data = {'resourceType': 'CommunicationRequest', 'requester': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.requester is not None

    def test_from_dict_recipient(self):
        data = {'resourceType': 'CommunicationRequest', 'recipient': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.recipient is not None

    def test_from_dict_sender(self):
        data = {'resourceType': 'CommunicationRequest', 'sender': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.sender is not None

    def test_from_dict_reason_code(self):
        data = {'reasonCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}],
         'resourceType': 'CommunicationRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.reasonCode is not None

    def test_from_dict_reason_reference(self):
        data = {'resourceType': 'CommunicationRequest', 'reasonReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.reasonReference is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'CommunicationRequest', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CommunicationRequest)
        assert result.note is not None


class TestGetPathCommunicationRequest:

    def test_get_path_id(self):
        resource = CommunicationRequest()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = CommunicationRequest()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = CommunicationRequest()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'CommunicationRequest.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = CommunicationRequest()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = CommunicationRequest()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = CommunicationRequest()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = CommunicationRequest()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = CommunicationRequest()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = CommunicationRequest()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = CommunicationRequest()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = CommunicationRequest()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_based_on(self):
        resource = CommunicationRequest()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_replaces(self):
        resource = CommunicationRequest()
        resource.replaces = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'replaces')
        assert result is not None

    def test_get_path_group_identifier(self):
        resource = CommunicationRequest()
        resource.groupIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'groupIdentifier')
        assert result is not None

    def test_get_path_status(self):
        resource = CommunicationRequest()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_status_reason(self):
        resource = CommunicationRequest()
        resource.statusReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'statusReason')
        assert result is not None

    def test_get_path_category(self):
        resource = CommunicationRequest()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_priority(self):
        resource = CommunicationRequest()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priority')
        assert result is not None

    def test_get_path_do_not_perform(self):
        resource = CommunicationRequest()
        resource.doNotPerform = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'doNotPerform')
        assert result is not None

    def test_get_path_medium(self):
        resource = CommunicationRequest()
        resource.medium = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'medium')
        assert result is not None

    def test_get_path_subject(self):
        resource = CommunicationRequest()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_about(self):
        resource = CommunicationRequest()
        resource.about = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'about')
        assert result is not None

    def test_get_path_encounter(self):
        resource = CommunicationRequest()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_payload(self):
        resource = CommunicationRequest()
        resource.payload = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'payload')
        assert result is not None

    def test_get_path_authored_on(self):
        resource = CommunicationRequest()
        resource.authoredOn = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'authoredOn')
        assert result is not None

    def test_get_path_requester(self):
        resource = CommunicationRequest()
        resource.requester = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'requester')
        assert result is not None

    def test_get_path_recipient(self):
        resource = CommunicationRequest()
        resource.recipient = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recipient')
        assert result is not None

    def test_get_path_sender(self):
        resource = CommunicationRequest()
        resource.sender = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'sender')
        assert result is not None

    def test_get_path_reason_code(self):
        resource = CommunicationRequest()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonCode')
        assert result is not None

    def test_get_path_reason_reference(self):
        resource = CommunicationRequest()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonReference')
        assert result is not None

    def test_get_path_note(self):
        resource = CommunicationRequest()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None


class TestSetPathCommunicationRequest:

    def test_set_path_id(self):
        resource = CommunicationRequest()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = CommunicationRequest()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'CommunicationRequest.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = CommunicationRequest()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = CommunicationRequest()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = CommunicationRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = CommunicationRequest()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = CommunicationRequest()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = CommunicationRequest()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = CommunicationRequest()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = CommunicationRequest()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_based_on(self):
        resource = CommunicationRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_replaces(self):
        resource = CommunicationRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'replaces', value)
        assert result is True
        assert resource.replaces is not None

    def test_set_path_group_identifier(self):
        resource = CommunicationRequest()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'groupIdentifier', value)
        assert result is True
        assert resource.groupIdentifier is not None

    def test_set_path_status(self):
        resource = CommunicationRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_status_reason(self):
        resource = CommunicationRequest()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'statusReason', value)
        assert result is True
        assert resource.statusReason is not None

    def test_set_path_category(self):
        resource = CommunicationRequest()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_priority(self):
        resource = CommunicationRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priority', value)
        assert result is True
        assert resource.priority is not None

    def test_set_path_do_not_perform(self):
        resource = CommunicationRequest()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'doNotPerform', value)
        assert result is True
        assert resource.doNotPerform is not None

    def test_set_path_medium(self):
        resource = CommunicationRequest()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'medium', value)
        assert result is True
        assert resource.medium is not None

    def test_set_path_subject(self):
        resource = CommunicationRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_about(self):
        resource = CommunicationRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'about', value)
        assert result is True
        assert resource.about is not None

    def test_set_path_encounter(self):
        resource = CommunicationRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_payload(self):
        resource = CommunicationRequest()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'payload', value)
        assert result is True
        assert resource.payload is not None

    def test_set_path_authored_on(self):
        resource = CommunicationRequest()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'authoredOn', value)
        assert result is True
        assert resource.authoredOn is not None

    def test_set_path_requester(self):
        resource = CommunicationRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'requester', value)
        assert result is True
        assert resource.requester is not None

    def test_set_path_recipient(self):
        resource = CommunicationRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recipient', value)
        assert result is True
        assert resource.recipient is not None

    def test_set_path_sender(self):
        resource = CommunicationRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'sender', value)
        assert result is True
        assert resource.sender is not None

    def test_set_path_reason_code(self):
        resource = CommunicationRequest()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonCode', value)
        assert result is True
        assert resource.reasonCode is not None

    def test_set_path_reason_reference(self):
        resource = CommunicationRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonReference', value)
        assert result is True
        assert resource.reasonReference is not None

    def test_set_path_note(self):
        resource = CommunicationRequest()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None


class TestParsePathCommunicationRequest:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('CommunicationRequest.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('CommunicationRequest.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('CommunicationRequest.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
