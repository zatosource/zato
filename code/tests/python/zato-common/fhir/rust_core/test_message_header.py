# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import MessageHeader


class TestToDictMessageHeader:

    def test_to_dict_empty(self):
        resource = MessageHeader()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'MessageHeader'

    def test_to_dict_with_id(self):
        resource = MessageHeader()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = MessageHeader()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, MessageHeader)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = MessageHeader()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = MessageHeader()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = MessageHeader()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = MessageHeader()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = MessageHeader()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = MessageHeader()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = MessageHeader()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = MessageHeader()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_destination(self):
        resource = MessageHeader()
        resource.destination = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'destination' in result

    def test_to_dict_sender(self):
        resource = MessageHeader()
        resource.sender = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'sender' in result

    def test_to_dict_enterer(self):
        resource = MessageHeader()
        resource.enterer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'enterer' in result

    def test_to_dict_author(self):
        resource = MessageHeader()
        resource.author = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_source(self):
        resource = MessageHeader()
        resource.source = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'source' in result

    def test_to_dict_responsible(self):
        resource = MessageHeader()
        resource.responsible = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'responsible' in result

    def test_to_dict_reason(self):
        resource = MessageHeader()
        resource.reason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reason' in result

    def test_to_dict_response(self):
        resource = MessageHeader()
        resource.response = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'response' in result

    def test_to_dict_focus(self):
        resource = MessageHeader()
        resource.focus = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'focus' in result

    def test_to_dict_definition(self):
        resource = MessageHeader()
        resource.definition = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'definition' in result


class TestFromDictMessageHeader:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'MessageHeader', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert isinstance(result, MessageHeader)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'MessageHeader'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert isinstance(result, MessageHeader)

    def test_from_dict_id(self):
        data = {'resourceType': 'MessageHeader', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'MessageHeader', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'MessageHeader', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'MessageHeader', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'MessageHeader', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'MessageHeader', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'MessageHeader', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'MessageHeader', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.modifierExtension is not None

    def test_from_dict_destination(self):
        data = {'resourceType': 'MessageHeader', 'destination': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.destination is not None

    def test_from_dict_sender(self):
        data = {'resourceType': 'MessageHeader', 'sender': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.sender is not None

    def test_from_dict_enterer(self):
        data = {'resourceType': 'MessageHeader', 'enterer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.enterer is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'MessageHeader', 'author': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.author is not None

    def test_from_dict_source(self):
        data = {'resourceType': 'MessageHeader', 'source': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.source is not None

    def test_from_dict_responsible(self):
        data = {'resourceType': 'MessageHeader', 'responsible': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.responsible is not None

    def test_from_dict_reason(self):
        data = {'reason': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'},
         'resourceType': 'MessageHeader'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.reason is not None

    def test_from_dict_response(self):
        data = {'resourceType': 'MessageHeader', 'response': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.response is not None

    def test_from_dict_focus(self):
        data = {'resourceType': 'MessageHeader', 'focus': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.focus is not None

    def test_from_dict_definition(self):
        data = {'resourceType': 'MessageHeader', 'definition': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MessageHeader)
        assert result.definition is not None


class TestGetPathMessageHeader:

    def test_get_path_id(self):
        resource = MessageHeader()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = MessageHeader()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = MessageHeader()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'MessageHeader.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = MessageHeader()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = MessageHeader()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = MessageHeader()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = MessageHeader()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = MessageHeader()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = MessageHeader()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = MessageHeader()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_destination(self):
        resource = MessageHeader()
        resource.destination = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'destination')
        assert result is not None

    def test_get_path_sender(self):
        resource = MessageHeader()
        resource.sender = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'sender')
        assert result is not None

    def test_get_path_enterer(self):
        resource = MessageHeader()
        resource.enterer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'enterer')
        assert result is not None

    def test_get_path_author(self):
        resource = MessageHeader()
        resource.author = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_source(self):
        resource = MessageHeader()
        resource.source = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'source')
        assert result is not None

    def test_get_path_responsible(self):
        resource = MessageHeader()
        resource.responsible = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'responsible')
        assert result is not None

    def test_get_path_reason(self):
        resource = MessageHeader()
        resource.reason = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reason')
        assert result is not None

    def test_get_path_response(self):
        resource = MessageHeader()
        resource.response = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'response')
        assert result is not None

    def test_get_path_focus(self):
        resource = MessageHeader()
        resource.focus = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'focus')
        assert result is not None

    def test_get_path_definition(self):
        resource = MessageHeader()
        resource.definition = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'definition')
        assert result is not None


class TestSetPathMessageHeader:

    def test_set_path_id(self):
        resource = MessageHeader()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = MessageHeader()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'MessageHeader.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = MessageHeader()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = MessageHeader()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = MessageHeader()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = MessageHeader()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = MessageHeader()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = MessageHeader()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = MessageHeader()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_destination(self):
        resource = MessageHeader()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'destination', value)
        assert result is True
        assert resource.destination is not None

    def test_set_path_sender(self):
        resource = MessageHeader()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'sender', value)
        assert result is True
        assert resource.sender is not None

    def test_set_path_enterer(self):
        resource = MessageHeader()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'enterer', value)
        assert result is True
        assert resource.enterer is not None

    def test_set_path_author(self):
        resource = MessageHeader()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_source(self):
        resource = MessageHeader()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'source', value)
        assert result is True
        assert resource.source is not None

    def test_set_path_responsible(self):
        resource = MessageHeader()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'responsible', value)
        assert result is True
        assert resource.responsible is not None

    def test_set_path_reason(self):
        resource = MessageHeader()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reason', value)
        assert result is True
        assert resource.reason is not None

    def test_set_path_response(self):
        resource = MessageHeader()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'response', value)
        assert result is True
        assert resource.response is not None

    def test_set_path_focus(self):
        resource = MessageHeader()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'focus', value)
        assert result is True
        assert resource.focus is not None

    def test_set_path_definition(self):
        resource = MessageHeader()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'definition', value)
        assert result is True
        assert resource.definition is not None


class TestParsePathMessageHeader:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('MessageHeader.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('MessageHeader.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('MessageHeader.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
