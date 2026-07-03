# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import TestReport


class TestToDictTestReport:

    def test_to_dict_empty(self):
        resource = TestReport()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'TestReport'

    def test_to_dict_with_id(self):
        resource = TestReport()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = TestReport()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, TestReport)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = TestReport()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = TestReport()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = TestReport()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = TestReport()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = TestReport()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = TestReport()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = TestReport()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = TestReport()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = TestReport()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_name(self):
        resource = TestReport()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_status(self):
        resource = TestReport()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_test_script(self):
        resource = TestReport()
        resource.testScript = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'testScript' in result

    def test_to_dict_result(self):
        resource = TestReport()
        resource.result = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'result' in result

    def test_to_dict_score(self):
        resource = TestReport()
        resource.score = 3.14
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'score' in result

    def test_to_dict_tester(self):
        resource = TestReport()
        resource.tester = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'tester' in result

    def test_to_dict_issued(self):
        resource = TestReport()
        resource.issued = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'issued' in result

    def test_to_dict_participant(self):
        resource = TestReport()
        resource.participant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'participant' in result

    def test_to_dict_setup(self):
        resource = TestReport()
        resource.setup = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'setup' in result

    def test_to_dict_test(self):
        resource = TestReport()
        resource.test = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'test' in result

    def test_to_dict_teardown(self):
        resource = TestReport()
        resource.teardown = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'teardown' in result


class TestFromDictTestReport:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'TestReport', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert isinstance(result, TestReport)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'TestReport'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert isinstance(result, TestReport)

    def test_from_dict_id(self):
        data = {'resourceType': 'TestReport', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'TestReport', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'TestReport', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'TestReport', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'TestReport', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'TestReport', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'TestReport', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'TestReport', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'TestReport', 'identifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.identifier is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'TestReport', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.name is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'TestReport', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.status is not None

    def test_from_dict_test_script(self):
        data = {'resourceType': 'TestReport', 'testScript': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.testScript is not None

    def test_from_dict_result(self):
        data = {'resourceType': 'TestReport', 'result': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.result is not None

    def test_from_dict_score(self):
        data = {'resourceType': 'TestReport', 'score': 3.14}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.score is not None

    def test_from_dict_tester(self):
        data = {'resourceType': 'TestReport', 'tester': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.tester is not None

    def test_from_dict_issued(self):
        data = {'resourceType': 'TestReport', 'issued': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.issued is not None

    def test_from_dict_participant(self):
        data = {'resourceType': 'TestReport', 'participant': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.participant is not None

    def test_from_dict_setup(self):
        data = {'resourceType': 'TestReport', 'setup': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.setup is not None

    def test_from_dict_test(self):
        data = {'resourceType': 'TestReport', 'test': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.test is not None

    def test_from_dict_teardown(self):
        data = {'resourceType': 'TestReport', 'teardown': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestReport)
        assert result.teardown is not None


class TestGetPathTestReport:

    def test_get_path_id(self):
        resource = TestReport()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = TestReport()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = TestReport()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'TestReport.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = TestReport()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = TestReport()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = TestReport()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = TestReport()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = TestReport()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = TestReport()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = TestReport()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = TestReport()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_name(self):
        resource = TestReport()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_status(self):
        resource = TestReport()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_test_script(self):
        resource = TestReport()
        resource.testScript = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'testScript')
        assert result is not None

    def test_get_path_result(self):
        resource = TestReport()
        resource.result = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'result')
        assert result is not None

    def test_get_path_score(self):
        resource = TestReport()
        resource.score = 3.14
        result = zato.fhir_r4_0_1_core.get_path(resource, 'score')
        assert result is not None

    def test_get_path_tester(self):
        resource = TestReport()
        resource.tester = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'tester')
        assert result is not None

    def test_get_path_issued(self):
        resource = TestReport()
        resource.issued = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'issued')
        assert result is not None

    def test_get_path_participant(self):
        resource = TestReport()
        resource.participant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'participant')
        assert result is not None

    def test_get_path_setup(self):
        resource = TestReport()
        resource.setup = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'setup')
        assert result is not None

    def test_get_path_test(self):
        resource = TestReport()
        resource.test = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'test')
        assert result is not None

    def test_get_path_teardown(self):
        resource = TestReport()
        resource.teardown = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'teardown')
        assert result is not None


class TestSetPathTestReport:

    def test_set_path_id(self):
        resource = TestReport()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = TestReport()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'TestReport.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = TestReport()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = TestReport()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = TestReport()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = TestReport()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = TestReport()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = TestReport()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = TestReport()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = TestReport()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_name(self):
        resource = TestReport()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_status(self):
        resource = TestReport()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_test_script(self):
        resource = TestReport()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'testScript', value)
        assert result is True
        assert resource.testScript is not None

    def test_set_path_result(self):
        resource = TestReport()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'result', value)
        assert result is True
        assert resource.result is not None

    def test_set_path_score(self):
        resource = TestReport()
        value = 3.14
        result = zato.fhir_r4_0_1_core.set_path(resource, 'score', value)
        assert result is True
        assert resource.score is not None

    def test_set_path_tester(self):
        resource = TestReport()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'tester', value)
        assert result is True
        assert resource.tester is not None

    def test_set_path_issued(self):
        resource = TestReport()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'issued', value)
        assert result is True
        assert resource.issued is not None

    def test_set_path_participant(self):
        resource = TestReport()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'participant', value)
        assert result is True
        assert resource.participant is not None

    def test_set_path_setup(self):
        resource = TestReport()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'setup', value)
        assert result is True
        assert resource.setup is not None

    def test_set_path_test(self):
        resource = TestReport()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'test', value)
        assert result is True
        assert resource.test is not None

    def test_set_path_teardown(self):
        resource = TestReport()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'teardown', value)
        assert result is True
        assert resource.teardown is not None


class TestParsePathTestReport:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('TestReport.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('TestReport.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('TestReport.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
