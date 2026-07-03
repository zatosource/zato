# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import actualgroup


class TestToDictactualgroup:

    def test_to_dict_empty(self):
        resource = actualgroup()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'actualgroup'

    def test_to_dict_with_id(self):
        resource = actualgroup()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = actualgroup()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, actualgroup)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = actualgroup()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = actualgroup()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = actualgroup()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = actualgroup()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = actualgroup()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = actualgroup()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = actualgroup()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = actualgroup()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = actualgroup()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_active(self):
        resource = actualgroup()
        resource.active = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'active' in result

    def test_to_dict_type(self):
        resource = actualgroup()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_actual(self):
        resource = actualgroup()
        resource.actual = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'actual' in result

    def test_to_dict_code(self):
        resource = actualgroup()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_name(self):
        resource = actualgroup()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_quantity(self):
        resource = actualgroup()
        resource.quantity = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'quantity' in result

    def test_to_dict_managing_entity(self):
        resource = actualgroup()
        resource.managingEntity = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'managingEntity' in result

    def test_to_dict_characteristic(self):
        resource = actualgroup()
        resource.characteristic = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'characteristic' in result

    def test_to_dict_member(self):
        resource = actualgroup()
        resource.member = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'member' in result


class TestFromDictactualgroup:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'actualgroup', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert isinstance(result, actualgroup)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'actualgroup'}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert isinstance(result, actualgroup)

    def test_from_dict_id(self):
        data = {'resourceType': 'actualgroup', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'actualgroup', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'actualgroup', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'actualgroup', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'actualgroup', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'actualgroup', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'actualgroup', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'actualgroup', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'actualgroup', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.identifier is not None

    def test_from_dict_active(self):
        data = {'resourceType': 'actualgroup', 'active': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.active is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'actualgroup', 'type': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.type_ is not None

    def test_from_dict_actual(self):
        data = {'resourceType': 'actualgroup', 'actual': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.actual is not None

    def test_from_dict_code(self):
        data = {'code': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'actualgroup'}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.code is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'actualgroup', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.name is not None

    def test_from_dict_quantity(self):
        data = {'resourceType': 'actualgroup', 'quantity': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.quantity is not None

    def test_from_dict_managing_entity(self):
        data = {'resourceType': 'actualgroup', 'managingEntity': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.managingEntity is not None

    def test_from_dict_characteristic(self):
        data = {'resourceType': 'actualgroup', 'characteristic': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.characteristic is not None

    def test_from_dict_member(self):
        data = {'resourceType': 'actualgroup', 'member': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, actualgroup)
        assert result.member is not None


class TestGetPathactualgroup:

    def test_get_path_id(self):
        resource = actualgroup()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = actualgroup()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = actualgroup()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'actualgroup.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = actualgroup()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = actualgroup()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = actualgroup()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = actualgroup()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = actualgroup()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = actualgroup()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = actualgroup()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = actualgroup()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_active(self):
        resource = actualgroup()
        resource.active = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'active')
        assert result is not None

    def test_get_path_type(self):
        resource = actualgroup()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_actual(self):
        resource = actualgroup()
        resource.actual = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'actual')
        assert result is not None

    def test_get_path_code(self):
        resource = actualgroup()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_name(self):
        resource = actualgroup()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_quantity(self):
        resource = actualgroup()
        resource.quantity = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'quantity')
        assert result is not None

    def test_get_path_managing_entity(self):
        resource = actualgroup()
        resource.managingEntity = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'managingEntity')
        assert result is not None

    def test_get_path_characteristic(self):
        resource = actualgroup()
        resource.characteristic = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'characteristic')
        assert result is not None

    def test_get_path_member(self):
        resource = actualgroup()
        resource.member = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'member')
        assert result is not None


class TestSetPathactualgroup:

    def test_set_path_id(self):
        resource = actualgroup()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = actualgroup()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'actualgroup.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = actualgroup()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = actualgroup()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = actualgroup()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = actualgroup()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = actualgroup()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = actualgroup()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = actualgroup()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = actualgroup()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_active(self):
        resource = actualgroup()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'active', value)
        assert result is True
        assert resource.active is not None

    def test_set_path_type(self):
        resource = actualgroup()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_actual(self):
        resource = actualgroup()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'actual', value)
        assert result is True
        assert resource.actual is not None

    def test_set_path_code(self):
        resource = actualgroup()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_name(self):
        resource = actualgroup()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_quantity(self):
        resource = actualgroup()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'quantity', value)
        assert result is True
        assert resource.quantity is not None

    def test_set_path_managing_entity(self):
        resource = actualgroup()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'managingEntity', value)
        assert result is True
        assert resource.managingEntity is not None

    def test_set_path_characteristic(self):
        resource = actualgroup()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'characteristic', value)
        assert result is True
        assert resource.characteristic is not None

    def test_set_path_member(self):
        resource = actualgroup()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'member', value)
        assert result is True
        assert resource.member is not None


class TestParsePathactualgroup:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('actualgroup.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('actualgroup.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('actualgroup.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
