# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import MedicinalProductUndesirableEffect


class TestToDictMedicinalProductUndesirableEffect:

    def test_to_dict_empty(self):
        resource = MedicinalProductUndesirableEffect()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'MedicinalProductUndesirableEffect'

    def test_to_dict_with_id(self):
        resource = MedicinalProductUndesirableEffect()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = MedicinalProductUndesirableEffect()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, MedicinalProductUndesirableEffect)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = MedicinalProductUndesirableEffect()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = MedicinalProductUndesirableEffect()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = MedicinalProductUndesirableEffect()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = MedicinalProductUndesirableEffect()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = MedicinalProductUndesirableEffect()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = MedicinalProductUndesirableEffect()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = MedicinalProductUndesirableEffect()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = MedicinalProductUndesirableEffect()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_subject(self):
        resource = MedicinalProductUndesirableEffect()
        resource.subject = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_symptom_condition_effect(self):
        resource = MedicinalProductUndesirableEffect()
        resource.symptomConditionEffect = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'symptomConditionEffect' in result

    def test_to_dict_classification(self):
        resource = MedicinalProductUndesirableEffect()
        resource.classification = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'classification' in result

    def test_to_dict_frequency_of_occurrence(self):
        resource = MedicinalProductUndesirableEffect()
        resource.frequencyOfOccurrence = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'frequencyOfOccurrence' in result

    def test_to_dict_population(self):
        resource = MedicinalProductUndesirableEffect()
        resource.population = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'population' in result


class TestFromDictMedicinalProductUndesirableEffect:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'MedicinalProductUndesirableEffect', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductUndesirableEffect)
        assert isinstance(result, MedicinalProductUndesirableEffect)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'MedicinalProductUndesirableEffect'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductUndesirableEffect)
        assert isinstance(result, MedicinalProductUndesirableEffect)

    def test_from_dict_id(self):
        data = {'resourceType': 'MedicinalProductUndesirableEffect', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductUndesirableEffect)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'MedicinalProductUndesirableEffect', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductUndesirableEffect)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'MedicinalProductUndesirableEffect', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductUndesirableEffect)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'MedicinalProductUndesirableEffect', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductUndesirableEffect)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'MedicinalProductUndesirableEffect',
         'text': {'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>', 'status': 'generated'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductUndesirableEffect)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'MedicinalProductUndesirableEffect', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductUndesirableEffect)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'MedicinalProductUndesirableEffect', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductUndesirableEffect)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'MedicinalProductUndesirableEffect', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductUndesirableEffect)
        assert result.modifierExtension is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'MedicinalProductUndesirableEffect', 'subject': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductUndesirableEffect)
        assert result.subject is not None

    def test_from_dict_symptom_condition_effect(self):
        data = {'resourceType': 'MedicinalProductUndesirableEffect',
         'symptomConditionEffect': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                    'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductUndesirableEffect)
        assert result.symptomConditionEffect is not None

    def test_from_dict_classification(self):
        data = {'classification': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                            'text': 'Test concept'},
         'resourceType': 'MedicinalProductUndesirableEffect'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductUndesirableEffect)
        assert result.classification is not None

    def test_from_dict_frequency_of_occurrence(self):
        data = {'frequencyOfOccurrence': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                   'text': 'Test concept'},
         'resourceType': 'MedicinalProductUndesirableEffect'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductUndesirableEffect)
        assert result.frequencyOfOccurrence is not None

    def test_from_dict_population(self):
        data = {'resourceType': 'MedicinalProductUndesirableEffect', 'population': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductUndesirableEffect)
        assert result.population is not None


class TestGetPathMedicinalProductUndesirableEffect:

    def test_get_path_id(self):
        resource = MedicinalProductUndesirableEffect()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = MedicinalProductUndesirableEffect()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = MedicinalProductUndesirableEffect()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'MedicinalProductUndesirableEffect.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = MedicinalProductUndesirableEffect()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = MedicinalProductUndesirableEffect()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = MedicinalProductUndesirableEffect()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = MedicinalProductUndesirableEffect()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = MedicinalProductUndesirableEffect()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = MedicinalProductUndesirableEffect()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = MedicinalProductUndesirableEffect()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_subject(self):
        resource = MedicinalProductUndesirableEffect()
        resource.subject = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_symptom_condition_effect(self):
        resource = MedicinalProductUndesirableEffect()
        resource.symptomConditionEffect = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'symptomConditionEffect')
        assert result is not None

    def test_get_path_classification(self):
        resource = MedicinalProductUndesirableEffect()
        resource.classification = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'classification')
        assert result is not None

    def test_get_path_frequency_of_occurrence(self):
        resource = MedicinalProductUndesirableEffect()
        resource.frequencyOfOccurrence = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'frequencyOfOccurrence')
        assert result is not None

    def test_get_path_population(self):
        resource = MedicinalProductUndesirableEffect()
        resource.population = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'population')
        assert result is not None


class TestSetPathMedicinalProductUndesirableEffect:

    def test_set_path_id(self):
        resource = MedicinalProductUndesirableEffect()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = MedicinalProductUndesirableEffect()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'MedicinalProductUndesirableEffect.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = MedicinalProductUndesirableEffect()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = MedicinalProductUndesirableEffect()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = MedicinalProductUndesirableEffect()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = MedicinalProductUndesirableEffect()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = MedicinalProductUndesirableEffect()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = MedicinalProductUndesirableEffect()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = MedicinalProductUndesirableEffect()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_subject(self):
        resource = MedicinalProductUndesirableEffect()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_symptom_condition_effect(self):
        resource = MedicinalProductUndesirableEffect()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'symptomConditionEffect', value)
        assert result is True
        assert resource.symptomConditionEffect is not None

    def test_set_path_classification(self):
        resource = MedicinalProductUndesirableEffect()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'classification', value)
        assert result is True
        assert resource.classification is not None

    def test_set_path_frequency_of_occurrence(self):
        resource = MedicinalProductUndesirableEffect()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'frequencyOfOccurrence', value)
        assert result is True
        assert resource.frequencyOfOccurrence is not None

    def test_set_path_population(self):
        resource = MedicinalProductUndesirableEffect()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'population', value)
        assert result is True
        assert resource.population is not None


class TestParsePathMedicinalProductUndesirableEffect:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductUndesirableEffect.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductUndesirableEffect.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductUndesirableEffect.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
