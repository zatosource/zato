# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import CoverageEligibilityResponse


class TestToDictCoverageEligibilityResponse:

    def test_to_dict_empty(self):
        resource = CoverageEligibilityResponse()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'CoverageEligibilityResponse'

    def test_to_dict_with_id(self):
        resource = CoverageEligibilityResponse()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = CoverageEligibilityResponse()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, CoverageEligibilityResponse)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = CoverageEligibilityResponse()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = CoverageEligibilityResponse()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = CoverageEligibilityResponse()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = CoverageEligibilityResponse()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = CoverageEligibilityResponse()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = CoverageEligibilityResponse()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = CoverageEligibilityResponse()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = CoverageEligibilityResponse()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = CoverageEligibilityResponse()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = CoverageEligibilityResponse()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_purpose(self):
        resource = CoverageEligibilityResponse()
        resource.purpose = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_patient(self):
        resource = CoverageEligibilityResponse()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_created(self):
        resource = CoverageEligibilityResponse()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'created' in result

    def test_to_dict_requestor(self):
        resource = CoverageEligibilityResponse()
        resource.requestor = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'requestor' in result

    def test_to_dict_request(self):
        resource = CoverageEligibilityResponse()
        resource.request = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'request' in result

    def test_to_dict_outcome(self):
        resource = CoverageEligibilityResponse()
        resource.outcome = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'outcome' in result

    def test_to_dict_disposition(self):
        resource = CoverageEligibilityResponse()
        resource.disposition = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'disposition' in result

    def test_to_dict_insurer(self):
        resource = CoverageEligibilityResponse()
        resource.insurer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'insurer' in result

    def test_to_dict_insurance(self):
        resource = CoverageEligibilityResponse()
        resource.insurance = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'insurance' in result

    def test_to_dict_pre_auth_ref(self):
        resource = CoverageEligibilityResponse()
        resource.preAuthRef = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'preAuthRef' in result

    def test_to_dict_form(self):
        resource = CoverageEligibilityResponse()
        resource.form = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'form' in result

    def test_to_dict_error(self):
        resource = CoverageEligibilityResponse()
        resource.error = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'error' in result


class TestFromDictCoverageEligibilityResponse:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert isinstance(result, CoverageEligibilityResponse)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'CoverageEligibilityResponse'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert isinstance(result, CoverageEligibilityResponse)

    def test_from_dict_id(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.status is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'purpose': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.purpose is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.patient is not None

    def test_from_dict_created(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'created': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.created is not None

    def test_from_dict_requestor(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'requestor': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.requestor is not None

    def test_from_dict_request(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'request': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.request is not None

    def test_from_dict_outcome(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'outcome': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.outcome is not None

    def test_from_dict_disposition(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'disposition': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.disposition is not None

    def test_from_dict_insurer(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'insurer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.insurer is not None

    def test_from_dict_insurance(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'insurance': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.insurance is not None

    def test_from_dict_pre_auth_ref(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'preAuthRef': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.preAuthRef is not None

    def test_from_dict_form(self):
        data = {'form': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'CoverageEligibilityResponse'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.form is not None

    def test_from_dict_error(self):
        data = {'resourceType': 'CoverageEligibilityResponse', 'error': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityResponse)
        assert result.error is not None


class TestGetPathCoverageEligibilityResponse:

    def test_get_path_id(self):
        resource = CoverageEligibilityResponse()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = CoverageEligibilityResponse()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = CoverageEligibilityResponse()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'CoverageEligibilityResponse.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = CoverageEligibilityResponse()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = CoverageEligibilityResponse()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = CoverageEligibilityResponse()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = CoverageEligibilityResponse()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = CoverageEligibilityResponse()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = CoverageEligibilityResponse()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = CoverageEligibilityResponse()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = CoverageEligibilityResponse()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = CoverageEligibilityResponse()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_purpose(self):
        resource = CoverageEligibilityResponse()
        resource.purpose = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_patient(self):
        resource = CoverageEligibilityResponse()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_created(self):
        resource = CoverageEligibilityResponse()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'created')
        assert result is not None

    def test_get_path_requestor(self):
        resource = CoverageEligibilityResponse()
        resource.requestor = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'requestor')
        assert result is not None

    def test_get_path_request(self):
        resource = CoverageEligibilityResponse()
        resource.request = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'request')
        assert result is not None

    def test_get_path_outcome(self):
        resource = CoverageEligibilityResponse()
        resource.outcome = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'outcome')
        assert result is not None

    def test_get_path_disposition(self):
        resource = CoverageEligibilityResponse()
        resource.disposition = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'disposition')
        assert result is not None

    def test_get_path_insurer(self):
        resource = CoverageEligibilityResponse()
        resource.insurer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'insurer')
        assert result is not None

    def test_get_path_insurance(self):
        resource = CoverageEligibilityResponse()
        resource.insurance = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'insurance')
        assert result is not None

    def test_get_path_pre_auth_ref(self):
        resource = CoverageEligibilityResponse()
        resource.preAuthRef = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'preAuthRef')
        assert result is not None

    def test_get_path_form(self):
        resource = CoverageEligibilityResponse()
        resource.form = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'form')
        assert result is not None

    def test_get_path_error(self):
        resource = CoverageEligibilityResponse()
        resource.error = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'error')
        assert result is not None


class TestSetPathCoverageEligibilityResponse:

    def test_set_path_id(self):
        resource = CoverageEligibilityResponse()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = CoverageEligibilityResponse()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'CoverageEligibilityResponse.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = CoverageEligibilityResponse()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = CoverageEligibilityResponse()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = CoverageEligibilityResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = CoverageEligibilityResponse()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = CoverageEligibilityResponse()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = CoverageEligibilityResponse()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = CoverageEligibilityResponse()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = CoverageEligibilityResponse()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = CoverageEligibilityResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_purpose(self):
        resource = CoverageEligibilityResponse()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_patient(self):
        resource = CoverageEligibilityResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_created(self):
        resource = CoverageEligibilityResponse()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'created', value)
        assert result is True
        assert resource.created is not None

    def test_set_path_requestor(self):
        resource = CoverageEligibilityResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'requestor', value)
        assert result is True
        assert resource.requestor is not None

    def test_set_path_request(self):
        resource = CoverageEligibilityResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'request', value)
        assert result is True
        assert resource.request is not None

    def test_set_path_outcome(self):
        resource = CoverageEligibilityResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'outcome', value)
        assert result is True
        assert resource.outcome is not None

    def test_set_path_disposition(self):
        resource = CoverageEligibilityResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'disposition', value)
        assert result is True
        assert resource.disposition is not None

    def test_set_path_insurer(self):
        resource = CoverageEligibilityResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'insurer', value)
        assert result is True
        assert resource.insurer is not None

    def test_set_path_insurance(self):
        resource = CoverageEligibilityResponse()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'insurance', value)
        assert result is True
        assert resource.insurance is not None

    def test_set_path_pre_auth_ref(self):
        resource = CoverageEligibilityResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'preAuthRef', value)
        assert result is True
        assert resource.preAuthRef is not None

    def test_set_path_form(self):
        resource = CoverageEligibilityResponse()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'form', value)
        assert result is True
        assert resource.form is not None

    def test_set_path_error(self):
        resource = CoverageEligibilityResponse()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'error', value)
        assert result is True
        assert resource.error is not None


class TestParsePathCoverageEligibilityResponse:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('CoverageEligibilityResponse.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('CoverageEligibilityResponse.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('CoverageEligibilityResponse.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
