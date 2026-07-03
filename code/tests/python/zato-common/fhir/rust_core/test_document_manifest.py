# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import DocumentManifest


class TestToDictDocumentManifest:

    def test_to_dict_empty(self):
        resource = DocumentManifest()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'DocumentManifest'

    def test_to_dict_with_id(self):
        resource = DocumentManifest()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = DocumentManifest()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, DocumentManifest)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = DocumentManifest()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = DocumentManifest()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = DocumentManifest()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = DocumentManifest()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = DocumentManifest()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = DocumentManifest()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = DocumentManifest()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = DocumentManifest()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_master_identifier(self):
        resource = DocumentManifest()
        resource.masterIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'masterIdentifier' in result

    def test_to_dict_identifier(self):
        resource = DocumentManifest()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = DocumentManifest()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_type(self):
        resource = DocumentManifest()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_subject(self):
        resource = DocumentManifest()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_created(self):
        resource = DocumentManifest()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'created' in result

    def test_to_dict_author(self):
        resource = DocumentManifest()
        resource.author = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_recipient(self):
        resource = DocumentManifest()
        resource.recipient = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recipient' in result

    def test_to_dict_source(self):
        resource = DocumentManifest()
        resource.source = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'source' in result

    def test_to_dict_description(self):
        resource = DocumentManifest()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_content(self):
        resource = DocumentManifest()
        resource.content = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'content' in result

    def test_to_dict_related(self):
        resource = DocumentManifest()
        resource.related = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'related' in result


class TestFromDictDocumentManifest:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'DocumentManifest', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert isinstance(result, DocumentManifest)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'DocumentManifest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert isinstance(result, DocumentManifest)

    def test_from_dict_id(self):
        data = {'resourceType': 'DocumentManifest', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'DocumentManifest', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'DocumentManifest', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'DocumentManifest', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'DocumentManifest', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'DocumentManifest', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'DocumentManifest', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'DocumentManifest', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.modifierExtension is not None

    def test_from_dict_master_identifier(self):
        data = {'resourceType': 'DocumentManifest', 'masterIdentifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.masterIdentifier is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'DocumentManifest', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'DocumentManifest', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.status is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'DocumentManifest',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.type_ is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'DocumentManifest', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.subject is not None

    def test_from_dict_created(self):
        data = {'resourceType': 'DocumentManifest', 'created': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.created is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'DocumentManifest', 'author': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.author is not None

    def test_from_dict_recipient(self):
        data = {'resourceType': 'DocumentManifest', 'recipient': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.recipient is not None

    def test_from_dict_source(self):
        data = {'resourceType': 'DocumentManifest', 'source': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.source is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'DocumentManifest', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.description is not None

    def test_from_dict_content(self):
        data = {'resourceType': 'DocumentManifest', 'content': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.content is not None

    def test_from_dict_related(self):
        data = {'resourceType': 'DocumentManifest', 'related': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentManifest)
        assert result.related is not None


class TestGetPathDocumentManifest:

    def test_get_path_id(self):
        resource = DocumentManifest()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = DocumentManifest()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = DocumentManifest()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'DocumentManifest.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = DocumentManifest()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = DocumentManifest()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = DocumentManifest()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = DocumentManifest()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = DocumentManifest()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = DocumentManifest()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = DocumentManifest()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_master_identifier(self):
        resource = DocumentManifest()
        resource.masterIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'masterIdentifier')
        assert result is not None

    def test_get_path_identifier(self):
        resource = DocumentManifest()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = DocumentManifest()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_type(self):
        resource = DocumentManifest()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_subject(self):
        resource = DocumentManifest()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_created(self):
        resource = DocumentManifest()
        resource.created = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'created')
        assert result is not None

    def test_get_path_author(self):
        resource = DocumentManifest()
        resource.author = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_recipient(self):
        resource = DocumentManifest()
        resource.recipient = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recipient')
        assert result is not None

    def test_get_path_source(self):
        resource = DocumentManifest()
        resource.source = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'source')
        assert result is not None

    def test_get_path_description(self):
        resource = DocumentManifest()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_content(self):
        resource = DocumentManifest()
        resource.content = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'content')
        assert result is not None

    def test_get_path_related(self):
        resource = DocumentManifest()
        resource.related = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'related')
        assert result is not None


class TestSetPathDocumentManifest:

    def test_set_path_id(self):
        resource = DocumentManifest()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = DocumentManifest()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'DocumentManifest.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = DocumentManifest()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = DocumentManifest()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = DocumentManifest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = DocumentManifest()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = DocumentManifest()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = DocumentManifest()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = DocumentManifest()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_master_identifier(self):
        resource = DocumentManifest()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'masterIdentifier', value)
        assert result is True
        assert resource.masterIdentifier is not None

    def test_set_path_identifier(self):
        resource = DocumentManifest()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = DocumentManifest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_type(self):
        resource = DocumentManifest()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_subject(self):
        resource = DocumentManifest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_created(self):
        resource = DocumentManifest()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'created', value)
        assert result is True
        assert resource.created is not None

    def test_set_path_author(self):
        resource = DocumentManifest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_recipient(self):
        resource = DocumentManifest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recipient', value)
        assert result is True
        assert resource.recipient is not None

    def test_set_path_source(self):
        resource = DocumentManifest()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'source', value)
        assert result is True
        assert resource.source is not None

    def test_set_path_description(self):
        resource = DocumentManifest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_content(self):
        resource = DocumentManifest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'content', value)
        assert result is True
        assert resource.content is not None

    def test_set_path_related(self):
        resource = DocumentManifest()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'related', value)
        assert result is True
        assert resource.related is not None


class TestParsePathDocumentManifest:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('DocumentManifest.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('DocumentManifest.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('DocumentManifest.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
