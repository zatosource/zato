# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import PractitionerRole


class TestToDictPractitionerRole:

    def test_to_dict_empty(self):
        resource = PractitionerRole()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'PractitionerRole'

    def test_to_dict_with_id(self):
        resource = PractitionerRole()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = PractitionerRole()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, PractitionerRole)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = PractitionerRole()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = PractitionerRole()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = PractitionerRole()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = PractitionerRole()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = PractitionerRole()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = PractitionerRole()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = PractitionerRole()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = PractitionerRole()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = PractitionerRole()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_active(self):
        resource = PractitionerRole()
        resource.active = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'active' in result

    def test_to_dict_period(self):
        resource = PractitionerRole()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'period' in result

    def test_to_dict_practitioner(self):
        resource = PractitionerRole()
        resource.practitioner = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'practitioner' in result

    def test_to_dict_organization(self):
        resource = PractitionerRole()
        resource.organization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'organization' in result

    def test_to_dict_code(self):
        resource = PractitionerRole()
        resource.code = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_specialty(self):
        resource = PractitionerRole()
        resource.specialty = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'specialty' in result

    def test_to_dict_location(self):
        resource = PractitionerRole()
        resource.location = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'location' in result

    def test_to_dict_healthcare_service(self):
        resource = PractitionerRole()
        resource.healthcareService = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'healthcareService' in result

    def test_to_dict_telecom(self):
        resource = PractitionerRole()
        resource.telecom = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'telecom' in result

    def test_to_dict_available_time(self):
        resource = PractitionerRole()
        resource.availableTime = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'availableTime' in result

    def test_to_dict_not_available(self):
        resource = PractitionerRole()
        resource.notAvailable = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'notAvailable' in result

    def test_to_dict_availability_exceptions(self):
        resource = PractitionerRole()
        resource.availabilityExceptions = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'availabilityExceptions' in result

    def test_to_dict_endpoint(self):
        resource = PractitionerRole()
        resource.endpoint = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'endpoint' in result


class TestFromDictPractitionerRole:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'PractitionerRole', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert isinstance(result, PractitionerRole)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'PractitionerRole'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert isinstance(result, PractitionerRole)

    def test_from_dict_id(self):
        data = {'resourceType': 'PractitionerRole', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'PractitionerRole', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'PractitionerRole', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'PractitionerRole', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'PractitionerRole', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'PractitionerRole', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'PractitionerRole', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'PractitionerRole', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'PractitionerRole', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.identifier is not None

    def test_from_dict_active(self):
        data = {'resourceType': 'PractitionerRole', 'active': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.active is not None

    def test_from_dict_period(self):
        data = {'resourceType': 'PractitionerRole', 'period': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.period is not None

    def test_from_dict_practitioner(self):
        data = {'resourceType': 'PractitionerRole', 'practitioner': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.practitioner is not None

    def test_from_dict_organization(self):
        data = {'resourceType': 'PractitionerRole', 'organization': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.organization is not None

    def test_from_dict_code(self):
        data = {'code': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                   'text': 'Test concept'}],
         'resourceType': 'PractitionerRole'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.code is not None

    def test_from_dict_specialty(self):
        data = {'resourceType': 'PractitionerRole',
         'specialty': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                        'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.specialty is not None

    def test_from_dict_location(self):
        data = {'resourceType': 'PractitionerRole', 'location': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.location is not None

    def test_from_dict_healthcare_service(self):
        data = {'resourceType': 'PractitionerRole', 'healthcareService': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.healthcareService is not None

    def test_from_dict_telecom(self):
        data = {'resourceType': 'PractitionerRole', 'telecom': [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.telecom is not None

    def test_from_dict_available_time(self):
        data = {'resourceType': 'PractitionerRole', 'availableTime': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.availableTime is not None

    def test_from_dict_not_available(self):
        data = {'resourceType': 'PractitionerRole', 'notAvailable': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.notAvailable is not None

    def test_from_dict_availability_exceptions(self):
        data = {'resourceType': 'PractitionerRole', 'availabilityExceptions': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.availabilityExceptions is not None

    def test_from_dict_endpoint(self):
        data = {'resourceType': 'PractitionerRole', 'endpoint': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PractitionerRole)
        assert result.endpoint is not None


class TestGetPathPractitionerRole:

    def test_get_path_id(self):
        resource = PractitionerRole()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = PractitionerRole()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = PractitionerRole()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'PractitionerRole.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = PractitionerRole()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = PractitionerRole()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = PractitionerRole()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = PractitionerRole()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = PractitionerRole()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = PractitionerRole()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = PractitionerRole()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = PractitionerRole()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_active(self):
        resource = PractitionerRole()
        resource.active = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'active')
        assert result is not None

    def test_get_path_period(self):
        resource = PractitionerRole()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'period')
        assert result is not None

    def test_get_path_practitioner(self):
        resource = PractitionerRole()
        resource.practitioner = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'practitioner')
        assert result is not None

    def test_get_path_organization(self):
        resource = PractitionerRole()
        resource.organization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'organization')
        assert result is not None

    def test_get_path_code(self):
        resource = PractitionerRole()
        resource.code = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_specialty(self):
        resource = PractitionerRole()
        resource.specialty = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'specialty')
        assert result is not None

    def test_get_path_location(self):
        resource = PractitionerRole()
        resource.location = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'location')
        assert result is not None

    def test_get_path_healthcare_service(self):
        resource = PractitionerRole()
        resource.healthcareService = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'healthcareService')
        assert result is not None

    def test_get_path_telecom(self):
        resource = PractitionerRole()
        resource.telecom = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'telecom')
        assert result is not None

    def test_get_path_available_time(self):
        resource = PractitionerRole()
        resource.availableTime = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'availableTime')
        assert result is not None

    def test_get_path_not_available(self):
        resource = PractitionerRole()
        resource.notAvailable = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'notAvailable')
        assert result is not None

    def test_get_path_availability_exceptions(self):
        resource = PractitionerRole()
        resource.availabilityExceptions = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'availabilityExceptions')
        assert result is not None

    def test_get_path_endpoint(self):
        resource = PractitionerRole()
        resource.endpoint = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'endpoint')
        assert result is not None


class TestSetPathPractitionerRole:

    def test_set_path_id(self):
        resource = PractitionerRole()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = PractitionerRole()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'PractitionerRole.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = PractitionerRole()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = PractitionerRole()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = PractitionerRole()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = PractitionerRole()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = PractitionerRole()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = PractitionerRole()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = PractitionerRole()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = PractitionerRole()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_active(self):
        resource = PractitionerRole()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'active', value)
        assert result is True
        assert resource.active is not None

    def test_set_path_period(self):
        resource = PractitionerRole()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'period', value)
        assert result is True
        assert resource.period is not None

    def test_set_path_practitioner(self):
        resource = PractitionerRole()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'practitioner', value)
        assert result is True
        assert resource.practitioner is not None

    def test_set_path_organization(self):
        resource = PractitionerRole()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'organization', value)
        assert result is True
        assert resource.organization is not None

    def test_set_path_code(self):
        resource = PractitionerRole()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_specialty(self):
        resource = PractitionerRole()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'specialty', value)
        assert result is True
        assert resource.specialty is not None

    def test_set_path_location(self):
        resource = PractitionerRole()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'location', value)
        assert result is True
        assert resource.location is not None

    def test_set_path_healthcare_service(self):
        resource = PractitionerRole()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'healthcareService', value)
        assert result is True
        assert resource.healthcareService is not None

    def test_set_path_telecom(self):
        resource = PractitionerRole()
        value = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'telecom', value)
        assert result is True
        assert resource.telecom is not None

    def test_set_path_available_time(self):
        resource = PractitionerRole()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'availableTime', value)
        assert result is True
        assert resource.availableTime is not None

    def test_set_path_not_available(self):
        resource = PractitionerRole()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'notAvailable', value)
        assert result is True
        assert resource.notAvailable is not None

    def test_set_path_availability_exceptions(self):
        resource = PractitionerRole()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'availabilityExceptions', value)
        assert result is True
        assert resource.availabilityExceptions is not None

    def test_set_path_endpoint(self):
        resource = PractitionerRole()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'endpoint', value)
        assert result is True
        assert resource.endpoint is not None


class TestParsePathPractitionerRole:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('PractitionerRole.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('PractitionerRole.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('PractitionerRole.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
