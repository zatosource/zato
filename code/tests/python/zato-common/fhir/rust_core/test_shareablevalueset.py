# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import shareablevalueset


class TestToDictshareablevalueset:

    def test_to_dict_empty(self):
        resource = shareablevalueset()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'shareablevalueset'

    def test_to_dict_with_id(self):
        resource = shareablevalueset()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = shareablevalueset()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, shareablevalueset)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = shareablevalueset()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = shareablevalueset()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = shareablevalueset()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = shareablevalueset()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = shareablevalueset()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = shareablevalueset()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = shareablevalueset()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = shareablevalueset()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = shareablevalueset()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_identifier(self):
        resource = shareablevalueset()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_version(self):
        resource = shareablevalueset()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = shareablevalueset()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = shareablevalueset()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_status(self):
        resource = shareablevalueset()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = shareablevalueset()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = shareablevalueset()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = shareablevalueset()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = shareablevalueset()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = shareablevalueset()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = shareablevalueset()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = shareablevalueset()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_immutable(self):
        resource = shareablevalueset()
        resource.immutable = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'immutable' in result

    def test_to_dict_purpose(self):
        resource = shareablevalueset()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_copyright(self):
        resource = shareablevalueset()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_compose(self):
        resource = shareablevalueset()
        resource.compose = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'compose' in result

    def test_to_dict_expansion(self):
        resource = shareablevalueset()
        resource.expansion = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'expansion' in result


class TestFromDictshareablevalueset:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'shareablevalueset', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert isinstance(result, shareablevalueset)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'shareablevalueset'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert isinstance(result, shareablevalueset)

    def test_from_dict_id(self):
        data = {'resourceType': 'shareablevalueset', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'shareablevalueset', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'shareablevalueset', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'shareablevalueset', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'shareablevalueset', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'shareablevalueset', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'shareablevalueset', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'shareablevalueset', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'shareablevalueset', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.url is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'shareablevalueset', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.identifier is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'shareablevalueset', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'shareablevalueset', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'shareablevalueset', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.title is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'shareablevalueset', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'shareablevalueset', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'shareablevalueset', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'shareablevalueset', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'shareablevalueset', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'shareablevalueset', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'shareablevalueset', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'shareablevalueset'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.jurisdiction is not None

    def test_from_dict_immutable(self):
        data = {'resourceType': 'shareablevalueset', 'immutable': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.immutable is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'shareablevalueset', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.purpose is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'shareablevalueset', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.copyright is not None

    def test_from_dict_compose(self):
        data = {'resourceType': 'shareablevalueset', 'compose': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.compose is not None

    def test_from_dict_expansion(self):
        data = {'resourceType': 'shareablevalueset', 'expansion': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablevalueset)
        assert result.expansion is not None


class TestGetPathshareablevalueset:

    def test_get_path_id(self):
        resource = shareablevalueset()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = shareablevalueset()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = shareablevalueset()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'shareablevalueset.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = shareablevalueset()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = shareablevalueset()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = shareablevalueset()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = shareablevalueset()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = shareablevalueset()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = shareablevalueset()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = shareablevalueset()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = shareablevalueset()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_identifier(self):
        resource = shareablevalueset()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_version(self):
        resource = shareablevalueset()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = shareablevalueset()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = shareablevalueset()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_status(self):
        resource = shareablevalueset()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = shareablevalueset()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = shareablevalueset()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = shareablevalueset()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = shareablevalueset()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = shareablevalueset()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = shareablevalueset()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = shareablevalueset()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_immutable(self):
        resource = shareablevalueset()
        resource.immutable = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'immutable')
        assert result is not None

    def test_get_path_purpose(self):
        resource = shareablevalueset()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_copyright(self):
        resource = shareablevalueset()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_compose(self):
        resource = shareablevalueset()
        resource.compose = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'compose')
        assert result is not None

    def test_get_path_expansion(self):
        resource = shareablevalueset()
        resource.expansion = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'expansion')
        assert result is not None


class TestSetPathshareablevalueset:

    def test_set_path_id(self):
        resource = shareablevalueset()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = shareablevalueset()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'shareablevalueset.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = shareablevalueset()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = shareablevalueset()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = shareablevalueset()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = shareablevalueset()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = shareablevalueset()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = shareablevalueset()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = shareablevalueset()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = shareablevalueset()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_identifier(self):
        resource = shareablevalueset()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_version(self):
        resource = shareablevalueset()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = shareablevalueset()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = shareablevalueset()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_status(self):
        resource = shareablevalueset()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = shareablevalueset()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = shareablevalueset()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = shareablevalueset()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = shareablevalueset()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = shareablevalueset()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = shareablevalueset()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = shareablevalueset()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_immutable(self):
        resource = shareablevalueset()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'immutable', value)
        assert result is True
        assert resource.immutable is not None

    def test_set_path_purpose(self):
        resource = shareablevalueset()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_copyright(self):
        resource = shareablevalueset()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_compose(self):
        resource = shareablevalueset()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'compose', value)
        assert result is True
        assert resource.compose is not None

    def test_set_path_expansion(self):
        resource = shareablevalueset()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'expansion', value)
        assert result is True
        assert resource.expansion is not None


class TestParsePathshareablevalueset:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('shareablevalueset.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('shareablevalueset.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('shareablevalueset.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
