# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import DetectedIssue


class TestToDictDetectedIssue:

    def test_to_dict_empty(self):
        resource = DetectedIssue()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'DetectedIssue'

    def test_to_dict_with_id(self):
        resource = DetectedIssue()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = DetectedIssue()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, DetectedIssue)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = DetectedIssue()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = DetectedIssue()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = DetectedIssue()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = DetectedIssue()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = DetectedIssue()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = DetectedIssue()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = DetectedIssue()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = DetectedIssue()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = DetectedIssue()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = DetectedIssue()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_code(self):
        resource = DetectedIssue()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_severity(self):
        resource = DetectedIssue()
        resource.severity = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'severity' in result

    def test_to_dict_patient(self):
        resource = DetectedIssue()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_author(self):
        resource = DetectedIssue()
        resource.author = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_implicated(self):
        resource = DetectedIssue()
        resource.implicated = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicated' in result

    def test_to_dict_evidence(self):
        resource = DetectedIssue()
        resource.evidence = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'evidence' in result

    def test_to_dict_detail(self):
        resource = DetectedIssue()
        resource.detail = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'detail' in result

    def test_to_dict_reference(self):
        resource = DetectedIssue()
        resource.reference = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reference' in result

    def test_to_dict_mitigation(self):
        resource = DetectedIssue()
        resource.mitigation = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'mitigation' in result


class TestFromDictDetectedIssue:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'DetectedIssue', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert isinstance(result, DetectedIssue)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'DetectedIssue'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert isinstance(result, DetectedIssue)

    def test_from_dict_id(self):
        data = {'resourceType': 'DetectedIssue', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'DetectedIssue', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'DetectedIssue', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'DetectedIssue', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'DetectedIssue', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'DetectedIssue', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'DetectedIssue', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'DetectedIssue', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'DetectedIssue', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'DetectedIssue', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.status is not None

    def test_from_dict_code(self):
        data = {'code': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'DetectedIssue'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.code is not None

    def test_from_dict_severity(self):
        data = {'resourceType': 'DetectedIssue', 'severity': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.severity is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'DetectedIssue', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.patient is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'DetectedIssue', 'author': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.author is not None

    def test_from_dict_implicated(self):
        data = {'resourceType': 'DetectedIssue', 'implicated': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.implicated is not None

    def test_from_dict_evidence(self):
        data = {'resourceType': 'DetectedIssue', 'evidence': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.evidence is not None

    def test_from_dict_detail(self):
        data = {'resourceType': 'DetectedIssue', 'detail': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.detail is not None

    def test_from_dict_reference(self):
        data = {'resourceType': 'DetectedIssue', 'reference': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.reference is not None

    def test_from_dict_mitigation(self):
        data = {'resourceType': 'DetectedIssue', 'mitigation': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DetectedIssue)
        assert result.mitigation is not None


class TestGetPathDetectedIssue:

    def test_get_path_id(self):
        resource = DetectedIssue()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = DetectedIssue()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = DetectedIssue()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'DetectedIssue.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = DetectedIssue()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = DetectedIssue()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = DetectedIssue()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = DetectedIssue()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = DetectedIssue()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = DetectedIssue()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = DetectedIssue()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = DetectedIssue()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = DetectedIssue()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_code(self):
        resource = DetectedIssue()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_severity(self):
        resource = DetectedIssue()
        resource.severity = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'severity')
        assert result is not None

    def test_get_path_patient(self):
        resource = DetectedIssue()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_author(self):
        resource = DetectedIssue()
        resource.author = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_implicated(self):
        resource = DetectedIssue()
        resource.implicated = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicated')
        assert result is not None

    def test_get_path_evidence(self):
        resource = DetectedIssue()
        resource.evidence = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'evidence')
        assert result is not None

    def test_get_path_detail(self):
        resource = DetectedIssue()
        resource.detail = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'detail')
        assert result is not None

    def test_get_path_reference(self):
        resource = DetectedIssue()
        resource.reference = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reference')
        assert result is not None

    def test_get_path_mitigation(self):
        resource = DetectedIssue()
        resource.mitigation = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'mitigation')
        assert result is not None


class TestSetPathDetectedIssue:

    def test_set_path_id(self):
        resource = DetectedIssue()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = DetectedIssue()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'DetectedIssue.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = DetectedIssue()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = DetectedIssue()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = DetectedIssue()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = DetectedIssue()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = DetectedIssue()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = DetectedIssue()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = DetectedIssue()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = DetectedIssue()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = DetectedIssue()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_code(self):
        resource = DetectedIssue()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_severity(self):
        resource = DetectedIssue()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'severity', value)
        assert result is True
        assert resource.severity is not None

    def test_set_path_patient(self):
        resource = DetectedIssue()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_author(self):
        resource = DetectedIssue()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_implicated(self):
        resource = DetectedIssue()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicated', value)
        assert result is True
        assert resource.implicated is not None

    def test_set_path_evidence(self):
        resource = DetectedIssue()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'evidence', value)
        assert result is True
        assert resource.evidence is not None

    def test_set_path_detail(self):
        resource = DetectedIssue()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'detail', value)
        assert result is True
        assert resource.detail is not None

    def test_set_path_reference(self):
        resource = DetectedIssue()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reference', value)
        assert result is True
        assert resource.reference is not None

    def test_set_path_mitigation(self):
        resource = DetectedIssue()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'mitigation', value)
        assert result is True
        assert resource.mitigation is not None


class TestParsePathDetectedIssue:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('DetectedIssue.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('DetectedIssue.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('DetectedIssue.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
