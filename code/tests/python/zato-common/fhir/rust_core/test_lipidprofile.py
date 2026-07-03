# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import lipidprofile


class TestToDictlipidprofile:

    def test_to_dict_empty(self):
        resource = lipidprofile()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'lipidprofile'

    def test_to_dict_with_id(self):
        resource = lipidprofile()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = lipidprofile()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, lipidprofile)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = lipidprofile()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = lipidprofile()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = lipidprofile()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = lipidprofile()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = lipidprofile()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = lipidprofile()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = lipidprofile()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = lipidprofile()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = lipidprofile()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_based_on(self):
        resource = lipidprofile()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_status(self):
        resource = lipidprofile()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_category(self):
        resource = lipidprofile()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_code(self):
        resource = lipidprofile()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_subject(self):
        resource = lipidprofile()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_encounter(self):
        resource = lipidprofile()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_issued(self):
        resource = lipidprofile()
        resource.issued = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'issued' in result

    def test_to_dict_performer(self):
        resource = lipidprofile()
        resource.performer = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performer' in result

    def test_to_dict_results_interpreter(self):
        resource = lipidprofile()
        resource.resultsInterpreter = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'resultsInterpreter' in result

    def test_to_dict_specimen(self):
        resource = lipidprofile()
        resource.specimen = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'specimen' in result

    def test_to_dict_result(self):
        resource = lipidprofile()
        resource.result = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'result' in result

    def test_to_dict_imaging_study(self):
        resource = lipidprofile()
        resource.imagingStudy = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'imagingStudy' in result

    def test_to_dict_media(self):
        resource = lipidprofile()
        resource.media = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'media' in result

    def test_to_dict_conclusion(self):
        resource = lipidprofile()
        resource.conclusion = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'conclusion' in result

    def test_to_dict_conclusion_code(self):
        resource = lipidprofile()
        resource.conclusionCode = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'conclusionCode' in result

    def test_to_dict_presented_form(self):
        resource = lipidprofile()
        resource.presentedForm = [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'presentedForm' in result


class TestFromDictlipidprofile:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'lipidprofile', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert isinstance(result, lipidprofile)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'lipidprofile'}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert isinstance(result, lipidprofile)

    def test_from_dict_id(self):
        data = {'resourceType': 'lipidprofile', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'lipidprofile', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'lipidprofile', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'lipidprofile', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'lipidprofile', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'lipidprofile', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'lipidprofile', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'lipidprofile', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'lipidprofile', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.identifier is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'lipidprofile', 'basedOn': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.basedOn is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'lipidprofile', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.status is not None

    def test_from_dict_category(self):
        data = {'category': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'lipidprofile'}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.category is not None

    def test_from_dict_code(self):
        data = {'code': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'lipidprofile'}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.code is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'lipidprofile', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.subject is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'lipidprofile', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.encounter is not None

    def test_from_dict_issued(self):
        data = {'resourceType': 'lipidprofile', 'issued': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.issued is not None

    def test_from_dict_performer(self):
        data = {'resourceType': 'lipidprofile', 'performer': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.performer is not None

    def test_from_dict_results_interpreter(self):
        data = {'resourceType': 'lipidprofile', 'resultsInterpreter': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.resultsInterpreter is not None

    def test_from_dict_specimen(self):
        data = {'resourceType': 'lipidprofile', 'specimen': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.specimen is not None

    def test_from_dict_result(self):
        data = {'resourceType': 'lipidprofile', 'result': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.result is not None

    def test_from_dict_imaging_study(self):
        data = {'resourceType': 'lipidprofile', 'imagingStudy': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.imagingStudy is not None

    def test_from_dict_media(self):
        data = {'resourceType': 'lipidprofile', 'media': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.media is not None

    def test_from_dict_conclusion(self):
        data = {'resourceType': 'lipidprofile', 'conclusion': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.conclusion is not None

    def test_from_dict_conclusion_code(self):
        data = {'conclusionCode': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                            'text': 'Test concept'},
         'resourceType': 'lipidprofile'}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.conclusionCode is not None

    def test_from_dict_presented_form(self):
        data = {'resourceType': 'lipidprofile', 'presentedForm': [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, lipidprofile)
        assert result.presentedForm is not None


class TestGetPathlipidprofile:

    def test_get_path_id(self):
        resource = lipidprofile()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = lipidprofile()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = lipidprofile()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lipidprofile.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = lipidprofile()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = lipidprofile()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = lipidprofile()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = lipidprofile()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = lipidprofile()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = lipidprofile()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = lipidprofile()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = lipidprofile()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_based_on(self):
        resource = lipidprofile()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_status(self):
        resource = lipidprofile()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_category(self):
        resource = lipidprofile()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_code(self):
        resource = lipidprofile()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_subject(self):
        resource = lipidprofile()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_encounter(self):
        resource = lipidprofile()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_issued(self):
        resource = lipidprofile()
        resource.issued = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'issued')
        assert result is not None

    def test_get_path_performer(self):
        resource = lipidprofile()
        resource.performer = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performer')
        assert result is not None

    def test_get_path_results_interpreter(self):
        resource = lipidprofile()
        resource.resultsInterpreter = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'resultsInterpreter')
        assert result is not None

    def test_get_path_specimen(self):
        resource = lipidprofile()
        resource.specimen = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'specimen')
        assert result is not None

    def test_get_path_result(self):
        resource = lipidprofile()
        resource.result = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'result')
        assert result is not None

    def test_get_path_imaging_study(self):
        resource = lipidprofile()
        resource.imagingStudy = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'imagingStudy')
        assert result is not None

    def test_get_path_media(self):
        resource = lipidprofile()
        resource.media = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'media')
        assert result is not None

    def test_get_path_conclusion(self):
        resource = lipidprofile()
        resource.conclusion = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'conclusion')
        assert result is not None

    def test_get_path_conclusion_code(self):
        resource = lipidprofile()
        resource.conclusionCode = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'conclusionCode')
        assert result is not None

    def test_get_path_presented_form(self):
        resource = lipidprofile()
        resource.presentedForm = [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'presentedForm')
        assert result is not None


class TestSetPathlipidprofile:

    def test_set_path_id(self):
        resource = lipidprofile()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = lipidprofile()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lipidprofile.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = lipidprofile()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = lipidprofile()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = lipidprofile()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = lipidprofile()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = lipidprofile()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = lipidprofile()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = lipidprofile()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = lipidprofile()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_based_on(self):
        resource = lipidprofile()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_status(self):
        resource = lipidprofile()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_category(self):
        resource = lipidprofile()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_code(self):
        resource = lipidprofile()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_subject(self):
        resource = lipidprofile()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_encounter(self):
        resource = lipidprofile()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_issued(self):
        resource = lipidprofile()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'issued', value)
        assert result is True
        assert resource.issued is not None

    def test_set_path_performer(self):
        resource = lipidprofile()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performer', value)
        assert result is True
        assert resource.performer is not None

    def test_set_path_results_interpreter(self):
        resource = lipidprofile()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'resultsInterpreter', value)
        assert result is True
        assert resource.resultsInterpreter is not None

    def test_set_path_specimen(self):
        resource = lipidprofile()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'specimen', value)
        assert result is True
        assert resource.specimen is not None

    def test_set_path_result(self):
        resource = lipidprofile()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'result', value)
        assert result is True
        assert resource.result is not None

    def test_set_path_imaging_study(self):
        resource = lipidprofile()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'imagingStudy', value)
        assert result is True
        assert resource.imagingStudy is not None

    def test_set_path_media(self):
        resource = lipidprofile()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'media', value)
        assert result is True
        assert resource.media is not None

    def test_set_path_conclusion(self):
        resource = lipidprofile()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'conclusion', value)
        assert result is True
        assert resource.conclusion is not None

    def test_set_path_conclusion_code(self):
        resource = lipidprofile()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'conclusionCode', value)
        assert result is True
        assert resource.conclusionCode is not None

    def test_set_path_presented_form(self):
        resource = lipidprofile()
        value = [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'presentedForm', value)
        assert result is True
        assert resource.presentedForm is not None


class TestParsePathlipidprofile:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('lipidprofile.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('lipidprofile.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('lipidprofile.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
