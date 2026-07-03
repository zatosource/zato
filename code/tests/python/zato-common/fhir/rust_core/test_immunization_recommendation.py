# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ImmunizationRecommendation


class TestToDictImmunizationRecommendation:

    def test_to_dict_empty(self):
        resource = ImmunizationRecommendation()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ImmunizationRecommendation'

    def test_to_dict_with_id(self):
        resource = ImmunizationRecommendation()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ImmunizationRecommendation()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ImmunizationRecommendation)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ImmunizationRecommendation()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ImmunizationRecommendation()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ImmunizationRecommendation()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ImmunizationRecommendation()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ImmunizationRecommendation()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ImmunizationRecommendation()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ImmunizationRecommendation()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ImmunizationRecommendation()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = ImmunizationRecommendation()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_patient(self):
        resource = ImmunizationRecommendation()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_date(self):
        resource = ImmunizationRecommendation()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_authority(self):
        resource = ImmunizationRecommendation()
        resource.authority = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'authority' in result

    def test_to_dict_recommendation(self):
        resource = ImmunizationRecommendation()
        resource.recommendation = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recommendation' in result


class TestFromDictImmunizationRecommendation:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ImmunizationRecommendation', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationRecommendation)
        assert isinstance(result, ImmunizationRecommendation)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ImmunizationRecommendation'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationRecommendation)
        assert isinstance(result, ImmunizationRecommendation)

    def test_from_dict_id(self):
        data = {'resourceType': 'ImmunizationRecommendation', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationRecommendation)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ImmunizationRecommendation', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationRecommendation)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ImmunizationRecommendation', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationRecommendation)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ImmunizationRecommendation', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationRecommendation)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ImmunizationRecommendation', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationRecommendation)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ImmunizationRecommendation', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationRecommendation)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ImmunizationRecommendation', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationRecommendation)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ImmunizationRecommendation', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationRecommendation)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'ImmunizationRecommendation', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationRecommendation)
        assert result.identifier is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'ImmunizationRecommendation', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationRecommendation)
        assert result.patient is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'ImmunizationRecommendation', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationRecommendation)
        assert result.date is not None

    def test_from_dict_authority(self):
        data = {'resourceType': 'ImmunizationRecommendation', 'authority': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationRecommendation)
        assert result.authority is not None

    def test_from_dict_recommendation(self):
        data = {'resourceType': 'ImmunizationRecommendation', 'recommendation': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImmunizationRecommendation)
        assert result.recommendation is not None


class TestGetPathImmunizationRecommendation:

    def test_get_path_id(self):
        resource = ImmunizationRecommendation()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ImmunizationRecommendation()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ImmunizationRecommendation()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ImmunizationRecommendation.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ImmunizationRecommendation()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ImmunizationRecommendation()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ImmunizationRecommendation()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ImmunizationRecommendation()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ImmunizationRecommendation()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ImmunizationRecommendation()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ImmunizationRecommendation()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = ImmunizationRecommendation()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_patient(self):
        resource = ImmunizationRecommendation()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_date(self):
        resource = ImmunizationRecommendation()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_authority(self):
        resource = ImmunizationRecommendation()
        resource.authority = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'authority')
        assert result is not None

    def test_get_path_recommendation(self):
        resource = ImmunizationRecommendation()
        resource.recommendation = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recommendation')
        assert result is not None


class TestSetPathImmunizationRecommendation:

    def test_set_path_id(self):
        resource = ImmunizationRecommendation()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ImmunizationRecommendation()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ImmunizationRecommendation.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ImmunizationRecommendation()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ImmunizationRecommendation()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ImmunizationRecommendation()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ImmunizationRecommendation()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ImmunizationRecommendation()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ImmunizationRecommendation()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ImmunizationRecommendation()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = ImmunizationRecommendation()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_patient(self):
        resource = ImmunizationRecommendation()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_date(self):
        resource = ImmunizationRecommendation()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_authority(self):
        resource = ImmunizationRecommendation()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'authority', value)
        assert result is True
        assert resource.authority is not None

    def test_set_path_recommendation(self):
        resource = ImmunizationRecommendation()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recommendation', value)
        assert result is True
        assert resource.recommendation is not None


class TestParsePathImmunizationRecommendation:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ImmunizationRecommendation.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ImmunizationRecommendation.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ImmunizationRecommendation.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
