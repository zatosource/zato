# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import MedicinalProductAuthorization


class TestToDictMedicinalProductAuthorization:

    def test_to_dict_empty(self):
        resource = MedicinalProductAuthorization()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'MedicinalProductAuthorization'

    def test_to_dict_with_id(self):
        resource = MedicinalProductAuthorization()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = MedicinalProductAuthorization()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, MedicinalProductAuthorization)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = MedicinalProductAuthorization()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = MedicinalProductAuthorization()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = MedicinalProductAuthorization()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = MedicinalProductAuthorization()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = MedicinalProductAuthorization()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = MedicinalProductAuthorization()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = MedicinalProductAuthorization()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = MedicinalProductAuthorization()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = MedicinalProductAuthorization()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_subject(self):
        resource = MedicinalProductAuthorization()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_country(self):
        resource = MedicinalProductAuthorization()
        resource.country = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'country' in result

    def test_to_dict_jurisdiction(self):
        resource = MedicinalProductAuthorization()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_status(self):
        resource = MedicinalProductAuthorization()
        resource.status = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_status_date(self):
        resource = MedicinalProductAuthorization()
        resource.statusDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'statusDate' in result

    def test_to_dict_restore_date(self):
        resource = MedicinalProductAuthorization()
        resource.restoreDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'restoreDate' in result

    def test_to_dict_validity_period(self):
        resource = MedicinalProductAuthorization()
        resource.validityPeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'validityPeriod' in result

    def test_to_dict_data_exclusivity_period(self):
        resource = MedicinalProductAuthorization()
        resource.dataExclusivityPeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dataExclusivityPeriod' in result

    def test_to_dict_date_of_first_authorization(self):
        resource = MedicinalProductAuthorization()
        resource.dateOfFirstAuthorization = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dateOfFirstAuthorization' in result

    def test_to_dict_international_birth_date(self):
        resource = MedicinalProductAuthorization()
        resource.internationalBirthDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'internationalBirthDate' in result

    def test_to_dict_legal_basis(self):
        resource = MedicinalProductAuthorization()
        resource.legalBasis = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'legalBasis' in result

    def test_to_dict_jurisdictional_authorization(self):
        resource = MedicinalProductAuthorization()
        resource.jurisdictionalAuthorization = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdictionalAuthorization' in result

    def test_to_dict_holder(self):
        resource = MedicinalProductAuthorization()
        resource.holder = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'holder' in result

    def test_to_dict_regulator(self):
        resource = MedicinalProductAuthorization()
        resource.regulator = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'regulator' in result

    def test_to_dict_procedure(self):
        resource = MedicinalProductAuthorization()
        resource.procedure = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'procedure' in result


class TestFromDictMedicinalProductAuthorization:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert isinstance(result, MedicinalProductAuthorization)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'MedicinalProductAuthorization'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert isinstance(result, MedicinalProductAuthorization)

    def test_from_dict_id(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.identifier is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.subject is not None

    def test_from_dict_country(self):
        data = {'country': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'}],
         'resourceType': 'MedicinalProductAuthorization'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.country is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'MedicinalProductAuthorization'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.jurisdiction is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'MedicinalProductAuthorization',
         'status': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.status is not None

    def test_from_dict_status_date(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'statusDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.statusDate is not None

    def test_from_dict_restore_date(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'restoreDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.restoreDate is not None

    def test_from_dict_validity_period(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'validityPeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.validityPeriod is not None

    def test_from_dict_data_exclusivity_period(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'dataExclusivityPeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.dataExclusivityPeriod is not None

    def test_from_dict_date_of_first_authorization(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'dateOfFirstAuthorization': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.dateOfFirstAuthorization is not None

    def test_from_dict_international_birth_date(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'internationalBirthDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.internationalBirthDate is not None

    def test_from_dict_legal_basis(self):
        data = {'legalBasis': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                        'text': 'Test concept'},
         'resourceType': 'MedicinalProductAuthorization'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.legalBasis is not None

    def test_from_dict_jurisdictional_authorization(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'jurisdictionalAuthorization': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.jurisdictionalAuthorization is not None

    def test_from_dict_holder(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'holder': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.holder is not None

    def test_from_dict_regulator(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'regulator': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.regulator is not None

    def test_from_dict_procedure(self):
        data = {'resourceType': 'MedicinalProductAuthorization', 'procedure': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductAuthorization)
        assert result.procedure is not None


class TestGetPathMedicinalProductAuthorization:

    def test_get_path_id(self):
        resource = MedicinalProductAuthorization()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = MedicinalProductAuthorization()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = MedicinalProductAuthorization()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'MedicinalProductAuthorization.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = MedicinalProductAuthorization()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = MedicinalProductAuthorization()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = MedicinalProductAuthorization()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = MedicinalProductAuthorization()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = MedicinalProductAuthorization()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = MedicinalProductAuthorization()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = MedicinalProductAuthorization()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = MedicinalProductAuthorization()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_subject(self):
        resource = MedicinalProductAuthorization()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_country(self):
        resource = MedicinalProductAuthorization()
        resource.country = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'country')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = MedicinalProductAuthorization()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_status(self):
        resource = MedicinalProductAuthorization()
        resource.status = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_status_date(self):
        resource = MedicinalProductAuthorization()
        resource.statusDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'statusDate')
        assert result is not None

    def test_get_path_restore_date(self):
        resource = MedicinalProductAuthorization()
        resource.restoreDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'restoreDate')
        assert result is not None

    def test_get_path_validity_period(self):
        resource = MedicinalProductAuthorization()
        resource.validityPeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'validityPeriod')
        assert result is not None

    def test_get_path_data_exclusivity_period(self):
        resource = MedicinalProductAuthorization()
        resource.dataExclusivityPeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dataExclusivityPeriod')
        assert result is not None

    def test_get_path_date_of_first_authorization(self):
        resource = MedicinalProductAuthorization()
        resource.dateOfFirstAuthorization = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dateOfFirstAuthorization')
        assert result is not None

    def test_get_path_international_birth_date(self):
        resource = MedicinalProductAuthorization()
        resource.internationalBirthDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'internationalBirthDate')
        assert result is not None

    def test_get_path_legal_basis(self):
        resource = MedicinalProductAuthorization()
        resource.legalBasis = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'legalBasis')
        assert result is not None

    def test_get_path_jurisdictional_authorization(self):
        resource = MedicinalProductAuthorization()
        resource.jurisdictionalAuthorization = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdictionalAuthorization')
        assert result is not None

    def test_get_path_holder(self):
        resource = MedicinalProductAuthorization()
        resource.holder = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'holder')
        assert result is not None

    def test_get_path_regulator(self):
        resource = MedicinalProductAuthorization()
        resource.regulator = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'regulator')
        assert result is not None

    def test_get_path_procedure(self):
        resource = MedicinalProductAuthorization()
        resource.procedure = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'procedure')
        assert result is not None


class TestSetPathMedicinalProductAuthorization:

    def test_set_path_id(self):
        resource = MedicinalProductAuthorization()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = MedicinalProductAuthorization()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'MedicinalProductAuthorization.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = MedicinalProductAuthorization()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = MedicinalProductAuthorization()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = MedicinalProductAuthorization()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = MedicinalProductAuthorization()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = MedicinalProductAuthorization()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = MedicinalProductAuthorization()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = MedicinalProductAuthorization()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = MedicinalProductAuthorization()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_subject(self):
        resource = MedicinalProductAuthorization()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_country(self):
        resource = MedicinalProductAuthorization()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'country', value)
        assert result is True
        assert resource.country is not None

    def test_set_path_jurisdiction(self):
        resource = MedicinalProductAuthorization()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_status(self):
        resource = MedicinalProductAuthorization()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_status_date(self):
        resource = MedicinalProductAuthorization()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'statusDate', value)
        assert result is True
        assert resource.statusDate is not None

    def test_set_path_restore_date(self):
        resource = MedicinalProductAuthorization()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'restoreDate', value)
        assert result is True
        assert resource.restoreDate is not None

    def test_set_path_validity_period(self):
        resource = MedicinalProductAuthorization()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'validityPeriod', value)
        assert result is True
        assert resource.validityPeriod is not None

    def test_set_path_data_exclusivity_period(self):
        resource = MedicinalProductAuthorization()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dataExclusivityPeriod', value)
        assert result is True
        assert resource.dataExclusivityPeriod is not None

    def test_set_path_date_of_first_authorization(self):
        resource = MedicinalProductAuthorization()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dateOfFirstAuthorization', value)
        assert result is True
        assert resource.dateOfFirstAuthorization is not None

    def test_set_path_international_birth_date(self):
        resource = MedicinalProductAuthorization()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'internationalBirthDate', value)
        assert result is True
        assert resource.internationalBirthDate is not None

    def test_set_path_legal_basis(self):
        resource = MedicinalProductAuthorization()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'legalBasis', value)
        assert result is True
        assert resource.legalBasis is not None

    def test_set_path_jurisdictional_authorization(self):
        resource = MedicinalProductAuthorization()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdictionalAuthorization', value)
        assert result is True
        assert resource.jurisdictionalAuthorization is not None

    def test_set_path_holder(self):
        resource = MedicinalProductAuthorization()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'holder', value)
        assert result is True
        assert resource.holder is not None

    def test_set_path_regulator(self):
        resource = MedicinalProductAuthorization()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'regulator', value)
        assert result is True
        assert resource.regulator is not None

    def test_set_path_procedure(self):
        resource = MedicinalProductAuthorization()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'procedure', value)
        assert result is True
        assert resource.procedure is not None


class TestParsePathMedicinalProductAuthorization:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductAuthorization.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductAuthorization.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductAuthorization.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
