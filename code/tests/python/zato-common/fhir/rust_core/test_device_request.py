# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import DeviceRequest


class TestToDictDeviceRequest:

    def test_to_dict_empty(self):
        resource = DeviceRequest()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'DeviceRequest'

    def test_to_dict_with_id(self):
        resource = DeviceRequest()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = DeviceRequest()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, DeviceRequest)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = DeviceRequest()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = DeviceRequest()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = DeviceRequest()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = DeviceRequest()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = DeviceRequest()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = DeviceRequest()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = DeviceRequest()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = DeviceRequest()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = DeviceRequest()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_instantiates_canonical(self):
        resource = DeviceRequest()
        resource.instantiatesCanonical = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesCanonical' in result

    def test_to_dict_instantiates_uri(self):
        resource = DeviceRequest()
        resource.instantiatesUri = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesUri' in result

    def test_to_dict_based_on(self):
        resource = DeviceRequest()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_prior_request(self):
        resource = DeviceRequest()
        resource.priorRequest = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priorRequest' in result

    def test_to_dict_group_identifier(self):
        resource = DeviceRequest()
        resource.groupIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'groupIdentifier' in result

    def test_to_dict_status(self):
        resource = DeviceRequest()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_intent(self):
        resource = DeviceRequest()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'intent' in result

    def test_to_dict_priority(self):
        resource = DeviceRequest()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priority' in result

    def test_to_dict_parameter(self):
        resource = DeviceRequest()
        resource.parameter = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'parameter' in result

    def test_to_dict_subject(self):
        resource = DeviceRequest()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_encounter(self):
        resource = DeviceRequest()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_authored_on(self):
        resource = DeviceRequest()
        resource.authoredOn = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'authoredOn' in result

    def test_to_dict_requester(self):
        resource = DeviceRequest()
        resource.requester = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'requester' in result

    def test_to_dict_performer_type(self):
        resource = DeviceRequest()
        resource.performerType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performerType' in result

    def test_to_dict_performer(self):
        resource = DeviceRequest()
        resource.performer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performer' in result

    def test_to_dict_reason_code(self):
        resource = DeviceRequest()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonCode' in result

    def test_to_dict_reason_reference(self):
        resource = DeviceRequest()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonReference' in result

    def test_to_dict_insurance(self):
        resource = DeviceRequest()
        resource.insurance = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'insurance' in result

    def test_to_dict_supporting_info(self):
        resource = DeviceRequest()
        resource.supportingInfo = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supportingInfo' in result

    def test_to_dict_note(self):
        resource = DeviceRequest()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_relevant_history(self):
        resource = DeviceRequest()
        resource.relevantHistory = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relevantHistory' in result


class TestFromDictDeviceRequest:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'DeviceRequest', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert isinstance(result, DeviceRequest)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'DeviceRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert isinstance(result, DeviceRequest)

    def test_from_dict_id(self):
        data = {'resourceType': 'DeviceRequest', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'DeviceRequest', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'DeviceRequest', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'DeviceRequest', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'DeviceRequest', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'DeviceRequest', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'DeviceRequest', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'DeviceRequest', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'DeviceRequest', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.identifier is not None

    def test_from_dict_instantiates_canonical(self):
        data = {'resourceType': 'DeviceRequest', 'instantiatesCanonical': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.instantiatesCanonical is not None

    def test_from_dict_instantiates_uri(self):
        data = {'resourceType': 'DeviceRequest', 'instantiatesUri': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.instantiatesUri is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'DeviceRequest', 'basedOn': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.basedOn is not None

    def test_from_dict_prior_request(self):
        data = {'resourceType': 'DeviceRequest', 'priorRequest': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.priorRequest is not None

    def test_from_dict_group_identifier(self):
        data = {'resourceType': 'DeviceRequest', 'groupIdentifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.groupIdentifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'DeviceRequest', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.status is not None

    def test_from_dict_intent(self):
        data = {'resourceType': 'DeviceRequest', 'intent': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.intent is not None

    def test_from_dict_priority(self):
        data = {'resourceType': 'DeviceRequest', 'priority': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.priority is not None

    def test_from_dict_parameter(self):
        data = {'resourceType': 'DeviceRequest', 'parameter': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.parameter is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'DeviceRequest', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.subject is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'DeviceRequest', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.encounter is not None

    def test_from_dict_authored_on(self):
        data = {'resourceType': 'DeviceRequest', 'authoredOn': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.authoredOn is not None

    def test_from_dict_requester(self):
        data = {'resourceType': 'DeviceRequest', 'requester': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.requester is not None

    def test_from_dict_performer_type(self):
        data = {'performerType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'},
         'resourceType': 'DeviceRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.performerType is not None

    def test_from_dict_performer(self):
        data = {'resourceType': 'DeviceRequest', 'performer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.performer is not None

    def test_from_dict_reason_code(self):
        data = {'reasonCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}],
         'resourceType': 'DeviceRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.reasonCode is not None

    def test_from_dict_reason_reference(self):
        data = {'resourceType': 'DeviceRequest', 'reasonReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.reasonReference is not None

    def test_from_dict_insurance(self):
        data = {'resourceType': 'DeviceRequest', 'insurance': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.insurance is not None

    def test_from_dict_supporting_info(self):
        data = {'resourceType': 'DeviceRequest', 'supportingInfo': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.supportingInfo is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'DeviceRequest', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.note is not None

    def test_from_dict_relevant_history(self):
        data = {'resourceType': 'DeviceRequest', 'relevantHistory': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceRequest)
        assert result.relevantHistory is not None


class TestGetPathDeviceRequest:

    def test_get_path_id(self):
        resource = DeviceRequest()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = DeviceRequest()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = DeviceRequest()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'DeviceRequest.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = DeviceRequest()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = DeviceRequest()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = DeviceRequest()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = DeviceRequest()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = DeviceRequest()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = DeviceRequest()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = DeviceRequest()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = DeviceRequest()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_instantiates_canonical(self):
        resource = DeviceRequest()
        resource.instantiatesCanonical = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesCanonical')
        assert result is not None

    def test_get_path_instantiates_uri(self):
        resource = DeviceRequest()
        resource.instantiatesUri = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesUri')
        assert result is not None

    def test_get_path_based_on(self):
        resource = DeviceRequest()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_prior_request(self):
        resource = DeviceRequest()
        resource.priorRequest = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priorRequest')
        assert result is not None

    def test_get_path_group_identifier(self):
        resource = DeviceRequest()
        resource.groupIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'groupIdentifier')
        assert result is not None

    def test_get_path_status(self):
        resource = DeviceRequest()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_intent(self):
        resource = DeviceRequest()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'intent')
        assert result is not None

    def test_get_path_priority(self):
        resource = DeviceRequest()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priority')
        assert result is not None

    def test_get_path_parameter(self):
        resource = DeviceRequest()
        resource.parameter = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'parameter')
        assert result is not None

    def test_get_path_subject(self):
        resource = DeviceRequest()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_encounter(self):
        resource = DeviceRequest()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_authored_on(self):
        resource = DeviceRequest()
        resource.authoredOn = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'authoredOn')
        assert result is not None

    def test_get_path_requester(self):
        resource = DeviceRequest()
        resource.requester = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'requester')
        assert result is not None

    def test_get_path_performer_type(self):
        resource = DeviceRequest()
        resource.performerType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performerType')
        assert result is not None

    def test_get_path_performer(self):
        resource = DeviceRequest()
        resource.performer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performer')
        assert result is not None

    def test_get_path_reason_code(self):
        resource = DeviceRequest()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonCode')
        assert result is not None

    def test_get_path_reason_reference(self):
        resource = DeviceRequest()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonReference')
        assert result is not None

    def test_get_path_insurance(self):
        resource = DeviceRequest()
        resource.insurance = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'insurance')
        assert result is not None

    def test_get_path_supporting_info(self):
        resource = DeviceRequest()
        resource.supportingInfo = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supportingInfo')
        assert result is not None

    def test_get_path_note(self):
        resource = DeviceRequest()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_relevant_history(self):
        resource = DeviceRequest()
        resource.relevantHistory = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relevantHistory')
        assert result is not None


class TestSetPathDeviceRequest:

    def test_set_path_id(self):
        resource = DeviceRequest()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = DeviceRequest()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'DeviceRequest.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = DeviceRequest()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = DeviceRequest()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = DeviceRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = DeviceRequest()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = DeviceRequest()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = DeviceRequest()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = DeviceRequest()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = DeviceRequest()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_instantiates_canonical(self):
        resource = DeviceRequest()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesCanonical', value)
        assert result is True
        assert resource.instantiatesCanonical is not None

    def test_set_path_instantiates_uri(self):
        resource = DeviceRequest()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesUri', value)
        assert result is True
        assert resource.instantiatesUri is not None

    def test_set_path_based_on(self):
        resource = DeviceRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_prior_request(self):
        resource = DeviceRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priorRequest', value)
        assert result is True
        assert resource.priorRequest is not None

    def test_set_path_group_identifier(self):
        resource = DeviceRequest()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'groupIdentifier', value)
        assert result is True
        assert resource.groupIdentifier is not None

    def test_set_path_status(self):
        resource = DeviceRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_intent(self):
        resource = DeviceRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'intent', value)
        assert result is True
        assert resource.intent is not None

    def test_set_path_priority(self):
        resource = DeviceRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priority', value)
        assert result is True
        assert resource.priority is not None

    def test_set_path_parameter(self):
        resource = DeviceRequest()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'parameter', value)
        assert result is True
        assert resource.parameter is not None

    def test_set_path_subject(self):
        resource = DeviceRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_encounter(self):
        resource = DeviceRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_authored_on(self):
        resource = DeviceRequest()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'authoredOn', value)
        assert result is True
        assert resource.authoredOn is not None

    def test_set_path_requester(self):
        resource = DeviceRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'requester', value)
        assert result is True
        assert resource.requester is not None

    def test_set_path_performer_type(self):
        resource = DeviceRequest()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performerType', value)
        assert result is True
        assert resource.performerType is not None

    def test_set_path_performer(self):
        resource = DeviceRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performer', value)
        assert result is True
        assert resource.performer is not None

    def test_set_path_reason_code(self):
        resource = DeviceRequest()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonCode', value)
        assert result is True
        assert resource.reasonCode is not None

    def test_set_path_reason_reference(self):
        resource = DeviceRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonReference', value)
        assert result is True
        assert resource.reasonReference is not None

    def test_set_path_insurance(self):
        resource = DeviceRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'insurance', value)
        assert result is True
        assert resource.insurance is not None

    def test_set_path_supporting_info(self):
        resource = DeviceRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supportingInfo', value)
        assert result is True
        assert resource.supportingInfo is not None

    def test_set_path_note(self):
        resource = DeviceRequest()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_relevant_history(self):
        resource = DeviceRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relevantHistory', value)
        assert result is True
        assert resource.relevantHistory is not None


class TestParsePathDeviceRequest:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('DeviceRequest.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('DeviceRequest.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('DeviceRequest.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
