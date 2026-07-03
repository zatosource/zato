# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import InsurancePlan


class TestToDictInsurancePlan:

    def test_to_dict_empty(self):
        resource = InsurancePlan()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'InsurancePlan'

    def test_to_dict_with_id(self):
        resource = InsurancePlan()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = InsurancePlan()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, InsurancePlan)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = InsurancePlan()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = InsurancePlan()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = InsurancePlan()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = InsurancePlan()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = InsurancePlan()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = InsurancePlan()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = InsurancePlan()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = InsurancePlan()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = InsurancePlan()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = InsurancePlan()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_type(self):
        resource = InsurancePlan()
        resource.type_ = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_name(self):
        resource = InsurancePlan()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_alias(self):
        resource = InsurancePlan()
        resource.alias = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'alias' in result

    def test_to_dict_period(self):
        resource = InsurancePlan()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'period' in result

    def test_to_dict_owned_by(self):
        resource = InsurancePlan()
        resource.ownedBy = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'ownedBy' in result

    def test_to_dict_administered_by(self):
        resource = InsurancePlan()
        resource.administeredBy = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'administeredBy' in result

    def test_to_dict_coverage_area(self):
        resource = InsurancePlan()
        resource.coverageArea = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'coverageArea' in result

    def test_to_dict_contact(self):
        resource = InsurancePlan()
        resource.contact = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_endpoint(self):
        resource = InsurancePlan()
        resource.endpoint = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'endpoint' in result

    def test_to_dict_network(self):
        resource = InsurancePlan()
        resource.network = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'network' in result

    def test_to_dict_coverage(self):
        resource = InsurancePlan()
        resource.coverage = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'coverage' in result

    def test_to_dict_plan(self):
        resource = InsurancePlan()
        resource.plan = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'plan' in result


class TestFromDictInsurancePlan:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'InsurancePlan', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert isinstance(result, InsurancePlan)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'InsurancePlan'}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert isinstance(result, InsurancePlan)

    def test_from_dict_id(self):
        data = {'resourceType': 'InsurancePlan', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'InsurancePlan', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'InsurancePlan', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'InsurancePlan', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'InsurancePlan', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'InsurancePlan', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'InsurancePlan', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'InsurancePlan', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'InsurancePlan', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'InsurancePlan', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.status is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'InsurancePlan',
         'type': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                   'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.type_ is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'InsurancePlan', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.name is not None

    def test_from_dict_alias(self):
        data = {'resourceType': 'InsurancePlan', 'alias': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.alias is not None

    def test_from_dict_period(self):
        data = {'resourceType': 'InsurancePlan', 'period': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.period is not None

    def test_from_dict_owned_by(self):
        data = {'resourceType': 'InsurancePlan', 'ownedBy': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.ownedBy is not None

    def test_from_dict_administered_by(self):
        data = {'resourceType': 'InsurancePlan', 'administeredBy': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.administeredBy is not None

    def test_from_dict_coverage_area(self):
        data = {'resourceType': 'InsurancePlan', 'coverageArea': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.coverageArea is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'InsurancePlan', 'contact': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.contact is not None

    def test_from_dict_endpoint(self):
        data = {'resourceType': 'InsurancePlan', 'endpoint': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.endpoint is not None

    def test_from_dict_network(self):
        data = {'resourceType': 'InsurancePlan', 'network': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.network is not None

    def test_from_dict_coverage(self):
        data = {'resourceType': 'InsurancePlan', 'coverage': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.coverage is not None

    def test_from_dict_plan(self):
        data = {'resourceType': 'InsurancePlan', 'plan': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, InsurancePlan)
        assert result.plan is not None


class TestGetPathInsurancePlan:

    def test_get_path_id(self):
        resource = InsurancePlan()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = InsurancePlan()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = InsurancePlan()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'InsurancePlan.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = InsurancePlan()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = InsurancePlan()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = InsurancePlan()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = InsurancePlan()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = InsurancePlan()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = InsurancePlan()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = InsurancePlan()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = InsurancePlan()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = InsurancePlan()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_type(self):
        resource = InsurancePlan()
        resource.type_ = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_name(self):
        resource = InsurancePlan()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_alias(self):
        resource = InsurancePlan()
        resource.alias = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'alias')
        assert result is not None

    def test_get_path_period(self):
        resource = InsurancePlan()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'period')
        assert result is not None

    def test_get_path_owned_by(self):
        resource = InsurancePlan()
        resource.ownedBy = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ownedBy')
        assert result is not None

    def test_get_path_administered_by(self):
        resource = InsurancePlan()
        resource.administeredBy = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'administeredBy')
        assert result is not None

    def test_get_path_coverage_area(self):
        resource = InsurancePlan()
        resource.coverageArea = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'coverageArea')
        assert result is not None

    def test_get_path_contact(self):
        resource = InsurancePlan()
        resource.contact = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_endpoint(self):
        resource = InsurancePlan()
        resource.endpoint = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'endpoint')
        assert result is not None

    def test_get_path_network(self):
        resource = InsurancePlan()
        resource.network = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'network')
        assert result is not None

    def test_get_path_coverage(self):
        resource = InsurancePlan()
        resource.coverage = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'coverage')
        assert result is not None

    def test_get_path_plan(self):
        resource = InsurancePlan()
        resource.plan = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'plan')
        assert result is not None


class TestSetPathInsurancePlan:

    def test_set_path_id(self):
        resource = InsurancePlan()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = InsurancePlan()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'InsurancePlan.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = InsurancePlan()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = InsurancePlan()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = InsurancePlan()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = InsurancePlan()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = InsurancePlan()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = InsurancePlan()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = InsurancePlan()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = InsurancePlan()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = InsurancePlan()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_type(self):
        resource = InsurancePlan()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_name(self):
        resource = InsurancePlan()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_alias(self):
        resource = InsurancePlan()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'alias', value)
        assert result is True
        assert resource.alias is not None

    def test_set_path_period(self):
        resource = InsurancePlan()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'period', value)
        assert result is True
        assert resource.period is not None

    def test_set_path_owned_by(self):
        resource = InsurancePlan()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ownedBy', value)
        assert result is True
        assert resource.ownedBy is not None

    def test_set_path_administered_by(self):
        resource = InsurancePlan()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'administeredBy', value)
        assert result is True
        assert resource.administeredBy is not None

    def test_set_path_coverage_area(self):
        resource = InsurancePlan()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'coverageArea', value)
        assert result is True
        assert resource.coverageArea is not None

    def test_set_path_contact(self):
        resource = InsurancePlan()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_endpoint(self):
        resource = InsurancePlan()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'endpoint', value)
        assert result is True
        assert resource.endpoint is not None

    def test_set_path_network(self):
        resource = InsurancePlan()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'network', value)
        assert result is True
        assert resource.network is not None

    def test_set_path_coverage(self):
        resource = InsurancePlan()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'coverage', value)
        assert result is True
        assert resource.coverage is not None

    def test_set_path_plan(self):
        resource = InsurancePlan()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'plan', value)
        assert result is True
        assert resource.plan is not None


class TestParsePathInsurancePlan:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('InsurancePlan.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('InsurancePlan.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('InsurancePlan.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
