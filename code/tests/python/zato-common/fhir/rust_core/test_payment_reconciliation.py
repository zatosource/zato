# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import PaymentReconciliation


class TestToDictPaymentReconciliation:

    def test_to_dict_empty(self):
        resource = PaymentReconciliation()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'PaymentReconciliation'

    def test_to_dict_with_id(self):
        resource = PaymentReconciliation()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = PaymentReconciliation()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, PaymentReconciliation)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = PaymentReconciliation()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = PaymentReconciliation()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = PaymentReconciliation()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = PaymentReconciliation()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = PaymentReconciliation()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = PaymentReconciliation()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = PaymentReconciliation()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = PaymentReconciliation()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = PaymentReconciliation()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = PaymentReconciliation()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_period(self):
        resource = PaymentReconciliation()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'period' in result

    def test_to_dict_created(self):
        resource = PaymentReconciliation()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'created' in result

    def test_to_dict_payment_issuer(self):
        resource = PaymentReconciliation()
        resource.paymentIssuer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'paymentIssuer' in result

    def test_to_dict_request(self):
        resource = PaymentReconciliation()
        resource.request = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'request' in result

    def test_to_dict_requestor(self):
        resource = PaymentReconciliation()
        resource.requestor = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'requestor' in result

    def test_to_dict_outcome(self):
        resource = PaymentReconciliation()
        resource.outcome = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'outcome' in result

    def test_to_dict_disposition(self):
        resource = PaymentReconciliation()
        resource.disposition = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'disposition' in result

    def test_to_dict_payment_date(self):
        resource = PaymentReconciliation()
        resource.paymentDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'paymentDate' in result

    def test_to_dict_payment_amount(self):
        resource = PaymentReconciliation()
        resource.paymentAmount = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'paymentAmount' in result

    def test_to_dict_payment_identifier(self):
        resource = PaymentReconciliation()
        resource.paymentIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'paymentIdentifier' in result

    def test_to_dict_detail(self):
        resource = PaymentReconciliation()
        resource.detail = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'detail' in result

    def test_to_dict_form_code(self):
        resource = PaymentReconciliation()
        resource.formCode = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'formCode' in result

    def test_to_dict_process_note(self):
        resource = PaymentReconciliation()
        resource.processNote = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'processNote' in result


class TestFromDictPaymentReconciliation:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'PaymentReconciliation', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert isinstance(result, PaymentReconciliation)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'PaymentReconciliation'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert isinstance(result, PaymentReconciliation)

    def test_from_dict_id(self):
        data = {'resourceType': 'PaymentReconciliation', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'PaymentReconciliation', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'PaymentReconciliation', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'PaymentReconciliation', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'PaymentReconciliation', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'PaymentReconciliation', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'PaymentReconciliation', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'PaymentReconciliation', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'PaymentReconciliation', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'PaymentReconciliation', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.status is not None

    def test_from_dict_period(self):
        data = {'resourceType': 'PaymentReconciliation', 'period': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.period is not None

    def test_from_dict_created(self):
        data = {'resourceType': 'PaymentReconciliation', 'created': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.created is not None

    def test_from_dict_payment_issuer(self):
        data = {'resourceType': 'PaymentReconciliation', 'paymentIssuer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.paymentIssuer is not None

    def test_from_dict_request(self):
        data = {'resourceType': 'PaymentReconciliation', 'request': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.request is not None

    def test_from_dict_requestor(self):
        data = {'resourceType': 'PaymentReconciliation', 'requestor': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.requestor is not None

    def test_from_dict_outcome(self):
        data = {'resourceType': 'PaymentReconciliation', 'outcome': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.outcome is not None

    def test_from_dict_disposition(self):
        data = {'resourceType': 'PaymentReconciliation', 'disposition': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.disposition is not None

    def test_from_dict_payment_date(self):
        data = {'resourceType': 'PaymentReconciliation', 'paymentDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.paymentDate is not None

    def test_from_dict_payment_amount(self):
        data = {'resourceType': 'PaymentReconciliation', 'paymentAmount': {'value': 'test'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.paymentAmount is not None

    def test_from_dict_payment_identifier(self):
        data = {'resourceType': 'PaymentReconciliation', 'paymentIdentifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.paymentIdentifier is not None

    def test_from_dict_detail(self):
        data = {'resourceType': 'PaymentReconciliation', 'detail': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.detail is not None

    def test_from_dict_form_code(self):
        data = {'formCode': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'PaymentReconciliation'}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.formCode is not None

    def test_from_dict_process_note(self):
        data = {'resourceType': 'PaymentReconciliation', 'processNote': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, PaymentReconciliation)
        assert result.processNote is not None


class TestGetPathPaymentReconciliation:

    def test_get_path_id(self):
        resource = PaymentReconciliation()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = PaymentReconciliation()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = PaymentReconciliation()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'PaymentReconciliation.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = PaymentReconciliation()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = PaymentReconciliation()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = PaymentReconciliation()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = PaymentReconciliation()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = PaymentReconciliation()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = PaymentReconciliation()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = PaymentReconciliation()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = PaymentReconciliation()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = PaymentReconciliation()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_period(self):
        resource = PaymentReconciliation()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'period')
        assert result is not None

    def test_get_path_created(self):
        resource = PaymentReconciliation()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'created')
        assert result is not None

    def test_get_path_payment_issuer(self):
        resource = PaymentReconciliation()
        resource.paymentIssuer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'paymentIssuer')
        assert result is not None

    def test_get_path_request(self):
        resource = PaymentReconciliation()
        resource.request = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'request')
        assert result is not None

    def test_get_path_requestor(self):
        resource = PaymentReconciliation()
        resource.requestor = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'requestor')
        assert result is not None

    def test_get_path_outcome(self):
        resource = PaymentReconciliation()
        resource.outcome = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'outcome')
        assert result is not None

    def test_get_path_disposition(self):
        resource = PaymentReconciliation()
        resource.disposition = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'disposition')
        assert result is not None

    def test_get_path_payment_date(self):
        resource = PaymentReconciliation()
        resource.paymentDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'paymentDate')
        assert result is not None

    def test_get_path_payment_amount(self):
        resource = PaymentReconciliation()
        resource.paymentAmount = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'paymentAmount')
        assert result is not None

    def test_get_path_payment_identifier(self):
        resource = PaymentReconciliation()
        resource.paymentIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'paymentIdentifier')
        assert result is not None

    def test_get_path_detail(self):
        resource = PaymentReconciliation()
        resource.detail = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'detail')
        assert result is not None

    def test_get_path_form_code(self):
        resource = PaymentReconciliation()
        resource.formCode = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'formCode')
        assert result is not None

    def test_get_path_process_note(self):
        resource = PaymentReconciliation()
        resource.processNote = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'processNote')
        assert result is not None


class TestSetPathPaymentReconciliation:

    def test_set_path_id(self):
        resource = PaymentReconciliation()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = PaymentReconciliation()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'PaymentReconciliation.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = PaymentReconciliation()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = PaymentReconciliation()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = PaymentReconciliation()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = PaymentReconciliation()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = PaymentReconciliation()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = PaymentReconciliation()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = PaymentReconciliation()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = PaymentReconciliation()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = PaymentReconciliation()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_period(self):
        resource = PaymentReconciliation()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'period', value)
        assert result is True
        assert resource.period is not None

    def test_set_path_created(self):
        resource = PaymentReconciliation()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'created', value)
        assert result is True
        assert resource.created is not None

    def test_set_path_payment_issuer(self):
        resource = PaymentReconciliation()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'paymentIssuer', value)
        assert result is True
        assert resource.paymentIssuer is not None

    def test_set_path_request(self):
        resource = PaymentReconciliation()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'request', value)
        assert result is True
        assert resource.request is not None

    def test_set_path_requestor(self):
        resource = PaymentReconciliation()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'requestor', value)
        assert result is True
        assert resource.requestor is not None

    def test_set_path_outcome(self):
        resource = PaymentReconciliation()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'outcome', value)
        assert result is True
        assert resource.outcome is not None

    def test_set_path_disposition(self):
        resource = PaymentReconciliation()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'disposition', value)
        assert result is True
        assert resource.disposition is not None

    def test_set_path_payment_date(self):
        resource = PaymentReconciliation()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'paymentDate', value)
        assert result is True
        assert resource.paymentDate is not None

    def test_set_path_payment_amount(self):
        resource = PaymentReconciliation()
        value = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'paymentAmount', value)
        assert result is True
        assert resource.paymentAmount is not None

    def test_set_path_payment_identifier(self):
        resource = PaymentReconciliation()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'paymentIdentifier', value)
        assert result is True
        assert resource.paymentIdentifier is not None

    def test_set_path_detail(self):
        resource = PaymentReconciliation()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'detail', value)
        assert result is True
        assert resource.detail is not None

    def test_set_path_form_code(self):
        resource = PaymentReconciliation()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'formCode', value)
        assert result is True
        assert resource.formCode is not None

    def test_set_path_process_note(self):
        resource = PaymentReconciliation()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'processNote', value)
        assert result is True
        assert resource.processNote is not None


class TestParsePathPaymentReconciliation:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('PaymentReconciliation.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('PaymentReconciliation.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('PaymentReconciliation.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
