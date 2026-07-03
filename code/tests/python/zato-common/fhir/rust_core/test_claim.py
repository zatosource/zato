# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Claim


class TestToDictClaim:

    def test_to_dict_empty(self):
        resource = Claim()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Claim'

    def test_to_dict_with_id(self):
        resource = Claim()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Claim()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Claim)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Claim()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Claim()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Claim()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Claim()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Claim()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Claim()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Claim()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Claim()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Claim()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = Claim()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_type(self):
        resource = Claim()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_sub_type(self):
        resource = Claim()
        resource.subType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subType' in result

    def test_to_dict_use(self):
        resource = Claim()
        resource.use = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'use' in result

    def test_to_dict_patient(self):
        resource = Claim()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_billable_period(self):
        resource = Claim()
        resource.billablePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'billablePeriod' in result

    def test_to_dict_created(self):
        resource = Claim()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'created' in result

    def test_to_dict_enterer(self):
        resource = Claim()
        resource.enterer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'enterer' in result

    def test_to_dict_insurer(self):
        resource = Claim()
        resource.insurer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'insurer' in result

    def test_to_dict_provider(self):
        resource = Claim()
        resource.provider = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'provider' in result

    def test_to_dict_priority(self):
        resource = Claim()
        resource.priority = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priority' in result

    def test_to_dict_funds_reserve(self):
        resource = Claim()
        resource.fundsReserve = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'fundsReserve' in result

    def test_to_dict_related(self):
        resource = Claim()
        resource.related = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'related' in result

    def test_to_dict_prescription(self):
        resource = Claim()
        resource.prescription = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'prescription' in result

    def test_to_dict_original_prescription(self):
        resource = Claim()
        resource.originalPrescription = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'originalPrescription' in result

    def test_to_dict_payee(self):
        resource = Claim()
        resource.payee = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'payee' in result

    def test_to_dict_referral(self):
        resource = Claim()
        resource.referral = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'referral' in result

    def test_to_dict_facility(self):
        resource = Claim()
        resource.facility = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'facility' in result

    def test_to_dict_care_team(self):
        resource = Claim()
        resource.careTeam = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'careTeam' in result

    def test_to_dict_supporting_info(self):
        resource = Claim()
        resource.supportingInfo = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supportingInfo' in result

    def test_to_dict_diagnosis(self):
        resource = Claim()
        resource.diagnosis = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'diagnosis' in result

    def test_to_dict_procedure(self):
        resource = Claim()
        resource.procedure = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'procedure' in result

    def test_to_dict_insurance(self):
        resource = Claim()
        resource.insurance = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'insurance' in result

    def test_to_dict_accident(self):
        resource = Claim()
        resource.accident = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'accident' in result

    def test_to_dict_item(self):
        resource = Claim()
        resource.item = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'item' in result

    def test_to_dict_total(self):
        resource = Claim()
        resource.total = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'total' in result


class TestFromDictClaim:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Claim', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert isinstance(result, Claim)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Claim'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert isinstance(result, Claim)

    def test_from_dict_id(self):
        data = {'resourceType': 'Claim', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Claim', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Claim', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Claim', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Claim', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Claim', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Claim', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Claim', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Claim', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Claim', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.status is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'Claim', 'type': {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.type_ is not None

    def test_from_dict_sub_type(self):
        data = {'resourceType': 'Claim',
         'subType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                     'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.subType is not None

    def test_from_dict_use(self):
        data = {'resourceType': 'Claim', 'use': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.use is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'Claim', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.patient is not None

    def test_from_dict_billable_period(self):
        data = {'resourceType': 'Claim', 'billablePeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.billablePeriod is not None

    def test_from_dict_created(self):
        data = {'resourceType': 'Claim', 'created': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.created is not None

    def test_from_dict_enterer(self):
        data = {'resourceType': 'Claim', 'enterer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.enterer is not None

    def test_from_dict_insurer(self):
        data = {'resourceType': 'Claim', 'insurer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.insurer is not None

    def test_from_dict_provider(self):
        data = {'resourceType': 'Claim', 'provider': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.provider is not None

    def test_from_dict_priority(self):
        data = {'priority': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'Claim'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.priority is not None

    def test_from_dict_funds_reserve(self):
        data = {'fundsReserve': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'},
         'resourceType': 'Claim'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.fundsReserve is not None

    def test_from_dict_related(self):
        data = {'resourceType': 'Claim', 'related': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.related is not None

    def test_from_dict_prescription(self):
        data = {'resourceType': 'Claim', 'prescription': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.prescription is not None

    def test_from_dict_original_prescription(self):
        data = {'resourceType': 'Claim', 'originalPrescription': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.originalPrescription is not None

    def test_from_dict_payee(self):
        data = {'resourceType': 'Claim', 'payee': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.payee is not None

    def test_from_dict_referral(self):
        data = {'resourceType': 'Claim', 'referral': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.referral is not None

    def test_from_dict_facility(self):
        data = {'resourceType': 'Claim', 'facility': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.facility is not None

    def test_from_dict_care_team(self):
        data = {'resourceType': 'Claim', 'careTeam': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.careTeam is not None

    def test_from_dict_supporting_info(self):
        data = {'resourceType': 'Claim', 'supportingInfo': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.supportingInfo is not None

    def test_from_dict_diagnosis(self):
        data = {'resourceType': 'Claim', 'diagnosis': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.diagnosis is not None

    def test_from_dict_procedure(self):
        data = {'resourceType': 'Claim', 'procedure': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.procedure is not None

    def test_from_dict_insurance(self):
        data = {'resourceType': 'Claim', 'insurance': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.insurance is not None

    def test_from_dict_accident(self):
        data = {'resourceType': 'Claim', 'accident': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.accident is not None

    def test_from_dict_item(self):
        data = {'resourceType': 'Claim', 'item': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.item is not None

    def test_from_dict_total(self):
        data = {'resourceType': 'Claim', 'total': {'value': 'test'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Claim)
        assert result.total is not None


class TestGetPathClaim:

    def test_get_path_id(self):
        resource = Claim()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Claim()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Claim()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Claim.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Claim()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Claim()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Claim()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Claim()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Claim()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Claim()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Claim()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Claim()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = Claim()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_type(self):
        resource = Claim()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_sub_type(self):
        resource = Claim()
        resource.subType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subType')
        assert result is not None

    def test_get_path_use(self):
        resource = Claim()
        resource.use = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'use')
        assert result is not None

    def test_get_path_patient(self):
        resource = Claim()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_billable_period(self):
        resource = Claim()
        resource.billablePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'billablePeriod')
        assert result is not None

    def test_get_path_created(self):
        resource = Claim()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'created')
        assert result is not None

    def test_get_path_enterer(self):
        resource = Claim()
        resource.enterer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'enterer')
        assert result is not None

    def test_get_path_insurer(self):
        resource = Claim()
        resource.insurer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'insurer')
        assert result is not None

    def test_get_path_provider(self):
        resource = Claim()
        resource.provider = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'provider')
        assert result is not None

    def test_get_path_priority(self):
        resource = Claim()
        resource.priority = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priority')
        assert result is not None

    def test_get_path_funds_reserve(self):
        resource = Claim()
        resource.fundsReserve = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'fundsReserve')
        assert result is not None

    def test_get_path_related(self):
        resource = Claim()
        resource.related = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'related')
        assert result is not None

    def test_get_path_prescription(self):
        resource = Claim()
        resource.prescription = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'prescription')
        assert result is not None

    def test_get_path_original_prescription(self):
        resource = Claim()
        resource.originalPrescription = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'originalPrescription')
        assert result is not None

    def test_get_path_payee(self):
        resource = Claim()
        resource.payee = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'payee')
        assert result is not None

    def test_get_path_referral(self):
        resource = Claim()
        resource.referral = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'referral')
        assert result is not None

    def test_get_path_facility(self):
        resource = Claim()
        resource.facility = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'facility')
        assert result is not None

    def test_get_path_care_team(self):
        resource = Claim()
        resource.careTeam = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'careTeam')
        assert result is not None

    def test_get_path_supporting_info(self):
        resource = Claim()
        resource.supportingInfo = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supportingInfo')
        assert result is not None

    def test_get_path_diagnosis(self):
        resource = Claim()
        resource.diagnosis = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'diagnosis')
        assert result is not None

    def test_get_path_procedure(self):
        resource = Claim()
        resource.procedure = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'procedure')
        assert result is not None

    def test_get_path_insurance(self):
        resource = Claim()
        resource.insurance = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'insurance')
        assert result is not None

    def test_get_path_accident(self):
        resource = Claim()
        resource.accident = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'accident')
        assert result is not None

    def test_get_path_item(self):
        resource = Claim()
        resource.item = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'item')
        assert result is not None

    def test_get_path_total(self):
        resource = Claim()
        resource.total = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'total')
        assert result is not None


class TestSetPathClaim:

    def test_set_path_id(self):
        resource = Claim()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Claim()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Claim.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Claim()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Claim()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Claim()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Claim()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Claim()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Claim()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Claim()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Claim()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = Claim()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_type(self):
        resource = Claim()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_sub_type(self):
        resource = Claim()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subType', value)
        assert result is True
        assert resource.subType is not None

    def test_set_path_use(self):
        resource = Claim()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'use', value)
        assert result is True
        assert resource.use is not None

    def test_set_path_patient(self):
        resource = Claim()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_billable_period(self):
        resource = Claim()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'billablePeriod', value)
        assert result is True
        assert resource.billablePeriod is not None

    def test_set_path_created(self):
        resource = Claim()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'created', value)
        assert result is True
        assert resource.created is not None

    def test_set_path_enterer(self):
        resource = Claim()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'enterer', value)
        assert result is True
        assert resource.enterer is not None

    def test_set_path_insurer(self):
        resource = Claim()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'insurer', value)
        assert result is True
        assert resource.insurer is not None

    def test_set_path_provider(self):
        resource = Claim()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'provider', value)
        assert result is True
        assert resource.provider is not None

    def test_set_path_priority(self):
        resource = Claim()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priority', value)
        assert result is True
        assert resource.priority is not None

    def test_set_path_funds_reserve(self):
        resource = Claim()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'fundsReserve', value)
        assert result is True
        assert resource.fundsReserve is not None

    def test_set_path_related(self):
        resource = Claim()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'related', value)
        assert result is True
        assert resource.related is not None

    def test_set_path_prescription(self):
        resource = Claim()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'prescription', value)
        assert result is True
        assert resource.prescription is not None

    def test_set_path_original_prescription(self):
        resource = Claim()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'originalPrescription', value)
        assert result is True
        assert resource.originalPrescription is not None

    def test_set_path_payee(self):
        resource = Claim()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'payee', value)
        assert result is True
        assert resource.payee is not None

    def test_set_path_referral(self):
        resource = Claim()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'referral', value)
        assert result is True
        assert resource.referral is not None

    def test_set_path_facility(self):
        resource = Claim()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'facility', value)
        assert result is True
        assert resource.facility is not None

    def test_set_path_care_team(self):
        resource = Claim()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'careTeam', value)
        assert result is True
        assert resource.careTeam is not None

    def test_set_path_supporting_info(self):
        resource = Claim()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supportingInfo', value)
        assert result is True
        assert resource.supportingInfo is not None

    def test_set_path_diagnosis(self):
        resource = Claim()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'diagnosis', value)
        assert result is True
        assert resource.diagnosis is not None

    def test_set_path_procedure(self):
        resource = Claim()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'procedure', value)
        assert result is True
        assert resource.procedure is not None

    def test_set_path_insurance(self):
        resource = Claim()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'insurance', value)
        assert result is True
        assert resource.insurance is not None

    def test_set_path_accident(self):
        resource = Claim()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'accident', value)
        assert result is True
        assert resource.accident is not None

    def test_set_path_item(self):
        resource = Claim()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'item', value)
        assert result is True
        assert resource.item is not None

    def test_set_path_total(self):
        resource = Claim()
        value = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'total', value)
        assert result is True
        assert resource.total is not None


class TestParsePathClaim:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Claim.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Claim.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Claim.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
