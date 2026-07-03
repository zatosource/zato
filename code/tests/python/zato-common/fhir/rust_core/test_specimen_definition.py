# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import SpecimenDefinition


class TestToDictSpecimenDefinition:

    def test_to_dict_empty(self):
        resource = SpecimenDefinition()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'SpecimenDefinition'

    def test_to_dict_with_id(self):
        resource = SpecimenDefinition()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = SpecimenDefinition()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, SpecimenDefinition)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = SpecimenDefinition()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = SpecimenDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = SpecimenDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = SpecimenDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = SpecimenDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = SpecimenDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = SpecimenDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = SpecimenDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = SpecimenDefinition()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_type_collected(self):
        resource = SpecimenDefinition()
        resource.typeCollected = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'typeCollected' in result

    def test_to_dict_patient_preparation(self):
        resource = SpecimenDefinition()
        resource.patientPreparation = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patientPreparation' in result

    def test_to_dict_time_aspect(self):
        resource = SpecimenDefinition()
        resource.timeAspect = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'timeAspect' in result

    def test_to_dict_collection(self):
        resource = SpecimenDefinition()
        resource.collection = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'collection' in result

    def test_to_dict_type_tested(self):
        resource = SpecimenDefinition()
        resource.typeTested = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'typeTested' in result


class TestFromDictSpecimenDefinition:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'SpecimenDefinition', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert isinstance(result, SpecimenDefinition)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'SpecimenDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert isinstance(result, SpecimenDefinition)

    def test_from_dict_id(self):
        data = {'resourceType': 'SpecimenDefinition', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'SpecimenDefinition', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'SpecimenDefinition', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'SpecimenDefinition', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'SpecimenDefinition', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'SpecimenDefinition', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'SpecimenDefinition', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'SpecimenDefinition', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'SpecimenDefinition', 'identifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert result.identifier is not None

    def test_from_dict_type_collected(self):
        data = {'resourceType': 'SpecimenDefinition',
         'typeCollected': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert result.typeCollected is not None

    def test_from_dict_patient_preparation(self):
        data = {'patientPreparation': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                 'text': 'Test concept'}],
         'resourceType': 'SpecimenDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert result.patientPreparation is not None

    def test_from_dict_time_aspect(self):
        data = {'resourceType': 'SpecimenDefinition', 'timeAspect': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert result.timeAspect is not None

    def test_from_dict_collection(self):
        data = {'collection': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}],
         'resourceType': 'SpecimenDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert result.collection is not None

    def test_from_dict_type_tested(self):
        data = {'resourceType': 'SpecimenDefinition', 'typeTested': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SpecimenDefinition)
        assert result.typeTested is not None


class TestGetPathSpecimenDefinition:

    def test_get_path_id(self):
        resource = SpecimenDefinition()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = SpecimenDefinition()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = SpecimenDefinition()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'SpecimenDefinition.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = SpecimenDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = SpecimenDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = SpecimenDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = SpecimenDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = SpecimenDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = SpecimenDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = SpecimenDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = SpecimenDefinition()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_type_collected(self):
        resource = SpecimenDefinition()
        resource.typeCollected = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'typeCollected')
        assert result is not None

    def test_get_path_patient_preparation(self):
        resource = SpecimenDefinition()
        resource.patientPreparation = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patientPreparation')
        assert result is not None

    def test_get_path_time_aspect(self):
        resource = SpecimenDefinition()
        resource.timeAspect = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'timeAspect')
        assert result is not None

    def test_get_path_collection(self):
        resource = SpecimenDefinition()
        resource.collection = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'collection')
        assert result is not None

    def test_get_path_type_tested(self):
        resource = SpecimenDefinition()
        resource.typeTested = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'typeTested')
        assert result is not None


class TestSetPathSpecimenDefinition:

    def test_set_path_id(self):
        resource = SpecimenDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = SpecimenDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'SpecimenDefinition.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = SpecimenDefinition()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = SpecimenDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = SpecimenDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = SpecimenDefinition()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = SpecimenDefinition()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = SpecimenDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = SpecimenDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = SpecimenDefinition()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_type_collected(self):
        resource = SpecimenDefinition()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'typeCollected', value)
        assert result is True
        assert resource.typeCollected is not None

    def test_set_path_patient_preparation(self):
        resource = SpecimenDefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patientPreparation', value)
        assert result is True
        assert resource.patientPreparation is not None

    def test_set_path_time_aspect(self):
        resource = SpecimenDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'timeAspect', value)
        assert result is True
        assert resource.timeAspect is not None

    def test_set_path_collection(self):
        resource = SpecimenDefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'collection', value)
        assert result is True
        assert resource.collection is not None

    def test_set_path_type_tested(self):
        resource = SpecimenDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'typeTested', value)
        assert result is True
        assert resource.typeTested is not None


class TestParsePathSpecimenDefinition:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('SpecimenDefinition.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('SpecimenDefinition.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('SpecimenDefinition.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
