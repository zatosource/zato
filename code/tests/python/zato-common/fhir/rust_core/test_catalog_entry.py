# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import CatalogEntry


class TestToDictCatalogEntry:

    def test_to_dict_empty(self):
        resource = CatalogEntry()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'CatalogEntry'

    def test_to_dict_with_id(self):
        resource = CatalogEntry()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = CatalogEntry()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, CatalogEntry)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = CatalogEntry()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = CatalogEntry()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = CatalogEntry()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = CatalogEntry()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = CatalogEntry()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = CatalogEntry()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = CatalogEntry()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = CatalogEntry()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = CatalogEntry()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_type(self):
        resource = CatalogEntry()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_orderable(self):
        resource = CatalogEntry()
        resource.orderable = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'orderable' in result

    def test_to_dict_referenced_item(self):
        resource = CatalogEntry()
        resource.referencedItem = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'referencedItem' in result

    def test_to_dict_additional_identifier(self):
        resource = CatalogEntry()
        resource.additionalIdentifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'additionalIdentifier' in result

    def test_to_dict_classification(self):
        resource = CatalogEntry()
        resource.classification = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'classification' in result

    def test_to_dict_status(self):
        resource = CatalogEntry()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_validity_period(self):
        resource = CatalogEntry()
        resource.validityPeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'validityPeriod' in result

    def test_to_dict_valid_to(self):
        resource = CatalogEntry()
        resource.validTo = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'validTo' in result

    def test_to_dict_last_updated(self):
        resource = CatalogEntry()
        resource.lastUpdated = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lastUpdated' in result

    def test_to_dict_additional_characteristic(self):
        resource = CatalogEntry()
        resource.additionalCharacteristic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'additionalCharacteristic' in result

    def test_to_dict_additional_classification(self):
        resource = CatalogEntry()
        resource.additionalClassification = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'additionalClassification' in result

    def test_to_dict_related_entry(self):
        resource = CatalogEntry()
        resource.relatedEntry = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relatedEntry' in result


class TestFromDictCatalogEntry:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'CatalogEntry', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert isinstance(result, CatalogEntry)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'CatalogEntry'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert isinstance(result, CatalogEntry)

    def test_from_dict_id(self):
        data = {'resourceType': 'CatalogEntry', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'CatalogEntry', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'CatalogEntry', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'CatalogEntry', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'CatalogEntry', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'CatalogEntry', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'CatalogEntry', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'CatalogEntry', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'CatalogEntry', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.identifier is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'CatalogEntry',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.type_ is not None

    def test_from_dict_orderable(self):
        data = {'resourceType': 'CatalogEntry', 'orderable': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.orderable is not None

    def test_from_dict_referenced_item(self):
        data = {'resourceType': 'CatalogEntry', 'referencedItem': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.referencedItem is not None

    def test_from_dict_additional_identifier(self):
        data = {'resourceType': 'CatalogEntry', 'additionalIdentifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.additionalIdentifier is not None

    def test_from_dict_classification(self):
        data = {'classification': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                             'text': 'Test concept'}],
         'resourceType': 'CatalogEntry'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.classification is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'CatalogEntry', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.status is not None

    def test_from_dict_validity_period(self):
        data = {'resourceType': 'CatalogEntry', 'validityPeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.validityPeriod is not None

    def test_from_dict_valid_to(self):
        data = {'resourceType': 'CatalogEntry', 'validTo': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.validTo is not None

    def test_from_dict_last_updated(self):
        data = {'resourceType': 'CatalogEntry', 'lastUpdated': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.lastUpdated is not None

    def test_from_dict_additional_characteristic(self):
        data = {'additionalCharacteristic': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                       'text': 'Test concept'}],
         'resourceType': 'CatalogEntry'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.additionalCharacteristic is not None

    def test_from_dict_additional_classification(self):
        data = {'additionalClassification': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                       'text': 'Test concept'}],
         'resourceType': 'CatalogEntry'}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.additionalClassification is not None

    def test_from_dict_related_entry(self):
        data = {'resourceType': 'CatalogEntry', 'relatedEntry': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, CatalogEntry)
        assert result.relatedEntry is not None


class TestGetPathCatalogEntry:

    def test_get_path_id(self):
        resource = CatalogEntry()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = CatalogEntry()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = CatalogEntry()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'CatalogEntry.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = CatalogEntry()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = CatalogEntry()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = CatalogEntry()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = CatalogEntry()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = CatalogEntry()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = CatalogEntry()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = CatalogEntry()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = CatalogEntry()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_type(self):
        resource = CatalogEntry()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_orderable(self):
        resource = CatalogEntry()
        resource.orderable = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'orderable')
        assert result is not None

    def test_get_path_referenced_item(self):
        resource = CatalogEntry()
        resource.referencedItem = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'referencedItem')
        assert result is not None

    def test_get_path_additional_identifier(self):
        resource = CatalogEntry()
        resource.additionalIdentifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'additionalIdentifier')
        assert result is not None

    def test_get_path_classification(self):
        resource = CatalogEntry()
        resource.classification = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'classification')
        assert result is not None

    def test_get_path_status(self):
        resource = CatalogEntry()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_validity_period(self):
        resource = CatalogEntry()
        resource.validityPeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'validityPeriod')
        assert result is not None

    def test_get_path_valid_to(self):
        resource = CatalogEntry()
        resource.validTo = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'validTo')
        assert result is not None

    def test_get_path_last_updated(self):
        resource = CatalogEntry()
        resource.lastUpdated = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lastUpdated')
        assert result is not None

    def test_get_path_additional_characteristic(self):
        resource = CatalogEntry()
        resource.additionalCharacteristic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'additionalCharacteristic')
        assert result is not None

    def test_get_path_additional_classification(self):
        resource = CatalogEntry()
        resource.additionalClassification = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'additionalClassification')
        assert result is not None

    def test_get_path_related_entry(self):
        resource = CatalogEntry()
        resource.relatedEntry = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relatedEntry')
        assert result is not None


class TestSetPathCatalogEntry:

    def test_set_path_id(self):
        resource = CatalogEntry()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = CatalogEntry()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'CatalogEntry.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = CatalogEntry()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = CatalogEntry()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = CatalogEntry()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = CatalogEntry()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = CatalogEntry()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = CatalogEntry()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = CatalogEntry()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = CatalogEntry()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_type(self):
        resource = CatalogEntry()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_orderable(self):
        resource = CatalogEntry()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'orderable', value)
        assert result is True
        assert resource.orderable is not None

    def test_set_path_referenced_item(self):
        resource = CatalogEntry()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'referencedItem', value)
        assert result is True
        assert resource.referencedItem is not None

    def test_set_path_additional_identifier(self):
        resource = CatalogEntry()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'additionalIdentifier', value)
        assert result is True
        assert resource.additionalIdentifier is not None

    def test_set_path_classification(self):
        resource = CatalogEntry()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'classification', value)
        assert result is True
        assert resource.classification is not None

    def test_set_path_status(self):
        resource = CatalogEntry()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_validity_period(self):
        resource = CatalogEntry()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'validityPeriod', value)
        assert result is True
        assert resource.validityPeriod is not None

    def test_set_path_valid_to(self):
        resource = CatalogEntry()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'validTo', value)
        assert result is True
        assert resource.validTo is not None

    def test_set_path_last_updated(self):
        resource = CatalogEntry()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lastUpdated', value)
        assert result is True
        assert resource.lastUpdated is not None

    def test_set_path_additional_characteristic(self):
        resource = CatalogEntry()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'additionalCharacteristic', value)
        assert result is True
        assert resource.additionalCharacteristic is not None

    def test_set_path_additional_classification(self):
        resource = CatalogEntry()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'additionalClassification', value)
        assert result is True
        assert resource.additionalClassification is not None

    def test_set_path_related_entry(self):
        resource = CatalogEntry()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relatedEntry', value)
        assert result is True
        assert resource.relatedEntry is not None


class TestParsePathCatalogEntry:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('CatalogEntry.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('CatalogEntry.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('CatalogEntry.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
