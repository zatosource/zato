# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import TerminologyCapabilities


class TestToDictTerminologyCapabilities:

    def test_to_dict_empty(self):
        resource = TerminologyCapabilities()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'TerminologyCapabilities'

    def test_to_dict_with_id(self):
        resource = TerminologyCapabilities()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = TerminologyCapabilities()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, TerminologyCapabilities)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = TerminologyCapabilities()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = TerminologyCapabilities()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = TerminologyCapabilities()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = TerminologyCapabilities()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = TerminologyCapabilities()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = TerminologyCapabilities()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = TerminologyCapabilities()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = TerminologyCapabilities()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = TerminologyCapabilities()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_version(self):
        resource = TerminologyCapabilities()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = TerminologyCapabilities()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = TerminologyCapabilities()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_status(self):
        resource = TerminologyCapabilities()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = TerminologyCapabilities()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = TerminologyCapabilities()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = TerminologyCapabilities()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = TerminologyCapabilities()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = TerminologyCapabilities()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = TerminologyCapabilities()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = TerminologyCapabilities()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_purpose(self):
        resource = TerminologyCapabilities()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_copyright(self):
        resource = TerminologyCapabilities()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_kind(self):
        resource = TerminologyCapabilities()
        resource.kind = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'kind' in result

    def test_to_dict_software(self):
        resource = TerminologyCapabilities()
        resource.software = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'software' in result

    def test_to_dict_implementation(self):
        resource = TerminologyCapabilities()
        resource.implementation = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implementation' in result

    def test_to_dict_locked_date(self):
        resource = TerminologyCapabilities()
        resource.lockedDate = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lockedDate' in result

    def test_to_dict_code_system(self):
        resource = TerminologyCapabilities()
        resource.codeSystem = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'codeSystem' in result

    def test_to_dict_expansion(self):
        resource = TerminologyCapabilities()
        resource.expansion = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'expansion' in result

    def test_to_dict_code_search(self):
        resource = TerminologyCapabilities()
        resource.codeSearch = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'codeSearch' in result

    def test_to_dict_validate_code(self):
        resource = TerminologyCapabilities()
        resource.validateCode = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'validateCode' in result

    def test_to_dict_translation(self):
        resource = TerminologyCapabilities()
        resource.translation = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'translation' in result

    def test_to_dict_closure(self):
        resource = TerminologyCapabilities()
        resource.closure = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'closure' in result


class TestFromDictTerminologyCapabilities:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'TerminologyCapabilities', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert isinstance(result, TerminologyCapabilities)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'TerminologyCapabilities'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert isinstance(result, TerminologyCapabilities)

    def test_from_dict_id(self):
        data = {'resourceType': 'TerminologyCapabilities', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'TerminologyCapabilities', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'TerminologyCapabilities', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'TerminologyCapabilities', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'TerminologyCapabilities', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'TerminologyCapabilities', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'TerminologyCapabilities', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'TerminologyCapabilities', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'TerminologyCapabilities', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.url is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'TerminologyCapabilities', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'TerminologyCapabilities', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'TerminologyCapabilities', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.title is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'TerminologyCapabilities', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'TerminologyCapabilities', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'TerminologyCapabilities', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'TerminologyCapabilities', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'TerminologyCapabilities', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'TerminologyCapabilities', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'TerminologyCapabilities', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'TerminologyCapabilities'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.jurisdiction is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'TerminologyCapabilities', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.purpose is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'TerminologyCapabilities', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.copyright is not None

    def test_from_dict_kind(self):
        data = {'resourceType': 'TerminologyCapabilities', 'kind': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.kind is not None

    def test_from_dict_software(self):
        data = {'resourceType': 'TerminologyCapabilities', 'software': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.software is not None

    def test_from_dict_implementation(self):
        data = {'resourceType': 'TerminologyCapabilities', 'implementation': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.implementation is not None

    def test_from_dict_locked_date(self):
        data = {'resourceType': 'TerminologyCapabilities', 'lockedDate': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.lockedDate is not None

    def test_from_dict_code_system(self):
        data = {'resourceType': 'TerminologyCapabilities', 'codeSystem': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.codeSystem is not None

    def test_from_dict_expansion(self):
        data = {'resourceType': 'TerminologyCapabilities', 'expansion': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.expansion is not None

    def test_from_dict_code_search(self):
        data = {'resourceType': 'TerminologyCapabilities', 'codeSearch': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.codeSearch is not None

    def test_from_dict_validate_code(self):
        data = {'resourceType': 'TerminologyCapabilities', 'validateCode': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.validateCode is not None

    def test_from_dict_translation(self):
        data = {'resourceType': 'TerminologyCapabilities', 'translation': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.translation is not None

    def test_from_dict_closure(self):
        data = {'resourceType': 'TerminologyCapabilities', 'closure': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, TerminologyCapabilities)
        assert result.closure is not None


class TestGetPathTerminologyCapabilities:

    def test_get_path_id(self):
        resource = TerminologyCapabilities()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = TerminologyCapabilities()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = TerminologyCapabilities()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'TerminologyCapabilities.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = TerminologyCapabilities()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = TerminologyCapabilities()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = TerminologyCapabilities()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = TerminologyCapabilities()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = TerminologyCapabilities()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = TerminologyCapabilities()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = TerminologyCapabilities()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = TerminologyCapabilities()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_version(self):
        resource = TerminologyCapabilities()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = TerminologyCapabilities()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = TerminologyCapabilities()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_status(self):
        resource = TerminologyCapabilities()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = TerminologyCapabilities()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = TerminologyCapabilities()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = TerminologyCapabilities()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = TerminologyCapabilities()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = TerminologyCapabilities()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = TerminologyCapabilities()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = TerminologyCapabilities()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_purpose(self):
        resource = TerminologyCapabilities()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_copyright(self):
        resource = TerminologyCapabilities()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_kind(self):
        resource = TerminologyCapabilities()
        resource.kind = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'kind')
        assert result is not None

    def test_get_path_software(self):
        resource = TerminologyCapabilities()
        resource.software = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'software')
        assert result is not None

    def test_get_path_implementation(self):
        resource = TerminologyCapabilities()
        resource.implementation = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implementation')
        assert result is not None

    def test_get_path_locked_date(self):
        resource = TerminologyCapabilities()
        resource.lockedDate = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lockedDate')
        assert result is not None

    def test_get_path_code_system(self):
        resource = TerminologyCapabilities()
        resource.codeSystem = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'codeSystem')
        assert result is not None

    def test_get_path_expansion(self):
        resource = TerminologyCapabilities()
        resource.expansion = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'expansion')
        assert result is not None

    def test_get_path_code_search(self):
        resource = TerminologyCapabilities()
        resource.codeSearch = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'codeSearch')
        assert result is not None

    def test_get_path_validate_code(self):
        resource = TerminologyCapabilities()
        resource.validateCode = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'validateCode')
        assert result is not None

    def test_get_path_translation(self):
        resource = TerminologyCapabilities()
        resource.translation = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'translation')
        assert result is not None

    def test_get_path_closure(self):
        resource = TerminologyCapabilities()
        resource.closure = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'closure')
        assert result is not None


class TestSetPathTerminologyCapabilities:

    def test_set_path_id(self):
        resource = TerminologyCapabilities()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = TerminologyCapabilities()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'TerminologyCapabilities.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = TerminologyCapabilities()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = TerminologyCapabilities()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = TerminologyCapabilities()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = TerminologyCapabilities()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = TerminologyCapabilities()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = TerminologyCapabilities()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = TerminologyCapabilities()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = TerminologyCapabilities()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_version(self):
        resource = TerminologyCapabilities()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = TerminologyCapabilities()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = TerminologyCapabilities()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_status(self):
        resource = TerminologyCapabilities()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = TerminologyCapabilities()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = TerminologyCapabilities()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = TerminologyCapabilities()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = TerminologyCapabilities()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = TerminologyCapabilities()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = TerminologyCapabilities()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = TerminologyCapabilities()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_purpose(self):
        resource = TerminologyCapabilities()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_copyright(self):
        resource = TerminologyCapabilities()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_kind(self):
        resource = TerminologyCapabilities()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'kind', value)
        assert result is True
        assert resource.kind is not None

    def test_set_path_software(self):
        resource = TerminologyCapabilities()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'software', value)
        assert result is True
        assert resource.software is not None

    def test_set_path_implementation(self):
        resource = TerminologyCapabilities()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implementation', value)
        assert result is True
        assert resource.implementation is not None

    def test_set_path_locked_date(self):
        resource = TerminologyCapabilities()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lockedDate', value)
        assert result is True
        assert resource.lockedDate is not None

    def test_set_path_code_system(self):
        resource = TerminologyCapabilities()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'codeSystem', value)
        assert result is True
        assert resource.codeSystem is not None

    def test_set_path_expansion(self):
        resource = TerminologyCapabilities()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'expansion', value)
        assert result is True
        assert resource.expansion is not None

    def test_set_path_code_search(self):
        resource = TerminologyCapabilities()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'codeSearch', value)
        assert result is True
        assert resource.codeSearch is not None

    def test_set_path_validate_code(self):
        resource = TerminologyCapabilities()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'validateCode', value)
        assert result is True
        assert resource.validateCode is not None

    def test_set_path_translation(self):
        resource = TerminologyCapabilities()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'translation', value)
        assert result is True
        assert resource.translation is not None

    def test_set_path_closure(self):
        resource = TerminologyCapabilities()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'closure', value)
        assert result is True
        assert resource.closure is not None


class TestParsePathTerminologyCapabilities:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('TerminologyCapabilities.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('TerminologyCapabilities.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('TerminologyCapabilities.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
