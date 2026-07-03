# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Encounter


class TestToDictEncounter:

    def test_to_dict_empty(self):
        resource = Encounter()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Encounter'

    def test_to_dict_with_id(self):
        resource = Encounter()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Encounter()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Encounter)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Encounter()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Encounter()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Encounter()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Encounter()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Encounter()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Encounter()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Encounter()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Encounter()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Encounter()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = Encounter()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_status_history(self):
        resource = Encounter()
        resource.statusHistory = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'statusHistory' in result

    def test_to_dict_class(self):
        resource = Encounter()
        resource.class_ = {'system': 'http://example.org', 'code': 'test-code'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'class' in result

    def test_to_dict_class_history(self):
        resource = Encounter()
        resource.classHistory = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'classHistory' in result

    def test_to_dict_type(self):
        resource = Encounter()
        resource.type_ = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_service_type(self):
        resource = Encounter()
        resource.serviceType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'serviceType' in result

    def test_to_dict_priority(self):
        resource = Encounter()
        resource.priority = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priority' in result

    def test_to_dict_subject(self):
        resource = Encounter()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_episode_of_care(self):
        resource = Encounter()
        resource.episodeOfCare = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'episodeOfCare' in result

    def test_to_dict_based_on(self):
        resource = Encounter()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_participant(self):
        resource = Encounter()
        resource.participant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'participant' in result

    def test_to_dict_appointment(self):
        resource = Encounter()
        resource.appointment = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'appointment' in result

    def test_to_dict_period(self):
        resource = Encounter()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'period' in result

    def test_to_dict_length(self):
        resource = Encounter()
        resource.length = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'length' in result

    def test_to_dict_reason_code(self):
        resource = Encounter()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonCode' in result

    def test_to_dict_reason_reference(self):
        resource = Encounter()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonReference' in result

    def test_to_dict_diagnosis(self):
        resource = Encounter()
        resource.diagnosis = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'diagnosis' in result

    def test_to_dict_account(self):
        resource = Encounter()
        resource.account = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'account' in result

    def test_to_dict_hospitalization(self):
        resource = Encounter()
        resource.hospitalization = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'hospitalization' in result

    def test_to_dict_location(self):
        resource = Encounter()
        resource.location = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'location' in result

    def test_to_dict_service_provider(self):
        resource = Encounter()
        resource.serviceProvider = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'serviceProvider' in result

    def test_to_dict_part_of(self):
        resource = Encounter()
        resource.partOf = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'partOf' in result


class TestFromDictEncounter:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Encounter', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert isinstance(result, Encounter)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Encounter'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert isinstance(result, Encounter)

    def test_from_dict_id(self):
        data = {'resourceType': 'Encounter', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Encounter', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Encounter', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Encounter', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Encounter', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Encounter', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Encounter', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Encounter', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Encounter', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Encounter', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.status is not None

    def test_from_dict_status_history(self):
        data = {'resourceType': 'Encounter', 'statusHistory': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.statusHistory is not None

    def test_from_dict_class(self):
        data = {'resourceType': 'Encounter', 'class': {'system': 'http://example.org', 'code': 'test-code'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.class_ is not None

    def test_from_dict_class_history(self):
        data = {'resourceType': 'Encounter', 'classHistory': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.classHistory is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'Encounter',
         'type': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                   'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.type_ is not None

    def test_from_dict_service_type(self):
        data = {'resourceType': 'Encounter',
         'serviceType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.serviceType is not None

    def test_from_dict_priority(self):
        data = {'priority': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'Encounter'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.priority is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'Encounter', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.subject is not None

    def test_from_dict_episode_of_care(self):
        data = {'resourceType': 'Encounter', 'episodeOfCare': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.episodeOfCare is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'Encounter', 'basedOn': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.basedOn is not None

    def test_from_dict_participant(self):
        data = {'resourceType': 'Encounter', 'participant': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.participant is not None

    def test_from_dict_appointment(self):
        data = {'resourceType': 'Encounter', 'appointment': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.appointment is not None

    def test_from_dict_period(self):
        data = {'resourceType': 'Encounter', 'period': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.period is not None

    def test_from_dict_length(self):
        data = {'resourceType': 'Encounter', 'length': {'value': 'test'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.length is not None

    def test_from_dict_reason_code(self):
        data = {'reasonCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}],
         'resourceType': 'Encounter'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.reasonCode is not None

    def test_from_dict_reason_reference(self):
        data = {'resourceType': 'Encounter', 'reasonReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.reasonReference is not None

    def test_from_dict_diagnosis(self):
        data = {'resourceType': 'Encounter', 'diagnosis': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.diagnosis is not None

    def test_from_dict_account(self):
        data = {'resourceType': 'Encounter', 'account': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.account is not None

    def test_from_dict_hospitalization(self):
        data = {'resourceType': 'Encounter', 'hospitalization': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.hospitalization is not None

    def test_from_dict_location(self):
        data = {'resourceType': 'Encounter', 'location': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.location is not None

    def test_from_dict_service_provider(self):
        data = {'resourceType': 'Encounter', 'serviceProvider': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.serviceProvider is not None

    def test_from_dict_part_of(self):
        data = {'resourceType': 'Encounter', 'partOf': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Encounter)
        assert result.partOf is not None


class TestGetPathEncounter:

    def test_get_path_id(self):
        resource = Encounter()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Encounter()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Encounter()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Encounter.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Encounter()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Encounter()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Encounter()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Encounter()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Encounter()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Encounter()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Encounter()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Encounter()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = Encounter()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_status_history(self):
        resource = Encounter()
        resource.statusHistory = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'statusHistory')
        assert result is not None

    def test_get_path_class(self):
        resource = Encounter()
        resource.class_ = {'system': 'http://example.org', 'code': 'test-code'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'class')
        assert result is not None

    def test_get_path_class_history(self):
        resource = Encounter()
        resource.classHistory = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'classHistory')
        assert result is not None

    def test_get_path_type(self):
        resource = Encounter()
        resource.type_ = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_service_type(self):
        resource = Encounter()
        resource.serviceType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'serviceType')
        assert result is not None

    def test_get_path_priority(self):
        resource = Encounter()
        resource.priority = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priority')
        assert result is not None

    def test_get_path_subject(self):
        resource = Encounter()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_episode_of_care(self):
        resource = Encounter()
        resource.episodeOfCare = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'episodeOfCare')
        assert result is not None

    def test_get_path_based_on(self):
        resource = Encounter()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_participant(self):
        resource = Encounter()
        resource.participant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'participant')
        assert result is not None

    def test_get_path_appointment(self):
        resource = Encounter()
        resource.appointment = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'appointment')
        assert result is not None

    def test_get_path_period(self):
        resource = Encounter()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'period')
        assert result is not None

    def test_get_path_length(self):
        resource = Encounter()
        resource.length = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'length')
        assert result is not None

    def test_get_path_reason_code(self):
        resource = Encounter()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonCode')
        assert result is not None

    def test_get_path_reason_reference(self):
        resource = Encounter()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonReference')
        assert result is not None

    def test_get_path_diagnosis(self):
        resource = Encounter()
        resource.diagnosis = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'diagnosis')
        assert result is not None

    def test_get_path_account(self):
        resource = Encounter()
        resource.account = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'account')
        assert result is not None

    def test_get_path_hospitalization(self):
        resource = Encounter()
        resource.hospitalization = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'hospitalization')
        assert result is not None

    def test_get_path_location(self):
        resource = Encounter()
        resource.location = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'location')
        assert result is not None

    def test_get_path_service_provider(self):
        resource = Encounter()
        resource.serviceProvider = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'serviceProvider')
        assert result is not None

    def test_get_path_part_of(self):
        resource = Encounter()
        resource.partOf = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'partOf')
        assert result is not None


class TestSetPathEncounter:

    def test_set_path_id(self):
        resource = Encounter()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Encounter()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Encounter.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Encounter()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Encounter()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Encounter()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Encounter()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Encounter()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Encounter()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Encounter()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Encounter()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = Encounter()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_status_history(self):
        resource = Encounter()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'statusHistory', value)
        assert result is True
        assert resource.statusHistory is not None

    def test_set_path_class(self):
        resource = Encounter()
        value = {'system': 'http://example.org', 'code': 'test-code'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'class', value)
        assert result is True
        assert resource.class_ is not None

    def test_set_path_class_history(self):
        resource = Encounter()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'classHistory', value)
        assert result is True
        assert resource.classHistory is not None

    def test_set_path_type(self):
        resource = Encounter()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_service_type(self):
        resource = Encounter()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'serviceType', value)
        assert result is True
        assert resource.serviceType is not None

    def test_set_path_priority(self):
        resource = Encounter()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priority', value)
        assert result is True
        assert resource.priority is not None

    def test_set_path_subject(self):
        resource = Encounter()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_episode_of_care(self):
        resource = Encounter()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'episodeOfCare', value)
        assert result is True
        assert resource.episodeOfCare is not None

    def test_set_path_based_on(self):
        resource = Encounter()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_participant(self):
        resource = Encounter()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'participant', value)
        assert result is True
        assert resource.participant is not None

    def test_set_path_appointment(self):
        resource = Encounter()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'appointment', value)
        assert result is True
        assert resource.appointment is not None

    def test_set_path_period(self):
        resource = Encounter()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'period', value)
        assert result is True
        assert resource.period is not None

    def test_set_path_length(self):
        resource = Encounter()
        value = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'length', value)
        assert result is True
        assert resource.length is not None

    def test_set_path_reason_code(self):
        resource = Encounter()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonCode', value)
        assert result is True
        assert resource.reasonCode is not None

    def test_set_path_reason_reference(self):
        resource = Encounter()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonReference', value)
        assert result is True
        assert resource.reasonReference is not None

    def test_set_path_diagnosis(self):
        resource = Encounter()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'diagnosis', value)
        assert result is True
        assert resource.diagnosis is not None

    def test_set_path_account(self):
        resource = Encounter()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'account', value)
        assert result is True
        assert resource.account is not None

    def test_set_path_hospitalization(self):
        resource = Encounter()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'hospitalization', value)
        assert result is True
        assert resource.hospitalization is not None

    def test_set_path_location(self):
        resource = Encounter()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'location', value)
        assert result is True
        assert resource.location is not None

    def test_set_path_service_provider(self):
        resource = Encounter()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'serviceProvider', value)
        assert result is True
        assert resource.serviceProvider is not None

    def test_set_path_part_of(self):
        resource = Encounter()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'partOf', value)
        assert result is True
        assert resource.partOf is not None


class TestParsePathEncounter:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Encounter.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Encounter.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Encounter.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
