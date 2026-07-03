# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Media


class TestToDictMedia:

    def test_to_dict_empty(self):
        resource = Media()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Media'

    def test_to_dict_with_id(self):
        resource = Media()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Media()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Media)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Media()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Media()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Media()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Media()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Media()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Media()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Media()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Media()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Media()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_based_on(self):
        resource = Media()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_part_of(self):
        resource = Media()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'partOf' in result

    def test_to_dict_status(self):
        resource = Media()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_type(self):
        resource = Media()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_modality(self):
        resource = Media()
        resource.modality = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modality' in result

    def test_to_dict_view(self):
        resource = Media()
        resource.view = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'view' in result

    def test_to_dict_subject(self):
        resource = Media()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_encounter(self):
        resource = Media()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_issued(self):
        resource = Media()
        resource.issued = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'issued' in result

    def test_to_dict_operator(self):
        resource = Media()
        resource.operator = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'operator' in result

    def test_to_dict_reason_code(self):
        resource = Media()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonCode' in result

    def test_to_dict_body_site(self):
        resource = Media()
        resource.bodySite = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'bodySite' in result

    def test_to_dict_device_name(self):
        resource = Media()
        resource.deviceName = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'deviceName' in result

    def test_to_dict_device(self):
        resource = Media()
        resource.device = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'device' in result

    def test_to_dict_height(self):
        resource = Media()
        resource.height = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'height' in result

    def test_to_dict_width(self):
        resource = Media()
        resource.width = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'width' in result

    def test_to_dict_frames(self):
        resource = Media()
        resource.frames = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'frames' in result

    def test_to_dict_duration(self):
        resource = Media()
        resource.duration = 3.14
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'duration' in result

    def test_to_dict_content(self):
        resource = Media()
        resource.content = {'contentType': 'text/plain', 'data': 'SGVsbG8='}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'content' in result

    def test_to_dict_note(self):
        resource = Media()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result


class TestFromDictMedia:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Media', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert isinstance(result, Media)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Media'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert isinstance(result, Media)

    def test_from_dict_id(self):
        data = {'resourceType': 'Media', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Media', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Media', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Media', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Media', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Media', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Media', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Media', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Media', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.identifier is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'Media', 'basedOn': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.basedOn is not None

    def test_from_dict_part_of(self):
        data = {'resourceType': 'Media', 'partOf': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.partOf is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Media', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.status is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'Media', 'type': {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.type_ is not None

    def test_from_dict_modality(self):
        data = {'modality': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'Media'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.modality is not None

    def test_from_dict_view(self):
        data = {'resourceType': 'Media', 'view': {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.view is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'Media', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.subject is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'Media', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.encounter is not None

    def test_from_dict_issued(self):
        data = {'resourceType': 'Media', 'issued': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.issued is not None

    def test_from_dict_operator(self):
        data = {'resourceType': 'Media', 'operator': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.operator is not None

    def test_from_dict_reason_code(self):
        data = {'reasonCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}],
         'resourceType': 'Media'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.reasonCode is not None

    def test_from_dict_body_site(self):
        data = {'bodySite': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'Media'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.bodySite is not None

    def test_from_dict_device_name(self):
        data = {'resourceType': 'Media', 'deviceName': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.deviceName is not None

    def test_from_dict_device(self):
        data = {'resourceType': 'Media', 'device': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.device is not None

    def test_from_dict_height(self):
        data = {'resourceType': 'Media', 'height': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.height is not None

    def test_from_dict_width(self):
        data = {'resourceType': 'Media', 'width': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.width is not None

    def test_from_dict_frames(self):
        data = {'resourceType': 'Media', 'frames': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.frames is not None

    def test_from_dict_duration(self):
        data = {'resourceType': 'Media', 'duration': 3.14}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.duration is not None

    def test_from_dict_content(self):
        data = {'resourceType': 'Media', 'content': {'contentType': 'text/plain', 'data': 'SGVsbG8='}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.content is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'Media', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Media)
        assert result.note is not None


class TestGetPathMedia:

    def test_get_path_id(self):
        resource = Media()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Media()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Media()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Media.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Media()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Media()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Media()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Media()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Media()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Media()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Media()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Media()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_based_on(self):
        resource = Media()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_part_of(self):
        resource = Media()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'partOf')
        assert result is not None

    def test_get_path_status(self):
        resource = Media()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_type(self):
        resource = Media()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_modality(self):
        resource = Media()
        resource.modality = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modality')
        assert result is not None

    def test_get_path_view(self):
        resource = Media()
        resource.view = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'view')
        assert result is not None

    def test_get_path_subject(self):
        resource = Media()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_encounter(self):
        resource = Media()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_issued(self):
        resource = Media()
        resource.issued = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'issued')
        assert result is not None

    def test_get_path_operator(self):
        resource = Media()
        resource.operator = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'operator')
        assert result is not None

    def test_get_path_reason_code(self):
        resource = Media()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonCode')
        assert result is not None

    def test_get_path_body_site(self):
        resource = Media()
        resource.bodySite = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'bodySite')
        assert result is not None

    def test_get_path_device_name(self):
        resource = Media()
        resource.deviceName = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'deviceName')
        assert result is not None

    def test_get_path_device(self):
        resource = Media()
        resource.device = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'device')
        assert result is not None

    def test_get_path_height(self):
        resource = Media()
        resource.height = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'height')
        assert result is not None

    def test_get_path_width(self):
        resource = Media()
        resource.width = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'width')
        assert result is not None

    def test_get_path_frames(self):
        resource = Media()
        resource.frames = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'frames')
        assert result is not None

    def test_get_path_duration(self):
        resource = Media()
        resource.duration = 3.14
        result = zato.fhir_r4_0_1_core.get_path(resource, 'duration')
        assert result is not None

    def test_get_path_content(self):
        resource = Media()
        resource.content = {'contentType': 'text/plain', 'data': 'SGVsbG8='}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'content')
        assert result is not None

    def test_get_path_note(self):
        resource = Media()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None


class TestSetPathMedia:

    def test_set_path_id(self):
        resource = Media()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Media()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Media.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Media()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Media()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Media()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Media()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Media()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Media()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Media()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Media()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_based_on(self):
        resource = Media()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_part_of(self):
        resource = Media()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'partOf', value)
        assert result is True
        assert resource.partOf is not None

    def test_set_path_status(self):
        resource = Media()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_type(self):
        resource = Media()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_modality(self):
        resource = Media()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modality', value)
        assert result is True
        assert resource.modality is not None

    def test_set_path_view(self):
        resource = Media()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'view', value)
        assert result is True
        assert resource.view is not None

    def test_set_path_subject(self):
        resource = Media()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_encounter(self):
        resource = Media()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_issued(self):
        resource = Media()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'issued', value)
        assert result is True
        assert resource.issued is not None

    def test_set_path_operator(self):
        resource = Media()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'operator', value)
        assert result is True
        assert resource.operator is not None

    def test_set_path_reason_code(self):
        resource = Media()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonCode', value)
        assert result is True
        assert resource.reasonCode is not None

    def test_set_path_body_site(self):
        resource = Media()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'bodySite', value)
        assert result is True
        assert resource.bodySite is not None

    def test_set_path_device_name(self):
        resource = Media()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'deviceName', value)
        assert result is True
        assert resource.deviceName is not None

    def test_set_path_device(self):
        resource = Media()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'device', value)
        assert result is True
        assert resource.device is not None

    def test_set_path_height(self):
        resource = Media()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'height', value)
        assert result is True
        assert resource.height is not None

    def test_set_path_width(self):
        resource = Media()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'width', value)
        assert result is True
        assert resource.width is not None

    def test_set_path_frames(self):
        resource = Media()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'frames', value)
        assert result is True
        assert resource.frames is not None

    def test_set_path_duration(self):
        resource = Media()
        value = 3.14
        result = zato.fhir_r4_0_1_core.set_path(resource, 'duration', value)
        assert result is True
        assert resource.duration is not None

    def test_set_path_content(self):
        resource = Media()
        value = {'contentType': 'text/plain', 'data': 'SGVsbG8='}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'content', value)
        assert result is True
        assert resource.content is not None

    def test_set_path_note(self):
        resource = Media()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None


class TestParsePathMedia:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Media.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Media.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Media.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
