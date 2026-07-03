# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import CompartmentDefinition


class TestToDictCompartmentDefinition:

    def test_to_dict_empty(self):
        resource = CompartmentDefinition()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'CompartmentDefinition'

    def test_to_dict_with_id(self):
        resource = CompartmentDefinition()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = CompartmentDefinition()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, CompartmentDefinition)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = CompartmentDefinition()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = CompartmentDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = CompartmentDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = CompartmentDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = CompartmentDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = CompartmentDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = CompartmentDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = CompartmentDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = CompartmentDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_version(self):
        resource = CompartmentDefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = CompartmentDefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_status(self):
        resource = CompartmentDefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = CompartmentDefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = CompartmentDefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = CompartmentDefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = CompartmentDefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = CompartmentDefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = CompartmentDefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_purpose(self):
        resource = CompartmentDefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_code(self):
        resource = CompartmentDefinition()
        resource.code = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_search(self):
        resource = CompartmentDefinition()
        resource.search = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'search' in result

    def test_to_dict_resource(self):
        resource = CompartmentDefinition()
        resource.resource = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'resource' in result


class TestFromDictCompartmentDefinition:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'CompartmentDefinition', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert isinstance(result, CompartmentDefinition)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'CompartmentDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert isinstance(result, CompartmentDefinition)

    def test_from_dict_id(self):
        data = {'resourceType': 'CompartmentDefinition', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'CompartmentDefinition', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'CompartmentDefinition', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'CompartmentDefinition', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'CompartmentDefinition', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'CompartmentDefinition', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'CompartmentDefinition', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'CompartmentDefinition', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'CompartmentDefinition', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.url is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'CompartmentDefinition', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'CompartmentDefinition', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.name is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'CompartmentDefinition', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'CompartmentDefinition', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'CompartmentDefinition', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'CompartmentDefinition', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'CompartmentDefinition', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'CompartmentDefinition', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'CompartmentDefinition', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.useContext is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'CompartmentDefinition', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.purpose is not None

    def test_from_dict_code(self):
        data = {'resourceType': 'CompartmentDefinition', 'code': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.code is not None

    def test_from_dict_search(self):
        data = {'resourceType': 'CompartmentDefinition', 'search': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.search is not None

    def test_from_dict_resource(self):
        data = {'resourceType': 'CompartmentDefinition', 'resource': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CompartmentDefinition)
        assert result.resource is not None


class TestGetPathCompartmentDefinition:

    def test_get_path_id(self):
        resource = CompartmentDefinition()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = CompartmentDefinition()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = CompartmentDefinition()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'CompartmentDefinition.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = CompartmentDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = CompartmentDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = CompartmentDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = CompartmentDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = CompartmentDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = CompartmentDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = CompartmentDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = CompartmentDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_version(self):
        resource = CompartmentDefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = CompartmentDefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_status(self):
        resource = CompartmentDefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = CompartmentDefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = CompartmentDefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = CompartmentDefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = CompartmentDefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = CompartmentDefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = CompartmentDefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_purpose(self):
        resource = CompartmentDefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_code(self):
        resource = CompartmentDefinition()
        resource.code = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_search(self):
        resource = CompartmentDefinition()
        resource.search = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'search')
        assert result is not None

    def test_get_path_resource(self):
        resource = CompartmentDefinition()
        resource.resource = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'resource')
        assert result is not None


class TestSetPathCompartmentDefinition:

    def test_set_path_id(self):
        resource = CompartmentDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = CompartmentDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'CompartmentDefinition.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = CompartmentDefinition()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = CompartmentDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = CompartmentDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = CompartmentDefinition()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = CompartmentDefinition()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = CompartmentDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = CompartmentDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = CompartmentDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_version(self):
        resource = CompartmentDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = CompartmentDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_status(self):
        resource = CompartmentDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = CompartmentDefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = CompartmentDefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = CompartmentDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = CompartmentDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = CompartmentDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = CompartmentDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_purpose(self):
        resource = CompartmentDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_code(self):
        resource = CompartmentDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_search(self):
        resource = CompartmentDefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'search', value)
        assert result is True
        assert resource.search is not None

    def test_set_path_resource(self):
        resource = CompartmentDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'resource', value)
        assert result is True
        assert resource.resource is not None


class TestParsePathCompartmentDefinition:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('CompartmentDefinition.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('CompartmentDefinition.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('CompartmentDefinition.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
