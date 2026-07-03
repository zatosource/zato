# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Group


class TestToDictGroup:

    def test_to_dict_empty(self):
        resource = Group()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Group'

    def test_to_dict_with_id(self):
        resource = Group()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Group()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Group)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Group()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Group()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Group()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Group()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Group()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Group()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Group()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Group()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Group()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_active(self):
        resource = Group()
        resource.active = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'active' in result

    def test_to_dict_type(self):
        resource = Group()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_actual(self):
        resource = Group()
        resource.actual = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'actual' in result

    def test_to_dict_code(self):
        resource = Group()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_name(self):
        resource = Group()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_quantity(self):
        resource = Group()
        resource.quantity = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'quantity' in result

    def test_to_dict_managing_entity(self):
        resource = Group()
        resource.managingEntity = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'managingEntity' in result

    def test_to_dict_characteristic(self):
        resource = Group()
        resource.characteristic = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'characteristic' in result

    def test_to_dict_member(self):
        resource = Group()
        resource.member = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'member' in result


class TestFromDictGroup:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Group', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert isinstance(result, Group)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Group'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert isinstance(result, Group)

    def test_from_dict_id(self):
        data = {'resourceType': 'Group', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Group', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Group', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Group', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Group', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Group', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Group', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Group', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Group', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.identifier is not None

    def test_from_dict_active(self):
        data = {'resourceType': 'Group', 'active': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.active is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'Group', 'type': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.type_ is not None

    def test_from_dict_actual(self):
        data = {'resourceType': 'Group', 'actual': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.actual is not None

    def test_from_dict_code(self):
        data = {'resourceType': 'Group', 'code': {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.code is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'Group', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.name is not None

    def test_from_dict_quantity(self):
        data = {'resourceType': 'Group', 'quantity': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.quantity is not None

    def test_from_dict_managing_entity(self):
        data = {'resourceType': 'Group', 'managingEntity': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.managingEntity is not None

    def test_from_dict_characteristic(self):
        data = {'resourceType': 'Group', 'characteristic': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.characteristic is not None

    def test_from_dict_member(self):
        data = {'resourceType': 'Group', 'member': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Group)
        assert result.member is not None


class TestGetPathGroup:

    def test_get_path_id(self):
        resource = Group()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Group()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Group()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Group.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Group()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Group()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Group()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Group()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Group()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Group()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Group()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Group()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_active(self):
        resource = Group()
        resource.active = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'active')
        assert result is not None

    def test_get_path_type(self):
        resource = Group()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_actual(self):
        resource = Group()
        resource.actual = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'actual')
        assert result is not None

    def test_get_path_code(self):
        resource = Group()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_name(self):
        resource = Group()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_quantity(self):
        resource = Group()
        resource.quantity = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'quantity')
        assert result is not None

    def test_get_path_managing_entity(self):
        resource = Group()
        resource.managingEntity = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'managingEntity')
        assert result is not None

    def test_get_path_characteristic(self):
        resource = Group()
        resource.characteristic = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'characteristic')
        assert result is not None

    def test_get_path_member(self):
        resource = Group()
        resource.member = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'member')
        assert result is not None


class TestSetPathGroup:

    def test_set_path_id(self):
        resource = Group()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Group()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Group.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Group()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Group()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Group()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Group()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Group()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Group()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Group()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Group()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_active(self):
        resource = Group()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'active', value)
        assert result is True
        assert resource.active is not None

    def test_set_path_type(self):
        resource = Group()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_actual(self):
        resource = Group()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'actual', value)
        assert result is True
        assert resource.actual is not None

    def test_set_path_code(self):
        resource = Group()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_name(self):
        resource = Group()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_quantity(self):
        resource = Group()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'quantity', value)
        assert result is True
        assert resource.quantity is not None

    def test_set_path_managing_entity(self):
        resource = Group()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'managingEntity', value)
        assert result is True
        assert resource.managingEntity is not None

    def test_set_path_characteristic(self):
        resource = Group()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'characteristic', value)
        assert result is True
        assert resource.characteristic is not None

    def test_set_path_member(self):
        resource = Group()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'member', value)
        assert result is True
        assert resource.member is not None


class TestParsePathGroup:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Group.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Group.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Group.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
