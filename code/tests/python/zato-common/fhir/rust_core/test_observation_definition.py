# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ObservationDefinition


class TestToDictObservationDefinition:

    def test_to_dict_empty(self):
        resource = ObservationDefinition()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ObservationDefinition'

    def test_to_dict_with_id(self):
        resource = ObservationDefinition()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ObservationDefinition()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ObservationDefinition)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ObservationDefinition()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ObservationDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ObservationDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ObservationDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ObservationDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ObservationDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ObservationDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ObservationDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_category(self):
        resource = ObservationDefinition()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_code(self):
        resource = ObservationDefinition()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_identifier(self):
        resource = ObservationDefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_permitted_data_type(self):
        resource = ObservationDefinition()
        resource.permittedDataType = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'permittedDataType' in result

    def test_to_dict_multiple_results_allowed(self):
        resource = ObservationDefinition()
        resource.multipleResultsAllowed = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'multipleResultsAllowed' in result

    def test_to_dict_method(self):
        resource = ObservationDefinition()
        resource.method = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'method' in result

    def test_to_dict_preferred_report_name(self):
        resource = ObservationDefinition()
        resource.preferredReportName = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'preferredReportName' in result

    def test_to_dict_quantitative_details(self):
        resource = ObservationDefinition()
        resource.quantitativeDetails = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'quantitativeDetails' in result

    def test_to_dict_qualified_interval(self):
        resource = ObservationDefinition()
        resource.qualifiedInterval = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'qualifiedInterval' in result

    def test_to_dict_valid_coded_value_set(self):
        resource = ObservationDefinition()
        resource.validCodedValueSet = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'validCodedValueSet' in result

    def test_to_dict_normal_coded_value_set(self):
        resource = ObservationDefinition()
        resource.normalCodedValueSet = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'normalCodedValueSet' in result

    def test_to_dict_abnormal_coded_value_set(self):
        resource = ObservationDefinition()
        resource.abnormalCodedValueSet = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'abnormalCodedValueSet' in result

    def test_to_dict_critical_coded_value_set(self):
        resource = ObservationDefinition()
        resource.criticalCodedValueSet = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'criticalCodedValueSet' in result


class TestFromDictObservationDefinition:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ObservationDefinition', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert isinstance(result, ObservationDefinition)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ObservationDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert isinstance(result, ObservationDefinition)

    def test_from_dict_id(self):
        data = {'resourceType': 'ObservationDefinition', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ObservationDefinition', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ObservationDefinition', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ObservationDefinition', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ObservationDefinition', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ObservationDefinition', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ObservationDefinition', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ObservationDefinition', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.modifierExtension is not None

    def test_from_dict_category(self):
        data = {'category': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'ObservationDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.category is not None

    def test_from_dict_code(self):
        data = {'code': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'ObservationDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.code is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'ObservationDefinition', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.identifier is not None

    def test_from_dict_permitted_data_type(self):
        data = {'resourceType': 'ObservationDefinition', 'permittedDataType': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.permittedDataType is not None

    def test_from_dict_multiple_results_allowed(self):
        data = {'resourceType': 'ObservationDefinition', 'multipleResultsAllowed': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.multipleResultsAllowed is not None

    def test_from_dict_method(self):
        data = {'method': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'},
         'resourceType': 'ObservationDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.method is not None

    def test_from_dict_preferred_report_name(self):
        data = {'resourceType': 'ObservationDefinition', 'preferredReportName': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.preferredReportName is not None

    def test_from_dict_quantitative_details(self):
        data = {'resourceType': 'ObservationDefinition', 'quantitativeDetails': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.quantitativeDetails is not None

    def test_from_dict_qualified_interval(self):
        data = {'resourceType': 'ObservationDefinition', 'qualifiedInterval': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.qualifiedInterval is not None

    def test_from_dict_valid_coded_value_set(self):
        data = {'resourceType': 'ObservationDefinition', 'validCodedValueSet': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.validCodedValueSet is not None

    def test_from_dict_normal_coded_value_set(self):
        data = {'resourceType': 'ObservationDefinition', 'normalCodedValueSet': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.normalCodedValueSet is not None

    def test_from_dict_abnormal_coded_value_set(self):
        data = {'resourceType': 'ObservationDefinition', 'abnormalCodedValueSet': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.abnormalCodedValueSet is not None

    def test_from_dict_critical_coded_value_set(self):
        data = {'resourceType': 'ObservationDefinition', 'criticalCodedValueSet': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ObservationDefinition)
        assert result.criticalCodedValueSet is not None


class TestGetPathObservationDefinition:

    def test_get_path_id(self):
        resource = ObservationDefinition()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ObservationDefinition()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ObservationDefinition()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ObservationDefinition.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ObservationDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ObservationDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ObservationDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ObservationDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ObservationDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ObservationDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ObservationDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_category(self):
        resource = ObservationDefinition()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_code(self):
        resource = ObservationDefinition()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_identifier(self):
        resource = ObservationDefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_permitted_data_type(self):
        resource = ObservationDefinition()
        resource.permittedDataType = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'permittedDataType')
        assert result is not None

    def test_get_path_multiple_results_allowed(self):
        resource = ObservationDefinition()
        resource.multipleResultsAllowed = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'multipleResultsAllowed')
        assert result is not None

    def test_get_path_method(self):
        resource = ObservationDefinition()
        resource.method = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'method')
        assert result is not None

    def test_get_path_preferred_report_name(self):
        resource = ObservationDefinition()
        resource.preferredReportName = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'preferredReportName')
        assert result is not None

    def test_get_path_quantitative_details(self):
        resource = ObservationDefinition()
        resource.quantitativeDetails = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'quantitativeDetails')
        assert result is not None

    def test_get_path_qualified_interval(self):
        resource = ObservationDefinition()
        resource.qualifiedInterval = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'qualifiedInterval')
        assert result is not None

    def test_get_path_valid_coded_value_set(self):
        resource = ObservationDefinition()
        resource.validCodedValueSet = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'validCodedValueSet')
        assert result is not None

    def test_get_path_normal_coded_value_set(self):
        resource = ObservationDefinition()
        resource.normalCodedValueSet = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'normalCodedValueSet')
        assert result is not None

    def test_get_path_abnormal_coded_value_set(self):
        resource = ObservationDefinition()
        resource.abnormalCodedValueSet = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'abnormalCodedValueSet')
        assert result is not None

    def test_get_path_critical_coded_value_set(self):
        resource = ObservationDefinition()
        resource.criticalCodedValueSet = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'criticalCodedValueSet')
        assert result is not None


class TestSetPathObservationDefinition:

    def test_set_path_id(self):
        resource = ObservationDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ObservationDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ObservationDefinition.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ObservationDefinition()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ObservationDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ObservationDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ObservationDefinition()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ObservationDefinition()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ObservationDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ObservationDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_category(self):
        resource = ObservationDefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_code(self):
        resource = ObservationDefinition()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_identifier(self):
        resource = ObservationDefinition()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_permitted_data_type(self):
        resource = ObservationDefinition()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'permittedDataType', value)
        assert result is True
        assert resource.permittedDataType is not None

    def test_set_path_multiple_results_allowed(self):
        resource = ObservationDefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'multipleResultsAllowed', value)
        assert result is True
        assert resource.multipleResultsAllowed is not None

    def test_set_path_method(self):
        resource = ObservationDefinition()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'method', value)
        assert result is True
        assert resource.method is not None

    def test_set_path_preferred_report_name(self):
        resource = ObservationDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'preferredReportName', value)
        assert result is True
        assert resource.preferredReportName is not None

    def test_set_path_quantitative_details(self):
        resource = ObservationDefinition()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'quantitativeDetails', value)
        assert result is True
        assert resource.quantitativeDetails is not None

    def test_set_path_qualified_interval(self):
        resource = ObservationDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'qualifiedInterval', value)
        assert result is True
        assert resource.qualifiedInterval is not None

    def test_set_path_valid_coded_value_set(self):
        resource = ObservationDefinition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'validCodedValueSet', value)
        assert result is True
        assert resource.validCodedValueSet is not None

    def test_set_path_normal_coded_value_set(self):
        resource = ObservationDefinition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'normalCodedValueSet', value)
        assert result is True
        assert resource.normalCodedValueSet is not None

    def test_set_path_abnormal_coded_value_set(self):
        resource = ObservationDefinition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'abnormalCodedValueSet', value)
        assert result is True
        assert resource.abnormalCodedValueSet is not None

    def test_set_path_critical_coded_value_set(self):
        resource = ObservationDefinition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'criticalCodedValueSet', value)
        assert result is True
        assert resource.criticalCodedValueSet is not None


class TestParsePathObservationDefinition:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ObservationDefinition.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ObservationDefinition.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ObservationDefinition.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
