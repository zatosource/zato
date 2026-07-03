# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import devicemetricobservation


class TestToDictdevicemetricobservation:

    def test_to_dict_empty(self):
        resource = devicemetricobservation()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'devicemetricobservation'

    def test_to_dict_with_id(self):
        resource = devicemetricobservation()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = devicemetricobservation()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, devicemetricobservation)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = devicemetricobservation()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = devicemetricobservation()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = devicemetricobservation()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = devicemetricobservation()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = devicemetricobservation()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = devicemetricobservation()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = devicemetricobservation()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = devicemetricobservation()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = devicemetricobservation()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_based_on(self):
        resource = devicemetricobservation()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_part_of(self):
        resource = devicemetricobservation()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'partOf' in result

    def test_to_dict_status(self):
        resource = devicemetricobservation()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_category(self):
        resource = devicemetricobservation()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_code(self):
        resource = devicemetricobservation()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_subject(self):
        resource = devicemetricobservation()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_focus(self):
        resource = devicemetricobservation()
        resource.focus = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'focus' in result

    def test_to_dict_encounter(self):
        resource = devicemetricobservation()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_issued(self):
        resource = devicemetricobservation()
        resource.issued = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'issued' in result

    def test_to_dict_performer(self):
        resource = devicemetricobservation()
        resource.performer = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performer' in result

    def test_to_dict_data_absent_reason(self):
        resource = devicemetricobservation()
        resource.dataAbsentReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dataAbsentReason' in result

    def test_to_dict_interpretation(self):
        resource = devicemetricobservation()
        resource.interpretation = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'interpretation' in result

    def test_to_dict_note(self):
        resource = devicemetricobservation()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_body_site(self):
        resource = devicemetricobservation()
        resource.bodySite = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'bodySite' in result

    def test_to_dict_method(self):
        resource = devicemetricobservation()
        resource.method = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'method' in result

    def test_to_dict_specimen(self):
        resource = devicemetricobservation()
        resource.specimen = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'specimen' in result

    def test_to_dict_device(self):
        resource = devicemetricobservation()
        resource.device = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'device' in result

    def test_to_dict_reference_range(self):
        resource = devicemetricobservation()
        resource.referenceRange = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'referenceRange' in result

    def test_to_dict_has_member(self):
        resource = devicemetricobservation()
        resource.hasMember = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'hasMember' in result

    def test_to_dict_derived_from(self):
        resource = devicemetricobservation()
        resource.derivedFrom = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'derivedFrom' in result

    def test_to_dict_component(self):
        resource = devicemetricobservation()
        resource.component = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'component' in result


class TestFromDictdevicemetricobservation:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'devicemetricobservation', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert isinstance(result, devicemetricobservation)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'devicemetricobservation'}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert isinstance(result, devicemetricobservation)

    def test_from_dict_id(self):
        data = {'resourceType': 'devicemetricobservation', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'devicemetricobservation', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'devicemetricobservation', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'devicemetricobservation', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'devicemetricobservation', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'devicemetricobservation', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'devicemetricobservation', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'devicemetricobservation', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'devicemetricobservation', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.identifier is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'devicemetricobservation', 'basedOn': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.basedOn is not None

    def test_from_dict_part_of(self):
        data = {'resourceType': 'devicemetricobservation', 'partOf': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.partOf is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'devicemetricobservation', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.status is not None

    def test_from_dict_category(self):
        data = {'category': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'devicemetricobservation'}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.category is not None

    def test_from_dict_code(self):
        data = {'code': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'devicemetricobservation'}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.code is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'devicemetricobservation', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.subject is not None

    def test_from_dict_focus(self):
        data = {'resourceType': 'devicemetricobservation', 'focus': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.focus is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'devicemetricobservation', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.encounter is not None

    def test_from_dict_issued(self):
        data = {'resourceType': 'devicemetricobservation', 'issued': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.issued is not None

    def test_from_dict_performer(self):
        data = {'resourceType': 'devicemetricobservation', 'performer': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.performer is not None

    def test_from_dict_data_absent_reason(self):
        data = {'dataAbsentReason': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                              'text': 'Test concept'},
         'resourceType': 'devicemetricobservation'}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.dataAbsentReason is not None

    def test_from_dict_interpretation(self):
        data = {'interpretation': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                            'text': 'Test concept'},
         'resourceType': 'devicemetricobservation'}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.interpretation is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'devicemetricobservation', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.note is not None

    def test_from_dict_body_site(self):
        data = {'bodySite': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'devicemetricobservation'}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.bodySite is not None

    def test_from_dict_method(self):
        data = {'method': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'},
         'resourceType': 'devicemetricobservation'}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.method is not None

    def test_from_dict_specimen(self):
        data = {'resourceType': 'devicemetricobservation', 'specimen': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.specimen is not None

    def test_from_dict_device(self):
        data = {'resourceType': 'devicemetricobservation', 'device': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.device is not None

    def test_from_dict_reference_range(self):
        data = {'resourceType': 'devicemetricobservation', 'referenceRange': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.referenceRange is not None

    def test_from_dict_has_member(self):
        data = {'resourceType': 'devicemetricobservation', 'hasMember': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.hasMember is not None

    def test_from_dict_derived_from(self):
        data = {'resourceType': 'devicemetricobservation', 'derivedFrom': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.derivedFrom is not None

    def test_from_dict_component(self):
        data = {'resourceType': 'devicemetricobservation', 'component': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, devicemetricobservation)
        assert result.component is not None


class TestGetPathdevicemetricobservation:

    def test_get_path_id(self):
        resource = devicemetricobservation()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = devicemetricobservation()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = devicemetricobservation()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'devicemetricobservation.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = devicemetricobservation()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = devicemetricobservation()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = devicemetricobservation()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = devicemetricobservation()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = devicemetricobservation()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = devicemetricobservation()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = devicemetricobservation()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = devicemetricobservation()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_based_on(self):
        resource = devicemetricobservation()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_part_of(self):
        resource = devicemetricobservation()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'partOf')
        assert result is not None

    def test_get_path_status(self):
        resource = devicemetricobservation()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_category(self):
        resource = devicemetricobservation()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_code(self):
        resource = devicemetricobservation()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_subject(self):
        resource = devicemetricobservation()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_focus(self):
        resource = devicemetricobservation()
        resource.focus = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'focus')
        assert result is not None

    def test_get_path_encounter(self):
        resource = devicemetricobservation()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_issued(self):
        resource = devicemetricobservation()
        resource.issued = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'issued')
        assert result is not None

    def test_get_path_performer(self):
        resource = devicemetricobservation()
        resource.performer = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performer')
        assert result is not None

    def test_get_path_data_absent_reason(self):
        resource = devicemetricobservation()
        resource.dataAbsentReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dataAbsentReason')
        assert result is not None

    def test_get_path_interpretation(self):
        resource = devicemetricobservation()
        resource.interpretation = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'interpretation')
        assert result is not None

    def test_get_path_note(self):
        resource = devicemetricobservation()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_body_site(self):
        resource = devicemetricobservation()
        resource.bodySite = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'bodySite')
        assert result is not None

    def test_get_path_method(self):
        resource = devicemetricobservation()
        resource.method = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'method')
        assert result is not None

    def test_get_path_specimen(self):
        resource = devicemetricobservation()
        resource.specimen = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'specimen')
        assert result is not None

    def test_get_path_device(self):
        resource = devicemetricobservation()
        resource.device = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'device')
        assert result is not None

    def test_get_path_reference_range(self):
        resource = devicemetricobservation()
        resource.referenceRange = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'referenceRange')
        assert result is not None

    def test_get_path_has_member(self):
        resource = devicemetricobservation()
        resource.hasMember = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'hasMember')
        assert result is not None

    def test_get_path_derived_from(self):
        resource = devicemetricobservation()
        resource.derivedFrom = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'derivedFrom')
        assert result is not None

    def test_get_path_component(self):
        resource = devicemetricobservation()
        resource.component = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'component')
        assert result is not None


class TestSetPathdevicemetricobservation:

    def test_set_path_id(self):
        resource = devicemetricobservation()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = devicemetricobservation()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'devicemetricobservation.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = devicemetricobservation()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = devicemetricobservation()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = devicemetricobservation()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = devicemetricobservation()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = devicemetricobservation()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = devicemetricobservation()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = devicemetricobservation()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = devicemetricobservation()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_based_on(self):
        resource = devicemetricobservation()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_part_of(self):
        resource = devicemetricobservation()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'partOf', value)
        assert result is True
        assert resource.partOf is not None

    def test_set_path_status(self):
        resource = devicemetricobservation()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_category(self):
        resource = devicemetricobservation()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_code(self):
        resource = devicemetricobservation()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_subject(self):
        resource = devicemetricobservation()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_focus(self):
        resource = devicemetricobservation()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'focus', value)
        assert result is True
        assert resource.focus is not None

    def test_set_path_encounter(self):
        resource = devicemetricobservation()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_issued(self):
        resource = devicemetricobservation()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'issued', value)
        assert result is True
        assert resource.issued is not None

    def test_set_path_performer(self):
        resource = devicemetricobservation()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performer', value)
        assert result is True
        assert resource.performer is not None

    def test_set_path_data_absent_reason(self):
        resource = devicemetricobservation()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dataAbsentReason', value)
        assert result is True
        assert resource.dataAbsentReason is not None

    def test_set_path_interpretation(self):
        resource = devicemetricobservation()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'interpretation', value)
        assert result is True
        assert resource.interpretation is not None

    def test_set_path_note(self):
        resource = devicemetricobservation()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_body_site(self):
        resource = devicemetricobservation()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'bodySite', value)
        assert result is True
        assert resource.bodySite is not None

    def test_set_path_method(self):
        resource = devicemetricobservation()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'method', value)
        assert result is True
        assert resource.method is not None

    def test_set_path_specimen(self):
        resource = devicemetricobservation()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'specimen', value)
        assert result is True
        assert resource.specimen is not None

    def test_set_path_device(self):
        resource = devicemetricobservation()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'device', value)
        assert result is True
        assert resource.device is not None

    def test_set_path_reference_range(self):
        resource = devicemetricobservation()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'referenceRange', value)
        assert result is True
        assert resource.referenceRange is not None

    def test_set_path_has_member(self):
        resource = devicemetricobservation()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'hasMember', value)
        assert result is True
        assert resource.hasMember is not None

    def test_set_path_derived_from(self):
        resource = devicemetricobservation()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'derivedFrom', value)
        assert result is True
        assert resource.derivedFrom is not None

    def test_set_path_component(self):
        resource = devicemetricobservation()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'component', value)
        assert result is True
        assert resource.component is not None


class TestParsePathdevicemetricobservation:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('devicemetricobservation.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('devicemetricobservation.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('devicemetricobservation.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
