# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import NutritionOrder


class TestToDictNutritionOrder:

    def test_to_dict_empty(self):
        resource = NutritionOrder()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'NutritionOrder'

    def test_to_dict_with_id(self):
        resource = NutritionOrder()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = NutritionOrder()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, NutritionOrder)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = NutritionOrder()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = NutritionOrder()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = NutritionOrder()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = NutritionOrder()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = NutritionOrder()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = NutritionOrder()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = NutritionOrder()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = NutritionOrder()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = NutritionOrder()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_instantiates_canonical(self):
        resource = NutritionOrder()
        resource.instantiatesCanonical = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesCanonical' in result

    def test_to_dict_instantiates_uri(self):
        resource = NutritionOrder()
        resource.instantiatesUri = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesUri' in result

    def test_to_dict_instantiates(self):
        resource = NutritionOrder()
        resource.instantiates = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiates' in result

    def test_to_dict_status(self):
        resource = NutritionOrder()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_intent(self):
        resource = NutritionOrder()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'intent' in result

    def test_to_dict_patient(self):
        resource = NutritionOrder()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patient' in result

    def test_to_dict_encounter(self):
        resource = NutritionOrder()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_date_time(self):
        resource = NutritionOrder()
        resource.dateTime = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dateTime' in result

    def test_to_dict_orderer(self):
        resource = NutritionOrder()
        resource.orderer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'orderer' in result

    def test_to_dict_allergy_intolerance(self):
        resource = NutritionOrder()
        resource.allergyIntolerance = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'allergyIntolerance' in result

    def test_to_dict_food_preference_modifier(self):
        resource = NutritionOrder()
        resource.foodPreferenceModifier = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'foodPreferenceModifier' in result

    def test_to_dict_exclude_food_modifier(self):
        resource = NutritionOrder()
        resource.excludeFoodModifier = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'excludeFoodModifier' in result

    def test_to_dict_oral_diet(self):
        resource = NutritionOrder()
        resource.oralDiet = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'oralDiet' in result

    def test_to_dict_supplement(self):
        resource = NutritionOrder()
        resource.supplement = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supplement' in result

    def test_to_dict_enteral_formula(self):
        resource = NutritionOrder()
        resource.enteralFormula = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'enteralFormula' in result

    def test_to_dict_note(self):
        resource = NutritionOrder()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result


class TestFromDictNutritionOrder:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'NutritionOrder', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert isinstance(result, NutritionOrder)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'NutritionOrder'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert isinstance(result, NutritionOrder)

    def test_from_dict_id(self):
        data = {'resourceType': 'NutritionOrder', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'NutritionOrder', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'NutritionOrder', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'NutritionOrder', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'NutritionOrder', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'NutritionOrder', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'NutritionOrder', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'NutritionOrder', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'NutritionOrder', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.identifier is not None

    def test_from_dict_instantiates_canonical(self):
        data = {'resourceType': 'NutritionOrder', 'instantiatesCanonical': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.instantiatesCanonical is not None

    def test_from_dict_instantiates_uri(self):
        data = {'resourceType': 'NutritionOrder', 'instantiatesUri': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.instantiatesUri is not None

    def test_from_dict_instantiates(self):
        data = {'resourceType': 'NutritionOrder', 'instantiates': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.instantiates is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'NutritionOrder', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.status is not None

    def test_from_dict_intent(self):
        data = {'resourceType': 'NutritionOrder', 'intent': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.intent is not None

    def test_from_dict_patient(self):
        data = {'resourceType': 'NutritionOrder', 'patient': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.patient is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'NutritionOrder', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.encounter is not None

    def test_from_dict_date_time(self):
        data = {'resourceType': 'NutritionOrder', 'dateTime': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.dateTime is not None

    def test_from_dict_orderer(self):
        data = {'resourceType': 'NutritionOrder', 'orderer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.orderer is not None

    def test_from_dict_allergy_intolerance(self):
        data = {'resourceType': 'NutritionOrder', 'allergyIntolerance': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.allergyIntolerance is not None

    def test_from_dict_food_preference_modifier(self):
        data = {'foodPreferenceModifier': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                     'text': 'Test concept'}],
         'resourceType': 'NutritionOrder'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.foodPreferenceModifier is not None

    def test_from_dict_exclude_food_modifier(self):
        data = {'excludeFoodModifier': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                  'text': 'Test concept'}],
         'resourceType': 'NutritionOrder'}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.excludeFoodModifier is not None

    def test_from_dict_oral_diet(self):
        data = {'resourceType': 'NutritionOrder', 'oralDiet': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.oralDiet is not None

    def test_from_dict_supplement(self):
        data = {'resourceType': 'NutritionOrder', 'supplement': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.supplement is not None

    def test_from_dict_enteral_formula(self):
        data = {'resourceType': 'NutritionOrder', 'enteralFormula': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.enteralFormula is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'NutritionOrder', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, NutritionOrder)
        assert result.note is not None


class TestGetPathNutritionOrder:

    def test_get_path_id(self):
        resource = NutritionOrder()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = NutritionOrder()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = NutritionOrder()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'NutritionOrder.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = NutritionOrder()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = NutritionOrder()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = NutritionOrder()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = NutritionOrder()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = NutritionOrder()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = NutritionOrder()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = NutritionOrder()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = NutritionOrder()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_instantiates_canonical(self):
        resource = NutritionOrder()
        resource.instantiatesCanonical = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesCanonical')
        assert result is not None

    def test_get_path_instantiates_uri(self):
        resource = NutritionOrder()
        resource.instantiatesUri = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesUri')
        assert result is not None

    def test_get_path_instantiates(self):
        resource = NutritionOrder()
        resource.instantiates = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiates')
        assert result is not None

    def test_get_path_status(self):
        resource = NutritionOrder()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_intent(self):
        resource = NutritionOrder()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'intent')
        assert result is not None

    def test_get_path_patient(self):
        resource = NutritionOrder()
        resource.patient = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patient')
        assert result is not None

    def test_get_path_encounter(self):
        resource = NutritionOrder()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_date_time(self):
        resource = NutritionOrder()
        resource.dateTime = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dateTime')
        assert result is not None

    def test_get_path_orderer(self):
        resource = NutritionOrder()
        resource.orderer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'orderer')
        assert result is not None

    def test_get_path_allergy_intolerance(self):
        resource = NutritionOrder()
        resource.allergyIntolerance = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'allergyIntolerance')
        assert result is not None

    def test_get_path_food_preference_modifier(self):
        resource = NutritionOrder()
        resource.foodPreferenceModifier = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'foodPreferenceModifier')
        assert result is not None

    def test_get_path_exclude_food_modifier(self):
        resource = NutritionOrder()
        resource.excludeFoodModifier = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'excludeFoodModifier')
        assert result is not None

    def test_get_path_oral_diet(self):
        resource = NutritionOrder()
        resource.oralDiet = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'oralDiet')
        assert result is not None

    def test_get_path_supplement(self):
        resource = NutritionOrder()
        resource.supplement = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supplement')
        assert result is not None

    def test_get_path_enteral_formula(self):
        resource = NutritionOrder()
        resource.enteralFormula = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'enteralFormula')
        assert result is not None

    def test_get_path_note(self):
        resource = NutritionOrder()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None


class TestSetPathNutritionOrder:

    def test_set_path_id(self):
        resource = NutritionOrder()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = NutritionOrder()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'NutritionOrder.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = NutritionOrder()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = NutritionOrder()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = NutritionOrder()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = NutritionOrder()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = NutritionOrder()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = NutritionOrder()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = NutritionOrder()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = NutritionOrder()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_instantiates_canonical(self):
        resource = NutritionOrder()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesCanonical', value)
        assert result is True
        assert resource.instantiatesCanonical is not None

    def test_set_path_instantiates_uri(self):
        resource = NutritionOrder()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesUri', value)
        assert result is True
        assert resource.instantiatesUri is not None

    def test_set_path_instantiates(self):
        resource = NutritionOrder()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiates', value)
        assert result is True
        assert resource.instantiates is not None

    def test_set_path_status(self):
        resource = NutritionOrder()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_intent(self):
        resource = NutritionOrder()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'intent', value)
        assert result is True
        assert resource.intent is not None

    def test_set_path_patient(self):
        resource = NutritionOrder()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patient', value)
        assert result is True
        assert resource.patient is not None

    def test_set_path_encounter(self):
        resource = NutritionOrder()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_date_time(self):
        resource = NutritionOrder()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dateTime', value)
        assert result is True
        assert resource.dateTime is not None

    def test_set_path_orderer(self):
        resource = NutritionOrder()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'orderer', value)
        assert result is True
        assert resource.orderer is not None

    def test_set_path_allergy_intolerance(self):
        resource = NutritionOrder()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'allergyIntolerance', value)
        assert result is True
        assert resource.allergyIntolerance is not None

    def test_set_path_food_preference_modifier(self):
        resource = NutritionOrder()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'foodPreferenceModifier', value)
        assert result is True
        assert resource.foodPreferenceModifier is not None

    def test_set_path_exclude_food_modifier(self):
        resource = NutritionOrder()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'excludeFoodModifier', value)
        assert result is True
        assert resource.excludeFoodModifier is not None

    def test_set_path_oral_diet(self):
        resource = NutritionOrder()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'oralDiet', value)
        assert result is True
        assert resource.oralDiet is not None

    def test_set_path_supplement(self):
        resource = NutritionOrder()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supplement', value)
        assert result is True
        assert resource.supplement is not None

    def test_set_path_enteral_formula(self):
        resource = NutritionOrder()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'enteralFormula', value)
        assert result is True
        assert resource.enteralFormula is not None

    def test_set_path_note(self):
        resource = NutritionOrder()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None


class TestParsePathNutritionOrder:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('NutritionOrder.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('NutritionOrder.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('NutritionOrder.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
