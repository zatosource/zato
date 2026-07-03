# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Contract


class TestToDictContract:

    def test_to_dict_empty(self):
        resource = Contract()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Contract'

    def test_to_dict_with_id(self):
        resource = Contract()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Contract()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Contract)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Contract()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Contract()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Contract()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Contract()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Contract()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Contract()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Contract()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Contract()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Contract()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_url(self):
        resource = Contract()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_version(self):
        resource = Contract()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_status(self):
        resource = Contract()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_legal_state(self):
        resource = Contract()
        resource.legalState = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'legalState' in result

    def test_to_dict_instantiates_canonical(self):
        resource = Contract()
        resource.instantiatesCanonical = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesCanonical' in result

    def test_to_dict_instantiates_uri(self):
        resource = Contract()
        resource.instantiatesUri = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesUri' in result

    def test_to_dict_content_derivative(self):
        resource = Contract()
        resource.contentDerivative = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contentDerivative' in result

    def test_to_dict_issued(self):
        resource = Contract()
        resource.issued = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'issued' in result

    def test_to_dict_applies(self):
        resource = Contract()
        resource.applies = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'applies' in result

    def test_to_dict_expiration_type(self):
        resource = Contract()
        resource.expirationType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'expirationType' in result

    def test_to_dict_subject(self):
        resource = Contract()
        resource.subject = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_authority(self):
        resource = Contract()
        resource.authority = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'authority' in result

    def test_to_dict_domain(self):
        resource = Contract()
        resource.domain = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'domain' in result

    def test_to_dict_site(self):
        resource = Contract()
        resource.site = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'site' in result

    def test_to_dict_name(self):
        resource = Contract()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = Contract()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_subtitle(self):
        resource = Contract()
        resource.subtitle = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subtitle' in result

    def test_to_dict_alias(self):
        resource = Contract()
        resource.alias = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'alias' in result

    def test_to_dict_author(self):
        resource = Contract()
        resource.author = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_scope(self):
        resource = Contract()
        resource.scope = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'scope' in result

    def test_to_dict_type(self):
        resource = Contract()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_sub_type(self):
        resource = Contract()
        resource.subType = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subType' in result

    def test_to_dict_content_definition(self):
        resource = Contract()
        resource.contentDefinition = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contentDefinition' in result

    def test_to_dict_term(self):
        resource = Contract()
        resource.term = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'term' in result

    def test_to_dict_supporting_info(self):
        resource = Contract()
        resource.supportingInfo = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supportingInfo' in result

    def test_to_dict_relevant_history(self):
        resource = Contract()
        resource.relevantHistory = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relevantHistory' in result

    def test_to_dict_signer(self):
        resource = Contract()
        resource.signer = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'signer' in result

    def test_to_dict_friendly(self):
        resource = Contract()
        resource.friendly = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'friendly' in result

    def test_to_dict_legal(self):
        resource = Contract()
        resource.legal = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'legal' in result

    def test_to_dict_rule(self):
        resource = Contract()
        resource.rule = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'rule' in result


class TestFromDictContract:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Contract', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert isinstance(result, Contract)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Contract'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert isinstance(result, Contract)

    def test_from_dict_id(self):
        data = {'resourceType': 'Contract', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Contract', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Contract', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Contract', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Contract', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Contract', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Contract', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Contract', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Contract', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.identifier is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'Contract', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.url is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'Contract', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.version is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Contract', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.status is not None

    def test_from_dict_legal_state(self):
        data = {'legalState': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                        'text': 'Test concept'},
         'resourceType': 'Contract'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.legalState is not None

    def test_from_dict_instantiates_canonical(self):
        data = {'resourceType': 'Contract', 'instantiatesCanonical': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.instantiatesCanonical is not None

    def test_from_dict_instantiates_uri(self):
        data = {'resourceType': 'Contract', 'instantiatesUri': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.instantiatesUri is not None

    def test_from_dict_content_derivative(self):
        data = {'contentDerivative': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                               'text': 'Test concept'},
         'resourceType': 'Contract'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.contentDerivative is not None

    def test_from_dict_issued(self):
        data = {'resourceType': 'Contract', 'issued': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.issued is not None

    def test_from_dict_applies(self):
        data = {'resourceType': 'Contract', 'applies': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.applies is not None

    def test_from_dict_expiration_type(self):
        data = {'expirationType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                            'text': 'Test concept'},
         'resourceType': 'Contract'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.expirationType is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'Contract', 'subject': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.subject is not None

    def test_from_dict_authority(self):
        data = {'resourceType': 'Contract', 'authority': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.authority is not None

    def test_from_dict_domain(self):
        data = {'resourceType': 'Contract', 'domain': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.domain is not None

    def test_from_dict_site(self):
        data = {'resourceType': 'Contract', 'site': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.site is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'Contract', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'Contract', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.title is not None

    def test_from_dict_subtitle(self):
        data = {'resourceType': 'Contract', 'subtitle': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.subtitle is not None

    def test_from_dict_alias(self):
        data = {'resourceType': 'Contract', 'alias': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.alias is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'Contract', 'author': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.author is not None

    def test_from_dict_scope(self):
        data = {'resourceType': 'Contract',
         'scope': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                   'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.scope is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'Contract',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.type_ is not None

    def test_from_dict_sub_type(self):
        data = {'resourceType': 'Contract',
         'subType': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.subType is not None

    def test_from_dict_content_definition(self):
        data = {'resourceType': 'Contract', 'contentDefinition': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.contentDefinition is not None

    def test_from_dict_term(self):
        data = {'resourceType': 'Contract', 'term': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.term is not None

    def test_from_dict_supporting_info(self):
        data = {'resourceType': 'Contract', 'supportingInfo': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.supportingInfo is not None

    def test_from_dict_relevant_history(self):
        data = {'resourceType': 'Contract', 'relevantHistory': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.relevantHistory is not None

    def test_from_dict_signer(self):
        data = {'resourceType': 'Contract', 'signer': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.signer is not None

    def test_from_dict_friendly(self):
        data = {'resourceType': 'Contract', 'friendly': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.friendly is not None

    def test_from_dict_legal(self):
        data = {'resourceType': 'Contract', 'legal': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.legal is not None

    def test_from_dict_rule(self):
        data = {'resourceType': 'Contract', 'rule': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Contract)
        assert result.rule is not None


class TestGetPathContract:

    def test_get_path_id(self):
        resource = Contract()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Contract()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Contract()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Contract.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Contract()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Contract()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Contract()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Contract()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Contract()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Contract()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Contract()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Contract()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_url(self):
        resource = Contract()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_version(self):
        resource = Contract()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_status(self):
        resource = Contract()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_legal_state(self):
        resource = Contract()
        resource.legalState = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'legalState')
        assert result is not None

    def test_get_path_instantiates_canonical(self):
        resource = Contract()
        resource.instantiatesCanonical = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesCanonical')
        assert result is not None

    def test_get_path_instantiates_uri(self):
        resource = Contract()
        resource.instantiatesUri = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesUri')
        assert result is not None

    def test_get_path_content_derivative(self):
        resource = Contract()
        resource.contentDerivative = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contentDerivative')
        assert result is not None

    def test_get_path_issued(self):
        resource = Contract()
        resource.issued = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'issued')
        assert result is not None

    def test_get_path_applies(self):
        resource = Contract()
        resource.applies = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'applies')
        assert result is not None

    def test_get_path_expiration_type(self):
        resource = Contract()
        resource.expirationType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'expirationType')
        assert result is not None

    def test_get_path_subject(self):
        resource = Contract()
        resource.subject = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_authority(self):
        resource = Contract()
        resource.authority = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'authority')
        assert result is not None

    def test_get_path_domain(self):
        resource = Contract()
        resource.domain = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'domain')
        assert result is not None

    def test_get_path_site(self):
        resource = Contract()
        resource.site = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'site')
        assert result is not None

    def test_get_path_name(self):
        resource = Contract()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = Contract()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_subtitle(self):
        resource = Contract()
        resource.subtitle = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subtitle')
        assert result is not None

    def test_get_path_alias(self):
        resource = Contract()
        resource.alias = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'alias')
        assert result is not None

    def test_get_path_author(self):
        resource = Contract()
        resource.author = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_scope(self):
        resource = Contract()
        resource.scope = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'scope')
        assert result is not None

    def test_get_path_type(self):
        resource = Contract()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_sub_type(self):
        resource = Contract()
        resource.subType = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subType')
        assert result is not None

    def test_get_path_content_definition(self):
        resource = Contract()
        resource.contentDefinition = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contentDefinition')
        assert result is not None

    def test_get_path_term(self):
        resource = Contract()
        resource.term = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'term')
        assert result is not None

    def test_get_path_supporting_info(self):
        resource = Contract()
        resource.supportingInfo = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supportingInfo')
        assert result is not None

    def test_get_path_relevant_history(self):
        resource = Contract()
        resource.relevantHistory = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relevantHistory')
        assert result is not None

    def test_get_path_signer(self):
        resource = Contract()
        resource.signer = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'signer')
        assert result is not None

    def test_get_path_friendly(self):
        resource = Contract()
        resource.friendly = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'friendly')
        assert result is not None

    def test_get_path_legal(self):
        resource = Contract()
        resource.legal = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'legal')
        assert result is not None

    def test_get_path_rule(self):
        resource = Contract()
        resource.rule = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'rule')
        assert result is not None


class TestSetPathContract:

    def test_set_path_id(self):
        resource = Contract()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Contract()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Contract.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Contract()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Contract()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Contract()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Contract()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Contract()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Contract()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Contract()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Contract()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_url(self):
        resource = Contract()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_version(self):
        resource = Contract()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_status(self):
        resource = Contract()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_legal_state(self):
        resource = Contract()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'legalState', value)
        assert result is True
        assert resource.legalState is not None

    def test_set_path_instantiates_canonical(self):
        resource = Contract()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesCanonical', value)
        assert result is True
        assert resource.instantiatesCanonical is not None

    def test_set_path_instantiates_uri(self):
        resource = Contract()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesUri', value)
        assert result is True
        assert resource.instantiatesUri is not None

    def test_set_path_content_derivative(self):
        resource = Contract()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contentDerivative', value)
        assert result is True
        assert resource.contentDerivative is not None

    def test_set_path_issued(self):
        resource = Contract()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'issued', value)
        assert result is True
        assert resource.issued is not None

    def test_set_path_applies(self):
        resource = Contract()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'applies', value)
        assert result is True
        assert resource.applies is not None

    def test_set_path_expiration_type(self):
        resource = Contract()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'expirationType', value)
        assert result is True
        assert resource.expirationType is not None

    def test_set_path_subject(self):
        resource = Contract()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_authority(self):
        resource = Contract()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'authority', value)
        assert result is True
        assert resource.authority is not None

    def test_set_path_domain(self):
        resource = Contract()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'domain', value)
        assert result is True
        assert resource.domain is not None

    def test_set_path_site(self):
        resource = Contract()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'site', value)
        assert result is True
        assert resource.site is not None

    def test_set_path_name(self):
        resource = Contract()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = Contract()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_subtitle(self):
        resource = Contract()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subtitle', value)
        assert result is True
        assert resource.subtitle is not None

    def test_set_path_alias(self):
        resource = Contract()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'alias', value)
        assert result is True
        assert resource.alias is not None

    def test_set_path_author(self):
        resource = Contract()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_scope(self):
        resource = Contract()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'scope', value)
        assert result is True
        assert resource.scope is not None

    def test_set_path_type(self):
        resource = Contract()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_sub_type(self):
        resource = Contract()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subType', value)
        assert result is True
        assert resource.subType is not None

    def test_set_path_content_definition(self):
        resource = Contract()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contentDefinition', value)
        assert result is True
        assert resource.contentDefinition is not None

    def test_set_path_term(self):
        resource = Contract()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'term', value)
        assert result is True
        assert resource.term is not None

    def test_set_path_supporting_info(self):
        resource = Contract()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supportingInfo', value)
        assert result is True
        assert resource.supportingInfo is not None

    def test_set_path_relevant_history(self):
        resource = Contract()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relevantHistory', value)
        assert result is True
        assert resource.relevantHistory is not None

    def test_set_path_signer(self):
        resource = Contract()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'signer', value)
        assert result is True
        assert resource.signer is not None

    def test_set_path_friendly(self):
        resource = Contract()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'friendly', value)
        assert result is True
        assert resource.friendly is not None

    def test_set_path_legal(self):
        resource = Contract()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'legal', value)
        assert result is True
        assert resource.legal is not None

    def test_set_path_rule(self):
        resource = Contract()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'rule', value)
        assert result is True
        assert resource.rule is not None


class TestParsePathContract:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Contract.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Contract.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Contract.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
