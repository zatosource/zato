# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import FamilyMemberHistory


class TestToDictFamilyMemberHistory:

    def test_to_dict_empty(self):
        resource = FamilyMemberHistory()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'FamilyMemberHistory'

    def test_to_dict_with_id(self):
        resource = FamilyMemberHistory()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = FamilyMemberHistory()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, FamilyMemberHistory)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = FamilyMemberHistory()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = FamilyMemberHistory()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = FamilyMemberHistory()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = FamilyMemberHistory()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = FamilyMemberHistory()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = FamilyMemberHistory()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = FamilyMemberHistory()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = FamilyMemberHistory()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = FamilyMemberHistory()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_instantiates_canonical(self):
        resource = FamilyMemberHistory()
        resource.instantiatesCanonical = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesCanonical' in result

    def test_to_dict_instantiates_uri(self):
        resource = FamilyMemberHistory()
        resource.instantiatesUri = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesUri' in result

    def test_to_dict_status(self):
        resource = FamilyMemberHistory()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_data_absent_reason(self):
        resource = FamilyMemberHistory()
        resource.dataAbsentReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dataAbsentReason' in result

    def test_to_dict_patient(self):
        resource = FamilyMemberHistory()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_date(self):
        resource = FamilyMemberHistory()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_name(self):
        resource = FamilyMemberHistory()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_relationship(self):
        resource = FamilyMemberHistory()
        resource.relationship = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relationship' in result

    def test_to_dict_sex(self):
        resource = FamilyMemberHistory()
        resource.sex = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'sex' in result

    def test_to_dict_estimated_age(self):
        resource = FamilyMemberHistory()
        resource.estimatedAge = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'estimatedAge' in result

    def test_to_dict_reason_code(self):
        resource = FamilyMemberHistory()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonCode' in result

    def test_to_dict_reason_reference(self):
        resource = FamilyMemberHistory()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonReference' in result

    def test_to_dict_note(self):
        resource = FamilyMemberHistory()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_condition(self):
        resource = FamilyMemberHistory()
        resource.condition = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'condition' in result


class TestFromDictFamilyMemberHistory:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'FamilyMemberHistory', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert isinstance(result, FamilyMemberHistory)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'FamilyMemberHistory'}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert isinstance(result, FamilyMemberHistory)

    def test_from_dict_id(self):
        data = {'resourceType': 'FamilyMemberHistory', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'FamilyMemberHistory', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'FamilyMemberHistory', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'FamilyMemberHistory', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'FamilyMemberHistory', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'FamilyMemberHistory', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'FamilyMemberHistory', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'FamilyMemberHistory', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'FamilyMemberHistory', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.identifier is not None

    def test_from_dict_instantiates_canonical(self):
        data = {'resourceType': 'FamilyMemberHistory', 'instantiatesCanonical': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.instantiatesCanonical is not None

    def test_from_dict_instantiates_uri(self):
        data = {'resourceType': 'FamilyMemberHistory', 'instantiatesUri': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.instantiatesUri is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'FamilyMemberHistory', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.status is not None

    def test_from_dict_data_absent_reason(self):
        data = {'dataAbsentReason': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                              'text': 'Test concept'},
         'resourceType': 'FamilyMemberHistory'}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.dataAbsentReason is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'FamilyMemberHistory', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.patient is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'FamilyMemberHistory', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.date is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'FamilyMemberHistory', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.name is not None

    def test_from_dict_relationship(self):
        data = {'relationship': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'},
         'resourceType': 'FamilyMemberHistory'}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.relationship is not None

    def test_from_dict_sex(self):
        data = {'resourceType': 'FamilyMemberHistory',
         'sex': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.sex is not None

    def test_from_dict_estimated_age(self):
        data = {'resourceType': 'FamilyMemberHistory', 'estimatedAge': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.estimatedAge is not None

    def test_from_dict_reason_code(self):
        data = {'reasonCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}],
         'resourceType': 'FamilyMemberHistory'}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.reasonCode is not None

    def test_from_dict_reason_reference(self):
        data = {'resourceType': 'FamilyMemberHistory', 'reasonReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.reasonReference is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'FamilyMemberHistory', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.note is not None

    def test_from_dict_condition(self):
        data = {'resourceType': 'FamilyMemberHistory', 'condition': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, FamilyMemberHistory)
        assert result.condition is not None


class TestGetPathFamilyMemberHistory:

    def test_get_path_id(self):
        resource = FamilyMemberHistory()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = FamilyMemberHistory()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = FamilyMemberHistory()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'FamilyMemberHistory.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = FamilyMemberHistory()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = FamilyMemberHistory()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = FamilyMemberHistory()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = FamilyMemberHistory()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = FamilyMemberHistory()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = FamilyMemberHistory()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = FamilyMemberHistory()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = FamilyMemberHistory()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_instantiates_canonical(self):
        resource = FamilyMemberHistory()
        resource.instantiatesCanonical = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesCanonical')
        assert result is not None

    def test_get_path_instantiates_uri(self):
        resource = FamilyMemberHistory()
        resource.instantiatesUri = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesUri')
        assert result is not None

    def test_get_path_status(self):
        resource = FamilyMemberHistory()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_data_absent_reason(self):
        resource = FamilyMemberHistory()
        resource.dataAbsentReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dataAbsentReason')
        assert result is not None

    def test_get_path_patient(self):
        resource = FamilyMemberHistory()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_date(self):
        resource = FamilyMemberHistory()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_name(self):
        resource = FamilyMemberHistory()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_relationship(self):
        resource = FamilyMemberHistory()
        resource.relationship = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relationship')
        assert result is not None

    def test_get_path_sex(self):
        resource = FamilyMemberHistory()
        resource.sex = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'sex')
        assert result is not None

    def test_get_path_estimated_age(self):
        resource = FamilyMemberHistory()
        resource.estimatedAge = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'estimatedAge')
        assert result is not None

    def test_get_path_reason_code(self):
        resource = FamilyMemberHistory()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonCode')
        assert result is not None

    def test_get_path_reason_reference(self):
        resource = FamilyMemberHistory()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonReference')
        assert result is not None

    def test_get_path_note(self):
        resource = FamilyMemberHistory()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_condition(self):
        resource = FamilyMemberHistory()
        resource.condition = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'condition')
        assert result is not None


class TestSetPathFamilyMemberHistory:

    def test_set_path_id(self):
        resource = FamilyMemberHistory()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = FamilyMemberHistory()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'FamilyMemberHistory.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = FamilyMemberHistory()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = FamilyMemberHistory()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = FamilyMemberHistory()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = FamilyMemberHistory()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = FamilyMemberHistory()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = FamilyMemberHistory()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = FamilyMemberHistory()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = FamilyMemberHistory()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_instantiates_canonical(self):
        resource = FamilyMemberHistory()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesCanonical', value)
        assert result is True
        assert resource.instantiatesCanonical is not None

    def test_set_path_instantiates_uri(self):
        resource = FamilyMemberHistory()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesUri', value)
        assert result is True
        assert resource.instantiatesUri is not None

    def test_set_path_status(self):
        resource = FamilyMemberHistory()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_data_absent_reason(self):
        resource = FamilyMemberHistory()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dataAbsentReason', value)
        assert result is True
        assert resource.dataAbsentReason is not None

    def test_set_path_patient(self):
        resource = FamilyMemberHistory()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_date(self):
        resource = FamilyMemberHistory()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_name(self):
        resource = FamilyMemberHistory()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_relationship(self):
        resource = FamilyMemberHistory()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relationship', value)
        assert result is True
        assert resource.relationship is not None

    def test_set_path_sex(self):
        resource = FamilyMemberHistory()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'sex', value)
        assert result is True
        assert resource.sex is not None

    def test_set_path_estimated_age(self):
        resource = FamilyMemberHistory()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'estimatedAge', value)
        assert result is True
        assert resource.estimatedAge is not None

    def test_set_path_reason_code(self):
        resource = FamilyMemberHistory()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonCode', value)
        assert result is True
        assert resource.reasonCode is not None

    def test_set_path_reason_reference(self):
        resource = FamilyMemberHistory()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonReference', value)
        assert result is True
        assert resource.reasonReference is not None

    def test_set_path_note(self):
        resource = FamilyMemberHistory()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_condition(self):
        resource = FamilyMemberHistory()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'condition', value)
        assert result is True
        assert resource.condition is not None


class TestParsePathFamilyMemberHistory:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('FamilyMemberHistory.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('FamilyMemberHistory.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('FamilyMemberHistory.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
