# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import StructureDefinition


class TestToDictStructureDefinition:

    def test_to_dict_empty(self):
        resource = StructureDefinition()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'StructureDefinition'

    def test_to_dict_with_id(self):
        resource = StructureDefinition()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = StructureDefinition()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, StructureDefinition)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = StructureDefinition()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = StructureDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = StructureDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = StructureDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = StructureDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = StructureDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = StructureDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = StructureDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = StructureDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_identifier(self):
        resource = StructureDefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_version(self):
        resource = StructureDefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = StructureDefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = StructureDefinition()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_status(self):
        resource = StructureDefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = StructureDefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = StructureDefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = StructureDefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = StructureDefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = StructureDefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = StructureDefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = StructureDefinition()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_purpose(self):
        resource = StructureDefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_copyright(self):
        resource = StructureDefinition()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_keyword(self):
        resource = StructureDefinition()
        resource.keyword = [{'system': 'http://example.org', 'code': 'test-code'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'keyword' in result

    def test_to_dict_fhir_version(self):
        resource = StructureDefinition()
        resource.fhirVersion = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'fhirVersion' in result

    def test_to_dict_mapping(self):
        resource = StructureDefinition()
        resource.mapping = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'mapping' in result

    def test_to_dict_kind(self):
        resource = StructureDefinition()
        resource.kind = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'kind' in result

    def test_to_dict_abstract(self):
        resource = StructureDefinition()
        resource.abstract = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'abstract' in result

    def test_to_dict_context(self):
        resource = StructureDefinition()
        resource.context = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'context' in result

    def test_to_dict_context_invariant(self):
        resource = StructureDefinition()
        resource.contextInvariant = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contextInvariant' in result

    def test_to_dict_type(self):
        resource = StructureDefinition()
        resource.type_ = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_base_definition(self):
        resource = StructureDefinition()
        resource.baseDefinition = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'baseDefinition' in result

    def test_to_dict_derivation(self):
        resource = StructureDefinition()
        resource.derivation = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'derivation' in result

    def test_to_dict_snapshot(self):
        resource = StructureDefinition()
        resource.snapshot = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'snapshot' in result

    def test_to_dict_differential(self):
        resource = StructureDefinition()
        resource.differential = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'differential' in result


class TestFromDictStructureDefinition:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'StructureDefinition', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert isinstance(result, StructureDefinition)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'StructureDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert isinstance(result, StructureDefinition)

    def test_from_dict_id(self):
        data = {'resourceType': 'StructureDefinition', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'StructureDefinition', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'StructureDefinition', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'StructureDefinition', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'StructureDefinition', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'StructureDefinition', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'StructureDefinition', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'StructureDefinition', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'StructureDefinition', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.url is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'StructureDefinition', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.identifier is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'StructureDefinition', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'StructureDefinition', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'StructureDefinition', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.title is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'StructureDefinition', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'StructureDefinition', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'StructureDefinition', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'StructureDefinition', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'StructureDefinition', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'StructureDefinition', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'StructureDefinition', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'StructureDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.jurisdiction is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'StructureDefinition', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.purpose is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'StructureDefinition', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.copyright is not None

    def test_from_dict_keyword(self):
        data = {'resourceType': 'StructureDefinition', 'keyword': [{'system': 'http://example.org', 'code': 'test-code'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.keyword is not None

    def test_from_dict_fhir_version(self):
        data = {'resourceType': 'StructureDefinition', 'fhirVersion': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.fhirVersion is not None

    def test_from_dict_mapping(self):
        data = {'resourceType': 'StructureDefinition', 'mapping': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.mapping is not None

    def test_from_dict_kind(self):
        data = {'resourceType': 'StructureDefinition', 'kind': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.kind is not None

    def test_from_dict_abstract(self):
        data = {'resourceType': 'StructureDefinition', 'abstract': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.abstract is not None

    def test_from_dict_context(self):
        data = {'resourceType': 'StructureDefinition', 'context': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.context is not None

    def test_from_dict_context_invariant(self):
        data = {'resourceType': 'StructureDefinition', 'contextInvariant': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.contextInvariant is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'StructureDefinition', 'type': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.type_ is not None

    def test_from_dict_base_definition(self):
        data = {'resourceType': 'StructureDefinition', 'baseDefinition': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.baseDefinition is not None

    def test_from_dict_derivation(self):
        data = {'resourceType': 'StructureDefinition', 'derivation': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.derivation is not None

    def test_from_dict_snapshot(self):
        data = {'resourceType': 'StructureDefinition', 'snapshot': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.snapshot is not None

    def test_from_dict_differential(self):
        data = {'resourceType': 'StructureDefinition', 'differential': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, StructureDefinition)
        assert result.differential is not None


class TestGetPathStructureDefinition:

    def test_get_path_id(self):
        resource = StructureDefinition()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = StructureDefinition()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = StructureDefinition()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'StructureDefinition.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = StructureDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = StructureDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = StructureDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = StructureDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = StructureDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = StructureDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = StructureDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = StructureDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_identifier(self):
        resource = StructureDefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_version(self):
        resource = StructureDefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = StructureDefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = StructureDefinition()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_status(self):
        resource = StructureDefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = StructureDefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = StructureDefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = StructureDefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = StructureDefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = StructureDefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = StructureDefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = StructureDefinition()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_purpose(self):
        resource = StructureDefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_copyright(self):
        resource = StructureDefinition()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_keyword(self):
        resource = StructureDefinition()
        resource.keyword = [{'system': 'http://example.org', 'code': 'test-code'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'keyword')
        assert result is not None

    def test_get_path_fhir_version(self):
        resource = StructureDefinition()
        resource.fhirVersion = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'fhirVersion')
        assert result is not None

    def test_get_path_mapping(self):
        resource = StructureDefinition()
        resource.mapping = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'mapping')
        assert result is not None

    def test_get_path_kind(self):
        resource = StructureDefinition()
        resource.kind = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'kind')
        assert result is not None

    def test_get_path_abstract(self):
        resource = StructureDefinition()
        resource.abstract = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'abstract')
        assert result is not None

    def test_get_path_context(self):
        resource = StructureDefinition()
        resource.context = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'context')
        assert result is not None

    def test_get_path_context_invariant(self):
        resource = StructureDefinition()
        resource.contextInvariant = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contextInvariant')
        assert result is not None

    def test_get_path_type(self):
        resource = StructureDefinition()
        resource.type_ = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_base_definition(self):
        resource = StructureDefinition()
        resource.baseDefinition = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'baseDefinition')
        assert result is not None

    def test_get_path_derivation(self):
        resource = StructureDefinition()
        resource.derivation = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'derivation')
        assert result is not None

    def test_get_path_snapshot(self):
        resource = StructureDefinition()
        resource.snapshot = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'snapshot')
        assert result is not None

    def test_get_path_differential(self):
        resource = StructureDefinition()
        resource.differential = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'differential')
        assert result is not None


class TestSetPathStructureDefinition:

    def test_set_path_id(self):
        resource = StructureDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = StructureDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'StructureDefinition.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = StructureDefinition()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = StructureDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = StructureDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = StructureDefinition()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = StructureDefinition()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = StructureDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = StructureDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = StructureDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_identifier(self):
        resource = StructureDefinition()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_version(self):
        resource = StructureDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = StructureDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = StructureDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_status(self):
        resource = StructureDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = StructureDefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = StructureDefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = StructureDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = StructureDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = StructureDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = StructureDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = StructureDefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_purpose(self):
        resource = StructureDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_copyright(self):
        resource = StructureDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_keyword(self):
        resource = StructureDefinition()
        value = [{'system': 'http://example.org', 'code': 'test-code'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'keyword', value)
        assert result is True
        assert resource.keyword is not None

    def test_set_path_fhir_version(self):
        resource = StructureDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'fhirVersion', value)
        assert result is True
        assert resource.fhirVersion is not None

    def test_set_path_mapping(self):
        resource = StructureDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'mapping', value)
        assert result is True
        assert resource.mapping is not None

    def test_set_path_kind(self):
        resource = StructureDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'kind', value)
        assert result is True
        assert resource.kind is not None

    def test_set_path_abstract(self):
        resource = StructureDefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'abstract', value)
        assert result is True
        assert resource.abstract is not None

    def test_set_path_context(self):
        resource = StructureDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'context', value)
        assert result is True
        assert resource.context is not None

    def test_set_path_context_invariant(self):
        resource = StructureDefinition()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contextInvariant', value)
        assert result is True
        assert resource.contextInvariant is not None

    def test_set_path_type(self):
        resource = StructureDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_base_definition(self):
        resource = StructureDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'baseDefinition', value)
        assert result is True
        assert resource.baseDefinition is not None

    def test_set_path_derivation(self):
        resource = StructureDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'derivation', value)
        assert result is True
        assert resource.derivation is not None

    def test_set_path_snapshot(self):
        resource = StructureDefinition()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'snapshot', value)
        assert result is True
        assert resource.snapshot is not None

    def test_set_path_differential(self):
        resource = StructureDefinition()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'differential', value)
        assert result is True
        assert resource.differential is not None


class TestParsePathStructureDefinition:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('StructureDefinition.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('StructureDefinition.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('StructureDefinition.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
