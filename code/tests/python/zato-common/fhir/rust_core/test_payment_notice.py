# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import PaymentNotice


class TestToDictPaymentNotice:

    def test_to_dict_empty(self):
        resource = PaymentNotice()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'PaymentNotice'

    def test_to_dict_with_id(self):
        resource = PaymentNotice()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = PaymentNotice()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, PaymentNotice)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = PaymentNotice()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = PaymentNotice()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = PaymentNotice()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = PaymentNotice()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = PaymentNotice()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = PaymentNotice()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = PaymentNotice()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = PaymentNotice()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = PaymentNotice()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = PaymentNotice()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_request(self):
        resource = PaymentNotice()
        resource.request = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'request' in result

    def test_to_dict_response(self):
        resource = PaymentNotice()
        resource.response = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'response' in result

    def test_to_dict_created(self):
        resource = PaymentNotice()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'created' in result

    def test_to_dict_provider(self):
        resource = PaymentNotice()
        resource.provider = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'provider' in result

    def test_to_dict_payment(self):
        resource = PaymentNotice()
        resource.payment = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'payment' in result

    def test_to_dict_payment_date(self):
        resource = PaymentNotice()
        resource.paymentDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'paymentDate' in result

    def test_to_dict_payee(self):
        resource = PaymentNotice()
        resource.payee = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'payee' in result

    def test_to_dict_recipient(self):
        resource = PaymentNotice()
        resource.recipient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recipient' in result

    def test_to_dict_amount(self):
        resource = PaymentNotice()
        resource.amount = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'amount' in result

    def test_to_dict_payment_status(self):
        resource = PaymentNotice()
        resource.paymentStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'paymentStatus' in result


class TestFromDictPaymentNotice:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'PaymentNotice', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert isinstance(result, PaymentNotice)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'PaymentNotice'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert isinstance(result, PaymentNotice)

    def test_from_dict_id(self):
        data = {'resourceType': 'PaymentNotice', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'PaymentNotice', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'PaymentNotice', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'PaymentNotice', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'PaymentNotice', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'PaymentNotice', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'PaymentNotice', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'PaymentNotice', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'PaymentNotice', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'PaymentNotice', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.status is not None

    def test_from_dict_request(self):
        data = {'resourceType': 'PaymentNotice', 'request': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.request is not None

    def test_from_dict_response(self):
        data = {'resourceType': 'PaymentNotice', 'response': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.response is not None

    def test_from_dict_created(self):
        data = {'resourceType': 'PaymentNotice', 'created': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.created is not None

    def test_from_dict_provider(self):
        data = {'resourceType': 'PaymentNotice', 'provider': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.provider is not None

    def test_from_dict_payment(self):
        data = {'resourceType': 'PaymentNotice', 'payment': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.payment is not None

    def test_from_dict_payment_date(self):
        data = {'resourceType': 'PaymentNotice', 'paymentDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.paymentDate is not None

    def test_from_dict_payee(self):
        data = {'resourceType': 'PaymentNotice', 'payee': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.payee is not None

    def test_from_dict_recipient(self):
        data = {'resourceType': 'PaymentNotice', 'recipient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.recipient is not None

    def test_from_dict_amount(self):
        data = {'resourceType': 'PaymentNotice', 'amount': {'value': 'test'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.amount is not None

    def test_from_dict_payment_status(self):
        data = {'paymentStatus': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'},
         'resourceType': 'PaymentNotice'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentNotice)
        assert result.paymentStatus is not None


class TestGetPathPaymentNotice:

    def test_get_path_id(self):
        resource = PaymentNotice()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = PaymentNotice()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = PaymentNotice()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'PaymentNotice.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = PaymentNotice()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = PaymentNotice()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = PaymentNotice()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = PaymentNotice()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = PaymentNotice()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = PaymentNotice()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = PaymentNotice()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = PaymentNotice()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = PaymentNotice()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_request(self):
        resource = PaymentNotice()
        resource.request = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'request')
        assert result is not None

    def test_get_path_response(self):
        resource = PaymentNotice()
        resource.response = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'response')
        assert result is not None

    def test_get_path_created(self):
        resource = PaymentNotice()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'created')
        assert result is not None

    def test_get_path_provider(self):
        resource = PaymentNotice()
        resource.provider = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'provider')
        assert result is not None

    def test_get_path_payment(self):
        resource = PaymentNotice()
        resource.payment = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'payment')
        assert result is not None

    def test_get_path_payment_date(self):
        resource = PaymentNotice()
        resource.paymentDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'paymentDate')
        assert result is not None

    def test_get_path_payee(self):
        resource = PaymentNotice()
        resource.payee = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'payee')
        assert result is not None

    def test_get_path_recipient(self):
        resource = PaymentNotice()
        resource.recipient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recipient')
        assert result is not None

    def test_get_path_amount(self):
        resource = PaymentNotice()
        resource.amount = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'amount')
        assert result is not None

    def test_get_path_payment_status(self):
        resource = PaymentNotice()
        resource.paymentStatus = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'paymentStatus')
        assert result is not None


class TestSetPathPaymentNotice:

    def test_set_path_id(self):
        resource = PaymentNotice()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = PaymentNotice()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'PaymentNotice.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = PaymentNotice()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = PaymentNotice()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = PaymentNotice()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = PaymentNotice()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = PaymentNotice()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = PaymentNotice()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = PaymentNotice()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = PaymentNotice()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = PaymentNotice()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_request(self):
        resource = PaymentNotice()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'request', value)
        assert result is True
        assert resource.request is not None

    def test_set_path_response(self):
        resource = PaymentNotice()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'response', value)
        assert result is True
        assert resource.response is not None

    def test_set_path_created(self):
        resource = PaymentNotice()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'created', value)
        assert result is True
        assert resource.created is not None

    def test_set_path_provider(self):
        resource = PaymentNotice()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'provider', value)
        assert result is True
        assert resource.provider is not None

    def test_set_path_payment(self):
        resource = PaymentNotice()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'payment', value)
        assert result is True
        assert resource.payment is not None

    def test_set_path_payment_date(self):
        resource = PaymentNotice()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'paymentDate', value)
        assert result is True
        assert resource.paymentDate is not None

    def test_set_path_payee(self):
        resource = PaymentNotice()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'payee', value)
        assert result is True
        assert resource.payee is not None

    def test_set_path_recipient(self):
        resource = PaymentNotice()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recipient', value)
        assert result is True
        assert resource.recipient is not None

    def test_set_path_amount(self):
        resource = PaymentNotice()
        value = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'amount', value)
        assert result is True
        assert resource.amount is not None

    def test_set_path_payment_status(self):
        resource = PaymentNotice()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'paymentStatus', value)
        assert result is True
        assert resource.paymentStatus is not None


class TestParsePathPaymentNotice:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('PaymentNotice.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('PaymentNotice.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('PaymentNotice.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
