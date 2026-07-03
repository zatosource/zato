# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ExampleScenario


class TestToDictExampleScenario:

    def test_to_dict_empty(self):
        resource = ExampleScenario()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ExampleScenario'

    def test_to_dict_with_id(self):
        resource = ExampleScenario()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ExampleScenario()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ExampleScenario)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ExampleScenario()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ExampleScenario()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ExampleScenario()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ExampleScenario()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ExampleScenario()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ExampleScenario()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ExampleScenario()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ExampleScenario()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = ExampleScenario()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_identifier(self):
        resource = ExampleScenario()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_version(self):
        resource = ExampleScenario()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = ExampleScenario()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_status(self):
        resource = ExampleScenario()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = ExampleScenario()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = ExampleScenario()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = ExampleScenario()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = ExampleScenario()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_use_context(self):
        resource = ExampleScenario()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = ExampleScenario()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_copyright(self):
        resource = ExampleScenario()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_purpose(self):
        resource = ExampleScenario()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_actor(self):
        resource = ExampleScenario()
        resource.actor = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'actor' in result

    def test_to_dict_instance(self):
        resource = ExampleScenario()
        resource.instance = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instance' in result

    def test_to_dict_process(self):
        resource = ExampleScenario()
        resource.process = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'process' in result

    def test_to_dict_workflow(self):
        resource = ExampleScenario()
        resource.workflow = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'workflow' in result


class TestFromDictExampleScenario:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ExampleScenario', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert isinstance(result, ExampleScenario)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ExampleScenario'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert isinstance(result, ExampleScenario)

    def test_from_dict_id(self):
        data = {'resourceType': 'ExampleScenario', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ExampleScenario', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ExampleScenario', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ExampleScenario', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ExampleScenario', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ExampleScenario', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ExampleScenario', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ExampleScenario', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'ExampleScenario', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.url is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'ExampleScenario', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.identifier is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'ExampleScenario', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'ExampleScenario', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.name is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'ExampleScenario', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'ExampleScenario', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'ExampleScenario', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'ExampleScenario', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'ExampleScenario', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.contact is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'ExampleScenario', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'ExampleScenario'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.jurisdiction is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'ExampleScenario', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.copyright is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'ExampleScenario', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.purpose is not None

    def test_from_dict_actor(self):
        data = {'resourceType': 'ExampleScenario', 'actor': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.actor is not None

    def test_from_dict_instance(self):
        data = {'resourceType': 'ExampleScenario', 'instance': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.instance is not None

    def test_from_dict_process(self):
        data = {'resourceType': 'ExampleScenario', 'process': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.process is not None

    def test_from_dict_workflow(self):
        data = {'resourceType': 'ExampleScenario', 'workflow': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExampleScenario)
        assert result.workflow is not None


class TestGetPathExampleScenario:

    def test_get_path_id(self):
        resource = ExampleScenario()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ExampleScenario()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ExampleScenario()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ExampleScenario.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ExampleScenario()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ExampleScenario()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ExampleScenario()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ExampleScenario()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ExampleScenario()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ExampleScenario()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ExampleScenario()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = ExampleScenario()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_identifier(self):
        resource = ExampleScenario()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_version(self):
        resource = ExampleScenario()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = ExampleScenario()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_status(self):
        resource = ExampleScenario()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = ExampleScenario()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = ExampleScenario()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = ExampleScenario()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = ExampleScenario()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_use_context(self):
        resource = ExampleScenario()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = ExampleScenario()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_copyright(self):
        resource = ExampleScenario()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_purpose(self):
        resource = ExampleScenario()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_actor(self):
        resource = ExampleScenario()
        resource.actor = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'actor')
        assert result is not None

    def test_get_path_instance(self):
        resource = ExampleScenario()
        resource.instance = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instance')
        assert result is not None

    def test_get_path_process(self):
        resource = ExampleScenario()
        resource.process = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'process')
        assert result is not None

    def test_get_path_workflow(self):
        resource = ExampleScenario()
        resource.workflow = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'workflow')
        assert result is not None


class TestSetPathExampleScenario:

    def test_set_path_id(self):
        resource = ExampleScenario()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ExampleScenario()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ExampleScenario.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ExampleScenario()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ExampleScenario()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ExampleScenario()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ExampleScenario()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ExampleScenario()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ExampleScenario()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ExampleScenario()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = ExampleScenario()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_identifier(self):
        resource = ExampleScenario()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_version(self):
        resource = ExampleScenario()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = ExampleScenario()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_status(self):
        resource = ExampleScenario()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = ExampleScenario()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = ExampleScenario()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = ExampleScenario()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = ExampleScenario()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_use_context(self):
        resource = ExampleScenario()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = ExampleScenario()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_copyright(self):
        resource = ExampleScenario()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_purpose(self):
        resource = ExampleScenario()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_actor(self):
        resource = ExampleScenario()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'actor', value)
        assert result is True
        assert resource.actor is not None

    def test_set_path_instance(self):
        resource = ExampleScenario()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instance', value)
        assert result is True
        assert resource.instance is not None

    def test_set_path_process(self):
        resource = ExampleScenario()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'process', value)
        assert result is True
        assert resource.process is not None

    def test_set_path_workflow(self):
        resource = ExampleScenario()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'workflow', value)
        assert result is True
        assert resource.workflow is not None


class TestParsePathExampleScenario:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ExampleScenario.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ExampleScenario.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ExampleScenario.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
