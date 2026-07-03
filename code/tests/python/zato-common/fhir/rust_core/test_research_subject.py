# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ResearchSubject


class TestToDictResearchSubject:

    def test_to_dict_empty(self):
        resource = ResearchSubject()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ResearchSubject'

    def test_to_dict_with_id(self):
        resource = ResearchSubject()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ResearchSubject()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ResearchSubject)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ResearchSubject()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ResearchSubject()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ResearchSubject()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ResearchSubject()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ResearchSubject()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ResearchSubject()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ResearchSubject()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ResearchSubject()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = ResearchSubject()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = ResearchSubject()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_period(self):
        resource = ResearchSubject()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'period' in result

    def test_to_dict_study(self):
        resource = ResearchSubject()
        resource.study = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'study' in result

    def test_to_dict_individual(self):
        resource = ResearchSubject()
        resource.individual = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'individual' in result

    def test_to_dict_assigned_arm(self):
        resource = ResearchSubject()
        resource.assignedArm = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'assignedArm' in result

    def test_to_dict_actual_arm(self):
        resource = ResearchSubject()
        resource.actualArm = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'actualArm' in result

    def test_to_dict_consent(self):
        resource = ResearchSubject()
        resource.consent = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'consent' in result


class TestFromDictResearchSubject:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ResearchSubject', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert isinstance(result, ResearchSubject)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ResearchSubject'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert isinstance(result, ResearchSubject)

    def test_from_dict_id(self):
        data = {'resourceType': 'ResearchSubject', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ResearchSubject', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ResearchSubject', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ResearchSubject', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ResearchSubject', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ResearchSubject', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ResearchSubject', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ResearchSubject', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'ResearchSubject', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'ResearchSubject', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.status is not None

    def test_from_dict_period(self):
        data = {'resourceType': 'ResearchSubject', 'period': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.period is not None

    def test_from_dict_study(self):
        data = {'resourceType': 'ResearchSubject', 'study': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.study is not None

    def test_from_dict_individual(self):
        data = {'resourceType': 'ResearchSubject', 'individual': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.individual is not None

    def test_from_dict_assigned_arm(self):
        data = {'resourceType': 'ResearchSubject', 'assignedArm': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.assignedArm is not None

    def test_from_dict_actual_arm(self):
        data = {'resourceType': 'ResearchSubject', 'actualArm': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.actualArm is not None

    def test_from_dict_consent(self):
        data = {'resourceType': 'ResearchSubject', 'consent': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchSubject)
        assert result.consent is not None


class TestGetPathResearchSubject:

    def test_get_path_id(self):
        resource = ResearchSubject()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ResearchSubject()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ResearchSubject()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ResearchSubject.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ResearchSubject()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ResearchSubject()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ResearchSubject()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ResearchSubject()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ResearchSubject()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ResearchSubject()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ResearchSubject()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = ResearchSubject()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = ResearchSubject()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_period(self):
        resource = ResearchSubject()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'period')
        assert result is not None

    def test_get_path_study(self):
        resource = ResearchSubject()
        resource.study = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'study')
        assert result is not None

    def test_get_path_individual(self):
        resource = ResearchSubject()
        resource.individual = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'individual')
        assert result is not None

    def test_get_path_assigned_arm(self):
        resource = ResearchSubject()
        resource.assignedArm = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'assignedArm')
        assert result is not None

    def test_get_path_actual_arm(self):
        resource = ResearchSubject()
        resource.actualArm = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'actualArm')
        assert result is not None

    def test_get_path_consent(self):
        resource = ResearchSubject()
        resource.consent = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'consent')
        assert result is not None


class TestSetPathResearchSubject:

    def test_set_path_id(self):
        resource = ResearchSubject()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ResearchSubject()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ResearchSubject.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ResearchSubject()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ResearchSubject()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ResearchSubject()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ResearchSubject()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ResearchSubject()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ResearchSubject()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ResearchSubject()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = ResearchSubject()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = ResearchSubject()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_period(self):
        resource = ResearchSubject()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'period', value)
        assert result is True
        assert resource.period is not None

    def test_set_path_study(self):
        resource = ResearchSubject()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'study', value)
        assert result is True
        assert resource.study is not None

    def test_set_path_individual(self):
        resource = ResearchSubject()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'individual', value)
        assert result is True
        assert resource.individual is not None

    def test_set_path_assigned_arm(self):
        resource = ResearchSubject()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'assignedArm', value)
        assert result is True
        assert resource.assignedArm is not None

    def test_set_path_actual_arm(self):
        resource = ResearchSubject()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'actualArm', value)
        assert result is True
        assert resource.actualArm is not None

    def test_set_path_consent(self):
        resource = ResearchSubject()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'consent', value)
        assert result is True
        assert resource.consent is not None


class TestParsePathResearchSubject:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ResearchSubject.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ResearchSubject.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ResearchSubject.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
