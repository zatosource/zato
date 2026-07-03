# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import TestScript


class TestToDictTestScript:

    def test_to_dict_empty(self):
        resource = TestScript()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'TestScript'

    def test_to_dict_with_id(self):
        resource = TestScript()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = TestScript()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, TestScript)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = TestScript()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = TestScript()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = TestScript()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = TestScript()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = TestScript()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = TestScript()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = TestScript()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = TestScript()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = TestScript()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_identifier(self):
        resource = TestScript()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_version(self):
        resource = TestScript()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = TestScript()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = TestScript()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_status(self):
        resource = TestScript()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = TestScript()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = TestScript()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = TestScript()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = TestScript()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = TestScript()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = TestScript()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = TestScript()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_purpose(self):
        resource = TestScript()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_copyright(self):
        resource = TestScript()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_origin(self):
        resource = TestScript()
        resource.origin = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'origin' in result

    def test_to_dict_destination(self):
        resource = TestScript()
        resource.destination = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'destination' in result

    def test_to_dict_metadata(self):
        resource = TestScript()
        resource.metadata = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'metadata' in result

    def test_to_dict_fixture(self):
        resource = TestScript()
        resource.fixture = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'fixture' in result

    def test_to_dict_profile(self):
        resource = TestScript()
        resource.profile = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'profile' in result

    def test_to_dict_variable(self):
        resource = TestScript()
        resource.variable = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'variable' in result

    def test_to_dict_setup(self):
        resource = TestScript()
        resource.setup = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'setup' in result

    def test_to_dict_test(self):
        resource = TestScript()
        resource.test = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'test' in result

    def test_to_dict_teardown(self):
        resource = TestScript()
        resource.teardown = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'teardown' in result


class TestFromDictTestScript:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'TestScript', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert isinstance(result, TestScript)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'TestScript'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert isinstance(result, TestScript)

    def test_from_dict_id(self):
        data = {'resourceType': 'TestScript', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'TestScript', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'TestScript', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'TestScript', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'TestScript', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'TestScript', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'TestScript', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'TestScript', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'TestScript', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.url is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'TestScript', 'identifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.identifier is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'TestScript', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'TestScript', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'TestScript', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.title is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'TestScript', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'TestScript', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'TestScript', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'TestScript', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'TestScript', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'TestScript', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'TestScript', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'TestScript'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.jurisdiction is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'TestScript', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.purpose is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'TestScript', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.copyright is not None

    def test_from_dict_origin(self):
        data = {'resourceType': 'TestScript', 'origin': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.origin is not None

    def test_from_dict_destination(self):
        data = {'resourceType': 'TestScript', 'destination': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.destination is not None

    def test_from_dict_metadata(self):
        data = {'resourceType': 'TestScript', 'metadata': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.metadata is not None

    def test_from_dict_fixture(self):
        data = {'resourceType': 'TestScript', 'fixture': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.fixture is not None

    def test_from_dict_profile(self):
        data = {'resourceType': 'TestScript', 'profile': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.profile is not None

    def test_from_dict_variable(self):
        data = {'resourceType': 'TestScript', 'variable': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.variable is not None

    def test_from_dict_setup(self):
        data = {'resourceType': 'TestScript', 'setup': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.setup is not None

    def test_from_dict_test(self):
        data = {'resourceType': 'TestScript', 'test': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.test is not None

    def test_from_dict_teardown(self):
        data = {'resourceType': 'TestScript', 'teardown': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TestScript)
        assert result.teardown is not None


class TestGetPathTestScript:

    def test_get_path_id(self):
        resource = TestScript()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = TestScript()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = TestScript()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'TestScript.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = TestScript()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = TestScript()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = TestScript()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = TestScript()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = TestScript()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = TestScript()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = TestScript()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = TestScript()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_identifier(self):
        resource = TestScript()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_version(self):
        resource = TestScript()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = TestScript()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = TestScript()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_status(self):
        resource = TestScript()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = TestScript()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = TestScript()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = TestScript()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = TestScript()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = TestScript()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = TestScript()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = TestScript()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_purpose(self):
        resource = TestScript()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_copyright(self):
        resource = TestScript()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_origin(self):
        resource = TestScript()
        resource.origin = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'origin')
        assert result is not None

    def test_get_path_destination(self):
        resource = TestScript()
        resource.destination = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'destination')
        assert result is not None

    def test_get_path_metadata(self):
        resource = TestScript()
        resource.metadata = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'metadata')
        assert result is not None

    def test_get_path_fixture(self):
        resource = TestScript()
        resource.fixture = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'fixture')
        assert result is not None

    def test_get_path_profile(self):
        resource = TestScript()
        resource.profile = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'profile')
        assert result is not None

    def test_get_path_variable(self):
        resource = TestScript()
        resource.variable = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'variable')
        assert result is not None

    def test_get_path_setup(self):
        resource = TestScript()
        resource.setup = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'setup')
        assert result is not None

    def test_get_path_test(self):
        resource = TestScript()
        resource.test = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'test')
        assert result is not None

    def test_get_path_teardown(self):
        resource = TestScript()
        resource.teardown = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'teardown')
        assert result is not None


class TestSetPathTestScript:

    def test_set_path_id(self):
        resource = TestScript()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = TestScript()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'TestScript.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = TestScript()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = TestScript()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = TestScript()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = TestScript()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = TestScript()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = TestScript()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = TestScript()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = TestScript()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_identifier(self):
        resource = TestScript()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_version(self):
        resource = TestScript()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = TestScript()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = TestScript()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_status(self):
        resource = TestScript()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = TestScript()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = TestScript()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = TestScript()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = TestScript()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = TestScript()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = TestScript()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = TestScript()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_purpose(self):
        resource = TestScript()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_copyright(self):
        resource = TestScript()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_origin(self):
        resource = TestScript()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'origin', value)
        assert result is True
        assert resource.origin is not None

    def test_set_path_destination(self):
        resource = TestScript()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'destination', value)
        assert result is True
        assert resource.destination is not None

    def test_set_path_metadata(self):
        resource = TestScript()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'metadata', value)
        assert result is True
        assert resource.metadata is not None

    def test_set_path_fixture(self):
        resource = TestScript()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'fixture', value)
        assert result is True
        assert resource.fixture is not None

    def test_set_path_profile(self):
        resource = TestScript()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'profile', value)
        assert result is True
        assert resource.profile is not None

    def test_set_path_variable(self):
        resource = TestScript()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'variable', value)
        assert result is True
        assert resource.variable is not None

    def test_set_path_setup(self):
        resource = TestScript()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'setup', value)
        assert result is True
        assert resource.setup is not None

    def test_set_path_test(self):
        resource = TestScript()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'test', value)
        assert result is True
        assert resource.test is not None

    def test_set_path_teardown(self):
        resource = TestScript()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'teardown', value)
        assert result is True
        assert resource.teardown is not None


class TestParsePathTestScript:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('TestScript.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('TestScript.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('TestScript.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
