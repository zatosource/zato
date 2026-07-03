# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Patient


class TestToDictPatient:

    def test_to_dict_empty(self):
        resource = Patient()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Patient'

    def test_to_dict_with_id(self):
        resource = Patient()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Patient()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Patient)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Patient()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Patient()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Patient()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Patient()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Patient()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Patient()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Patient()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Patient()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Patient()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_active(self):
        resource = Patient()
        resource.active = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'active' in result

    def test_to_dict_name(self):
        resource = Patient()
        resource.name = [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_telecom(self):
        resource = Patient()
        resource.telecom = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'telecom' in result

    def test_to_dict_gender(self):
        resource = Patient()
        resource.gender = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'gender' in result

    def test_to_dict_birth_date(self):
        resource = Patient()
        resource.birthDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'birthDate' in result

    def test_to_dict_address(self):
        resource = Patient()
        resource.address = [{'use': 'home', 'line': ['123 Main St'], 'city': 'Boston', 'state': 'MA', 'postalCode': '02101', 'country': 'USA'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'address' in result

    def test_to_dict_marital_status(self):
        resource = Patient()
        resource.maritalStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'maritalStatus' in result

    def test_to_dict_photo(self):
        resource = Patient()
        resource.photo = [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'photo' in result

    def test_to_dict_contact(self):
        resource = Patient()
        resource.contact = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_communication(self):
        resource = Patient()
        resource.communication = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'communication' in result

    def test_to_dict_general_practitioner(self):
        resource = Patient()
        resource.generalPractitioner = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'generalPractitioner' in result

    def test_to_dict_managing_organization(self):
        resource = Patient()
        resource.managingOrganization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'managingOrganization' in result

    def test_to_dict_link(self):
        resource = Patient()
        resource.link = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'link' in result


class TestFromDictPatient:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Patient', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert isinstance(result, Patient)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Patient'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert isinstance(result, Patient)

    def test_from_dict_id(self):
        data = {'resourceType': 'Patient', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Patient', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Patient', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Patient', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Patient', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Patient', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Patient', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Patient', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Patient', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.identifier is not None

    def test_from_dict_active(self):
        data = {'resourceType': 'Patient', 'active': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.active is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'Patient', 'name': [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.name is not None

    def test_from_dict_telecom(self):
        data = {'resourceType': 'Patient', 'telecom': [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.telecom is not None

    def test_from_dict_gender(self):
        data = {'resourceType': 'Patient', 'gender': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.gender is not None

    def test_from_dict_birth_date(self):
        data = {'resourceType': 'Patient', 'birthDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.birthDate is not None

    def test_from_dict_address(self):
        data = {'address': [{'city': 'Boston',
                      'country': 'USA',
                      'line': ['123 Main St'],
                      'postalCode': '02101',
                      'state': 'MA',
                      'use': 'home'}],
         'resourceType': 'Patient'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.address is not None

    def test_from_dict_marital_status(self):
        data = {'maritalStatus': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'},
         'resourceType': 'Patient'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.maritalStatus is not None

    def test_from_dict_photo(self):
        data = {'resourceType': 'Patient', 'photo': [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.photo is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'Patient', 'contact': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.contact is not None

    def test_from_dict_communication(self):
        data = {'resourceType': 'Patient', 'communication': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.communication is not None

    def test_from_dict_general_practitioner(self):
        data = {'resourceType': 'Patient', 'generalPractitioner': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.generalPractitioner is not None

    def test_from_dict_managing_organization(self):
        data = {'resourceType': 'Patient', 'managingOrganization': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.managingOrganization is not None

    def test_from_dict_link(self):
        data = {'resourceType': 'Patient', 'link': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Patient)
        assert result.link is not None


class TestGetPathPatient:

    def test_get_path_id(self):
        resource = Patient()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Patient()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Patient()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Patient.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Patient()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Patient()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Patient()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Patient()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Patient()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Patient()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Patient()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Patient()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_active(self):
        resource = Patient()
        resource.active = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'active')
        assert result is not None

    def test_get_path_name(self):
        resource = Patient()
        resource.name = [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_telecom(self):
        resource = Patient()
        resource.telecom = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'telecom')
        assert result is not None

    def test_get_path_gender(self):
        resource = Patient()
        resource.gender = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'gender')
        assert result is not None

    def test_get_path_birth_date(self):
        resource = Patient()
        resource.birthDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'birthDate')
        assert result is not None

    def test_get_path_address(self):
        resource = Patient()
        resource.address = [{'use': 'home', 'line': ['123 Main St'], 'city': 'Boston', 'state': 'MA', 'postalCode': '02101', 'country': 'USA'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'address')
        assert result is not None

    def test_get_path_marital_status(self):
        resource = Patient()
        resource.maritalStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'maritalStatus')
        assert result is not None

    def test_get_path_photo(self):
        resource = Patient()
        resource.photo = [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'photo')
        assert result is not None

    def test_get_path_contact(self):
        resource = Patient()
        resource.contact = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_communication(self):
        resource = Patient()
        resource.communication = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'communication')
        assert result is not None

    def test_get_path_general_practitioner(self):
        resource = Patient()
        resource.generalPractitioner = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'generalPractitioner')
        assert result is not None

    def test_get_path_managing_organization(self):
        resource = Patient()
        resource.managingOrganization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'managingOrganization')
        assert result is not None

    def test_get_path_link(self):
        resource = Patient()
        resource.link = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'link')
        assert result is not None


class TestSetPathPatient:

    def test_set_path_id(self):
        resource = Patient()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Patient()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Patient.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Patient()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Patient()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Patient()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Patient()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Patient()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Patient()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Patient()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Patient()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_active(self):
        resource = Patient()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'active', value)
        assert result is True
        assert resource.active is not None

    def test_set_path_name(self):
        resource = Patient()
        value = [{'family': 'Smith', 'given': ['John', 'Q'], 'prefix': ['Mr']}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_telecom(self):
        resource = Patient()
        value = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'telecom', value)
        assert result is True
        assert resource.telecom is not None

    def test_set_path_gender(self):
        resource = Patient()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'gender', value)
        assert result is True
        assert resource.gender is not None

    def test_set_path_birth_date(self):
        resource = Patient()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'birthDate', value)
        assert result is True
        assert resource.birthDate is not None

    def test_set_path_address(self):
        resource = Patient()
        value = [{'use': 'home', 'line': ['123 Main St'], 'city': 'Boston', 'state': 'MA', 'postalCode': '02101', 'country': 'USA'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'address', value)
        assert result is True
        assert resource.address is not None

    def test_set_path_marital_status(self):
        resource = Patient()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'maritalStatus', value)
        assert result is True
        assert resource.maritalStatus is not None

    def test_set_path_photo(self):
        resource = Patient()
        value = [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'photo', value)
        assert result is True
        assert resource.photo is not None

    def test_set_path_contact(self):
        resource = Patient()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_communication(self):
        resource = Patient()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'communication', value)
        assert result is True
        assert resource.communication is not None

    def test_set_path_general_practitioner(self):
        resource = Patient()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'generalPractitioner', value)
        assert result is True
        assert resource.generalPractitioner is not None

    def test_set_path_managing_organization(self):
        resource = Patient()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'managingOrganization', value)
        assert result is True
        assert resource.managingOrganization is not None

    def test_set_path_link(self):
        resource = Patient()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'link', value)
        assert result is True
        assert resource.link is not None


class TestParsePathPatient:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Patient.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Patient.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Patient.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
