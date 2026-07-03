# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import EpisodeOfCare


class TestToDictEpisodeOfCare:

    def test_to_dict_empty(self):
        resource = EpisodeOfCare()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'EpisodeOfCare'

    def test_to_dict_with_id(self):
        resource = EpisodeOfCare()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = EpisodeOfCare()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, EpisodeOfCare)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = EpisodeOfCare()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = EpisodeOfCare()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = EpisodeOfCare()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = EpisodeOfCare()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = EpisodeOfCare()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = EpisodeOfCare()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = EpisodeOfCare()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = EpisodeOfCare()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = EpisodeOfCare()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = EpisodeOfCare()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_status_history(self):
        resource = EpisodeOfCare()
        resource.statusHistory = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'statusHistory' in result

    def test_to_dict_type(self):
        resource = EpisodeOfCare()
        resource.type_ = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_diagnosis(self):
        resource = EpisodeOfCare()
        resource.diagnosis = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'diagnosis' in result

    def test_to_dict_patient(self):
        resource = EpisodeOfCare()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_managing_organization(self):
        resource = EpisodeOfCare()
        resource.managingOrganization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'managingOrganization' in result

    def test_to_dict_period(self):
        resource = EpisodeOfCare()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'period' in result

    def test_to_dict_referral_request(self):
        resource = EpisodeOfCare()
        resource.referralRequest = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'referralRequest' in result

    def test_to_dict_care_manager(self):
        resource = EpisodeOfCare()
        resource.careManager = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'careManager' in result

    def test_to_dict_team(self):
        resource = EpisodeOfCare()
        resource.team = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'team' in result

    def test_to_dict_account(self):
        resource = EpisodeOfCare()
        resource.account = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'account' in result


class TestFromDictEpisodeOfCare:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'EpisodeOfCare', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert isinstance(result, EpisodeOfCare)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'EpisodeOfCare'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert isinstance(result, EpisodeOfCare)

    def test_from_dict_id(self):
        data = {'resourceType': 'EpisodeOfCare', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'EpisodeOfCare', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'EpisodeOfCare', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'EpisodeOfCare', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'EpisodeOfCare', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'EpisodeOfCare', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'EpisodeOfCare', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'EpisodeOfCare', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'EpisodeOfCare', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'EpisodeOfCare', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.status is not None

    def test_from_dict_status_history(self):
        data = {'resourceType': 'EpisodeOfCare', 'statusHistory': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.statusHistory is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'EpisodeOfCare',
         'type': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                   'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.type_ is not None

    def test_from_dict_diagnosis(self):
        data = {'resourceType': 'EpisodeOfCare', 'diagnosis': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.diagnosis is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'EpisodeOfCare', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.patient is not None

    def test_from_dict_managing_organization(self):
        data = {'resourceType': 'EpisodeOfCare', 'managingOrganization': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.managingOrganization is not None

    def test_from_dict_period(self):
        data = {'resourceType': 'EpisodeOfCare', 'period': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.period is not None

    def test_from_dict_referral_request(self):
        data = {'resourceType': 'EpisodeOfCare', 'referralRequest': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.referralRequest is not None

    def test_from_dict_care_manager(self):
        data = {'resourceType': 'EpisodeOfCare', 'careManager': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.careManager is not None

    def test_from_dict_team(self):
        data = {'resourceType': 'EpisodeOfCare', 'team': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.team is not None

    def test_from_dict_account(self):
        data = {'resourceType': 'EpisodeOfCare', 'account': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EpisodeOfCare)
        assert result.account is not None


class TestGetPathEpisodeOfCare:

    def test_get_path_id(self):
        resource = EpisodeOfCare()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = EpisodeOfCare()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = EpisodeOfCare()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'EpisodeOfCare.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = EpisodeOfCare()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = EpisodeOfCare()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = EpisodeOfCare()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = EpisodeOfCare()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = EpisodeOfCare()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = EpisodeOfCare()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = EpisodeOfCare()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = EpisodeOfCare()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = EpisodeOfCare()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_status_history(self):
        resource = EpisodeOfCare()
        resource.statusHistory = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'statusHistory')
        assert result is not None

    def test_get_path_type(self):
        resource = EpisodeOfCare()
        resource.type_ = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_diagnosis(self):
        resource = EpisodeOfCare()
        resource.diagnosis = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'diagnosis')
        assert result is not None

    def test_get_path_patient(self):
        resource = EpisodeOfCare()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_managing_organization(self):
        resource = EpisodeOfCare()
        resource.managingOrganization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'managingOrganization')
        assert result is not None

    def test_get_path_period(self):
        resource = EpisodeOfCare()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'period')
        assert result is not None

    def test_get_path_referral_request(self):
        resource = EpisodeOfCare()
        resource.referralRequest = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'referralRequest')
        assert result is not None

    def test_get_path_care_manager(self):
        resource = EpisodeOfCare()
        resource.careManager = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'careManager')
        assert result is not None

    def test_get_path_team(self):
        resource = EpisodeOfCare()
        resource.team = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'team')
        assert result is not None

    def test_get_path_account(self):
        resource = EpisodeOfCare()
        resource.account = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'account')
        assert result is not None


class TestSetPathEpisodeOfCare:

    def test_set_path_id(self):
        resource = EpisodeOfCare()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = EpisodeOfCare()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'EpisodeOfCare.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = EpisodeOfCare()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = EpisodeOfCare()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = EpisodeOfCare()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = EpisodeOfCare()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = EpisodeOfCare()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = EpisodeOfCare()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = EpisodeOfCare()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = EpisodeOfCare()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = EpisodeOfCare()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_status_history(self):
        resource = EpisodeOfCare()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'statusHistory', value)
        assert result is True
        assert resource.statusHistory is not None

    def test_set_path_type(self):
        resource = EpisodeOfCare()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_diagnosis(self):
        resource = EpisodeOfCare()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'diagnosis', value)
        assert result is True
        assert resource.diagnosis is not None

    def test_set_path_patient(self):
        resource = EpisodeOfCare()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_managing_organization(self):
        resource = EpisodeOfCare()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'managingOrganization', value)
        assert result is True
        assert resource.managingOrganization is not None

    def test_set_path_period(self):
        resource = EpisodeOfCare()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'period', value)
        assert result is True
        assert resource.period is not None

    def test_set_path_referral_request(self):
        resource = EpisodeOfCare()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'referralRequest', value)
        assert result is True
        assert resource.referralRequest is not None

    def test_set_path_care_manager(self):
        resource = EpisodeOfCare()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'careManager', value)
        assert result is True
        assert resource.careManager is not None

    def test_set_path_team(self):
        resource = EpisodeOfCare()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'team', value)
        assert result is True
        assert resource.team is not None

    def test_set_path_account(self):
        resource = EpisodeOfCare()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'account', value)
        assert result is True
        assert resource.account is not None


class TestParsePathEpisodeOfCare:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('EpisodeOfCare.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('EpisodeOfCare.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('EpisodeOfCare.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
