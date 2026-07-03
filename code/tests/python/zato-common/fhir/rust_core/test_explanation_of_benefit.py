# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ExplanationOfBenefit


class TestToDictExplanationOfBenefit:

    def test_to_dict_empty(self):
        resource = ExplanationOfBenefit()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ExplanationOfBenefit'

    def test_to_dict_with_id(self):
        resource = ExplanationOfBenefit()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ExplanationOfBenefit()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ExplanationOfBenefit)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ExplanationOfBenefit()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ExplanationOfBenefit()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ExplanationOfBenefit()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ExplanationOfBenefit()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ExplanationOfBenefit()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ExplanationOfBenefit()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ExplanationOfBenefit()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ExplanationOfBenefit()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = ExplanationOfBenefit()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = ExplanationOfBenefit()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_type(self):
        resource = ExplanationOfBenefit()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_sub_type(self):
        resource = ExplanationOfBenefit()
        resource.subType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subType' in result

    def test_to_dict_use(self):
        resource = ExplanationOfBenefit()
        resource.use = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'use' in result

    def test_to_dict_patient(self):
        resource = ExplanationOfBenefit()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_billable_period(self):
        resource = ExplanationOfBenefit()
        resource.billablePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'billablePeriod' in result

    def test_to_dict_created(self):
        resource = ExplanationOfBenefit()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'created' in result

    def test_to_dict_enterer(self):
        resource = ExplanationOfBenefit()
        resource.enterer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'enterer' in result

    def test_to_dict_insurer(self):
        resource = ExplanationOfBenefit()
        resource.insurer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'insurer' in result

    def test_to_dict_provider(self):
        resource = ExplanationOfBenefit()
        resource.provider = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'provider' in result

    def test_to_dict_priority(self):
        resource = ExplanationOfBenefit()
        resource.priority = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priority' in result

    def test_to_dict_funds_reserve_requested(self):
        resource = ExplanationOfBenefit()
        resource.fundsReserveRequested = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'fundsReserveRequested' in result

    def test_to_dict_funds_reserve(self):
        resource = ExplanationOfBenefit()
        resource.fundsReserve = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'fundsReserve' in result

    def test_to_dict_related(self):
        resource = ExplanationOfBenefit()
        resource.related = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'related' in result

    def test_to_dict_prescription(self):
        resource = ExplanationOfBenefit()
        resource.prescription = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'prescription' in result

    def test_to_dict_original_prescription(self):
        resource = ExplanationOfBenefit()
        resource.originalPrescription = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'originalPrescription' in result

    def test_to_dict_payee(self):
        resource = ExplanationOfBenefit()
        resource.payee = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'payee' in result

    def test_to_dict_referral(self):
        resource = ExplanationOfBenefit()
        resource.referral = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'referral' in result

    def test_to_dict_facility(self):
        resource = ExplanationOfBenefit()
        resource.facility = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'facility' in result

    def test_to_dict_claim(self):
        resource = ExplanationOfBenefit()
        resource.claim = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'claim' in result

    def test_to_dict_claim_response(self):
        resource = ExplanationOfBenefit()
        resource.claimResponse = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'claimResponse' in result

    def test_to_dict_outcome(self):
        resource = ExplanationOfBenefit()
        resource.outcome = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'outcome' in result

    def test_to_dict_disposition(self):
        resource = ExplanationOfBenefit()
        resource.disposition = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'disposition' in result

    def test_to_dict_pre_auth_ref(self):
        resource = ExplanationOfBenefit()
        resource.preAuthRef = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'preAuthRef' in result

    def test_to_dict_pre_auth_ref_period(self):
        resource = ExplanationOfBenefit()
        resource.preAuthRefPeriod = [{'start': '2024-01-01', 'end': '2024-12-31'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'preAuthRefPeriod' in result

    def test_to_dict_care_team(self):
        resource = ExplanationOfBenefit()
        resource.careTeam = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'careTeam' in result

    def test_to_dict_supporting_info(self):
        resource = ExplanationOfBenefit()
        resource.supportingInfo = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supportingInfo' in result

    def test_to_dict_diagnosis(self):
        resource = ExplanationOfBenefit()
        resource.diagnosis = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'diagnosis' in result

    def test_to_dict_procedure(self):
        resource = ExplanationOfBenefit()
        resource.procedure = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'procedure' in result

    def test_to_dict_precedence(self):
        resource = ExplanationOfBenefit()
        resource.precedence = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'precedence' in result

    def test_to_dict_insurance(self):
        resource = ExplanationOfBenefit()
        resource.insurance = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'insurance' in result

    def test_to_dict_accident(self):
        resource = ExplanationOfBenefit()
        resource.accident = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'accident' in result

    def test_to_dict_item(self):
        resource = ExplanationOfBenefit()
        resource.item = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'item' in result

    def test_to_dict_add_item(self):
        resource = ExplanationOfBenefit()
        resource.addItem = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'addItem' in result

    def test_to_dict_adjudication(self):
        resource = ExplanationOfBenefit()
        resource.adjudication = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'adjudication' in result

    def test_to_dict_total(self):
        resource = ExplanationOfBenefit()
        resource.total = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'total' in result

    def test_to_dict_payment(self):
        resource = ExplanationOfBenefit()
        resource.payment = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'payment' in result

    def test_to_dict_form_code(self):
        resource = ExplanationOfBenefit()
        resource.formCode = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'formCode' in result

    def test_to_dict_form(self):
        resource = ExplanationOfBenefit()
        resource.form = {'contentType': 'text/plain', 'data': 'SGVsbG8='}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'form' in result

    def test_to_dict_process_note(self):
        resource = ExplanationOfBenefit()
        resource.processNote = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'processNote' in result

    def test_to_dict_benefit_period(self):
        resource = ExplanationOfBenefit()
        resource.benefitPeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'benefitPeriod' in result

    def test_to_dict_benefit_balance(self):
        resource = ExplanationOfBenefit()
        resource.benefitBalance = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'benefitBalance' in result


class TestFromDictExplanationOfBenefit:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert isinstance(result, ExplanationOfBenefit)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ExplanationOfBenefit'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert isinstance(result, ExplanationOfBenefit)

    def test_from_dict_id(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.status is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'ExplanationOfBenefit',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.type_ is not None

    def test_from_dict_sub_type(self):
        data = {'resourceType': 'ExplanationOfBenefit',
         'subType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                     'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.subType is not None

    def test_from_dict_use(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'use': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.use is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.patient is not None

    def test_from_dict_billable_period(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'billablePeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.billablePeriod is not None

    def test_from_dict_created(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'created': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.created is not None

    def test_from_dict_enterer(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'enterer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.enterer is not None

    def test_from_dict_insurer(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'insurer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.insurer is not None

    def test_from_dict_provider(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'provider': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.provider is not None

    def test_from_dict_priority(self):
        data = {'priority': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'ExplanationOfBenefit'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.priority is not None

    def test_from_dict_funds_reserve_requested(self):
        data = {'fundsReserveRequested': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                   'text': 'Test concept'},
         'resourceType': 'ExplanationOfBenefit'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.fundsReserveRequested is not None

    def test_from_dict_funds_reserve(self):
        data = {'fundsReserve': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'},
         'resourceType': 'ExplanationOfBenefit'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.fundsReserve is not None

    def test_from_dict_related(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'related': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.related is not None

    def test_from_dict_prescription(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'prescription': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.prescription is not None

    def test_from_dict_original_prescription(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'originalPrescription': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.originalPrescription is not None

    def test_from_dict_payee(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'payee': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.payee is not None

    def test_from_dict_referral(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'referral': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.referral is not None

    def test_from_dict_facility(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'facility': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.facility is not None

    def test_from_dict_claim(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'claim': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.claim is not None

    def test_from_dict_claim_response(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'claimResponse': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.claimResponse is not None

    def test_from_dict_outcome(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'outcome': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.outcome is not None

    def test_from_dict_disposition(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'disposition': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.disposition is not None

    def test_from_dict_pre_auth_ref(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'preAuthRef': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.preAuthRef is not None

    def test_from_dict_pre_auth_ref_period(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'preAuthRefPeriod': [{'start': '2024-01-01', 'end': '2024-12-31'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.preAuthRefPeriod is not None

    def test_from_dict_care_team(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'careTeam': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.careTeam is not None

    def test_from_dict_supporting_info(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'supportingInfo': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.supportingInfo is not None

    def test_from_dict_diagnosis(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'diagnosis': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.diagnosis is not None

    def test_from_dict_procedure(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'procedure': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.procedure is not None

    def test_from_dict_precedence(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'precedence': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.precedence is not None

    def test_from_dict_insurance(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'insurance': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.insurance is not None

    def test_from_dict_accident(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'accident': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.accident is not None

    def test_from_dict_item(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'item': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.item is not None

    def test_from_dict_add_item(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'addItem': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.addItem is not None

    def test_from_dict_adjudication(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'adjudication': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.adjudication is not None

    def test_from_dict_total(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'total': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.total is not None

    def test_from_dict_payment(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'payment': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.payment is not None

    def test_from_dict_form_code(self):
        data = {'formCode': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'ExplanationOfBenefit'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.formCode is not None

    def test_from_dict_form(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'form': {'contentType': 'text/plain', 'data': 'SGVsbG8='}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.form is not None

    def test_from_dict_process_note(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'processNote': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.processNote is not None

    def test_from_dict_benefit_period(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'benefitPeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.benefitPeriod is not None

    def test_from_dict_benefit_balance(self):
        data = {'resourceType': 'ExplanationOfBenefit', 'benefitBalance': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ExplanationOfBenefit)
        assert result.benefitBalance is not None


class TestGetPathExplanationOfBenefit:

    def test_get_path_id(self):
        resource = ExplanationOfBenefit()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ExplanationOfBenefit()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ExplanationOfBenefit()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ExplanationOfBenefit.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ExplanationOfBenefit()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ExplanationOfBenefit()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ExplanationOfBenefit()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ExplanationOfBenefit()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ExplanationOfBenefit()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ExplanationOfBenefit()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ExplanationOfBenefit()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = ExplanationOfBenefit()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = ExplanationOfBenefit()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_type(self):
        resource = ExplanationOfBenefit()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_sub_type(self):
        resource = ExplanationOfBenefit()
        resource.subType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subType')
        assert result is not None

    def test_get_path_use(self):
        resource = ExplanationOfBenefit()
        resource.use = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'use')
        assert result is not None

    def test_get_path_patient(self):
        resource = ExplanationOfBenefit()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_billable_period(self):
        resource = ExplanationOfBenefit()
        resource.billablePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'billablePeriod')
        assert result is not None

    def test_get_path_created(self):
        resource = ExplanationOfBenefit()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'created')
        assert result is not None

    def test_get_path_enterer(self):
        resource = ExplanationOfBenefit()
        resource.enterer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'enterer')
        assert result is not None

    def test_get_path_insurer(self):
        resource = ExplanationOfBenefit()
        resource.insurer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'insurer')
        assert result is not None

    def test_get_path_provider(self):
        resource = ExplanationOfBenefit()
        resource.provider = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'provider')
        assert result is not None

    def test_get_path_priority(self):
        resource = ExplanationOfBenefit()
        resource.priority = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priority')
        assert result is not None

    def test_get_path_funds_reserve_requested(self):
        resource = ExplanationOfBenefit()
        resource.fundsReserveRequested = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'fundsReserveRequested')
        assert result is not None

    def test_get_path_funds_reserve(self):
        resource = ExplanationOfBenefit()
        resource.fundsReserve = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'fundsReserve')
        assert result is not None

    def test_get_path_related(self):
        resource = ExplanationOfBenefit()
        resource.related = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'related')
        assert result is not None

    def test_get_path_prescription(self):
        resource = ExplanationOfBenefit()
        resource.prescription = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'prescription')
        assert result is not None

    def test_get_path_original_prescription(self):
        resource = ExplanationOfBenefit()
        resource.originalPrescription = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'originalPrescription')
        assert result is not None

    def test_get_path_payee(self):
        resource = ExplanationOfBenefit()
        resource.payee = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'payee')
        assert result is not None

    def test_get_path_referral(self):
        resource = ExplanationOfBenefit()
        resource.referral = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'referral')
        assert result is not None

    def test_get_path_facility(self):
        resource = ExplanationOfBenefit()
        resource.facility = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'facility')
        assert result is not None

    def test_get_path_claim(self):
        resource = ExplanationOfBenefit()
        resource.claim = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'claim')
        assert result is not None

    def test_get_path_claim_response(self):
        resource = ExplanationOfBenefit()
        resource.claimResponse = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'claimResponse')
        assert result is not None

    def test_get_path_outcome(self):
        resource = ExplanationOfBenefit()
        resource.outcome = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'outcome')
        assert result is not None

    def test_get_path_disposition(self):
        resource = ExplanationOfBenefit()
        resource.disposition = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'disposition')
        assert result is not None

    def test_get_path_pre_auth_ref(self):
        resource = ExplanationOfBenefit()
        resource.preAuthRef = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'preAuthRef')
        assert result is not None

    def test_get_path_pre_auth_ref_period(self):
        resource = ExplanationOfBenefit()
        resource.preAuthRefPeriod = [{'start': '2024-01-01', 'end': '2024-12-31'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'preAuthRefPeriod')
        assert result is not None

    def test_get_path_care_team(self):
        resource = ExplanationOfBenefit()
        resource.careTeam = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'careTeam')
        assert result is not None

    def test_get_path_supporting_info(self):
        resource = ExplanationOfBenefit()
        resource.supportingInfo = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supportingInfo')
        assert result is not None

    def test_get_path_diagnosis(self):
        resource = ExplanationOfBenefit()
        resource.diagnosis = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'diagnosis')
        assert result is not None

    def test_get_path_procedure(self):
        resource = ExplanationOfBenefit()
        resource.procedure = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'procedure')
        assert result is not None

    def test_get_path_precedence(self):
        resource = ExplanationOfBenefit()
        resource.precedence = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'precedence')
        assert result is not None

    def test_get_path_insurance(self):
        resource = ExplanationOfBenefit()
        resource.insurance = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'insurance')
        assert result is not None

    def test_get_path_accident(self):
        resource = ExplanationOfBenefit()
        resource.accident = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'accident')
        assert result is not None

    def test_get_path_item(self):
        resource = ExplanationOfBenefit()
        resource.item = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'item')
        assert result is not None

    def test_get_path_add_item(self):
        resource = ExplanationOfBenefit()
        resource.addItem = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'addItem')
        assert result is not None

    def test_get_path_adjudication(self):
        resource = ExplanationOfBenefit()
        resource.adjudication = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'adjudication')
        assert result is not None

    def test_get_path_total(self):
        resource = ExplanationOfBenefit()
        resource.total = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'total')
        assert result is not None

    def test_get_path_payment(self):
        resource = ExplanationOfBenefit()
        resource.payment = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'payment')
        assert result is not None

    def test_get_path_form_code(self):
        resource = ExplanationOfBenefit()
        resource.formCode = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'formCode')
        assert result is not None

    def test_get_path_form(self):
        resource = ExplanationOfBenefit()
        resource.form = {'contentType': 'text/plain', 'data': 'SGVsbG8='}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'form')
        assert result is not None

    def test_get_path_process_note(self):
        resource = ExplanationOfBenefit()
        resource.processNote = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'processNote')
        assert result is not None

    def test_get_path_benefit_period(self):
        resource = ExplanationOfBenefit()
        resource.benefitPeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'benefitPeriod')
        assert result is not None

    def test_get_path_benefit_balance(self):
        resource = ExplanationOfBenefit()
        resource.benefitBalance = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'benefitBalance')
        assert result is not None


class TestSetPathExplanationOfBenefit:

    def test_set_path_id(self):
        resource = ExplanationOfBenefit()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ExplanationOfBenefit()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ExplanationOfBenefit.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ExplanationOfBenefit()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ExplanationOfBenefit()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ExplanationOfBenefit()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ExplanationOfBenefit()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ExplanationOfBenefit()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ExplanationOfBenefit()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ExplanationOfBenefit()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = ExplanationOfBenefit()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = ExplanationOfBenefit()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_type(self):
        resource = ExplanationOfBenefit()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_sub_type(self):
        resource = ExplanationOfBenefit()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subType', value)
        assert result is True
        assert resource.subType is not None

    def test_set_path_use(self):
        resource = ExplanationOfBenefit()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'use', value)
        assert result is True
        assert resource.use is not None

    def test_set_path_patient(self):
        resource = ExplanationOfBenefit()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_billable_period(self):
        resource = ExplanationOfBenefit()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'billablePeriod', value)
        assert result is True
        assert resource.billablePeriod is not None

    def test_set_path_created(self):
        resource = ExplanationOfBenefit()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'created', value)
        assert result is True
        assert resource.created is not None

    def test_set_path_enterer(self):
        resource = ExplanationOfBenefit()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'enterer', value)
        assert result is True
        assert resource.enterer is not None

    def test_set_path_insurer(self):
        resource = ExplanationOfBenefit()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'insurer', value)
        assert result is True
        assert resource.insurer is not None

    def test_set_path_provider(self):
        resource = ExplanationOfBenefit()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'provider', value)
        assert result is True
        assert resource.provider is not None

    def test_set_path_priority(self):
        resource = ExplanationOfBenefit()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priority', value)
        assert result is True
        assert resource.priority is not None

    def test_set_path_funds_reserve_requested(self):
        resource = ExplanationOfBenefit()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'fundsReserveRequested', value)
        assert result is True
        assert resource.fundsReserveRequested is not None

    def test_set_path_funds_reserve(self):
        resource = ExplanationOfBenefit()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'fundsReserve', value)
        assert result is True
        assert resource.fundsReserve is not None

    def test_set_path_related(self):
        resource = ExplanationOfBenefit()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'related', value)
        assert result is True
        assert resource.related is not None

    def test_set_path_prescription(self):
        resource = ExplanationOfBenefit()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'prescription', value)
        assert result is True
        assert resource.prescription is not None

    def test_set_path_original_prescription(self):
        resource = ExplanationOfBenefit()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'originalPrescription', value)
        assert result is True
        assert resource.originalPrescription is not None

    def test_set_path_payee(self):
        resource = ExplanationOfBenefit()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'payee', value)
        assert result is True
        assert resource.payee is not None

    def test_set_path_referral(self):
        resource = ExplanationOfBenefit()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'referral', value)
        assert result is True
        assert resource.referral is not None

    def test_set_path_facility(self):
        resource = ExplanationOfBenefit()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'facility', value)
        assert result is True
        assert resource.facility is not None

    def test_set_path_claim(self):
        resource = ExplanationOfBenefit()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'claim', value)
        assert result is True
        assert resource.claim is not None

    def test_set_path_claim_response(self):
        resource = ExplanationOfBenefit()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'claimResponse', value)
        assert result is True
        assert resource.claimResponse is not None

    def test_set_path_outcome(self):
        resource = ExplanationOfBenefit()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'outcome', value)
        assert result is True
        assert resource.outcome is not None

    def test_set_path_disposition(self):
        resource = ExplanationOfBenefit()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'disposition', value)
        assert result is True
        assert resource.disposition is not None

    def test_set_path_pre_auth_ref(self):
        resource = ExplanationOfBenefit()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'preAuthRef', value)
        assert result is True
        assert resource.preAuthRef is not None

    def test_set_path_pre_auth_ref_period(self):
        resource = ExplanationOfBenefit()
        value = [{'start': '2024-01-01', 'end': '2024-12-31'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'preAuthRefPeriod', value)
        assert result is True
        assert resource.preAuthRefPeriod is not None

    def test_set_path_care_team(self):
        resource = ExplanationOfBenefit()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'careTeam', value)
        assert result is True
        assert resource.careTeam is not None

    def test_set_path_supporting_info(self):
        resource = ExplanationOfBenefit()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supportingInfo', value)
        assert result is True
        assert resource.supportingInfo is not None

    def test_set_path_diagnosis(self):
        resource = ExplanationOfBenefit()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'diagnosis', value)
        assert result is True
        assert resource.diagnosis is not None

    def test_set_path_procedure(self):
        resource = ExplanationOfBenefit()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'procedure', value)
        assert result is True
        assert resource.procedure is not None

    def test_set_path_precedence(self):
        resource = ExplanationOfBenefit()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'precedence', value)
        assert result is True
        assert resource.precedence is not None

    def test_set_path_insurance(self):
        resource = ExplanationOfBenefit()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'insurance', value)
        assert result is True
        assert resource.insurance is not None

    def test_set_path_accident(self):
        resource = ExplanationOfBenefit()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'accident', value)
        assert result is True
        assert resource.accident is not None

    def test_set_path_item(self):
        resource = ExplanationOfBenefit()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'item', value)
        assert result is True
        assert resource.item is not None

    def test_set_path_add_item(self):
        resource = ExplanationOfBenefit()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'addItem', value)
        assert result is True
        assert resource.addItem is not None

    def test_set_path_adjudication(self):
        resource = ExplanationOfBenefit()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'adjudication', value)
        assert result is True
        assert resource.adjudication is not None

    def test_set_path_total(self):
        resource = ExplanationOfBenefit()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'total', value)
        assert result is True
        assert resource.total is not None

    def test_set_path_payment(self):
        resource = ExplanationOfBenefit()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'payment', value)
        assert result is True
        assert resource.payment is not None

    def test_set_path_form_code(self):
        resource = ExplanationOfBenefit()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'formCode', value)
        assert result is True
        assert resource.formCode is not None

    def test_set_path_form(self):
        resource = ExplanationOfBenefit()
        value = {'contentType': 'text/plain', 'data': 'SGVsbG8='}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'form', value)
        assert result is True
        assert resource.form is not None

    def test_set_path_process_note(self):
        resource = ExplanationOfBenefit()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'processNote', value)
        assert result is True
        assert resource.processNote is not None

    def test_set_path_benefit_period(self):
        resource = ExplanationOfBenefit()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'benefitPeriod', value)
        assert result is True
        assert resource.benefitPeriod is not None

    def test_set_path_benefit_balance(self):
        resource = ExplanationOfBenefit()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'benefitBalance', value)
        assert result is True
        assert resource.benefitBalance is not None


class TestParsePathExplanationOfBenefit:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ExplanationOfBenefit.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ExplanationOfBenefit.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ExplanationOfBenefit.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
