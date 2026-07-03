# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import SubstanceProtein


class TestToDictSubstanceProtein:

    def test_to_dict_empty(self):
        resource = SubstanceProtein()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'SubstanceProtein'

    def test_to_dict_with_id(self):
        resource = SubstanceProtein()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = SubstanceProtein()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, SubstanceProtein)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = SubstanceProtein()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = SubstanceProtein()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = SubstanceProtein()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = SubstanceProtein()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = SubstanceProtein()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = SubstanceProtein()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = SubstanceProtein()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = SubstanceProtein()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_sequence_type(self):
        resource = SubstanceProtein()
        resource.sequenceType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'sequenceType' in result

    def test_to_dict_number_of_subunits(self):
        resource = SubstanceProtein()
        resource.numberOfSubunits = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'numberOfSubunits' in result

    def test_to_dict_disulfide_linkage(self):
        resource = SubstanceProtein()
        resource.disulfideLinkage = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'disulfideLinkage' in result

    def test_to_dict_subunit(self):
        resource = SubstanceProtein()
        resource.subunit = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subunit' in result


class TestFromDictSubstanceProtein:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'SubstanceProtein', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceProtein)
        assert isinstance(result, SubstanceProtein)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'SubstanceProtein'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceProtein)
        assert isinstance(result, SubstanceProtein)

    def test_from_dict_id(self):
        data = {'resourceType': 'SubstanceProtein', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceProtein)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'SubstanceProtein', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceProtein)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'SubstanceProtein', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceProtein)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'SubstanceProtein', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceProtein)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'SubstanceProtein', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceProtein)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'SubstanceProtein', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceProtein)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'SubstanceProtein', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceProtein)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'SubstanceProtein', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceProtein)
        assert result.modifierExtension is not None

    def test_from_dict_sequence_type(self):
        data = {'resourceType': 'SubstanceProtein',
         'sequenceType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceProtein)
        assert result.sequenceType is not None

    def test_from_dict_number_of_subunits(self):
        data = {'resourceType': 'SubstanceProtein', 'numberOfSubunits': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceProtein)
        assert result.numberOfSubunits is not None

    def test_from_dict_disulfide_linkage(self):
        data = {'resourceType': 'SubstanceProtein', 'disulfideLinkage': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceProtein)
        assert result.disulfideLinkage is not None

    def test_from_dict_subunit(self):
        data = {'resourceType': 'SubstanceProtein', 'subunit': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceProtein)
        assert result.subunit is not None


class TestGetPathSubstanceProtein:

    def test_get_path_id(self):
        resource = SubstanceProtein()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = SubstanceProtein()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = SubstanceProtein()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'SubstanceProtein.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = SubstanceProtein()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = SubstanceProtein()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = SubstanceProtein()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = SubstanceProtein()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = SubstanceProtein()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = SubstanceProtein()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = SubstanceProtein()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_sequence_type(self):
        resource = SubstanceProtein()
        resource.sequenceType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'sequenceType')
        assert result is not None

    def test_get_path_number_of_subunits(self):
        resource = SubstanceProtein()
        resource.numberOfSubunits = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'numberOfSubunits')
        assert result is not None

    def test_get_path_disulfide_linkage(self):
        resource = SubstanceProtein()
        resource.disulfideLinkage = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'disulfideLinkage')
        assert result is not None

    def test_get_path_subunit(self):
        resource = SubstanceProtein()
        resource.subunit = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subunit')
        assert result is not None


class TestSetPathSubstanceProtein:

    def test_set_path_id(self):
        resource = SubstanceProtein()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = SubstanceProtein()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'SubstanceProtein.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = SubstanceProtein()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = SubstanceProtein()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = SubstanceProtein()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = SubstanceProtein()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = SubstanceProtein()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = SubstanceProtein()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = SubstanceProtein()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_sequence_type(self):
        resource = SubstanceProtein()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'sequenceType', value)
        assert result is True
        assert resource.sequenceType is not None

    def test_set_path_number_of_subunits(self):
        resource = SubstanceProtein()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'numberOfSubunits', value)
        assert result is True
        assert resource.numberOfSubunits is not None

    def test_set_path_disulfide_linkage(self):
        resource = SubstanceProtein()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'disulfideLinkage', value)
        assert result is True
        assert resource.disulfideLinkage is not None

    def test_set_path_subunit(self):
        resource = SubstanceProtein()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subunit', value)
        assert result is True
        assert resource.subunit is not None


class TestParsePathSubstanceProtein:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstanceProtein.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstanceProtein.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstanceProtein.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
