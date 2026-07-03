# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import MedicinalProductPharmaceutical


class TestToDictMedicinalProductPharmaceutical:

    def test_to_dict_empty(self):
        resource = MedicinalProductPharmaceutical()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'MedicinalProductPharmaceutical'

    def test_to_dict_with_id(self):
        resource = MedicinalProductPharmaceutical()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = MedicinalProductPharmaceutical()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, MedicinalProductPharmaceutical)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = MedicinalProductPharmaceutical()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = MedicinalProductPharmaceutical()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = MedicinalProductPharmaceutical()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = MedicinalProductPharmaceutical()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = MedicinalProductPharmaceutical()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = MedicinalProductPharmaceutical()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = MedicinalProductPharmaceutical()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = MedicinalProductPharmaceutical()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = MedicinalProductPharmaceutical()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_administrable_dose_form(self):
        resource = MedicinalProductPharmaceutical()
        resource.administrableDoseForm = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'administrableDoseForm' in result

    def test_to_dict_unit_of_presentation(self):
        resource = MedicinalProductPharmaceutical()
        resource.unitOfPresentation = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'unitOfPresentation' in result

    def test_to_dict_ingredient(self):
        resource = MedicinalProductPharmaceutical()
        resource.ingredient = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'ingredient' in result

    def test_to_dict_device(self):
        resource = MedicinalProductPharmaceutical()
        resource.device = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'device' in result

    def test_to_dict_characteristics(self):
        resource = MedicinalProductPharmaceutical()
        resource.characteristics = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'characteristics' in result

    def test_to_dict_route_of_administration(self):
        resource = MedicinalProductPharmaceutical()
        resource.routeOfAdministration = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'routeOfAdministration' in result


class TestFromDictMedicinalProductPharmaceutical:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert isinstance(result, MedicinalProductPharmaceutical)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert isinstance(result, MedicinalProductPharmaceutical)

    def test_from_dict_id(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical',
         'text': {'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>', 'status': 'generated'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert result.identifier is not None

    def test_from_dict_administrable_dose_form(self):
        data = {'administrableDoseForm': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                   'text': 'Test concept'},
         'resourceType': 'MedicinalProductPharmaceutical'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert result.administrableDoseForm is not None

    def test_from_dict_unit_of_presentation(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical',
         'unitOfPresentation': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert result.unitOfPresentation is not None

    def test_from_dict_ingredient(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical', 'ingredient': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert result.ingredient is not None

    def test_from_dict_device(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical', 'device': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert result.device is not None

    def test_from_dict_characteristics(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical', 'characteristics': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert result.characteristics is not None

    def test_from_dict_route_of_administration(self):
        data = {'resourceType': 'MedicinalProductPharmaceutical', 'routeOfAdministration': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProductPharmaceutical)
        assert result.routeOfAdministration is not None


class TestGetPathMedicinalProductPharmaceutical:

    def test_get_path_id(self):
        resource = MedicinalProductPharmaceutical()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = MedicinalProductPharmaceutical()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = MedicinalProductPharmaceutical()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'MedicinalProductPharmaceutical.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = MedicinalProductPharmaceutical()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = MedicinalProductPharmaceutical()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = MedicinalProductPharmaceutical()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = MedicinalProductPharmaceutical()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = MedicinalProductPharmaceutical()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = MedicinalProductPharmaceutical()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = MedicinalProductPharmaceutical()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = MedicinalProductPharmaceutical()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_administrable_dose_form(self):
        resource = MedicinalProductPharmaceutical()
        resource.administrableDoseForm = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'administrableDoseForm')
        assert result is not None

    def test_get_path_unit_of_presentation(self):
        resource = MedicinalProductPharmaceutical()
        resource.unitOfPresentation = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'unitOfPresentation')
        assert result is not None

    def test_get_path_ingredient(self):
        resource = MedicinalProductPharmaceutical()
        resource.ingredient = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ingredient')
        assert result is not None

    def test_get_path_device(self):
        resource = MedicinalProductPharmaceutical()
        resource.device = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'device')
        assert result is not None

    def test_get_path_characteristics(self):
        resource = MedicinalProductPharmaceutical()
        resource.characteristics = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'characteristics')
        assert result is not None

    def test_get_path_route_of_administration(self):
        resource = MedicinalProductPharmaceutical()
        resource.routeOfAdministration = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'routeOfAdministration')
        assert result is not None


class TestSetPathMedicinalProductPharmaceutical:

    def test_set_path_id(self):
        resource = MedicinalProductPharmaceutical()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = MedicinalProductPharmaceutical()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'MedicinalProductPharmaceutical.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = MedicinalProductPharmaceutical()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = MedicinalProductPharmaceutical()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = MedicinalProductPharmaceutical()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = MedicinalProductPharmaceutical()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = MedicinalProductPharmaceutical()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = MedicinalProductPharmaceutical()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = MedicinalProductPharmaceutical()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = MedicinalProductPharmaceutical()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_administrable_dose_form(self):
        resource = MedicinalProductPharmaceutical()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'administrableDoseForm', value)
        assert result is True
        assert resource.administrableDoseForm is not None

    def test_set_path_unit_of_presentation(self):
        resource = MedicinalProductPharmaceutical()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'unitOfPresentation', value)
        assert result is True
        assert resource.unitOfPresentation is not None

    def test_set_path_ingredient(self):
        resource = MedicinalProductPharmaceutical()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ingredient', value)
        assert result is True
        assert resource.ingredient is not None

    def test_set_path_device(self):
        resource = MedicinalProductPharmaceutical()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'device', value)
        assert result is True
        assert resource.device is not None

    def test_set_path_characteristics(self):
        resource = MedicinalProductPharmaceutical()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'characteristics', value)
        assert result is True
        assert resource.characteristics is not None

    def test_set_path_route_of_administration(self):
        resource = MedicinalProductPharmaceutical()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'routeOfAdministration', value)
        assert result is True
        assert resource.routeOfAdministration is not None


class TestParsePathMedicinalProductPharmaceutical:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductPharmaceutical.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductPharmaceutical.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProductPharmaceutical.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
