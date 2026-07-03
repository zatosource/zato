# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Coverage


class TestToDictCoverage:

    def test_to_dict_empty(self):
        resource = Coverage()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Coverage'

    def test_to_dict_with_id(self):
        resource = Coverage()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Coverage()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Coverage)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Coverage()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Coverage()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Coverage()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Coverage()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Coverage()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Coverage()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Coverage()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Coverage()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Coverage()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = Coverage()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_type(self):
        resource = Coverage()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_policy_holder(self):
        resource = Coverage()
        resource.policyHolder = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'policyHolder' in result

    def test_to_dict_subscriber(self):
        resource = Coverage()
        resource.subscriber = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subscriber' in result

    def test_to_dict_subscriber_id(self):
        resource = Coverage()
        resource.subscriberId = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subscriberId' in result

    def test_to_dict_beneficiary(self):
        resource = Coverage()
        resource.beneficiary = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'beneficiary' in result

    def test_to_dict_dependent(self):
        resource = Coverage()
        resource.dependent = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dependent' in result

    def test_to_dict_relationship(self):
        resource = Coverage()
        resource.relationship = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relationship' in result

    def test_to_dict_period(self):
        resource = Coverage()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'period' in result

    def test_to_dict_payor(self):
        resource = Coverage()
        resource.payor = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'payor' in result

    def test_to_dict_class(self):
        resource = Coverage()
        resource.class_ = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'class' in result

    def test_to_dict_order(self):
        resource = Coverage()
        resource.order = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'order' in result

    def test_to_dict_network(self):
        resource = Coverage()
        resource.network = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'network' in result

    def test_to_dict_cost_to_beneficiary(self):
        resource = Coverage()
        resource.costToBeneficiary = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'costToBeneficiary' in result

    def test_to_dict_subrogation(self):
        resource = Coverage()
        resource.subrogation = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subrogation' in result

    def test_to_dict_contract(self):
        resource = Coverage()
        resource.contract = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contract' in result


class TestFromDictCoverage:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Coverage', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert isinstance(result, Coverage)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Coverage'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert isinstance(result, Coverage)

    def test_from_dict_id(self):
        data = {'resourceType': 'Coverage', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Coverage', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Coverage', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Coverage', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Coverage', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Coverage', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Coverage', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Coverage', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Coverage', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Coverage', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.status is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'Coverage',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.type_ is not None

    def test_from_dict_policy_holder(self):
        data = {'resourceType': 'Coverage', 'policyHolder': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.policyHolder is not None

    def test_from_dict_subscriber(self):
        data = {'resourceType': 'Coverage', 'subscriber': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.subscriber is not None

    def test_from_dict_subscriber_id(self):
        data = {'resourceType': 'Coverage', 'subscriberId': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.subscriberId is not None

    def test_from_dict_beneficiary(self):
        data = {'resourceType': 'Coverage', 'beneficiary': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.beneficiary is not None

    def test_from_dict_dependent(self):
        data = {'resourceType': 'Coverage', 'dependent': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.dependent is not None

    def test_from_dict_relationship(self):
        data = {'relationship': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'},
         'resourceType': 'Coverage'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.relationship is not None

    def test_from_dict_period(self):
        data = {'resourceType': 'Coverage', 'period': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.period is not None

    def test_from_dict_payor(self):
        data = {'resourceType': 'Coverage', 'payor': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.payor is not None

    def test_from_dict_class(self):
        data = {'resourceType': 'Coverage', 'class': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.class_ is not None

    def test_from_dict_order(self):
        data = {'resourceType': 'Coverage', 'order': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.order is not None

    def test_from_dict_network(self):
        data = {'resourceType': 'Coverage', 'network': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.network is not None

    def test_from_dict_cost_to_beneficiary(self):
        data = {'resourceType': 'Coverage', 'costToBeneficiary': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.costToBeneficiary is not None

    def test_from_dict_subrogation(self):
        data = {'resourceType': 'Coverage', 'subrogation': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.subrogation is not None

    def test_from_dict_contract(self):
        data = {'resourceType': 'Coverage', 'contract': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Coverage)
        assert result.contract is not None


class TestGetPathCoverage:

    def test_get_path_id(self):
        resource = Coverage()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Coverage()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Coverage()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Coverage.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Coverage()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Coverage()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Coverage()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Coverage()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Coverage()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Coverage()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Coverage()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Coverage()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = Coverage()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_type(self):
        resource = Coverage()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_policy_holder(self):
        resource = Coverage()
        resource.policyHolder = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'policyHolder')
        assert result is not None

    def test_get_path_subscriber(self):
        resource = Coverage()
        resource.subscriber = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subscriber')
        assert result is not None

    def test_get_path_subscriber_id(self):
        resource = Coverage()
        resource.subscriberId = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subscriberId')
        assert result is not None

    def test_get_path_beneficiary(self):
        resource = Coverage()
        resource.beneficiary = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'beneficiary')
        assert result is not None

    def test_get_path_dependent(self):
        resource = Coverage()
        resource.dependent = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dependent')
        assert result is not None

    def test_get_path_relationship(self):
        resource = Coverage()
        resource.relationship = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relationship')
        assert result is not None

    def test_get_path_period(self):
        resource = Coverage()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'period')
        assert result is not None

    def test_get_path_payor(self):
        resource = Coverage()
        resource.payor = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'payor')
        assert result is not None

    def test_get_path_class(self):
        resource = Coverage()
        resource.class_ = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'class')
        assert result is not None

    def test_get_path_order(self):
        resource = Coverage()
        resource.order = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'order')
        assert result is not None

    def test_get_path_network(self):
        resource = Coverage()
        resource.network = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'network')
        assert result is not None

    def test_get_path_cost_to_beneficiary(self):
        resource = Coverage()
        resource.costToBeneficiary = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'costToBeneficiary')
        assert result is not None

    def test_get_path_subrogation(self):
        resource = Coverage()
        resource.subrogation = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subrogation')
        assert result is not None

    def test_get_path_contract(self):
        resource = Coverage()
        resource.contract = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contract')
        assert result is not None


class TestSetPathCoverage:

    def test_set_path_id(self):
        resource = Coverage()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Coverage()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Coverage.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Coverage()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Coverage()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Coverage()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Coverage()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Coverage()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Coverage()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Coverage()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Coverage()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = Coverage()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_type(self):
        resource = Coverage()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_policy_holder(self):
        resource = Coverage()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'policyHolder', value)
        assert result is True
        assert resource.policyHolder is not None

    def test_set_path_subscriber(self):
        resource = Coverage()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subscriber', value)
        assert result is True
        assert resource.subscriber is not None

    def test_set_path_subscriber_id(self):
        resource = Coverage()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subscriberId', value)
        assert result is True
        assert resource.subscriberId is not None

    def test_set_path_beneficiary(self):
        resource = Coverage()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'beneficiary', value)
        assert result is True
        assert resource.beneficiary is not None

    def test_set_path_dependent(self):
        resource = Coverage()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dependent', value)
        assert result is True
        assert resource.dependent is not None

    def test_set_path_relationship(self):
        resource = Coverage()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relationship', value)
        assert result is True
        assert resource.relationship is not None

    def test_set_path_period(self):
        resource = Coverage()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'period', value)
        assert result is True
        assert resource.period is not None

    def test_set_path_payor(self):
        resource = Coverage()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'payor', value)
        assert result is True
        assert resource.payor is not None

    def test_set_path_class(self):
        resource = Coverage()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'class', value)
        assert result is True
        assert resource.class_ is not None

    def test_set_path_order(self):
        resource = Coverage()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'order', value)
        assert result is True
        assert resource.order is not None

    def test_set_path_network(self):
        resource = Coverage()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'network', value)
        assert result is True
        assert resource.network is not None

    def test_set_path_cost_to_beneficiary(self):
        resource = Coverage()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'costToBeneficiary', value)
        assert result is True
        assert resource.costToBeneficiary is not None

    def test_set_path_subrogation(self):
        resource = Coverage()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subrogation', value)
        assert result is True
        assert resource.subrogation is not None

    def test_set_path_contract(self):
        resource = Coverage()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contract', value)
        assert result is True
        assert resource.contract is not None


class TestParsePathCoverage:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Coverage.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Coverage.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Coverage.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
