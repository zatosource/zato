# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import BiologicallyDerivedProduct


class TestToDictBiologicallyDerivedProduct:

    def test_to_dict_empty(self):
        resource = BiologicallyDerivedProduct()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'BiologicallyDerivedProduct'

    def test_to_dict_with_id(self):
        resource = BiologicallyDerivedProduct()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = BiologicallyDerivedProduct()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, BiologicallyDerivedProduct)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = BiologicallyDerivedProduct()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = BiologicallyDerivedProduct()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = BiologicallyDerivedProduct()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = BiologicallyDerivedProduct()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = BiologicallyDerivedProduct()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = BiologicallyDerivedProduct()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = BiologicallyDerivedProduct()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = BiologicallyDerivedProduct()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = BiologicallyDerivedProduct()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_product_category(self):
        resource = BiologicallyDerivedProduct()
        resource.productCategory = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'productCategory' in result

    def test_to_dict_product_code(self):
        resource = BiologicallyDerivedProduct()
        resource.productCode = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'productCode' in result

    def test_to_dict_status(self):
        resource = BiologicallyDerivedProduct()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_request(self):
        resource = BiologicallyDerivedProduct()
        resource.request = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'request' in result

    def test_to_dict_quantity(self):
        resource = BiologicallyDerivedProduct()
        resource.quantity = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'quantity' in result

    def test_to_dict_parent(self):
        resource = BiologicallyDerivedProduct()
        resource.parent = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'parent' in result

    def test_to_dict_collection(self):
        resource = BiologicallyDerivedProduct()
        resource.collection = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'collection' in result

    def test_to_dict_processing(self):
        resource = BiologicallyDerivedProduct()
        resource.processing = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'processing' in result

    def test_to_dict_manipulation(self):
        resource = BiologicallyDerivedProduct()
        resource.manipulation = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'manipulation' in result

    def test_to_dict_storage(self):
        resource = BiologicallyDerivedProduct()
        resource.storage = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'storage' in result


class TestFromDictBiologicallyDerivedProduct:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert isinstance(result, BiologicallyDerivedProduct)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'BiologicallyDerivedProduct'}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert isinstance(result, BiologicallyDerivedProduct)

    def test_from_dict_id(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.identifier is not None

    def test_from_dict_product_category(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'productCategory': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.productCategory is not None

    def test_from_dict_product_code(self):
        data = {'productCode': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'},
         'resourceType': 'BiologicallyDerivedProduct'}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.productCode is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.status is not None

    def test_from_dict_request(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'request': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.request is not None

    def test_from_dict_quantity(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'quantity': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.quantity is not None

    def test_from_dict_parent(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'parent': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.parent is not None

    def test_from_dict_collection(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'collection': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.collection is not None

    def test_from_dict_processing(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'processing': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.processing is not None

    def test_from_dict_manipulation(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'manipulation': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.manipulation is not None

    def test_from_dict_storage(self):
        data = {'resourceType': 'BiologicallyDerivedProduct', 'storage': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, BiologicallyDerivedProduct)
        assert result.storage is not None


class TestGetPathBiologicallyDerivedProduct:

    def test_get_path_id(self):
        resource = BiologicallyDerivedProduct()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = BiologicallyDerivedProduct()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = BiologicallyDerivedProduct()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'BiologicallyDerivedProduct.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = BiologicallyDerivedProduct()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = BiologicallyDerivedProduct()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = BiologicallyDerivedProduct()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = BiologicallyDerivedProduct()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = BiologicallyDerivedProduct()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = BiologicallyDerivedProduct()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = BiologicallyDerivedProduct()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = BiologicallyDerivedProduct()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_product_category(self):
        resource = BiologicallyDerivedProduct()
        resource.productCategory = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'productCategory')
        assert result is not None

    def test_get_path_product_code(self):
        resource = BiologicallyDerivedProduct()
        resource.productCode = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'productCode')
        assert result is not None

    def test_get_path_status(self):
        resource = BiologicallyDerivedProduct()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_request(self):
        resource = BiologicallyDerivedProduct()
        resource.request = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'request')
        assert result is not None

    def test_get_path_quantity(self):
        resource = BiologicallyDerivedProduct()
        resource.quantity = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'quantity')
        assert result is not None

    def test_get_path_parent(self):
        resource = BiologicallyDerivedProduct()
        resource.parent = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'parent')
        assert result is not None

    def test_get_path_collection(self):
        resource = BiologicallyDerivedProduct()
        resource.collection = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'collection')
        assert result is not None

    def test_get_path_processing(self):
        resource = BiologicallyDerivedProduct()
        resource.processing = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'processing')
        assert result is not None

    def test_get_path_manipulation(self):
        resource = BiologicallyDerivedProduct()
        resource.manipulation = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'manipulation')
        assert result is not None

    def test_get_path_storage(self):
        resource = BiologicallyDerivedProduct()
        resource.storage = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'storage')
        assert result is not None


class TestSetPathBiologicallyDerivedProduct:

    def test_set_path_id(self):
        resource = BiologicallyDerivedProduct()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = BiologicallyDerivedProduct()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'BiologicallyDerivedProduct.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = BiologicallyDerivedProduct()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = BiologicallyDerivedProduct()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = BiologicallyDerivedProduct()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = BiologicallyDerivedProduct()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = BiologicallyDerivedProduct()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = BiologicallyDerivedProduct()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = BiologicallyDerivedProduct()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = BiologicallyDerivedProduct()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_product_category(self):
        resource = BiologicallyDerivedProduct()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'productCategory', value)
        assert result is True
        assert resource.productCategory is not None

    def test_set_path_product_code(self):
        resource = BiologicallyDerivedProduct()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'productCode', value)
        assert result is True
        assert resource.productCode is not None

    def test_set_path_status(self):
        resource = BiologicallyDerivedProduct()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_request(self):
        resource = BiologicallyDerivedProduct()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'request', value)
        assert result is True
        assert resource.request is not None

    def test_set_path_quantity(self):
        resource = BiologicallyDerivedProduct()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'quantity', value)
        assert result is True
        assert resource.quantity is not None

    def test_set_path_parent(self):
        resource = BiologicallyDerivedProduct()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'parent', value)
        assert result is True
        assert resource.parent is not None

    def test_set_path_collection(self):
        resource = BiologicallyDerivedProduct()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'collection', value)
        assert result is True
        assert resource.collection is not None

    def test_set_path_processing(self):
        resource = BiologicallyDerivedProduct()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'processing', value)
        assert result is True
        assert resource.processing is not None

    def test_set_path_manipulation(self):
        resource = BiologicallyDerivedProduct()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'manipulation', value)
        assert result is True
        assert resource.manipulation is not None

    def test_set_path_storage(self):
        resource = BiologicallyDerivedProduct()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'storage', value)
        assert result is True
        assert resource.storage is not None


class TestParsePathBiologicallyDerivedProduct:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('BiologicallyDerivedProduct.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('BiologicallyDerivedProduct.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('BiologicallyDerivedProduct.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
