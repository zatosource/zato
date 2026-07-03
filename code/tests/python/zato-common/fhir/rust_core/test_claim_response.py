# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ClaimResponse


class TestToDictClaimResponse:

    def test_to_dict_empty(self):
        resource = ClaimResponse()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ClaimResponse'

    def test_to_dict_with_id(self):
        resource = ClaimResponse()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ClaimResponse()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ClaimResponse)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ClaimResponse()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ClaimResponse()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ClaimResponse()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ClaimResponse()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ClaimResponse()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ClaimResponse()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ClaimResponse()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ClaimResponse()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = ClaimResponse()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = ClaimResponse()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_type(self):
        resource = ClaimResponse()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_sub_type(self):
        resource = ClaimResponse()
        resource.subType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subType' in result

    def test_to_dict_use(self):
        resource = ClaimResponse()
        resource.use = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'use' in result

    def test_to_dict_patient(self):
        resource = ClaimResponse()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_created(self):
        resource = ClaimResponse()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'created' in result

    def test_to_dict_insurer(self):
        resource = ClaimResponse()
        resource.insurer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'insurer' in result

    def test_to_dict_requestor(self):
        resource = ClaimResponse()
        resource.requestor = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'requestor' in result

    def test_to_dict_request(self):
        resource = ClaimResponse()
        resource.request = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'request' in result

    def test_to_dict_outcome(self):
        resource = ClaimResponse()
        resource.outcome = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'outcome' in result

    def test_to_dict_disposition(self):
        resource = ClaimResponse()
        resource.disposition = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'disposition' in result

    def test_to_dict_pre_auth_ref(self):
        resource = ClaimResponse()
        resource.preAuthRef = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'preAuthRef' in result

    def test_to_dict_pre_auth_period(self):
        resource = ClaimResponse()
        resource.preAuthPeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'preAuthPeriod' in result

    def test_to_dict_payee_type(self):
        resource = ClaimResponse()
        resource.payeeType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'payeeType' in result

    def test_to_dict_item(self):
        resource = ClaimResponse()
        resource.item = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'item' in result

    def test_to_dict_add_item(self):
        resource = ClaimResponse()
        resource.addItem = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'addItem' in result

    def test_to_dict_adjudication(self):
        resource = ClaimResponse()
        resource.adjudication = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'adjudication' in result

    def test_to_dict_total(self):
        resource = ClaimResponse()
        resource.total = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'total' in result

    def test_to_dict_payment(self):
        resource = ClaimResponse()
        resource.payment = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'payment' in result

    def test_to_dict_funds_reserve(self):
        resource = ClaimResponse()
        resource.fundsReserve = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'fundsReserve' in result

    def test_to_dict_form_code(self):
        resource = ClaimResponse()
        resource.formCode = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'formCode' in result

    def test_to_dict_form(self):
        resource = ClaimResponse()
        resource.form = {'contentType': 'text/plain', 'data': 'SGVsbG8='}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'form' in result

    def test_to_dict_process_note(self):
        resource = ClaimResponse()
        resource.processNote = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'processNote' in result

    def test_to_dict_communication_request(self):
        resource = ClaimResponse()
        resource.communicationRequest = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'communicationRequest' in result

    def test_to_dict_insurance(self):
        resource = ClaimResponse()
        resource.insurance = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'insurance' in result

    def test_to_dict_error(self):
        resource = ClaimResponse()
        resource.error = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'error' in result


class TestFromDictClaimResponse:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ClaimResponse', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert isinstance(result, ClaimResponse)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ClaimResponse'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert isinstance(result, ClaimResponse)

    def test_from_dict_id(self):
        data = {'resourceType': 'ClaimResponse', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ClaimResponse', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ClaimResponse', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ClaimResponse', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ClaimResponse', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ClaimResponse', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ClaimResponse', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ClaimResponse', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'ClaimResponse', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'ClaimResponse', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.status is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'ClaimResponse',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.type_ is not None

    def test_from_dict_sub_type(self):
        data = {'resourceType': 'ClaimResponse',
         'subType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                     'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.subType is not None

    def test_from_dict_use(self):
        data = {'resourceType': 'ClaimResponse', 'use': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.use is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'ClaimResponse', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.patient is not None

    def test_from_dict_created(self):
        data = {'resourceType': 'ClaimResponse', 'created': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.created is not None

    def test_from_dict_insurer(self):
        data = {'resourceType': 'ClaimResponse', 'insurer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.insurer is not None

    def test_from_dict_requestor(self):
        data = {'resourceType': 'ClaimResponse', 'requestor': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.requestor is not None

    def test_from_dict_request(self):
        data = {'resourceType': 'ClaimResponse', 'request': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.request is not None

    def test_from_dict_outcome(self):
        data = {'resourceType': 'ClaimResponse', 'outcome': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.outcome is not None

    def test_from_dict_disposition(self):
        data = {'resourceType': 'ClaimResponse', 'disposition': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.disposition is not None

    def test_from_dict_pre_auth_ref(self):
        data = {'resourceType': 'ClaimResponse', 'preAuthRef': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.preAuthRef is not None

    def test_from_dict_pre_auth_period(self):
        data = {'resourceType': 'ClaimResponse', 'preAuthPeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.preAuthPeriod is not None

    def test_from_dict_payee_type(self):
        data = {'payeeType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'},
         'resourceType': 'ClaimResponse'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.payeeType is not None

    def test_from_dict_item(self):
        data = {'resourceType': 'ClaimResponse', 'item': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.item is not None

    def test_from_dict_add_item(self):
        data = {'resourceType': 'ClaimResponse', 'addItem': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.addItem is not None

    def test_from_dict_adjudication(self):
        data = {'resourceType': 'ClaimResponse', 'adjudication': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.adjudication is not None

    def test_from_dict_total(self):
        data = {'resourceType': 'ClaimResponse', 'total': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.total is not None

    def test_from_dict_payment(self):
        data = {'resourceType': 'ClaimResponse', 'payment': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.payment is not None

    def test_from_dict_funds_reserve(self):
        data = {'fundsReserve': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'},
         'resourceType': 'ClaimResponse'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.fundsReserve is not None

    def test_from_dict_form_code(self):
        data = {'formCode': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'ClaimResponse'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.formCode is not None

    def test_from_dict_form(self):
        data = {'resourceType': 'ClaimResponse', 'form': {'contentType': 'text/plain', 'data': 'SGVsbG8='}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.form is not None

    def test_from_dict_process_note(self):
        data = {'resourceType': 'ClaimResponse', 'processNote': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.processNote is not None

    def test_from_dict_communication_request(self):
        data = {'resourceType': 'ClaimResponse', 'communicationRequest': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.communicationRequest is not None

    def test_from_dict_insurance(self):
        data = {'resourceType': 'ClaimResponse', 'insurance': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.insurance is not None

    def test_from_dict_error(self):
        data = {'resourceType': 'ClaimResponse', 'error': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ClaimResponse)
        assert result.error is not None


class TestGetPathClaimResponse:

    def test_get_path_id(self):
        resource = ClaimResponse()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ClaimResponse()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ClaimResponse()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ClaimResponse.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ClaimResponse()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ClaimResponse()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ClaimResponse()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ClaimResponse()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ClaimResponse()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ClaimResponse()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ClaimResponse()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = ClaimResponse()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = ClaimResponse()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_type(self):
        resource = ClaimResponse()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_sub_type(self):
        resource = ClaimResponse()
        resource.subType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subType')
        assert result is not None

    def test_get_path_use(self):
        resource = ClaimResponse()
        resource.use = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'use')
        assert result is not None

    def test_get_path_patient(self):
        resource = ClaimResponse()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_created(self):
        resource = ClaimResponse()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'created')
        assert result is not None

    def test_get_path_insurer(self):
        resource = ClaimResponse()
        resource.insurer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'insurer')
        assert result is not None

    def test_get_path_requestor(self):
        resource = ClaimResponse()
        resource.requestor = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'requestor')
        assert result is not None

    def test_get_path_request(self):
        resource = ClaimResponse()
        resource.request = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'request')
        assert result is not None

    def test_get_path_outcome(self):
        resource = ClaimResponse()
        resource.outcome = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'outcome')
        assert result is not None

    def test_get_path_disposition(self):
        resource = ClaimResponse()
        resource.disposition = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'disposition')
        assert result is not None

    def test_get_path_pre_auth_ref(self):
        resource = ClaimResponse()
        resource.preAuthRef = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'preAuthRef')
        assert result is not None

    def test_get_path_pre_auth_period(self):
        resource = ClaimResponse()
        resource.preAuthPeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'preAuthPeriod')
        assert result is not None

    def test_get_path_payee_type(self):
        resource = ClaimResponse()
        resource.payeeType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'payeeType')
        assert result is not None

    def test_get_path_item(self):
        resource = ClaimResponse()
        resource.item = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'item')
        assert result is not None

    def test_get_path_add_item(self):
        resource = ClaimResponse()
        resource.addItem = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'addItem')
        assert result is not None

    def test_get_path_adjudication(self):
        resource = ClaimResponse()
        resource.adjudication = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'adjudication')
        assert result is not None

    def test_get_path_total(self):
        resource = ClaimResponse()
        resource.total = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'total')
        assert result is not None

    def test_get_path_payment(self):
        resource = ClaimResponse()
        resource.payment = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'payment')
        assert result is not None

    def test_get_path_funds_reserve(self):
        resource = ClaimResponse()
        resource.fundsReserve = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'fundsReserve')
        assert result is not None

    def test_get_path_form_code(self):
        resource = ClaimResponse()
        resource.formCode = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'formCode')
        assert result is not None

    def test_get_path_form(self):
        resource = ClaimResponse()
        resource.form = {'contentType': 'text/plain', 'data': 'SGVsbG8='}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'form')
        assert result is not None

    def test_get_path_process_note(self):
        resource = ClaimResponse()
        resource.processNote = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'processNote')
        assert result is not None

    def test_get_path_communication_request(self):
        resource = ClaimResponse()
        resource.communicationRequest = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'communicationRequest')
        assert result is not None

    def test_get_path_insurance(self):
        resource = ClaimResponse()
        resource.insurance = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'insurance')
        assert result is not None

    def test_get_path_error(self):
        resource = ClaimResponse()
        resource.error = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'error')
        assert result is not None


class TestSetPathClaimResponse:

    def test_set_path_id(self):
        resource = ClaimResponse()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ClaimResponse()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ClaimResponse.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ClaimResponse()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ClaimResponse()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ClaimResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ClaimResponse()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ClaimResponse()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ClaimResponse()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ClaimResponse()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = ClaimResponse()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = ClaimResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_type(self):
        resource = ClaimResponse()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_sub_type(self):
        resource = ClaimResponse()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subType', value)
        assert result is True
        assert resource.subType is not None

    def test_set_path_use(self):
        resource = ClaimResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'use', value)
        assert result is True
        assert resource.use is not None

    def test_set_path_patient(self):
        resource = ClaimResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_created(self):
        resource = ClaimResponse()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'created', value)
        assert result is True
        assert resource.created is not None

    def test_set_path_insurer(self):
        resource = ClaimResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'insurer', value)
        assert result is True
        assert resource.insurer is not None

    def test_set_path_requestor(self):
        resource = ClaimResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'requestor', value)
        assert result is True
        assert resource.requestor is not None

    def test_set_path_request(self):
        resource = ClaimResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'request', value)
        assert result is True
        assert resource.request is not None

    def test_set_path_outcome(self):
        resource = ClaimResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'outcome', value)
        assert result is True
        assert resource.outcome is not None

    def test_set_path_disposition(self):
        resource = ClaimResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'disposition', value)
        assert result is True
        assert resource.disposition is not None

    def test_set_path_pre_auth_ref(self):
        resource = ClaimResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'preAuthRef', value)
        assert result is True
        assert resource.preAuthRef is not None

    def test_set_path_pre_auth_period(self):
        resource = ClaimResponse()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'preAuthPeriod', value)
        assert result is True
        assert resource.preAuthPeriod is not None

    def test_set_path_payee_type(self):
        resource = ClaimResponse()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'payeeType', value)
        assert result is True
        assert resource.payeeType is not None

    def test_set_path_item(self):
        resource = ClaimResponse()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'item', value)
        assert result is True
        assert resource.item is not None

    def test_set_path_add_item(self):
        resource = ClaimResponse()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'addItem', value)
        assert result is True
        assert resource.addItem is not None

    def test_set_path_adjudication(self):
        resource = ClaimResponse()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'adjudication', value)
        assert result is True
        assert resource.adjudication is not None

    def test_set_path_total(self):
        resource = ClaimResponse()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'total', value)
        assert result is True
        assert resource.total is not None

    def test_set_path_payment(self):
        resource = ClaimResponse()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'payment', value)
        assert result is True
        assert resource.payment is not None

    def test_set_path_funds_reserve(self):
        resource = ClaimResponse()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'fundsReserve', value)
        assert result is True
        assert resource.fundsReserve is not None

    def test_set_path_form_code(self):
        resource = ClaimResponse()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'formCode', value)
        assert result is True
        assert resource.formCode is not None

    def test_set_path_form(self):
        resource = ClaimResponse()
        value = {'contentType': 'text/plain', 'data': 'SGVsbG8='}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'form', value)
        assert result is True
        assert resource.form is not None

    def test_set_path_process_note(self):
        resource = ClaimResponse()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'processNote', value)
        assert result is True
        assert resource.processNote is not None

    def test_set_path_communication_request(self):
        resource = ClaimResponse()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'communicationRequest', value)
        assert result is True
        assert resource.communicationRequest is not None

    def test_set_path_insurance(self):
        resource = ClaimResponse()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'insurance', value)
        assert result is True
        assert resource.insurance is not None

    def test_set_path_error(self):
        resource = ClaimResponse()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'error', value)
        assert result is True
        assert resource.error is not None


class TestParsePathClaimResponse:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ClaimResponse.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ClaimResponse.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ClaimResponse.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
