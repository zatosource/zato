# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Condition


class TestToDictCondition:

    def test_to_dict_empty(self):
        resource = Condition()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Condition'

    def test_to_dict_with_id(self):
        resource = Condition()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Condition()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Condition)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Condition()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Condition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Condition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Condition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Condition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Condition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Condition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Condition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Condition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_clinical_status(self):
        resource = Condition()
        resource.clinicalStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'clinicalStatus' in result

    def test_to_dict_verification_status(self):
        resource = Condition()
        resource.verificationStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'verificationStatus' in result

    def test_to_dict_category(self):
        resource = Condition()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_severity(self):
        resource = Condition()
        resource.severity = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'severity' in result

    def test_to_dict_code(self):
        resource = Condition()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_body_site(self):
        resource = Condition()
        resource.bodySite = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'bodySite' in result

    def test_to_dict_subject(self):
        resource = Condition()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_encounter(self):
        resource = Condition()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_recorded_date(self):
        resource = Condition()
        resource.recordedDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recordedDate' in result

    def test_to_dict_recorder(self):
        resource = Condition()
        resource.recorder = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recorder' in result

    def test_to_dict_asserter(self):
        resource = Condition()
        resource.asserter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'asserter' in result

    def test_to_dict_stage(self):
        resource = Condition()
        resource.stage = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'stage' in result

    def test_to_dict_evidence(self):
        resource = Condition()
        resource.evidence = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'evidence' in result

    def test_to_dict_note(self):
        resource = Condition()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result


class TestFromDictCondition:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Condition', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert isinstance(result, Condition)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Condition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert isinstance(result, Condition)

    def test_from_dict_id(self):
        data = {'resourceType': 'Condition', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Condition', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Condition', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Condition', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Condition', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Condition', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Condition', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Condition', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Condition', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.identifier is not None

    def test_from_dict_clinical_status(self):
        data = {'clinicalStatus': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                            'text': 'Test concept'},
         'resourceType': 'Condition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.clinicalStatus is not None

    def test_from_dict_verification_status(self):
        data = {'resourceType': 'Condition',
         'verificationStatus': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.verificationStatus is not None

    def test_from_dict_category(self):
        data = {'category': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'Condition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.category is not None

    def test_from_dict_severity(self):
        data = {'resourceType': 'Condition',
         'severity': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.severity is not None

    def test_from_dict_code(self):
        data = {'code': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'Condition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.code is not None

    def test_from_dict_body_site(self):
        data = {'bodySite': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'Condition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.bodySite is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'Condition', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.subject is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'Condition', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.encounter is not None

    def test_from_dict_recorded_date(self):
        data = {'resourceType': 'Condition', 'recordedDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.recordedDate is not None

    def test_from_dict_recorder(self):
        data = {'resourceType': 'Condition', 'recorder': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.recorder is not None

    def test_from_dict_asserter(self):
        data = {'resourceType': 'Condition', 'asserter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.asserter is not None

    def test_from_dict_stage(self):
        data = {'resourceType': 'Condition', 'stage': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.stage is not None

    def test_from_dict_evidence(self):
        data = {'resourceType': 'Condition', 'evidence': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.evidence is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'Condition', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Condition)
        assert result.note is not None


class TestGetPathCondition:

    def test_get_path_id(self):
        resource = Condition()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Condition()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Condition()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Condition.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Condition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Condition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Condition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Condition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Condition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Condition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Condition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Condition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_clinical_status(self):
        resource = Condition()
        resource.clinicalStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'clinicalStatus')
        assert result is not None

    def test_get_path_verification_status(self):
        resource = Condition()
        resource.verificationStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'verificationStatus')
        assert result is not None

    def test_get_path_category(self):
        resource = Condition()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_severity(self):
        resource = Condition()
        resource.severity = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'severity')
        assert result is not None

    def test_get_path_code(self):
        resource = Condition()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_body_site(self):
        resource = Condition()
        resource.bodySite = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'bodySite')
        assert result is not None

    def test_get_path_subject(self):
        resource = Condition()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_encounter(self):
        resource = Condition()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_recorded_date(self):
        resource = Condition()
        resource.recordedDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recordedDate')
        assert result is not None

    def test_get_path_recorder(self):
        resource = Condition()
        resource.recorder = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recorder')
        assert result is not None

    def test_get_path_asserter(self):
        resource = Condition()
        resource.asserter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'asserter')
        assert result is not None

    def test_get_path_stage(self):
        resource = Condition()
        resource.stage = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'stage')
        assert result is not None

    def test_get_path_evidence(self):
        resource = Condition()
        resource.evidence = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'evidence')
        assert result is not None

    def test_get_path_note(self):
        resource = Condition()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None


class TestSetPathCondition:

    def test_set_path_id(self):
        resource = Condition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Condition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Condition.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Condition()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Condition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Condition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Condition()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Condition()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Condition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Condition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Condition()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_clinical_status(self):
        resource = Condition()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'clinicalStatus', value)
        assert result is True
        assert resource.clinicalStatus is not None

    def test_set_path_verification_status(self):
        resource = Condition()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'verificationStatus', value)
        assert result is True
        assert resource.verificationStatus is not None

    def test_set_path_category(self):
        resource = Condition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_severity(self):
        resource = Condition()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'severity', value)
        assert result is True
        assert resource.severity is not None

    def test_set_path_code(self):
        resource = Condition()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_body_site(self):
        resource = Condition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'bodySite', value)
        assert result is True
        assert resource.bodySite is not None

    def test_set_path_subject(self):
        resource = Condition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_encounter(self):
        resource = Condition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_recorded_date(self):
        resource = Condition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recordedDate', value)
        assert result is True
        assert resource.recordedDate is not None

    def test_set_path_recorder(self):
        resource = Condition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recorder', value)
        assert result is True
        assert resource.recorder is not None

    def test_set_path_asserter(self):
        resource = Condition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'asserter', value)
        assert result is True
        assert resource.asserter is not None

    def test_set_path_stage(self):
        resource = Condition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'stage', value)
        assert result is True
        assert resource.stage is not None

    def test_set_path_evidence(self):
        resource = Condition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'evidence', value)
        assert result is True
        assert resource.evidence is not None

    def test_set_path_note(self):
        resource = Condition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None


class TestParsePathCondition:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Condition.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Condition.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Condition.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
