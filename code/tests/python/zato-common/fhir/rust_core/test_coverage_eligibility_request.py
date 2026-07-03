# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import CoverageEligibilityRequest


class TestToDictCoverageEligibilityRequest:

    def test_to_dict_empty(self):
        resource = CoverageEligibilityRequest()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'CoverageEligibilityRequest'

    def test_to_dict_with_id(self):
        resource = CoverageEligibilityRequest()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = CoverageEligibilityRequest()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, CoverageEligibilityRequest)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = CoverageEligibilityRequest()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = CoverageEligibilityRequest()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = CoverageEligibilityRequest()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = CoverageEligibilityRequest()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = CoverageEligibilityRequest()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = CoverageEligibilityRequest()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = CoverageEligibilityRequest()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = CoverageEligibilityRequest()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = CoverageEligibilityRequest()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = CoverageEligibilityRequest()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_priority(self):
        resource = CoverageEligibilityRequest()
        resource.priority = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priority' in result

    def test_to_dict_purpose(self):
        resource = CoverageEligibilityRequest()
        resource.purpose = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_patient(self):
        resource = CoverageEligibilityRequest()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_created(self):
        resource = CoverageEligibilityRequest()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'created' in result

    def test_to_dict_enterer(self):
        resource = CoverageEligibilityRequest()
        resource.enterer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'enterer' in result

    def test_to_dict_provider(self):
        resource = CoverageEligibilityRequest()
        resource.provider = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'provider' in result

    def test_to_dict_insurer(self):
        resource = CoverageEligibilityRequest()
        resource.insurer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'insurer' in result

    def test_to_dict_facility(self):
        resource = CoverageEligibilityRequest()
        resource.facility = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'facility' in result

    def test_to_dict_supporting_info(self):
        resource = CoverageEligibilityRequest()
        resource.supportingInfo = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supportingInfo' in result

    def test_to_dict_insurance(self):
        resource = CoverageEligibilityRequest()
        resource.insurance = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'insurance' in result

    def test_to_dict_item(self):
        resource = CoverageEligibilityRequest()
        resource.item = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'item' in result


class TestFromDictCoverageEligibilityRequest:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert isinstance(result, CoverageEligibilityRequest)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'CoverageEligibilityRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert isinstance(result, CoverageEligibilityRequest)

    def test_from_dict_id(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.status is not None

    def test_from_dict_priority(self):
        data = {'priority': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'CoverageEligibilityRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.priority is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'purpose': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.purpose is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.patient is not None

    def test_from_dict_created(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'created': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.created is not None

    def test_from_dict_enterer(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'enterer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.enterer is not None

    def test_from_dict_provider(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'provider': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.provider is not None

    def test_from_dict_insurer(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'insurer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.insurer is not None

    def test_from_dict_facility(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'facility': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.facility is not None

    def test_from_dict_supporting_info(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'supportingInfo': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.supportingInfo is not None

    def test_from_dict_insurance(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'insurance': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.insurance is not None

    def test_from_dict_item(self):
        data = {'resourceType': 'CoverageEligibilityRequest', 'item': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CoverageEligibilityRequest)
        assert result.item is not None


class TestGetPathCoverageEligibilityRequest:

    def test_get_path_id(self):
        resource = CoverageEligibilityRequest()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = CoverageEligibilityRequest()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = CoverageEligibilityRequest()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'CoverageEligibilityRequest.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = CoverageEligibilityRequest()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = CoverageEligibilityRequest()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = CoverageEligibilityRequest()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = CoverageEligibilityRequest()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = CoverageEligibilityRequest()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = CoverageEligibilityRequest()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = CoverageEligibilityRequest()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = CoverageEligibilityRequest()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = CoverageEligibilityRequest()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_priority(self):
        resource = CoverageEligibilityRequest()
        resource.priority = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priority')
        assert result is not None

    def test_get_path_purpose(self):
        resource = CoverageEligibilityRequest()
        resource.purpose = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_patient(self):
        resource = CoverageEligibilityRequest()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_created(self):
        resource = CoverageEligibilityRequest()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'created')
        assert result is not None

    def test_get_path_enterer(self):
        resource = CoverageEligibilityRequest()
        resource.enterer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'enterer')
        assert result is not None

    def test_get_path_provider(self):
        resource = CoverageEligibilityRequest()
        resource.provider = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'provider')
        assert result is not None

    def test_get_path_insurer(self):
        resource = CoverageEligibilityRequest()
        resource.insurer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'insurer')
        assert result is not None

    def test_get_path_facility(self):
        resource = CoverageEligibilityRequest()
        resource.facility = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'facility')
        assert result is not None

    def test_get_path_supporting_info(self):
        resource = CoverageEligibilityRequest()
        resource.supportingInfo = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supportingInfo')
        assert result is not None

    def test_get_path_insurance(self):
        resource = CoverageEligibilityRequest()
        resource.insurance = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'insurance')
        assert result is not None

    def test_get_path_item(self):
        resource = CoverageEligibilityRequest()
        resource.item = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'item')
        assert result is not None


class TestSetPathCoverageEligibilityRequest:

    def test_set_path_id(self):
        resource = CoverageEligibilityRequest()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = CoverageEligibilityRequest()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'CoverageEligibilityRequest.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = CoverageEligibilityRequest()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = CoverageEligibilityRequest()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = CoverageEligibilityRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = CoverageEligibilityRequest()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = CoverageEligibilityRequest()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = CoverageEligibilityRequest()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = CoverageEligibilityRequest()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = CoverageEligibilityRequest()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = CoverageEligibilityRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_priority(self):
        resource = CoverageEligibilityRequest()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priority', value)
        assert result is True
        assert resource.priority is not None

    def test_set_path_purpose(self):
        resource = CoverageEligibilityRequest()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_patient(self):
        resource = CoverageEligibilityRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_created(self):
        resource = CoverageEligibilityRequest()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'created', value)
        assert result is True
        assert resource.created is not None

    def test_set_path_enterer(self):
        resource = CoverageEligibilityRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'enterer', value)
        assert result is True
        assert resource.enterer is not None

    def test_set_path_provider(self):
        resource = CoverageEligibilityRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'provider', value)
        assert result is True
        assert resource.provider is not None

    def test_set_path_insurer(self):
        resource = CoverageEligibilityRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'insurer', value)
        assert result is True
        assert resource.insurer is not None

    def test_set_path_facility(self):
        resource = CoverageEligibilityRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'facility', value)
        assert result is True
        assert resource.facility is not None

    def test_set_path_supporting_info(self):
        resource = CoverageEligibilityRequest()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supportingInfo', value)
        assert result is True
        assert resource.supportingInfo is not None

    def test_set_path_insurance(self):
        resource = CoverageEligibilityRequest()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'insurance', value)
        assert result is True
        assert resource.insurance is not None

    def test_set_path_item(self):
        resource = CoverageEligibilityRequest()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'item', value)
        assert result is True
        assert resource.item is not None


class TestParsePathCoverageEligibilityRequest:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('CoverageEligibilityRequest.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('CoverageEligibilityRequest.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('CoverageEligibilityRequest.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
