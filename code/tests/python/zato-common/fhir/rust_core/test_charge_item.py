# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ChargeItem


class TestToDictChargeItem:

    def test_to_dict_empty(self):
        resource = ChargeItem()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ChargeItem'

    def test_to_dict_with_id(self):
        resource = ChargeItem()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ChargeItem()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ChargeItem)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ChargeItem()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ChargeItem()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ChargeItem()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ChargeItem()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ChargeItem()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ChargeItem()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ChargeItem()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ChargeItem()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = ChargeItem()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_definition_uri(self):
        resource = ChargeItem()
        resource.definitionUri = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'definitionUri' in result

    def test_to_dict_definition_canonical(self):
        resource = ChargeItem()
        resource.definitionCanonical = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'definitionCanonical' in result

    def test_to_dict_status(self):
        resource = ChargeItem()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_part_of(self):
        resource = ChargeItem()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'partOf' in result

    def test_to_dict_code(self):
        resource = ChargeItem()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_subject(self):
        resource = ChargeItem()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_context(self):
        resource = ChargeItem()
        resource.context = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'context' in result

    def test_to_dict_performer(self):
        resource = ChargeItem()
        resource.performer = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performer' in result

    def test_to_dict_performing_organization(self):
        resource = ChargeItem()
        resource.performingOrganization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performingOrganization' in result

    def test_to_dict_requesting_organization(self):
        resource = ChargeItem()
        resource.requestingOrganization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'requestingOrganization' in result

    def test_to_dict_cost_center(self):
        resource = ChargeItem()
        resource.costCenter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'costCenter' in result

    def test_to_dict_quantity(self):
        resource = ChargeItem()
        resource.quantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'quantity' in result

    def test_to_dict_bodysite(self):
        resource = ChargeItem()
        resource.bodysite = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'bodysite' in result

    def test_to_dict_factor_override(self):
        resource = ChargeItem()
        resource.factorOverride = 3.14
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'factorOverride' in result

    def test_to_dict_price_override(self):
        resource = ChargeItem()
        resource.priceOverride = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priceOverride' in result

    def test_to_dict_override_reason(self):
        resource = ChargeItem()
        resource.overrideReason = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'overrideReason' in result

    def test_to_dict_enterer(self):
        resource = ChargeItem()
        resource.enterer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'enterer' in result

    def test_to_dict_entered_date(self):
        resource = ChargeItem()
        resource.enteredDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'enteredDate' in result

    def test_to_dict_reason(self):
        resource = ChargeItem()
        resource.reason = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reason' in result

    def test_to_dict_service(self):
        resource = ChargeItem()
        resource.service = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'service' in result

    def test_to_dict_account(self):
        resource = ChargeItem()
        resource.account = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'account' in result

    def test_to_dict_note(self):
        resource = ChargeItem()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_supporting_information(self):
        resource = ChargeItem()
        resource.supportingInformation = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supportingInformation' in result


class TestFromDictChargeItem:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ChargeItem', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert isinstance(result, ChargeItem)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ChargeItem'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert isinstance(result, ChargeItem)

    def test_from_dict_id(self):
        data = {'resourceType': 'ChargeItem', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ChargeItem', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ChargeItem', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ChargeItem', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ChargeItem', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ChargeItem', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ChargeItem', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ChargeItem', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'ChargeItem', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.identifier is not None

    def test_from_dict_definition_uri(self):
        data = {'resourceType': 'ChargeItem', 'definitionUri': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.definitionUri is not None

    def test_from_dict_definition_canonical(self):
        data = {'resourceType': 'ChargeItem', 'definitionCanonical': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.definitionCanonical is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'ChargeItem', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.status is not None

    def test_from_dict_part_of(self):
        data = {'resourceType': 'ChargeItem', 'partOf': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.partOf is not None

    def test_from_dict_code(self):
        data = {'code': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'ChargeItem'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.code is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'ChargeItem', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.subject is not None

    def test_from_dict_context(self):
        data = {'resourceType': 'ChargeItem', 'context': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.context is not None

    def test_from_dict_performer(self):
        data = {'resourceType': 'ChargeItem', 'performer': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.performer is not None

    def test_from_dict_performing_organization(self):
        data = {'resourceType': 'ChargeItem', 'performingOrganization': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.performingOrganization is not None

    def test_from_dict_requesting_organization(self):
        data = {'resourceType': 'ChargeItem', 'requestingOrganization': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.requestingOrganization is not None

    def test_from_dict_cost_center(self):
        data = {'resourceType': 'ChargeItem', 'costCenter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.costCenter is not None

    def test_from_dict_quantity(self):
        data = {'resourceType': 'ChargeItem', 'quantity': {'value': 100, 'unit': 'mg'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.quantity is not None

    def test_from_dict_bodysite(self):
        data = {'bodysite': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'ChargeItem'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.bodysite is not None

    def test_from_dict_factor_override(self):
        data = {'resourceType': 'ChargeItem', 'factorOverride': 3.14}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.factorOverride is not None

    def test_from_dict_price_override(self):
        data = {'resourceType': 'ChargeItem', 'priceOverride': {'value': 'test'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.priceOverride is not None

    def test_from_dict_override_reason(self):
        data = {'resourceType': 'ChargeItem', 'overrideReason': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.overrideReason is not None

    def test_from_dict_enterer(self):
        data = {'resourceType': 'ChargeItem', 'enterer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.enterer is not None

    def test_from_dict_entered_date(self):
        data = {'resourceType': 'ChargeItem', 'enteredDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.enteredDate is not None

    def test_from_dict_reason(self):
        data = {'reason': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                     'text': 'Test concept'}],
         'resourceType': 'ChargeItem'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.reason is not None

    def test_from_dict_service(self):
        data = {'resourceType': 'ChargeItem', 'service': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.service is not None

    def test_from_dict_account(self):
        data = {'resourceType': 'ChargeItem', 'account': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.account is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'ChargeItem', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.note is not None

    def test_from_dict_supporting_information(self):
        data = {'resourceType': 'ChargeItem', 'supportingInformation': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ChargeItem)
        assert result.supportingInformation is not None


class TestGetPathChargeItem:

    def test_get_path_id(self):
        resource = ChargeItem()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ChargeItem()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ChargeItem()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ChargeItem.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ChargeItem()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ChargeItem()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ChargeItem()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ChargeItem()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ChargeItem()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ChargeItem()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ChargeItem()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = ChargeItem()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_definition_uri(self):
        resource = ChargeItem()
        resource.definitionUri = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'definitionUri')
        assert result is not None

    def test_get_path_definition_canonical(self):
        resource = ChargeItem()
        resource.definitionCanonical = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'definitionCanonical')
        assert result is not None

    def test_get_path_status(self):
        resource = ChargeItem()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_part_of(self):
        resource = ChargeItem()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'partOf')
        assert result is not None

    def test_get_path_code(self):
        resource = ChargeItem()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_subject(self):
        resource = ChargeItem()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_context(self):
        resource = ChargeItem()
        resource.context = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'context')
        assert result is not None

    def test_get_path_performer(self):
        resource = ChargeItem()
        resource.performer = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performer')
        assert result is not None

    def test_get_path_performing_organization(self):
        resource = ChargeItem()
        resource.performingOrganization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performingOrganization')
        assert result is not None

    def test_get_path_requesting_organization(self):
        resource = ChargeItem()
        resource.requestingOrganization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'requestingOrganization')
        assert result is not None

    def test_get_path_cost_center(self):
        resource = ChargeItem()
        resource.costCenter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'costCenter')
        assert result is not None

    def test_get_path_quantity(self):
        resource = ChargeItem()
        resource.quantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'quantity')
        assert result is not None

    def test_get_path_bodysite(self):
        resource = ChargeItem()
        resource.bodysite = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'bodysite')
        assert result is not None

    def test_get_path_factor_override(self):
        resource = ChargeItem()
        resource.factorOverride = 3.14
        result = zato.fhir_r4_0_1_core.get_path(resource, 'factorOverride')
        assert result is not None

    def test_get_path_price_override(self):
        resource = ChargeItem()
        resource.priceOverride = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priceOverride')
        assert result is not None

    def test_get_path_override_reason(self):
        resource = ChargeItem()
        resource.overrideReason = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'overrideReason')
        assert result is not None

    def test_get_path_enterer(self):
        resource = ChargeItem()
        resource.enterer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'enterer')
        assert result is not None

    def test_get_path_entered_date(self):
        resource = ChargeItem()
        resource.enteredDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'enteredDate')
        assert result is not None

    def test_get_path_reason(self):
        resource = ChargeItem()
        resource.reason = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reason')
        assert result is not None

    def test_get_path_service(self):
        resource = ChargeItem()
        resource.service = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'service')
        assert result is not None

    def test_get_path_account(self):
        resource = ChargeItem()
        resource.account = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'account')
        assert result is not None

    def test_get_path_note(self):
        resource = ChargeItem()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_supporting_information(self):
        resource = ChargeItem()
        resource.supportingInformation = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supportingInformation')
        assert result is not None


class TestSetPathChargeItem:

    def test_set_path_id(self):
        resource = ChargeItem()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ChargeItem()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ChargeItem.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ChargeItem()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ChargeItem()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ChargeItem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ChargeItem()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ChargeItem()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ChargeItem()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ChargeItem()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = ChargeItem()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_definition_uri(self):
        resource = ChargeItem()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'definitionUri', value)
        assert result is True
        assert resource.definitionUri is not None

    def test_set_path_definition_canonical(self):
        resource = ChargeItem()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'definitionCanonical', value)
        assert result is True
        assert resource.definitionCanonical is not None

    def test_set_path_status(self):
        resource = ChargeItem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_part_of(self):
        resource = ChargeItem()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'partOf', value)
        assert result is True
        assert resource.partOf is not None

    def test_set_path_code(self):
        resource = ChargeItem()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_subject(self):
        resource = ChargeItem()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_context(self):
        resource = ChargeItem()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'context', value)
        assert result is True
        assert resource.context is not None

    def test_set_path_performer(self):
        resource = ChargeItem()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performer', value)
        assert result is True
        assert resource.performer is not None

    def test_set_path_performing_organization(self):
        resource = ChargeItem()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performingOrganization', value)
        assert result is True
        assert resource.performingOrganization is not None

    def test_set_path_requesting_organization(self):
        resource = ChargeItem()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'requestingOrganization', value)
        assert result is True
        assert resource.requestingOrganization is not None

    def test_set_path_cost_center(self):
        resource = ChargeItem()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'costCenter', value)
        assert result is True
        assert resource.costCenter is not None

    def test_set_path_quantity(self):
        resource = ChargeItem()
        value = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'quantity', value)
        assert result is True
        assert resource.quantity is not None

    def test_set_path_bodysite(self):
        resource = ChargeItem()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'bodysite', value)
        assert result is True
        assert resource.bodysite is not None

    def test_set_path_factor_override(self):
        resource = ChargeItem()
        value = 3.14
        result = zato.fhir_r4_0_1_core.set_path(resource, 'factorOverride', value)
        assert result is True
        assert resource.factorOverride is not None

    def test_set_path_price_override(self):
        resource = ChargeItem()
        value = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priceOverride', value)
        assert result is True
        assert resource.priceOverride is not None

    def test_set_path_override_reason(self):
        resource = ChargeItem()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'overrideReason', value)
        assert result is True
        assert resource.overrideReason is not None

    def test_set_path_enterer(self):
        resource = ChargeItem()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'enterer', value)
        assert result is True
        assert resource.enterer is not None

    def test_set_path_entered_date(self):
        resource = ChargeItem()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'enteredDate', value)
        assert result is True
        assert resource.enteredDate is not None

    def test_set_path_reason(self):
        resource = ChargeItem()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reason', value)
        assert result is True
        assert resource.reason is not None

    def test_set_path_service(self):
        resource = ChargeItem()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'service', value)
        assert result is True
        assert resource.service is not None

    def test_set_path_account(self):
        resource = ChargeItem()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'account', value)
        assert result is True
        assert resource.account is not None

    def test_set_path_note(self):
        resource = ChargeItem()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_supporting_information(self):
        resource = ChargeItem()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supportingInformation', value)
        assert result is True
        assert resource.supportingInformation is not None


class TestParsePathChargeItem:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ChargeItem.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ChargeItem.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ChargeItem.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
