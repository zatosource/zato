# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import DocumentReference


class TestToDictDocumentReference:

    def test_to_dict_empty(self):
        resource = DocumentReference()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'DocumentReference'

    def test_to_dict_with_id(self):
        resource = DocumentReference()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = DocumentReference()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, DocumentReference)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = DocumentReference()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = DocumentReference()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = DocumentReference()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = DocumentReference()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = DocumentReference()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = DocumentReference()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = DocumentReference()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = DocumentReference()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_master_identifier(self):
        resource = DocumentReference()
        resource.masterIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'masterIdentifier' in result

    def test_to_dict_identifier(self):
        resource = DocumentReference()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = DocumentReference()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_doc_status(self):
        resource = DocumentReference()
        resource.docStatus = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'docStatus' in result

    def test_to_dict_type(self):
        resource = DocumentReference()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_category(self):
        resource = DocumentReference()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_subject(self):
        resource = DocumentReference()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_date(self):
        resource = DocumentReference()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_author(self):
        resource = DocumentReference()
        resource.author = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_authenticator(self):
        resource = DocumentReference()
        resource.authenticator = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'authenticator' in result

    def test_to_dict_custodian(self):
        resource = DocumentReference()
        resource.custodian = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'custodian' in result

    def test_to_dict_relates_to(self):
        resource = DocumentReference()
        resource.relatesTo = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relatesTo' in result

    def test_to_dict_description(self):
        resource = DocumentReference()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_security_label(self):
        resource = DocumentReference()
        resource.securityLabel = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'securityLabel' in result

    def test_to_dict_content(self):
        resource = DocumentReference()
        resource.content = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'content' in result

    def test_to_dict_context(self):
        resource = DocumentReference()
        resource.context = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'context' in result


class TestFromDictDocumentReference:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'DocumentReference', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert isinstance(result, DocumentReference)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'DocumentReference'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert isinstance(result, DocumentReference)

    def test_from_dict_id(self):
        data = {'resourceType': 'DocumentReference', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'DocumentReference', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'DocumentReference', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'DocumentReference', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'DocumentReference', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'DocumentReference', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'DocumentReference', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'DocumentReference', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.modifierExtension is not None

    def test_from_dict_master_identifier(self):
        data = {'resourceType': 'DocumentReference', 'masterIdentifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.masterIdentifier is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'DocumentReference', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'DocumentReference', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.status is not None

    def test_from_dict_doc_status(self):
        data = {'resourceType': 'DocumentReference', 'docStatus': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.docStatus is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'DocumentReference',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.type_ is not None

    def test_from_dict_category(self):
        data = {'category': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'DocumentReference'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.category is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'DocumentReference', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.subject is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'DocumentReference', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.date is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'DocumentReference', 'author': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.author is not None

    def test_from_dict_authenticator(self):
        data = {'resourceType': 'DocumentReference', 'authenticator': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.authenticator is not None

    def test_from_dict_custodian(self):
        data = {'resourceType': 'DocumentReference', 'custodian': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.custodian is not None

    def test_from_dict_relates_to(self):
        data = {'resourceType': 'DocumentReference', 'relatesTo': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.relatesTo is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'DocumentReference', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.description is not None

    def test_from_dict_security_label(self):
        data = {'resourceType': 'DocumentReference',
         'securityLabel': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                            'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.securityLabel is not None

    def test_from_dict_content(self):
        data = {'resourceType': 'DocumentReference', 'content': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.content is not None

    def test_from_dict_context(self):
        data = {'resourceType': 'DocumentReference', 'context': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DocumentReference)
        assert result.context is not None


class TestGetPathDocumentReference:

    def test_get_path_id(self):
        resource = DocumentReference()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = DocumentReference()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = DocumentReference()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'DocumentReference.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = DocumentReference()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = DocumentReference()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = DocumentReference()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = DocumentReference()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = DocumentReference()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = DocumentReference()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = DocumentReference()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_master_identifier(self):
        resource = DocumentReference()
        resource.masterIdentifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'masterIdentifier')
        assert result is not None

    def test_get_path_identifier(self):
        resource = DocumentReference()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = DocumentReference()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_doc_status(self):
        resource = DocumentReference()
        resource.docStatus = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'docStatus')
        assert result is not None

    def test_get_path_type(self):
        resource = DocumentReference()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_category(self):
        resource = DocumentReference()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_subject(self):
        resource = DocumentReference()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_date(self):
        resource = DocumentReference()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_author(self):
        resource = DocumentReference()
        resource.author = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_authenticator(self):
        resource = DocumentReference()
        resource.authenticator = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'authenticator')
        assert result is not None

    def test_get_path_custodian(self):
        resource = DocumentReference()
        resource.custodian = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'custodian')
        assert result is not None

    def test_get_path_relates_to(self):
        resource = DocumentReference()
        resource.relatesTo = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relatesTo')
        assert result is not None

    def test_get_path_description(self):
        resource = DocumentReference()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_security_label(self):
        resource = DocumentReference()
        resource.securityLabel = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'securityLabel')
        assert result is not None

    def test_get_path_content(self):
        resource = DocumentReference()
        resource.content = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'content')
        assert result is not None

    def test_get_path_context(self):
        resource = DocumentReference()
        resource.context = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'context')
        assert result is not None


class TestSetPathDocumentReference:

    def test_set_path_id(self):
        resource = DocumentReference()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = DocumentReference()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'DocumentReference.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = DocumentReference()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = DocumentReference()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = DocumentReference()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = DocumentReference()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = DocumentReference()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = DocumentReference()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = DocumentReference()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_master_identifier(self):
        resource = DocumentReference()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'masterIdentifier', value)
        assert result is True
        assert resource.masterIdentifier is not None

    def test_set_path_identifier(self):
        resource = DocumentReference()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = DocumentReference()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_doc_status(self):
        resource = DocumentReference()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'docStatus', value)
        assert result is True
        assert resource.docStatus is not None

    def test_set_path_type(self):
        resource = DocumentReference()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_category(self):
        resource = DocumentReference()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_subject(self):
        resource = DocumentReference()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_date(self):
        resource = DocumentReference()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_author(self):
        resource = DocumentReference()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_authenticator(self):
        resource = DocumentReference()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'authenticator', value)
        assert result is True
        assert resource.authenticator is not None

    def test_set_path_custodian(self):
        resource = DocumentReference()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'custodian', value)
        assert result is True
        assert resource.custodian is not None

    def test_set_path_relates_to(self):
        resource = DocumentReference()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relatesTo', value)
        assert result is True
        assert resource.relatesTo is not None

    def test_set_path_description(self):
        resource = DocumentReference()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_security_label(self):
        resource = DocumentReference()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'securityLabel', value)
        assert result is True
        assert resource.securityLabel is not None

    def test_set_path_content(self):
        resource = DocumentReference()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'content', value)
        assert result is True
        assert resource.content is not None

    def test_set_path_context(self):
        resource = DocumentReference()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'context', value)
        assert result is True
        assert resource.context is not None


class TestParsePathDocumentReference:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('DocumentReference.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('DocumentReference.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('DocumentReference.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
