# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Consent


class TestToDictConsent:

    def test_to_dict_empty(self):
        resource = Consent()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Consent'

    def test_to_dict_with_id(self):
        resource = Consent()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Consent()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Consent)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Consent()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Consent()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Consent()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Consent()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Consent()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Consent()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Consent()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Consent()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Consent()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = Consent()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_scope(self):
        resource = Consent()
        resource.scope = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'scope' in result

    def test_to_dict_category(self):
        resource = Consent()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_patient(self):
        resource = Consent()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_date_time(self):
        resource = Consent()
        resource.dateTime = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dateTime' in result

    def test_to_dict_performer(self):
        resource = Consent()
        resource.performer = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performer' in result

    def test_to_dict_organization(self):
        resource = Consent()
        resource.organization = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'organization' in result

    def test_to_dict_policy(self):
        resource = Consent()
        resource.policy = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'policy' in result

    def test_to_dict_policy_rule(self):
        resource = Consent()
        resource.policyRule = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'policyRule' in result

    def test_to_dict_verification(self):
        resource = Consent()
        resource.verification = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'verification' in result

    def test_to_dict_provision(self):
        resource = Consent()
        resource.provision = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'provision' in result


class TestFromDictConsent:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Consent', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert isinstance(result, Consent)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Consent'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert isinstance(result, Consent)

    def test_from_dict_id(self):
        data = {'resourceType': 'Consent', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Consent', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Consent', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Consent', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Consent', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Consent', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Consent', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Consent', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Consent', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Consent', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.status is not None

    def test_from_dict_scope(self):
        data = {'resourceType': 'Consent',
         'scope': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                   'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.scope is not None

    def test_from_dict_category(self):
        data = {'category': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'Consent'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.category is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'Consent', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.patient is not None

    def test_from_dict_date_time(self):
        data = {'resourceType': 'Consent', 'dateTime': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.dateTime is not None

    def test_from_dict_performer(self):
        data = {'resourceType': 'Consent', 'performer': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.performer is not None

    def test_from_dict_organization(self):
        data = {'resourceType': 'Consent', 'organization': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.organization is not None

    def test_from_dict_policy(self):
        data = {'resourceType': 'Consent', 'policy': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.policy is not None

    def test_from_dict_policy_rule(self):
        data = {'policyRule': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                        'text': 'Test concept'},
         'resourceType': 'Consent'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.policyRule is not None

    def test_from_dict_verification(self):
        data = {'resourceType': 'Consent', 'verification': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.verification is not None

    def test_from_dict_provision(self):
        data = {'resourceType': 'Consent', 'provision': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Consent)
        assert result.provision is not None


class TestGetPathConsent:

    def test_get_path_id(self):
        resource = Consent()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Consent()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Consent()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Consent.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Consent()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Consent()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Consent()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Consent()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Consent()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Consent()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Consent()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Consent()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = Consent()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_scope(self):
        resource = Consent()
        resource.scope = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'scope')
        assert result is not None

    def test_get_path_category(self):
        resource = Consent()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_patient(self):
        resource = Consent()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_date_time(self):
        resource = Consent()
        resource.dateTime = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dateTime')
        assert result is not None

    def test_get_path_performer(self):
        resource = Consent()
        resource.performer = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performer')
        assert result is not None

    def test_get_path_organization(self):
        resource = Consent()
        resource.organization = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'organization')
        assert result is not None

    def test_get_path_policy(self):
        resource = Consent()
        resource.policy = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'policy')
        assert result is not None

    def test_get_path_policy_rule(self):
        resource = Consent()
        resource.policyRule = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'policyRule')
        assert result is not None

    def test_get_path_verification(self):
        resource = Consent()
        resource.verification = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'verification')
        assert result is not None

    def test_get_path_provision(self):
        resource = Consent()
        resource.provision = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'provision')
        assert result is not None


class TestSetPathConsent:

    def test_set_path_id(self):
        resource = Consent()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Consent()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Consent.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Consent()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Consent()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Consent()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Consent()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Consent()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Consent()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Consent()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Consent()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = Consent()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_scope(self):
        resource = Consent()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'scope', value)
        assert result is True
        assert resource.scope is not None

    def test_set_path_category(self):
        resource = Consent()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_patient(self):
        resource = Consent()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_date_time(self):
        resource = Consent()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dateTime', value)
        assert result is True
        assert resource.dateTime is not None

    def test_set_path_performer(self):
        resource = Consent()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performer', value)
        assert result is True
        assert resource.performer is not None

    def test_set_path_organization(self):
        resource = Consent()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'organization', value)
        assert result is True
        assert resource.organization is not None

    def test_set_path_policy(self):
        resource = Consent()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'policy', value)
        assert result is True
        assert resource.policy is not None

    def test_set_path_policy_rule(self):
        resource = Consent()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'policyRule', value)
        assert result is True
        assert resource.policyRule is not None

    def test_set_path_verification(self):
        resource = Consent()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'verification', value)
        assert result is True
        assert resource.verification is not None

    def test_set_path_provision(self):
        resource = Consent()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'provision', value)
        assert result is True
        assert resource.provision is not None


class TestParsePathConsent:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Consent.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Consent.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Consent.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
