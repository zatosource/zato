# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import MedicinalProduct


class TestToDictMedicinalProduct:

    def test_to_dict_empty(self):
        resource = MedicinalProduct()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'MedicinalProduct'

    def test_to_dict_with_id(self):
        resource = MedicinalProduct()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = MedicinalProduct()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, MedicinalProduct)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = MedicinalProduct()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = MedicinalProduct()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = MedicinalProduct()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = MedicinalProduct()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = MedicinalProduct()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = MedicinalProduct()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = MedicinalProduct()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = MedicinalProduct()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = MedicinalProduct()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_type(self):
        resource = MedicinalProduct()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_domain(self):
        resource = MedicinalProduct()
        resource.domain = {'system': 'http://example.org', 'code': 'test-code'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'domain' in result

    def test_to_dict_combined_pharmaceutical_dose_form(self):
        resource = MedicinalProduct()
        resource.combinedPharmaceuticalDoseForm = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'combinedPharmaceuticalDoseForm' in result

    def test_to_dict_legal_status_of_supply(self):
        resource = MedicinalProduct()
        resource.legalStatusOfSupply = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'legalStatusOfSupply' in result

    def test_to_dict_additional_monitoring_indicator(self):
        resource = MedicinalProduct()
        resource.additionalMonitoringIndicator = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'additionalMonitoringIndicator' in result

    def test_to_dict_special_measures(self):
        resource = MedicinalProduct()
        resource.specialMeasures = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'specialMeasures' in result

    def test_to_dict_paediatric_use_indicator(self):
        resource = MedicinalProduct()
        resource.paediatricUseIndicator = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'paediatricUseIndicator' in result

    def test_to_dict_product_classification(self):
        resource = MedicinalProduct()
        resource.productClassification = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'productClassification' in result

    def test_to_dict_marketing_status(self):
        resource = MedicinalProduct()
        resource.marketingStatus = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'marketingStatus' in result

    def test_to_dict_pharmaceutical_product(self):
        resource = MedicinalProduct()
        resource.pharmaceuticalProduct = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'pharmaceuticalProduct' in result

    def test_to_dict_packaged_medicinal_product(self):
        resource = MedicinalProduct()
        resource.packagedMedicinalProduct = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'packagedMedicinalProduct' in result

    def test_to_dict_attached_document(self):
        resource = MedicinalProduct()
        resource.attachedDocument = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'attachedDocument' in result

    def test_to_dict_master_file(self):
        resource = MedicinalProduct()
        resource.masterFile = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'masterFile' in result

    def test_to_dict_contact(self):
        resource = MedicinalProduct()
        resource.contact = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_clinical_trial(self):
        resource = MedicinalProduct()
        resource.clinicalTrial = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'clinicalTrial' in result

    def test_to_dict_name(self):
        resource = MedicinalProduct()
        resource.name = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_cross_reference(self):
        resource = MedicinalProduct()
        resource.crossReference = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'crossReference' in result

    def test_to_dict_manufacturing_business_operation(self):
        resource = MedicinalProduct()
        resource.manufacturingBusinessOperation = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'manufacturingBusinessOperation' in result

    def test_to_dict_special_designation(self):
        resource = MedicinalProduct()
        resource.specialDesignation = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'specialDesignation' in result


class TestFromDictMedicinalProduct:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'MedicinalProduct', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert isinstance(result, MedicinalProduct)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'MedicinalProduct'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert isinstance(result, MedicinalProduct)

    def test_from_dict_id(self):
        data = {'resourceType': 'MedicinalProduct', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'MedicinalProduct', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'MedicinalProduct', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'MedicinalProduct', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'MedicinalProduct', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'MedicinalProduct', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'MedicinalProduct', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'MedicinalProduct', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'MedicinalProduct', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.identifier is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'MedicinalProduct',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.type_ is not None

    def test_from_dict_domain(self):
        data = {'resourceType': 'MedicinalProduct', 'domain': {'system': 'http://example.org', 'code': 'test-code'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.domain is not None

    def test_from_dict_combined_pharmaceutical_dose_form(self):
        data = {'combinedPharmaceuticalDoseForm': {'coding': [{'code': 'test-code',
                                                        'display': 'Test',
                                                        'system': 'http://example.org'}],
                                            'text': 'Test concept'},
         'resourceType': 'MedicinalProduct'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.combinedPharmaceuticalDoseForm is not None

    def test_from_dict_legal_status_of_supply(self):
        data = {'legalStatusOfSupply': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                 'text': 'Test concept'},
         'resourceType': 'MedicinalProduct'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.legalStatusOfSupply is not None

    def test_from_dict_additional_monitoring_indicator(self):
        data = {'additionalMonitoringIndicator': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                           'text': 'Test concept'},
         'resourceType': 'MedicinalProduct'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.additionalMonitoringIndicator is not None

    def test_from_dict_special_measures(self):
        data = {'resourceType': 'MedicinalProduct', 'specialMeasures': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.specialMeasures is not None

    def test_from_dict_paediatric_use_indicator(self):
        data = {'paediatricUseIndicator': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                    'text': 'Test concept'},
         'resourceType': 'MedicinalProduct'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.paediatricUseIndicator is not None

    def test_from_dict_product_classification(self):
        data = {'productClassification': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                    'text': 'Test concept'}],
         'resourceType': 'MedicinalProduct'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.productClassification is not None

    def test_from_dict_marketing_status(self):
        data = {'resourceType': 'MedicinalProduct', 'marketingStatus': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.marketingStatus is not None

    def test_from_dict_pharmaceutical_product(self):
        data = {'resourceType': 'MedicinalProduct', 'pharmaceuticalProduct': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.pharmaceuticalProduct is not None

    def test_from_dict_packaged_medicinal_product(self):
        data = {'resourceType': 'MedicinalProduct', 'packagedMedicinalProduct': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.packagedMedicinalProduct is not None

    def test_from_dict_attached_document(self):
        data = {'resourceType': 'MedicinalProduct', 'attachedDocument': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.attachedDocument is not None

    def test_from_dict_master_file(self):
        data = {'resourceType': 'MedicinalProduct', 'masterFile': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.masterFile is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'MedicinalProduct', 'contact': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.contact is not None

    def test_from_dict_clinical_trial(self):
        data = {'resourceType': 'MedicinalProduct', 'clinicalTrial': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.clinicalTrial is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'MedicinalProduct', 'name': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.name is not None

    def test_from_dict_cross_reference(self):
        data = {'resourceType': 'MedicinalProduct', 'crossReference': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.crossReference is not None

    def test_from_dict_manufacturing_business_operation(self):
        data = {'resourceType': 'MedicinalProduct', 'manufacturingBusinessOperation': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.manufacturingBusinessOperation is not None

    def test_from_dict_special_designation(self):
        data = {'resourceType': 'MedicinalProduct', 'specialDesignation': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MedicinalProduct)
        assert result.specialDesignation is not None


class TestGetPathMedicinalProduct:

    def test_get_path_id(self):
        resource = MedicinalProduct()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = MedicinalProduct()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = MedicinalProduct()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'MedicinalProduct.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = MedicinalProduct()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = MedicinalProduct()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = MedicinalProduct()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = MedicinalProduct()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = MedicinalProduct()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = MedicinalProduct()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = MedicinalProduct()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = MedicinalProduct()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_type(self):
        resource = MedicinalProduct()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_domain(self):
        resource = MedicinalProduct()
        resource.domain = {'system': 'http://example.org', 'code': 'test-code'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'domain')
        assert result is not None

    def test_get_path_combined_pharmaceutical_dose_form(self):
        resource = MedicinalProduct()
        resource.combinedPharmaceuticalDoseForm = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'combinedPharmaceuticalDoseForm')
        assert result is not None

    def test_get_path_legal_status_of_supply(self):
        resource = MedicinalProduct()
        resource.legalStatusOfSupply = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'legalStatusOfSupply')
        assert result is not None

    def test_get_path_additional_monitoring_indicator(self):
        resource = MedicinalProduct()
        resource.additionalMonitoringIndicator = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'additionalMonitoringIndicator')
        assert result is not None

    def test_get_path_special_measures(self):
        resource = MedicinalProduct()
        resource.specialMeasures = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'specialMeasures')
        assert result is not None

    def test_get_path_paediatric_use_indicator(self):
        resource = MedicinalProduct()
        resource.paediatricUseIndicator = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'paediatricUseIndicator')
        assert result is not None

    def test_get_path_product_classification(self):
        resource = MedicinalProduct()
        resource.productClassification = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'productClassification')
        assert result is not None

    def test_get_path_marketing_status(self):
        resource = MedicinalProduct()
        resource.marketingStatus = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'marketingStatus')
        assert result is not None

    def test_get_path_pharmaceutical_product(self):
        resource = MedicinalProduct()
        resource.pharmaceuticalProduct = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'pharmaceuticalProduct')
        assert result is not None

    def test_get_path_packaged_medicinal_product(self):
        resource = MedicinalProduct()
        resource.packagedMedicinalProduct = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'packagedMedicinalProduct')
        assert result is not None

    def test_get_path_attached_document(self):
        resource = MedicinalProduct()
        resource.attachedDocument = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'attachedDocument')
        assert result is not None

    def test_get_path_master_file(self):
        resource = MedicinalProduct()
        resource.masterFile = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'masterFile')
        assert result is not None

    def test_get_path_contact(self):
        resource = MedicinalProduct()
        resource.contact = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_clinical_trial(self):
        resource = MedicinalProduct()
        resource.clinicalTrial = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'clinicalTrial')
        assert result is not None

    def test_get_path_name(self):
        resource = MedicinalProduct()
        resource.name = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_cross_reference(self):
        resource = MedicinalProduct()
        resource.crossReference = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'crossReference')
        assert result is not None

    def test_get_path_manufacturing_business_operation(self):
        resource = MedicinalProduct()
        resource.manufacturingBusinessOperation = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'manufacturingBusinessOperation')
        assert result is not None

    def test_get_path_special_designation(self):
        resource = MedicinalProduct()
        resource.specialDesignation = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'specialDesignation')
        assert result is not None


class TestSetPathMedicinalProduct:

    def test_set_path_id(self):
        resource = MedicinalProduct()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = MedicinalProduct()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'MedicinalProduct.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = MedicinalProduct()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = MedicinalProduct()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = MedicinalProduct()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = MedicinalProduct()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = MedicinalProduct()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = MedicinalProduct()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = MedicinalProduct()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = MedicinalProduct()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_type(self):
        resource = MedicinalProduct()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_domain(self):
        resource = MedicinalProduct()
        value = {'system': 'http://example.org', 'code': 'test-code'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'domain', value)
        assert result is True
        assert resource.domain is not None

    def test_set_path_combined_pharmaceutical_dose_form(self):
        resource = MedicinalProduct()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'combinedPharmaceuticalDoseForm', value)
        assert result is True
        assert resource.combinedPharmaceuticalDoseForm is not None

    def test_set_path_legal_status_of_supply(self):
        resource = MedicinalProduct()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'legalStatusOfSupply', value)
        assert result is True
        assert resource.legalStatusOfSupply is not None

    def test_set_path_additional_monitoring_indicator(self):
        resource = MedicinalProduct()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'additionalMonitoringIndicator', value)
        assert result is True
        assert resource.additionalMonitoringIndicator is not None

    def test_set_path_special_measures(self):
        resource = MedicinalProduct()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'specialMeasures', value)
        assert result is True
        assert resource.specialMeasures is not None

    def test_set_path_paediatric_use_indicator(self):
        resource = MedicinalProduct()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'paediatricUseIndicator', value)
        assert result is True
        assert resource.paediatricUseIndicator is not None

    def test_set_path_product_classification(self):
        resource = MedicinalProduct()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'productClassification', value)
        assert result is True
        assert resource.productClassification is not None

    def test_set_path_marketing_status(self):
        resource = MedicinalProduct()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'marketingStatus', value)
        assert result is True
        assert resource.marketingStatus is not None

    def test_set_path_pharmaceutical_product(self):
        resource = MedicinalProduct()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'pharmaceuticalProduct', value)
        assert result is True
        assert resource.pharmaceuticalProduct is not None

    def test_set_path_packaged_medicinal_product(self):
        resource = MedicinalProduct()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'packagedMedicinalProduct', value)
        assert result is True
        assert resource.packagedMedicinalProduct is not None

    def test_set_path_attached_document(self):
        resource = MedicinalProduct()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'attachedDocument', value)
        assert result is True
        assert resource.attachedDocument is not None

    def test_set_path_master_file(self):
        resource = MedicinalProduct()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'masterFile', value)
        assert result is True
        assert resource.masterFile is not None

    def test_set_path_contact(self):
        resource = MedicinalProduct()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_clinical_trial(self):
        resource = MedicinalProduct()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'clinicalTrial', value)
        assert result is True
        assert resource.clinicalTrial is not None

    def test_set_path_name(self):
        resource = MedicinalProduct()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_cross_reference(self):
        resource = MedicinalProduct()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'crossReference', value)
        assert result is True
        assert resource.crossReference is not None

    def test_set_path_manufacturing_business_operation(self):
        resource = MedicinalProduct()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'manufacturingBusinessOperation', value)
        assert result is True
        assert resource.manufacturingBusinessOperation is not None

    def test_set_path_special_designation(self):
        resource = MedicinalProduct()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'specialDesignation', value)
        assert result is True
        assert resource.specialDesignation is not None


class TestParsePathMedicinalProduct:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProduct.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProduct.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('MedicinalProduct.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
