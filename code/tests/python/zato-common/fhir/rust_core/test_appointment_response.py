# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import AppointmentResponse


class TestToDictAppointmentResponse:

    def test_to_dict_empty(self):
        resource = AppointmentResponse()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'AppointmentResponse'

    def test_to_dict_with_id(self):
        resource = AppointmentResponse()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = AppointmentResponse()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, AppointmentResponse)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = AppointmentResponse()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = AppointmentResponse()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = AppointmentResponse()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = AppointmentResponse()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = AppointmentResponse()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = AppointmentResponse()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = AppointmentResponse()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = AppointmentResponse()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = AppointmentResponse()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_appointment(self):
        resource = AppointmentResponse()
        resource.appointment = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'appointment' in result

    def test_to_dict_start(self):
        resource = AppointmentResponse()
        resource.start = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'start' in result

    def test_to_dict_end(self):
        resource = AppointmentResponse()
        resource.end = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'end' in result

    def test_to_dict_participant_type(self):
        resource = AppointmentResponse()
        resource.participantType = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'participantType' in result

    def test_to_dict_actor(self):
        resource = AppointmentResponse()
        resource.actor = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'actor' in result

    def test_to_dict_participant_status(self):
        resource = AppointmentResponse()
        resource.participantStatus = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'participantStatus' in result

    def test_to_dict_comment(self):
        resource = AppointmentResponse()
        resource.comment = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'comment' in result


class TestFromDictAppointmentResponse:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'AppointmentResponse', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert isinstance(result, AppointmentResponse)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'AppointmentResponse'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert isinstance(result, AppointmentResponse)

    def test_from_dict_id(self):
        data = {'resourceType': 'AppointmentResponse', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'AppointmentResponse', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'AppointmentResponse', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'AppointmentResponse', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'AppointmentResponse', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'AppointmentResponse', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'AppointmentResponse', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'AppointmentResponse', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'AppointmentResponse', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.identifier is not None

    def test_from_dict_appointment(self):
        data = {'resourceType': 'AppointmentResponse', 'appointment': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.appointment is not None

    def test_from_dict_start(self):
        data = {'resourceType': 'AppointmentResponse', 'start': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.start is not None

    def test_from_dict_end(self):
        data = {'resourceType': 'AppointmentResponse', 'end': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.end is not None

    def test_from_dict_participant_type(self):
        data = {'participantType': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                              'text': 'Test concept'}],
         'resourceType': 'AppointmentResponse'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.participantType is not None

    def test_from_dict_actor(self):
        data = {'resourceType': 'AppointmentResponse', 'actor': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.actor is not None

    def test_from_dict_participant_status(self):
        data = {'resourceType': 'AppointmentResponse', 'participantStatus': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.participantStatus is not None

    def test_from_dict_comment(self):
        data = {'resourceType': 'AppointmentResponse', 'comment': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AppointmentResponse)
        assert result.comment is not None


class TestGetPathAppointmentResponse:

    def test_get_path_id(self):
        resource = AppointmentResponse()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = AppointmentResponse()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = AppointmentResponse()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'AppointmentResponse.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = AppointmentResponse()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = AppointmentResponse()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = AppointmentResponse()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = AppointmentResponse()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = AppointmentResponse()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = AppointmentResponse()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = AppointmentResponse()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = AppointmentResponse()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_appointment(self):
        resource = AppointmentResponse()
        resource.appointment = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'appointment')
        assert result is not None

    def test_get_path_start(self):
        resource = AppointmentResponse()
        resource.start = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'start')
        assert result is not None

    def test_get_path_end(self):
        resource = AppointmentResponse()
        resource.end = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'end')
        assert result is not None

    def test_get_path_participant_type(self):
        resource = AppointmentResponse()
        resource.participantType = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'participantType')
        assert result is not None

    def test_get_path_actor(self):
        resource = AppointmentResponse()
        resource.actor = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'actor')
        assert result is not None

    def test_get_path_participant_status(self):
        resource = AppointmentResponse()
        resource.participantStatus = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'participantStatus')
        assert result is not None

    def test_get_path_comment(self):
        resource = AppointmentResponse()
        resource.comment = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'comment')
        assert result is not None


class TestSetPathAppointmentResponse:

    def test_set_path_id(self):
        resource = AppointmentResponse()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = AppointmentResponse()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'AppointmentResponse.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = AppointmentResponse()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = AppointmentResponse()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = AppointmentResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = AppointmentResponse()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = AppointmentResponse()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = AppointmentResponse()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = AppointmentResponse()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = AppointmentResponse()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_appointment(self):
        resource = AppointmentResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'appointment', value)
        assert result is True
        assert resource.appointment is not None

    def test_set_path_start(self):
        resource = AppointmentResponse()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'start', value)
        assert result is True
        assert resource.start is not None

    def test_set_path_end(self):
        resource = AppointmentResponse()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'end', value)
        assert result is True
        assert resource.end is not None

    def test_set_path_participant_type(self):
        resource = AppointmentResponse()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'participantType', value)
        assert result is True
        assert resource.participantType is not None

    def test_set_path_actor(self):
        resource = AppointmentResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'actor', value)
        assert result is True
        assert resource.actor is not None

    def test_set_path_participant_status(self):
        resource = AppointmentResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'participantStatus', value)
        assert result is True
        assert resource.participantStatus is not None

    def test_set_path_comment(self):
        resource = AppointmentResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'comment', value)
        assert result is True
        assert resource.comment is not None


class TestParsePathAppointmentResponse:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('AppointmentResponse.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('AppointmentResponse.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('AppointmentResponse.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
