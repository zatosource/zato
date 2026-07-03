# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Specimen


class TestToDictSpecimen:

    def test_to_dict_empty(self):
        resource = Specimen()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Specimen'

    def test_to_dict_with_id(self):
        resource = Specimen()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Specimen()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Specimen)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Specimen()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Specimen()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Specimen()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Specimen()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Specimen()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Specimen()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Specimen()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Specimen()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Specimen()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_accession_identifier(self):
        resource = Specimen()
        resource.accessionIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'accessionIdentifier' in result

    def test_to_dict_status(self):
        resource = Specimen()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_type(self):
        resource = Specimen()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_subject(self):
        resource = Specimen()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_received_time(self):
        resource = Specimen()
        resource.receivedTime = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'receivedTime' in result

    def test_to_dict_parent(self):
        resource = Specimen()
        resource.parent = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'parent' in result

    def test_to_dict_request(self):
        resource = Specimen()
        resource.request = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'request' in result

    def test_to_dict_collection(self):
        resource = Specimen()
        resource.collection = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'collection' in result

    def test_to_dict_processing(self):
        resource = Specimen()
        resource.processing = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'processing' in result

    def test_to_dict_container(self):
        resource = Specimen()
        resource.container = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'container' in result

    def test_to_dict_condition(self):
        resource = Specimen()
        resource.condition = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'condition' in result

    def test_to_dict_note(self):
        resource = Specimen()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result


class TestFromDictSpecimen:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Specimen', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert isinstance(result, Specimen)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Specimen'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert isinstance(result, Specimen)

    def test_from_dict_id(self):
        data = {'resourceType': 'Specimen', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Specimen', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Specimen', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Specimen', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Specimen', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Specimen', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Specimen', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Specimen', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Specimen', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.identifier is not None

    def test_from_dict_accession_identifier(self):
        data = {'resourceType': 'Specimen', 'accessionIdentifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.accessionIdentifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Specimen', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.status is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'Specimen',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.type_ is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'Specimen', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.subject is not None

    def test_from_dict_received_time(self):
        data = {'resourceType': 'Specimen', 'receivedTime': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.receivedTime is not None

    def test_from_dict_parent(self):
        data = {'resourceType': 'Specimen', 'parent': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.parent is not None

    def test_from_dict_request(self):
        data = {'resourceType': 'Specimen', 'request': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.request is not None

    def test_from_dict_collection(self):
        data = {'resourceType': 'Specimen', 'collection': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.collection is not None

    def test_from_dict_processing(self):
        data = {'resourceType': 'Specimen', 'processing': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.processing is not None

    def test_from_dict_container(self):
        data = {'resourceType': 'Specimen', 'container': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.container is not None

    def test_from_dict_condition(self):
        data = {'condition': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                        'text': 'Test concept'}],
         'resourceType': 'Specimen'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.condition is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'Specimen', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Specimen)
        assert result.note is not None


class TestGetPathSpecimen:

    def test_get_path_id(self):
        resource = Specimen()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Specimen()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Specimen()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Specimen.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Specimen()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Specimen()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Specimen()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Specimen()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Specimen()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Specimen()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Specimen()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Specimen()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_accession_identifier(self):
        resource = Specimen()
        resource.accessionIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'accessionIdentifier')
        assert result is not None

    def test_get_path_status(self):
        resource = Specimen()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_type(self):
        resource = Specimen()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_subject(self):
        resource = Specimen()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_received_time(self):
        resource = Specimen()
        resource.receivedTime = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'receivedTime')
        assert result is not None

    def test_get_path_parent(self):
        resource = Specimen()
        resource.parent = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'parent')
        assert result is not None

    def test_get_path_request(self):
        resource = Specimen()
        resource.request = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'request')
        assert result is not None

    def test_get_path_collection(self):
        resource = Specimen()
        resource.collection = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'collection')
        assert result is not None

    def test_get_path_processing(self):
        resource = Specimen()
        resource.processing = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'processing')
        assert result is not None

    def test_get_path_container(self):
        resource = Specimen()
        resource.container = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'container')
        assert result is not None

    def test_get_path_condition(self):
        resource = Specimen()
        resource.condition = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'condition')
        assert result is not None

    def test_get_path_note(self):
        resource = Specimen()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None


class TestSetPathSpecimen:

    def test_set_path_id(self):
        resource = Specimen()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Specimen()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Specimen.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Specimen()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Specimen()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Specimen()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Specimen()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Specimen()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Specimen()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Specimen()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Specimen()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_accession_identifier(self):
        resource = Specimen()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'accessionIdentifier', value)
        assert result is True
        assert resource.accessionIdentifier is not None

    def test_set_path_status(self):
        resource = Specimen()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_type(self):
        resource = Specimen()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_subject(self):
        resource = Specimen()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_received_time(self):
        resource = Specimen()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'receivedTime', value)
        assert result is True
        assert resource.receivedTime is not None

    def test_set_path_parent(self):
        resource = Specimen()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'parent', value)
        assert result is True
        assert resource.parent is not None

    def test_set_path_request(self):
        resource = Specimen()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'request', value)
        assert result is True
        assert resource.request is not None

    def test_set_path_collection(self):
        resource = Specimen()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'collection', value)
        assert result is True
        assert resource.collection is not None

    def test_set_path_processing(self):
        resource = Specimen()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'processing', value)
        assert result is True
        assert resource.processing is not None

    def test_set_path_container(self):
        resource = Specimen()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'container', value)
        assert result is True
        assert resource.container is not None

    def test_set_path_condition(self):
        resource = Specimen()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'condition', value)
        assert result is True
        assert resource.condition is not None

    def test_set_path_note(self):
        resource = Specimen()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None


class TestParsePathSpecimen:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Specimen.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Specimen.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Specimen.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
