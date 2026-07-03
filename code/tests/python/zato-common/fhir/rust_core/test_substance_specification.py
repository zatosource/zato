# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import SubstanceSpecification


class TestToDictSubstanceSpecification:

    def test_to_dict_empty(self):
        resource = SubstanceSpecification()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'SubstanceSpecification'

    def test_to_dict_with_id(self):
        resource = SubstanceSpecification()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = SubstanceSpecification()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, SubstanceSpecification)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = SubstanceSpecification()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = SubstanceSpecification()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = SubstanceSpecification()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = SubstanceSpecification()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = SubstanceSpecification()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = SubstanceSpecification()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = SubstanceSpecification()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = SubstanceSpecification()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = SubstanceSpecification()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_type(self):
        resource = SubstanceSpecification()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_status(self):
        resource = SubstanceSpecification()
        resource.status = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_domain(self):
        resource = SubstanceSpecification()
        resource.domain = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'domain' in result

    def test_to_dict_description(self):
        resource = SubstanceSpecification()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_source(self):
        resource = SubstanceSpecification()
        resource.source = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'source' in result

    def test_to_dict_comment(self):
        resource = SubstanceSpecification()
        resource.comment = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'comment' in result

    def test_to_dict_moiety(self):
        resource = SubstanceSpecification()
        resource.moiety = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'moiety' in result

    def test_to_dict_property(self):
        resource = SubstanceSpecification()
        resource.property = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'property' in result

    def test_to_dict_reference_information(self):
        resource = SubstanceSpecification()
        resource.referenceInformation = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'referenceInformation' in result

    def test_to_dict_structure(self):
        resource = SubstanceSpecification()
        resource.structure = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'structure' in result

    def test_to_dict_code(self):
        resource = SubstanceSpecification()
        resource.code = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_name(self):
        resource = SubstanceSpecification()
        resource.name = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_molecular_weight(self):
        resource = SubstanceSpecification()
        resource.molecularWeight = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'molecularWeight' in result

    def test_to_dict_relationship(self):
        resource = SubstanceSpecification()
        resource.relationship = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relationship' in result

    def test_to_dict_nucleic_acid(self):
        resource = SubstanceSpecification()
        resource.nucleicAcid = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'nucleicAcid' in result

    def test_to_dict_polymer(self):
        resource = SubstanceSpecification()
        resource.polymer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'polymer' in result

    def test_to_dict_protein(self):
        resource = SubstanceSpecification()
        resource.protein = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'protein' in result

    def test_to_dict_source_material(self):
        resource = SubstanceSpecification()
        resource.sourceMaterial = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'sourceMaterial' in result


class TestFromDictSubstanceSpecification:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'SubstanceSpecification', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert isinstance(result, SubstanceSpecification)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'SubstanceSpecification'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert isinstance(result, SubstanceSpecification)

    def test_from_dict_id(self):
        data = {'resourceType': 'SubstanceSpecification', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'SubstanceSpecification', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'SubstanceSpecification', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'SubstanceSpecification', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'SubstanceSpecification', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'SubstanceSpecification', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'SubstanceSpecification', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'SubstanceSpecification', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'SubstanceSpecification', 'identifier': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.identifier is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'SubstanceSpecification',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.type_ is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'SubstanceSpecification',
         'status': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.status is not None

    def test_from_dict_domain(self):
        data = {'domain': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'},
         'resourceType': 'SubstanceSpecification'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.domain is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'SubstanceSpecification', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.description is not None

    def test_from_dict_source(self):
        data = {'resourceType': 'SubstanceSpecification', 'source': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.source is not None

    def test_from_dict_comment(self):
        data = {'resourceType': 'SubstanceSpecification', 'comment': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.comment is not None

    def test_from_dict_moiety(self):
        data = {'resourceType': 'SubstanceSpecification', 'moiety': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.moiety is not None

    def test_from_dict_property(self):
        data = {'resourceType': 'SubstanceSpecification', 'property': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.property is not None

    def test_from_dict_reference_information(self):
        data = {'resourceType': 'SubstanceSpecification', 'referenceInformation': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.referenceInformation is not None

    def test_from_dict_structure(self):
        data = {'resourceType': 'SubstanceSpecification', 'structure': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.structure is not None

    def test_from_dict_code(self):
        data = {'resourceType': 'SubstanceSpecification', 'code': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.code is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'SubstanceSpecification', 'name': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.name is not None

    def test_from_dict_molecular_weight(self):
        data = {'resourceType': 'SubstanceSpecification', 'molecularWeight': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.molecularWeight is not None

    def test_from_dict_relationship(self):
        data = {'resourceType': 'SubstanceSpecification', 'relationship': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.relationship is not None

    def test_from_dict_nucleic_acid(self):
        data = {'resourceType': 'SubstanceSpecification', 'nucleicAcid': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.nucleicAcid is not None

    def test_from_dict_polymer(self):
        data = {'resourceType': 'SubstanceSpecification', 'polymer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.polymer is not None

    def test_from_dict_protein(self):
        data = {'resourceType': 'SubstanceSpecification', 'protein': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.protein is not None

    def test_from_dict_source_material(self):
        data = {'resourceType': 'SubstanceSpecification', 'sourceMaterial': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SubstanceSpecification)
        assert result.sourceMaterial is not None


class TestGetPathSubstanceSpecification:

    def test_get_path_id(self):
        resource = SubstanceSpecification()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = SubstanceSpecification()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = SubstanceSpecification()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'SubstanceSpecification.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = SubstanceSpecification()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = SubstanceSpecification()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = SubstanceSpecification()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = SubstanceSpecification()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = SubstanceSpecification()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = SubstanceSpecification()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = SubstanceSpecification()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = SubstanceSpecification()
        resource.identifier = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_type(self):
        resource = SubstanceSpecification()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_status(self):
        resource = SubstanceSpecification()
        resource.status = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_domain(self):
        resource = SubstanceSpecification()
        resource.domain = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'domain')
        assert result is not None

    def test_get_path_description(self):
        resource = SubstanceSpecification()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_source(self):
        resource = SubstanceSpecification()
        resource.source = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'source')
        assert result is not None

    def test_get_path_comment(self):
        resource = SubstanceSpecification()
        resource.comment = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'comment')
        assert result is not None

    def test_get_path_moiety(self):
        resource = SubstanceSpecification()
        resource.moiety = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'moiety')
        assert result is not None

    def test_get_path_property(self):
        resource = SubstanceSpecification()
        resource.property = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'property')
        assert result is not None

    def test_get_path_reference_information(self):
        resource = SubstanceSpecification()
        resource.referenceInformation = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'referenceInformation')
        assert result is not None

    def test_get_path_structure(self):
        resource = SubstanceSpecification()
        resource.structure = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'structure')
        assert result is not None

    def test_get_path_code(self):
        resource = SubstanceSpecification()
        resource.code = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_name(self):
        resource = SubstanceSpecification()
        resource.name = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_molecular_weight(self):
        resource = SubstanceSpecification()
        resource.molecularWeight = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'molecularWeight')
        assert result is not None

    def test_get_path_relationship(self):
        resource = SubstanceSpecification()
        resource.relationship = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relationship')
        assert result is not None

    def test_get_path_nucleic_acid(self):
        resource = SubstanceSpecification()
        resource.nucleicAcid = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nucleicAcid')
        assert result is not None

    def test_get_path_polymer(self):
        resource = SubstanceSpecification()
        resource.polymer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'polymer')
        assert result is not None

    def test_get_path_protein(self):
        resource = SubstanceSpecification()
        resource.protein = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'protein')
        assert result is not None

    def test_get_path_source_material(self):
        resource = SubstanceSpecification()
        resource.sourceMaterial = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'sourceMaterial')
        assert result is not None


class TestSetPathSubstanceSpecification:

    def test_set_path_id(self):
        resource = SubstanceSpecification()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = SubstanceSpecification()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'SubstanceSpecification.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = SubstanceSpecification()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = SubstanceSpecification()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = SubstanceSpecification()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = SubstanceSpecification()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = SubstanceSpecification()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = SubstanceSpecification()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = SubstanceSpecification()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = SubstanceSpecification()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_type(self):
        resource = SubstanceSpecification()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_status(self):
        resource = SubstanceSpecification()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_domain(self):
        resource = SubstanceSpecification()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'domain', value)
        assert result is True
        assert resource.domain is not None

    def test_set_path_description(self):
        resource = SubstanceSpecification()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_source(self):
        resource = SubstanceSpecification()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'source', value)
        assert result is True
        assert resource.source is not None

    def test_set_path_comment(self):
        resource = SubstanceSpecification()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'comment', value)
        assert result is True
        assert resource.comment is not None

    def test_set_path_moiety(self):
        resource = SubstanceSpecification()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'moiety', value)
        assert result is True
        assert resource.moiety is not None

    def test_set_path_property(self):
        resource = SubstanceSpecification()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'property', value)
        assert result is True
        assert resource.property is not None

    def test_set_path_reference_information(self):
        resource = SubstanceSpecification()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'referenceInformation', value)
        assert result is True
        assert resource.referenceInformation is not None

    def test_set_path_structure(self):
        resource = SubstanceSpecification()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'structure', value)
        assert result is True
        assert resource.structure is not None

    def test_set_path_code(self):
        resource = SubstanceSpecification()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_name(self):
        resource = SubstanceSpecification()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_molecular_weight(self):
        resource = SubstanceSpecification()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'molecularWeight', value)
        assert result is True
        assert resource.molecularWeight is not None

    def test_set_path_relationship(self):
        resource = SubstanceSpecification()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relationship', value)
        assert result is True
        assert resource.relationship is not None

    def test_set_path_nucleic_acid(self):
        resource = SubstanceSpecification()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'nucleicAcid', value)
        assert result is True
        assert resource.nucleicAcid is not None

    def test_set_path_polymer(self):
        resource = SubstanceSpecification()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'polymer', value)
        assert result is True
        assert resource.polymer is not None

    def test_set_path_protein(self):
        resource = SubstanceSpecification()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'protein', value)
        assert result is True
        assert resource.protein is not None

    def test_set_path_source_material(self):
        resource = SubstanceSpecification()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'sourceMaterial', value)
        assert result is True
        assert resource.sourceMaterial is not None


class TestParsePathSubstanceSpecification:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstanceSpecification.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstanceSpecification.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('SubstanceSpecification.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
