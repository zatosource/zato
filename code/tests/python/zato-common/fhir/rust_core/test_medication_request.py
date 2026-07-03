# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import MedicationRequest


class TestToDictMedicationRequest:

    def test_to_dict_empty(self):
        resource = MedicationRequest()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'MedicationRequest'

    def test_to_dict_with_id(self):
        resource = MedicationRequest()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = MedicationRequest()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, MedicationRequest)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = MedicationRequest()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = MedicationRequest()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = MedicationRequest()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = MedicationRequest()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = MedicationRequest()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = MedicationRequest()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = MedicationRequest()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = MedicationRequest()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = MedicationRequest()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = MedicationRequest()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_status_reason(self):
        resource = MedicationRequest()
        resource.statusReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'statusReason' in result

    def test_to_dict_intent(self):
        resource = MedicationRequest()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'intent' in result

    def test_to_dict_category(self):
        resource = MedicationRequest()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_priority(self):
        resource = MedicationRequest()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priority' in result

    def test_to_dict_do_not_perform(self):
        resource = MedicationRequest()
        resource.doNotPerform = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'doNotPerform' in result

    def test_to_dict_subject(self):
        resource = MedicationRequest()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_encounter(self):
        resource = MedicationRequest()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_supporting_information(self):
        resource = MedicationRequest()
        resource.supportingInformation = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supportingInformation' in result

    def test_to_dict_authored_on(self):
        resource = MedicationRequest()
        resource.authoredOn = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'authoredOn' in result

    def test_to_dict_requester(self):
        resource = MedicationRequest()
        resource.requester = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'requester' in result

    def test_to_dict_performer(self):
        resource = MedicationRequest()
        resource.performer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performer' in result

    def test_to_dict_performer_type(self):
        resource = MedicationRequest()
        resource.performerType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performerType' in result

    def test_to_dict_recorder(self):
        resource = MedicationRequest()
        resource.recorder = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recorder' in result

    def test_to_dict_reason_code(self):
        resource = MedicationRequest()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonCode' in result

    def test_to_dict_reason_reference(self):
        resource = MedicationRequest()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonReference' in result

    def test_to_dict_instantiates_canonical(self):
        resource = MedicationRequest()
        resource.instantiatesCanonical = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesCanonical' in result

    def test_to_dict_instantiates_uri(self):
        resource = MedicationRequest()
        resource.instantiatesUri = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesUri' in result

    def test_to_dict_based_on(self):
        resource = MedicationRequest()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_group_identifier(self):
        resource = MedicationRequest()
        resource.groupIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'groupIdentifier' in result

    def test_to_dict_course_of_therapy_type(self):
        resource = MedicationRequest()
        resource.courseOfTherapyType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'courseOfTherapyType' in result

    def test_to_dict_insurance(self):
        resource = MedicationRequest()
        resource.insurance = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'insurance' in result

    def test_to_dict_note(self):
        resource = MedicationRequest()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_dosage_instruction(self):
        resource = MedicationRequest()
        resource.dosageInstruction = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dosageInstruction' in result

    def test_to_dict_dispense_request(self):
        resource = MedicationRequest()
        resource.dispenseRequest = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dispenseRequest' in result

    def test_to_dict_substitution(self):
        resource = MedicationRequest()
        resource.substitution = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'substitution' in result

    def test_to_dict_prior_prescription(self):
        resource = MedicationRequest()
        resource.priorPrescription = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priorPrescription' in result

    def test_to_dict_detected_issue(self):
        resource = MedicationRequest()
        resource.detectedIssue = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'detectedIssue' in result

    def test_to_dict_event_history(self):
        resource = MedicationRequest()
        resource.eventHistory = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'eventHistory' in result


class TestFromDictMedicationRequest:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'MedicationRequest', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert isinstance(result, MedicationRequest)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'MedicationRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert isinstance(result, MedicationRequest)

    def test_from_dict_id(self):
        data = {'resourceType': 'MedicationRequest', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'MedicationRequest', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'MedicationRequest', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'MedicationRequest', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'MedicationRequest', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'MedicationRequest', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'MedicationRequest', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'MedicationRequest', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'MedicationRequest', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'MedicationRequest', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.status is not None

    def test_from_dict_status_reason(self):
        data = {'resourceType': 'MedicationRequest',
         'statusReason': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.statusReason is not None

    def test_from_dict_intent(self):
        data = {'resourceType': 'MedicationRequest', 'intent': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.intent is not None

    def test_from_dict_category(self):
        data = {'category': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'MedicationRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.category is not None

    def test_from_dict_priority(self):
        data = {'resourceType': 'MedicationRequest', 'priority': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.priority is not None

    def test_from_dict_do_not_perform(self):
        data = {'resourceType': 'MedicationRequest', 'doNotPerform': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.doNotPerform is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'MedicationRequest', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.subject is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'MedicationRequest', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.encounter is not None

    def test_from_dict_supporting_information(self):
        data = {'resourceType': 'MedicationRequest', 'supportingInformation': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.supportingInformation is not None

    def test_from_dict_authored_on(self):
        data = {'resourceType': 'MedicationRequest', 'authoredOn': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.authoredOn is not None

    def test_from_dict_requester(self):
        data = {'resourceType': 'MedicationRequest', 'requester': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.requester is not None

    def test_from_dict_performer(self):
        data = {'resourceType': 'MedicationRequest', 'performer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.performer is not None

    def test_from_dict_performer_type(self):
        data = {'performerType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'},
         'resourceType': 'MedicationRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.performerType is not None

    def test_from_dict_recorder(self):
        data = {'resourceType': 'MedicationRequest', 'recorder': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.recorder is not None

    def test_from_dict_reason_code(self):
        data = {'reasonCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}],
         'resourceType': 'MedicationRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.reasonCode is not None

    def test_from_dict_reason_reference(self):
        data = {'resourceType': 'MedicationRequest', 'reasonReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.reasonReference is not None

    def test_from_dict_instantiates_canonical(self):
        data = {'resourceType': 'MedicationRequest', 'instantiatesCanonical': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.instantiatesCanonical is not None

    def test_from_dict_instantiates_uri(self):
        data = {'resourceType': 'MedicationRequest', 'instantiatesUri': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.instantiatesUri is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'MedicationRequest', 'basedOn': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.basedOn is not None

    def test_from_dict_group_identifier(self):
        data = {'resourceType': 'MedicationRequest', 'groupIdentifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.groupIdentifier is not None

    def test_from_dict_course_of_therapy_type(self):
        data = {'courseOfTherapyType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                 'text': 'Test concept'},
         'resourceType': 'MedicationRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.courseOfTherapyType is not None

    def test_from_dict_insurance(self):
        data = {'resourceType': 'MedicationRequest', 'insurance': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.insurance is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'MedicationRequest', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.note is not None

    def test_from_dict_dosage_instruction(self):
        data = {'resourceType': 'MedicationRequest', 'dosageInstruction': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.dosageInstruction is not None

    def test_from_dict_dispense_request(self):
        data = {'resourceType': 'MedicationRequest', 'dispenseRequest': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.dispenseRequest is not None

    def test_from_dict_substitution(self):
        data = {'resourceType': 'MedicationRequest', 'substitution': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.substitution is not None

    def test_from_dict_prior_prescription(self):
        data = {'resourceType': 'MedicationRequest', 'priorPrescription': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.priorPrescription is not None

    def test_from_dict_detected_issue(self):
        data = {'resourceType': 'MedicationRequest', 'detectedIssue': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.detectedIssue is not None

    def test_from_dict_event_history(self):
        data = {'resourceType': 'MedicationRequest', 'eventHistory': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationRequest)
        assert result.eventHistory is not None


class TestGetPathMedicationRequest:

    def test_get_path_id(self):
        resource = MedicationRequest()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = MedicationRequest()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = MedicationRequest()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'MedicationRequest.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = MedicationRequest()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = MedicationRequest()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = MedicationRequest()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = MedicationRequest()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = MedicationRequest()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = MedicationRequest()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = MedicationRequest()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = MedicationRequest()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = MedicationRequest()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_status_reason(self):
        resource = MedicationRequest()
        resource.statusReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'statusReason')
        assert result is not None

    def test_get_path_intent(self):
        resource = MedicationRequest()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'intent')
        assert result is not None

    def test_get_path_category(self):
        resource = MedicationRequest()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_priority(self):
        resource = MedicationRequest()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priority')
        assert result is not None

    def test_get_path_do_not_perform(self):
        resource = MedicationRequest()
        resource.doNotPerform = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'doNotPerform')
        assert result is not None

    def test_get_path_subject(self):
        resource = MedicationRequest()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_encounter(self):
        resource = MedicationRequest()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_supporting_information(self):
        resource = MedicationRequest()
        resource.supportingInformation = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supportingInformation')
        assert result is not None

    def test_get_path_authored_on(self):
        resource = MedicationRequest()
        resource.authoredOn = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'authoredOn')
        assert result is not None

    def test_get_path_requester(self):
        resource = MedicationRequest()
        resource.requester = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'requester')
        assert result is not None

    def test_get_path_performer(self):
        resource = MedicationRequest()
        resource.performer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performer')
        assert result is not None

    def test_get_path_performer_type(self):
        resource = MedicationRequest()
        resource.performerType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performerType')
        assert result is not None

    def test_get_path_recorder(self):
        resource = MedicationRequest()
        resource.recorder = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recorder')
        assert result is not None

    def test_get_path_reason_code(self):
        resource = MedicationRequest()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonCode')
        assert result is not None

    def test_get_path_reason_reference(self):
        resource = MedicationRequest()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonReference')
        assert result is not None

    def test_get_path_instantiates_canonical(self):
        resource = MedicationRequest()
        resource.instantiatesCanonical = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesCanonical')
        assert result is not None

    def test_get_path_instantiates_uri(self):
        resource = MedicationRequest()
        resource.instantiatesUri = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesUri')
        assert result is not None

    def test_get_path_based_on(self):
        resource = MedicationRequest()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_group_identifier(self):
        resource = MedicationRequest()
        resource.groupIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'groupIdentifier')
        assert result is not None

    def test_get_path_course_of_therapy_type(self):
        resource = MedicationRequest()
        resource.courseOfTherapyType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'courseOfTherapyType')
        assert result is not None

    def test_get_path_insurance(self):
        resource = MedicationRequest()
        resource.insurance = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'insurance')
        assert result is not None

    def test_get_path_note(self):
        resource = MedicationRequest()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_dosage_instruction(self):
        resource = MedicationRequest()
        resource.dosageInstruction = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dosageInstruction')
        assert result is not None

    def test_get_path_dispense_request(self):
        resource = MedicationRequest()
        resource.dispenseRequest = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dispenseRequest')
        assert result is not None

    def test_get_path_substitution(self):
        resource = MedicationRequest()
        resource.substitution = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'substitution')
        assert result is not None

    def test_get_path_prior_prescription(self):
        resource = MedicationRequest()
        resource.priorPrescription = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priorPrescription')
        assert result is not None

    def test_get_path_detected_issue(self):
        resource = MedicationRequest()
        resource.detectedIssue = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'detectedIssue')
        assert result is not None

    def test_get_path_event_history(self):
        resource = MedicationRequest()
        resource.eventHistory = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'eventHistory')
        assert result is not None


class TestSetPathMedicationRequest:

    def test_set_path_id(self):
        resource = MedicationRequest()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = MedicationRequest()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'MedicationRequest.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = MedicationRequest()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = MedicationRequest()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = MedicationRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = MedicationRequest()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = MedicationRequest()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = MedicationRequest()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = MedicationRequest()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = MedicationRequest()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = MedicationRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_status_reason(self):
        resource = MedicationRequest()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'statusReason', value)
        assert result is True
        assert resource.statusReason is not None

    def test_set_path_intent(self):
        resource = MedicationRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'intent', value)
        assert result is True
        assert resource.intent is not None

    def test_set_path_category(self):
        resource = MedicationRequest()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_priority(self):
        resource = MedicationRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priority', value)
        assert result is True
        assert resource.priority is not None

    def test_set_path_do_not_perform(self):
        resource = MedicationRequest()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'doNotPerform', value)
        assert result is True
        assert resource.doNotPerform is not None

    def test_set_path_subject(self):
        resource = MedicationRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_encounter(self):
        resource = MedicationRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_supporting_information(self):
        resource = MedicationRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supportingInformation', value)
        assert result is True
        assert resource.supportingInformation is not None

    def test_set_path_authored_on(self):
        resource = MedicationRequest()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'authoredOn', value)
        assert result is True
        assert resource.authoredOn is not None

    def test_set_path_requester(self):
        resource = MedicationRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'requester', value)
        assert result is True
        assert resource.requester is not None

    def test_set_path_performer(self):
        resource = MedicationRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performer', value)
        assert result is True
        assert resource.performer is not None

    def test_set_path_performer_type(self):
        resource = MedicationRequest()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performerType', value)
        assert result is True
        assert resource.performerType is not None

    def test_set_path_recorder(self):
        resource = MedicationRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recorder', value)
        assert result is True
        assert resource.recorder is not None

    def test_set_path_reason_code(self):
        resource = MedicationRequest()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonCode', value)
        assert result is True
        assert resource.reasonCode is not None

    def test_set_path_reason_reference(self):
        resource = MedicationRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonReference', value)
        assert result is True
        assert resource.reasonReference is not None

    def test_set_path_instantiates_canonical(self):
        resource = MedicationRequest()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesCanonical', value)
        assert result is True
        assert resource.instantiatesCanonical is not None

    def test_set_path_instantiates_uri(self):
        resource = MedicationRequest()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesUri', value)
        assert result is True
        assert resource.instantiatesUri is not None

    def test_set_path_based_on(self):
        resource = MedicationRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_group_identifier(self):
        resource = MedicationRequest()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'groupIdentifier', value)
        assert result is True
        assert resource.groupIdentifier is not None

    def test_set_path_course_of_therapy_type(self):
        resource = MedicationRequest()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'courseOfTherapyType', value)
        assert result is True
        assert resource.courseOfTherapyType is not None

    def test_set_path_insurance(self):
        resource = MedicationRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'insurance', value)
        assert result is True
        assert resource.insurance is not None

    def test_set_path_note(self):
        resource = MedicationRequest()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_dosage_instruction(self):
        resource = MedicationRequest()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dosageInstruction', value)
        assert result is True
        assert resource.dosageInstruction is not None

    def test_set_path_dispense_request(self):
        resource = MedicationRequest()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dispenseRequest', value)
        assert result is True
        assert resource.dispenseRequest is not None

    def test_set_path_substitution(self):
        resource = MedicationRequest()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'substitution', value)
        assert result is True
        assert resource.substitution is not None

    def test_set_path_prior_prescription(self):
        resource = MedicationRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priorPrescription', value)
        assert result is True
        assert resource.priorPrescription is not None

    def test_set_path_detected_issue(self):
        resource = MedicationRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'detectedIssue', value)
        assert result is True
        assert resource.detectedIssue is not None

    def test_set_path_event_history(self):
        resource = MedicationRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'eventHistory', value)
        assert result is True
        assert resource.eventHistory is not None


class TestParsePathMedicationRequest:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicationRequest.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicationRequest.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicationRequest.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
