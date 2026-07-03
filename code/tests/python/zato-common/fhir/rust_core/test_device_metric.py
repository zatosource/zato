# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import DeviceMetric


class TestToDictDeviceMetric:

    def test_to_dict_empty(self):
        resource = DeviceMetric()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'DeviceMetric'

    def test_to_dict_with_id(self):
        resource = DeviceMetric()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = DeviceMetric()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, DeviceMetric)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = DeviceMetric()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = DeviceMetric()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = DeviceMetric()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = DeviceMetric()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = DeviceMetric()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = DeviceMetric()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = DeviceMetric()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = DeviceMetric()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = DeviceMetric()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_type(self):
        resource = DeviceMetric()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_unit(self):
        resource = DeviceMetric()
        resource.unit = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'unit' in result

    def test_to_dict_source(self):
        resource = DeviceMetric()
        resource.source = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'source' in result

    def test_to_dict_parent(self):
        resource = DeviceMetric()
        resource.parent = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'parent' in result

    def test_to_dict_operational_status(self):
        resource = DeviceMetric()
        resource.operationalStatus = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'operationalStatus' in result

    def test_to_dict_color(self):
        resource = DeviceMetric()
        resource.color = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'color' in result

    def test_to_dict_category(self):
        resource = DeviceMetric()
        resource.category = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_measurement_period(self):
        resource = DeviceMetric()
        resource.measurementPeriod = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'measurementPeriod' in result

    def test_to_dict_calibration(self):
        resource = DeviceMetric()
        resource.calibration = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'calibration' in result


class TestFromDictDeviceMetric:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'DeviceMetric', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert isinstance(result, DeviceMetric)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'DeviceMetric'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert isinstance(result, DeviceMetric)

    def test_from_dict_id(self):
        data = {'resourceType': 'DeviceMetric', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'DeviceMetric', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'DeviceMetric', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'DeviceMetric', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'DeviceMetric', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'DeviceMetric', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'DeviceMetric', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'DeviceMetric', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'DeviceMetric', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.identifier is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'DeviceMetric',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.type_ is not None

    def test_from_dict_unit(self):
        data = {'resourceType': 'DeviceMetric',
         'unit': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.unit is not None

    def test_from_dict_source(self):
        data = {'resourceType': 'DeviceMetric', 'source': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.source is not None

    def test_from_dict_parent(self):
        data = {'resourceType': 'DeviceMetric', 'parent': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.parent is not None

    def test_from_dict_operational_status(self):
        data = {'resourceType': 'DeviceMetric', 'operationalStatus': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.operationalStatus is not None

    def test_from_dict_color(self):
        data = {'resourceType': 'DeviceMetric', 'color': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.color is not None

    def test_from_dict_category(self):
        data = {'resourceType': 'DeviceMetric', 'category': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.category is not None

    def test_from_dict_measurement_period(self):
        data = {'resourceType': 'DeviceMetric', 'measurementPeriod': {'value': 'test'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.measurementPeriod is not None

    def test_from_dict_calibration(self):
        data = {'resourceType': 'DeviceMetric', 'calibration': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceMetric)
        assert result.calibration is not None


class TestGetPathDeviceMetric:

    def test_get_path_id(self):
        resource = DeviceMetric()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = DeviceMetric()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = DeviceMetric()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'DeviceMetric.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = DeviceMetric()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = DeviceMetric()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = DeviceMetric()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = DeviceMetric()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = DeviceMetric()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = DeviceMetric()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = DeviceMetric()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = DeviceMetric()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_type(self):
        resource = DeviceMetric()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_unit(self):
        resource = DeviceMetric()
        resource.unit = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'unit')
        assert result is not None

    def test_get_path_source(self):
        resource = DeviceMetric()
        resource.source = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'source')
        assert result is not None

    def test_get_path_parent(self):
        resource = DeviceMetric()
        resource.parent = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'parent')
        assert result is not None

    def test_get_path_operational_status(self):
        resource = DeviceMetric()
        resource.operationalStatus = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'operationalStatus')
        assert result is not None

    def test_get_path_color(self):
        resource = DeviceMetric()
        resource.color = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'color')
        assert result is not None

    def test_get_path_category(self):
        resource = DeviceMetric()
        resource.category = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_measurement_period(self):
        resource = DeviceMetric()
        resource.measurementPeriod = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'measurementPeriod')
        assert result is not None

    def test_get_path_calibration(self):
        resource = DeviceMetric()
        resource.calibration = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'calibration')
        assert result is not None


class TestSetPathDeviceMetric:

    def test_set_path_id(self):
        resource = DeviceMetric()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = DeviceMetric()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'DeviceMetric.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = DeviceMetric()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = DeviceMetric()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = DeviceMetric()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = DeviceMetric()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = DeviceMetric()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = DeviceMetric()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = DeviceMetric()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = DeviceMetric()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_type(self):
        resource = DeviceMetric()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_unit(self):
        resource = DeviceMetric()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'unit', value)
        assert result is True
        assert resource.unit is not None

    def test_set_path_source(self):
        resource = DeviceMetric()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'source', value)
        assert result is True
        assert resource.source is not None

    def test_set_path_parent(self):
        resource = DeviceMetric()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'parent', value)
        assert result is True
        assert resource.parent is not None

    def test_set_path_operational_status(self):
        resource = DeviceMetric()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'operationalStatus', value)
        assert result is True
        assert resource.operationalStatus is not None

    def test_set_path_color(self):
        resource = DeviceMetric()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'color', value)
        assert result is True
        assert resource.color is not None

    def test_set_path_category(self):
        resource = DeviceMetric()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_measurement_period(self):
        resource = DeviceMetric()
        value = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'measurementPeriod', value)
        assert result is True
        assert resource.measurementPeriod is not None

    def test_set_path_calibration(self):
        resource = DeviceMetric()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'calibration', value)
        assert result is True
        assert resource.calibration is not None


class TestParsePathDeviceMetric:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('DeviceMetric.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('DeviceMetric.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('DeviceMetric.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
