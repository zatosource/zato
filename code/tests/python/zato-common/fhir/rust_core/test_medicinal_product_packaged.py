# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import MedicinalProductPackaged


class TestToDictMedicinalProductPackaged:

    def test_to_dict_empty(self):
        resource = MedicinalProductPackaged()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'MedicinalProductPackaged'

    def test_to_dict_with_id(self):
        resource = MedicinalProductPackaged()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = MedicinalProductPackaged()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, MedicinalProductPackaged)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = MedicinalProductPackaged()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = MedicinalProductPackaged()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = MedicinalProductPackaged()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = MedicinalProductPackaged()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = MedicinalProductPackaged()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = MedicinalProductPackaged()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = MedicinalProductPackaged()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = MedicinalProductPackaged()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = MedicinalProductPackaged()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_subject(self):
        resource = MedicinalProductPackaged()
        resource.subject = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_description(self):
        resource = MedicinalProductPackaged()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_legal_status_of_supply(self):
        resource = MedicinalProductPackaged()
        resource.legalStatusOfSupply = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'legalStatusOfSupply' in result

    def test_to_dict_marketing_status(self):
        resource = MedicinalProductPackaged()
        resource.marketingStatus = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'marketingStatus' in result

    def test_to_dict_marketing_authorization(self):
        resource = MedicinalProductPackaged()
        resource.marketingAuthorization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'marketingAuthorization' in result

    def test_to_dict_manufacturer(self):
        resource = MedicinalProductPackaged()
        resource.manufacturer = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'manufacturer' in result

    def test_to_dict_batch_identifier(self):
        resource = MedicinalProductPackaged()
        resource.batchIdentifier = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'batchIdentifier' in result

    def test_to_dict_package_item(self):
        resource = MedicinalProductPackaged()
        resource.packageItem = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'packageItem' in result


class TestFromDictMedicinalProductPackaged:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert isinstance(result, MedicinalProductPackaged)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'MedicinalProductPackaged'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert isinstance(result, MedicinalProductPackaged)

    def test_from_dict_id(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.identifier is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'subject': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.subject is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.description is not None

    def test_from_dict_legal_status_of_supply(self):
        data = {'legalStatusOfSupply': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                 'text': 'Test concept'},
         'resourceType': 'MedicinalProductPackaged'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.legalStatusOfSupply is not None

    def test_from_dict_marketing_status(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'marketingStatus': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.marketingStatus is not None

    def test_from_dict_marketing_authorization(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'marketingAuthorization': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.marketingAuthorization is not None

    def test_from_dict_manufacturer(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'manufacturer': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.manufacturer is not None

    def test_from_dict_batch_identifier(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'batchIdentifier': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.batchIdentifier is not None

    def test_from_dict_package_item(self):
        data = {'resourceType': 'MedicinalProductPackaged', 'packageItem': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPackaged)
        assert result.packageItem is not None


class TestGetPathMedicinalProductPackaged:

    def test_get_path_id(self):
        resource = MedicinalProductPackaged()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = MedicinalProductPackaged()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = MedicinalProductPackaged()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'MedicinalProductPackaged.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = MedicinalProductPackaged()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = MedicinalProductPackaged()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = MedicinalProductPackaged()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = MedicinalProductPackaged()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = MedicinalProductPackaged()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = MedicinalProductPackaged()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = MedicinalProductPackaged()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = MedicinalProductPackaged()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_subject(self):
        resource = MedicinalProductPackaged()
        resource.subject = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_description(self):
        resource = MedicinalProductPackaged()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_legal_status_of_supply(self):
        resource = MedicinalProductPackaged()
        resource.legalStatusOfSupply = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'legalStatusOfSupply')
        assert result is not None

    def test_get_path_marketing_status(self):
        resource = MedicinalProductPackaged()
        resource.marketingStatus = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'marketingStatus')
        assert result is not None

    def test_get_path_marketing_authorization(self):
        resource = MedicinalProductPackaged()
        resource.marketingAuthorization = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'marketingAuthorization')
        assert result is not None

    def test_get_path_manufacturer(self):
        resource = MedicinalProductPackaged()
        resource.manufacturer = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'manufacturer')
        assert result is not None

    def test_get_path_batch_identifier(self):
        resource = MedicinalProductPackaged()
        resource.batchIdentifier = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'batchIdentifier')
        assert result is not None

    def test_get_path_package_item(self):
        resource = MedicinalProductPackaged()
        resource.packageItem = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'packageItem')
        assert result is not None


class TestSetPathMedicinalProductPackaged:

    def test_set_path_id(self):
        resource = MedicinalProductPackaged()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = MedicinalProductPackaged()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'MedicinalProductPackaged.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = MedicinalProductPackaged()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = MedicinalProductPackaged()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = MedicinalProductPackaged()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = MedicinalProductPackaged()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = MedicinalProductPackaged()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = MedicinalProductPackaged()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = MedicinalProductPackaged()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = MedicinalProductPackaged()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_subject(self):
        resource = MedicinalProductPackaged()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_description(self):
        resource = MedicinalProductPackaged()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_legal_status_of_supply(self):
        resource = MedicinalProductPackaged()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'legalStatusOfSupply', value)
        assert result is True
        assert resource.legalStatusOfSupply is not None

    def test_set_path_marketing_status(self):
        resource = MedicinalProductPackaged()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'marketingStatus', value)
        assert result is True
        assert resource.marketingStatus is not None

    def test_set_path_marketing_authorization(self):
        resource = MedicinalProductPackaged()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'marketingAuthorization', value)
        assert result is True
        assert resource.marketingAuthorization is not None

    def test_set_path_manufacturer(self):
        resource = MedicinalProductPackaged()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'manufacturer', value)
        assert result is True
        assert resource.manufacturer is not None

    def test_set_path_batch_identifier(self):
        resource = MedicinalProductPackaged()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'batchIdentifier', value)
        assert result is True
        assert resource.batchIdentifier is not None

    def test_set_path_package_item(self):
        resource = MedicinalProductPackaged()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'packageItem', value)
        assert result is True
        assert resource.packageItem is not None


class TestParsePathMedicinalProductPackaged:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductPackaged.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductPackaged.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductPackaged.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
