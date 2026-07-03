# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import MedicationDispense


class TestToDictMedicationDispense:

    def test_to_dict_empty(self):
        resource = MedicationDispense()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'MedicationDispense'

    def test_to_dict_with_id(self):
        resource = MedicationDispense()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = MedicationDispense()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, MedicationDispense)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = MedicationDispense()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = MedicationDispense()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = MedicationDispense()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = MedicationDispense()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = MedicationDispense()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = MedicationDispense()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = MedicationDispense()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = MedicationDispense()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = MedicationDispense()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_part_of(self):
        resource = MedicationDispense()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'partOf' in result

    def test_to_dict_status(self):
        resource = MedicationDispense()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_category(self):
        resource = MedicationDispense()
        resource.category = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_subject(self):
        resource = MedicationDispense()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_context(self):
        resource = MedicationDispense()
        resource.context = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'context' in result

    def test_to_dict_supporting_information(self):
        resource = MedicationDispense()
        resource.supportingInformation = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supportingInformation' in result

    def test_to_dict_performer(self):
        resource = MedicationDispense()
        resource.performer = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performer' in result

    def test_to_dict_location(self):
        resource = MedicationDispense()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'location' in result

    def test_to_dict_authorizing_prescription(self):
        resource = MedicationDispense()
        resource.authorizingPrescription = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'authorizingPrescription' in result

    def test_to_dict_type(self):
        resource = MedicationDispense()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_quantity(self):
        resource = MedicationDispense()
        resource.quantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'quantity' in result

    def test_to_dict_days_supply(self):
        resource = MedicationDispense()
        resource.daysSupply = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'daysSupply' in result

    def test_to_dict_when_prepared(self):
        resource = MedicationDispense()
        resource.whenPrepared = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'whenPrepared' in result

    def test_to_dict_when_handed_over(self):
        resource = MedicationDispense()
        resource.whenHandedOver = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'whenHandedOver' in result

    def test_to_dict_destination(self):
        resource = MedicationDispense()
        resource.destination = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'destination' in result

    def test_to_dict_receiver(self):
        resource = MedicationDispense()
        resource.receiver = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'receiver' in result

    def test_to_dict_note(self):
        resource = MedicationDispense()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_dosage_instruction(self):
        resource = MedicationDispense()
        resource.dosageInstruction = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dosageInstruction' in result

    def test_to_dict_substitution(self):
        resource = MedicationDispense()
        resource.substitution = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'substitution' in result

    def test_to_dict_detected_issue(self):
        resource = MedicationDispense()
        resource.detectedIssue = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'detectedIssue' in result

    def test_to_dict_event_history(self):
        resource = MedicationDispense()
        resource.eventHistory = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'eventHistory' in result


class TestFromDictMedicationDispense:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'MedicationDispense', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert isinstance(result, MedicationDispense)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'MedicationDispense'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert isinstance(result, MedicationDispense)

    def test_from_dict_id(self):
        data = {'resourceType': 'MedicationDispense', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'MedicationDispense', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'MedicationDispense', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'MedicationDispense', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'MedicationDispense', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'MedicationDispense', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'MedicationDispense', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'MedicationDispense', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'MedicationDispense', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.identifier is not None

    def test_from_dict_part_of(self):
        data = {'resourceType': 'MedicationDispense', 'partOf': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.partOf is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'MedicationDispense', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.status is not None

    def test_from_dict_category(self):
        data = {'category': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'MedicationDispense'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.category is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'MedicationDispense', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.subject is not None

    def test_from_dict_context(self):
        data = {'resourceType': 'MedicationDispense', 'context': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.context is not None

    def test_from_dict_supporting_information(self):
        data = {'resourceType': 'MedicationDispense', 'supportingInformation': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.supportingInformation is not None

    def test_from_dict_performer(self):
        data = {'resourceType': 'MedicationDispense', 'performer': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.performer is not None

    def test_from_dict_location(self):
        data = {'resourceType': 'MedicationDispense', 'location': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.location is not None

    def test_from_dict_authorizing_prescription(self):
        data = {'resourceType': 'MedicationDispense', 'authorizingPrescription': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.authorizingPrescription is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'MedicationDispense',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.type_ is not None

    def test_from_dict_quantity(self):
        data = {'resourceType': 'MedicationDispense', 'quantity': {'value': 100, 'unit': 'mg'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.quantity is not None

    def test_from_dict_days_supply(self):
        data = {'resourceType': 'MedicationDispense', 'daysSupply': {'value': 100, 'unit': 'mg'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.daysSupply is not None

    def test_from_dict_when_prepared(self):
        data = {'resourceType': 'MedicationDispense', 'whenPrepared': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.whenPrepared is not None

    def test_from_dict_when_handed_over(self):
        data = {'resourceType': 'MedicationDispense', 'whenHandedOver': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.whenHandedOver is not None

    def test_from_dict_destination(self):
        data = {'resourceType': 'MedicationDispense', 'destination': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.destination is not None

    def test_from_dict_receiver(self):
        data = {'resourceType': 'MedicationDispense', 'receiver': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.receiver is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'MedicationDispense', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.note is not None

    def test_from_dict_dosage_instruction(self):
        data = {'resourceType': 'MedicationDispense', 'dosageInstruction': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.dosageInstruction is not None

    def test_from_dict_substitution(self):
        data = {'resourceType': 'MedicationDispense', 'substitution': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.substitution is not None

    def test_from_dict_detected_issue(self):
        data = {'resourceType': 'MedicationDispense', 'detectedIssue': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.detectedIssue is not None

    def test_from_dict_event_history(self):
        data = {'resourceType': 'MedicationDispense', 'eventHistory': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationDispense)
        assert result.eventHistory is not None


class TestGetPathMedicationDispense:

    def test_get_path_id(self):
        resource = MedicationDispense()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = MedicationDispense()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = MedicationDispense()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'MedicationDispense.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = MedicationDispense()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = MedicationDispense()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = MedicationDispense()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = MedicationDispense()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = MedicationDispense()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = MedicationDispense()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = MedicationDispense()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = MedicationDispense()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_part_of(self):
        resource = MedicationDispense()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'partOf')
        assert result is not None

    def test_get_path_status(self):
        resource = MedicationDispense()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_category(self):
        resource = MedicationDispense()
        resource.category = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_subject(self):
        resource = MedicationDispense()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_context(self):
        resource = MedicationDispense()
        resource.context = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'context')
        assert result is not None

    def test_get_path_supporting_information(self):
        resource = MedicationDispense()
        resource.supportingInformation = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supportingInformation')
        assert result is not None

    def test_get_path_performer(self):
        resource = MedicationDispense()
        resource.performer = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performer')
        assert result is not None

    def test_get_path_location(self):
        resource = MedicationDispense()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'location')
        assert result is not None

    def test_get_path_authorizing_prescription(self):
        resource = MedicationDispense()
        resource.authorizingPrescription = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'authorizingPrescription')
        assert result is not None

    def test_get_path_type(self):
        resource = MedicationDispense()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_quantity(self):
        resource = MedicationDispense()
        resource.quantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'quantity')
        assert result is not None

    def test_get_path_days_supply(self):
        resource = MedicationDispense()
        resource.daysSupply = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'daysSupply')
        assert result is not None

    def test_get_path_when_prepared(self):
        resource = MedicationDispense()
        resource.whenPrepared = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'whenPrepared')
        assert result is not None

    def test_get_path_when_handed_over(self):
        resource = MedicationDispense()
        resource.whenHandedOver = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'whenHandedOver')
        assert result is not None

    def test_get_path_destination(self):
        resource = MedicationDispense()
        resource.destination = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'destination')
        assert result is not None

    def test_get_path_receiver(self):
        resource = MedicationDispense()
        resource.receiver = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'receiver')
        assert result is not None

    def test_get_path_note(self):
        resource = MedicationDispense()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_dosage_instruction(self):
        resource = MedicationDispense()
        resource.dosageInstruction = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dosageInstruction')
        assert result is not None

    def test_get_path_substitution(self):
        resource = MedicationDispense()
        resource.substitution = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'substitution')
        assert result is not None

    def test_get_path_detected_issue(self):
        resource = MedicationDispense()
        resource.detectedIssue = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'detectedIssue')
        assert result is not None

    def test_get_path_event_history(self):
        resource = MedicationDispense()
        resource.eventHistory = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'eventHistory')
        assert result is not None


class TestSetPathMedicationDispense:

    def test_set_path_id(self):
        resource = MedicationDispense()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = MedicationDispense()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'MedicationDispense.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = MedicationDispense()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = MedicationDispense()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = MedicationDispense()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = MedicationDispense()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = MedicationDispense()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = MedicationDispense()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = MedicationDispense()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = MedicationDispense()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_part_of(self):
        resource = MedicationDispense()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'partOf', value)
        assert result is True
        assert resource.partOf is not None

    def test_set_path_status(self):
        resource = MedicationDispense()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_category(self):
        resource = MedicationDispense()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_subject(self):
        resource = MedicationDispense()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_context(self):
        resource = MedicationDispense()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'context', value)
        assert result is True
        assert resource.context is not None

    def test_set_path_supporting_information(self):
        resource = MedicationDispense()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supportingInformation', value)
        assert result is True
        assert resource.supportingInformation is not None

    def test_set_path_performer(self):
        resource = MedicationDispense()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performer', value)
        assert result is True
        assert resource.performer is not None

    def test_set_path_location(self):
        resource = MedicationDispense()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'location', value)
        assert result is True
        assert resource.location is not None

    def test_set_path_authorizing_prescription(self):
        resource = MedicationDispense()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'authorizingPrescription', value)
        assert result is True
        assert resource.authorizingPrescription is not None

    def test_set_path_type(self):
        resource = MedicationDispense()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_quantity(self):
        resource = MedicationDispense()
        value = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'quantity', value)
        assert result is True
        assert resource.quantity is not None

    def test_set_path_days_supply(self):
        resource = MedicationDispense()
        value = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'daysSupply', value)
        assert result is True
        assert resource.daysSupply is not None

    def test_set_path_when_prepared(self):
        resource = MedicationDispense()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'whenPrepared', value)
        assert result is True
        assert resource.whenPrepared is not None

    def test_set_path_when_handed_over(self):
        resource = MedicationDispense()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'whenHandedOver', value)
        assert result is True
        assert resource.whenHandedOver is not None

    def test_set_path_destination(self):
        resource = MedicationDispense()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'destination', value)
        assert result is True
        assert resource.destination is not None

    def test_set_path_receiver(self):
        resource = MedicationDispense()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'receiver', value)
        assert result is True
        assert resource.receiver is not None

    def test_set_path_note(self):
        resource = MedicationDispense()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_dosage_instruction(self):
        resource = MedicationDispense()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dosageInstruction', value)
        assert result is True
        assert resource.dosageInstruction is not None

    def test_set_path_substitution(self):
        resource = MedicationDispense()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'substitution', value)
        assert result is True
        assert resource.substitution is not None

    def test_set_path_detected_issue(self):
        resource = MedicationDispense()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'detectedIssue', value)
        assert result is True
        assert resource.detectedIssue is not None

    def test_set_path_event_history(self):
        resource = MedicationDispense()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'eventHistory', value)
        assert result is True
        assert resource.eventHistory is not None


class TestParsePathMedicationDispense:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicationDispense.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicationDispense.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicationDispense.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
