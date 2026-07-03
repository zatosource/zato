# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import NamingSystem


class TestToDictNamingSystem:

    def test_to_dict_empty(self):
        resource = NamingSystem()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'NamingSystem'

    def test_to_dict_with_id(self):
        resource = NamingSystem()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = NamingSystem()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, NamingSystem)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = NamingSystem()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = NamingSystem()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = NamingSystem()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = NamingSystem()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = NamingSystem()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = NamingSystem()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = NamingSystem()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = NamingSystem()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_name(self):
        resource = NamingSystem()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_status(self):
        resource = NamingSystem()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_kind(self):
        resource = NamingSystem()
        resource.kind = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'kind' in result

    def test_to_dict_date(self):
        resource = NamingSystem()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = NamingSystem()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = NamingSystem()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_responsible(self):
        resource = NamingSystem()
        resource.responsible = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'responsible' in result

    def test_to_dict_type(self):
        resource = NamingSystem()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_description(self):
        resource = NamingSystem()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = NamingSystem()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = NamingSystem()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_usage(self):
        resource = NamingSystem()
        resource.usage = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'usage' in result

    def test_to_dict_unique_id(self):
        resource = NamingSystem()
        resource.uniqueId = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'uniqueId' in result


class TestFromDictNamingSystem:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'NamingSystem', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert isinstance(result, NamingSystem)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'NamingSystem'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert isinstance(result, NamingSystem)

    def test_from_dict_id(self):
        data = {'resourceType': 'NamingSystem', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'NamingSystem', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'NamingSystem', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'NamingSystem', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'NamingSystem', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'NamingSystem', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'NamingSystem', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'NamingSystem', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.modifierExtension is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'NamingSystem', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.name is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'NamingSystem', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.status is not None

    def test_from_dict_kind(self):
        data = {'resourceType': 'NamingSystem', 'kind': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.kind is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'NamingSystem', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'NamingSystem', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'NamingSystem', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.contact is not None

    def test_from_dict_responsible(self):
        data = {'resourceType': 'NamingSystem', 'responsible': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.responsible is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'NamingSystem',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.type_ is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'NamingSystem', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'NamingSystem', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'NamingSystem'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.jurisdiction is not None

    def test_from_dict_usage(self):
        data = {'resourceType': 'NamingSystem', 'usage': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.usage is not None

    def test_from_dict_unique_id(self):
        data = {'resourceType': 'NamingSystem', 'uniqueId': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, NamingSystem)
        assert result.uniqueId is not None


class TestGetPathNamingSystem:

    def test_get_path_id(self):
        resource = NamingSystem()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = NamingSystem()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = NamingSystem()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'NamingSystem.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = NamingSystem()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = NamingSystem()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = NamingSystem()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = NamingSystem()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = NamingSystem()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = NamingSystem()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = NamingSystem()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_name(self):
        resource = NamingSystem()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_status(self):
        resource = NamingSystem()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_kind(self):
        resource = NamingSystem()
        resource.kind = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'kind')
        assert result is not None

    def test_get_path_date(self):
        resource = NamingSystem()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = NamingSystem()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = NamingSystem()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_responsible(self):
        resource = NamingSystem()
        resource.responsible = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'responsible')
        assert result is not None

    def test_get_path_type(self):
        resource = NamingSystem()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_description(self):
        resource = NamingSystem()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = NamingSystem()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = NamingSystem()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_usage(self):
        resource = NamingSystem()
        resource.usage = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'usage')
        assert result is not None

    def test_get_path_unique_id(self):
        resource = NamingSystem()
        resource.uniqueId = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'uniqueId')
        assert result is not None


class TestSetPathNamingSystem:

    def test_set_path_id(self):
        resource = NamingSystem()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = NamingSystem()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'NamingSystem.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = NamingSystem()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = NamingSystem()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = NamingSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = NamingSystem()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = NamingSystem()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = NamingSystem()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = NamingSystem()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_name(self):
        resource = NamingSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_status(self):
        resource = NamingSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_kind(self):
        resource = NamingSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'kind', value)
        assert result is True
        assert resource.kind is not None

    def test_set_path_date(self):
        resource = NamingSystem()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = NamingSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = NamingSystem()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_responsible(self):
        resource = NamingSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'responsible', value)
        assert result is True
        assert resource.responsible is not None

    def test_set_path_type(self):
        resource = NamingSystem()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_description(self):
        resource = NamingSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = NamingSystem()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = NamingSystem()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_usage(self):
        resource = NamingSystem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'usage', value)
        assert result is True
        assert resource.usage is not None

    def test_set_path_unique_id(self):
        resource = NamingSystem()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'uniqueId', value)
        assert result is True
        assert resource.uniqueId is not None


class TestParsePathNamingSystem:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('NamingSystem.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('NamingSystem.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('NamingSystem.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
