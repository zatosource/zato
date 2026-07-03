# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import VerificationResult


class TestToDictVerificationResult:

    def test_to_dict_empty(self):
        resource = VerificationResult()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'VerificationResult'

    def test_to_dict_with_id(self):
        resource = VerificationResult()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = VerificationResult()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, VerificationResult)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = VerificationResult()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = VerificationResult()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = VerificationResult()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = VerificationResult()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = VerificationResult()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = VerificationResult()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = VerificationResult()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = VerificationResult()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_target(self):
        resource = VerificationResult()
        resource.target = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'target' in result

    def test_to_dict_target_location(self):
        resource = VerificationResult()
        resource.targetLocation = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'targetLocation' in result

    def test_to_dict_need(self):
        resource = VerificationResult()
        resource.need = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'need' in result

    def test_to_dict_status(self):
        resource = VerificationResult()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_status_date(self):
        resource = VerificationResult()
        resource.statusDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'statusDate' in result

    def test_to_dict_validation_type(self):
        resource = VerificationResult()
        resource.validationType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'validationType' in result

    def test_to_dict_validation_process(self):
        resource = VerificationResult()
        resource.validationProcess = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'validationProcess' in result

    def test_to_dict_frequency(self):
        resource = VerificationResult()
        resource.frequency = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'frequency' in result

    def test_to_dict_last_performed(self):
        resource = VerificationResult()
        resource.lastPerformed = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lastPerformed' in result

    def test_to_dict_next_scheduled(self):
        resource = VerificationResult()
        resource.nextScheduled = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'nextScheduled' in result

    def test_to_dict_failure_action(self):
        resource = VerificationResult()
        resource.failureAction = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'failureAction' in result

    def test_to_dict_primary_source(self):
        resource = VerificationResult()
        resource.primarySource = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'primarySource' in result

    def test_to_dict_attestation(self):
        resource = VerificationResult()
        resource.attestation = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'attestation' in result

    def test_to_dict_validator(self):
        resource = VerificationResult()
        resource.validator = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'validator' in result


class TestFromDictVerificationResult:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'VerificationResult', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert isinstance(result, VerificationResult)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'VerificationResult'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert isinstance(result, VerificationResult)

    def test_from_dict_id(self):
        data = {'resourceType': 'VerificationResult', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'VerificationResult', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'VerificationResult', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'VerificationResult', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'VerificationResult', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'VerificationResult', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'VerificationResult', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'VerificationResult', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.modifierExtension is not None

    def test_from_dict_target(self):
        data = {'resourceType': 'VerificationResult', 'target': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.target is not None

    def test_from_dict_target_location(self):
        data = {'resourceType': 'VerificationResult', 'targetLocation': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.targetLocation is not None

    def test_from_dict_need(self):
        data = {'need': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'VerificationResult'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.need is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'VerificationResult', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.status is not None

    def test_from_dict_status_date(self):
        data = {'resourceType': 'VerificationResult', 'statusDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.statusDate is not None

    def test_from_dict_validation_type(self):
        data = {'resourceType': 'VerificationResult',
         'validationType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                            'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.validationType is not None

    def test_from_dict_validation_process(self):
        data = {'resourceType': 'VerificationResult',
         'validationProcess': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.validationProcess is not None

    def test_from_dict_frequency(self):
        data = {'resourceType': 'VerificationResult', 'frequency': {'value': 'test'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.frequency is not None

    def test_from_dict_last_performed(self):
        data = {'resourceType': 'VerificationResult', 'lastPerformed': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.lastPerformed is not None

    def test_from_dict_next_scheduled(self):
        data = {'resourceType': 'VerificationResult', 'nextScheduled': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.nextScheduled is not None

    def test_from_dict_failure_action(self):
        data = {'failureAction': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'},
         'resourceType': 'VerificationResult'}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.failureAction is not None

    def test_from_dict_primary_source(self):
        data = {'resourceType': 'VerificationResult', 'primarySource': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.primarySource is not None

    def test_from_dict_attestation(self):
        data = {'resourceType': 'VerificationResult', 'attestation': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.attestation is not None

    def test_from_dict_validator(self):
        data = {'resourceType': 'VerificationResult', 'validator': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, VerificationResult)
        assert result.validator is not None


class TestGetPathVerificationResult:

    def test_get_path_id(self):
        resource = VerificationResult()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = VerificationResult()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = VerificationResult()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'VerificationResult.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = VerificationResult()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = VerificationResult()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = VerificationResult()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = VerificationResult()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = VerificationResult()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = VerificationResult()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = VerificationResult()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_target(self):
        resource = VerificationResult()
        resource.target = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'target')
        assert result is not None

    def test_get_path_target_location(self):
        resource = VerificationResult()
        resource.targetLocation = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'targetLocation')
        assert result is not None

    def test_get_path_need(self):
        resource = VerificationResult()
        resource.need = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'need')
        assert result is not None

    def test_get_path_status(self):
        resource = VerificationResult()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_status_date(self):
        resource = VerificationResult()
        resource.statusDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'statusDate')
        assert result is not None

    def test_get_path_validation_type(self):
        resource = VerificationResult()
        resource.validationType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'validationType')
        assert result is not None

    def test_get_path_validation_process(self):
        resource = VerificationResult()
        resource.validationProcess = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'validationProcess')
        assert result is not None

    def test_get_path_frequency(self):
        resource = VerificationResult()
        resource.frequency = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'frequency')
        assert result is not None

    def test_get_path_last_performed(self):
        resource = VerificationResult()
        resource.lastPerformed = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lastPerformed')
        assert result is not None

    def test_get_path_next_scheduled(self):
        resource = VerificationResult()
        resource.nextScheduled = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nextScheduled')
        assert result is not None

    def test_get_path_failure_action(self):
        resource = VerificationResult()
        resource.failureAction = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'failureAction')
        assert result is not None

    def test_get_path_primary_source(self):
        resource = VerificationResult()
        resource.primarySource = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'primarySource')
        assert result is not None

    def test_get_path_attestation(self):
        resource = VerificationResult()
        resource.attestation = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'attestation')
        assert result is not None

    def test_get_path_validator(self):
        resource = VerificationResult()
        resource.validator = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'validator')
        assert result is not None


class TestSetPathVerificationResult:

    def test_set_path_id(self):
        resource = VerificationResult()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = VerificationResult()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'VerificationResult.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = VerificationResult()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = VerificationResult()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = VerificationResult()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = VerificationResult()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = VerificationResult()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = VerificationResult()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = VerificationResult()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_target(self):
        resource = VerificationResult()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'target', value)
        assert result is True
        assert resource.target is not None

    def test_set_path_target_location(self):
        resource = VerificationResult()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'targetLocation', value)
        assert result is True
        assert resource.targetLocation is not None

    def test_set_path_need(self):
        resource = VerificationResult()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'need', value)
        assert result is True
        assert resource.need is not None

    def test_set_path_status(self):
        resource = VerificationResult()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_status_date(self):
        resource = VerificationResult()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'statusDate', value)
        assert result is True
        assert resource.statusDate is not None

    def test_set_path_validation_type(self):
        resource = VerificationResult()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'validationType', value)
        assert result is True
        assert resource.validationType is not None

    def test_set_path_validation_process(self):
        resource = VerificationResult()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'validationProcess', value)
        assert result is True
        assert resource.validationProcess is not None

    def test_set_path_frequency(self):
        resource = VerificationResult()
        value = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'frequency', value)
        assert result is True
        assert resource.frequency is not None

    def test_set_path_last_performed(self):
        resource = VerificationResult()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lastPerformed', value)
        assert result is True
        assert resource.lastPerformed is not None

    def test_set_path_next_scheduled(self):
        resource = VerificationResult()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'nextScheduled', value)
        assert result is True
        assert resource.nextScheduled is not None

    def test_set_path_failure_action(self):
        resource = VerificationResult()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'failureAction', value)
        assert result is True
        assert resource.failureAction is not None

    def test_set_path_primary_source(self):
        resource = VerificationResult()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'primarySource', value)
        assert result is True
        assert resource.primarySource is not None

    def test_set_path_attestation(self):
        resource = VerificationResult()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'attestation', value)
        assert result is True
        assert resource.attestation is not None

    def test_set_path_validator(self):
        resource = VerificationResult()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'validator', value)
        assert result is True
        assert resource.validator is not None


class TestParsePathVerificationResult:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('VerificationResult.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('VerificationResult.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('VerificationResult.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
