# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import SubstanceReferenceInformation


class TestToDictSubstanceReferenceInformation:

    def test_to_dict_empty(self):
        resource = SubstanceReferenceInformation()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'SubstanceReferenceInformation'

    def test_to_dict_with_id(self):
        resource = SubstanceReferenceInformation()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = SubstanceReferenceInformation()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, SubstanceReferenceInformation)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = SubstanceReferenceInformation()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = SubstanceReferenceInformation()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = SubstanceReferenceInformation()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = SubstanceReferenceInformation()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = SubstanceReferenceInformation()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = SubstanceReferenceInformation()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = SubstanceReferenceInformation()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = SubstanceReferenceInformation()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_comment(self):
        resource = SubstanceReferenceInformation()
        resource.comment = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'comment' in result

    def test_to_dict_gene(self):
        resource = SubstanceReferenceInformation()
        resource.gene = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'gene' in result

    def test_to_dict_gene_element(self):
        resource = SubstanceReferenceInformation()
        resource.geneElement = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'geneElement' in result

    def test_to_dict_classification(self):
        resource = SubstanceReferenceInformation()
        resource.classification = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'classification' in result

    def test_to_dict_target(self):
        resource = SubstanceReferenceInformation()
        resource.target = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'target' in result


class TestFromDictSubstanceReferenceInformation:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'SubstanceReferenceInformation', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceReferenceInformation)
        assert isinstance(result, SubstanceReferenceInformation)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'SubstanceReferenceInformation'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceReferenceInformation)
        assert isinstance(result, SubstanceReferenceInformation)

    def test_from_dict_id(self):
        data = {'resourceType': 'SubstanceReferenceInformation', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceReferenceInformation)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'SubstanceReferenceInformation', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceReferenceInformation)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'SubstanceReferenceInformation', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceReferenceInformation)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'SubstanceReferenceInformation', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceReferenceInformation)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'SubstanceReferenceInformation', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceReferenceInformation)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'SubstanceReferenceInformation', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceReferenceInformation)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'SubstanceReferenceInformation', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceReferenceInformation)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'SubstanceReferenceInformation', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceReferenceInformation)
        assert result.modifierExtension is not None

    def test_from_dict_comment(self):
        data = {'resourceType': 'SubstanceReferenceInformation', 'comment': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceReferenceInformation)
        assert result.comment is not None

    def test_from_dict_gene(self):
        data = {'resourceType': 'SubstanceReferenceInformation', 'gene': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceReferenceInformation)
        assert result.gene is not None

    def test_from_dict_gene_element(self):
        data = {'resourceType': 'SubstanceReferenceInformation', 'geneElement': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceReferenceInformation)
        assert result.geneElement is not None

    def test_from_dict_classification(self):
        data = {'resourceType': 'SubstanceReferenceInformation', 'classification': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceReferenceInformation)
        assert result.classification is not None

    def test_from_dict_target(self):
        data = {'resourceType': 'SubstanceReferenceInformation', 'target': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceReferenceInformation)
        assert result.target is not None


class TestGetPathSubstanceReferenceInformation:

    def test_get_path_id(self):
        resource = SubstanceReferenceInformation()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = SubstanceReferenceInformation()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = SubstanceReferenceInformation()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'SubstanceReferenceInformation.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = SubstanceReferenceInformation()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = SubstanceReferenceInformation()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = SubstanceReferenceInformation()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = SubstanceReferenceInformation()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = SubstanceReferenceInformation()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = SubstanceReferenceInformation()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = SubstanceReferenceInformation()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_comment(self):
        resource = SubstanceReferenceInformation()
        resource.comment = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'comment')
        assert result is not None

    def test_get_path_gene(self):
        resource = SubstanceReferenceInformation()
        resource.gene = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'gene')
        assert result is not None

    def test_get_path_gene_element(self):
        resource = SubstanceReferenceInformation()
        resource.geneElement = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'geneElement')
        assert result is not None

    def test_get_path_classification(self):
        resource = SubstanceReferenceInformation()
        resource.classification = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'classification')
        assert result is not None

    def test_get_path_target(self):
        resource = SubstanceReferenceInformation()
        resource.target = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'target')
        assert result is not None


class TestSetPathSubstanceReferenceInformation:

    def test_set_path_id(self):
        resource = SubstanceReferenceInformation()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = SubstanceReferenceInformation()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'SubstanceReferenceInformation.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = SubstanceReferenceInformation()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = SubstanceReferenceInformation()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = SubstanceReferenceInformation()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = SubstanceReferenceInformation()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = SubstanceReferenceInformation()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = SubstanceReferenceInformation()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = SubstanceReferenceInformation()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_comment(self):
        resource = SubstanceReferenceInformation()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'comment', value)
        assert result is True
        assert resource.comment is not None

    def test_set_path_gene(self):
        resource = SubstanceReferenceInformation()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'gene', value)
        assert result is True
        assert resource.gene is not None

    def test_set_path_gene_element(self):
        resource = SubstanceReferenceInformation()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'geneElement', value)
        assert result is True
        assert resource.geneElement is not None

    def test_set_path_classification(self):
        resource = SubstanceReferenceInformation()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'classification', value)
        assert result is True
        assert resource.classification is not None

    def test_set_path_target(self):
        resource = SubstanceReferenceInformation()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'target', value)
        assert result is True
        assert resource.target is not None


class TestParsePathSubstanceReferenceInformation:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstanceReferenceInformation.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstanceReferenceInformation.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstanceReferenceInformation.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
