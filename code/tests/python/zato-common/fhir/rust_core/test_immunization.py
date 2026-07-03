# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Immunization


class TestToDictImmunization:

    def test_to_dict_empty(self):
        resource = Immunization()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Immunization'

    def test_to_dict_with_id(self):
        resource = Immunization()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Immunization()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Immunization)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Immunization()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Immunization()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Immunization()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Immunization()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Immunization()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Immunization()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Immunization()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Immunization()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Immunization()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = Immunization()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_status_reason(self):
        resource = Immunization()
        resource.statusReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'statusReason' in result

    def test_to_dict_vaccine_code(self):
        resource = Immunization()
        resource.vaccineCode = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'vaccineCode' in result

    def test_to_dict_patient(self):
        resource = Immunization()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_encounter(self):
        resource = Immunization()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_recorded(self):
        resource = Immunization()
        resource.recorded = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recorded' in result

    def test_to_dict_primary_source(self):
        resource = Immunization()
        resource.primarySource = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'primarySource' in result

    def test_to_dict_report_origin(self):
        resource = Immunization()
        resource.reportOrigin = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reportOrigin' in result

    def test_to_dict_location(self):
        resource = Immunization()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'location' in result

    def test_to_dict_manufacturer(self):
        resource = Immunization()
        resource.manufacturer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'manufacturer' in result

    def test_to_dict_lot_number(self):
        resource = Immunization()
        resource.lotNumber = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lotNumber' in result

    def test_to_dict_expiration_date(self):
        resource = Immunization()
        resource.expirationDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'expirationDate' in result

    def test_to_dict_site(self):
        resource = Immunization()
        resource.site = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'site' in result

    def test_to_dict_route(self):
        resource = Immunization()
        resource.route = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'route' in result

    def test_to_dict_dose_quantity(self):
        resource = Immunization()
        resource.doseQuantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'doseQuantity' in result

    def test_to_dict_performer(self):
        resource = Immunization()
        resource.performer = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performer' in result

    def test_to_dict_note(self):
        resource = Immunization()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_reason_code(self):
        resource = Immunization()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonCode' in result

    def test_to_dict_reason_reference(self):
        resource = Immunization()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonReference' in result

    def test_to_dict_is_subpotent(self):
        resource = Immunization()
        resource.isSubpotent = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'isSubpotent' in result

    def test_to_dict_subpotent_reason(self):
        resource = Immunization()
        resource.subpotentReason = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subpotentReason' in result

    def test_to_dict_education(self):
        resource = Immunization()
        resource.education = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'education' in result

    def test_to_dict_program_eligibility(self):
        resource = Immunization()
        resource.programEligibility = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'programEligibility' in result

    def test_to_dict_funding_source(self):
        resource = Immunization()
        resource.fundingSource = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'fundingSource' in result

    def test_to_dict_reaction(self):
        resource = Immunization()
        resource.reaction = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reaction' in result

    def test_to_dict_protocol_applied(self):
        resource = Immunization()
        resource.protocolApplied = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'protocolApplied' in result


class TestFromDictImmunization:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Immunization', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert isinstance(result, Immunization)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Immunization'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert isinstance(result, Immunization)

    def test_from_dict_id(self):
        data = {'resourceType': 'Immunization', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Immunization', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Immunization', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Immunization', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Immunization', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Immunization', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Immunization', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Immunization', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Immunization', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Immunization', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.status is not None

    def test_from_dict_status_reason(self):
        data = {'resourceType': 'Immunization',
         'statusReason': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.statusReason is not None

    def test_from_dict_vaccine_code(self):
        data = {'resourceType': 'Immunization',
         'vaccineCode': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.vaccineCode is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'Immunization', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.patient is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'Immunization', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.encounter is not None

    def test_from_dict_recorded(self):
        data = {'resourceType': 'Immunization', 'recorded': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.recorded is not None

    def test_from_dict_primary_source(self):
        data = {'resourceType': 'Immunization', 'primarySource': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.primarySource is not None

    def test_from_dict_report_origin(self):
        data = {'reportOrigin': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'},
         'resourceType': 'Immunization'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.reportOrigin is not None

    def test_from_dict_location(self):
        data = {'resourceType': 'Immunization', 'location': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.location is not None

    def test_from_dict_manufacturer(self):
        data = {'resourceType': 'Immunization', 'manufacturer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.manufacturer is not None

    def test_from_dict_lot_number(self):
        data = {'resourceType': 'Immunization', 'lotNumber': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.lotNumber is not None

    def test_from_dict_expiration_date(self):
        data = {'resourceType': 'Immunization', 'expirationDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.expirationDate is not None

    def test_from_dict_site(self):
        data = {'resourceType': 'Immunization',
         'site': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.site is not None

    def test_from_dict_route(self):
        data = {'resourceType': 'Immunization',
         'route': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                   'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.route is not None

    def test_from_dict_dose_quantity(self):
        data = {'resourceType': 'Immunization', 'doseQuantity': {'value': 100, 'unit': 'mg'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.doseQuantity is not None

    def test_from_dict_performer(self):
        data = {'resourceType': 'Immunization', 'performer': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.performer is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'Immunization', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.note is not None

    def test_from_dict_reason_code(self):
        data = {'reasonCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}],
         'resourceType': 'Immunization'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.reasonCode is not None

    def test_from_dict_reason_reference(self):
        data = {'resourceType': 'Immunization', 'reasonReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.reasonReference is not None

    def test_from_dict_is_subpotent(self):
        data = {'resourceType': 'Immunization', 'isSubpotent': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.isSubpotent is not None

    def test_from_dict_subpotent_reason(self):
        data = {'resourceType': 'Immunization',
         'subpotentReason': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                              'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.subpotentReason is not None

    def test_from_dict_education(self):
        data = {'resourceType': 'Immunization', 'education': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.education is not None

    def test_from_dict_program_eligibility(self):
        data = {'programEligibility': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                 'text': 'Test concept'}],
         'resourceType': 'Immunization'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.programEligibility is not None

    def test_from_dict_funding_source(self):
        data = {'fundingSource': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'},
         'resourceType': 'Immunization'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.fundingSource is not None

    def test_from_dict_reaction(self):
        data = {'resourceType': 'Immunization', 'reaction': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.reaction is not None

    def test_from_dict_protocol_applied(self):
        data = {'resourceType': 'Immunization', 'protocolApplied': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Immunization)
        assert result.protocolApplied is not None


class TestGetPathImmunization:

    def test_get_path_id(self):
        resource = Immunization()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Immunization()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Immunization()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Immunization.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Immunization()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Immunization()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Immunization()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Immunization()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Immunization()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Immunization()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Immunization()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Immunization()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = Immunization()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_status_reason(self):
        resource = Immunization()
        resource.statusReason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'statusReason')
        assert result is not None

    def test_get_path_vaccine_code(self):
        resource = Immunization()
        resource.vaccineCode = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'vaccineCode')
        assert result is not None

    def test_get_path_patient(self):
        resource = Immunization()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_encounter(self):
        resource = Immunization()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_recorded(self):
        resource = Immunization()
        resource.recorded = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recorded')
        assert result is not None

    def test_get_path_primary_source(self):
        resource = Immunization()
        resource.primarySource = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'primarySource')
        assert result is not None

    def test_get_path_report_origin(self):
        resource = Immunization()
        resource.reportOrigin = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reportOrigin')
        assert result is not None

    def test_get_path_location(self):
        resource = Immunization()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'location')
        assert result is not None

    def test_get_path_manufacturer(self):
        resource = Immunization()
        resource.manufacturer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'manufacturer')
        assert result is not None

    def test_get_path_lot_number(self):
        resource = Immunization()
        resource.lotNumber = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lotNumber')
        assert result is not None

    def test_get_path_expiration_date(self):
        resource = Immunization()
        resource.expirationDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'expirationDate')
        assert result is not None

    def test_get_path_site(self):
        resource = Immunization()
        resource.site = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'site')
        assert result is not None

    def test_get_path_route(self):
        resource = Immunization()
        resource.route = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'route')
        assert result is not None

    def test_get_path_dose_quantity(self):
        resource = Immunization()
        resource.doseQuantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'doseQuantity')
        assert result is not None

    def test_get_path_performer(self):
        resource = Immunization()
        resource.performer = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performer')
        assert result is not None

    def test_get_path_note(self):
        resource = Immunization()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_reason_code(self):
        resource = Immunization()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonCode')
        assert result is not None

    def test_get_path_reason_reference(self):
        resource = Immunization()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonReference')
        assert result is not None

    def test_get_path_is_subpotent(self):
        resource = Immunization()
        resource.isSubpotent = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'isSubpotent')
        assert result is not None

    def test_get_path_subpotent_reason(self):
        resource = Immunization()
        resource.subpotentReason = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subpotentReason')
        assert result is not None

    def test_get_path_education(self):
        resource = Immunization()
        resource.education = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'education')
        assert result is not None

    def test_get_path_program_eligibility(self):
        resource = Immunization()
        resource.programEligibility = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'programEligibility')
        assert result is not None

    def test_get_path_funding_source(self):
        resource = Immunization()
        resource.fundingSource = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'fundingSource')
        assert result is not None

    def test_get_path_reaction(self):
        resource = Immunization()
        resource.reaction = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reaction')
        assert result is not None

    def test_get_path_protocol_applied(self):
        resource = Immunization()
        resource.protocolApplied = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'protocolApplied')
        assert result is not None


class TestSetPathImmunization:

    def test_set_path_id(self):
        resource = Immunization()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Immunization()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Immunization.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Immunization()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Immunization()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Immunization()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Immunization()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Immunization()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Immunization()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Immunization()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Immunization()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = Immunization()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_status_reason(self):
        resource = Immunization()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'statusReason', value)
        assert result is True
        assert resource.statusReason is not None

    def test_set_path_vaccine_code(self):
        resource = Immunization()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'vaccineCode', value)
        assert result is True
        assert resource.vaccineCode is not None

    def test_set_path_patient(self):
        resource = Immunization()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_encounter(self):
        resource = Immunization()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_recorded(self):
        resource = Immunization()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recorded', value)
        assert result is True
        assert resource.recorded is not None

    def test_set_path_primary_source(self):
        resource = Immunization()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'primarySource', value)
        assert result is True
        assert resource.primarySource is not None

    def test_set_path_report_origin(self):
        resource = Immunization()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reportOrigin', value)
        assert result is True
        assert resource.reportOrigin is not None

    def test_set_path_location(self):
        resource = Immunization()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'location', value)
        assert result is True
        assert resource.location is not None

    def test_set_path_manufacturer(self):
        resource = Immunization()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'manufacturer', value)
        assert result is True
        assert resource.manufacturer is not None

    def test_set_path_lot_number(self):
        resource = Immunization()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lotNumber', value)
        assert result is True
        assert resource.lotNumber is not None

    def test_set_path_expiration_date(self):
        resource = Immunization()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'expirationDate', value)
        assert result is True
        assert resource.expirationDate is not None

    def test_set_path_site(self):
        resource = Immunization()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'site', value)
        assert result is True
        assert resource.site is not None

    def test_set_path_route(self):
        resource = Immunization()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'route', value)
        assert result is True
        assert resource.route is not None

    def test_set_path_dose_quantity(self):
        resource = Immunization()
        value = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'doseQuantity', value)
        assert result is True
        assert resource.doseQuantity is not None

    def test_set_path_performer(self):
        resource = Immunization()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performer', value)
        assert result is True
        assert resource.performer is not None

    def test_set_path_note(self):
        resource = Immunization()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_reason_code(self):
        resource = Immunization()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonCode', value)
        assert result is True
        assert resource.reasonCode is not None

    def test_set_path_reason_reference(self):
        resource = Immunization()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonReference', value)
        assert result is True
        assert resource.reasonReference is not None

    def test_set_path_is_subpotent(self):
        resource = Immunization()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'isSubpotent', value)
        assert result is True
        assert resource.isSubpotent is not None

    def test_set_path_subpotent_reason(self):
        resource = Immunization()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subpotentReason', value)
        assert result is True
        assert resource.subpotentReason is not None

    def test_set_path_education(self):
        resource = Immunization()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'education', value)
        assert result is True
        assert resource.education is not None

    def test_set_path_program_eligibility(self):
        resource = Immunization()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'programEligibility', value)
        assert result is True
        assert resource.programEligibility is not None

    def test_set_path_funding_source(self):
        resource = Immunization()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'fundingSource', value)
        assert result is True
        assert resource.fundingSource is not None

    def test_set_path_reaction(self):
        resource = Immunization()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reaction', value)
        assert result is True
        assert resource.reaction is not None

    def test_set_path_protocol_applied(self):
        resource = Immunization()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'protocolApplied', value)
        assert result is True
        assert resource.protocolApplied is not None


class TestParsePathImmunization:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Immunization.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Immunization.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Immunization.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
