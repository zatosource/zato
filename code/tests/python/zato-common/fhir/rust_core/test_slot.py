# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Slot


class TestToDictSlot:

    def test_to_dict_empty(self):
        resource = Slot()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Slot'

    def test_to_dict_with_id(self):
        resource = Slot()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Slot()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Slot)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Slot()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Slot()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Slot()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Slot()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Slot()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Slot()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Slot()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Slot()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Slot()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_service_category(self):
        resource = Slot()
        resource.serviceCategory = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'serviceCategory' in result

    def test_to_dict_service_type(self):
        resource = Slot()
        resource.serviceType = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'serviceType' in result

    def test_to_dict_specialty(self):
        resource = Slot()
        resource.specialty = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'specialty' in result

    def test_to_dict_appointment_type(self):
        resource = Slot()
        resource.appointmentType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'appointmentType' in result

    def test_to_dict_schedule(self):
        resource = Slot()
        resource.schedule = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'schedule' in result

    def test_to_dict_status(self):
        resource = Slot()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_start(self):
        resource = Slot()
        resource.start = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'start' in result

    def test_to_dict_end(self):
        resource = Slot()
        resource.end = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'end' in result

    def test_to_dict_overbooked(self):
        resource = Slot()
        resource.overbooked = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'overbooked' in result

    def test_to_dict_comment(self):
        resource = Slot()
        resource.comment = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'comment' in result


class TestFromDictSlot:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Slot', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert isinstance(result, Slot)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Slot'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert isinstance(result, Slot)

    def test_from_dict_id(self):
        data = {'resourceType': 'Slot', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Slot', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Slot', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Slot', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Slot', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Slot', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Slot', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Slot', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Slot', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.identifier is not None

    def test_from_dict_service_category(self):
        data = {'resourceType': 'Slot',
         'serviceCategory': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                              'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.serviceCategory is not None

    def test_from_dict_service_type(self):
        data = {'resourceType': 'Slot',
         'serviceType': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.serviceType is not None

    def test_from_dict_specialty(self):
        data = {'resourceType': 'Slot',
         'specialty': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                        'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.specialty is not None

    def test_from_dict_appointment_type(self):
        data = {'appointmentType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                             'text': 'Test concept'},
         'resourceType': 'Slot'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.appointmentType is not None

    def test_from_dict_schedule(self):
        data = {'resourceType': 'Slot', 'schedule': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.schedule is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Slot', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.status is not None

    def test_from_dict_start(self):
        data = {'resourceType': 'Slot', 'start': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.start is not None

    def test_from_dict_end(self):
        data = {'resourceType': 'Slot', 'end': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.end is not None

    def test_from_dict_overbooked(self):
        data = {'resourceType': 'Slot', 'overbooked': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.overbooked is not None

    def test_from_dict_comment(self):
        data = {'resourceType': 'Slot', 'comment': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Slot)
        assert result.comment is not None


class TestGetPathSlot:

    def test_get_path_id(self):
        resource = Slot()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Slot()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Slot()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Slot.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Slot()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Slot()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Slot()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Slot()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Slot()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Slot()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Slot()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Slot()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_service_category(self):
        resource = Slot()
        resource.serviceCategory = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'serviceCategory')
        assert result is not None

    def test_get_path_service_type(self):
        resource = Slot()
        resource.serviceType = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'serviceType')
        assert result is not None

    def test_get_path_specialty(self):
        resource = Slot()
        resource.specialty = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'specialty')
        assert result is not None

    def test_get_path_appointment_type(self):
        resource = Slot()
        resource.appointmentType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'appointmentType')
        assert result is not None

    def test_get_path_schedule(self):
        resource = Slot()
        resource.schedule = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'schedule')
        assert result is not None

    def test_get_path_status(self):
        resource = Slot()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_start(self):
        resource = Slot()
        resource.start = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'start')
        assert result is not None

    def test_get_path_end(self):
        resource = Slot()
        resource.end = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'end')
        assert result is not None

    def test_get_path_overbooked(self):
        resource = Slot()
        resource.overbooked = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'overbooked')
        assert result is not None

    def test_get_path_comment(self):
        resource = Slot()
        resource.comment = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'comment')
        assert result is not None


class TestSetPathSlot:

    def test_set_path_id(self):
        resource = Slot()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Slot()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Slot.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Slot()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Slot()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Slot()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Slot()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Slot()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Slot()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Slot()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Slot()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_service_category(self):
        resource = Slot()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'serviceCategory', value)
        assert result is True
        assert resource.serviceCategory is not None

    def test_set_path_service_type(self):
        resource = Slot()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'serviceType', value)
        assert result is True
        assert resource.serviceType is not None

    def test_set_path_specialty(self):
        resource = Slot()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'specialty', value)
        assert result is True
        assert resource.specialty is not None

    def test_set_path_appointment_type(self):
        resource = Slot()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'appointmentType', value)
        assert result is True
        assert resource.appointmentType is not None

    def test_set_path_schedule(self):
        resource = Slot()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'schedule', value)
        assert result is True
        assert resource.schedule is not None

    def test_set_path_status(self):
        resource = Slot()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_start(self):
        resource = Slot()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'start', value)
        assert result is True
        assert resource.start is not None

    def test_set_path_end(self):
        resource = Slot()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'end', value)
        assert result is True
        assert resource.end is not None

    def test_set_path_overbooked(self):
        resource = Slot()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'overbooked', value)
        assert result is True
        assert resource.overbooked is not None

    def test_set_path_comment(self):
        resource = Slot()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'comment', value)
        assert result is True
        assert resource.comment is not None


class TestParsePathSlot:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Slot.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Slot.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Slot.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
