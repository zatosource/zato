# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ImagingStudy


class TestToDictImagingStudy:

    def test_to_dict_empty(self):
        resource = ImagingStudy()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ImagingStudy'

    def test_to_dict_with_id(self):
        resource = ImagingStudy()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ImagingStudy()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ImagingStudy)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ImagingStudy()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ImagingStudy()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ImagingStudy()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ImagingStudy()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ImagingStudy()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ImagingStudy()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ImagingStudy()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ImagingStudy()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = ImagingStudy()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = ImagingStudy()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_modality(self):
        resource = ImagingStudy()
        resource.modality = [{'system': 'http://example.org', 'code': 'test-code'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modality' in result

    def test_to_dict_subject(self):
        resource = ImagingStudy()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_encounter(self):
        resource = ImagingStudy()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_started(self):
        resource = ImagingStudy()
        resource.started = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'started' in result

    def test_to_dict_based_on(self):
        resource = ImagingStudy()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_referrer(self):
        resource = ImagingStudy()
        resource.referrer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'referrer' in result

    def test_to_dict_interpreter(self):
        resource = ImagingStudy()
        resource.interpreter = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'interpreter' in result

    def test_to_dict_endpoint(self):
        resource = ImagingStudy()
        resource.endpoint = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'endpoint' in result

    def test_to_dict_number_of_series(self):
        resource = ImagingStudy()
        resource.numberOfSeries = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'numberOfSeries' in result

    def test_to_dict_number_of_instances(self):
        resource = ImagingStudy()
        resource.numberOfInstances = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'numberOfInstances' in result

    def test_to_dict_procedure_reference(self):
        resource = ImagingStudy()
        resource.procedureReference = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'procedureReference' in result

    def test_to_dict_procedure_code(self):
        resource = ImagingStudy()
        resource.procedureCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'procedureCode' in result

    def test_to_dict_location(self):
        resource = ImagingStudy()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'location' in result

    def test_to_dict_reason_code(self):
        resource = ImagingStudy()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonCode' in result

    def test_to_dict_reason_reference(self):
        resource = ImagingStudy()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonReference' in result

    def test_to_dict_note(self):
        resource = ImagingStudy()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_description(self):
        resource = ImagingStudy()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_series(self):
        resource = ImagingStudy()
        resource.series = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'series' in result


class TestFromDictImagingStudy:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ImagingStudy', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert isinstance(result, ImagingStudy)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ImagingStudy'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert isinstance(result, ImagingStudy)

    def test_from_dict_id(self):
        data = {'resourceType': 'ImagingStudy', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ImagingStudy', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ImagingStudy', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ImagingStudy', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ImagingStudy', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ImagingStudy', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ImagingStudy', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ImagingStudy', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'ImagingStudy', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'ImagingStudy', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.status is not None

    def test_from_dict_modality(self):
        data = {'resourceType': 'ImagingStudy', 'modality': [{'system': 'http://example.org', 'code': 'test-code'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.modality is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'ImagingStudy', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.subject is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'ImagingStudy', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.encounter is not None

    def test_from_dict_started(self):
        data = {'resourceType': 'ImagingStudy', 'started': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.started is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'ImagingStudy', 'basedOn': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.basedOn is not None

    def test_from_dict_referrer(self):
        data = {'resourceType': 'ImagingStudy', 'referrer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.referrer is not None

    def test_from_dict_interpreter(self):
        data = {'resourceType': 'ImagingStudy', 'interpreter': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.interpreter is not None

    def test_from_dict_endpoint(self):
        data = {'resourceType': 'ImagingStudy', 'endpoint': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.endpoint is not None

    def test_from_dict_number_of_series(self):
        data = {'resourceType': 'ImagingStudy', 'numberOfSeries': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.numberOfSeries is not None

    def test_from_dict_number_of_instances(self):
        data = {'resourceType': 'ImagingStudy', 'numberOfInstances': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.numberOfInstances is not None

    def test_from_dict_procedure_reference(self):
        data = {'resourceType': 'ImagingStudy', 'procedureReference': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.procedureReference is not None

    def test_from_dict_procedure_code(self):
        data = {'procedureCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                            'text': 'Test concept'}],
         'resourceType': 'ImagingStudy'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.procedureCode is not None

    def test_from_dict_location(self):
        data = {'resourceType': 'ImagingStudy', 'location': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.location is not None

    def test_from_dict_reason_code(self):
        data = {'reasonCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}],
         'resourceType': 'ImagingStudy'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.reasonCode is not None

    def test_from_dict_reason_reference(self):
        data = {'resourceType': 'ImagingStudy', 'reasonReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.reasonReference is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'ImagingStudy', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.note is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'ImagingStudy', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.description is not None

    def test_from_dict_series(self):
        data = {'resourceType': 'ImagingStudy', 'series': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImagingStudy)
        assert result.series is not None


class TestGetPathImagingStudy:

    def test_get_path_id(self):
        resource = ImagingStudy()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ImagingStudy()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ImagingStudy()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ImagingStudy.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ImagingStudy()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ImagingStudy()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ImagingStudy()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ImagingStudy()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ImagingStudy()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ImagingStudy()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ImagingStudy()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = ImagingStudy()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = ImagingStudy()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_modality(self):
        resource = ImagingStudy()
        resource.modality = [{'system': 'http://example.org', 'code': 'test-code'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modality')
        assert result is not None

    def test_get_path_subject(self):
        resource = ImagingStudy()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_encounter(self):
        resource = ImagingStudy()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_started(self):
        resource = ImagingStudy()
        resource.started = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'started')
        assert result is not None

    def test_get_path_based_on(self):
        resource = ImagingStudy()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_referrer(self):
        resource = ImagingStudy()
        resource.referrer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'referrer')
        assert result is not None

    def test_get_path_interpreter(self):
        resource = ImagingStudy()
        resource.interpreter = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'interpreter')
        assert result is not None

    def test_get_path_endpoint(self):
        resource = ImagingStudy()
        resource.endpoint = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'endpoint')
        assert result is not None

    def test_get_path_number_of_series(self):
        resource = ImagingStudy()
        resource.numberOfSeries = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'numberOfSeries')
        assert result is not None

    def test_get_path_number_of_instances(self):
        resource = ImagingStudy()
        resource.numberOfInstances = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'numberOfInstances')
        assert result is not None

    def test_get_path_procedure_reference(self):
        resource = ImagingStudy()
        resource.procedureReference = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'procedureReference')
        assert result is not None

    def test_get_path_procedure_code(self):
        resource = ImagingStudy()
        resource.procedureCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'procedureCode')
        assert result is not None

    def test_get_path_location(self):
        resource = ImagingStudy()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'location')
        assert result is not None

    def test_get_path_reason_code(self):
        resource = ImagingStudy()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonCode')
        assert result is not None

    def test_get_path_reason_reference(self):
        resource = ImagingStudy()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonReference')
        assert result is not None

    def test_get_path_note(self):
        resource = ImagingStudy()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_description(self):
        resource = ImagingStudy()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_series(self):
        resource = ImagingStudy()
        resource.series = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'series')
        assert result is not None


class TestSetPathImagingStudy:

    def test_set_path_id(self):
        resource = ImagingStudy()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ImagingStudy()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ImagingStudy.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ImagingStudy()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ImagingStudy()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ImagingStudy()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ImagingStudy()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ImagingStudy()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ImagingStudy()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ImagingStudy()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = ImagingStudy()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = ImagingStudy()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_modality(self):
        resource = ImagingStudy()
        value = [{'system': 'http://example.org', 'code': 'test-code'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modality', value)
        assert result is True
        assert resource.modality is not None

    def test_set_path_subject(self):
        resource = ImagingStudy()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_encounter(self):
        resource = ImagingStudy()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_started(self):
        resource = ImagingStudy()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'started', value)
        assert result is True
        assert resource.started is not None

    def test_set_path_based_on(self):
        resource = ImagingStudy()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_referrer(self):
        resource = ImagingStudy()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'referrer', value)
        assert result is True
        assert resource.referrer is not None

    def test_set_path_interpreter(self):
        resource = ImagingStudy()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'interpreter', value)
        assert result is True
        assert resource.interpreter is not None

    def test_set_path_endpoint(self):
        resource = ImagingStudy()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'endpoint', value)
        assert result is True
        assert resource.endpoint is not None

    def test_set_path_number_of_series(self):
        resource = ImagingStudy()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'numberOfSeries', value)
        assert result is True
        assert resource.numberOfSeries is not None

    def test_set_path_number_of_instances(self):
        resource = ImagingStudy()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'numberOfInstances', value)
        assert result is True
        assert resource.numberOfInstances is not None

    def test_set_path_procedure_reference(self):
        resource = ImagingStudy()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'procedureReference', value)
        assert result is True
        assert resource.procedureReference is not None

    def test_set_path_procedure_code(self):
        resource = ImagingStudy()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'procedureCode', value)
        assert result is True
        assert resource.procedureCode is not None

    def test_set_path_location(self):
        resource = ImagingStudy()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'location', value)
        assert result is True
        assert resource.location is not None

    def test_set_path_reason_code(self):
        resource = ImagingStudy()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonCode', value)
        assert result is True
        assert resource.reasonCode is not None

    def test_set_path_reason_reference(self):
        resource = ImagingStudy()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonReference', value)
        assert result is True
        assert resource.reasonReference is not None

    def test_set_path_note(self):
        resource = ImagingStudy()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_description(self):
        resource = ImagingStudy()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_series(self):
        resource = ImagingStudy()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'series', value)
        assert result is True
        assert resource.series is not None


class TestParsePathImagingStudy:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ImagingStudy.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ImagingStudy.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ImagingStudy.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
