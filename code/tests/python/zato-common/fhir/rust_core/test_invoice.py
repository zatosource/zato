# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Invoice


class TestToDictInvoice:

    def test_to_dict_empty(self):
        resource = Invoice()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Invoice'

    def test_to_dict_with_id(self):
        resource = Invoice()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Invoice()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Invoice)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Invoice()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Invoice()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Invoice()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Invoice()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Invoice()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Invoice()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Invoice()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Invoice()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Invoice()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = Invoice()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_cancelled_reason(self):
        resource = Invoice()
        resource.cancelledReason = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'cancelledReason' in result

    def test_to_dict_type(self):
        resource = Invoice()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_subject(self):
        resource = Invoice()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_recipient(self):
        resource = Invoice()
        resource.recipient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recipient' in result

    def test_to_dict_date(self):
        resource = Invoice()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_participant(self):
        resource = Invoice()
        resource.participant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'participant' in result

    def test_to_dict_issuer(self):
        resource = Invoice()
        resource.issuer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'issuer' in result

    def test_to_dict_account(self):
        resource = Invoice()
        resource.account = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'account' in result

    def test_to_dict_line_item(self):
        resource = Invoice()
        resource.lineItem = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lineItem' in result

    def test_to_dict_total_price_component(self):
        resource = Invoice()
        resource.totalPriceComponent = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'totalPriceComponent' in result

    def test_to_dict_total_net(self):
        resource = Invoice()
        resource.totalNet = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'totalNet' in result

    def test_to_dict_total_gross(self):
        resource = Invoice()
        resource.totalGross = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'totalGross' in result

    def test_to_dict_payment_terms(self):
        resource = Invoice()
        resource.paymentTerms = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'paymentTerms' in result

    def test_to_dict_note(self):
        resource = Invoice()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result


class TestFromDictInvoice:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Invoice', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert isinstance(result, Invoice)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Invoice'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert isinstance(result, Invoice)

    def test_from_dict_id(self):
        data = {'resourceType': 'Invoice', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Invoice', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Invoice', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Invoice', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Invoice', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Invoice', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Invoice', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Invoice', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Invoice', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Invoice', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.status is not None

    def test_from_dict_cancelled_reason(self):
        data = {'resourceType': 'Invoice', 'cancelledReason': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.cancelledReason is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'Invoice',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.type_ is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'Invoice', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.subject is not None

    def test_from_dict_recipient(self):
        data = {'resourceType': 'Invoice', 'recipient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.recipient is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'Invoice', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.date is not None

    def test_from_dict_participant(self):
        data = {'resourceType': 'Invoice', 'participant': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.participant is not None

    def test_from_dict_issuer(self):
        data = {'resourceType': 'Invoice', 'issuer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.issuer is not None

    def test_from_dict_account(self):
        data = {'resourceType': 'Invoice', 'account': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.account is not None

    def test_from_dict_line_item(self):
        data = {'resourceType': 'Invoice', 'lineItem': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.lineItem is not None

    def test_from_dict_total_price_component(self):
        data = {'resourceType': 'Invoice', 'totalPriceComponent': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.totalPriceComponent is not None

    def test_from_dict_total_net(self):
        data = {'resourceType': 'Invoice', 'totalNet': {'value': 'test'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.totalNet is not None

    def test_from_dict_total_gross(self):
        data = {'resourceType': 'Invoice', 'totalGross': {'value': 'test'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.totalGross is not None

    def test_from_dict_payment_terms(self):
        data = {'resourceType': 'Invoice', 'paymentTerms': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.paymentTerms is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'Invoice', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Invoice)
        assert result.note is not None


class TestGetPathInvoice:

    def test_get_path_id(self):
        resource = Invoice()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Invoice()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Invoice()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Invoice.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Invoice()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Invoice()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Invoice()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Invoice()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Invoice()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Invoice()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Invoice()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Invoice()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = Invoice()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_cancelled_reason(self):
        resource = Invoice()
        resource.cancelledReason = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'cancelledReason')
        assert result is not None

    def test_get_path_type(self):
        resource = Invoice()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_subject(self):
        resource = Invoice()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_recipient(self):
        resource = Invoice()
        resource.recipient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recipient')
        assert result is not None

    def test_get_path_date(self):
        resource = Invoice()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_participant(self):
        resource = Invoice()
        resource.participant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'participant')
        assert result is not None

    def test_get_path_issuer(self):
        resource = Invoice()
        resource.issuer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'issuer')
        assert result is not None

    def test_get_path_account(self):
        resource = Invoice()
        resource.account = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'account')
        assert result is not None

    def test_get_path_line_item(self):
        resource = Invoice()
        resource.lineItem = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lineItem')
        assert result is not None

    def test_get_path_total_price_component(self):
        resource = Invoice()
        resource.totalPriceComponent = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'totalPriceComponent')
        assert result is not None

    def test_get_path_total_net(self):
        resource = Invoice()
        resource.totalNet = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'totalNet')
        assert result is not None

    def test_get_path_total_gross(self):
        resource = Invoice()
        resource.totalGross = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'totalGross')
        assert result is not None

    def test_get_path_payment_terms(self):
        resource = Invoice()
        resource.paymentTerms = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'paymentTerms')
        assert result is not None

    def test_get_path_note(self):
        resource = Invoice()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None


class TestSetPathInvoice:

    def test_set_path_id(self):
        resource = Invoice()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Invoice()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Invoice.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Invoice()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Invoice()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Invoice()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Invoice()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Invoice()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Invoice()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Invoice()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Invoice()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = Invoice()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_cancelled_reason(self):
        resource = Invoice()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'cancelledReason', value)
        assert result is True
        assert resource.cancelledReason is not None

    def test_set_path_type(self):
        resource = Invoice()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_subject(self):
        resource = Invoice()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_recipient(self):
        resource = Invoice()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recipient', value)
        assert result is True
        assert resource.recipient is not None

    def test_set_path_date(self):
        resource = Invoice()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_participant(self):
        resource = Invoice()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'participant', value)
        assert result is True
        assert resource.participant is not None

    def test_set_path_issuer(self):
        resource = Invoice()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'issuer', value)
        assert result is True
        assert resource.issuer is not None

    def test_set_path_account(self):
        resource = Invoice()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'account', value)
        assert result is True
        assert resource.account is not None

    def test_set_path_line_item(self):
        resource = Invoice()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lineItem', value)
        assert result is True
        assert resource.lineItem is not None

    def test_set_path_total_price_component(self):
        resource = Invoice()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'totalPriceComponent', value)
        assert result is True
        assert resource.totalPriceComponent is not None

    def test_set_path_total_net(self):
        resource = Invoice()
        value = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'totalNet', value)
        assert result is True
        assert resource.totalNet is not None

    def test_set_path_total_gross(self):
        resource = Invoice()
        value = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'totalGross', value)
        assert result is True
        assert resource.totalGross is not None

    def test_set_path_payment_terms(self):
        resource = Invoice()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'paymentTerms', value)
        assert result is True
        assert resource.paymentTerms is not None

    def test_set_path_note(self):
        resource = Invoice()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None


class TestParsePathInvoice:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Invoice.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Invoice.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Invoice.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
