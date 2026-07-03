# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import QuestionnaireResponse


class TestToDictQuestionnaireResponse:

    def test_to_dict_empty(self):
        resource = QuestionnaireResponse()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'QuestionnaireResponse'

    def test_to_dict_with_id(self):
        resource = QuestionnaireResponse()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = QuestionnaireResponse()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, QuestionnaireResponse)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = QuestionnaireResponse()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = QuestionnaireResponse()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = QuestionnaireResponse()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = QuestionnaireResponse()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = QuestionnaireResponse()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = QuestionnaireResponse()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = QuestionnaireResponse()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = QuestionnaireResponse()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = QuestionnaireResponse()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_based_on(self):
        resource = QuestionnaireResponse()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_part_of(self):
        resource = QuestionnaireResponse()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'partOf' in result

    def test_to_dict_questionnaire(self):
        resource = QuestionnaireResponse()
        resource.questionnaire = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'questionnaire' in result

    def test_to_dict_status(self):
        resource = QuestionnaireResponse()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_subject(self):
        resource = QuestionnaireResponse()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_encounter(self):
        resource = QuestionnaireResponse()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_authored(self):
        resource = QuestionnaireResponse()
        resource.authored = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'authored' in result

    def test_to_dict_author(self):
        resource = QuestionnaireResponse()
        resource.author = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_source(self):
        resource = QuestionnaireResponse()
        resource.source = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'source' in result

    def test_to_dict_item(self):
        resource = QuestionnaireResponse()
        resource.item = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'item' in result


class TestFromDictQuestionnaireResponse:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'QuestionnaireResponse', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert isinstance(result, QuestionnaireResponse)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'QuestionnaireResponse'}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert isinstance(result, QuestionnaireResponse)

    def test_from_dict_id(self):
        data = {'resourceType': 'QuestionnaireResponse', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'QuestionnaireResponse', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'QuestionnaireResponse', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'QuestionnaireResponse', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'QuestionnaireResponse', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'QuestionnaireResponse', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'QuestionnaireResponse', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'QuestionnaireResponse', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'QuestionnaireResponse', 'identifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.identifier is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'QuestionnaireResponse', 'basedOn': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.basedOn is not None

    def test_from_dict_part_of(self):
        data = {'resourceType': 'QuestionnaireResponse', 'partOf': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.partOf is not None

    def test_from_dict_questionnaire(self):
        data = {'resourceType': 'QuestionnaireResponse', 'questionnaire': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.questionnaire is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'QuestionnaireResponse', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.status is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'QuestionnaireResponse', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.subject is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'QuestionnaireResponse', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.encounter is not None

    def test_from_dict_authored(self):
        data = {'resourceType': 'QuestionnaireResponse', 'authored': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.authored is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'QuestionnaireResponse', 'author': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.author is not None

    def test_from_dict_source(self):
        data = {'resourceType': 'QuestionnaireResponse', 'source': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.source is not None

    def test_from_dict_item(self):
        data = {'resourceType': 'QuestionnaireResponse', 'item': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, QuestionnaireResponse)
        assert result.item is not None


class TestGetPathQuestionnaireResponse:

    def test_get_path_id(self):
        resource = QuestionnaireResponse()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = QuestionnaireResponse()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = QuestionnaireResponse()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'QuestionnaireResponse.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = QuestionnaireResponse()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = QuestionnaireResponse()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = QuestionnaireResponse()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = QuestionnaireResponse()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = QuestionnaireResponse()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = QuestionnaireResponse()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = QuestionnaireResponse()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = QuestionnaireResponse()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_based_on(self):
        resource = QuestionnaireResponse()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_part_of(self):
        resource = QuestionnaireResponse()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'partOf')
        assert result is not None

    def test_get_path_questionnaire(self):
        resource = QuestionnaireResponse()
        resource.questionnaire = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'questionnaire')
        assert result is not None

    def test_get_path_status(self):
        resource = QuestionnaireResponse()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_subject(self):
        resource = QuestionnaireResponse()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_encounter(self):
        resource = QuestionnaireResponse()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_authored(self):
        resource = QuestionnaireResponse()
        resource.authored = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'authored')
        assert result is not None

    def test_get_path_author(self):
        resource = QuestionnaireResponse()
        resource.author = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_source(self):
        resource = QuestionnaireResponse()
        resource.source = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'source')
        assert result is not None

    def test_get_path_item(self):
        resource = QuestionnaireResponse()
        resource.item = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'item')
        assert result is not None


class TestSetPathQuestionnaireResponse:

    def test_set_path_id(self):
        resource = QuestionnaireResponse()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = QuestionnaireResponse()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'QuestionnaireResponse.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = QuestionnaireResponse()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = QuestionnaireResponse()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = QuestionnaireResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = QuestionnaireResponse()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = QuestionnaireResponse()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = QuestionnaireResponse()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = QuestionnaireResponse()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = QuestionnaireResponse()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_based_on(self):
        resource = QuestionnaireResponse()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_part_of(self):
        resource = QuestionnaireResponse()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'partOf', value)
        assert result is True
        assert resource.partOf is not None

    def test_set_path_questionnaire(self):
        resource = QuestionnaireResponse()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'questionnaire', value)
        assert result is True
        assert resource.questionnaire is not None

    def test_set_path_status(self):
        resource = QuestionnaireResponse()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_subject(self):
        resource = QuestionnaireResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_encounter(self):
        resource = QuestionnaireResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_authored(self):
        resource = QuestionnaireResponse()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'authored', value)
        assert result is True
        assert resource.authored is not None

    def test_set_path_author(self):
        resource = QuestionnaireResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_source(self):
        resource = QuestionnaireResponse()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'source', value)
        assert result is True
        assert resource.source is not None

    def test_set_path_item(self):
        resource = QuestionnaireResponse()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'item', value)
        assert result is True
        assert resource.item is not None


class TestParsePathQuestionnaireResponse:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('QuestionnaireResponse.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('QuestionnaireResponse.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('QuestionnaireResponse.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
