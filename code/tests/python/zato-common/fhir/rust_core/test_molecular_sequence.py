# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import MolecularSequence


class TestToDictMolecularSequence:

    def test_to_dict_empty(self):
        resource = MolecularSequence()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'MolecularSequence'

    def test_to_dict_with_id(self):
        resource = MolecularSequence()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = MolecularSequence()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, MolecularSequence)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = MolecularSequence()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = MolecularSequence()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = MolecularSequence()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = MolecularSequence()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = MolecularSequence()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = MolecularSequence()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = MolecularSequence()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = MolecularSequence()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = MolecularSequence()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_type(self):
        resource = MolecularSequence()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_coordinate_system(self):
        resource = MolecularSequence()
        resource.coordinateSystem = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'coordinateSystem' in result

    def test_to_dict_patient(self):
        resource = MolecularSequence()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_specimen(self):
        resource = MolecularSequence()
        resource.specimen = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'specimen' in result

    def test_to_dict_device(self):
        resource = MolecularSequence()
        resource.device = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'device' in result

    def test_to_dict_performer(self):
        resource = MolecularSequence()
        resource.performer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performer' in result

    def test_to_dict_quantity(self):
        resource = MolecularSequence()
        resource.quantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'quantity' in result

    def test_to_dict_reference_seq(self):
        resource = MolecularSequence()
        resource.referenceSeq = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'referenceSeq' in result

    def test_to_dict_variant(self):
        resource = MolecularSequence()
        resource.variant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'variant' in result

    def test_to_dict_observed_seq(self):
        resource = MolecularSequence()
        resource.observedSeq = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'observedSeq' in result

    def test_to_dict_quality(self):
        resource = MolecularSequence()
        resource.quality = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'quality' in result

    def test_to_dict_read_coverage(self):
        resource = MolecularSequence()
        resource.readCoverage = 42
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'readCoverage' in result

    def test_to_dict_repository(self):
        resource = MolecularSequence()
        resource.repository = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'repository' in result

    def test_to_dict_pointer(self):
        resource = MolecularSequence()
        resource.pointer = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'pointer' in result

    def test_to_dict_structure_variant(self):
        resource = MolecularSequence()
        resource.structureVariant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'structureVariant' in result


class TestFromDictMolecularSequence:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'MolecularSequence', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert isinstance(result, MolecularSequence)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'MolecularSequence'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert isinstance(result, MolecularSequence)

    def test_from_dict_id(self):
        data = {'resourceType': 'MolecularSequence', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'MolecularSequence', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'MolecularSequence', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'MolecularSequence', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'MolecularSequence', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'MolecularSequence', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'MolecularSequence', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'MolecularSequence', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'MolecularSequence', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.identifier is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'MolecularSequence', 'type': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.type_ is not None

    def test_from_dict_coordinate_system(self):
        data = {'resourceType': 'MolecularSequence', 'coordinateSystem': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.coordinateSystem is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'MolecularSequence', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.patient is not None

    def test_from_dict_specimen(self):
        data = {'resourceType': 'MolecularSequence', 'specimen': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.specimen is not None

    def test_from_dict_device(self):
        data = {'resourceType': 'MolecularSequence', 'device': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.device is not None

    def test_from_dict_performer(self):
        data = {'resourceType': 'MolecularSequence', 'performer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.performer is not None

    def test_from_dict_quantity(self):
        data = {'resourceType': 'MolecularSequence', 'quantity': {'value': 100, 'unit': 'mg'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.quantity is not None

    def test_from_dict_reference_seq(self):
        data = {'resourceType': 'MolecularSequence', 'referenceSeq': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.referenceSeq is not None

    def test_from_dict_variant(self):
        data = {'resourceType': 'MolecularSequence', 'variant': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.variant is not None

    def test_from_dict_observed_seq(self):
        data = {'resourceType': 'MolecularSequence', 'observedSeq': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.observedSeq is not None

    def test_from_dict_quality(self):
        data = {'resourceType': 'MolecularSequence', 'quality': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.quality is not None

    def test_from_dict_read_coverage(self):
        data = {'resourceType': 'MolecularSequence', 'readCoverage': 42}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.readCoverage is not None

    def test_from_dict_repository(self):
        data = {'resourceType': 'MolecularSequence', 'repository': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.repository is not None

    def test_from_dict_pointer(self):
        data = {'resourceType': 'MolecularSequence', 'pointer': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.pointer is not None

    def test_from_dict_structure_variant(self):
        data = {'resourceType': 'MolecularSequence', 'structureVariant': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MolecularSequence)
        assert result.structureVariant is not None


class TestGetPathMolecularSequence:

    def test_get_path_id(self):
        resource = MolecularSequence()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = MolecularSequence()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = MolecularSequence()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'MolecularSequence.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = MolecularSequence()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = MolecularSequence()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = MolecularSequence()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = MolecularSequence()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = MolecularSequence()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = MolecularSequence()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = MolecularSequence()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = MolecularSequence()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_type(self):
        resource = MolecularSequence()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_coordinate_system(self):
        resource = MolecularSequence()
        resource.coordinateSystem = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'coordinateSystem')
        assert result is not None

    def test_get_path_patient(self):
        resource = MolecularSequence()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_specimen(self):
        resource = MolecularSequence()
        resource.specimen = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'specimen')
        assert result is not None

    def test_get_path_device(self):
        resource = MolecularSequence()
        resource.device = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'device')
        assert result is not None

    def test_get_path_performer(self):
        resource = MolecularSequence()
        resource.performer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performer')
        assert result is not None

    def test_get_path_quantity(self):
        resource = MolecularSequence()
        resource.quantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'quantity')
        assert result is not None

    def test_get_path_reference_seq(self):
        resource = MolecularSequence()
        resource.referenceSeq = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'referenceSeq')
        assert result is not None

    def test_get_path_variant(self):
        resource = MolecularSequence()
        resource.variant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'variant')
        assert result is not None

    def test_get_path_observed_seq(self):
        resource = MolecularSequence()
        resource.observedSeq = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'observedSeq')
        assert result is not None

    def test_get_path_quality(self):
        resource = MolecularSequence()
        resource.quality = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'quality')
        assert result is not None

    def test_get_path_read_coverage(self):
        resource = MolecularSequence()
        resource.readCoverage = 42
        result = zato.fhir_r4_0_1_core.get_path(resource, 'readCoverage')
        assert result is not None

    def test_get_path_repository(self):
        resource = MolecularSequence()
        resource.repository = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'repository')
        assert result is not None

    def test_get_path_pointer(self):
        resource = MolecularSequence()
        resource.pointer = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'pointer')
        assert result is not None

    def test_get_path_structure_variant(self):
        resource = MolecularSequence()
        resource.structureVariant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'structureVariant')
        assert result is not None


class TestSetPathMolecularSequence:

    def test_set_path_id(self):
        resource = MolecularSequence()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = MolecularSequence()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'MolecularSequence.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = MolecularSequence()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = MolecularSequence()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = MolecularSequence()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = MolecularSequence()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = MolecularSequence()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = MolecularSequence()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = MolecularSequence()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = MolecularSequence()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_type(self):
        resource = MolecularSequence()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_coordinate_system(self):
        resource = MolecularSequence()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'coordinateSystem', value)
        assert result is True
        assert resource.coordinateSystem is not None

    def test_set_path_patient(self):
        resource = MolecularSequence()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_specimen(self):
        resource = MolecularSequence()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'specimen', value)
        assert result is True
        assert resource.specimen is not None

    def test_set_path_device(self):
        resource = MolecularSequence()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'device', value)
        assert result is True
        assert resource.device is not None

    def test_set_path_performer(self):
        resource = MolecularSequence()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performer', value)
        assert result is True
        assert resource.performer is not None

    def test_set_path_quantity(self):
        resource = MolecularSequence()
        value = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'quantity', value)
        assert result is True
        assert resource.quantity is not None

    def test_set_path_reference_seq(self):
        resource = MolecularSequence()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'referenceSeq', value)
        assert result is True
        assert resource.referenceSeq is not None

    def test_set_path_variant(self):
        resource = MolecularSequence()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'variant', value)
        assert result is True
        assert resource.variant is not None

    def test_set_path_observed_seq(self):
        resource = MolecularSequence()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'observedSeq', value)
        assert result is True
        assert resource.observedSeq is not None

    def test_set_path_quality(self):
        resource = MolecularSequence()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'quality', value)
        assert result is True
        assert resource.quality is not None

    def test_set_path_read_coverage(self):
        resource = MolecularSequence()
        value = 42
        result = zato.fhir_r4_0_1_core.set_path(resource, 'readCoverage', value)
        assert result is True
        assert resource.readCoverage is not None

    def test_set_path_repository(self):
        resource = MolecularSequence()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'repository', value)
        assert result is True
        assert resource.repository is not None

    def test_set_path_pointer(self):
        resource = MolecularSequence()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'pointer', value)
        assert result is True
        assert resource.pointer is not None

    def test_set_path_structure_variant(self):
        resource = MolecularSequence()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'structureVariant', value)
        assert result is True
        assert resource.structureVariant is not None


class TestParsePathMolecularSequence:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('MolecularSequence.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('MolecularSequence.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('MolecularSequence.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
