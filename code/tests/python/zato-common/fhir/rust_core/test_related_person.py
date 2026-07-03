# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import RelatedPerson


class TestToDictRelatedPerson:

    def test_to_dict_empty(self):
        resource = RelatedPerson()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'RelatedPerson'

    def test_to_dict_with_id(self):
        resource = RelatedPerson()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = RelatedPerson()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, RelatedPerson)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = RelatedPerson()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = RelatedPerson()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = RelatedPerson()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = RelatedPerson()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = RelatedPerson()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = RelatedPerson()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = RelatedPerson()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = RelatedPerson()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = RelatedPerson()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_active(self):
        resource = RelatedPerson()
        resource.active = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'active' in result

    def test_to_dict_patient(self):
        resource = RelatedPerson()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_relationship(self):
        resource = RelatedPerson()
        resource.relationship = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relationship' in result

    def test_to_dict_name(self):
        resource = RelatedPerson()
        resource.name = [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_telecom(self):
        resource = RelatedPerson()
        resource.telecom = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'telecom' in result

    def test_to_dict_gender(self):
        resource = RelatedPerson()
        resource.gender = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'gender' in result

    def test_to_dict_birth_date(self):
        resource = RelatedPerson()
        resource.birthDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'birthDate' in result

    def test_to_dict_address(self):
        resource = RelatedPerson()
        resource.address = [{'use': 'home', 'line': ['123 Main St'], 'city': 'Boston', 'state': 'MA', 'postalCode': '02101', 'country': 'USA'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'address' in result

    def test_to_dict_photo(self):
        resource = RelatedPerson()
        resource.photo = [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'photo' in result

    def test_to_dict_period(self):
        resource = RelatedPerson()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'period' in result

    def test_to_dict_communication(self):
        resource = RelatedPerson()
        resource.communication = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'communication' in result


class TestFromDictRelatedPerson:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'RelatedPerson', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert isinstance(result, RelatedPerson)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'RelatedPerson'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert isinstance(result, RelatedPerson)

    def test_from_dict_id(self):
        data = {'resourceType': 'RelatedPerson', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'RelatedPerson', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'RelatedPerson', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'RelatedPerson', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'RelatedPerson', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'RelatedPerson', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'RelatedPerson', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'RelatedPerson', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'RelatedPerson', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.identifier is not None

    def test_from_dict_active(self):
        data = {'resourceType': 'RelatedPerson', 'active': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.active is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'RelatedPerson', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.patient is not None

    def test_from_dict_relationship(self):
        data = {'relationship': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'RelatedPerson'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.relationship is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'RelatedPerson', 'name': [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.name is not None

    def test_from_dict_telecom(self):
        data = {'resourceType': 'RelatedPerson', 'telecom': [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.telecom is not None

    def test_from_dict_gender(self):
        data = {'resourceType': 'RelatedPerson', 'gender': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.gender is not None

    def test_from_dict_birth_date(self):
        data = {'resourceType': 'RelatedPerson', 'birthDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.birthDate is not None

    def test_from_dict_address(self):
        data = {'address': [{'city': 'Boston',
                      'country': 'USA',
                      'line': ['123 Main St'],
                      'postalCode': '02101',
                      'state': 'MA',
                      'use': 'home'}],
         'resourceType': 'RelatedPerson'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.address is not None

    def test_from_dict_photo(self):
        data = {'resourceType': 'RelatedPerson', 'photo': [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.photo is not None

    def test_from_dict_period(self):
        data = {'resourceType': 'RelatedPerson', 'period': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.period is not None

    def test_from_dict_communication(self):
        data = {'resourceType': 'RelatedPerson', 'communication': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RelatedPerson)
        assert result.communication is not None


class TestGetPathRelatedPerson:

    def test_get_path_id(self):
        resource = RelatedPerson()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = RelatedPerson()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = RelatedPerson()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'RelatedPerson.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = RelatedPerson()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = RelatedPerson()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = RelatedPerson()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = RelatedPerson()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = RelatedPerson()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = RelatedPerson()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = RelatedPerson()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = RelatedPerson()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_active(self):
        resource = RelatedPerson()
        resource.active = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'active')
        assert result is not None

    def test_get_path_patient(self):
        resource = RelatedPerson()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_relationship(self):
        resource = RelatedPerson()
        resource.relationship = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relationship')
        assert result is not None

    def test_get_path_name(self):
        resource = RelatedPerson()
        resource.name = [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_telecom(self):
        resource = RelatedPerson()
        resource.telecom = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'telecom')
        assert result is not None

    def test_get_path_gender(self):
        resource = RelatedPerson()
        resource.gender = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'gender')
        assert result is not None

    def test_get_path_birth_date(self):
        resource = RelatedPerson()
        resource.birthDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'birthDate')
        assert result is not None

    def test_get_path_address(self):
        resource = RelatedPerson()
        resource.address = [{'use': 'home', 'line': ['123 Main St'], 'city': 'Boston', 'state': 'MA', 'postalCode': '02101', 'country': 'USA'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'address')
        assert result is not None

    def test_get_path_photo(self):
        resource = RelatedPerson()
        resource.photo = [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'photo')
        assert result is not None

    def test_get_path_period(self):
        resource = RelatedPerson()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'period')
        assert result is not None

    def test_get_path_communication(self):
        resource = RelatedPerson()
        resource.communication = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'communication')
        assert result is not None


class TestSetPathRelatedPerson:

    def test_set_path_id(self):
        resource = RelatedPerson()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = RelatedPerson()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'RelatedPerson.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = RelatedPerson()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = RelatedPerson()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = RelatedPerson()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = RelatedPerson()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = RelatedPerson()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = RelatedPerson()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = RelatedPerson()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = RelatedPerson()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_active(self):
        resource = RelatedPerson()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'active', value)
        assert result is True
        assert resource.active is not None

    def test_set_path_patient(self):
        resource = RelatedPerson()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_relationship(self):
        resource = RelatedPerson()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relationship', value)
        assert result is True
        assert resource.relationship is not None

    def test_set_path_name(self):
        resource = RelatedPerson()
        value = [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_telecom(self):
        resource = RelatedPerson()
        value = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'telecom', value)
        assert result is True
        assert resource.telecom is not None

    def test_set_path_gender(self):
        resource = RelatedPerson()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'gender', value)
        assert result is True
        assert resource.gender is not None

    def test_set_path_birth_date(self):
        resource = RelatedPerson()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'birthDate', value)
        assert result is True
        assert resource.birthDate is not None

    def test_set_path_address(self):
        resource = RelatedPerson()
        value = [{'use': 'home', 'line': ['123 Main St'], 'city': 'Boston', 'state': 'MA', 'postalCode': '02101', 'country': 'USA'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'address', value)
        assert result is True
        assert resource.address is not None

    def test_set_path_photo(self):
        resource = RelatedPerson()
        value = [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'photo', value)
        assert result is True
        assert resource.photo is not None

    def test_set_path_period(self):
        resource = RelatedPerson()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'period', value)
        assert result is True
        assert resource.period is not None

    def test_set_path_communication(self):
        resource = RelatedPerson()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'communication', value)
        assert result is True
        assert resource.communication is not None


class TestParsePathRelatedPerson:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('RelatedPerson.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('RelatedPerson.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('RelatedPerson.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
