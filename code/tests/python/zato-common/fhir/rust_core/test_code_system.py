# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import CodeSystem


class TestToDictCodeSystem:

    def test_to_dict_empty(self):
        resource = CodeSystem()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'CodeSystem'

    def test_to_dict_with_id(self):
        resource = CodeSystem()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = CodeSystem()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, CodeSystem)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = CodeSystem()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = CodeSystem()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = CodeSystem()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = CodeSystem()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = CodeSystem()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = CodeSystem()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = CodeSystem()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = CodeSystem()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = CodeSystem()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_identifier(self):
        resource = CodeSystem()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_version(self):
        resource = CodeSystem()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = CodeSystem()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = CodeSystem()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_status(self):
        resource = CodeSystem()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = CodeSystem()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = CodeSystem()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = CodeSystem()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = CodeSystem()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = CodeSystem()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = CodeSystem()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = CodeSystem()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_purpose(self):
        resource = CodeSystem()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_copyright(self):
        resource = CodeSystem()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_case_sensitive(self):
        resource = CodeSystem()
        resource.caseSensitive = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'caseSensitive' in result

    def test_to_dict_value_set(self):
        resource = CodeSystem()
        resource.valueSet = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'valueSet' in result

    def test_to_dict_hierarchy_meaning(self):
        resource = CodeSystem()
        resource.hierarchyMeaning = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'hierarchyMeaning' in result

    def test_to_dict_compositional(self):
        resource = CodeSystem()
        resource.compositional = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'compositional' in result

    def test_to_dict_version_needed(self):
        resource = CodeSystem()
        resource.versionNeeded = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'versionNeeded' in result

    def test_to_dict_content(self):
        resource = CodeSystem()
        resource.content = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'content' in result

    def test_to_dict_supplements(self):
        resource = CodeSystem()
        resource.supplements = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supplements' in result

    def test_to_dict_count(self):
        resource = CodeSystem()
        resource.count = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'count' in result

    def test_to_dict_filter(self):
        resource = CodeSystem()
        resource.filter = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'filter' in result

    def test_to_dict_property(self):
        resource = CodeSystem()
        resource.property = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'property' in result

    def test_to_dict_concept(self):
        resource = CodeSystem()
        resource.concept = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'concept' in result


class TestFromDictCodeSystem:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'CodeSystem', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert isinstance(result, CodeSystem)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'CodeSystem'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert isinstance(result, CodeSystem)

    def test_from_dict_id(self):
        data = {'resourceType': 'CodeSystem', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'CodeSystem', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'CodeSystem', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'CodeSystem', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'CodeSystem', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'CodeSystem', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'CodeSystem', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'CodeSystem', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'CodeSystem', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.url is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'CodeSystem', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.identifier is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'CodeSystem', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'CodeSystem', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'CodeSystem', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.title is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'CodeSystem', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'CodeSystem', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'CodeSystem', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'CodeSystem', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'CodeSystem', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'CodeSystem', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'CodeSystem', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'CodeSystem'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.jurisdiction is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'CodeSystem', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.purpose is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'CodeSystem', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.copyright is not None

    def test_from_dict_case_sensitive(self):
        data = {'resourceType': 'CodeSystem', 'caseSensitive': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.caseSensitive is not None

    def test_from_dict_value_set(self):
        data = {'resourceType': 'CodeSystem', 'valueSet': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.valueSet is not None

    def test_from_dict_hierarchy_meaning(self):
        data = {'resourceType': 'CodeSystem', 'hierarchyMeaning': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.hierarchyMeaning is not None

    def test_from_dict_compositional(self):
        data = {'resourceType': 'CodeSystem', 'compositional': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.compositional is not None

    def test_from_dict_version_needed(self):
        data = {'resourceType': 'CodeSystem', 'versionNeeded': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.versionNeeded is not None

    def test_from_dict_content(self):
        data = {'resourceType': 'CodeSystem', 'content': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.content is not None

    def test_from_dict_supplements(self):
        data = {'resourceType': 'CodeSystem', 'supplements': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.supplements is not None

    def test_from_dict_count(self):
        data = {'resourceType': 'CodeSystem', 'count': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.count is not None

    def test_from_dict_filter(self):
        data = {'resourceType': 'CodeSystem', 'filter': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.filter is not None

    def test_from_dict_property(self):
        data = {'resourceType': 'CodeSystem', 'property': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.property is not None

    def test_from_dict_concept(self):
        data = {'resourceType': 'CodeSystem', 'concept': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CodeSystem)
        assert result.concept is not None


class TestGetPathCodeSystem:

    def test_get_path_id(self):
        resource = CodeSystem()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = CodeSystem()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = CodeSystem()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'CodeSystem.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = CodeSystem()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = CodeSystem()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = CodeSystem()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = CodeSystem()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = CodeSystem()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = CodeSystem()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = CodeSystem()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = CodeSystem()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_identifier(self):
        resource = CodeSystem()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_version(self):
        resource = CodeSystem()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = CodeSystem()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = CodeSystem()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_status(self):
        resource = CodeSystem()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = CodeSystem()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = CodeSystem()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = CodeSystem()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = CodeSystem()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = CodeSystem()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = CodeSystem()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = CodeSystem()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_purpose(self):
        resource = CodeSystem()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_copyright(self):
        resource = CodeSystem()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_case_sensitive(self):
        resource = CodeSystem()
        resource.caseSensitive = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'caseSensitive')
        assert result is not None

    def test_get_path_value_set(self):
        resource = CodeSystem()
        resource.valueSet = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'valueSet')
        assert result is not None

    def test_get_path_hierarchy_meaning(self):
        resource = CodeSystem()
        resource.hierarchyMeaning = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'hierarchyMeaning')
        assert result is not None

    def test_get_path_compositional(self):
        resource = CodeSystem()
        resource.compositional = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'compositional')
        assert result is not None

    def test_get_path_version_needed(self):
        resource = CodeSystem()
        resource.versionNeeded = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'versionNeeded')
        assert result is not None

    def test_get_path_content(self):
        resource = CodeSystem()
        resource.content = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'content')
        assert result is not None

    def test_get_path_supplements(self):
        resource = CodeSystem()
        resource.supplements = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supplements')
        assert result is not None

    def test_get_path_count(self):
        resource = CodeSystem()
        resource.count = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'count')
        assert result is not None

    def test_get_path_filter(self):
        resource = CodeSystem()
        resource.filter = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'filter')
        assert result is not None

    def test_get_path_property(self):
        resource = CodeSystem()
        resource.property = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'property')
        assert result is not None

    def test_get_path_concept(self):
        resource = CodeSystem()
        resource.concept = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'concept')
        assert result is not None


class TestSetPathCodeSystem:

    def test_set_path_id(self):
        resource = CodeSystem()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = CodeSystem()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'CodeSystem.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = CodeSystem()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = CodeSystem()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = CodeSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = CodeSystem()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = CodeSystem()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = CodeSystem()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = CodeSystem()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = CodeSystem()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_identifier(self):
        resource = CodeSystem()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_version(self):
        resource = CodeSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = CodeSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = CodeSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_status(self):
        resource = CodeSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = CodeSystem()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = CodeSystem()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = CodeSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = CodeSystem()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = CodeSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = CodeSystem()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = CodeSystem()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_purpose(self):
        resource = CodeSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_copyright(self):
        resource = CodeSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_case_sensitive(self):
        resource = CodeSystem()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'caseSensitive', value)
        assert result is True
        assert resource.caseSensitive is not None

    def test_set_path_value_set(self):
        resource = CodeSystem()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'valueSet', value)
        assert result is True
        assert resource.valueSet is not None

    def test_set_path_hierarchy_meaning(self):
        resource = CodeSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'hierarchyMeaning', value)
        assert result is True
        assert resource.hierarchyMeaning is not None

    def test_set_path_compositional(self):
        resource = CodeSystem()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'compositional', value)
        assert result is True
        assert resource.compositional is not None

    def test_set_path_version_needed(self):
        resource = CodeSystem()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'versionNeeded', value)
        assert result is True
        assert resource.versionNeeded is not None

    def test_set_path_content(self):
        resource = CodeSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'content', value)
        assert result is True
        assert resource.content is not None

    def test_set_path_supplements(self):
        resource = CodeSystem()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supplements', value)
        assert result is True
        assert resource.supplements is not None

    def test_set_path_count(self):
        resource = CodeSystem()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'count', value)
        assert result is True
        assert resource.count is not None

    def test_set_path_filter(self):
        resource = CodeSystem()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'filter', value)
        assert result is True
        assert resource.filter is not None

    def test_set_path_property(self):
        resource = CodeSystem()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'property', value)
        assert result is True
        assert resource.property is not None

    def test_set_path_concept(self):
        resource = CodeSystem()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'concept', value)
        assert result is True
        assert resource.concept is not None


class TestParsePathCodeSystem:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('CodeSystem.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('CodeSystem.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('CodeSystem.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
