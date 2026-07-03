# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import CapabilityStatement


class TestToDictCapabilityStatement:

    def test_to_dict_empty(self):
        resource = CapabilityStatement()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'CapabilityStatement'

    def test_to_dict_with_id(self):
        resource = CapabilityStatement()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = CapabilityStatement()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, CapabilityStatement)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = CapabilityStatement()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = CapabilityStatement()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = CapabilityStatement()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = CapabilityStatement()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = CapabilityStatement()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = CapabilityStatement()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = CapabilityStatement()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = CapabilityStatement()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = CapabilityStatement()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_version(self):
        resource = CapabilityStatement()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = CapabilityStatement()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = CapabilityStatement()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_status(self):
        resource = CapabilityStatement()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = CapabilityStatement()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = CapabilityStatement()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = CapabilityStatement()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = CapabilityStatement()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = CapabilityStatement()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = CapabilityStatement()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = CapabilityStatement()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_purpose(self):
        resource = CapabilityStatement()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_copyright(self):
        resource = CapabilityStatement()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_kind(self):
        resource = CapabilityStatement()
        resource.kind = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'kind' in result

    def test_to_dict_instantiates(self):
        resource = CapabilityStatement()
        resource.instantiates = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiates' in result

    def test_to_dict_imports(self):
        resource = CapabilityStatement()
        resource.imports = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'imports' in result

    def test_to_dict_software(self):
        resource = CapabilityStatement()
        resource.software = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'software' in result

    def test_to_dict_implementation(self):
        resource = CapabilityStatement()
        resource.implementation = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implementation' in result

    def test_to_dict_fhir_version(self):
        resource = CapabilityStatement()
        resource.fhirVersion = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'fhirVersion' in result

    def test_to_dict_format(self):
        resource = CapabilityStatement()
        resource.format = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'format' in result

    def test_to_dict_patch_format(self):
        resource = CapabilityStatement()
        resource.patchFormat = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patchFormat' in result

    def test_to_dict_implementation_guide(self):
        resource = CapabilityStatement()
        resource.implementationGuide = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implementationGuide' in result

    def test_to_dict_rest(self):
        resource = CapabilityStatement()
        resource.rest = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'rest' in result

    def test_to_dict_messaging(self):
        resource = CapabilityStatement()
        resource.messaging = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'messaging' in result

    def test_to_dict_document(self):
        resource = CapabilityStatement()
        resource.document = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'document' in result


class TestFromDictCapabilityStatement:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'CapabilityStatement', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert isinstance(result, CapabilityStatement)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'CapabilityStatement'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert isinstance(result, CapabilityStatement)

    def test_from_dict_id(self):
        data = {'resourceType': 'CapabilityStatement', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'CapabilityStatement', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'CapabilityStatement', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'CapabilityStatement', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'CapabilityStatement', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'CapabilityStatement', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'CapabilityStatement', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'CapabilityStatement', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'CapabilityStatement', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.url is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'CapabilityStatement', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'CapabilityStatement', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'CapabilityStatement', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.title is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'CapabilityStatement', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'CapabilityStatement', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'CapabilityStatement', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'CapabilityStatement', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'CapabilityStatement', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'CapabilityStatement', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'CapabilityStatement', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'CapabilityStatement'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.jurisdiction is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'CapabilityStatement', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.purpose is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'CapabilityStatement', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.copyright is not None

    def test_from_dict_kind(self):
        data = {'resourceType': 'CapabilityStatement', 'kind': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.kind is not None

    def test_from_dict_instantiates(self):
        data = {'resourceType': 'CapabilityStatement', 'instantiates': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.instantiates is not None

    def test_from_dict_imports(self):
        data = {'resourceType': 'CapabilityStatement', 'imports': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.imports is not None

    def test_from_dict_software(self):
        data = {'resourceType': 'CapabilityStatement', 'software': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.software is not None

    def test_from_dict_implementation(self):
        data = {'resourceType': 'CapabilityStatement', 'implementation': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.implementation is not None

    def test_from_dict_fhir_version(self):
        data = {'resourceType': 'CapabilityStatement', 'fhirVersion': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.fhirVersion is not None

    def test_from_dict_format(self):
        data = {'resourceType': 'CapabilityStatement', 'format': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.format is not None

    def test_from_dict_patch_format(self):
        data = {'resourceType': 'CapabilityStatement', 'patchFormat': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.patchFormat is not None

    def test_from_dict_implementation_guide(self):
        data = {'resourceType': 'CapabilityStatement', 'implementationGuide': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.implementationGuide is not None

    def test_from_dict_rest(self):
        data = {'resourceType': 'CapabilityStatement', 'rest': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.rest is not None

    def test_from_dict_messaging(self):
        data = {'resourceType': 'CapabilityStatement', 'messaging': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.messaging is not None

    def test_from_dict_document(self):
        data = {'resourceType': 'CapabilityStatement', 'document': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CapabilityStatement)
        assert result.document is not None


class TestGetPathCapabilityStatement:

    def test_get_path_id(self):
        resource = CapabilityStatement()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = CapabilityStatement()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = CapabilityStatement()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'CapabilityStatement.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = CapabilityStatement()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = CapabilityStatement()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = CapabilityStatement()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = CapabilityStatement()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = CapabilityStatement()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = CapabilityStatement()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = CapabilityStatement()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = CapabilityStatement()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_version(self):
        resource = CapabilityStatement()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = CapabilityStatement()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = CapabilityStatement()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_status(self):
        resource = CapabilityStatement()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = CapabilityStatement()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = CapabilityStatement()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = CapabilityStatement()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = CapabilityStatement()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = CapabilityStatement()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = CapabilityStatement()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = CapabilityStatement()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_purpose(self):
        resource = CapabilityStatement()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_copyright(self):
        resource = CapabilityStatement()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_kind(self):
        resource = CapabilityStatement()
        resource.kind = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'kind')
        assert result is not None

    def test_get_path_instantiates(self):
        resource = CapabilityStatement()
        resource.instantiates = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiates')
        assert result is not None

    def test_get_path_imports(self):
        resource = CapabilityStatement()
        resource.imports = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'imports')
        assert result is not None

    def test_get_path_software(self):
        resource = CapabilityStatement()
        resource.software = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'software')
        assert result is not None

    def test_get_path_implementation(self):
        resource = CapabilityStatement()
        resource.implementation = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implementation')
        assert result is not None

    def test_get_path_fhir_version(self):
        resource = CapabilityStatement()
        resource.fhirVersion = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'fhirVersion')
        assert result is not None

    def test_get_path_format(self):
        resource = CapabilityStatement()
        resource.format = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'format')
        assert result is not None

    def test_get_path_patch_format(self):
        resource = CapabilityStatement()
        resource.patchFormat = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patchFormat')
        assert result is not None

    def test_get_path_implementation_guide(self):
        resource = CapabilityStatement()
        resource.implementationGuide = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implementationGuide')
        assert result is not None

    def test_get_path_rest(self):
        resource = CapabilityStatement()
        resource.rest = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'rest')
        assert result is not None

    def test_get_path_messaging(self):
        resource = CapabilityStatement()
        resource.messaging = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'messaging')
        assert result is not None

    def test_get_path_document(self):
        resource = CapabilityStatement()
        resource.document = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'document')
        assert result is not None


class TestSetPathCapabilityStatement:

    def test_set_path_id(self):
        resource = CapabilityStatement()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = CapabilityStatement()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'CapabilityStatement.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = CapabilityStatement()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = CapabilityStatement()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = CapabilityStatement()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = CapabilityStatement()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = CapabilityStatement()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = CapabilityStatement()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = CapabilityStatement()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = CapabilityStatement()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_version(self):
        resource = CapabilityStatement()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = CapabilityStatement()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = CapabilityStatement()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_status(self):
        resource = CapabilityStatement()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = CapabilityStatement()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = CapabilityStatement()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = CapabilityStatement()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = CapabilityStatement()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = CapabilityStatement()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = CapabilityStatement()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = CapabilityStatement()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_purpose(self):
        resource = CapabilityStatement()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_copyright(self):
        resource = CapabilityStatement()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_kind(self):
        resource = CapabilityStatement()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'kind', value)
        assert result is True
        assert resource.kind is not None

    def test_set_path_instantiates(self):
        resource = CapabilityStatement()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiates', value)
        assert result is True
        assert resource.instantiates is not None

    def test_set_path_imports(self):
        resource = CapabilityStatement()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'imports', value)
        assert result is True
        assert resource.imports is not None

    def test_set_path_software(self):
        resource = CapabilityStatement()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'software', value)
        assert result is True
        assert resource.software is not None

    def test_set_path_implementation(self):
        resource = CapabilityStatement()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implementation', value)
        assert result is True
        assert resource.implementation is not None

    def test_set_path_fhir_version(self):
        resource = CapabilityStatement()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'fhirVersion', value)
        assert result is True
        assert resource.fhirVersion is not None

    def test_set_path_format(self):
        resource = CapabilityStatement()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'format', value)
        assert result is True
        assert resource.format is not None

    def test_set_path_patch_format(self):
        resource = CapabilityStatement()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patchFormat', value)
        assert result is True
        assert resource.patchFormat is not None

    def test_set_path_implementation_guide(self):
        resource = CapabilityStatement()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implementationGuide', value)
        assert result is True
        assert resource.implementationGuide is not None

    def test_set_path_rest(self):
        resource = CapabilityStatement()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'rest', value)
        assert result is True
        assert resource.rest is not None

    def test_set_path_messaging(self):
        resource = CapabilityStatement()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'messaging', value)
        assert result is True
        assert resource.messaging is not None

    def test_set_path_document(self):
        resource = CapabilityStatement()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'document', value)
        assert result is True
        assert resource.document is not None


class TestParsePathCapabilityStatement:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('CapabilityStatement.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('CapabilityStatement.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('CapabilityStatement.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
