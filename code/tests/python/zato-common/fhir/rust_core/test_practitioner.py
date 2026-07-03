# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Practitioner


class TestToDictPractitioner:

    def test_to_dict_empty(self):
        resource = Practitioner()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Practitioner'

    def test_to_dict_with_id(self):
        resource = Practitioner()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Practitioner()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Practitioner)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Practitioner()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Practitioner()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Practitioner()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Practitioner()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Practitioner()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Practitioner()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Practitioner()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Practitioner()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Practitioner()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_active(self):
        resource = Practitioner()
        resource.active = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'active' in result

    def test_to_dict_name(self):
        resource = Practitioner()
        resource.name = [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_telecom(self):
        resource = Practitioner()
        resource.telecom = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'telecom' in result

    def test_to_dict_address(self):
        resource = Practitioner()
        resource.address = [{'use': 'home', 'line': ['123 Main St'], 'city': 'Boston', 'state': 'MA', 'postalCode': '02101', 'country': 'USA'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'address' in result

    def test_to_dict_gender(self):
        resource = Practitioner()
        resource.gender = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'gender' in result

    def test_to_dict_birth_date(self):
        resource = Practitioner()
        resource.birthDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'birthDate' in result

    def test_to_dict_photo(self):
        resource = Practitioner()
        resource.photo = [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'photo' in result

    def test_to_dict_qualification(self):
        resource = Practitioner()
        resource.qualification = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'qualification' in result

    def test_to_dict_communication(self):
        resource = Practitioner()
        resource.communication = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'communication' in result


class TestFromDictPractitioner:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Practitioner', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert isinstance(result, Practitioner)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Practitioner'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert isinstance(result, Practitioner)

    def test_from_dict_id(self):
        data = {'resourceType': 'Practitioner', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Practitioner', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Practitioner', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Practitioner', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Practitioner', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Practitioner', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Practitioner', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Practitioner', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Practitioner', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.identifier is not None

    def test_from_dict_active(self):
        data = {'resourceType': 'Practitioner', 'active': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.active is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'Practitioner', 'name': [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.name is not None

    def test_from_dict_telecom(self):
        data = {'resourceType': 'Practitioner', 'telecom': [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.telecom is not None

    def test_from_dict_address(self):
        data = {'address': [{'city': 'Boston',
                      'country': 'USA',
                      'line': ['123 Main St'],
                      'postalCode': '02101',
                      'state': 'MA',
                      'use': 'home'}],
         'resourceType': 'Practitioner'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.address is not None

    def test_from_dict_gender(self):
        data = {'resourceType': 'Practitioner', 'gender': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.gender is not None

    def test_from_dict_birth_date(self):
        data = {'resourceType': 'Practitioner', 'birthDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.birthDate is not None

    def test_from_dict_photo(self):
        data = {'resourceType': 'Practitioner', 'photo': [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.photo is not None

    def test_from_dict_qualification(self):
        data = {'resourceType': 'Practitioner', 'qualification': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.qualification is not None

    def test_from_dict_communication(self):
        data = {'communication': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                            'text': 'Test concept'}],
         'resourceType': 'Practitioner'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Practitioner)
        assert result.communication is not None


class TestGetPathPractitioner:

    def test_get_path_id(self):
        resource = Practitioner()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Practitioner()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Practitioner()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Practitioner.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Practitioner()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Practitioner()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Practitioner()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Practitioner()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Practitioner()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Practitioner()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Practitioner()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Practitioner()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_active(self):
        resource = Practitioner()
        resource.active = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'active')
        assert result is not None

    def test_get_path_name(self):
        resource = Practitioner()
        resource.name = [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_telecom(self):
        resource = Practitioner()
        resource.telecom = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'telecom')
        assert result is not None

    def test_get_path_address(self):
        resource = Practitioner()
        resource.address = [{'use': 'home', 'line': ['123 Main St'], 'city': 'Boston', 'state': 'MA', 'postalCode': '02101', 'country': 'USA'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'address')
        assert result is not None

    def test_get_path_gender(self):
        resource = Practitioner()
        resource.gender = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'gender')
        assert result is not None

    def test_get_path_birth_date(self):
        resource = Practitioner()
        resource.birthDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'birthDate')
        assert result is not None

    def test_get_path_photo(self):
        resource = Practitioner()
        resource.photo = [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'photo')
        assert result is not None

    def test_get_path_qualification(self):
        resource = Practitioner()
        resource.qualification = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'qualification')
        assert result is not None

    def test_get_path_communication(self):
        resource = Practitioner()
        resource.communication = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'communication')
        assert result is not None


class TestSetPathPractitioner:

    def test_set_path_id(self):
        resource = Practitioner()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Practitioner()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Practitioner.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Practitioner()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Practitioner()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Practitioner()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Practitioner()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Practitioner()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Practitioner()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Practitioner()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Practitioner()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_active(self):
        resource = Practitioner()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'active', value)
        assert result is True
        assert resource.active is not None

    def test_set_path_name(self):
        resource = Practitioner()
        value = [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_telecom(self):
        resource = Practitioner()
        value = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'telecom', value)
        assert result is True
        assert resource.telecom is not None

    def test_set_path_address(self):
        resource = Practitioner()
        value = [{'use': 'home', 'line': ['123 Main St'], 'city': 'Boston', 'state': 'MA', 'postalCode': '02101', 'country': 'USA'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'address', value)
        assert result is True
        assert resource.address is not None

    def test_set_path_gender(self):
        resource = Practitioner()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'gender', value)
        assert result is True
        assert resource.gender is not None

    def test_set_path_birth_date(self):
        resource = Practitioner()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'birthDate', value)
        assert result is True
        assert resource.birthDate is not None

    def test_set_path_photo(self):
        resource = Practitioner()
        value = [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'photo', value)
        assert result is True
        assert resource.photo is not None

    def test_set_path_qualification(self):
        resource = Practitioner()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'qualification', value)
        assert result is True
        assert resource.qualification is not None

    def test_set_path_communication(self):
        resource = Practitioner()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'communication', value)
        assert result is True
        assert resource.communication is not None


class TestParsePathPractitioner:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Practitioner.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Practitioner.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Practitioner.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
