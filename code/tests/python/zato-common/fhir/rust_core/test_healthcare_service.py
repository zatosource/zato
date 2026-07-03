# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import HealthcareService


class TestToDictHealthcareService:

    def test_to_dict_empty(self):
        resource = HealthcareService()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'HealthcareService'

    def test_to_dict_with_id(self):
        resource = HealthcareService()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = HealthcareService()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, HealthcareService)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = HealthcareService()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = HealthcareService()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = HealthcareService()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = HealthcareService()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = HealthcareService()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = HealthcareService()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = HealthcareService()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = HealthcareService()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = HealthcareService()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_active(self):
        resource = HealthcareService()
        resource.active = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'active' in result

    def test_to_dict_provided_by(self):
        resource = HealthcareService()
        resource.providedBy = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'providedBy' in result

    def test_to_dict_category(self):
        resource = HealthcareService()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_type(self):
        resource = HealthcareService()
        resource.type_ = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_specialty(self):
        resource = HealthcareService()
        resource.specialty = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'specialty' in result

    def test_to_dict_location(self):
        resource = HealthcareService()
        resource.location = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'location' in result

    def test_to_dict_name(self):
        resource = HealthcareService()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_comment(self):
        resource = HealthcareService()
        resource.comment = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'comment' in result

    def test_to_dict_extra_details(self):
        resource = HealthcareService()
        resource.extraDetails = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extraDetails' in result

    def test_to_dict_photo(self):
        resource = HealthcareService()
        resource.photo = {'contentType': 'text/plain', 'data': 'SGVsbG8='}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'photo' in result

    def test_to_dict_telecom(self):
        resource = HealthcareService()
        resource.telecom = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'telecom' in result

    def test_to_dict_coverage_area(self):
        resource = HealthcareService()
        resource.coverageArea = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'coverageArea' in result

    def test_to_dict_service_provision_code(self):
        resource = HealthcareService()
        resource.serviceProvisionCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'serviceProvisionCode' in result

    def test_to_dict_eligibility(self):
        resource = HealthcareService()
        resource.eligibility = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'eligibility' in result

    def test_to_dict_program(self):
        resource = HealthcareService()
        resource.program = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'program' in result

    def test_to_dict_characteristic(self):
        resource = HealthcareService()
        resource.characteristic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'characteristic' in result

    def test_to_dict_communication(self):
        resource = HealthcareService()
        resource.communication = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'communication' in result

    def test_to_dict_referral_method(self):
        resource = HealthcareService()
        resource.referralMethod = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'referralMethod' in result

    def test_to_dict_appointment_required(self):
        resource = HealthcareService()
        resource.appointmentRequired = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'appointmentRequired' in result

    def test_to_dict_available_time(self):
        resource = HealthcareService()
        resource.availableTime = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'availableTime' in result

    def test_to_dict_not_available(self):
        resource = HealthcareService()
        resource.notAvailable = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'notAvailable' in result

    def test_to_dict_availability_exceptions(self):
        resource = HealthcareService()
        resource.availabilityExceptions = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'availabilityExceptions' in result

    def test_to_dict_endpoint(self):
        resource = HealthcareService()
        resource.endpoint = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'endpoint' in result


class TestFromDictHealthcareService:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'HealthcareService', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert isinstance(result, HealthcareService)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'HealthcareService'}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert isinstance(result, HealthcareService)

    def test_from_dict_id(self):
        data = {'resourceType': 'HealthcareService', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'HealthcareService', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'HealthcareService', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'HealthcareService', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'HealthcareService', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'HealthcareService', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'HealthcareService', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'HealthcareService', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'HealthcareService', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.identifier is not None

    def test_from_dict_active(self):
        data = {'resourceType': 'HealthcareService', 'active': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.active is not None

    def test_from_dict_provided_by(self):
        data = {'resourceType': 'HealthcareService', 'providedBy': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.providedBy is not None

    def test_from_dict_category(self):
        data = {'category': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'HealthcareService'}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.category is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'HealthcareService',
         'type': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                   'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.type_ is not None

    def test_from_dict_specialty(self):
        data = {'resourceType': 'HealthcareService',
         'specialty': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                        'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.specialty is not None

    def test_from_dict_location(self):
        data = {'resourceType': 'HealthcareService', 'location': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.location is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'HealthcareService', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.name is not None

    def test_from_dict_comment(self):
        data = {'resourceType': 'HealthcareService', 'comment': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.comment is not None

    def test_from_dict_extra_details(self):
        data = {'resourceType': 'HealthcareService', 'extraDetails': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.extraDetails is not None

    def test_from_dict_photo(self):
        data = {'resourceType': 'HealthcareService', 'photo': {'contentType': 'text/plain', 'data': 'SGVsbG8='}}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.photo is not None

    def test_from_dict_telecom(self):
        data = {'resourceType': 'HealthcareService', 'telecom': [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.telecom is not None

    def test_from_dict_coverage_area(self):
        data = {'resourceType': 'HealthcareService', 'coverageArea': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.coverageArea is not None

    def test_from_dict_service_provision_code(self):
        data = {'resourceType': 'HealthcareService',
         'serviceProvisionCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                   'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.serviceProvisionCode is not None

    def test_from_dict_eligibility(self):
        data = {'resourceType': 'HealthcareService', 'eligibility': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.eligibility is not None

    def test_from_dict_program(self):
        data = {'program': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'}],
         'resourceType': 'HealthcareService'}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.program is not None

    def test_from_dict_characteristic(self):
        data = {'characteristic': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                             'text': 'Test concept'}],
         'resourceType': 'HealthcareService'}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.characteristic is not None

    def test_from_dict_communication(self):
        data = {'communication': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                            'text': 'Test concept'}],
         'resourceType': 'HealthcareService'}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.communication is not None

    def test_from_dict_referral_method(self):
        data = {'referralMethod': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                             'text': 'Test concept'}],
         'resourceType': 'HealthcareService'}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.referralMethod is not None

    def test_from_dict_appointment_required(self):
        data = {'resourceType': 'HealthcareService', 'appointmentRequired': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.appointmentRequired is not None

    def test_from_dict_available_time(self):
        data = {'resourceType': 'HealthcareService', 'availableTime': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.availableTime is not None

    def test_from_dict_not_available(self):
        data = {'resourceType': 'HealthcareService', 'notAvailable': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.notAvailable is not None

    def test_from_dict_availability_exceptions(self):
        data = {'resourceType': 'HealthcareService', 'availabilityExceptions': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.availabilityExceptions is not None

    def test_from_dict_endpoint(self):
        data = {'resourceType': 'HealthcareService', 'endpoint': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, HealthcareService)
        assert result.endpoint is not None


class TestGetPathHealthcareService:

    def test_get_path_id(self):
        resource = HealthcareService()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = HealthcareService()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = HealthcareService()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'HealthcareService.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = HealthcareService()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = HealthcareService()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = HealthcareService()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = HealthcareService()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = HealthcareService()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = HealthcareService()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = HealthcareService()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = HealthcareService()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_active(self):
        resource = HealthcareService()
        resource.active = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'active')
        assert result is not None

    def test_get_path_provided_by(self):
        resource = HealthcareService()
        resource.providedBy = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'providedBy')
        assert result is not None

    def test_get_path_category(self):
        resource = HealthcareService()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_type(self):
        resource = HealthcareService()
        resource.type_ = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_specialty(self):
        resource = HealthcareService()
        resource.specialty = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'specialty')
        assert result is not None

    def test_get_path_location(self):
        resource = HealthcareService()
        resource.location = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'location')
        assert result is not None

    def test_get_path_name(self):
        resource = HealthcareService()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_comment(self):
        resource = HealthcareService()
        resource.comment = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'comment')
        assert result is not None

    def test_get_path_extra_details(self):
        resource = HealthcareService()
        resource.extraDetails = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extraDetails')
        assert result is not None

    def test_get_path_photo(self):
        resource = HealthcareService()
        resource.photo = {'contentType': 'text/plain', 'data': 'SGVsbG8='}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'photo')
        assert result is not None

    def test_get_path_telecom(self):
        resource = HealthcareService()
        resource.telecom = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'telecom')
        assert result is not None

    def test_get_path_coverage_area(self):
        resource = HealthcareService()
        resource.coverageArea = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'coverageArea')
        assert result is not None

    def test_get_path_service_provision_code(self):
        resource = HealthcareService()
        resource.serviceProvisionCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'serviceProvisionCode')
        assert result is not None

    def test_get_path_eligibility(self):
        resource = HealthcareService()
        resource.eligibility = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'eligibility')
        assert result is not None

    def test_get_path_program(self):
        resource = HealthcareService()
        resource.program = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'program')
        assert result is not None

    def test_get_path_characteristic(self):
        resource = HealthcareService()
        resource.characteristic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'characteristic')
        assert result is not None

    def test_get_path_communication(self):
        resource = HealthcareService()
        resource.communication = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'communication')
        assert result is not None

    def test_get_path_referral_method(self):
        resource = HealthcareService()
        resource.referralMethod = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'referralMethod')
        assert result is not None

    def test_get_path_appointment_required(self):
        resource = HealthcareService()
        resource.appointmentRequired = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'appointmentRequired')
        assert result is not None

    def test_get_path_available_time(self):
        resource = HealthcareService()
        resource.availableTime = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'availableTime')
        assert result is not None

    def test_get_path_not_available(self):
        resource = HealthcareService()
        resource.notAvailable = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'notAvailable')
        assert result is not None

    def test_get_path_availability_exceptions(self):
        resource = HealthcareService()
        resource.availabilityExceptions = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'availabilityExceptions')
        assert result is not None

    def test_get_path_endpoint(self):
        resource = HealthcareService()
        resource.endpoint = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'endpoint')
        assert result is not None


class TestSetPathHealthcareService:

    def test_set_path_id(self):
        resource = HealthcareService()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = HealthcareService()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'HealthcareService.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = HealthcareService()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = HealthcareService()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = HealthcareService()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = HealthcareService()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = HealthcareService()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = HealthcareService()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = HealthcareService()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = HealthcareService()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_active(self):
        resource = HealthcareService()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'active', value)
        assert result is True
        assert resource.active is not None

    def test_set_path_provided_by(self):
        resource = HealthcareService()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'providedBy', value)
        assert result is True
        assert resource.providedBy is not None

    def test_set_path_category(self):
        resource = HealthcareService()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_type(self):
        resource = HealthcareService()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_specialty(self):
        resource = HealthcareService()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'specialty', value)
        assert result is True
        assert resource.specialty is not None

    def test_set_path_location(self):
        resource = HealthcareService()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'location', value)
        assert result is True
        assert resource.location is not None

    def test_set_path_name(self):
        resource = HealthcareService()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_comment(self):
        resource = HealthcareService()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'comment', value)
        assert result is True
        assert resource.comment is not None

    def test_set_path_extra_details(self):
        resource = HealthcareService()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extraDetails', value)
        assert result is True
        assert resource.extraDetails is not None

    def test_set_path_photo(self):
        resource = HealthcareService()
        value = {'contentType': 'text/plain', 'data': 'SGVsbG8='}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'photo', value)
        assert result is True
        assert resource.photo is not None

    def test_set_path_telecom(self):
        resource = HealthcareService()
        value = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'telecom', value)
        assert result is True
        assert resource.telecom is not None

    def test_set_path_coverage_area(self):
        resource = HealthcareService()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'coverageArea', value)
        assert result is True
        assert resource.coverageArea is not None

    def test_set_path_service_provision_code(self):
        resource = HealthcareService()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'serviceProvisionCode', value)
        assert result is True
        assert resource.serviceProvisionCode is not None

    def test_set_path_eligibility(self):
        resource = HealthcareService()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'eligibility', value)
        assert result is True
        assert resource.eligibility is not None

    def test_set_path_program(self):
        resource = HealthcareService()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'program', value)
        assert result is True
        assert resource.program is not None

    def test_set_path_characteristic(self):
        resource = HealthcareService()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'characteristic', value)
        assert result is True
        assert resource.characteristic is not None

    def test_set_path_communication(self):
        resource = HealthcareService()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'communication', value)
        assert result is True
        assert resource.communication is not None

    def test_set_path_referral_method(self):
        resource = HealthcareService()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'referralMethod', value)
        assert result is True
        assert resource.referralMethod is not None

    def test_set_path_appointment_required(self):
        resource = HealthcareService()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'appointmentRequired', value)
        assert result is True
        assert resource.appointmentRequired is not None

    def test_set_path_available_time(self):
        resource = HealthcareService()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'availableTime', value)
        assert result is True
        assert resource.availableTime is not None

    def test_set_path_not_available(self):
        resource = HealthcareService()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'notAvailable', value)
        assert result is True
        assert resource.notAvailable is not None

    def test_set_path_availability_exceptions(self):
        resource = HealthcareService()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'availabilityExceptions', value)
        assert result is True
        assert resource.availabilityExceptions is not None

    def test_set_path_endpoint(self):
        resource = HealthcareService()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'endpoint', value)
        assert result is True
        assert resource.endpoint is not None


class TestParsePathHealthcareService:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('HealthcareService.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('HealthcareService.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('HealthcareService.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
