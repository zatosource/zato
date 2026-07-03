# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import SearchParameter


class TestToDictSearchParameter:

    def test_to_dict_empty(self):
        resource = SearchParameter()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'SearchParameter'

    def test_to_dict_with_id(self):
        resource = SearchParameter()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = SearchParameter()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, SearchParameter)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = SearchParameter()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = SearchParameter()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = SearchParameter()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = SearchParameter()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = SearchParameter()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = SearchParameter()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = SearchParameter()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = SearchParameter()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = SearchParameter()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_version(self):
        resource = SearchParameter()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = SearchParameter()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_derived_from(self):
        resource = SearchParameter()
        resource.derivedFrom = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'derivedFrom' in result

    def test_to_dict_status(self):
        resource = SearchParameter()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = SearchParameter()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = SearchParameter()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = SearchParameter()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = SearchParameter()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = SearchParameter()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = SearchParameter()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = SearchParameter()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_purpose(self):
        resource = SearchParameter()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_code(self):
        resource = SearchParameter()
        resource.code = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_base(self):
        resource = SearchParameter()
        resource.base = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'base' in result

    def test_to_dict_type(self):
        resource = SearchParameter()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_expression(self):
        resource = SearchParameter()
        resource.expression = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'expression' in result

    def test_to_dict_xpath(self):
        resource = SearchParameter()
        resource.xpath = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'xpath' in result

    def test_to_dict_xpath_usage(self):
        resource = SearchParameter()
        resource.xpathUsage = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'xpathUsage' in result

    def test_to_dict_target(self):
        resource = SearchParameter()
        resource.target = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'target' in result

    def test_to_dict_multiple_or(self):
        resource = SearchParameter()
        resource.multipleOr = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'multipleOr' in result

    def test_to_dict_multiple_and(self):
        resource = SearchParameter()
        resource.multipleAnd = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'multipleAnd' in result

    def test_to_dict_comparator(self):
        resource = SearchParameter()
        resource.comparator = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'comparator' in result

    def test_to_dict_modifier(self):
        resource = SearchParameter()
        resource.modifier = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifier' in result

    def test_to_dict_chain(self):
        resource = SearchParameter()
        resource.chain = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'chain' in result

    def test_to_dict_component(self):
        resource = SearchParameter()
        resource.component = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'component' in result


class TestFromDictSearchParameter:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'SearchParameter', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert isinstance(result, SearchParameter)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'SearchParameter'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert isinstance(result, SearchParameter)

    def test_from_dict_id(self):
        data = {'resourceType': 'SearchParameter', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'SearchParameter', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'SearchParameter', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'SearchParameter', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'SearchParameter', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'SearchParameter', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'SearchParameter', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'SearchParameter', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'SearchParameter', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.url is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'SearchParameter', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'SearchParameter', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.name is not None

    def test_from_dict_derived_from(self):
        data = {'resourceType': 'SearchParameter', 'derivedFrom': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.derivedFrom is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'SearchParameter', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'SearchParameter', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'SearchParameter', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'SearchParameter', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'SearchParameter', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'SearchParameter', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'SearchParameter', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'SearchParameter'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.jurisdiction is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'SearchParameter', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.purpose is not None

    def test_from_dict_code(self):
        data = {'resourceType': 'SearchParameter', 'code': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.code is not None

    def test_from_dict_base(self):
        data = {'resourceType': 'SearchParameter', 'base': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.base is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'SearchParameter', 'type': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.type_ is not None

    def test_from_dict_expression(self):
        data = {'resourceType': 'SearchParameter', 'expression': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.expression is not None

    def test_from_dict_xpath(self):
        data = {'resourceType': 'SearchParameter', 'xpath': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.xpath is not None

    def test_from_dict_xpath_usage(self):
        data = {'resourceType': 'SearchParameter', 'xpathUsage': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.xpathUsage is not None

    def test_from_dict_target(self):
        data = {'resourceType': 'SearchParameter', 'target': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.target is not None

    def test_from_dict_multiple_or(self):
        data = {'resourceType': 'SearchParameter', 'multipleOr': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.multipleOr is not None

    def test_from_dict_multiple_and(self):
        data = {'resourceType': 'SearchParameter', 'multipleAnd': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.multipleAnd is not None

    def test_from_dict_comparator(self):
        data = {'resourceType': 'SearchParameter', 'comparator': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.comparator is not None

    def test_from_dict_modifier(self):
        data = {'resourceType': 'SearchParameter', 'modifier': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.modifier is not None

    def test_from_dict_chain(self):
        data = {'resourceType': 'SearchParameter', 'chain': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.chain is not None

    def test_from_dict_component(self):
        data = {'resourceType': 'SearchParameter', 'component': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, SearchParameter)
        assert result.component is not None


class TestGetPathSearchParameter:

    def test_get_path_id(self):
        resource = SearchParameter()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = SearchParameter()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = SearchParameter()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'SearchParameter.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = SearchParameter()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = SearchParameter()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = SearchParameter()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = SearchParameter()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = SearchParameter()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = SearchParameter()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = SearchParameter()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = SearchParameter()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_version(self):
        resource = SearchParameter()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = SearchParameter()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_derived_from(self):
        resource = SearchParameter()
        resource.derivedFrom = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'derivedFrom')
        assert result is not None

    def test_get_path_status(self):
        resource = SearchParameter()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = SearchParameter()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = SearchParameter()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = SearchParameter()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = SearchParameter()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = SearchParameter()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = SearchParameter()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = SearchParameter()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_purpose(self):
        resource = SearchParameter()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_code(self):
        resource = SearchParameter()
        resource.code = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_base(self):
        resource = SearchParameter()
        resource.base = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'base')
        assert result is not None

    def test_get_path_type(self):
        resource = SearchParameter()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_expression(self):
        resource = SearchParameter()
        resource.expression = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'expression')
        assert result is not None

    def test_get_path_xpath(self):
        resource = SearchParameter()
        resource.xpath = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'xpath')
        assert result is not None

    def test_get_path_xpath_usage(self):
        resource = SearchParameter()
        resource.xpathUsage = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'xpathUsage')
        assert result is not None

    def test_get_path_target(self):
        resource = SearchParameter()
        resource.target = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'target')
        assert result is not None

    def test_get_path_multiple_or(self):
        resource = SearchParameter()
        resource.multipleOr = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'multipleOr')
        assert result is not None

    def test_get_path_multiple_and(self):
        resource = SearchParameter()
        resource.multipleAnd = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'multipleAnd')
        assert result is not None

    def test_get_path_comparator(self):
        resource = SearchParameter()
        resource.comparator = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'comparator')
        assert result is not None

    def test_get_path_modifier(self):
        resource = SearchParameter()
        resource.modifier = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifier')
        assert result is not None

    def test_get_path_chain(self):
        resource = SearchParameter()
        resource.chain = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'chain')
        assert result is not None

    def test_get_path_component(self):
        resource = SearchParameter()
        resource.component = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'component')
        assert result is not None


class TestSetPathSearchParameter:

    def test_set_path_id(self):
        resource = SearchParameter()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = SearchParameter()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'SearchParameter.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = SearchParameter()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = SearchParameter()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = SearchParameter()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = SearchParameter()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = SearchParameter()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = SearchParameter()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = SearchParameter()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = SearchParameter()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_version(self):
        resource = SearchParameter()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = SearchParameter()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_derived_from(self):
        resource = SearchParameter()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'derivedFrom', value)
        assert result is True
        assert resource.derivedFrom is not None

    def test_set_path_status(self):
        resource = SearchParameter()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = SearchParameter()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = SearchParameter()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = SearchParameter()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = SearchParameter()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = SearchParameter()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = SearchParameter()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = SearchParameter()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_purpose(self):
        resource = SearchParameter()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_code(self):
        resource = SearchParameter()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_base(self):
        resource = SearchParameter()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'base', value)
        assert result is True
        assert resource.base is not None

    def test_set_path_type(self):
        resource = SearchParameter()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_expression(self):
        resource = SearchParameter()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'expression', value)
        assert result is True
        assert resource.expression is not None

    def test_set_path_xpath(self):
        resource = SearchParameter()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'xpath', value)
        assert result is True
        assert resource.xpath is not None

    def test_set_path_xpath_usage(self):
        resource = SearchParameter()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'xpathUsage', value)
        assert result is True
        assert resource.xpathUsage is not None

    def test_set_path_target(self):
        resource = SearchParameter()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'target', value)
        assert result is True
        assert resource.target is not None

    def test_set_path_multiple_or(self):
        resource = SearchParameter()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'multipleOr', value)
        assert result is True
        assert resource.multipleOr is not None

    def test_set_path_multiple_and(self):
        resource = SearchParameter()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'multipleAnd', value)
        assert result is True
        assert resource.multipleAnd is not None

    def test_set_path_comparator(self):
        resource = SearchParameter()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'comparator', value)
        assert result is True
        assert resource.comparator is not None

    def test_set_path_modifier(self):
        resource = SearchParameter()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifier', value)
        assert result is True
        assert resource.modifier is not None

    def test_set_path_chain(self):
        resource = SearchParameter()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'chain', value)
        assert result is True
        assert resource.chain is not None

    def test_set_path_component(self):
        resource = SearchParameter()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'component', value)
        assert result is True
        assert resource.component is not None


class TestParsePathSearchParameter:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('SearchParameter.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('SearchParameter.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('SearchParameter.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
