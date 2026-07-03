# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import MessageDefinition


class TestToDictMessageDefinition:

    def test_to_dict_empty(self):
        resource = MessageDefinition()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'MessageDefinition'

    def test_to_dict_with_id(self):
        resource = MessageDefinition()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = MessageDefinition()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, MessageDefinition)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = MessageDefinition()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = MessageDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = MessageDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = MessageDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = MessageDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = MessageDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = MessageDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = MessageDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = MessageDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_identifier(self):
        resource = MessageDefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_version(self):
        resource = MessageDefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = MessageDefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = MessageDefinition()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_replaces(self):
        resource = MessageDefinition()
        resource.replaces = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'replaces' in result

    def test_to_dict_status(self):
        resource = MessageDefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = MessageDefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = MessageDefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = MessageDefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = MessageDefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = MessageDefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = MessageDefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = MessageDefinition()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_purpose(self):
        resource = MessageDefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_copyright(self):
        resource = MessageDefinition()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_base(self):
        resource = MessageDefinition()
        resource.base = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'base' in result

    def test_to_dict_parent(self):
        resource = MessageDefinition()
        resource.parent = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'parent' in result

    def test_to_dict_category(self):
        resource = MessageDefinition()
        resource.category = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_focus(self):
        resource = MessageDefinition()
        resource.focus = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'focus' in result

    def test_to_dict_response_required(self):
        resource = MessageDefinition()
        resource.responseRequired = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'responseRequired' in result

    def test_to_dict_allowed_response(self):
        resource = MessageDefinition()
        resource.allowedResponse = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'allowedResponse' in result

    def test_to_dict_graph(self):
        resource = MessageDefinition()
        resource.graph = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'graph' in result


class TestFromDictMessageDefinition:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'MessageDefinition', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert isinstance(result, MessageDefinition)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'MessageDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert isinstance(result, MessageDefinition)

    def test_from_dict_id(self):
        data = {'resourceType': 'MessageDefinition', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'MessageDefinition', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'MessageDefinition', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'MessageDefinition', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'MessageDefinition', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'MessageDefinition', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'MessageDefinition', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'MessageDefinition', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'MessageDefinition', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.url is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'MessageDefinition', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.identifier is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'MessageDefinition', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'MessageDefinition', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'MessageDefinition', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.title is not None

    def test_from_dict_replaces(self):
        data = {'resourceType': 'MessageDefinition', 'replaces': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.replaces is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'MessageDefinition', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'MessageDefinition', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'MessageDefinition', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'MessageDefinition', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'MessageDefinition', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'MessageDefinition', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'MessageDefinition', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'MessageDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.jurisdiction is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'MessageDefinition', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.purpose is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'MessageDefinition', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.copyright is not None

    def test_from_dict_base(self):
        data = {'resourceType': 'MessageDefinition', 'base': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.base is not None

    def test_from_dict_parent(self):
        data = {'resourceType': 'MessageDefinition', 'parent': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.parent is not None

    def test_from_dict_category(self):
        data = {'resourceType': 'MessageDefinition', 'category': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.category is not None

    def test_from_dict_focus(self):
        data = {'resourceType': 'MessageDefinition', 'focus': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.focus is not None

    def test_from_dict_response_required(self):
        data = {'resourceType': 'MessageDefinition', 'responseRequired': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.responseRequired is not None

    def test_from_dict_allowed_response(self):
        data = {'resourceType': 'MessageDefinition', 'allowedResponse': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.allowedResponse is not None

    def test_from_dict_graph(self):
        data = {'resourceType': 'MessageDefinition', 'graph': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageDefinition)
        assert result.graph is not None


class TestGetPathMessageDefinition:

    def test_get_path_id(self):
        resource = MessageDefinition()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = MessageDefinition()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = MessageDefinition()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'MessageDefinition.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = MessageDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = MessageDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = MessageDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = MessageDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = MessageDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = MessageDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = MessageDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = MessageDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_identifier(self):
        resource = MessageDefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_version(self):
        resource = MessageDefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = MessageDefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = MessageDefinition()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_replaces(self):
        resource = MessageDefinition()
        resource.replaces = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'replaces')
        assert result is not None

    def test_get_path_status(self):
        resource = MessageDefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = MessageDefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = MessageDefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = MessageDefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = MessageDefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = MessageDefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = MessageDefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = MessageDefinition()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_purpose(self):
        resource = MessageDefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_copyright(self):
        resource = MessageDefinition()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_base(self):
        resource = MessageDefinition()
        resource.base = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'base')
        assert result is not None

    def test_get_path_parent(self):
        resource = MessageDefinition()
        resource.parent = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'parent')
        assert result is not None

    def test_get_path_category(self):
        resource = MessageDefinition()
        resource.category = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_focus(self):
        resource = MessageDefinition()
        resource.focus = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'focus')
        assert result is not None

    def test_get_path_response_required(self):
        resource = MessageDefinition()
        resource.responseRequired = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'responseRequired')
        assert result is not None

    def test_get_path_allowed_response(self):
        resource = MessageDefinition()
        resource.allowedResponse = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'allowedResponse')
        assert result is not None

    def test_get_path_graph(self):
        resource = MessageDefinition()
        resource.graph = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'graph')
        assert result is not None


class TestSetPathMessageDefinition:

    def test_set_path_id(self):
        resource = MessageDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = MessageDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'MessageDefinition.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = MessageDefinition()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = MessageDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = MessageDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = MessageDefinition()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = MessageDefinition()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = MessageDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = MessageDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = MessageDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_identifier(self):
        resource = MessageDefinition()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_version(self):
        resource = MessageDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = MessageDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = MessageDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_replaces(self):
        resource = MessageDefinition()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'replaces', value)
        assert result is True
        assert resource.replaces is not None

    def test_set_path_status(self):
        resource = MessageDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = MessageDefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = MessageDefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = MessageDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = MessageDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = MessageDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = MessageDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = MessageDefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_purpose(self):
        resource = MessageDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_copyright(self):
        resource = MessageDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_base(self):
        resource = MessageDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'base', value)
        assert result is True
        assert resource.base is not None

    def test_set_path_parent(self):
        resource = MessageDefinition()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'parent', value)
        assert result is True
        assert resource.parent is not None

    def test_set_path_category(self):
        resource = MessageDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_focus(self):
        resource = MessageDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'focus', value)
        assert result is True
        assert resource.focus is not None

    def test_set_path_response_required(self):
        resource = MessageDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'responseRequired', value)
        assert result is True
        assert resource.responseRequired is not None

    def test_set_path_allowed_response(self):
        resource = MessageDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'allowedResponse', value)
        assert result is True
        assert resource.allowedResponse is not None

    def test_set_path_graph(self):
        resource = MessageDefinition()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'graph', value)
        assert result is True
        assert resource.graph is not None


class TestParsePathMessageDefinition:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('MessageDefinition.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('MessageDefinition.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('MessageDefinition.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
