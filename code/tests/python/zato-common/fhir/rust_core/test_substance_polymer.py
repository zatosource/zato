# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import SubstancePolymer


class TestToDictSubstancePolymer:

    def test_to_dict_empty(self):
        resource = SubstancePolymer()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'SubstancePolymer'

    def test_to_dict_with_id(self):
        resource = SubstancePolymer()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = SubstancePolymer()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, SubstancePolymer)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = SubstancePolymer()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = SubstancePolymer()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = SubstancePolymer()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = SubstancePolymer()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = SubstancePolymer()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = SubstancePolymer()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = SubstancePolymer()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = SubstancePolymer()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_class(self):
        resource = SubstancePolymer()
        resource.class_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'class' in result

    def test_to_dict_geometry(self):
        resource = SubstancePolymer()
        resource.geometry = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'geometry' in result

    def test_to_dict_copolymer_connectivity(self):
        resource = SubstancePolymer()
        resource.copolymerConnectivity = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copolymerConnectivity' in result

    def test_to_dict_modification(self):
        resource = SubstancePolymer()
        resource.modification = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modification' in result

    def test_to_dict_monomer_set(self):
        resource = SubstancePolymer()
        resource.monomerSet = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'monomerSet' in result

    def test_to_dict_repeat(self):
        resource = SubstancePolymer()
        resource.repeat = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'repeat' in result


class TestFromDictSubstancePolymer:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'SubstancePolymer', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert isinstance(result, SubstancePolymer)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'SubstancePolymer'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert isinstance(result, SubstancePolymer)

    def test_from_dict_id(self):
        data = {'resourceType': 'SubstancePolymer', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'SubstancePolymer', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'SubstancePolymer', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'SubstancePolymer', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'SubstancePolymer', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'SubstancePolymer', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'SubstancePolymer', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'SubstancePolymer', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert result.modifierExtension is not None

    def test_from_dict_class(self):
        data = {'class': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                   'text': 'Test concept'},
         'resourceType': 'SubstancePolymer'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert result.class_ is not None

    def test_from_dict_geometry(self):
        data = {'geometry': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'SubstancePolymer'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert result.geometry is not None

    def test_from_dict_copolymer_connectivity(self):
        data = {'copolymerConnectivity': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                    'text': 'Test concept'}],
         'resourceType': 'SubstancePolymer'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert result.copolymerConnectivity is not None

    def test_from_dict_modification(self):
        data = {'resourceType': 'SubstancePolymer', 'modification': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert result.modification is not None

    def test_from_dict_monomer_set(self):
        data = {'resourceType': 'SubstancePolymer', 'monomerSet': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert result.monomerSet is not None

    def test_from_dict_repeat(self):
        data = {'resourceType': 'SubstancePolymer', 'repeat': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstancePolymer)
        assert result.repeat is not None


class TestGetPathSubstancePolymer:

    def test_get_path_id(self):
        resource = SubstancePolymer()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = SubstancePolymer()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = SubstancePolymer()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'SubstancePolymer.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = SubstancePolymer()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = SubstancePolymer()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = SubstancePolymer()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = SubstancePolymer()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = SubstancePolymer()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = SubstancePolymer()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = SubstancePolymer()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_class(self):
        resource = SubstancePolymer()
        resource.class_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'class')
        assert result is not None

    def test_get_path_geometry(self):
        resource = SubstancePolymer()
        resource.geometry = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'geometry')
        assert result is not None

    def test_get_path_copolymer_connectivity(self):
        resource = SubstancePolymer()
        resource.copolymerConnectivity = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copolymerConnectivity')
        assert result is not None

    def test_get_path_modification(self):
        resource = SubstancePolymer()
        resource.modification = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modification')
        assert result is not None

    def test_get_path_monomer_set(self):
        resource = SubstancePolymer()
        resource.monomerSet = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'monomerSet')
        assert result is not None

    def test_get_path_repeat(self):
        resource = SubstancePolymer()
        resource.repeat = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'repeat')
        assert result is not None


class TestSetPathSubstancePolymer:

    def test_set_path_id(self):
        resource = SubstancePolymer()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = SubstancePolymer()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'SubstancePolymer.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = SubstancePolymer()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = SubstancePolymer()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = SubstancePolymer()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = SubstancePolymer()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = SubstancePolymer()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = SubstancePolymer()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = SubstancePolymer()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_class(self):
        resource = SubstancePolymer()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'class', value)
        assert result is True
        assert resource.class_ is not None

    def test_set_path_geometry(self):
        resource = SubstancePolymer()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'geometry', value)
        assert result is True
        assert resource.geometry is not None

    def test_set_path_copolymer_connectivity(self):
        resource = SubstancePolymer()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copolymerConnectivity', value)
        assert result is True
        assert resource.copolymerConnectivity is not None

    def test_set_path_modification(self):
        resource = SubstancePolymer()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modification', value)
        assert result is True
        assert resource.modification is not None

    def test_set_path_monomer_set(self):
        resource = SubstancePolymer()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'monomerSet', value)
        assert result is True
        assert resource.monomerSet is not None

    def test_set_path_repeat(self):
        resource = SubstancePolymer()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'repeat', value)
        assert result is True
        assert resource.repeat is not None


class TestParsePathSubstancePolymer:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstancePolymer.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstancePolymer.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstancePolymer.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
