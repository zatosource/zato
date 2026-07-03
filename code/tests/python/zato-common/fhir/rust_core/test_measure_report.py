# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import MeasureReport


class TestToDictMeasureReport:

    def test_to_dict_empty(self):
        resource = MeasureReport()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'MeasureReport'

    def test_to_dict_with_id(self):
        resource = MeasureReport()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = MeasureReport()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, MeasureReport)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = MeasureReport()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = MeasureReport()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = MeasureReport()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = MeasureReport()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = MeasureReport()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = MeasureReport()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = MeasureReport()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = MeasureReport()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = MeasureReport()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_status(self):
        resource = MeasureReport()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_type(self):
        resource = MeasureReport()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_measure(self):
        resource = MeasureReport()
        resource.measure = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'measure' in result

    def test_to_dict_subject(self):
        resource = MeasureReport()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_date(self):
        resource = MeasureReport()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_reporter(self):
        resource = MeasureReport()
        resource.reporter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reporter' in result

    def test_to_dict_period(self):
        resource = MeasureReport()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'period' in result

    def test_to_dict_improvement_notation(self):
        resource = MeasureReport()
        resource.improvementNotation = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'improvementNotation' in result

    def test_to_dict_group(self):
        resource = MeasureReport()
        resource.group = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'group' in result

    def test_to_dict_evaluated_resource(self):
        resource = MeasureReport()
        resource.evaluatedResource = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'evaluatedResource' in result


class TestFromDictMeasureReport:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'MeasureReport', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert isinstance(result, MeasureReport)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'MeasureReport'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert isinstance(result, MeasureReport)

    def test_from_dict_id(self):
        data = {'resourceType': 'MeasureReport', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'MeasureReport', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'MeasureReport', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'MeasureReport', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'MeasureReport', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'MeasureReport', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'MeasureReport', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'MeasureReport', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'MeasureReport', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.identifier is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'MeasureReport', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.status is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'MeasureReport', 'type': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.type_ is not None

    def test_from_dict_measure(self):
        data = {'resourceType': 'MeasureReport', 'measure': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.measure is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'MeasureReport', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.subject is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'MeasureReport', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.date is not None

    def test_from_dict_reporter(self):
        data = {'resourceType': 'MeasureReport', 'reporter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.reporter is not None

    def test_from_dict_period(self):
        data = {'resourceType': 'MeasureReport', 'period': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.period is not None

    def test_from_dict_improvement_notation(self):
        data = {'improvementNotation': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                 'text': 'Test concept'},
         'resourceType': 'MeasureReport'}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.improvementNotation is not None

    def test_from_dict_group(self):
        data = {'resourceType': 'MeasureReport', 'group': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.group is not None

    def test_from_dict_evaluated_resource(self):
        data = {'resourceType': 'MeasureReport', 'evaluatedResource': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, MeasureReport)
        assert result.evaluatedResource is not None


class TestGetPathMeasureReport:

    def test_get_path_id(self):
        resource = MeasureReport()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = MeasureReport()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = MeasureReport()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'MeasureReport.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = MeasureReport()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = MeasureReport()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = MeasureReport()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = MeasureReport()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = MeasureReport()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = MeasureReport()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = MeasureReport()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = MeasureReport()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_status(self):
        resource = MeasureReport()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_type(self):
        resource = MeasureReport()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_measure(self):
        resource = MeasureReport()
        resource.measure = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'measure')
        assert result is not None

    def test_get_path_subject(self):
        resource = MeasureReport()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_date(self):
        resource = MeasureReport()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_reporter(self):
        resource = MeasureReport()
        resource.reporter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reporter')
        assert result is not None

    def test_get_path_period(self):
        resource = MeasureReport()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'period')
        assert result is not None

    def test_get_path_improvement_notation(self):
        resource = MeasureReport()
        resource.improvementNotation = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'improvementNotation')
        assert result is not None

    def test_get_path_group(self):
        resource = MeasureReport()
        resource.group = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'group')
        assert result is not None

    def test_get_path_evaluated_resource(self):
        resource = MeasureReport()
        resource.evaluatedResource = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'evaluatedResource')
        assert result is not None


class TestSetPathMeasureReport:

    def test_set_path_id(self):
        resource = MeasureReport()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = MeasureReport()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'MeasureReport.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = MeasureReport()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = MeasureReport()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = MeasureReport()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = MeasureReport()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = MeasureReport()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = MeasureReport()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = MeasureReport()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = MeasureReport()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_status(self):
        resource = MeasureReport()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_type(self):
        resource = MeasureReport()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_measure(self):
        resource = MeasureReport()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'measure', value)
        assert result is True
        assert resource.measure is not None

    def test_set_path_subject(self):
        resource = MeasureReport()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_date(self):
        resource = MeasureReport()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_reporter(self):
        resource = MeasureReport()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reporter', value)
        assert result is True
        assert resource.reporter is not None

    def test_set_path_period(self):
        resource = MeasureReport()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'period', value)
        assert result is True
        assert resource.period is not None

    def test_set_path_improvement_notation(self):
        resource = MeasureReport()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'improvementNotation', value)
        assert result is True
        assert resource.improvementNotation is not None

    def test_set_path_group(self):
        resource = MeasureReport()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'group', value)
        assert result is True
        assert resource.group is not None

    def test_set_path_evaluated_resource(self):
        resource = MeasureReport()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'evaluatedResource', value)
        assert result is True
        assert resource.evaluatedResource is not None


class TestParsePathMeasureReport:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('MeasureReport.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('MeasureReport.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('MeasureReport.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
