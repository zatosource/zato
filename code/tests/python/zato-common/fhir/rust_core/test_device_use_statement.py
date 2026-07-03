# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import DeviceUseStatement


class TestToDictDeviceUseStatement:

    def test_to_dict_empty(self):
        resource = DeviceUseStatement()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'DeviceUseStatement'

    def test_to_dict_with_id(self):
        resource = DeviceUseStatement()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = DeviceUseStatement()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, DeviceUseStatement)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = DeviceUseStatement()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = DeviceUseStatement()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = DeviceUseStatement()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = DeviceUseStatement()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = DeviceUseStatement()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = DeviceUseStatement()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = DeviceUseStatement()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = DeviceUseStatement()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = DeviceUseStatement()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_based_on(self):
        resource = DeviceUseStatement()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_status(self):
        resource = DeviceUseStatement()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_subject(self):
        resource = DeviceUseStatement()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_derived_from(self):
        resource = DeviceUseStatement()
        resource.derivedFrom = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'derivedFrom' in result

    def test_to_dict_recorded_on(self):
        resource = DeviceUseStatement()
        resource.recordedOn = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'recordedOn' in result

    def test_to_dict_source(self):
        resource = DeviceUseStatement()
        resource.source = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'source' in result

    def test_to_dict_device(self):
        resource = DeviceUseStatement()
        resource.device = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'device' in result

    def test_to_dict_reason_code(self):
        resource = DeviceUseStatement()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonCode' in result

    def test_to_dict_reason_reference(self):
        resource = DeviceUseStatement()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonReference' in result

    def test_to_dict_body_site(self):
        resource = DeviceUseStatement()
        resource.bodySite = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'bodySite' in result

    def test_to_dict_note(self):
        resource = DeviceUseStatement()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result


class TestFromDictDeviceUseStatement:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'DeviceUseStatement', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert isinstance(result, DeviceUseStatement)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'DeviceUseStatement'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert isinstance(result, DeviceUseStatement)

    def test_from_dict_id(self):
        data = {'resourceType': 'DeviceUseStatement', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'DeviceUseStatement', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'DeviceUseStatement', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'DeviceUseStatement', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'DeviceUseStatement', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'DeviceUseStatement', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'DeviceUseStatement', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'DeviceUseStatement', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'DeviceUseStatement', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.identifier is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'DeviceUseStatement', 'basedOn': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.basedOn is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'DeviceUseStatement', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.status is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'DeviceUseStatement', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.subject is not None

    def test_from_dict_derived_from(self):
        data = {'resourceType': 'DeviceUseStatement', 'derivedFrom': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.derivedFrom is not None

    def test_from_dict_recorded_on(self):
        data = {'resourceType': 'DeviceUseStatement', 'recordedOn': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.recordedOn is not None

    def test_from_dict_source(self):
        data = {'resourceType': 'DeviceUseStatement', 'source': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.source is not None

    def test_from_dict_device(self):
        data = {'resourceType': 'DeviceUseStatement', 'device': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.device is not None

    def test_from_dict_reason_code(self):
        data = {'reasonCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}],
         'resourceType': 'DeviceUseStatement'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.reasonCode is not None

    def test_from_dict_reason_reference(self):
        data = {'resourceType': 'DeviceUseStatement', 'reasonReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.reasonReference is not None

    def test_from_dict_body_site(self):
        data = {'bodySite': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'DeviceUseStatement'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.bodySite is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'DeviceUseStatement', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceUseStatement)
        assert result.note is not None


class TestGetPathDeviceUseStatement:

    def test_get_path_id(self):
        resource = DeviceUseStatement()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = DeviceUseStatement()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = DeviceUseStatement()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'DeviceUseStatement.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = DeviceUseStatement()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = DeviceUseStatement()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = DeviceUseStatement()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = DeviceUseStatement()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = DeviceUseStatement()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = DeviceUseStatement()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = DeviceUseStatement()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = DeviceUseStatement()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_based_on(self):
        resource = DeviceUseStatement()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_status(self):
        resource = DeviceUseStatement()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_subject(self):
        resource = DeviceUseStatement()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_derived_from(self):
        resource = DeviceUseStatement()
        resource.derivedFrom = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'derivedFrom')
        assert result is not None

    def test_get_path_recorded_on(self):
        resource = DeviceUseStatement()
        resource.recordedOn = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'recordedOn')
        assert result is not None

    def test_get_path_source(self):
        resource = DeviceUseStatement()
        resource.source = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'source')
        assert result is not None

    def test_get_path_device(self):
        resource = DeviceUseStatement()
        resource.device = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'device')
        assert result is not None

    def test_get_path_reason_code(self):
        resource = DeviceUseStatement()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonCode')
        assert result is not None

    def test_get_path_reason_reference(self):
        resource = DeviceUseStatement()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonReference')
        assert result is not None

    def test_get_path_body_site(self):
        resource = DeviceUseStatement()
        resource.bodySite = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'bodySite')
        assert result is not None

    def test_get_path_note(self):
        resource = DeviceUseStatement()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None


class TestSetPathDeviceUseStatement:

    def test_set_path_id(self):
        resource = DeviceUseStatement()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = DeviceUseStatement()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'DeviceUseStatement.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = DeviceUseStatement()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = DeviceUseStatement()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = DeviceUseStatement()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = DeviceUseStatement()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = DeviceUseStatement()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = DeviceUseStatement()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = DeviceUseStatement()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = DeviceUseStatement()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_based_on(self):
        resource = DeviceUseStatement()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_status(self):
        resource = DeviceUseStatement()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_subject(self):
        resource = DeviceUseStatement()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_derived_from(self):
        resource = DeviceUseStatement()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'derivedFrom', value)
        assert result is True
        assert resource.derivedFrom is not None

    def test_set_path_recorded_on(self):
        resource = DeviceUseStatement()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'recordedOn', value)
        assert result is True
        assert resource.recordedOn is not None

    def test_set_path_source(self):
        resource = DeviceUseStatement()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'source', value)
        assert result is True
        assert resource.source is not None

    def test_set_path_device(self):
        resource = DeviceUseStatement()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'device', value)
        assert result is True
        assert resource.device is not None

    def test_set_path_reason_code(self):
        resource = DeviceUseStatement()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonCode', value)
        assert result is True
        assert resource.reasonCode is not None

    def test_set_path_reason_reference(self):
        resource = DeviceUseStatement()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonReference', value)
        assert result is True
        assert resource.reasonReference is not None

    def test_set_path_body_site(self):
        resource = DeviceUseStatement()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'bodySite', value)
        assert result is True
        assert resource.bodySite is not None

    def test_set_path_note(self):
        resource = DeviceUseStatement()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None


class TestParsePathDeviceUseStatement:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('DeviceUseStatement.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('DeviceUseStatement.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('DeviceUseStatement.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
