# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import DeviceDefinition


class TestToDictDeviceDefinition:

    def test_to_dict_empty(self):
        resource = DeviceDefinition()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'DeviceDefinition'

    def test_to_dict_with_id(self):
        resource = DeviceDefinition()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = DeviceDefinition()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, DeviceDefinition)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = DeviceDefinition()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = DeviceDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = DeviceDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = DeviceDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = DeviceDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = DeviceDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = DeviceDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = DeviceDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = DeviceDefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_udi_device_identifier(self):
        resource = DeviceDefinition()
        resource.udiDeviceIdentifier = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'udiDeviceIdentifier' in result

    def test_to_dict_device_name(self):
        resource = DeviceDefinition()
        resource.deviceName = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'deviceName' in result

    def test_to_dict_model_number(self):
        resource = DeviceDefinition()
        resource.modelNumber = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modelNumber' in result

    def test_to_dict_type(self):
        resource = DeviceDefinition()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_specialization(self):
        resource = DeviceDefinition()
        resource.specialization = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'specialization' in result

    def test_to_dict_version(self):
        resource = DeviceDefinition()
        resource.version = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_safety(self):
        resource = DeviceDefinition()
        resource.safety = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'safety' in result

    def test_to_dict_shelf_life_storage(self):
        resource = DeviceDefinition()
        resource.shelfLifeStorage = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'shelfLifeStorage' in result

    def test_to_dict_physical_characteristics(self):
        resource = DeviceDefinition()
        resource.physicalCharacteristics = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'physicalCharacteristics' in result

    def test_to_dict_language_code(self):
        resource = DeviceDefinition()
        resource.languageCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'languageCode' in result

    def test_to_dict_capability(self):
        resource = DeviceDefinition()
        resource.capability = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'capability' in result

    def test_to_dict_property(self):
        resource = DeviceDefinition()
        resource.property = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'property' in result

    def test_to_dict_owner(self):
        resource = DeviceDefinition()
        resource.owner = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'owner' in result

    def test_to_dict_contact(self):
        resource = DeviceDefinition()
        resource.contact = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_url(self):
        resource = DeviceDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_online_information(self):
        resource = DeviceDefinition()
        resource.onlineInformation = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'onlineInformation' in result

    def test_to_dict_note(self):
        resource = DeviceDefinition()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_quantity(self):
        resource = DeviceDefinition()
        resource.quantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'quantity' in result

    def test_to_dict_parent_device(self):
        resource = DeviceDefinition()
        resource.parentDevice = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'parentDevice' in result

    def test_to_dict_material(self):
        resource = DeviceDefinition()
        resource.material = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'material' in result


class TestFromDictDeviceDefinition:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'DeviceDefinition', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert isinstance(result, DeviceDefinition)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'DeviceDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert isinstance(result, DeviceDefinition)

    def test_from_dict_id(self):
        data = {'resourceType': 'DeviceDefinition', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'DeviceDefinition', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'DeviceDefinition', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'DeviceDefinition', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'DeviceDefinition', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'DeviceDefinition', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'DeviceDefinition', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'DeviceDefinition', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'DeviceDefinition', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.identifier is not None

    def test_from_dict_udi_device_identifier(self):
        data = {'resourceType': 'DeviceDefinition', 'udiDeviceIdentifier': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.udiDeviceIdentifier is not None

    def test_from_dict_device_name(self):
        data = {'resourceType': 'DeviceDefinition', 'deviceName': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.deviceName is not None

    def test_from_dict_model_number(self):
        data = {'resourceType': 'DeviceDefinition', 'modelNumber': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.modelNumber is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'DeviceDefinition',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.type_ is not None

    def test_from_dict_specialization(self):
        data = {'resourceType': 'DeviceDefinition', 'specialization': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.specialization is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'DeviceDefinition', 'version': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.version is not None

    def test_from_dict_safety(self):
        data = {'resourceType': 'DeviceDefinition',
         'safety': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                     'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.safety is not None

    def test_from_dict_shelf_life_storage(self):
        data = {'resourceType': 'DeviceDefinition', 'shelfLifeStorage': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.shelfLifeStorage is not None

    def test_from_dict_physical_characteristics(self):
        data = {'resourceType': 'DeviceDefinition', 'physicalCharacteristics': {'value': 'test'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.physicalCharacteristics is not None

    def test_from_dict_language_code(self):
        data = {'languageCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'DeviceDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.languageCode is not None

    def test_from_dict_capability(self):
        data = {'resourceType': 'DeviceDefinition', 'capability': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.capability is not None

    def test_from_dict_property(self):
        data = {'resourceType': 'DeviceDefinition', 'property': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.property is not None

    def test_from_dict_owner(self):
        data = {'resourceType': 'DeviceDefinition', 'owner': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.owner is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'DeviceDefinition', 'contact': [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.contact is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'DeviceDefinition', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.url is not None

    def test_from_dict_online_information(self):
        data = {'resourceType': 'DeviceDefinition', 'onlineInformation': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.onlineInformation is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'DeviceDefinition', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.note is not None

    def test_from_dict_quantity(self):
        data = {'resourceType': 'DeviceDefinition', 'quantity': {'value': 100, 'unit': 'mg'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.quantity is not None

    def test_from_dict_parent_device(self):
        data = {'resourceType': 'DeviceDefinition', 'parentDevice': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.parentDevice is not None

    def test_from_dict_material(self):
        data = {'resourceType': 'DeviceDefinition', 'material': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, DeviceDefinition)
        assert result.material is not None


class TestGetPathDeviceDefinition:

    def test_get_path_id(self):
        resource = DeviceDefinition()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = DeviceDefinition()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = DeviceDefinition()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'DeviceDefinition.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = DeviceDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = DeviceDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = DeviceDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = DeviceDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = DeviceDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = DeviceDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = DeviceDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = DeviceDefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_udi_device_identifier(self):
        resource = DeviceDefinition()
        resource.udiDeviceIdentifier = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'udiDeviceIdentifier')
        assert result is not None

    def test_get_path_device_name(self):
        resource = DeviceDefinition()
        resource.deviceName = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'deviceName')
        assert result is not None

    def test_get_path_model_number(self):
        resource = DeviceDefinition()
        resource.modelNumber = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modelNumber')
        assert result is not None

    def test_get_path_type(self):
        resource = DeviceDefinition()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_specialization(self):
        resource = DeviceDefinition()
        resource.specialization = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'specialization')
        assert result is not None

    def test_get_path_version(self):
        resource = DeviceDefinition()
        resource.version = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_safety(self):
        resource = DeviceDefinition()
        resource.safety = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'safety')
        assert result is not None

    def test_get_path_shelf_life_storage(self):
        resource = DeviceDefinition()
        resource.shelfLifeStorage = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'shelfLifeStorage')
        assert result is not None

    def test_get_path_physical_characteristics(self):
        resource = DeviceDefinition()
        resource.physicalCharacteristics = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'physicalCharacteristics')
        assert result is not None

    def test_get_path_language_code(self):
        resource = DeviceDefinition()
        resource.languageCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'languageCode')
        assert result is not None

    def test_get_path_capability(self):
        resource = DeviceDefinition()
        resource.capability = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'capability')
        assert result is not None

    def test_get_path_property(self):
        resource = DeviceDefinition()
        resource.property = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'property')
        assert result is not None

    def test_get_path_owner(self):
        resource = DeviceDefinition()
        resource.owner = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'owner')
        assert result is not None

    def test_get_path_contact(self):
        resource = DeviceDefinition()
        resource.contact = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_url(self):
        resource = DeviceDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_online_information(self):
        resource = DeviceDefinition()
        resource.onlineInformation = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'onlineInformation')
        assert result is not None

    def test_get_path_note(self):
        resource = DeviceDefinition()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_quantity(self):
        resource = DeviceDefinition()
        resource.quantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'quantity')
        assert result is not None

    def test_get_path_parent_device(self):
        resource = DeviceDefinition()
        resource.parentDevice = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'parentDevice')
        assert result is not None

    def test_get_path_material(self):
        resource = DeviceDefinition()
        resource.material = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'material')
        assert result is not None


class TestSetPathDeviceDefinition:

    def test_set_path_id(self):
        resource = DeviceDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = DeviceDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'DeviceDefinition.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = DeviceDefinition()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = DeviceDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = DeviceDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = DeviceDefinition()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = DeviceDefinition()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = DeviceDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = DeviceDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = DeviceDefinition()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_udi_device_identifier(self):
        resource = DeviceDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'udiDeviceIdentifier', value)
        assert result is True
        assert resource.udiDeviceIdentifier is not None

    def test_set_path_device_name(self):
        resource = DeviceDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'deviceName', value)
        assert result is True
        assert resource.deviceName is not None

    def test_set_path_model_number(self):
        resource = DeviceDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modelNumber', value)
        assert result is True
        assert resource.modelNumber is not None

    def test_set_path_type(self):
        resource = DeviceDefinition()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_specialization(self):
        resource = DeviceDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'specialization', value)
        assert result is True
        assert resource.specialization is not None

    def test_set_path_version(self):
        resource = DeviceDefinition()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_safety(self):
        resource = DeviceDefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'safety', value)
        assert result is True
        assert resource.safety is not None

    def test_set_path_shelf_life_storage(self):
        resource = DeviceDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'shelfLifeStorage', value)
        assert result is True
        assert resource.shelfLifeStorage is not None

    def test_set_path_physical_characteristics(self):
        resource = DeviceDefinition()
        value = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'physicalCharacteristics', value)
        assert result is True
        assert resource.physicalCharacteristics is not None

    def test_set_path_language_code(self):
        resource = DeviceDefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'languageCode', value)
        assert result is True
        assert resource.languageCode is not None

    def test_set_path_capability(self):
        resource = DeviceDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'capability', value)
        assert result is True
        assert resource.capability is not None

    def test_set_path_property(self):
        resource = DeviceDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'property', value)
        assert result is True
        assert resource.property is not None

    def test_set_path_owner(self):
        resource = DeviceDefinition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'owner', value)
        assert result is True
        assert resource.owner is not None

    def test_set_path_contact(self):
        resource = DeviceDefinition()
        value = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_url(self):
        resource = DeviceDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_online_information(self):
        resource = DeviceDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'onlineInformation', value)
        assert result is True
        assert resource.onlineInformation is not None

    def test_set_path_note(self):
        resource = DeviceDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_quantity(self):
        resource = DeviceDefinition()
        value = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'quantity', value)
        assert result is True
        assert resource.quantity is not None

    def test_set_path_parent_device(self):
        resource = DeviceDefinition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'parentDevice', value)
        assert result is True
        assert resource.parentDevice is not None

    def test_set_path_material(self):
        resource = DeviceDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'material', value)
        assert result is True
        assert resource.material is not None


class TestParsePathDeviceDefinition:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('DeviceDefinition.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('DeviceDefinition.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('DeviceDefinition.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
