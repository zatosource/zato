# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import cdshooksguidanceresponse


class TestToDictcdshooksguidanceresponse:

    def test_to_dict_empty(self):
        resource = cdshooksguidanceresponse()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'cdshooksguidanceresponse'

    def test_to_dict_with_id(self):
        resource = cdshooksguidanceresponse()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = cdshooksguidanceresponse()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, cdshooksguidanceresponse)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = cdshooksguidanceresponse()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = cdshooksguidanceresponse()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = cdshooksguidanceresponse()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = cdshooksguidanceresponse()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = cdshooksguidanceresponse()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = cdshooksguidanceresponse()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = cdshooksguidanceresponse()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = cdshooksguidanceresponse()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_request_identifier(self):
        resource = cdshooksguidanceresponse()
        resource.requestIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'requestIdentifier' in result

    def test_to_dict_identifier(self):
        resource = cdshooksguidanceresponse()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = cdshooksguidanceresponse()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_subject(self):
        resource = cdshooksguidanceresponse()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_encounter(self):
        resource = cdshooksguidanceresponse()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_occurrence_date_time(self):
        resource = cdshooksguidanceresponse()
        resource.occurrenceDateTime = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'occurrenceDateTime' in result

    def test_to_dict_performer(self):
        resource = cdshooksguidanceresponse()
        resource.performer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performer' in result

    def test_to_dict_reason_code(self):
        resource = cdshooksguidanceresponse()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonCode' in result

    def test_to_dict_reason_reference(self):
        resource = cdshooksguidanceresponse()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonReference' in result

    def test_to_dict_note(self):
        resource = cdshooksguidanceresponse()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_evaluation_message(self):
        resource = cdshooksguidanceresponse()
        resource.evaluationMessage = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'evaluationMessage' in result

    def test_to_dict_output_parameters(self):
        resource = cdshooksguidanceresponse()
        resource.outputParameters = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'outputParameters' in result

    def test_to_dict_result(self):
        resource = cdshooksguidanceresponse()
        resource.result = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'result' in result

    def test_to_dict_data_requirement(self):
        resource = cdshooksguidanceresponse()
        resource.dataRequirement = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dataRequirement' in result


class TestFromDictcdshooksguidanceresponse:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert isinstance(result, cdshooksguidanceresponse)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'cdshooksguidanceresponse'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert isinstance(result, cdshooksguidanceresponse)

    def test_from_dict_id(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.modifierExtension is not None

    def test_from_dict_request_identifier(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'requestIdentifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.requestIdentifier is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'identifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.status is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.subject is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.encounter is not None

    def test_from_dict_occurrence_date_time(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'occurrenceDateTime': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.occurrenceDateTime is not None

    def test_from_dict_performer(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'performer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.performer is not None

    def test_from_dict_reason_code(self):
        data = {'reasonCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}],
         'resourceType': 'cdshooksguidanceresponse'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.reasonCode is not None

    def test_from_dict_reason_reference(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'reasonReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.reasonReference is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.note is not None

    def test_from_dict_evaluation_message(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'evaluationMessage': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.evaluationMessage is not None

    def test_from_dict_output_parameters(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'outputParameters': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.outputParameters is not None

    def test_from_dict_result(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'result': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.result is not None

    def test_from_dict_data_requirement(self):
        data = {'resourceType': 'cdshooksguidanceresponse', 'dataRequirement': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cdshooksguidanceresponse)
        assert result.dataRequirement is not None


class TestGetPathcdshooksguidanceresponse:

    def test_get_path_id(self):
        resource = cdshooksguidanceresponse()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = cdshooksguidanceresponse()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = cdshooksguidanceresponse()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'cdshooksguidanceresponse.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = cdshooksguidanceresponse()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = cdshooksguidanceresponse()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = cdshooksguidanceresponse()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = cdshooksguidanceresponse()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = cdshooksguidanceresponse()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = cdshooksguidanceresponse()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = cdshooksguidanceresponse()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_request_identifier(self):
        resource = cdshooksguidanceresponse()
        resource.requestIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'requestIdentifier')
        assert result is not None

    def test_get_path_identifier(self):
        resource = cdshooksguidanceresponse()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = cdshooksguidanceresponse()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_subject(self):
        resource = cdshooksguidanceresponse()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_encounter(self):
        resource = cdshooksguidanceresponse()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_occurrence_date_time(self):
        resource = cdshooksguidanceresponse()
        resource.occurrenceDateTime = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'occurrenceDateTime')
        assert result is not None

    def test_get_path_performer(self):
        resource = cdshooksguidanceresponse()
        resource.performer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performer')
        assert result is not None

    def test_get_path_reason_code(self):
        resource = cdshooksguidanceresponse()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonCode')
        assert result is not None

    def test_get_path_reason_reference(self):
        resource = cdshooksguidanceresponse()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonReference')
        assert result is not None

    def test_get_path_note(self):
        resource = cdshooksguidanceresponse()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_evaluation_message(self):
        resource = cdshooksguidanceresponse()
        resource.evaluationMessage = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'evaluationMessage')
        assert result is not None

    def test_get_path_output_parameters(self):
        resource = cdshooksguidanceresponse()
        resource.outputParameters = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'outputParameters')
        assert result is not None

    def test_get_path_result(self):
        resource = cdshooksguidanceresponse()
        resource.result = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'result')
        assert result is not None

    def test_get_path_data_requirement(self):
        resource = cdshooksguidanceresponse()
        resource.dataRequirement = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dataRequirement')
        assert result is not None


class TestSetPathcdshooksguidanceresponse:

    def test_set_path_id(self):
        resource = cdshooksguidanceresponse()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = cdshooksguidanceresponse()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'cdshooksguidanceresponse.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = cdshooksguidanceresponse()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = cdshooksguidanceresponse()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = cdshooksguidanceresponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = cdshooksguidanceresponse()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = cdshooksguidanceresponse()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = cdshooksguidanceresponse()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = cdshooksguidanceresponse()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_request_identifier(self):
        resource = cdshooksguidanceresponse()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'requestIdentifier', value)
        assert result is True
        assert resource.requestIdentifier is not None

    def test_set_path_identifier(self):
        resource = cdshooksguidanceresponse()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = cdshooksguidanceresponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_subject(self):
        resource = cdshooksguidanceresponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_encounter(self):
        resource = cdshooksguidanceresponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_occurrence_date_time(self):
        resource = cdshooksguidanceresponse()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'occurrenceDateTime', value)
        assert result is True
        assert resource.occurrenceDateTime is not None

    def test_set_path_performer(self):
        resource = cdshooksguidanceresponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performer', value)
        assert result is True
        assert resource.performer is not None

    def test_set_path_reason_code(self):
        resource = cdshooksguidanceresponse()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonCode', value)
        assert result is True
        assert resource.reasonCode is not None

    def test_set_path_reason_reference(self):
        resource = cdshooksguidanceresponse()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonReference', value)
        assert result is True
        assert resource.reasonReference is not None

    def test_set_path_note(self):
        resource = cdshooksguidanceresponse()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_evaluation_message(self):
        resource = cdshooksguidanceresponse()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'evaluationMessage', value)
        assert result is True
        assert resource.evaluationMessage is not None

    def test_set_path_output_parameters(self):
        resource = cdshooksguidanceresponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'outputParameters', value)
        assert result is True
        assert resource.outputParameters is not None

    def test_set_path_result(self):
        resource = cdshooksguidanceresponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'result', value)
        assert result is True
        assert resource.result is not None

    def test_set_path_data_requirement(self):
        resource = cdshooksguidanceresponse()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dataRequirement', value)
        assert result is True
        assert resource.dataRequirement is not None


class TestParsePathcdshooksguidanceresponse:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('cdshooksguidanceresponse.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('cdshooksguidanceresponse.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('cdshooksguidanceresponse.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
