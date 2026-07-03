# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Person


class TestToDictPerson:

    def test_to_dict_empty(self):
        resource = Person()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Person'

    def test_to_dict_with_id(self):
        resource = Person()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Person()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Person)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Person()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Person()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Person()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Person()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Person()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Person()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Person()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Person()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Person()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_name(self):
        resource = Person()
        resource.name = [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_telecom(self):
        resource = Person()
        resource.telecom = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'telecom' in result

    def test_to_dict_gender(self):
        resource = Person()
        resource.gender = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'gender' in result

    def test_to_dict_birth_date(self):
        resource = Person()
        resource.birthDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'birthDate' in result

    def test_to_dict_address(self):
        resource = Person()
        resource.address = [{'use': 'home', 'line': ['123 Main St'], 'city': 'Boston', 'state': 'MA', 'postalCode': '02101', 'country': 'USA'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'address' in result

    def test_to_dict_photo(self):
        resource = Person()
        resource.photo = {'contentType': 'text/plain', 'data': 'SGVsbG8='}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'photo' in result

    def test_to_dict_managing_organization(self):
        resource = Person()
        resource.managingOrganization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'managingOrganization' in result

    def test_to_dict_active(self):
        resource = Person()
        resource.active = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'active' in result

    def test_to_dict_link(self):
        resource = Person()
        resource.link = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'link' in result


class TestFromDictPerson:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Person', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert isinstance(result, Person)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Person'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert isinstance(result, Person)

    def test_from_dict_id(self):
        data = {'resourceType': 'Person', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Person', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Person', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Person', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Person', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Person', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Person', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Person', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Person', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.identifier is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'Person', 'name': [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.name is not None

    def test_from_dict_telecom(self):
        data = {'resourceType': 'Person', 'telecom': [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.telecom is not None

    def test_from_dict_gender(self):
        data = {'resourceType': 'Person', 'gender': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.gender is not None

    def test_from_dict_birth_date(self):
        data = {'resourceType': 'Person', 'birthDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.birthDate is not None

    def test_from_dict_address(self):
        data = {'address': [{'city': 'Boston',
                      'country': 'USA',
                      'line': ['123 Main St'],
                      'postalCode': '02101',
                      'state': 'MA',
                      'use': 'home'}],
         'resourceType': 'Person'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.address is not None

    def test_from_dict_photo(self):
        data = {'resourceType': 'Person', 'photo': {'contentType': 'text/plain', 'data': 'SGVsbG8='}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.photo is not None

    def test_from_dict_managing_organization(self):
        data = {'resourceType': 'Person', 'managingOrganization': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.managingOrganization is not None

    def test_from_dict_active(self):
        data = {'resourceType': 'Person', 'active': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.active is not None

    def test_from_dict_link(self):
        data = {'resourceType': 'Person', 'link': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Person)
        assert result.link is not None


class TestGetPathPerson:

    def test_get_path_id(self):
        resource = Person()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Person()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Person()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Person.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Person()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Person()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Person()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Person()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Person()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Person()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Person()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Person()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_name(self):
        resource = Person()
        resource.name = [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_telecom(self):
        resource = Person()
        resource.telecom = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'telecom')
        assert result is not None

    def test_get_path_gender(self):
        resource = Person()
        resource.gender = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'gender')
        assert result is not None

    def test_get_path_birth_date(self):
        resource = Person()
        resource.birthDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'birthDate')
        assert result is not None

    def test_get_path_address(self):
        resource = Person()
        resource.address = [{'use': 'home', 'line': ['123 Main St'], 'city': 'Boston', 'state': 'MA', 'postalCode': '02101', 'country': 'USA'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'address')
        assert result is not None

    def test_get_path_photo(self):
        resource = Person()
        resource.photo = {'contentType': 'text/plain', 'data': 'SGVsbG8='}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'photo')
        assert result is not None

    def test_get_path_managing_organization(self):
        resource = Person()
        resource.managingOrganization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'managingOrganization')
        assert result is not None

    def test_get_path_active(self):
        resource = Person()
        resource.active = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'active')
        assert result is not None

    def test_get_path_link(self):
        resource = Person()
        resource.link = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'link')
        assert result is not None


class TestSetPathPerson:

    def test_set_path_id(self):
        resource = Person()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Person()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Person.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Person()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Person()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Person()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Person()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Person()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Person()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Person()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Person()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_name(self):
        resource = Person()
        value = [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_telecom(self):
        resource = Person()
        value = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'telecom', value)
        assert result is True
        assert resource.telecom is not None

    def test_set_path_gender(self):
        resource = Person()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'gender', value)
        assert result is True
        assert resource.gender is not None

    def test_set_path_birth_date(self):
        resource = Person()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'birthDate', value)
        assert result is True
        assert resource.birthDate is not None

    def test_set_path_address(self):
        resource = Person()
        value = [{'use': 'home', 'line': ['123 Main St'], 'city': 'Boston', 'state': 'MA', 'postalCode': '02101', 'country': 'USA'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'address', value)
        assert result is True
        assert resource.address is not None

    def test_set_path_photo(self):
        resource = Person()
        value = {'contentType': 'text/plain', 'data': 'SGVsbG8='}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'photo', value)
        assert result is True
        assert resource.photo is not None

    def test_set_path_managing_organization(self):
        resource = Person()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'managingOrganization', value)
        assert result is True
        assert resource.managingOrganization is not None

    def test_set_path_active(self):
        resource = Person()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'active', value)
        assert result is True
        assert resource.active is not None

    def test_set_path_link(self):
        resource = Person()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'link', value)
        assert result is True
        assert resource.link is not None


class TestParsePathPerson:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Person.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Person.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Person.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
