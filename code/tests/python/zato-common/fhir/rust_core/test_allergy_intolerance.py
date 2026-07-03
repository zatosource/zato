# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import AllergyIntolerance


class TestToDictAllergyIntolerance:

    def test_to_dict_empty(self):
        resource = AllergyIntolerance()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'AllergyIntolerance'

    def test_to_dict_with_id(self):
        resource = AllergyIntolerance()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = AllergyIntolerance()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, AllergyIntolerance)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = AllergyIntolerance()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = AllergyIntolerance()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = AllergyIntolerance()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = AllergyIntolerance()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = AllergyIntolerance()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = AllergyIntolerance()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = AllergyIntolerance()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = AllergyIntolerance()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = AllergyIntolerance()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_clinical_status(self):
        resource = AllergyIntolerance()
        resource.clinicalStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'clinicalStatus' in result

    def test_to_dict_verification_status(self):
        resource = AllergyIntolerance()
        resource.verificationStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'verificationStatus' in result

    def test_to_dict_type(self):
        resource = AllergyIntolerance()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_category(self):
        resource = AllergyIntolerance()
        resource.category = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_criticality(self):
        resource = AllergyIntolerance()
        resource.criticality = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'criticality' in result

    def test_to_dict_code(self):
        resource = AllergyIntolerance()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_patient(self):
        resource = AllergyIntolerance()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_encounter(self):
        resource = AllergyIntolerance()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_recorded_date(self):
        resource = AllergyIntolerance()
        resource.recordedDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recordedDate' in result

    def test_to_dict_recorder(self):
        resource = AllergyIntolerance()
        resource.recorder = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recorder' in result

    def test_to_dict_asserter(self):
        resource = AllergyIntolerance()
        resource.asserter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'asserter' in result

    def test_to_dict_last_occurrence(self):
        resource = AllergyIntolerance()
        resource.lastOccurrence = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lastOccurrence' in result

    def test_to_dict_note(self):
        resource = AllergyIntolerance()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_reaction(self):
        resource = AllergyIntolerance()
        resource.reaction = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reaction' in result


class TestFromDictAllergyIntolerance:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'AllergyIntolerance', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert isinstance(result, AllergyIntolerance)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'AllergyIntolerance'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert isinstance(result, AllergyIntolerance)

    def test_from_dict_id(self):
        data = {'resourceType': 'AllergyIntolerance', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'AllergyIntolerance', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'AllergyIntolerance', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'AllergyIntolerance', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'AllergyIntolerance', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'AllergyIntolerance', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'AllergyIntolerance', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'AllergyIntolerance', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'AllergyIntolerance', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.identifier is not None

    def test_from_dict_clinical_status(self):
        data = {'clinicalStatus': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                            'text': 'Test concept'},
         'resourceType': 'AllergyIntolerance'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.clinicalStatus is not None

    def test_from_dict_verification_status(self):
        data = {'resourceType': 'AllergyIntolerance',
         'verificationStatus': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.verificationStatus is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'AllergyIntolerance', 'type': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.type_ is not None

    def test_from_dict_category(self):
        data = {'resourceType': 'AllergyIntolerance', 'category': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.category is not None

    def test_from_dict_criticality(self):
        data = {'resourceType': 'AllergyIntolerance', 'criticality': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.criticality is not None

    def test_from_dict_code(self):
        data = {'code': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'AllergyIntolerance'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.code is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'AllergyIntolerance', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.patient is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'AllergyIntolerance', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.encounter is not None

    def test_from_dict_recorded_date(self):
        data = {'resourceType': 'AllergyIntolerance', 'recordedDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.recordedDate is not None

    def test_from_dict_recorder(self):
        data = {'resourceType': 'AllergyIntolerance', 'recorder': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.recorder is not None

    def test_from_dict_asserter(self):
        data = {'resourceType': 'AllergyIntolerance', 'asserter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.asserter is not None

    def test_from_dict_last_occurrence(self):
        data = {'resourceType': 'AllergyIntolerance', 'lastOccurrence': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.lastOccurrence is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'AllergyIntolerance', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.note is not None

    def test_from_dict_reaction(self):
        data = {'resourceType': 'AllergyIntolerance', 'reaction': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AllergyIntolerance)
        assert result.reaction is not None


class TestGetPathAllergyIntolerance:

    def test_get_path_id(self):
        resource = AllergyIntolerance()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = AllergyIntolerance()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = AllergyIntolerance()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'AllergyIntolerance.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = AllergyIntolerance()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = AllergyIntolerance()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = AllergyIntolerance()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = AllergyIntolerance()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = AllergyIntolerance()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = AllergyIntolerance()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = AllergyIntolerance()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = AllergyIntolerance()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_clinical_status(self):
        resource = AllergyIntolerance()
        resource.clinicalStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'clinicalStatus')
        assert result is not None

    def test_get_path_verification_status(self):
        resource = AllergyIntolerance()
        resource.verificationStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'verificationStatus')
        assert result is not None

    def test_get_path_type(self):
        resource = AllergyIntolerance()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_category(self):
        resource = AllergyIntolerance()
        resource.category = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_criticality(self):
        resource = AllergyIntolerance()
        resource.criticality = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'criticality')
        assert result is not None

    def test_get_path_code(self):
        resource = AllergyIntolerance()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_patient(self):
        resource = AllergyIntolerance()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_encounter(self):
        resource = AllergyIntolerance()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_recorded_date(self):
        resource = AllergyIntolerance()
        resource.recordedDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recordedDate')
        assert result is not None

    def test_get_path_recorder(self):
        resource = AllergyIntolerance()
        resource.recorder = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recorder')
        assert result is not None

    def test_get_path_asserter(self):
        resource = AllergyIntolerance()
        resource.asserter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'asserter')
        assert result is not None

    def test_get_path_last_occurrence(self):
        resource = AllergyIntolerance()
        resource.lastOccurrence = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lastOccurrence')
        assert result is not None

    def test_get_path_note(self):
        resource = AllergyIntolerance()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_reaction(self):
        resource = AllergyIntolerance()
        resource.reaction = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reaction')
        assert result is not None


class TestSetPathAllergyIntolerance:

    def test_set_path_id(self):
        resource = AllergyIntolerance()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = AllergyIntolerance()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'AllergyIntolerance.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = AllergyIntolerance()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = AllergyIntolerance()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = AllergyIntolerance()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = AllergyIntolerance()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = AllergyIntolerance()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = AllergyIntolerance()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = AllergyIntolerance()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = AllergyIntolerance()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_clinical_status(self):
        resource = AllergyIntolerance()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'clinicalStatus', value)
        assert result is True
        assert resource.clinicalStatus is not None

    def test_set_path_verification_status(self):
        resource = AllergyIntolerance()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'verificationStatus', value)
        assert result is True
        assert resource.verificationStatus is not None

    def test_set_path_type(self):
        resource = AllergyIntolerance()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_category(self):
        resource = AllergyIntolerance()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_criticality(self):
        resource = AllergyIntolerance()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'criticality', value)
        assert result is True
        assert resource.criticality is not None

    def test_set_path_code(self):
        resource = AllergyIntolerance()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_patient(self):
        resource = AllergyIntolerance()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_encounter(self):
        resource = AllergyIntolerance()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_recorded_date(self):
        resource = AllergyIntolerance()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recordedDate', value)
        assert result is True
        assert resource.recordedDate is not None

    def test_set_path_recorder(self):
        resource = AllergyIntolerance()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recorder', value)
        assert result is True
        assert resource.recorder is not None

    def test_set_path_asserter(self):
        resource = AllergyIntolerance()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'asserter', value)
        assert result is True
        assert resource.asserter is not None

    def test_set_path_last_occurrence(self):
        resource = AllergyIntolerance()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lastOccurrence', value)
        assert result is True
        assert resource.lastOccurrence is not None

    def test_set_path_note(self):
        resource = AllergyIntolerance()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_reaction(self):
        resource = AllergyIntolerance()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reaction', value)
        assert result is True
        assert resource.reaction is not None


class TestParsePathAllergyIntolerance:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('AllergyIntolerance.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('AllergyIntolerance.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('AllergyIntolerance.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
