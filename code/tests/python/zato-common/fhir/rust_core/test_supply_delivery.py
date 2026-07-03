# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import SupplyDelivery


class TestToDictSupplyDelivery:

    def test_to_dict_empty(self):
        resource = SupplyDelivery()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'SupplyDelivery'

    def test_to_dict_with_id(self):
        resource = SupplyDelivery()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = SupplyDelivery()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, SupplyDelivery)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = SupplyDelivery()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = SupplyDelivery()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = SupplyDelivery()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = SupplyDelivery()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = SupplyDelivery()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = SupplyDelivery()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = SupplyDelivery()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = SupplyDelivery()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = SupplyDelivery()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_based_on(self):
        resource = SupplyDelivery()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_part_of(self):
        resource = SupplyDelivery()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'partOf' in result

    def test_to_dict_status(self):
        resource = SupplyDelivery()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_patient(self):
        resource = SupplyDelivery()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_type(self):
        resource = SupplyDelivery()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_supplied_item(self):
        resource = SupplyDelivery()
        resource.suppliedItem = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'suppliedItem' in result

    def test_to_dict_supplier(self):
        resource = SupplyDelivery()
        resource.supplier = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supplier' in result

    def test_to_dict_destination(self):
        resource = SupplyDelivery()
        resource.destination = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'destination' in result

    def test_to_dict_receiver(self):
        resource = SupplyDelivery()
        resource.receiver = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'receiver' in result


class TestFromDictSupplyDelivery:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'SupplyDelivery', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert isinstance(result, SupplyDelivery)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'SupplyDelivery'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert isinstance(result, SupplyDelivery)

    def test_from_dict_id(self):
        data = {'resourceType': 'SupplyDelivery', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'SupplyDelivery', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'SupplyDelivery', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'SupplyDelivery', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'SupplyDelivery', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'SupplyDelivery', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'SupplyDelivery', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'SupplyDelivery', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'SupplyDelivery', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.identifier is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'SupplyDelivery', 'basedOn': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.basedOn is not None

    def test_from_dict_part_of(self):
        data = {'resourceType': 'SupplyDelivery', 'partOf': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.partOf is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'SupplyDelivery', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.status is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'SupplyDelivery', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.patient is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'SupplyDelivery',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.type_ is not None

    def test_from_dict_supplied_item(self):
        data = {'resourceType': 'SupplyDelivery', 'suppliedItem': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.suppliedItem is not None

    def test_from_dict_supplier(self):
        data = {'resourceType': 'SupplyDelivery', 'supplier': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.supplier is not None

    def test_from_dict_destination(self):
        data = {'resourceType': 'SupplyDelivery', 'destination': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.destination is not None

    def test_from_dict_receiver(self):
        data = {'resourceType': 'SupplyDelivery', 'receiver': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SupplyDelivery)
        assert result.receiver is not None


class TestGetPathSupplyDelivery:

    def test_get_path_id(self):
        resource = SupplyDelivery()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = SupplyDelivery()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = SupplyDelivery()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'SupplyDelivery.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = SupplyDelivery()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = SupplyDelivery()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = SupplyDelivery()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = SupplyDelivery()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = SupplyDelivery()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = SupplyDelivery()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = SupplyDelivery()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = SupplyDelivery()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_based_on(self):
        resource = SupplyDelivery()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_part_of(self):
        resource = SupplyDelivery()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'partOf')
        assert result is not None

    def test_get_path_status(self):
        resource = SupplyDelivery()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_patient(self):
        resource = SupplyDelivery()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_type(self):
        resource = SupplyDelivery()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_supplied_item(self):
        resource = SupplyDelivery()
        resource.suppliedItem = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'suppliedItem')
        assert result is not None

    def test_get_path_supplier(self):
        resource = SupplyDelivery()
        resource.supplier = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supplier')
        assert result is not None

    def test_get_path_destination(self):
        resource = SupplyDelivery()
        resource.destination = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'destination')
        assert result is not None

    def test_get_path_receiver(self):
        resource = SupplyDelivery()
        resource.receiver = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'receiver')
        assert result is not None


class TestSetPathSupplyDelivery:

    def test_set_path_id(self):
        resource = SupplyDelivery()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = SupplyDelivery()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'SupplyDelivery.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = SupplyDelivery()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = SupplyDelivery()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = SupplyDelivery()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = SupplyDelivery()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = SupplyDelivery()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = SupplyDelivery()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = SupplyDelivery()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = SupplyDelivery()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_based_on(self):
        resource = SupplyDelivery()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_part_of(self):
        resource = SupplyDelivery()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'partOf', value)
        assert result is True
        assert resource.partOf is not None

    def test_set_path_status(self):
        resource = SupplyDelivery()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_patient(self):
        resource = SupplyDelivery()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_type(self):
        resource = SupplyDelivery()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_supplied_item(self):
        resource = SupplyDelivery()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'suppliedItem', value)
        assert result is True
        assert resource.suppliedItem is not None

    def test_set_path_supplier(self):
        resource = SupplyDelivery()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supplier', value)
        assert result is True
        assert resource.supplier is not None

    def test_set_path_destination(self):
        resource = SupplyDelivery()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'destination', value)
        assert result is True
        assert resource.destination is not None

    def test_set_path_receiver(self):
        resource = SupplyDelivery()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'receiver', value)
        assert result is True
        assert resource.receiver is not None


class TestParsePathSupplyDelivery:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('SupplyDelivery.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('SupplyDelivery.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('SupplyDelivery.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
