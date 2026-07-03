# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import catalog


class TestToDictcatalog:

    def test_to_dict_empty(self):
        resource = catalog()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'catalog'

    def test_to_dict_with_id(self):
        resource = catalog()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = catalog()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, catalog)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = catalog()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = catalog()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = catalog()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = catalog()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = catalog()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = catalog()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = catalog()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = catalog()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = catalog()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = catalog()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_type(self):
        resource = catalog()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_category(self):
        resource = catalog()
        resource.category = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_subject(self):
        resource = catalog()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_encounter(self):
        resource = catalog()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_date(self):
        resource = catalog()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_author(self):
        resource = catalog()
        resource.author = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_title(self):
        resource = catalog()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_confidentiality(self):
        resource = catalog()
        resource.confidentiality = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'confidentiality' in result

    def test_to_dict_attester(self):
        resource = catalog()
        resource.attester = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'attester' in result

    def test_to_dict_custodian(self):
        resource = catalog()
        resource.custodian = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'custodian' in result

    def test_to_dict_relates_to(self):
        resource = catalog()
        resource.relatesTo = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relatesTo' in result

    def test_to_dict_event(self):
        resource = catalog()
        resource.event = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'event' in result

    def test_to_dict_section(self):
        resource = catalog()
        resource.section = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'section' in result


class TestFromDictcatalog:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'catalog', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert isinstance(result, catalog)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'catalog'}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert isinstance(result, catalog)

    def test_from_dict_id(self):
        data = {'resourceType': 'catalog', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'catalog', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'catalog', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'catalog', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'catalog', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'catalog', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'catalog', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'catalog', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'catalog', 'identifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'catalog', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.status is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'catalog',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.type_ is not None

    def test_from_dict_category(self):
        data = {'category': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'catalog'}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.category is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'catalog', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.subject is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'catalog', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.encounter is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'catalog', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.date is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'catalog', 'author': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.author is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'catalog', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.title is not None

    def test_from_dict_confidentiality(self):
        data = {'resourceType': 'catalog', 'confidentiality': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.confidentiality is not None

    def test_from_dict_attester(self):
        data = {'resourceType': 'catalog', 'attester': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.attester is not None

    def test_from_dict_custodian(self):
        data = {'resourceType': 'catalog', 'custodian': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.custodian is not None

    def test_from_dict_relates_to(self):
        data = {'resourceType': 'catalog', 'relatesTo': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.relatesTo is not None

    def test_from_dict_event(self):
        data = {'resourceType': 'catalog', 'event': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.event is not None

    def test_from_dict_section(self):
        data = {'resourceType': 'catalog', 'section': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, catalog)
        assert result.section is not None


class TestGetPathcatalog:

    def test_get_path_id(self):
        resource = catalog()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = catalog()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = catalog()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'catalog.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = catalog()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = catalog()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = catalog()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = catalog()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = catalog()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = catalog()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = catalog()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = catalog()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = catalog()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_type(self):
        resource = catalog()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_category(self):
        resource = catalog()
        resource.category = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_subject(self):
        resource = catalog()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_encounter(self):
        resource = catalog()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_date(self):
        resource = catalog()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_author(self):
        resource = catalog()
        resource.author = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_title(self):
        resource = catalog()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_confidentiality(self):
        resource = catalog()
        resource.confidentiality = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'confidentiality')
        assert result is not None

    def test_get_path_attester(self):
        resource = catalog()
        resource.attester = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'attester')
        assert result is not None

    def test_get_path_custodian(self):
        resource = catalog()
        resource.custodian = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'custodian')
        assert result is not None

    def test_get_path_relates_to(self):
        resource = catalog()
        resource.relatesTo = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relatesTo')
        assert result is not None

    def test_get_path_event(self):
        resource = catalog()
        resource.event = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'event')
        assert result is not None

    def test_get_path_section(self):
        resource = catalog()
        resource.section = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'section')
        assert result is not None


class TestSetPathcatalog:

    def test_set_path_id(self):
        resource = catalog()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = catalog()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'catalog.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = catalog()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = catalog()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = catalog()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = catalog()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = catalog()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = catalog()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = catalog()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = catalog()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = catalog()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_type(self):
        resource = catalog()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_category(self):
        resource = catalog()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_subject(self):
        resource = catalog()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_encounter(self):
        resource = catalog()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_date(self):
        resource = catalog()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_author(self):
        resource = catalog()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_title(self):
        resource = catalog()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_confidentiality(self):
        resource = catalog()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'confidentiality', value)
        assert result is True
        assert resource.confidentiality is not None

    def test_set_path_attester(self):
        resource = catalog()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'attester', value)
        assert result is True
        assert resource.attester is not None

    def test_set_path_custodian(self):
        resource = catalog()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'custodian', value)
        assert result is True
        assert resource.custodian is not None

    def test_set_path_relates_to(self):
        resource = catalog()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relatesTo', value)
        assert result is True
        assert resource.relatesTo is not None

    def test_set_path_event(self):
        resource = catalog()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'event', value)
        assert result is True
        assert resource.event is not None

    def test_set_path_section(self):
        resource = catalog()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'section', value)
        assert result is True
        assert resource.section is not None


class TestParsePathcatalog:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('catalog.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('catalog.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('catalog.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
