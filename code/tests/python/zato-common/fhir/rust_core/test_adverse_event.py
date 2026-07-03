# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import AdverseEvent


class TestToDictAdverseEvent:

    def test_to_dict_empty(self):
        resource = AdverseEvent()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'AdverseEvent'

    def test_to_dict_with_id(self):
        resource = AdverseEvent()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = AdverseEvent()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, AdverseEvent)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = AdverseEvent()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = AdverseEvent()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = AdverseEvent()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = AdverseEvent()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = AdverseEvent()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = AdverseEvent()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = AdverseEvent()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = AdverseEvent()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = AdverseEvent()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_actuality(self):
        resource = AdverseEvent()
        resource.actuality = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'actuality' in result

    def test_to_dict_category(self):
        resource = AdverseEvent()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_event(self):
        resource = AdverseEvent()
        resource.event = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'event' in result

    def test_to_dict_subject(self):
        resource = AdverseEvent()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_encounter(self):
        resource = AdverseEvent()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_date(self):
        resource = AdverseEvent()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_detected(self):
        resource = AdverseEvent()
        resource.detected = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'detected' in result

    def test_to_dict_recorded_date(self):
        resource = AdverseEvent()
        resource.recordedDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recordedDate' in result

    def test_to_dict_resulting_condition(self):
        resource = AdverseEvent()
        resource.resultingCondition = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'resultingCondition' in result

    def test_to_dict_location(self):
        resource = AdverseEvent()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'location' in result

    def test_to_dict_seriousness(self):
        resource = AdverseEvent()
        resource.seriousness = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'seriousness' in result

    def test_to_dict_severity(self):
        resource = AdverseEvent()
        resource.severity = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'severity' in result

    def test_to_dict_outcome(self):
        resource = AdverseEvent()
        resource.outcome = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'outcome' in result

    def test_to_dict_recorder(self):
        resource = AdverseEvent()
        resource.recorder = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recorder' in result

    def test_to_dict_contributor(self):
        resource = AdverseEvent()
        resource.contributor = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contributor' in result

    def test_to_dict_suspect_entity(self):
        resource = AdverseEvent()
        resource.suspectEntity = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'suspectEntity' in result

    def test_to_dict_subject_medical_history(self):
        resource = AdverseEvent()
        resource.subjectMedicalHistory = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subjectMedicalHistory' in result

    def test_to_dict_reference_document(self):
        resource = AdverseEvent()
        resource.referenceDocument = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'referenceDocument' in result

    def test_to_dict_study(self):
        resource = AdverseEvent()
        resource.study = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'study' in result


class TestFromDictAdverseEvent:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'AdverseEvent', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert isinstance(result, AdverseEvent)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'AdverseEvent'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert isinstance(result, AdverseEvent)

    def test_from_dict_id(self):
        data = {'resourceType': 'AdverseEvent', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'AdverseEvent', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'AdverseEvent', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'AdverseEvent', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'AdverseEvent', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'AdverseEvent', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'AdverseEvent', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'AdverseEvent', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'AdverseEvent', 'identifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.identifier is not None

    def test_from_dict_actuality(self):
        data = {'resourceType': 'AdverseEvent', 'actuality': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.actuality is not None

    def test_from_dict_category(self):
        data = {'category': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'AdverseEvent'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.category is not None

    def test_from_dict_event(self):
        data = {'event': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                   'text': 'Test concept'},
         'resourceType': 'AdverseEvent'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.event is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'AdverseEvent', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.subject is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'AdverseEvent', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.encounter is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'AdverseEvent', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.date is not None

    def test_from_dict_detected(self):
        data = {'resourceType': 'AdverseEvent', 'detected': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.detected is not None

    def test_from_dict_recorded_date(self):
        data = {'resourceType': 'AdverseEvent', 'recordedDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.recordedDate is not None

    def test_from_dict_resulting_condition(self):
        data = {'resourceType': 'AdverseEvent', 'resultingCondition': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.resultingCondition is not None

    def test_from_dict_location(self):
        data = {'resourceType': 'AdverseEvent', 'location': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.location is not None

    def test_from_dict_seriousness(self):
        data = {'resourceType': 'AdverseEvent',
         'seriousness': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.seriousness is not None

    def test_from_dict_severity(self):
        data = {'resourceType': 'AdverseEvent',
         'severity': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.severity is not None

    def test_from_dict_outcome(self):
        data = {'outcome': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                     'text': 'Test concept'},
         'resourceType': 'AdverseEvent'}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.outcome is not None

    def test_from_dict_recorder(self):
        data = {'resourceType': 'AdverseEvent', 'recorder': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.recorder is not None

    def test_from_dict_contributor(self):
        data = {'resourceType': 'AdverseEvent', 'contributor': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.contributor is not None

    def test_from_dict_suspect_entity(self):
        data = {'resourceType': 'AdverseEvent', 'suspectEntity': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.suspectEntity is not None

    def test_from_dict_subject_medical_history(self):
        data = {'resourceType': 'AdverseEvent', 'subjectMedicalHistory': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.subjectMedicalHistory is not None

    def test_from_dict_reference_document(self):
        data = {'resourceType': 'AdverseEvent', 'referenceDocument': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.referenceDocument is not None

    def test_from_dict_study(self):
        data = {'resourceType': 'AdverseEvent', 'study': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, AdverseEvent)
        assert result.study is not None


class TestGetPathAdverseEvent:

    def test_get_path_id(self):
        resource = AdverseEvent()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = AdverseEvent()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = AdverseEvent()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'AdverseEvent.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = AdverseEvent()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = AdverseEvent()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = AdverseEvent()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = AdverseEvent()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = AdverseEvent()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = AdverseEvent()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = AdverseEvent()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = AdverseEvent()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_actuality(self):
        resource = AdverseEvent()
        resource.actuality = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'actuality')
        assert result is not None

    def test_get_path_category(self):
        resource = AdverseEvent()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_event(self):
        resource = AdverseEvent()
        resource.event = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'event')
        assert result is not None

    def test_get_path_subject(self):
        resource = AdverseEvent()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_encounter(self):
        resource = AdverseEvent()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_date(self):
        resource = AdverseEvent()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_detected(self):
        resource = AdverseEvent()
        resource.detected = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'detected')
        assert result is not None

    def test_get_path_recorded_date(self):
        resource = AdverseEvent()
        resource.recordedDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recordedDate')
        assert result is not None

    def test_get_path_resulting_condition(self):
        resource = AdverseEvent()
        resource.resultingCondition = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'resultingCondition')
        assert result is not None

    def test_get_path_location(self):
        resource = AdverseEvent()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'location')
        assert result is not None

    def test_get_path_seriousness(self):
        resource = AdverseEvent()
        resource.seriousness = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'seriousness')
        assert result is not None

    def test_get_path_severity(self):
        resource = AdverseEvent()
        resource.severity = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'severity')
        assert result is not None

    def test_get_path_outcome(self):
        resource = AdverseEvent()
        resource.outcome = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'outcome')
        assert result is not None

    def test_get_path_recorder(self):
        resource = AdverseEvent()
        resource.recorder = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recorder')
        assert result is not None

    def test_get_path_contributor(self):
        resource = AdverseEvent()
        resource.contributor = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contributor')
        assert result is not None

    def test_get_path_suspect_entity(self):
        resource = AdverseEvent()
        resource.suspectEntity = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'suspectEntity')
        assert result is not None

    def test_get_path_subject_medical_history(self):
        resource = AdverseEvent()
        resource.subjectMedicalHistory = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subjectMedicalHistory')
        assert result is not None

    def test_get_path_reference_document(self):
        resource = AdverseEvent()
        resource.referenceDocument = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'referenceDocument')
        assert result is not None

    def test_get_path_study(self):
        resource = AdverseEvent()
        resource.study = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'study')
        assert result is not None


class TestSetPathAdverseEvent:

    def test_set_path_id(self):
        resource = AdverseEvent()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = AdverseEvent()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'AdverseEvent.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = AdverseEvent()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = AdverseEvent()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = AdverseEvent()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = AdverseEvent()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = AdverseEvent()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = AdverseEvent()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = AdverseEvent()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = AdverseEvent()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_actuality(self):
        resource = AdverseEvent()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'actuality', value)
        assert result is True
        assert resource.actuality is not None

    def test_set_path_category(self):
        resource = AdverseEvent()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_event(self):
        resource = AdverseEvent()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'event', value)
        assert result is True
        assert resource.event is not None

    def test_set_path_subject(self):
        resource = AdverseEvent()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_encounter(self):
        resource = AdverseEvent()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_date(self):
        resource = AdverseEvent()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_detected(self):
        resource = AdverseEvent()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'detected', value)
        assert result is True
        assert resource.detected is not None

    def test_set_path_recorded_date(self):
        resource = AdverseEvent()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recordedDate', value)
        assert result is True
        assert resource.recordedDate is not None

    def test_set_path_resulting_condition(self):
        resource = AdverseEvent()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'resultingCondition', value)
        assert result is True
        assert resource.resultingCondition is not None

    def test_set_path_location(self):
        resource = AdverseEvent()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'location', value)
        assert result is True
        assert resource.location is not None

    def test_set_path_seriousness(self):
        resource = AdverseEvent()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'seriousness', value)
        assert result is True
        assert resource.seriousness is not None

    def test_set_path_severity(self):
        resource = AdverseEvent()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'severity', value)
        assert result is True
        assert resource.severity is not None

    def test_set_path_outcome(self):
        resource = AdverseEvent()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'outcome', value)
        assert result is True
        assert resource.outcome is not None

    def test_set_path_recorder(self):
        resource = AdverseEvent()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recorder', value)
        assert result is True
        assert resource.recorder is not None

    def test_set_path_contributor(self):
        resource = AdverseEvent()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contributor', value)
        assert result is True
        assert resource.contributor is not None

    def test_set_path_suspect_entity(self):
        resource = AdverseEvent()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'suspectEntity', value)
        assert result is True
        assert resource.suspectEntity is not None

    def test_set_path_subject_medical_history(self):
        resource = AdverseEvent()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subjectMedicalHistory', value)
        assert result is True
        assert resource.subjectMedicalHistory is not None

    def test_set_path_reference_document(self):
        resource = AdverseEvent()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'referenceDocument', value)
        assert result is True
        assert resource.referenceDocument is not None

    def test_set_path_study(self):
        resource = AdverseEvent()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'study', value)
        assert result is True
        assert resource.study is not None


class TestParsePathAdverseEvent:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('AdverseEvent.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('AdverseEvent.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('AdverseEvent.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
