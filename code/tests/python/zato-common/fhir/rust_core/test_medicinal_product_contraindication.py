# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import MedicinalProductContraindication


class TestToDictMedicinalProductContraindication:

    def test_to_dict_empty(self):
        resource = MedicinalProductContraindication()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'MedicinalProductContraindication'

    def test_to_dict_with_id(self):
        resource = MedicinalProductContraindication()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = MedicinalProductContraindication()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, MedicinalProductContraindication)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = MedicinalProductContraindication()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = MedicinalProductContraindication()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = MedicinalProductContraindication()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = MedicinalProductContraindication()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = MedicinalProductContraindication()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = MedicinalProductContraindication()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = MedicinalProductContraindication()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = MedicinalProductContraindication()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_subject(self):
        resource = MedicinalProductContraindication()
        resource.subject = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_disease(self):
        resource = MedicinalProductContraindication()
        resource.disease = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'disease' in result

    def test_to_dict_disease_status(self):
        resource = MedicinalProductContraindication()
        resource.diseaseStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'diseaseStatus' in result

    def test_to_dict_comorbidity(self):
        resource = MedicinalProductContraindication()
        resource.comorbidity = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'comorbidity' in result

    def test_to_dict_therapeutic_indication(self):
        resource = MedicinalProductContraindication()
        resource.therapeuticIndication = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'therapeuticIndication' in result

    def test_to_dict_other_therapy(self):
        resource = MedicinalProductContraindication()
        resource.otherTherapy = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'otherTherapy' in result

    def test_to_dict_population(self):
        resource = MedicinalProductContraindication()
        resource.population = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'population' in result


class TestFromDictMedicinalProductContraindication:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'MedicinalProductContraindication', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert isinstance(result, MedicinalProductContraindication)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'MedicinalProductContraindication'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert isinstance(result, MedicinalProductContraindication)

    def test_from_dict_id(self):
        data = {'resourceType': 'MedicinalProductContraindication', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'MedicinalProductContraindication', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'MedicinalProductContraindication', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'MedicinalProductContraindication', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'MedicinalProductContraindication',
         'text': {'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>', 'status': 'generated'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'MedicinalProductContraindication', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'MedicinalProductContraindication', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'MedicinalProductContraindication', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert result.modifierExtension is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'MedicinalProductContraindication', 'subject': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert result.subject is not None

    def test_from_dict_disease(self):
        data = {'disease': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                     'text': 'Test concept'},
         'resourceType': 'MedicinalProductContraindication'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert result.disease is not None

    def test_from_dict_disease_status(self):
        data = {'diseaseStatus': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'},
         'resourceType': 'MedicinalProductContraindication'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert result.diseaseStatus is not None

    def test_from_dict_comorbidity(self):
        data = {'comorbidity': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'}],
         'resourceType': 'MedicinalProductContraindication'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert result.comorbidity is not None

    def test_from_dict_therapeutic_indication(self):
        data = {'resourceType': 'MedicinalProductContraindication', 'therapeuticIndication': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert result.therapeuticIndication is not None

    def test_from_dict_other_therapy(self):
        data = {'resourceType': 'MedicinalProductContraindication', 'otherTherapy': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert result.otherTherapy is not None

    def test_from_dict_population(self):
        data = {'resourceType': 'MedicinalProductContraindication', 'population': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductContraindication)
        assert result.population is not None


class TestGetPathMedicinalProductContraindication:

    def test_get_path_id(self):
        resource = MedicinalProductContraindication()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = MedicinalProductContraindication()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = MedicinalProductContraindication()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'MedicinalProductContraindication.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = MedicinalProductContraindication()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = MedicinalProductContraindication()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = MedicinalProductContraindication()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = MedicinalProductContraindication()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = MedicinalProductContraindication()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = MedicinalProductContraindication()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = MedicinalProductContraindication()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_subject(self):
        resource = MedicinalProductContraindication()
        resource.subject = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_disease(self):
        resource = MedicinalProductContraindication()
        resource.disease = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'disease')
        assert result is not None

    def test_get_path_disease_status(self):
        resource = MedicinalProductContraindication()
        resource.diseaseStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'diseaseStatus')
        assert result is not None

    def test_get_path_comorbidity(self):
        resource = MedicinalProductContraindication()
        resource.comorbidity = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'comorbidity')
        assert result is not None

    def test_get_path_therapeutic_indication(self):
        resource = MedicinalProductContraindication()
        resource.therapeuticIndication = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'therapeuticIndication')
        assert result is not None

    def test_get_path_other_therapy(self):
        resource = MedicinalProductContraindication()
        resource.otherTherapy = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'otherTherapy')
        assert result is not None

    def test_get_path_population(self):
        resource = MedicinalProductContraindication()
        resource.population = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'population')
        assert result is not None


class TestSetPathMedicinalProductContraindication:

    def test_set_path_id(self):
        resource = MedicinalProductContraindication()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = MedicinalProductContraindication()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'MedicinalProductContraindication.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = MedicinalProductContraindication()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = MedicinalProductContraindication()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = MedicinalProductContraindication()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = MedicinalProductContraindication()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = MedicinalProductContraindication()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = MedicinalProductContraindication()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = MedicinalProductContraindication()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_subject(self):
        resource = MedicinalProductContraindication()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_disease(self):
        resource = MedicinalProductContraindication()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'disease', value)
        assert result is True
        assert resource.disease is not None

    def test_set_path_disease_status(self):
        resource = MedicinalProductContraindication()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'diseaseStatus', value)
        assert result is True
        assert resource.diseaseStatus is not None

    def test_set_path_comorbidity(self):
        resource = MedicinalProductContraindication()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'comorbidity', value)
        assert result is True
        assert resource.comorbidity is not None

    def test_set_path_therapeutic_indication(self):
        resource = MedicinalProductContraindication()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'therapeuticIndication', value)
        assert result is True
        assert resource.therapeuticIndication is not None

    def test_set_path_other_therapy(self):
        resource = MedicinalProductContraindication()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'otherTherapy', value)
        assert result is True
        assert resource.otherTherapy is not None

    def test_set_path_population(self):
        resource = MedicinalProductContraindication()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'population', value)
        assert result is True
        assert resource.population is not None


class TestParsePathMedicinalProductContraindication:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductContraindication.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductContraindication.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductContraindication.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
