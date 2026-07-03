# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import shareablecodesystem


class TestToDictshareablecodesystem:

    def test_to_dict_empty(self):
        resource = shareablecodesystem()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'shareablecodesystem'

    def test_to_dict_with_id(self):
        resource = shareablecodesystem()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = shareablecodesystem()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, shareablecodesystem)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = shareablecodesystem()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = shareablecodesystem()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = shareablecodesystem()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = shareablecodesystem()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = shareablecodesystem()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = shareablecodesystem()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = shareablecodesystem()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = shareablecodesystem()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = shareablecodesystem()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_identifier(self):
        resource = shareablecodesystem()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_version(self):
        resource = shareablecodesystem()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = shareablecodesystem()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = shareablecodesystem()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_status(self):
        resource = shareablecodesystem()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = shareablecodesystem()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = shareablecodesystem()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = shareablecodesystem()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = shareablecodesystem()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = shareablecodesystem()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = shareablecodesystem()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = shareablecodesystem()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_purpose(self):
        resource = shareablecodesystem()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_copyright(self):
        resource = shareablecodesystem()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_case_sensitive(self):
        resource = shareablecodesystem()
        resource.caseSensitive = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'caseSensitive' in result

    def test_to_dict_value_set(self):
        resource = shareablecodesystem()
        resource.valueSet = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'valueSet' in result

    def test_to_dict_hierarchy_meaning(self):
        resource = shareablecodesystem()
        resource.hierarchyMeaning = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'hierarchyMeaning' in result

    def test_to_dict_compositional(self):
        resource = shareablecodesystem()
        resource.compositional = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'compositional' in result

    def test_to_dict_version_needed(self):
        resource = shareablecodesystem()
        resource.versionNeeded = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'versionNeeded' in result

    def test_to_dict_content(self):
        resource = shareablecodesystem()
        resource.content = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'content' in result

    def test_to_dict_supplements(self):
        resource = shareablecodesystem()
        resource.supplements = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supplements' in result

    def test_to_dict_count(self):
        resource = shareablecodesystem()
        resource.count = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'count' in result

    def test_to_dict_filter(self):
        resource = shareablecodesystem()
        resource.filter = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'filter' in result

    def test_to_dict_property(self):
        resource = shareablecodesystem()
        resource.property = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'property' in result

    def test_to_dict_concept(self):
        resource = shareablecodesystem()
        resource.concept = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'concept' in result


class TestFromDictshareablecodesystem:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'shareablecodesystem', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert isinstance(result, shareablecodesystem)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'shareablecodesystem'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert isinstance(result, shareablecodesystem)

    def test_from_dict_id(self):
        data = {'resourceType': 'shareablecodesystem', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'shareablecodesystem', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'shareablecodesystem', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'shareablecodesystem', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'shareablecodesystem', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'shareablecodesystem', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'shareablecodesystem', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'shareablecodesystem', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'shareablecodesystem', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.url is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'shareablecodesystem', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.identifier is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'shareablecodesystem', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'shareablecodesystem', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'shareablecodesystem', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.title is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'shareablecodesystem', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'shareablecodesystem', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'shareablecodesystem', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'shareablecodesystem', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'shareablecodesystem', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'shareablecodesystem', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'shareablecodesystem', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'shareablecodesystem'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.jurisdiction is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'shareablecodesystem', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.purpose is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'shareablecodesystem', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.copyright is not None

    def test_from_dict_case_sensitive(self):
        data = {'resourceType': 'shareablecodesystem', 'caseSensitive': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.caseSensitive is not None

    def test_from_dict_value_set(self):
        data = {'resourceType': 'shareablecodesystem', 'valueSet': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.valueSet is not None

    def test_from_dict_hierarchy_meaning(self):
        data = {'resourceType': 'shareablecodesystem', 'hierarchyMeaning': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.hierarchyMeaning is not None

    def test_from_dict_compositional(self):
        data = {'resourceType': 'shareablecodesystem', 'compositional': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.compositional is not None

    def test_from_dict_version_needed(self):
        data = {'resourceType': 'shareablecodesystem', 'versionNeeded': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.versionNeeded is not None

    def test_from_dict_content(self):
        data = {'resourceType': 'shareablecodesystem', 'content': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.content is not None

    def test_from_dict_supplements(self):
        data = {'resourceType': 'shareablecodesystem', 'supplements': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.supplements is not None

    def test_from_dict_count(self):
        data = {'resourceType': 'shareablecodesystem', 'count': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.count is not None

    def test_from_dict_filter(self):
        data = {'resourceType': 'shareablecodesystem', 'filter': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.filter is not None

    def test_from_dict_property(self):
        data = {'resourceType': 'shareablecodesystem', 'property': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.property is not None

    def test_from_dict_concept(self):
        data = {'resourceType': 'shareablecodesystem', 'concept': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareablecodesystem)
        assert result.concept is not None


class TestGetPathshareablecodesystem:

    def test_get_path_id(self):
        resource = shareablecodesystem()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = shareablecodesystem()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = shareablecodesystem()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'shareablecodesystem.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = shareablecodesystem()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = shareablecodesystem()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = shareablecodesystem()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = shareablecodesystem()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = shareablecodesystem()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = shareablecodesystem()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = shareablecodesystem()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = shareablecodesystem()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_identifier(self):
        resource = shareablecodesystem()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_version(self):
        resource = shareablecodesystem()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = shareablecodesystem()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = shareablecodesystem()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_status(self):
        resource = shareablecodesystem()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = shareablecodesystem()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = shareablecodesystem()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = shareablecodesystem()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = shareablecodesystem()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = shareablecodesystem()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = shareablecodesystem()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = shareablecodesystem()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_purpose(self):
        resource = shareablecodesystem()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_copyright(self):
        resource = shareablecodesystem()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_case_sensitive(self):
        resource = shareablecodesystem()
        resource.caseSensitive = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'caseSensitive')
        assert result is not None

    def test_get_path_value_set(self):
        resource = shareablecodesystem()
        resource.valueSet = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'valueSet')
        assert result is not None

    def test_get_path_hierarchy_meaning(self):
        resource = shareablecodesystem()
        resource.hierarchyMeaning = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'hierarchyMeaning')
        assert result is not None

    def test_get_path_compositional(self):
        resource = shareablecodesystem()
        resource.compositional = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'compositional')
        assert result is not None

    def test_get_path_version_needed(self):
        resource = shareablecodesystem()
        resource.versionNeeded = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'versionNeeded')
        assert result is not None

    def test_get_path_content(self):
        resource = shareablecodesystem()
        resource.content = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'content')
        assert result is not None

    def test_get_path_supplements(self):
        resource = shareablecodesystem()
        resource.supplements = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supplements')
        assert result is not None

    def test_get_path_count(self):
        resource = shareablecodesystem()
        resource.count = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'count')
        assert result is not None

    def test_get_path_filter(self):
        resource = shareablecodesystem()
        resource.filter = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'filter')
        assert result is not None

    def test_get_path_property(self):
        resource = shareablecodesystem()
        resource.property = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'property')
        assert result is not None

    def test_get_path_concept(self):
        resource = shareablecodesystem()
        resource.concept = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'concept')
        assert result is not None


class TestSetPathshareablecodesystem:

    def test_set_path_id(self):
        resource = shareablecodesystem()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = shareablecodesystem()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'shareablecodesystem.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = shareablecodesystem()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = shareablecodesystem()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = shareablecodesystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = shareablecodesystem()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = shareablecodesystem()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = shareablecodesystem()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = shareablecodesystem()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = shareablecodesystem()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_identifier(self):
        resource = shareablecodesystem()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_version(self):
        resource = shareablecodesystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = shareablecodesystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = shareablecodesystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_status(self):
        resource = shareablecodesystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = shareablecodesystem()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = shareablecodesystem()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = shareablecodesystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = shareablecodesystem()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = shareablecodesystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = shareablecodesystem()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = shareablecodesystem()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_purpose(self):
        resource = shareablecodesystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_copyright(self):
        resource = shareablecodesystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_case_sensitive(self):
        resource = shareablecodesystem()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'caseSensitive', value)
        assert result is True
        assert resource.caseSensitive is not None

    def test_set_path_value_set(self):
        resource = shareablecodesystem()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'valueSet', value)
        assert result is True
        assert resource.valueSet is not None

    def test_set_path_hierarchy_meaning(self):
        resource = shareablecodesystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'hierarchyMeaning', value)
        assert result is True
        assert resource.hierarchyMeaning is not None

    def test_set_path_compositional(self):
        resource = shareablecodesystem()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'compositional', value)
        assert result is True
        assert resource.compositional is not None

    def test_set_path_version_needed(self):
        resource = shareablecodesystem()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'versionNeeded', value)
        assert result is True
        assert resource.versionNeeded is not None

    def test_set_path_content(self):
        resource = shareablecodesystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'content', value)
        assert result is True
        assert resource.content is not None

    def test_set_path_supplements(self):
        resource = shareablecodesystem()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supplements', value)
        assert result is True
        assert resource.supplements is not None

    def test_set_path_count(self):
        resource = shareablecodesystem()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'count', value)
        assert result is True
        assert resource.count is not None

    def test_set_path_filter(self):
        resource = shareablecodesystem()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'filter', value)
        assert result is True
        assert resource.filter is not None

    def test_set_path_property(self):
        resource = shareablecodesystem()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'property', value)
        assert result is True
        assert resource.property is not None

    def test_set_path_concept(self):
        resource = shareablecodesystem()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'concept', value)
        assert result is True
        assert resource.concept is not None


class TestParsePathshareablecodesystem:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('shareablecodesystem.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('shareablecodesystem.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('shareablecodesystem.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
