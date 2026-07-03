# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import RiskAssessment


class TestToDictRiskAssessment:

    def test_to_dict_empty(self):
        resource = RiskAssessment()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'RiskAssessment'

    def test_to_dict_with_id(self):
        resource = RiskAssessment()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = RiskAssessment()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, RiskAssessment)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = RiskAssessment()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = RiskAssessment()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = RiskAssessment()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = RiskAssessment()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = RiskAssessment()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = RiskAssessment()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = RiskAssessment()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = RiskAssessment()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = RiskAssessment()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_based_on(self):
        resource = RiskAssessment()
        resource.basedOn = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_parent(self):
        resource = RiskAssessment()
        resource.parent = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'parent' in result

    def test_to_dict_status(self):
        resource = RiskAssessment()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_method(self):
        resource = RiskAssessment()
        resource.method = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'method' in result

    def test_to_dict_code(self):
        resource = RiskAssessment()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_subject(self):
        resource = RiskAssessment()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_encounter(self):
        resource = RiskAssessment()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_condition(self):
        resource = RiskAssessment()
        resource.condition = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'condition' in result

    def test_to_dict_performer(self):
        resource = RiskAssessment()
        resource.performer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performer' in result

    def test_to_dict_reason_code(self):
        resource = RiskAssessment()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonCode' in result

    def test_to_dict_reason_reference(self):
        resource = RiskAssessment()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonReference' in result

    def test_to_dict_basis(self):
        resource = RiskAssessment()
        resource.basis = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basis' in result

    def test_to_dict_prediction(self):
        resource = RiskAssessment()
        resource.prediction = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'prediction' in result

    def test_to_dict_mitigation(self):
        resource = RiskAssessment()
        resource.mitigation = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'mitigation' in result

    def test_to_dict_note(self):
        resource = RiskAssessment()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result


class TestFromDictRiskAssessment:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'RiskAssessment', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert isinstance(result, RiskAssessment)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'RiskAssessment'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert isinstance(result, RiskAssessment)

    def test_from_dict_id(self):
        data = {'resourceType': 'RiskAssessment', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'RiskAssessment', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'RiskAssessment', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'RiskAssessment', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'RiskAssessment', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'RiskAssessment', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'RiskAssessment', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'RiskAssessment', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'RiskAssessment', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.identifier is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'RiskAssessment', 'basedOn': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.basedOn is not None

    def test_from_dict_parent(self):
        data = {'resourceType': 'RiskAssessment', 'parent': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.parent is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'RiskAssessment', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.status is not None

    def test_from_dict_method(self):
        data = {'method': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'},
         'resourceType': 'RiskAssessment'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.method is not None

    def test_from_dict_code(self):
        data = {'code': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'RiskAssessment'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.code is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'RiskAssessment', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.subject is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'RiskAssessment', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.encounter is not None

    def test_from_dict_condition(self):
        data = {'resourceType': 'RiskAssessment', 'condition': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.condition is not None

    def test_from_dict_performer(self):
        data = {'resourceType': 'RiskAssessment', 'performer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.performer is not None

    def test_from_dict_reason_code(self):
        data = {'reasonCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}],
         'resourceType': 'RiskAssessment'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.reasonCode is not None

    def test_from_dict_reason_reference(self):
        data = {'resourceType': 'RiskAssessment', 'reasonReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.reasonReference is not None

    def test_from_dict_basis(self):
        data = {'resourceType': 'RiskAssessment', 'basis': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.basis is not None

    def test_from_dict_prediction(self):
        data = {'resourceType': 'RiskAssessment', 'prediction': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.prediction is not None

    def test_from_dict_mitigation(self):
        data = {'resourceType': 'RiskAssessment', 'mitigation': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.mitigation is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'RiskAssessment', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskAssessment)
        assert result.note is not None


class TestGetPathRiskAssessment:

    def test_get_path_id(self):
        resource = RiskAssessment()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = RiskAssessment()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = RiskAssessment()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'RiskAssessment.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = RiskAssessment()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = RiskAssessment()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = RiskAssessment()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = RiskAssessment()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = RiskAssessment()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = RiskAssessment()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = RiskAssessment()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = RiskAssessment()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_based_on(self):
        resource = RiskAssessment()
        resource.basedOn = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_parent(self):
        resource = RiskAssessment()
        resource.parent = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'parent')
        assert result is not None

    def test_get_path_status(self):
        resource = RiskAssessment()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_method(self):
        resource = RiskAssessment()
        resource.method = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'method')
        assert result is not None

    def test_get_path_code(self):
        resource = RiskAssessment()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_subject(self):
        resource = RiskAssessment()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_encounter(self):
        resource = RiskAssessment()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_condition(self):
        resource = RiskAssessment()
        resource.condition = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'condition')
        assert result is not None

    def test_get_path_performer(self):
        resource = RiskAssessment()
        resource.performer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performer')
        assert result is not None

    def test_get_path_reason_code(self):
        resource = RiskAssessment()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonCode')
        assert result is not None

    def test_get_path_reason_reference(self):
        resource = RiskAssessment()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonReference')
        assert result is not None

    def test_get_path_basis(self):
        resource = RiskAssessment()
        resource.basis = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basis')
        assert result is not None

    def test_get_path_prediction(self):
        resource = RiskAssessment()
        resource.prediction = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'prediction')
        assert result is not None

    def test_get_path_mitigation(self):
        resource = RiskAssessment()
        resource.mitigation = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'mitigation')
        assert result is not None

    def test_get_path_note(self):
        resource = RiskAssessment()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None


class TestSetPathRiskAssessment:

    def test_set_path_id(self):
        resource = RiskAssessment()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = RiskAssessment()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'RiskAssessment.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = RiskAssessment()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = RiskAssessment()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = RiskAssessment()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = RiskAssessment()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = RiskAssessment()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = RiskAssessment()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = RiskAssessment()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = RiskAssessment()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_based_on(self):
        resource = RiskAssessment()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_parent(self):
        resource = RiskAssessment()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'parent', value)
        assert result is True
        assert resource.parent is not None

    def test_set_path_status(self):
        resource = RiskAssessment()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_method(self):
        resource = RiskAssessment()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'method', value)
        assert result is True
        assert resource.method is not None

    def test_set_path_code(self):
        resource = RiskAssessment()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_subject(self):
        resource = RiskAssessment()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_encounter(self):
        resource = RiskAssessment()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_condition(self):
        resource = RiskAssessment()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'condition', value)
        assert result is True
        assert resource.condition is not None

    def test_set_path_performer(self):
        resource = RiskAssessment()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performer', value)
        assert result is True
        assert resource.performer is not None

    def test_set_path_reason_code(self):
        resource = RiskAssessment()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonCode', value)
        assert result is True
        assert resource.reasonCode is not None

    def test_set_path_reason_reference(self):
        resource = RiskAssessment()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonReference', value)
        assert result is True
        assert resource.reasonReference is not None

    def test_set_path_basis(self):
        resource = RiskAssessment()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basis', value)
        assert result is True
        assert resource.basis is not None

    def test_set_path_prediction(self):
        resource = RiskAssessment()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'prediction', value)
        assert result is True
        assert resource.prediction is not None

    def test_set_path_mitigation(self):
        resource = RiskAssessment()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'mitigation', value)
        assert result is True
        assert resource.mitigation is not None

    def test_set_path_note(self):
        resource = RiskAssessment()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None


class TestParsePathRiskAssessment:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('RiskAssessment.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('RiskAssessment.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('RiskAssessment.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
