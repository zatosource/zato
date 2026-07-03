# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Appointment


class TestToDictAppointment:

    def test_to_dict_empty(self):
        resource = Appointment()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Appointment'

    def test_to_dict_with_id(self):
        resource = Appointment()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Appointment()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Appointment)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Appointment()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Appointment()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Appointment()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Appointment()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Appointment()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Appointment()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Appointment()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Appointment()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Appointment()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = Appointment()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_cancelation_reason(self):
        resource = Appointment()
        resource.cancelationReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'cancelationReason' in result

    def test_to_dict_service_category(self):
        resource = Appointment()
        resource.serviceCategory = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'serviceCategory' in result

    def test_to_dict_service_type(self):
        resource = Appointment()
        resource.serviceType = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'serviceType' in result

    def test_to_dict_specialty(self):
        resource = Appointment()
        resource.specialty = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'specialty' in result

    def test_to_dict_appointment_type(self):
        resource = Appointment()
        resource.appointmentType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'appointmentType' in result

    def test_to_dict_reason_code(self):
        resource = Appointment()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonCode' in result

    def test_to_dict_reason_reference(self):
        resource = Appointment()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonReference' in result

    def test_to_dict_priority(self):
        resource = Appointment()
        resource.priority = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priority' in result

    def test_to_dict_description(self):
        resource = Appointment()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_supporting_information(self):
        resource = Appointment()
        resource.supportingInformation = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supportingInformation' in result

    def test_to_dict_start(self):
        resource = Appointment()
        resource.start = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'start' in result

    def test_to_dict_end(self):
        resource = Appointment()
        resource.end = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'end' in result

    def test_to_dict_minutes_duration(self):
        resource = Appointment()
        resource.minutesDuration = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'minutesDuration' in result

    def test_to_dict_slot(self):
        resource = Appointment()
        resource.slot = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'slot' in result

    def test_to_dict_created(self):
        resource = Appointment()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'created' in result

    def test_to_dict_comment(self):
        resource = Appointment()
        resource.comment = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'comment' in result

    def test_to_dict_patient_instruction(self):
        resource = Appointment()
        resource.patientInstruction = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patientInstruction' in result

    def test_to_dict_based_on(self):
        resource = Appointment()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_participant(self):
        resource = Appointment()
        resource.participant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'participant' in result

    def test_to_dict_requested_period(self):
        resource = Appointment()
        resource.requestedPeriod = [{'start': '2024-01-01', 'end': '2024-12-31'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'requestedPeriod' in result


class TestFromDictAppointment:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Appointment', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert isinstance(result, Appointment)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Appointment'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert isinstance(result, Appointment)

    def test_from_dict_id(self):
        data = {'resourceType': 'Appointment', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Appointment', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Appointment', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Appointment', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Appointment', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Appointment', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Appointment', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Appointment', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Appointment', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Appointment', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.status is not None

    def test_from_dict_cancelation_reason(self):
        data = {'cancelationReason': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                               'text': 'Test concept'},
         'resourceType': 'Appointment'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.cancelationReason is not None

    def test_from_dict_service_category(self):
        data = {'resourceType': 'Appointment',
         'serviceCategory': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                              'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.serviceCategory is not None

    def test_from_dict_service_type(self):
        data = {'resourceType': 'Appointment',
         'serviceType': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.serviceType is not None

    def test_from_dict_specialty(self):
        data = {'resourceType': 'Appointment',
         'specialty': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                        'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.specialty is not None

    def test_from_dict_appointment_type(self):
        data = {'appointmentType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                             'text': 'Test concept'},
         'resourceType': 'Appointment'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.appointmentType is not None

    def test_from_dict_reason_code(self):
        data = {'reasonCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}],
         'resourceType': 'Appointment'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.reasonCode is not None

    def test_from_dict_reason_reference(self):
        data = {'resourceType': 'Appointment', 'reasonReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.reasonReference is not None

    def test_from_dict_priority(self):
        data = {'resourceType': 'Appointment', 'priority': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.priority is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'Appointment', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.description is not None

    def test_from_dict_supporting_information(self):
        data = {'resourceType': 'Appointment', 'supportingInformation': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.supportingInformation is not None

    def test_from_dict_start(self):
        data = {'resourceType': 'Appointment', 'start': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.start is not None

    def test_from_dict_end(self):
        data = {'resourceType': 'Appointment', 'end': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.end is not None

    def test_from_dict_minutes_duration(self):
        data = {'resourceType': 'Appointment', 'minutesDuration': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.minutesDuration is not None

    def test_from_dict_slot(self):
        data = {'resourceType': 'Appointment', 'slot': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.slot is not None

    def test_from_dict_created(self):
        data = {'resourceType': 'Appointment', 'created': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.created is not None

    def test_from_dict_comment(self):
        data = {'resourceType': 'Appointment', 'comment': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.comment is not None

    def test_from_dict_patient_instruction(self):
        data = {'resourceType': 'Appointment', 'patientInstruction': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.patientInstruction is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'Appointment', 'basedOn': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.basedOn is not None

    def test_from_dict_participant(self):
        data = {'resourceType': 'Appointment', 'participant': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.participant is not None

    def test_from_dict_requested_period(self):
        data = {'resourceType': 'Appointment', 'requestedPeriod': [{'start': '2024-01-01', 'end': '2024-12-31'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Appointment)
        assert result.requestedPeriod is not None


class TestGetPathAppointment:

    def test_get_path_id(self):
        resource = Appointment()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Appointment()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Appointment()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Appointment.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Appointment()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Appointment()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Appointment()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Appointment()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Appointment()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Appointment()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Appointment()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Appointment()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = Appointment()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_cancelation_reason(self):
        resource = Appointment()
        resource.cancelationReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'cancelationReason')
        assert result is not None

    def test_get_path_service_category(self):
        resource = Appointment()
        resource.serviceCategory = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'serviceCategory')
        assert result is not None

    def test_get_path_service_type(self):
        resource = Appointment()
        resource.serviceType = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'serviceType')
        assert result is not None

    def test_get_path_specialty(self):
        resource = Appointment()
        resource.specialty = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'specialty')
        assert result is not None

    def test_get_path_appointment_type(self):
        resource = Appointment()
        resource.appointmentType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'appointmentType')
        assert result is not None

    def test_get_path_reason_code(self):
        resource = Appointment()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonCode')
        assert result is not None

    def test_get_path_reason_reference(self):
        resource = Appointment()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonReference')
        assert result is not None

    def test_get_path_priority(self):
        resource = Appointment()
        resource.priority = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priority')
        assert result is not None

    def test_get_path_description(self):
        resource = Appointment()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_supporting_information(self):
        resource = Appointment()
        resource.supportingInformation = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supportingInformation')
        assert result is not None

    def test_get_path_start(self):
        resource = Appointment()
        resource.start = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'start')
        assert result is not None

    def test_get_path_end(self):
        resource = Appointment()
        resource.end = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'end')
        assert result is not None

    def test_get_path_minutes_duration(self):
        resource = Appointment()
        resource.minutesDuration = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'minutesDuration')
        assert result is not None

    def test_get_path_slot(self):
        resource = Appointment()
        resource.slot = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'slot')
        assert result is not None

    def test_get_path_created(self):
        resource = Appointment()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'created')
        assert result is not None

    def test_get_path_comment(self):
        resource = Appointment()
        resource.comment = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'comment')
        assert result is not None

    def test_get_path_patient_instruction(self):
        resource = Appointment()
        resource.patientInstruction = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patientInstruction')
        assert result is not None

    def test_get_path_based_on(self):
        resource = Appointment()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_participant(self):
        resource = Appointment()
        resource.participant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'participant')
        assert result is not None

    def test_get_path_requested_period(self):
        resource = Appointment()
        resource.requestedPeriod = [{'start': '2024-01-01', 'end': '2024-12-31'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'requestedPeriod')
        assert result is not None


class TestSetPathAppointment:

    def test_set_path_id(self):
        resource = Appointment()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Appointment()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Appointment.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Appointment()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Appointment()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Appointment()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Appointment()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Appointment()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Appointment()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Appointment()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Appointment()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = Appointment()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_cancelation_reason(self):
        resource = Appointment()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'cancelationReason', value)
        assert result is True
        assert resource.cancelationReason is not None

    def test_set_path_service_category(self):
        resource = Appointment()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'serviceCategory', value)
        assert result is True
        assert resource.serviceCategory is not None

    def test_set_path_service_type(self):
        resource = Appointment()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'serviceType', value)
        assert result is True
        assert resource.serviceType is not None

    def test_set_path_specialty(self):
        resource = Appointment()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'specialty', value)
        assert result is True
        assert resource.specialty is not None

    def test_set_path_appointment_type(self):
        resource = Appointment()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'appointmentType', value)
        assert result is True
        assert resource.appointmentType is not None

    def test_set_path_reason_code(self):
        resource = Appointment()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonCode', value)
        assert result is True
        assert resource.reasonCode is not None

    def test_set_path_reason_reference(self):
        resource = Appointment()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonReference', value)
        assert result is True
        assert resource.reasonReference is not None

    def test_set_path_priority(self):
        resource = Appointment()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priority', value)
        assert result is True
        assert resource.priority is not None

    def test_set_path_description(self):
        resource = Appointment()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_supporting_information(self):
        resource = Appointment()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supportingInformation', value)
        assert result is True
        assert resource.supportingInformation is not None

    def test_set_path_start(self):
        resource = Appointment()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'start', value)
        assert result is True
        assert resource.start is not None

    def test_set_path_end(self):
        resource = Appointment()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'end', value)
        assert result is True
        assert resource.end is not None

    def test_set_path_minutes_duration(self):
        resource = Appointment()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'minutesDuration', value)
        assert result is True
        assert resource.minutesDuration is not None

    def test_set_path_slot(self):
        resource = Appointment()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'slot', value)
        assert result is True
        assert resource.slot is not None

    def test_set_path_created(self):
        resource = Appointment()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'created', value)
        assert result is True
        assert resource.created is not None

    def test_set_path_comment(self):
        resource = Appointment()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'comment', value)
        assert result is True
        assert resource.comment is not None

    def test_set_path_patient_instruction(self):
        resource = Appointment()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patientInstruction', value)
        assert result is True
        assert resource.patientInstruction is not None

    def test_set_path_based_on(self):
        resource = Appointment()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_participant(self):
        resource = Appointment()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'participant', value)
        assert result is True
        assert resource.participant is not None

    def test_set_path_requested_period(self):
        resource = Appointment()
        value = [{'start': '2024-01-01', 'end': '2024-12-31'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'requestedPeriod', value)
        assert result is True
        assert resource.requestedPeriod is not None


class TestParsePathAppointment:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Appointment.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Appointment.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Appointment.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
