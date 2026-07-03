# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import MedicinalProductManufactured


class TestToDictMedicinalProductManufactured:

    def test_to_dict_empty(self):
        resource = MedicinalProductManufactured()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'MedicinalProductManufactured'

    def test_to_dict_with_id(self):
        resource = MedicinalProductManufactured()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = MedicinalProductManufactured()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, MedicinalProductManufactured)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = MedicinalProductManufactured()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = MedicinalProductManufactured()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = MedicinalProductManufactured()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = MedicinalProductManufactured()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = MedicinalProductManufactured()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = MedicinalProductManufactured()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = MedicinalProductManufactured()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = MedicinalProductManufactured()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_manufactured_dose_form(self):
        resource = MedicinalProductManufactured()
        resource.manufacturedDoseForm = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'manufacturedDoseForm' in result

    def test_to_dict_unit_of_presentation(self):
        resource = MedicinalProductManufactured()
        resource.unitOfPresentation = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'unitOfPresentation' in result

    def test_to_dict_quantity(self):
        resource = MedicinalProductManufactured()
        resource.quantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'quantity' in result

    def test_to_dict_manufacturer(self):
        resource = MedicinalProductManufactured()
        resource.manufacturer = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'manufacturer' in result

    def test_to_dict_ingredient(self):
        resource = MedicinalProductManufactured()
        resource.ingredient = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'ingredient' in result

    def test_to_dict_physical_characteristics(self):
        resource = MedicinalProductManufactured()
        resource.physicalCharacteristics = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'physicalCharacteristics' in result

    def test_to_dict_other_characteristics(self):
        resource = MedicinalProductManufactured()
        resource.otherCharacteristics = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'otherCharacteristics' in result


class TestFromDictMedicinalProductManufactured:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'MedicinalProductManufactured', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert isinstance(result, MedicinalProductManufactured)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'MedicinalProductManufactured'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert isinstance(result, MedicinalProductManufactured)

    def test_from_dict_id(self):
        data = {'resourceType': 'MedicinalProductManufactured', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'MedicinalProductManufactured', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'MedicinalProductManufactured', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'MedicinalProductManufactured', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'MedicinalProductManufactured', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'MedicinalProductManufactured', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'MedicinalProductManufactured', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'MedicinalProductManufactured', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert result.modifierExtension is not None

    def test_from_dict_manufactured_dose_form(self):
        data = {'manufacturedDoseForm': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                  'text': 'Test concept'},
         'resourceType': 'MedicinalProductManufactured'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert result.manufacturedDoseForm is not None

    def test_from_dict_unit_of_presentation(self):
        data = {'resourceType': 'MedicinalProductManufactured',
         'unitOfPresentation': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert result.unitOfPresentation is not None

    def test_from_dict_quantity(self):
        data = {'resourceType': 'MedicinalProductManufactured', 'quantity': {'value': 100, 'unit': 'mg'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert result.quantity is not None

    def test_from_dict_manufacturer(self):
        data = {'resourceType': 'MedicinalProductManufactured', 'manufacturer': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert result.manufacturer is not None

    def test_from_dict_ingredient(self):
        data = {'resourceType': 'MedicinalProductManufactured', 'ingredient': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert result.ingredient is not None

    def test_from_dict_physical_characteristics(self):
        data = {'resourceType': 'MedicinalProductManufactured', 'physicalCharacteristics': {'value': 'test'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert result.physicalCharacteristics is not None

    def test_from_dict_other_characteristics(self):
        data = {'otherCharacteristics': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                   'text': 'Test concept'}],
         'resourceType': 'MedicinalProductManufactured'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductManufactured)
        assert result.otherCharacteristics is not None


class TestGetPathMedicinalProductManufactured:

    def test_get_path_id(self):
        resource = MedicinalProductManufactured()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = MedicinalProductManufactured()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = MedicinalProductManufactured()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'MedicinalProductManufactured.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = MedicinalProductManufactured()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = MedicinalProductManufactured()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = MedicinalProductManufactured()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = MedicinalProductManufactured()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = MedicinalProductManufactured()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = MedicinalProductManufactured()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = MedicinalProductManufactured()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_manufactured_dose_form(self):
        resource = MedicinalProductManufactured()
        resource.manufacturedDoseForm = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'manufacturedDoseForm')
        assert result is not None

    def test_get_path_unit_of_presentation(self):
        resource = MedicinalProductManufactured()
        resource.unitOfPresentation = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'unitOfPresentation')
        assert result is not None

    def test_get_path_quantity(self):
        resource = MedicinalProductManufactured()
        resource.quantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'quantity')
        assert result is not None

    def test_get_path_manufacturer(self):
        resource = MedicinalProductManufactured()
        resource.manufacturer = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'manufacturer')
        assert result is not None

    def test_get_path_ingredient(self):
        resource = MedicinalProductManufactured()
        resource.ingredient = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ingredient')
        assert result is not None

    def test_get_path_physical_characteristics(self):
        resource = MedicinalProductManufactured()
        resource.physicalCharacteristics = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'physicalCharacteristics')
        assert result is not None

    def test_get_path_other_characteristics(self):
        resource = MedicinalProductManufactured()
        resource.otherCharacteristics = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'otherCharacteristics')
        assert result is not None


class TestSetPathMedicinalProductManufactured:

    def test_set_path_id(self):
        resource = MedicinalProductManufactured()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = MedicinalProductManufactured()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'MedicinalProductManufactured.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = MedicinalProductManufactured()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = MedicinalProductManufactured()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = MedicinalProductManufactured()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = MedicinalProductManufactured()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = MedicinalProductManufactured()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = MedicinalProductManufactured()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = MedicinalProductManufactured()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_manufactured_dose_form(self):
        resource = MedicinalProductManufactured()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'manufacturedDoseForm', value)
        assert result is True
        assert resource.manufacturedDoseForm is not None

    def test_set_path_unit_of_presentation(self):
        resource = MedicinalProductManufactured()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'unitOfPresentation', value)
        assert result is True
        assert resource.unitOfPresentation is not None

    def test_set_path_quantity(self):
        resource = MedicinalProductManufactured()
        value = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'quantity', value)
        assert result is True
        assert resource.quantity is not None

    def test_set_path_manufacturer(self):
        resource = MedicinalProductManufactured()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'manufacturer', value)
        assert result is True
        assert resource.manufacturer is not None

    def test_set_path_ingredient(self):
        resource = MedicinalProductManufactured()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ingredient', value)
        assert result is True
        assert resource.ingredient is not None

    def test_set_path_physical_characteristics(self):
        resource = MedicinalProductManufactured()
        value = {'value': 'test'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'physicalCharacteristics', value)
        assert result is True
        assert resource.physicalCharacteristics is not None

    def test_set_path_other_characteristics(self):
        resource = MedicinalProductManufactured()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'otherCharacteristics', value)
        assert result is True
        assert resource.otherCharacteristics is not None


class TestParsePathMedicinalProductManufactured:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductManufactured.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductManufactured.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductManufactured.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
