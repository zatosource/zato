# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ImplementationGuide


class TestToDictImplementationGuide:

    def test_to_dict_empty(self):
        resource = ImplementationGuide()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ImplementationGuide'

    def test_to_dict_with_id(self):
        resource = ImplementationGuide()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ImplementationGuide()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ImplementationGuide)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ImplementationGuide()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ImplementationGuide()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ImplementationGuide()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ImplementationGuide()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ImplementationGuide()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ImplementationGuide()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ImplementationGuide()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ImplementationGuide()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = ImplementationGuide()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_version(self):
        resource = ImplementationGuide()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = ImplementationGuide()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = ImplementationGuide()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_status(self):
        resource = ImplementationGuide()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = ImplementationGuide()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = ImplementationGuide()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = ImplementationGuide()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = ImplementationGuide()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = ImplementationGuide()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = ImplementationGuide()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = ImplementationGuide()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_copyright(self):
        resource = ImplementationGuide()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_package_id(self):
        resource = ImplementationGuide()
        resource.packageId = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'packageId' in result

    def test_to_dict_license(self):
        resource = ImplementationGuide()
        resource.license = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'license' in result

    def test_to_dict_fhir_version(self):
        resource = ImplementationGuide()
        resource.fhirVersion = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'fhirVersion' in result

    def test_to_dict_depends_on(self):
        resource = ImplementationGuide()
        resource.dependsOn = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dependsOn' in result

    def test_to_dict_global(self):
        resource = ImplementationGuide()
        resource.global_ = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'global' in result

    def test_to_dict_definition(self):
        resource = ImplementationGuide()
        resource.definition = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'definition' in result

    def test_to_dict_manifest(self):
        resource = ImplementationGuide()
        resource.manifest = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'manifest' in result


class TestFromDictImplementationGuide:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ImplementationGuide', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert isinstance(result, ImplementationGuide)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ImplementationGuide'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert isinstance(result, ImplementationGuide)

    def test_from_dict_id(self):
        data = {'resourceType': 'ImplementationGuide', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ImplementationGuide', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ImplementationGuide', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ImplementationGuide', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ImplementationGuide', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ImplementationGuide', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ImplementationGuide', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ImplementationGuide', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'ImplementationGuide', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.url is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'ImplementationGuide', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'ImplementationGuide', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'ImplementationGuide', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.title is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'ImplementationGuide', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'ImplementationGuide', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'ImplementationGuide', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'ImplementationGuide', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'ImplementationGuide', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'ImplementationGuide', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'ImplementationGuide', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'ImplementationGuide'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.jurisdiction is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'ImplementationGuide', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.copyright is not None

    def test_from_dict_package_id(self):
        data = {'resourceType': 'ImplementationGuide', 'packageId': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.packageId is not None

    def test_from_dict_license(self):
        data = {'resourceType': 'ImplementationGuide', 'license': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.license is not None

    def test_from_dict_fhir_version(self):
        data = {'resourceType': 'ImplementationGuide', 'fhirVersion': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.fhirVersion is not None

    def test_from_dict_depends_on(self):
        data = {'resourceType': 'ImplementationGuide', 'dependsOn': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.dependsOn is not None

    def test_from_dict_global(self):
        data = {'resourceType': 'ImplementationGuide', 'global': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.global_ is not None

    def test_from_dict_definition(self):
        data = {'resourceType': 'ImplementationGuide', 'definition': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.definition is not None

    def test_from_dict_manifest(self):
        data = {'resourceType': 'ImplementationGuide', 'manifest': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ImplementationGuide)
        assert result.manifest is not None


class TestGetPathImplementationGuide:

    def test_get_path_id(self):
        resource = ImplementationGuide()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ImplementationGuide()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ImplementationGuide()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ImplementationGuide.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ImplementationGuide()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ImplementationGuide()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ImplementationGuide()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ImplementationGuide()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ImplementationGuide()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ImplementationGuide()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ImplementationGuide()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = ImplementationGuide()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_version(self):
        resource = ImplementationGuide()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = ImplementationGuide()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = ImplementationGuide()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_status(self):
        resource = ImplementationGuide()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = ImplementationGuide()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = ImplementationGuide()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = ImplementationGuide()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = ImplementationGuide()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = ImplementationGuide()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = ImplementationGuide()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = ImplementationGuide()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_copyright(self):
        resource = ImplementationGuide()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_package_id(self):
        resource = ImplementationGuide()
        resource.packageId = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'packageId')
        assert result is not None

    def test_get_path_license(self):
        resource = ImplementationGuide()
        resource.license = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'license')
        assert result is not None

    def test_get_path_fhir_version(self):
        resource = ImplementationGuide()
        resource.fhirVersion = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'fhirVersion')
        assert result is not None

    def test_get_path_depends_on(self):
        resource = ImplementationGuide()
        resource.dependsOn = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dependsOn')
        assert result is not None

    def test_get_path_global(self):
        resource = ImplementationGuide()
        resource.global_ = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'global')
        assert result is not None

    def test_get_path_definition(self):
        resource = ImplementationGuide()
        resource.definition = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'definition')
        assert result is not None

    def test_get_path_manifest(self):
        resource = ImplementationGuide()
        resource.manifest = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'manifest')
        assert result is not None


class TestSetPathImplementationGuide:

    def test_set_path_id(self):
        resource = ImplementationGuide()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ImplementationGuide()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ImplementationGuide.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ImplementationGuide()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ImplementationGuide()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ImplementationGuide()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ImplementationGuide()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ImplementationGuide()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ImplementationGuide()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ImplementationGuide()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = ImplementationGuide()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_version(self):
        resource = ImplementationGuide()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = ImplementationGuide()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = ImplementationGuide()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_status(self):
        resource = ImplementationGuide()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = ImplementationGuide()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = ImplementationGuide()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = ImplementationGuide()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = ImplementationGuide()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = ImplementationGuide()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = ImplementationGuide()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = ImplementationGuide()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_copyright(self):
        resource = ImplementationGuide()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_package_id(self):
        resource = ImplementationGuide()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'packageId', value)
        assert result is True
        assert resource.packageId is not None

    def test_set_path_license(self):
        resource = ImplementationGuide()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'license', value)
        assert result is True
        assert resource.license is not None

    def test_set_path_fhir_version(self):
        resource = ImplementationGuide()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'fhirVersion', value)
        assert result is True
        assert resource.fhirVersion is not None

    def test_set_path_depends_on(self):
        resource = ImplementationGuide()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dependsOn', value)
        assert result is True
        assert resource.dependsOn is not None

    def test_set_path_global(self):
        resource = ImplementationGuide()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'global', value)
        assert result is True
        assert resource.global_ is not None

    def test_set_path_definition(self):
        resource = ImplementationGuide()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'definition', value)
        assert result is True
        assert resource.definition is not None

    def test_set_path_manifest(self):
        resource = ImplementationGuide()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'manifest', value)
        assert result is True
        assert resource.manifest is not None


class TestParsePathImplementationGuide:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ImplementationGuide.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ImplementationGuide.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ImplementationGuide.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
