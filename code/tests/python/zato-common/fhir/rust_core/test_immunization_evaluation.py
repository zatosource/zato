# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ImmunizationEvaluation


class TestToDictImmunizationEvaluation:

    def test_to_dict_empty(self):
        resource = ImmunizationEvaluation()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ImmunizationEvaluation'

    def test_to_dict_with_id(self):
        resource = ImmunizationEvaluation()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ImmunizationEvaluation()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ImmunizationEvaluation)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ImmunizationEvaluation()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ImmunizationEvaluation()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ImmunizationEvaluation()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ImmunizationEvaluation()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ImmunizationEvaluation()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ImmunizationEvaluation()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ImmunizationEvaluation()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ImmunizationEvaluation()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = ImmunizationEvaluation()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = ImmunizationEvaluation()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_patient(self):
        resource = ImmunizationEvaluation()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_date(self):
        resource = ImmunizationEvaluation()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_authority(self):
        resource = ImmunizationEvaluation()
        resource.authority = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'authority' in result

    def test_to_dict_target_disease(self):
        resource = ImmunizationEvaluation()
        resource.targetDisease = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'targetDisease' in result

    def test_to_dict_immunization_event(self):
        resource = ImmunizationEvaluation()
        resource.immunizationEvent = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'immunizationEvent' in result

    def test_to_dict_dose_status(self):
        resource = ImmunizationEvaluation()
        resource.doseStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'doseStatus' in result

    def test_to_dict_dose_status_reason(self):
        resource = ImmunizationEvaluation()
        resource.doseStatusReason = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'doseStatusReason' in result

    def test_to_dict_description(self):
        resource = ImmunizationEvaluation()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_series(self):
        resource = ImmunizationEvaluation()
        resource.series = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'series' in result


class TestFromDictImmunizationEvaluation:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert isinstance(result, ImmunizationEvaluation)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ImmunizationEvaluation'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert isinstance(result, ImmunizationEvaluation)

    def test_from_dict_id(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.status is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.patient is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.date is not None

    def test_from_dict_authority(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'authority': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.authority is not None

    def test_from_dict_target_disease(self):
        data = {'resourceType': 'ImmunizationEvaluation',
         'targetDisease': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.targetDisease is not None

    def test_from_dict_immunization_event(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'immunizationEvent': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.immunizationEvent is not None

    def test_from_dict_dose_status(self):
        data = {'doseStatus': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                        'text': 'Test concept'},
         'resourceType': 'ImmunizationEvaluation'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.doseStatus is not None

    def test_from_dict_dose_status_reason(self):
        data = {'doseStatusReason': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                               'text': 'Test concept'}],
         'resourceType': 'ImmunizationEvaluation'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.doseStatusReason is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.description is not None

    def test_from_dict_series(self):
        data = {'resourceType': 'ImmunizationEvaluation', 'series': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationEvaluation)
        assert result.series is not None


class TestGetPathImmunizationEvaluation:

    def test_get_path_id(self):
        resource = ImmunizationEvaluation()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ImmunizationEvaluation()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ImmunizationEvaluation()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ImmunizationEvaluation.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ImmunizationEvaluation()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ImmunizationEvaluation()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ImmunizationEvaluation()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ImmunizationEvaluation()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ImmunizationEvaluation()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ImmunizationEvaluation()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ImmunizationEvaluation()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = ImmunizationEvaluation()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = ImmunizationEvaluation()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_patient(self):
        resource = ImmunizationEvaluation()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_date(self):
        resource = ImmunizationEvaluation()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_authority(self):
        resource = ImmunizationEvaluation()
        resource.authority = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'authority')
        assert result is not None

    def test_get_path_target_disease(self):
        resource = ImmunizationEvaluation()
        resource.targetDisease = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'targetDisease')
        assert result is not None

    def test_get_path_immunization_event(self):
        resource = ImmunizationEvaluation()
        resource.immunizationEvent = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'immunizationEvent')
        assert result is not None

    def test_get_path_dose_status(self):
        resource = ImmunizationEvaluation()
        resource.doseStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'doseStatus')
        assert result is not None

    def test_get_path_dose_status_reason(self):
        resource = ImmunizationEvaluation()
        resource.doseStatusReason = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'doseStatusReason')
        assert result is not None

    def test_get_path_description(self):
        resource = ImmunizationEvaluation()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_series(self):
        resource = ImmunizationEvaluation()
        resource.series = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'series')
        assert result is not None


class TestSetPathImmunizationEvaluation:

    def test_set_path_id(self):
        resource = ImmunizationEvaluation()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ImmunizationEvaluation()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ImmunizationEvaluation.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ImmunizationEvaluation()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ImmunizationEvaluation()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ImmunizationEvaluation()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ImmunizationEvaluation()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ImmunizationEvaluation()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ImmunizationEvaluation()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ImmunizationEvaluation()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = ImmunizationEvaluation()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = ImmunizationEvaluation()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_patient(self):
        resource = ImmunizationEvaluation()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_date(self):
        resource = ImmunizationEvaluation()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_authority(self):
        resource = ImmunizationEvaluation()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'authority', value)
        assert result is True
        assert resource.authority is not None

    def test_set_path_target_disease(self):
        resource = ImmunizationEvaluation()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'targetDisease', value)
        assert result is True
        assert resource.targetDisease is not None

    def test_set_path_immunization_event(self):
        resource = ImmunizationEvaluation()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'immunizationEvent', value)
        assert result is True
        assert resource.immunizationEvent is not None

    def test_set_path_dose_status(self):
        resource = ImmunizationEvaluation()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'doseStatus', value)
        assert result is True
        assert resource.doseStatus is not None

    def test_set_path_dose_status_reason(self):
        resource = ImmunizationEvaluation()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'doseStatusReason', value)
        assert result is True
        assert resource.doseStatusReason is not None

    def test_set_path_description(self):
        resource = ImmunizationEvaluation()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_series(self):
        resource = ImmunizationEvaluation()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'series', value)
        assert result is True
        assert resource.series is not None


class TestParsePathImmunizationEvaluation:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ImmunizationEvaluation.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ImmunizationEvaluation.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ImmunizationEvaluation.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
