# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import MedicationKnowledge


class TestToDictMedicationKnowledge:

    def test_to_dict_empty(self):
        resource = MedicationKnowledge()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'MedicationKnowledge'

    def test_to_dict_with_id(self):
        resource = MedicationKnowledge()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = MedicationKnowledge()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, MedicationKnowledge)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = MedicationKnowledge()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = MedicationKnowledge()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = MedicationKnowledge()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = MedicationKnowledge()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = MedicationKnowledge()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = MedicationKnowledge()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = MedicationKnowledge()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = MedicationKnowledge()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_code(self):
        resource = MedicationKnowledge()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_status(self):
        resource = MedicationKnowledge()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_manufacturer(self):
        resource = MedicationKnowledge()
        resource.manufacturer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'manufacturer' in result

    def test_to_dict_dose_form(self):
        resource = MedicationKnowledge()
        resource.doseForm = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'doseForm' in result

    def test_to_dict_amount(self):
        resource = MedicationKnowledge()
        resource.amount = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'amount' in result

    def test_to_dict_synonym(self):
        resource = MedicationKnowledge()
        resource.synonym = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'synonym' in result

    def test_to_dict_related_medication_knowledge(self):
        resource = MedicationKnowledge()
        resource.relatedMedicationKnowledge = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relatedMedicationKnowledge' in result

    def test_to_dict_associated_medication(self):
        resource = MedicationKnowledge()
        resource.associatedMedication = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'associatedMedication' in result

    def test_to_dict_product_type(self):
        resource = MedicationKnowledge()
        resource.productType = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'productType' in result

    def test_to_dict_monograph(self):
        resource = MedicationKnowledge()
        resource.monograph = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'monograph' in result

    def test_to_dict_ingredient(self):
        resource = MedicationKnowledge()
        resource.ingredient = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'ingredient' in result

    def test_to_dict_preparation_instruction(self):
        resource = MedicationKnowledge()
        resource.preparationInstruction = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'preparationInstruction' in result

    def test_to_dict_intended_route(self):
        resource = MedicationKnowledge()
        resource.intendedRoute = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'intendedRoute' in result

    def test_to_dict_cost(self):
        resource = MedicationKnowledge()
        resource.cost = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'cost' in result

    def test_to_dict_monitoring_program(self):
        resource = MedicationKnowledge()
        resource.monitoringProgram = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'monitoringProgram' in result

    def test_to_dict_administration_guidelines(self):
        resource = MedicationKnowledge()
        resource.administrationGuidelines = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'administrationGuidelines' in result

    def test_to_dict_medicine_classification(self):
        resource = MedicationKnowledge()
        resource.medicineClassification = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'medicineClassification' in result

    def test_to_dict_packaging(self):
        resource = MedicationKnowledge()
        resource.packaging = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'packaging' in result

    def test_to_dict_drug_characteristic(self):
        resource = MedicationKnowledge()
        resource.drugCharacteristic = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'drugCharacteristic' in result

    def test_to_dict_contraindication(self):
        resource = MedicationKnowledge()
        resource.contraindication = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contraindication' in result

    def test_to_dict_regulatory(self):
        resource = MedicationKnowledge()
        resource.regulatory = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'regulatory' in result

    def test_to_dict_kinetics(self):
        resource = MedicationKnowledge()
        resource.kinetics = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'kinetics' in result


class TestFromDictMedicationKnowledge:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'MedicationKnowledge', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert isinstance(result, MedicationKnowledge)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'MedicationKnowledge'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert isinstance(result, MedicationKnowledge)

    def test_from_dict_id(self):
        data = {'resourceType': 'MedicationKnowledge', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'MedicationKnowledge', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'MedicationKnowledge', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'MedicationKnowledge', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'MedicationKnowledge', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'MedicationKnowledge', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'MedicationKnowledge', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'MedicationKnowledge', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.modifierExtension is not None

    def test_from_dict_code(self):
        data = {'code': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'MedicationKnowledge'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.code is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'MedicationKnowledge', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.status is not None

    def test_from_dict_manufacturer(self):
        data = {'resourceType': 'MedicationKnowledge', 'manufacturer': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.manufacturer is not None

    def test_from_dict_dose_form(self):
        data = {'doseForm': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'},
         'resourceType': 'MedicationKnowledge'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.doseForm is not None

    def test_from_dict_amount(self):
        data = {'resourceType': 'MedicationKnowledge', 'amount': {'value': 100, 'unit': 'mg'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.amount is not None

    def test_from_dict_synonym(self):
        data = {'resourceType': 'MedicationKnowledge', 'synonym': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.synonym is not None

    def test_from_dict_related_medication_knowledge(self):
        data = {'resourceType': 'MedicationKnowledge', 'relatedMedicationKnowledge': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.relatedMedicationKnowledge is not None

    def test_from_dict_associated_medication(self):
        data = {'resourceType': 'MedicationKnowledge', 'associatedMedication': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.associatedMedication is not None

    def test_from_dict_product_type(self):
        data = {'productType': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'}],
         'resourceType': 'MedicationKnowledge'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.productType is not None

    def test_from_dict_monograph(self):
        data = {'resourceType': 'MedicationKnowledge', 'monograph': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.monograph is not None

    def test_from_dict_ingredient(self):
        data = {'resourceType': 'MedicationKnowledge', 'ingredient': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.ingredient is not None

    def test_from_dict_preparation_instruction(self):
        data = {'resourceType': 'MedicationKnowledge', 'preparationInstruction': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.preparationInstruction is not None

    def test_from_dict_intended_route(self):
        data = {'intendedRoute': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                            'text': 'Test concept'}],
         'resourceType': 'MedicationKnowledge'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.intendedRoute is not None

    def test_from_dict_cost(self):
        data = {'resourceType': 'MedicationKnowledge', 'cost': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.cost is not None

    def test_from_dict_monitoring_program(self):
        data = {'resourceType': 'MedicationKnowledge', 'monitoringProgram': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.monitoringProgram is not None

    def test_from_dict_administration_guidelines(self):
        data = {'resourceType': 'MedicationKnowledge', 'administrationGuidelines': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.administrationGuidelines is not None

    def test_from_dict_medicine_classification(self):
        data = {'resourceType': 'MedicationKnowledge', 'medicineClassification': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.medicineClassification is not None

    def test_from_dict_packaging(self):
        data = {'resourceType': 'MedicationKnowledge', 'packaging': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.packaging is not None

    def test_from_dict_drug_characteristic(self):
        data = {'resourceType': 'MedicationKnowledge', 'drugCharacteristic': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.drugCharacteristic is not None

    def test_from_dict_contraindication(self):
        data = {'resourceType': 'MedicationKnowledge', 'contraindication': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.contraindication is not None

    def test_from_dict_regulatory(self):
        data = {'resourceType': 'MedicationKnowledge', 'regulatory': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.regulatory is not None

    def test_from_dict_kinetics(self):
        data = {'resourceType': 'MedicationKnowledge', 'kinetics': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicationKnowledge)
        assert result.kinetics is not None


class TestGetPathMedicationKnowledge:

    def test_get_path_id(self):
        resource = MedicationKnowledge()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = MedicationKnowledge()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = MedicationKnowledge()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'MedicationKnowledge.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = MedicationKnowledge()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = MedicationKnowledge()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = MedicationKnowledge()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = MedicationKnowledge()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = MedicationKnowledge()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = MedicationKnowledge()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = MedicationKnowledge()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_code(self):
        resource = MedicationKnowledge()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_status(self):
        resource = MedicationKnowledge()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_manufacturer(self):
        resource = MedicationKnowledge()
        resource.manufacturer = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'manufacturer')
        assert result is not None

    def test_get_path_dose_form(self):
        resource = MedicationKnowledge()
        resource.doseForm = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'doseForm')
        assert result is not None

    def test_get_path_amount(self):
        resource = MedicationKnowledge()
        resource.amount = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'amount')
        assert result is not None

    def test_get_path_synonym(self):
        resource = MedicationKnowledge()
        resource.synonym = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'synonym')
        assert result is not None

    def test_get_path_related_medication_knowledge(self):
        resource = MedicationKnowledge()
        resource.relatedMedicationKnowledge = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relatedMedicationKnowledge')
        assert result is not None

    def test_get_path_associated_medication(self):
        resource = MedicationKnowledge()
        resource.associatedMedication = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'associatedMedication')
        assert result is not None

    def test_get_path_product_type(self):
        resource = MedicationKnowledge()
        resource.productType = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'productType')
        assert result is not None

    def test_get_path_monograph(self):
        resource = MedicationKnowledge()
        resource.monograph = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'monograph')
        assert result is not None

    def test_get_path_ingredient(self):
        resource = MedicationKnowledge()
        resource.ingredient = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ingredient')
        assert result is not None

    def test_get_path_preparation_instruction(self):
        resource = MedicationKnowledge()
        resource.preparationInstruction = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'preparationInstruction')
        assert result is not None

    def test_get_path_intended_route(self):
        resource = MedicationKnowledge()
        resource.intendedRoute = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'intendedRoute')
        assert result is not None

    def test_get_path_cost(self):
        resource = MedicationKnowledge()
        resource.cost = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'cost')
        assert result is not None

    def test_get_path_monitoring_program(self):
        resource = MedicationKnowledge()
        resource.monitoringProgram = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'monitoringProgram')
        assert result is not None

    def test_get_path_administration_guidelines(self):
        resource = MedicationKnowledge()
        resource.administrationGuidelines = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'administrationGuidelines')
        assert result is not None

    def test_get_path_medicine_classification(self):
        resource = MedicationKnowledge()
        resource.medicineClassification = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'medicineClassification')
        assert result is not None

    def test_get_path_packaging(self):
        resource = MedicationKnowledge()
        resource.packaging = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'packaging')
        assert result is not None

    def test_get_path_drug_characteristic(self):
        resource = MedicationKnowledge()
        resource.drugCharacteristic = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'drugCharacteristic')
        assert result is not None

    def test_get_path_contraindication(self):
        resource = MedicationKnowledge()
        resource.contraindication = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contraindication')
        assert result is not None

    def test_get_path_regulatory(self):
        resource = MedicationKnowledge()
        resource.regulatory = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'regulatory')
        assert result is not None

    def test_get_path_kinetics(self):
        resource = MedicationKnowledge()
        resource.kinetics = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'kinetics')
        assert result is not None


class TestSetPathMedicationKnowledge:

    def test_set_path_id(self):
        resource = MedicationKnowledge()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = MedicationKnowledge()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'MedicationKnowledge.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = MedicationKnowledge()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = MedicationKnowledge()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = MedicationKnowledge()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = MedicationKnowledge()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = MedicationKnowledge()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = MedicationKnowledge()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = MedicationKnowledge()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_code(self):
        resource = MedicationKnowledge()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_status(self):
        resource = MedicationKnowledge()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_manufacturer(self):
        resource = MedicationKnowledge()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'manufacturer', value)
        assert result is True
        assert resource.manufacturer is not None

    def test_set_path_dose_form(self):
        resource = MedicationKnowledge()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'doseForm', value)
        assert result is True
        assert resource.doseForm is not None

    def test_set_path_amount(self):
        resource = MedicationKnowledge()
        value = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'amount', value)
        assert result is True
        assert resource.amount is not None

    def test_set_path_synonym(self):
        resource = MedicationKnowledge()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'synonym', value)
        assert result is True
        assert resource.synonym is not None

    def test_set_path_related_medication_knowledge(self):
        resource = MedicationKnowledge()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relatedMedicationKnowledge', value)
        assert result is True
        assert resource.relatedMedicationKnowledge is not None

    def test_set_path_associated_medication(self):
        resource = MedicationKnowledge()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'associatedMedication', value)
        assert result is True
        assert resource.associatedMedication is not None

    def test_set_path_product_type(self):
        resource = MedicationKnowledge()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'productType', value)
        assert result is True
        assert resource.productType is not None

    def test_set_path_monograph(self):
        resource = MedicationKnowledge()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'monograph', value)
        assert result is True
        assert resource.monograph is not None

    def test_set_path_ingredient(self):
        resource = MedicationKnowledge()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ingredient', value)
        assert result is True
        assert resource.ingredient is not None

    def test_set_path_preparation_instruction(self):
        resource = MedicationKnowledge()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'preparationInstruction', value)
        assert result is True
        assert resource.preparationInstruction is not None

    def test_set_path_intended_route(self):
        resource = MedicationKnowledge()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'intendedRoute', value)
        assert result is True
        assert resource.intendedRoute is not None

    def test_set_path_cost(self):
        resource = MedicationKnowledge()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'cost', value)
        assert result is True
        assert resource.cost is not None

    def test_set_path_monitoring_program(self):
        resource = MedicationKnowledge()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'monitoringProgram', value)
        assert result is True
        assert resource.monitoringProgram is not None

    def test_set_path_administration_guidelines(self):
        resource = MedicationKnowledge()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'administrationGuidelines', value)
        assert result is True
        assert resource.administrationGuidelines is not None

    def test_set_path_medicine_classification(self):
        resource = MedicationKnowledge()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'medicineClassification', value)
        assert result is True
        assert resource.medicineClassification is not None

    def test_set_path_packaging(self):
        resource = MedicationKnowledge()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'packaging', value)
        assert result is True
        assert resource.packaging is not None

    def test_set_path_drug_characteristic(self):
        resource = MedicationKnowledge()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'drugCharacteristic', value)
        assert result is True
        assert resource.drugCharacteristic is not None

    def test_set_path_contraindication(self):
        resource = MedicationKnowledge()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contraindication', value)
        assert result is True
        assert resource.contraindication is not None

    def test_set_path_regulatory(self):
        resource = MedicationKnowledge()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'regulatory', value)
        assert result is True
        assert resource.regulatory is not None

    def test_set_path_kinetics(self):
        resource = MedicationKnowledge()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'kinetics', value)
        assert result is True
        assert resource.kinetics is not None


class TestParsePathMedicationKnowledge:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicationKnowledge.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicationKnowledge.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicationKnowledge.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
