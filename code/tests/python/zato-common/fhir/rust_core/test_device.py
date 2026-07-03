# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Device


class TestToDictDevice:

    def test_to_dict_empty(self):
        resource = Device()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Device'

    def test_to_dict_with_id(self):
        resource = Device()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Device()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Device)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Device()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Device()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Device()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Device()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Device()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Device()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Device()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Device()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = Device()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_definition(self):
        resource = Device()
        resource.definition = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'definition' in result

    def test_to_dict_udi_carrier(self):
        resource = Device()
        resource.udiCarrier = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'udiCarrier' in result

    def test_to_dict_status(self):
        resource = Device()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_status_reason(self):
        resource = Device()
        resource.statusReason = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'statusReason' in result

    def test_to_dict_distinct_identifier(self):
        resource = Device()
        resource.distinctIdentifier = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'distinctIdentifier' in result

    def test_to_dict_manufacturer(self):
        resource = Device()
        resource.manufacturer = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'manufacturer' in result

    def test_to_dict_manufacture_date(self):
        resource = Device()
        resource.manufactureDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'manufactureDate' in result

    def test_to_dict_expiration_date(self):
        resource = Device()
        resource.expirationDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'expirationDate' in result

    def test_to_dict_lot_number(self):
        resource = Device()
        resource.lotNumber = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lotNumber' in result

    def test_to_dict_serial_number(self):
        resource = Device()
        resource.serialNumber = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'serialNumber' in result

    def test_to_dict_device_name(self):
        resource = Device()
        resource.deviceName = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'deviceName' in result

    def test_to_dict_model_number(self):
        resource = Device()
        resource.modelNumber = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modelNumber' in result

    def test_to_dict_part_number(self):
        resource = Device()
        resource.partNumber = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'partNumber' in result

    def test_to_dict_type(self):
        resource = Device()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_specialization(self):
        resource = Device()
        resource.specialization = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'specialization' in result

    def test_to_dict_version(self):
        resource = Device()
        resource.version = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_property(self):
        resource = Device()
        resource.property = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'property' in result

    def test_to_dict_patient(self):
        resource = Device()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_owner(self):
        resource = Device()
        resource.owner = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'owner' in result

    def test_to_dict_contact(self):
        resource = Device()
        resource.contact = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_location(self):
        resource = Device()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'location' in result

    def test_to_dict_url(self):
        resource = Device()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_note(self):
        resource = Device()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_safety(self):
        resource = Device()
        resource.safety = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'safety' in result

    def test_to_dict_parent(self):
        resource = Device()
        resource.parent = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'parent' in result


class TestFromDictDevice:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Device', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert isinstance(result, Device)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Device'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert isinstance(result, Device)

    def test_from_dict_id(self):
        data = {'resourceType': 'Device', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Device', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Device', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Device', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Device', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Device', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Device', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Device', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Device', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.identifier is not None

    def test_from_dict_definition(self):
        data = {'resourceType': 'Device', 'definition': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.definition is not None

    def test_from_dict_udi_carrier(self):
        data = {'resourceType': 'Device', 'udiCarrier': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.udiCarrier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Device', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.status is not None

    def test_from_dict_status_reason(self):
        data = {'resourceType': 'Device',
         'statusReason': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.statusReason is not None

    def test_from_dict_distinct_identifier(self):
        data = {'resourceType': 'Device', 'distinctIdentifier': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.distinctIdentifier is not None

    def test_from_dict_manufacturer(self):
        data = {'resourceType': 'Device', 'manufacturer': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.manufacturer is not None

    def test_from_dict_manufacture_date(self):
        data = {'resourceType': 'Device', 'manufactureDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.manufactureDate is not None

    def test_from_dict_expiration_date(self):
        data = {'resourceType': 'Device', 'expirationDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.expirationDate is not None

    def test_from_dict_lot_number(self):
        data = {'resourceType': 'Device', 'lotNumber': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.lotNumber is not None

    def test_from_dict_serial_number(self):
        data = {'resourceType': 'Device', 'serialNumber': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.serialNumber is not None

    def test_from_dict_device_name(self):
        data = {'resourceType': 'Device', 'deviceName': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.deviceName is not None

    def test_from_dict_model_number(self):
        data = {'resourceType': 'Device', 'modelNumber': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.modelNumber is not None

    def test_from_dict_part_number(self):
        data = {'resourceType': 'Device', 'partNumber': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.partNumber is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'Device',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.type_ is not None

    def test_from_dict_specialization(self):
        data = {'resourceType': 'Device', 'specialization': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.specialization is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'Device', 'version': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.version is not None

    def test_from_dict_property(self):
        data = {'resourceType': 'Device', 'property': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.property is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'Device', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.patient is not None

    def test_from_dict_owner(self):
        data = {'resourceType': 'Device', 'owner': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.owner is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'Device', 'contact': [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.contact is not None

    def test_from_dict_location(self):
        data = {'resourceType': 'Device', 'location': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.location is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'Device', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.url is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'Device', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.note is not None

    def test_from_dict_safety(self):
        data = {'resourceType': 'Device',
         'safety': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                     'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.safety is not None

    def test_from_dict_parent(self):
        data = {'resourceType': 'Device', 'parent': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Device)
        assert result.parent is not None


class TestGetPathDevice:

    def test_get_path_id(self):
        resource = Device()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Device()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Device()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Device.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Device()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Device()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Device()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Device()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Device()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Device()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Device()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Device()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_definition(self):
        resource = Device()
        resource.definition = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'definition')
        assert result is not None

    def test_get_path_udi_carrier(self):
        resource = Device()
        resource.udiCarrier = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'udiCarrier')
        assert result is not None

    def test_get_path_status(self):
        resource = Device()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_status_reason(self):
        resource = Device()
        resource.statusReason = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'statusReason')
        assert result is not None

    def test_get_path_distinct_identifier(self):
        resource = Device()
        resource.distinctIdentifier = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'distinctIdentifier')
        assert result is not None

    def test_get_path_manufacturer(self):
        resource = Device()
        resource.manufacturer = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'manufacturer')
        assert result is not None

    def test_get_path_manufacture_date(self):
        resource = Device()
        resource.manufactureDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'manufactureDate')
        assert result is not None

    def test_get_path_expiration_date(self):
        resource = Device()
        resource.expirationDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'expirationDate')
        assert result is not None

    def test_get_path_lot_number(self):
        resource = Device()
        resource.lotNumber = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lotNumber')
        assert result is not None

    def test_get_path_serial_number(self):
        resource = Device()
        resource.serialNumber = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'serialNumber')
        assert result is not None

    def test_get_path_device_name(self):
        resource = Device()
        resource.deviceName = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'deviceName')
        assert result is not None

    def test_get_path_model_number(self):
        resource = Device()
        resource.modelNumber = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modelNumber')
        assert result is not None

    def test_get_path_part_number(self):
        resource = Device()
        resource.partNumber = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'partNumber')
        assert result is not None

    def test_get_path_type(self):
        resource = Device()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_specialization(self):
        resource = Device()
        resource.specialization = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'specialization')
        assert result is not None

    def test_get_path_version(self):
        resource = Device()
        resource.version = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_property(self):
        resource = Device()
        resource.property = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'property')
        assert result is not None

    def test_get_path_patient(self):
        resource = Device()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_owner(self):
        resource = Device()
        resource.owner = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'owner')
        assert result is not None

    def test_get_path_contact(self):
        resource = Device()
        resource.contact = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_location(self):
        resource = Device()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'location')
        assert result is not None

    def test_get_path_url(self):
        resource = Device()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_note(self):
        resource = Device()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_safety(self):
        resource = Device()
        resource.safety = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'safety')
        assert result is not None

    def test_get_path_parent(self):
        resource = Device()
        resource.parent = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'parent')
        assert result is not None


class TestSetPathDevice:

    def test_set_path_id(self):
        resource = Device()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Device()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Device.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Device()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Device()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Device()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Device()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Device()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Device()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Device()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = Device()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_definition(self):
        resource = Device()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'definition', value)
        assert result is True
        assert resource.definition is not None

    def test_set_path_udi_carrier(self):
        resource = Device()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'udiCarrier', value)
        assert result is True
        assert resource.udiCarrier is not None

    def test_set_path_status(self):
        resource = Device()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_status_reason(self):
        resource = Device()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'statusReason', value)
        assert result is True
        assert resource.statusReason is not None

    def test_set_path_distinct_identifier(self):
        resource = Device()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'distinctIdentifier', value)
        assert result is True
        assert resource.distinctIdentifier is not None

    def test_set_path_manufacturer(self):
        resource = Device()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'manufacturer', value)
        assert result is True
        assert resource.manufacturer is not None

    def test_set_path_manufacture_date(self):
        resource = Device()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'manufactureDate', value)
        assert result is True
        assert resource.manufactureDate is not None

    def test_set_path_expiration_date(self):
        resource = Device()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'expirationDate', value)
        assert result is True
        assert resource.expirationDate is not None

    def test_set_path_lot_number(self):
        resource = Device()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lotNumber', value)
        assert result is True
        assert resource.lotNumber is not None

    def test_set_path_serial_number(self):
        resource = Device()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'serialNumber', value)
        assert result is True
        assert resource.serialNumber is not None

    def test_set_path_device_name(self):
        resource = Device()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'deviceName', value)
        assert result is True
        assert resource.deviceName is not None

    def test_set_path_model_number(self):
        resource = Device()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modelNumber', value)
        assert result is True
        assert resource.modelNumber is not None

    def test_set_path_part_number(self):
        resource = Device()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'partNumber', value)
        assert result is True
        assert resource.partNumber is not None

    def test_set_path_type(self):
        resource = Device()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_specialization(self):
        resource = Device()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'specialization', value)
        assert result is True
        assert resource.specialization is not None

    def test_set_path_version(self):
        resource = Device()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_property(self):
        resource = Device()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'property', value)
        assert result is True
        assert resource.property is not None

    def test_set_path_patient(self):
        resource = Device()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_owner(self):
        resource = Device()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'owner', value)
        assert result is True
        assert resource.owner is not None

    def test_set_path_contact(self):
        resource = Device()
        value = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_location(self):
        resource = Device()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'location', value)
        assert result is True
        assert resource.location is not None

    def test_set_path_url(self):
        resource = Device()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_note(self):
        resource = Device()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_safety(self):
        resource = Device()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'safety', value)
        assert result is True
        assert resource.safety is not None

    def test_set_path_parent(self):
        resource = Device()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'parent', value)
        assert result is True
        assert resource.parent is not None


class TestParsePathDevice:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Device.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Device.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Device.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
