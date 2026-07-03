# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import VisionPrescription


class TestToDictVisionPrescription:

    def test_to_dict_empty(self):
        resource = VisionPrescription()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'VisionPrescription'

    def test_to_dict_with_id(self):
        resource = VisionPrescription()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = VisionPrescription()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, VisionPrescription)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = VisionPrescription()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = VisionPrescription()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = VisionPrescription()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = VisionPrescription()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = VisionPrescription()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = VisionPrescription()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = VisionPrescription()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = VisionPrescription()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = VisionPrescription()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = VisionPrescription()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_created(self):
        resource = VisionPrescription()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'created' in result

    def test_to_dict_patient(self):
        resource = VisionPrescription()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_encounter(self):
        resource = VisionPrescription()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_date_written(self):
        resource = VisionPrescription()
        resource.dateWritten = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dateWritten' in result

    def test_to_dict_prescriber(self):
        resource = VisionPrescription()
        resource.prescriber = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'prescriber' in result

    def test_to_dict_lens_specification(self):
        resource = VisionPrescription()
        resource.lensSpecification = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lensSpecification' in result


class TestFromDictVisionPrescription:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'VisionPrescription', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert isinstance(result, VisionPrescription)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'VisionPrescription'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert isinstance(result, VisionPrescription)

    def test_from_dict_id(self):
        data = {'resourceType': 'VisionPrescription', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'VisionPrescription', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'VisionPrescription', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'VisionPrescription', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'VisionPrescription', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'VisionPrescription', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'VisionPrescription', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'VisionPrescription', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'VisionPrescription', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'VisionPrescription', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.status is not None

    def test_from_dict_created(self):
        data = {'resourceType': 'VisionPrescription', 'created': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.created is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'VisionPrescription', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.patient is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'VisionPrescription', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.encounter is not None

    def test_from_dict_date_written(self):
        data = {'resourceType': 'VisionPrescription', 'dateWritten': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.dateWritten is not None

    def test_from_dict_prescriber(self):
        data = {'resourceType': 'VisionPrescription', 'prescriber': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.prescriber is not None

    def test_from_dict_lens_specification(self):
        data = {'resourceType': 'VisionPrescription', 'lensSpecification': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, VisionPrescription)
        assert result.lensSpecification is not None


class TestGetPathVisionPrescription:

    def test_get_path_id(self):
        resource = VisionPrescription()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = VisionPrescription()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = VisionPrescription()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'VisionPrescription.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = VisionPrescription()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = VisionPrescription()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = VisionPrescription()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = VisionPrescription()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = VisionPrescription()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = VisionPrescription()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = VisionPrescription()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = VisionPrescription()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = VisionPrescription()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_created(self):
        resource = VisionPrescription()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'created')
        assert result is not None

    def test_get_path_patient(self):
        resource = VisionPrescription()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_encounter(self):
        resource = VisionPrescription()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_date_written(self):
        resource = VisionPrescription()
        resource.dateWritten = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dateWritten')
        assert result is not None

    def test_get_path_prescriber(self):
        resource = VisionPrescription()
        resource.prescriber = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'prescriber')
        assert result is not None

    def test_get_path_lens_specification(self):
        resource = VisionPrescription()
        resource.lensSpecification = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lensSpecification')
        assert result is not None


class TestSetPathVisionPrescription:

    def test_set_path_id(self):
        resource = VisionPrescription()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = VisionPrescription()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'VisionPrescription.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = VisionPrescription()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = VisionPrescription()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = VisionPrescription()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = VisionPrescription()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = VisionPrescription()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = VisionPrescription()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = VisionPrescription()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = VisionPrescription()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = VisionPrescription()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_created(self):
        resource = VisionPrescription()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'created', value)
        assert result is True
        assert resource.created is not None

    def test_set_path_patient(self):
        resource = VisionPrescription()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_encounter(self):
        resource = VisionPrescription()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_date_written(self):
        resource = VisionPrescription()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dateWritten', value)
        assert result is True
        assert resource.dateWritten is not None

    def test_set_path_prescriber(self):
        resource = VisionPrescription()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'prescriber', value)
        assert result is True
        assert resource.prescriber is not None

    def test_set_path_lens_specification(self):
        resource = VisionPrescription()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lensSpecification', value)
        assert result is True
        assert resource.lensSpecification is not None


class TestParsePathVisionPrescription:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('VisionPrescription.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('VisionPrescription.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('VisionPrescription.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
