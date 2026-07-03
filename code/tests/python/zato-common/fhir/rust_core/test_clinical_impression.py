# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ClinicalImpression


class TestToDictClinicalImpression:

    def test_to_dict_empty(self):
        resource = ClinicalImpression()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ClinicalImpression'

    def test_to_dict_with_id(self):
        resource = ClinicalImpression()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ClinicalImpression()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ClinicalImpression)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ClinicalImpression()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ClinicalImpression()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ClinicalImpression()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ClinicalImpression()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ClinicalImpression()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ClinicalImpression()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ClinicalImpression()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ClinicalImpression()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = ClinicalImpression()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = ClinicalImpression()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_status_reason(self):
        resource = ClinicalImpression()
        resource.statusReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'statusReason' in result

    def test_to_dict_code(self):
        resource = ClinicalImpression()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_description(self):
        resource = ClinicalImpression()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_subject(self):
        resource = ClinicalImpression()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_encounter(self):
        resource = ClinicalImpression()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_date(self):
        resource = ClinicalImpression()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_assessor(self):
        resource = ClinicalImpression()
        resource.assessor = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'assessor' in result

    def test_to_dict_previous(self):
        resource = ClinicalImpression()
        resource.previous = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'previous' in result

    def test_to_dict_problem(self):
        resource = ClinicalImpression()
        resource.problem = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'problem' in result

    def test_to_dict_investigation(self):
        resource = ClinicalImpression()
        resource.investigation = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'investigation' in result

    def test_to_dict_protocol(self):
        resource = ClinicalImpression()
        resource.protocol = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'protocol' in result

    def test_to_dict_summary(self):
        resource = ClinicalImpression()
        resource.summary = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'summary' in result

    def test_to_dict_finding(self):
        resource = ClinicalImpression()
        resource.finding = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'finding' in result

    def test_to_dict_prognosis_codeable_concept(self):
        resource = ClinicalImpression()
        resource.prognosisCodeableConcept = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'prognosisCodeableConcept' in result

    def test_to_dict_prognosis_reference(self):
        resource = ClinicalImpression()
        resource.prognosisReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'prognosisReference' in result

    def test_to_dict_supporting_info(self):
        resource = ClinicalImpression()
        resource.supportingInfo = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supportingInfo' in result

    def test_to_dict_note(self):
        resource = ClinicalImpression()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result


class TestFromDictClinicalImpression:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ClinicalImpression', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert isinstance(result, ClinicalImpression)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ClinicalImpression'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert isinstance(result, ClinicalImpression)

    def test_from_dict_id(self):
        data = {'resourceType': 'ClinicalImpression', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ClinicalImpression', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ClinicalImpression', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ClinicalImpression', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ClinicalImpression', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ClinicalImpression', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ClinicalImpression', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ClinicalImpression', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'ClinicalImpression', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'ClinicalImpression', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.status is not None

    def test_from_dict_status_reason(self):
        data = {'resourceType': 'ClinicalImpression',
         'statusReason': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.statusReason is not None

    def test_from_dict_code(self):
        data = {'code': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'ClinicalImpression'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.code is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'ClinicalImpression', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.description is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'ClinicalImpression', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.subject is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'ClinicalImpression', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.encounter is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'ClinicalImpression', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.date is not None

    def test_from_dict_assessor(self):
        data = {'resourceType': 'ClinicalImpression', 'assessor': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.assessor is not None

    def test_from_dict_previous(self):
        data = {'resourceType': 'ClinicalImpression', 'previous': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.previous is not None

    def test_from_dict_problem(self):
        data = {'resourceType': 'ClinicalImpression', 'problem': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.problem is not None

    def test_from_dict_investigation(self):
        data = {'resourceType': 'ClinicalImpression', 'investigation': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.investigation is not None

    def test_from_dict_protocol(self):
        data = {'resourceType': 'ClinicalImpression', 'protocol': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.protocol is not None

    def test_from_dict_summary(self):
        data = {'resourceType': 'ClinicalImpression', 'summary': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.summary is not None

    def test_from_dict_finding(self):
        data = {'resourceType': 'ClinicalImpression', 'finding': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.finding is not None

    def test_from_dict_prognosis_codeable_concept(self):
        data = {'prognosisCodeableConcept': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                       'text': 'Test concept'}],
         'resourceType': 'ClinicalImpression'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.prognosisCodeableConcept is not None

    def test_from_dict_prognosis_reference(self):
        data = {'resourceType': 'ClinicalImpression', 'prognosisReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.prognosisReference is not None

    def test_from_dict_supporting_info(self):
        data = {'resourceType': 'ClinicalImpression', 'supportingInfo': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.supportingInfo is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'ClinicalImpression', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClinicalImpression)
        assert result.note is not None


class TestGetPathClinicalImpression:

    def test_get_path_id(self):
        resource = ClinicalImpression()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ClinicalImpression()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ClinicalImpression()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ClinicalImpression.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ClinicalImpression()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ClinicalImpression()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ClinicalImpression()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ClinicalImpression()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ClinicalImpression()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ClinicalImpression()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ClinicalImpression()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = ClinicalImpression()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = ClinicalImpression()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_status_reason(self):
        resource = ClinicalImpression()
        resource.statusReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'statusReason')
        assert result is not None

    def test_get_path_code(self):
        resource = ClinicalImpression()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_description(self):
        resource = ClinicalImpression()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_subject(self):
        resource = ClinicalImpression()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_encounter(self):
        resource = ClinicalImpression()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_date(self):
        resource = ClinicalImpression()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_assessor(self):
        resource = ClinicalImpression()
        resource.assessor = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'assessor')
        assert result is not None

    def test_get_path_previous(self):
        resource = ClinicalImpression()
        resource.previous = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'previous')
        assert result is not None

    def test_get_path_problem(self):
        resource = ClinicalImpression()
        resource.problem = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'problem')
        assert result is not None

    def test_get_path_investigation(self):
        resource = ClinicalImpression()
        resource.investigation = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'investigation')
        assert result is not None

    def test_get_path_protocol(self):
        resource = ClinicalImpression()
        resource.protocol = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'protocol')
        assert result is not None

    def test_get_path_summary(self):
        resource = ClinicalImpression()
        resource.summary = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'summary')
        assert result is not None

    def test_get_path_finding(self):
        resource = ClinicalImpression()
        resource.finding = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'finding')
        assert result is not None

    def test_get_path_prognosis_codeable_concept(self):
        resource = ClinicalImpression()
        resource.prognosisCodeableConcept = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'prognosisCodeableConcept')
        assert result is not None

    def test_get_path_prognosis_reference(self):
        resource = ClinicalImpression()
        resource.prognosisReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'prognosisReference')
        assert result is not None

    def test_get_path_supporting_info(self):
        resource = ClinicalImpression()
        resource.supportingInfo = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supportingInfo')
        assert result is not None

    def test_get_path_note(self):
        resource = ClinicalImpression()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None


class TestSetPathClinicalImpression:

    def test_set_path_id(self):
        resource = ClinicalImpression()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ClinicalImpression()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ClinicalImpression.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ClinicalImpression()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ClinicalImpression()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ClinicalImpression()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ClinicalImpression()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ClinicalImpression()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ClinicalImpression()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ClinicalImpression()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = ClinicalImpression()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = ClinicalImpression()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_status_reason(self):
        resource = ClinicalImpression()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'statusReason', value)
        assert result is True
        assert resource.statusReason is not None

    def test_set_path_code(self):
        resource = ClinicalImpression()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_description(self):
        resource = ClinicalImpression()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_subject(self):
        resource = ClinicalImpression()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_encounter(self):
        resource = ClinicalImpression()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_date(self):
        resource = ClinicalImpression()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_assessor(self):
        resource = ClinicalImpression()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'assessor', value)
        assert result is True
        assert resource.assessor is not None

    def test_set_path_previous(self):
        resource = ClinicalImpression()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'previous', value)
        assert result is True
        assert resource.previous is not None

    def test_set_path_problem(self):
        resource = ClinicalImpression()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'problem', value)
        assert result is True
        assert resource.problem is not None

    def test_set_path_investigation(self):
        resource = ClinicalImpression()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'investigation', value)
        assert result is True
        assert resource.investigation is not None

    def test_set_path_protocol(self):
        resource = ClinicalImpression()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'protocol', value)
        assert result is True
        assert resource.protocol is not None

    def test_set_path_summary(self):
        resource = ClinicalImpression()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'summary', value)
        assert result is True
        assert resource.summary is not None

    def test_set_path_finding(self):
        resource = ClinicalImpression()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'finding', value)
        assert result is True
        assert resource.finding is not None

    def test_set_path_prognosis_codeable_concept(self):
        resource = ClinicalImpression()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'prognosisCodeableConcept', value)
        assert result is True
        assert resource.prognosisCodeableConcept is not None

    def test_set_path_prognosis_reference(self):
        resource = ClinicalImpression()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'prognosisReference', value)
        assert result is True
        assert resource.prognosisReference is not None

    def test_set_path_supporting_info(self):
        resource = ClinicalImpression()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supportingInfo', value)
        assert result is True
        assert resource.supportingInfo is not None

    def test_set_path_note(self):
        resource = ClinicalImpression()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None


class TestParsePathClinicalImpression:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ClinicalImpression.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ClinicalImpression.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ClinicalImpression.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
