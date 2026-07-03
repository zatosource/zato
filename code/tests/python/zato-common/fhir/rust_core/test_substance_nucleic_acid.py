# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import SubstanceNucleicAcid


class TestToDictSubstanceNucleicAcid:

    def test_to_dict_empty(self):
        resource = SubstanceNucleicAcid()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'SubstanceNucleicAcid'

    def test_to_dict_with_id(self):
        resource = SubstanceNucleicAcid()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = SubstanceNucleicAcid()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, SubstanceNucleicAcid)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = SubstanceNucleicAcid()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = SubstanceNucleicAcid()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = SubstanceNucleicAcid()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = SubstanceNucleicAcid()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = SubstanceNucleicAcid()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = SubstanceNucleicAcid()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = SubstanceNucleicAcid()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = SubstanceNucleicAcid()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_sequence_type(self):
        resource = SubstanceNucleicAcid()
        resource.sequenceType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'sequenceType' in result

    def test_to_dict_number_of_subunits(self):
        resource = SubstanceNucleicAcid()
        resource.numberOfSubunits = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'numberOfSubunits' in result

    def test_to_dict_area_of_hybridisation(self):
        resource = SubstanceNucleicAcid()
        resource.areaOfHybridisation = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'areaOfHybridisation' in result

    def test_to_dict_oligo_nucleotide_type(self):
        resource = SubstanceNucleicAcid()
        resource.oligoNucleotideType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'oligoNucleotideType' in result

    def test_to_dict_subunit(self):
        resource = SubstanceNucleicAcid()
        resource.subunit = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subunit' in result


class TestFromDictSubstanceNucleicAcid:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'SubstanceNucleicAcid', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceNucleicAcid)
        assert isinstance(result, SubstanceNucleicAcid)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'SubstanceNucleicAcid'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceNucleicAcid)
        assert isinstance(result, SubstanceNucleicAcid)

    def test_from_dict_id(self):
        data = {'resourceType': 'SubstanceNucleicAcid', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceNucleicAcid)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'SubstanceNucleicAcid', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceNucleicAcid)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'SubstanceNucleicAcid', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceNucleicAcid)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'SubstanceNucleicAcid', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceNucleicAcid)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'SubstanceNucleicAcid', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceNucleicAcid)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'SubstanceNucleicAcid', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceNucleicAcid)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'SubstanceNucleicAcid', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceNucleicAcid)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'SubstanceNucleicAcid', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceNucleicAcid)
        assert result.modifierExtension is not None

    def test_from_dict_sequence_type(self):
        data = {'resourceType': 'SubstanceNucleicAcid',
         'sequenceType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceNucleicAcid)
        assert result.sequenceType is not None

    def test_from_dict_number_of_subunits(self):
        data = {'resourceType': 'SubstanceNucleicAcid', 'numberOfSubunits': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceNucleicAcid)
        assert result.numberOfSubunits is not None

    def test_from_dict_area_of_hybridisation(self):
        data = {'resourceType': 'SubstanceNucleicAcid', 'areaOfHybridisation': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceNucleicAcid)
        assert result.areaOfHybridisation is not None

    def test_from_dict_oligo_nucleotide_type(self):
        data = {'oligoNucleotideType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                 'text': 'Test concept'},
         'resourceType': 'SubstanceNucleicAcid'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceNucleicAcid)
        assert result.oligoNucleotideType is not None

    def test_from_dict_subunit(self):
        data = {'resourceType': 'SubstanceNucleicAcid', 'subunit': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceNucleicAcid)
        assert result.subunit is not None


class TestGetPathSubstanceNucleicAcid:

    def test_get_path_id(self):
        resource = SubstanceNucleicAcid()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = SubstanceNucleicAcid()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = SubstanceNucleicAcid()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'SubstanceNucleicAcid.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = SubstanceNucleicAcid()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = SubstanceNucleicAcid()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = SubstanceNucleicAcid()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = SubstanceNucleicAcid()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = SubstanceNucleicAcid()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = SubstanceNucleicAcid()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = SubstanceNucleicAcid()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_sequence_type(self):
        resource = SubstanceNucleicAcid()
        resource.sequenceType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'sequenceType')
        assert result is not None

    def test_get_path_number_of_subunits(self):
        resource = SubstanceNucleicAcid()
        resource.numberOfSubunits = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'numberOfSubunits')
        assert result is not None

    def test_get_path_area_of_hybridisation(self):
        resource = SubstanceNucleicAcid()
        resource.areaOfHybridisation = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'areaOfHybridisation')
        assert result is not None

    def test_get_path_oligo_nucleotide_type(self):
        resource = SubstanceNucleicAcid()
        resource.oligoNucleotideType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'oligoNucleotideType')
        assert result is not None

    def test_get_path_subunit(self):
        resource = SubstanceNucleicAcid()
        resource.subunit = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subunit')
        assert result is not None


class TestSetPathSubstanceNucleicAcid:

    def test_set_path_id(self):
        resource = SubstanceNucleicAcid()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = SubstanceNucleicAcid()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'SubstanceNucleicAcid.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = SubstanceNucleicAcid()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = SubstanceNucleicAcid()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = SubstanceNucleicAcid()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = SubstanceNucleicAcid()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = SubstanceNucleicAcid()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = SubstanceNucleicAcid()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = SubstanceNucleicAcid()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_sequence_type(self):
        resource = SubstanceNucleicAcid()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'sequenceType', value)
        assert result is True
        assert resource.sequenceType is not None

    def test_set_path_number_of_subunits(self):
        resource = SubstanceNucleicAcid()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'numberOfSubunits', value)
        assert result is True
        assert resource.numberOfSubunits is not None

    def test_set_path_area_of_hybridisation(self):
        resource = SubstanceNucleicAcid()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'areaOfHybridisation', value)
        assert result is True
        assert resource.areaOfHybridisation is not None

    def test_set_path_oligo_nucleotide_type(self):
        resource = SubstanceNucleicAcid()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'oligoNucleotideType', value)
        assert result is True
        assert resource.oligoNucleotideType is not None

    def test_set_path_subunit(self):
        resource = SubstanceNucleicAcid()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subunit', value)
        assert result is True
        assert resource.subunit is not None


class TestParsePathSubstanceNucleicAcid:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstanceNucleicAcid.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstanceNucleicAcid.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstanceNucleicAcid.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
