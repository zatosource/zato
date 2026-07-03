# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import MedicinalProductIndication


class TestToDictMedicinalProductIndication:

    def test_to_dict_empty(self):
        resource = MedicinalProductIndication()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'MedicinalProductIndication'

    def test_to_dict_with_id(self):
        resource = MedicinalProductIndication()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = MedicinalProductIndication()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, MedicinalProductIndication)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = MedicinalProductIndication()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = MedicinalProductIndication()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = MedicinalProductIndication()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = MedicinalProductIndication()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = MedicinalProductIndication()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = MedicinalProductIndication()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = MedicinalProductIndication()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = MedicinalProductIndication()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_subject(self):
        resource = MedicinalProductIndication()
        resource.subject = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_disease_symptom_procedure(self):
        resource = MedicinalProductIndication()
        resource.diseaseSymptomProcedure = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'diseaseSymptomProcedure' in result

    def test_to_dict_disease_status(self):
        resource = MedicinalProductIndication()
        resource.diseaseStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'diseaseStatus' in result

    def test_to_dict_comorbidity(self):
        resource = MedicinalProductIndication()
        resource.comorbidity = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'comorbidity' in result

    def test_to_dict_intended_effect(self):
        resource = MedicinalProductIndication()
        resource.intendedEffect = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'intendedEffect' in result

    def test_to_dict_duration(self):
        resource = MedicinalProductIndication()
        resource.duration = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'duration' in result

    def test_to_dict_other_therapy(self):
        resource = MedicinalProductIndication()
        resource.otherTherapy = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'otherTherapy' in result

    def test_to_dict_undesirable_effect(self):
        resource = MedicinalProductIndication()
        resource.undesirableEffect = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'undesirableEffect' in result

    def test_to_dict_population(self):
        resource = MedicinalProductIndication()
        resource.population = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'population' in result


class TestFromDictMedicinalProductIndication:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'MedicinalProductIndication', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert isinstance(result, MedicinalProductIndication)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'MedicinalProductIndication'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert isinstance(result, MedicinalProductIndication)

    def test_from_dict_id(self):
        data = {'resourceType': 'MedicinalProductIndication', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'MedicinalProductIndication', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'MedicinalProductIndication', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'MedicinalProductIndication', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'MedicinalProductIndication', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'MedicinalProductIndication', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'MedicinalProductIndication', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'MedicinalProductIndication', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.modifierExtension is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'MedicinalProductIndication', 'subject': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.subject is not None

    def test_from_dict_disease_symptom_procedure(self):
        data = {'diseaseSymptomProcedure': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                     'text': 'Test concept'},
         'resourceType': 'MedicinalProductIndication'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.diseaseSymptomProcedure is not None

    def test_from_dict_disease_status(self):
        data = {'diseaseStatus': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'},
         'resourceType': 'MedicinalProductIndication'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.diseaseStatus is not None

    def test_from_dict_comorbidity(self):
        data = {'comorbidity': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'}],
         'resourceType': 'MedicinalProductIndication'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.comorbidity is not None

    def test_from_dict_intended_effect(self):
        data = {'intendedEffect': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                            'text': 'Test concept'},
         'resourceType': 'MedicinalProductIndication'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.intendedEffect is not None

    def test_from_dict_duration(self):
        data = {'resourceType': 'MedicinalProductIndication', 'duration': {'value': 100, 'unit': 'mg'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.duration is not None

    def test_from_dict_other_therapy(self):
        data = {'resourceType': 'MedicinalProductIndication', 'otherTherapy': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.otherTherapy is not None

    def test_from_dict_undesirable_effect(self):
        data = {'resourceType': 'MedicinalProductIndication', 'undesirableEffect': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.undesirableEffect is not None

    def test_from_dict_population(self):
        data = {'resourceType': 'MedicinalProductIndication', 'population': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductIndication)
        assert result.population is not None


class TestGetPathMedicinalProductIndication:

    def test_get_path_id(self):
        resource = MedicinalProductIndication()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = MedicinalProductIndication()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = MedicinalProductIndication()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'MedicinalProductIndication.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = MedicinalProductIndication()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = MedicinalProductIndication()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = MedicinalProductIndication()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = MedicinalProductIndication()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = MedicinalProductIndication()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = MedicinalProductIndication()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = MedicinalProductIndication()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_subject(self):
        resource = MedicinalProductIndication()
        resource.subject = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_disease_symptom_procedure(self):
        resource = MedicinalProductIndication()
        resource.diseaseSymptomProcedure = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'diseaseSymptomProcedure')
        assert result is not None

    def test_get_path_disease_status(self):
        resource = MedicinalProductIndication()
        resource.diseaseStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'diseaseStatus')
        assert result is not None

    def test_get_path_comorbidity(self):
        resource = MedicinalProductIndication()
        resource.comorbidity = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'comorbidity')
        assert result is not None

    def test_get_path_intended_effect(self):
        resource = MedicinalProductIndication()
        resource.intendedEffect = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'intendedEffect')
        assert result is not None

    def test_get_path_duration(self):
        resource = MedicinalProductIndication()
        resource.duration = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'duration')
        assert result is not None

    def test_get_path_other_therapy(self):
        resource = MedicinalProductIndication()
        resource.otherTherapy = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'otherTherapy')
        assert result is not None

    def test_get_path_undesirable_effect(self):
        resource = MedicinalProductIndication()
        resource.undesirableEffect = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'undesirableEffect')
        assert result is not None

    def test_get_path_population(self):
        resource = MedicinalProductIndication()
        resource.population = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'population')
        assert result is not None


class TestSetPathMedicinalProductIndication:

    def test_set_path_id(self):
        resource = MedicinalProductIndication()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = MedicinalProductIndication()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'MedicinalProductIndication.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = MedicinalProductIndication()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = MedicinalProductIndication()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = MedicinalProductIndication()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = MedicinalProductIndication()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = MedicinalProductIndication()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = MedicinalProductIndication()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = MedicinalProductIndication()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_subject(self):
        resource = MedicinalProductIndication()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_disease_symptom_procedure(self):
        resource = MedicinalProductIndication()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'diseaseSymptomProcedure', value)
        assert result is True
        assert resource.diseaseSymptomProcedure is not None

    def test_set_path_disease_status(self):
        resource = MedicinalProductIndication()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'diseaseStatus', value)
        assert result is True
        assert resource.diseaseStatus is not None

    def test_set_path_comorbidity(self):
        resource = MedicinalProductIndication()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'comorbidity', value)
        assert result is True
        assert resource.comorbidity is not None

    def test_set_path_intended_effect(self):
        resource = MedicinalProductIndication()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'intendedEffect', value)
        assert result is True
        assert resource.intendedEffect is not None

    def test_set_path_duration(self):
        resource = MedicinalProductIndication()
        value = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'duration', value)
        assert result is True
        assert resource.duration is not None

    def test_set_path_other_therapy(self):
        resource = MedicinalProductIndication()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'otherTherapy', value)
        assert result is True
        assert resource.otherTherapy is not None

    def test_set_path_undesirable_effect(self):
        resource = MedicinalProductIndication()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'undesirableEffect', value)
        assert result is True
        assert resource.undesirableEffect is not None

    def test_set_path_population(self):
        resource = MedicinalProductIndication()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'population', value)
        assert result is True
        assert resource.population is not None


class TestParsePathMedicinalProductIndication:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductIndication.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductIndication.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductIndication.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
