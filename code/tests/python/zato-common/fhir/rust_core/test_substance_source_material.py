# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import SubstanceSourceMaterial


class TestToDictSubstanceSourceMaterial:

    def test_to_dict_empty(self):
        resource = SubstanceSourceMaterial()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'SubstanceSourceMaterial'

    def test_to_dict_with_id(self):
        resource = SubstanceSourceMaterial()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = SubstanceSourceMaterial()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, SubstanceSourceMaterial)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = SubstanceSourceMaterial()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = SubstanceSourceMaterial()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = SubstanceSourceMaterial()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = SubstanceSourceMaterial()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = SubstanceSourceMaterial()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = SubstanceSourceMaterial()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = SubstanceSourceMaterial()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = SubstanceSourceMaterial()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_source_material_class(self):
        resource = SubstanceSourceMaterial()
        resource.sourceMaterialClass = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'sourceMaterialClass' in result

    def test_to_dict_source_material_type(self):
        resource = SubstanceSourceMaterial()
        resource.sourceMaterialType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'sourceMaterialType' in result

    def test_to_dict_source_material_state(self):
        resource = SubstanceSourceMaterial()
        resource.sourceMaterialState = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'sourceMaterialState' in result

    def test_to_dict_organism_id(self):
        resource = SubstanceSourceMaterial()
        resource.organismId = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'organismId' in result

    def test_to_dict_organism_name(self):
        resource = SubstanceSourceMaterial()
        resource.organismName = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'organismName' in result

    def test_to_dict_parent_substance_id(self):
        resource = SubstanceSourceMaterial()
        resource.parentSubstanceId = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'parentSubstanceId' in result

    def test_to_dict_parent_substance_name(self):
        resource = SubstanceSourceMaterial()
        resource.parentSubstanceName = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'parentSubstanceName' in result

    def test_to_dict_country_of_origin(self):
        resource = SubstanceSourceMaterial()
        resource.countryOfOrigin = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'countryOfOrigin' in result

    def test_to_dict_geographical_location(self):
        resource = SubstanceSourceMaterial()
        resource.geographicalLocation = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'geographicalLocation' in result

    def test_to_dict_development_stage(self):
        resource = SubstanceSourceMaterial()
        resource.developmentStage = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'developmentStage' in result

    def test_to_dict_fraction_description(self):
        resource = SubstanceSourceMaterial()
        resource.fractionDescription = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'fractionDescription' in result

    def test_to_dict_organism(self):
        resource = SubstanceSourceMaterial()
        resource.organism = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'organism' in result

    def test_to_dict_part_description(self):
        resource = SubstanceSourceMaterial()
        resource.partDescription = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'partDescription' in result


class TestFromDictSubstanceSourceMaterial:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert isinstance(result, SubstanceSourceMaterial)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'SubstanceSourceMaterial'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert isinstance(result, SubstanceSourceMaterial)

    def test_from_dict_id(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.modifierExtension is not None

    def test_from_dict_source_material_class(self):
        data = {'resourceType': 'SubstanceSourceMaterial',
         'sourceMaterialClass': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.sourceMaterialClass is not None

    def test_from_dict_source_material_type(self):
        data = {'resourceType': 'SubstanceSourceMaterial',
         'sourceMaterialType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.sourceMaterialType is not None

    def test_from_dict_source_material_state(self):
        data = {'resourceType': 'SubstanceSourceMaterial',
         'sourceMaterialState': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.sourceMaterialState is not None

    def test_from_dict_organism_id(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'organismId': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.organismId is not None

    def test_from_dict_organism_name(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'organismName': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.organismName is not None

    def test_from_dict_parent_substance_id(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'parentSubstanceId': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.parentSubstanceId is not None

    def test_from_dict_parent_substance_name(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'parentSubstanceName': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.parentSubstanceName is not None

    def test_from_dict_country_of_origin(self):
        data = {'countryOfOrigin': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                              'text': 'Test concept'}],
         'resourceType': 'SubstanceSourceMaterial'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.countryOfOrigin is not None

    def test_from_dict_geographical_location(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'geographicalLocation': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.geographicalLocation is not None

    def test_from_dict_development_stage(self):
        data = {'developmentStage': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                              'text': 'Test concept'},
         'resourceType': 'SubstanceSourceMaterial'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.developmentStage is not None

    def test_from_dict_fraction_description(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'fractionDescription': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.fractionDescription is not None

    def test_from_dict_organism(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'organism': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.organism is not None

    def test_from_dict_part_description(self):
        data = {'resourceType': 'SubstanceSourceMaterial', 'partDescription': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSourceMaterial)
        assert result.partDescription is not None


class TestGetPathSubstanceSourceMaterial:

    def test_get_path_id(self):
        resource = SubstanceSourceMaterial()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = SubstanceSourceMaterial()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = SubstanceSourceMaterial()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'SubstanceSourceMaterial.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = SubstanceSourceMaterial()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = SubstanceSourceMaterial()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = SubstanceSourceMaterial()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = SubstanceSourceMaterial()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = SubstanceSourceMaterial()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = SubstanceSourceMaterial()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = SubstanceSourceMaterial()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_source_material_class(self):
        resource = SubstanceSourceMaterial()
        resource.sourceMaterialClass = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'sourceMaterialClass')
        assert result is not None

    def test_get_path_source_material_type(self):
        resource = SubstanceSourceMaterial()
        resource.sourceMaterialType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'sourceMaterialType')
        assert result is not None

    def test_get_path_source_material_state(self):
        resource = SubstanceSourceMaterial()
        resource.sourceMaterialState = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'sourceMaterialState')
        assert result is not None

    def test_get_path_organism_id(self):
        resource = SubstanceSourceMaterial()
        resource.organismId = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'organismId')
        assert result is not None

    def test_get_path_organism_name(self):
        resource = SubstanceSourceMaterial()
        resource.organismName = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'organismName')
        assert result is not None

    def test_get_path_parent_substance_id(self):
        resource = SubstanceSourceMaterial()
        resource.parentSubstanceId = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'parentSubstanceId')
        assert result is not None

    def test_get_path_parent_substance_name(self):
        resource = SubstanceSourceMaterial()
        resource.parentSubstanceName = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'parentSubstanceName')
        assert result is not None

    def test_get_path_country_of_origin(self):
        resource = SubstanceSourceMaterial()
        resource.countryOfOrigin = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'countryOfOrigin')
        assert result is not None

    def test_get_path_geographical_location(self):
        resource = SubstanceSourceMaterial()
        resource.geographicalLocation = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'geographicalLocation')
        assert result is not None

    def test_get_path_development_stage(self):
        resource = SubstanceSourceMaterial()
        resource.developmentStage = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'developmentStage')
        assert result is not None

    def test_get_path_fraction_description(self):
        resource = SubstanceSourceMaterial()
        resource.fractionDescription = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'fractionDescription')
        assert result is not None

    def test_get_path_organism(self):
        resource = SubstanceSourceMaterial()
        resource.organism = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'organism')
        assert result is not None

    def test_get_path_part_description(self):
        resource = SubstanceSourceMaterial()
        resource.partDescription = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'partDescription')
        assert result is not None


class TestSetPathSubstanceSourceMaterial:

    def test_set_path_id(self):
        resource = SubstanceSourceMaterial()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = SubstanceSourceMaterial()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'SubstanceSourceMaterial.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = SubstanceSourceMaterial()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = SubstanceSourceMaterial()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = SubstanceSourceMaterial()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = SubstanceSourceMaterial()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = SubstanceSourceMaterial()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = SubstanceSourceMaterial()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = SubstanceSourceMaterial()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_source_material_class(self):
        resource = SubstanceSourceMaterial()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'sourceMaterialClass', value)
        assert result is True
        assert resource.sourceMaterialClass is not None

    def test_set_path_source_material_type(self):
        resource = SubstanceSourceMaterial()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'sourceMaterialType', value)
        assert result is True
        assert resource.sourceMaterialType is not None

    def test_set_path_source_material_state(self):
        resource = SubstanceSourceMaterial()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'sourceMaterialState', value)
        assert result is True
        assert resource.sourceMaterialState is not None

    def test_set_path_organism_id(self):
        resource = SubstanceSourceMaterial()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'organismId', value)
        assert result is True
        assert resource.organismId is not None

    def test_set_path_organism_name(self):
        resource = SubstanceSourceMaterial()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'organismName', value)
        assert result is True
        assert resource.organismName is not None

    def test_set_path_parent_substance_id(self):
        resource = SubstanceSourceMaterial()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'parentSubstanceId', value)
        assert result is True
        assert resource.parentSubstanceId is not None

    def test_set_path_parent_substance_name(self):
        resource = SubstanceSourceMaterial()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'parentSubstanceName', value)
        assert result is True
        assert resource.parentSubstanceName is not None

    def test_set_path_country_of_origin(self):
        resource = SubstanceSourceMaterial()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'countryOfOrigin', value)
        assert result is True
        assert resource.countryOfOrigin is not None

    def test_set_path_geographical_location(self):
        resource = SubstanceSourceMaterial()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'geographicalLocation', value)
        assert result is True
        assert resource.geographicalLocation is not None

    def test_set_path_development_stage(self):
        resource = SubstanceSourceMaterial()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'developmentStage', value)
        assert result is True
        assert resource.developmentStage is not None

    def test_set_path_fraction_description(self):
        resource = SubstanceSourceMaterial()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'fractionDescription', value)
        assert result is True
        assert resource.fractionDescription is not None

    def test_set_path_organism(self):
        resource = SubstanceSourceMaterial()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'organism', value)
        assert result is True
        assert resource.organism is not None

    def test_set_path_part_description(self):
        resource = SubstanceSourceMaterial()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'partDescription', value)
        assert result is True
        assert resource.partDescription is not None


class TestParsePathSubstanceSourceMaterial:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstanceSourceMaterial.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstanceSourceMaterial.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstanceSourceMaterial.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
