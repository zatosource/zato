# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import OperationDefinition


class TestToDictOperationDefinition:

    def test_to_dict_empty(self):
        resource = OperationDefinition()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'OperationDefinition'

    def test_to_dict_with_id(self):
        resource = OperationDefinition()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = OperationDefinition()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, OperationDefinition)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = OperationDefinition()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = OperationDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = OperationDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = OperationDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = OperationDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = OperationDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = OperationDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = OperationDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = OperationDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_version(self):
        resource = OperationDefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = OperationDefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = OperationDefinition()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_status(self):
        resource = OperationDefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_kind(self):
        resource = OperationDefinition()
        resource.kind = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'kind' in result

    def test_to_dict_experimental(self):
        resource = OperationDefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = OperationDefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = OperationDefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = OperationDefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = OperationDefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = OperationDefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = OperationDefinition()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_purpose(self):
        resource = OperationDefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_affects_state(self):
        resource = OperationDefinition()
        resource.affectsState = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'affectsState' in result

    def test_to_dict_code(self):
        resource = OperationDefinition()
        resource.code = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_comment(self):
        resource = OperationDefinition()
        resource.comment = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'comment' in result

    def test_to_dict_base(self):
        resource = OperationDefinition()
        resource.base = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'base' in result

    def test_to_dict_resource(self):
        resource = OperationDefinition()
        resource.resource = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'resource' in result

    def test_to_dict_system(self):
        resource = OperationDefinition()
        resource.system = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'system' in result

    def test_to_dict_type(self):
        resource = OperationDefinition()
        resource.type_ = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_instance(self):
        resource = OperationDefinition()
        resource.instance = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instance' in result

    def test_to_dict_input_profile(self):
        resource = OperationDefinition()
        resource.inputProfile = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'inputProfile' in result

    def test_to_dict_output_profile(self):
        resource = OperationDefinition()
        resource.outputProfile = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'outputProfile' in result

    def test_to_dict_parameter(self):
        resource = OperationDefinition()
        resource.parameter = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'parameter' in result

    def test_to_dict_overload(self):
        resource = OperationDefinition()
        resource.overload = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'overload' in result


class TestFromDictOperationDefinition:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'OperationDefinition', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert isinstance(result, OperationDefinition)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'OperationDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert isinstance(result, OperationDefinition)

    def test_from_dict_id(self):
        data = {'resourceType': 'OperationDefinition', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'OperationDefinition', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'OperationDefinition', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'OperationDefinition', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'OperationDefinition', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'OperationDefinition', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'OperationDefinition', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'OperationDefinition', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'OperationDefinition', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.url is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'OperationDefinition', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'OperationDefinition', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'OperationDefinition', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.title is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'OperationDefinition', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.status is not None

    def test_from_dict_kind(self):
        data = {'resourceType': 'OperationDefinition', 'kind': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.kind is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'OperationDefinition', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'OperationDefinition', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'OperationDefinition', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'OperationDefinition', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'OperationDefinition', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'OperationDefinition', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'OperationDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.jurisdiction is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'OperationDefinition', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.purpose is not None

    def test_from_dict_affects_state(self):
        data = {'resourceType': 'OperationDefinition', 'affectsState': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.affectsState is not None

    def test_from_dict_code(self):
        data = {'resourceType': 'OperationDefinition', 'code': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.code is not None

    def test_from_dict_comment(self):
        data = {'resourceType': 'OperationDefinition', 'comment': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.comment is not None

    def test_from_dict_base(self):
        data = {'resourceType': 'OperationDefinition', 'base': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.base is not None

    def test_from_dict_resource(self):
        data = {'resourceType': 'OperationDefinition', 'resource': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.resource is not None

    def test_from_dict_system(self):
        data = {'resourceType': 'OperationDefinition', 'system': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.system is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'OperationDefinition', 'type': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.type_ is not None

    def test_from_dict_instance(self):
        data = {'resourceType': 'OperationDefinition', 'instance': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.instance is not None

    def test_from_dict_input_profile(self):
        data = {'resourceType': 'OperationDefinition', 'inputProfile': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.inputProfile is not None

    def test_from_dict_output_profile(self):
        data = {'resourceType': 'OperationDefinition', 'outputProfile': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.outputProfile is not None

    def test_from_dict_parameter(self):
        data = {'resourceType': 'OperationDefinition', 'parameter': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.parameter is not None

    def test_from_dict_overload(self):
        data = {'resourceType': 'OperationDefinition', 'overload': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, OperationDefinition)
        assert result.overload is not None


class TestGetPathOperationDefinition:

    def test_get_path_id(self):
        resource = OperationDefinition()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = OperationDefinition()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = OperationDefinition()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'OperationDefinition.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = OperationDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = OperationDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = OperationDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = OperationDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = OperationDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = OperationDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = OperationDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = OperationDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_version(self):
        resource = OperationDefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = OperationDefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = OperationDefinition()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_status(self):
        resource = OperationDefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_kind(self):
        resource = OperationDefinition()
        resource.kind = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'kind')
        assert result is not None

    def test_get_path_experimental(self):
        resource = OperationDefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = OperationDefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = OperationDefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = OperationDefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = OperationDefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = OperationDefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = OperationDefinition()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_purpose(self):
        resource = OperationDefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_affects_state(self):
        resource = OperationDefinition()
        resource.affectsState = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'affectsState')
        assert result is not None

    def test_get_path_code(self):
        resource = OperationDefinition()
        resource.code = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_comment(self):
        resource = OperationDefinition()
        resource.comment = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'comment')
        assert result is not None

    def test_get_path_base(self):
        resource = OperationDefinition()
        resource.base = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'base')
        assert result is not None

    def test_get_path_resource(self):
        resource = OperationDefinition()
        resource.resource = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'resource')
        assert result is not None

    def test_get_path_system(self):
        resource = OperationDefinition()
        resource.system = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'system')
        assert result is not None

    def test_get_path_type(self):
        resource = OperationDefinition()
        resource.type_ = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_instance(self):
        resource = OperationDefinition()
        resource.instance = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instance')
        assert result is not None

    def test_get_path_input_profile(self):
        resource = OperationDefinition()
        resource.inputProfile = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'inputProfile')
        assert result is not None

    def test_get_path_output_profile(self):
        resource = OperationDefinition()
        resource.outputProfile = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'outputProfile')
        assert result is not None

    def test_get_path_parameter(self):
        resource = OperationDefinition()
        resource.parameter = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'parameter')
        assert result is not None

    def test_get_path_overload(self):
        resource = OperationDefinition()
        resource.overload = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'overload')
        assert result is not None


class TestSetPathOperationDefinition:

    def test_set_path_id(self):
        resource = OperationDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = OperationDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'OperationDefinition.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = OperationDefinition()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = OperationDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = OperationDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = OperationDefinition()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = OperationDefinition()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = OperationDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = OperationDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = OperationDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_version(self):
        resource = OperationDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = OperationDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = OperationDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_status(self):
        resource = OperationDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_kind(self):
        resource = OperationDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'kind', value)
        assert result is True
        assert resource.kind is not None

    def test_set_path_experimental(self):
        resource = OperationDefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = OperationDefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = OperationDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = OperationDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = OperationDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = OperationDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = OperationDefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_purpose(self):
        resource = OperationDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_affects_state(self):
        resource = OperationDefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'affectsState', value)
        assert result is True
        assert resource.affectsState is not None

    def test_set_path_code(self):
        resource = OperationDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_comment(self):
        resource = OperationDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'comment', value)
        assert result is True
        assert resource.comment is not None

    def test_set_path_base(self):
        resource = OperationDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'base', value)
        assert result is True
        assert resource.base is not None

    def test_set_path_resource(self):
        resource = OperationDefinition()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'resource', value)
        assert result is True
        assert resource.resource is not None

    def test_set_path_system(self):
        resource = OperationDefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'system', value)
        assert result is True
        assert resource.system is not None

    def test_set_path_type(self):
        resource = OperationDefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_instance(self):
        resource = OperationDefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instance', value)
        assert result is True
        assert resource.instance is not None

    def test_set_path_input_profile(self):
        resource = OperationDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'inputProfile', value)
        assert result is True
        assert resource.inputProfile is not None

    def test_set_path_output_profile(self):
        resource = OperationDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'outputProfile', value)
        assert result is True
        assert resource.outputProfile is not None

    def test_set_path_parameter(self):
        resource = OperationDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'parameter', value)
        assert result is True
        assert resource.parameter is not None

    def test_set_path_overload(self):
        resource = OperationDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'overload', value)
        assert result is True
        assert resource.overload is not None


class TestParsePathOperationDefinition:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('OperationDefinition.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('OperationDefinition.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('OperationDefinition.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
