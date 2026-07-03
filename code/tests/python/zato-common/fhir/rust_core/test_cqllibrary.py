# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import cqllibrary


class TestToDictcqllibrary:

    def test_to_dict_empty(self):
        resource = cqllibrary()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'cqllibrary'

    def test_to_dict_with_id(self):
        resource = cqllibrary()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = cqllibrary()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, cqllibrary)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = cqllibrary()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = cqllibrary()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = cqllibrary()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = cqllibrary()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = cqllibrary()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = cqllibrary()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = cqllibrary()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = cqllibrary()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = cqllibrary()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_identifier(self):
        resource = cqllibrary()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_version(self):
        resource = cqllibrary()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = cqllibrary()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = cqllibrary()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_subtitle(self):
        resource = cqllibrary()
        resource.subtitle = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subtitle' in result

    def test_to_dict_status(self):
        resource = cqllibrary()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = cqllibrary()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_type(self):
        resource = cqllibrary()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_date(self):
        resource = cqllibrary()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = cqllibrary()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = cqllibrary()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = cqllibrary()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = cqllibrary()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = cqllibrary()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_purpose(self):
        resource = cqllibrary()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_usage(self):
        resource = cqllibrary()
        resource.usage = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'usage' in result

    def test_to_dict_copyright(self):
        resource = cqllibrary()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_approval_date(self):
        resource = cqllibrary()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'approvalDate' in result

    def test_to_dict_last_review_date(self):
        resource = cqllibrary()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lastReviewDate' in result

    def test_to_dict_effective_period(self):
        resource = cqllibrary()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'effectivePeriod' in result

    def test_to_dict_topic(self):
        resource = cqllibrary()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'topic' in result

    def test_to_dict_author(self):
        resource = cqllibrary()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_editor(self):
        resource = cqllibrary()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'editor' in result

    def test_to_dict_reviewer(self):
        resource = cqllibrary()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reviewer' in result

    def test_to_dict_endorser(self):
        resource = cqllibrary()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'endorser' in result

    def test_to_dict_related_artifact(self):
        resource = cqllibrary()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relatedArtifact' in result

    def test_to_dict_parameter(self):
        resource = cqllibrary()
        resource.parameter = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'parameter' in result

    def test_to_dict_data_requirement(self):
        resource = cqllibrary()
        resource.dataRequirement = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dataRequirement' in result

    def test_to_dict_content(self):
        resource = cqllibrary()
        resource.content = [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'content' in result


class TestFromDictcqllibrary:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'cqllibrary', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert isinstance(result, cqllibrary)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'cqllibrary'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert isinstance(result, cqllibrary)

    def test_from_dict_id(self):
        data = {'resourceType': 'cqllibrary', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'cqllibrary', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'cqllibrary', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'cqllibrary', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'cqllibrary', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'cqllibrary', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'cqllibrary', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'cqllibrary', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'cqllibrary', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.url is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'cqllibrary', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.identifier is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'cqllibrary', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'cqllibrary', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'cqllibrary', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.title is not None

    def test_from_dict_subtitle(self):
        data = {'resourceType': 'cqllibrary', 'subtitle': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.subtitle is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'cqllibrary', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'cqllibrary', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.experimental is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'cqllibrary',
         'type': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.type_ is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'cqllibrary', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'cqllibrary', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'cqllibrary', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'cqllibrary', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'cqllibrary', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'cqllibrary'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.jurisdiction is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'cqllibrary', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.purpose is not None

    def test_from_dict_usage(self):
        data = {'resourceType': 'cqllibrary', 'usage': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.usage is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'cqllibrary', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.copyright is not None

    def test_from_dict_approval_date(self):
        data = {'resourceType': 'cqllibrary', 'approvalDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.approvalDate is not None

    def test_from_dict_last_review_date(self):
        data = {'resourceType': 'cqllibrary', 'lastReviewDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.lastReviewDate is not None

    def test_from_dict_effective_period(self):
        data = {'resourceType': 'cqllibrary', 'effectivePeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.effectivePeriod is not None

    def test_from_dict_topic(self):
        data = {'resourceType': 'cqllibrary',
         'topic': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.topic is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'cqllibrary', 'author': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.author is not None

    def test_from_dict_editor(self):
        data = {'resourceType': 'cqllibrary', 'editor': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.editor is not None

    def test_from_dict_reviewer(self):
        data = {'resourceType': 'cqllibrary', 'reviewer': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.reviewer is not None

    def test_from_dict_endorser(self):
        data = {'resourceType': 'cqllibrary', 'endorser': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.endorser is not None

    def test_from_dict_related_artifact(self):
        data = {'resourceType': 'cqllibrary', 'relatedArtifact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.relatedArtifact is not None

    def test_from_dict_parameter(self):
        data = {'resourceType': 'cqllibrary', 'parameter': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.parameter is not None

    def test_from_dict_data_requirement(self):
        data = {'resourceType': 'cqllibrary', 'dataRequirement': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.dataRequirement is not None

    def test_from_dict_content(self):
        data = {'resourceType': 'cqllibrary', 'content': [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, cqllibrary)
        assert result.content is not None


class TestGetPathcqllibrary:

    def test_get_path_id(self):
        resource = cqllibrary()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = cqllibrary()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = cqllibrary()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'cqllibrary.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = cqllibrary()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = cqllibrary()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = cqllibrary()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = cqllibrary()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = cqllibrary()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = cqllibrary()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = cqllibrary()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = cqllibrary()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_identifier(self):
        resource = cqllibrary()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_version(self):
        resource = cqllibrary()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = cqllibrary()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = cqllibrary()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_subtitle(self):
        resource = cqllibrary()
        resource.subtitle = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subtitle')
        assert result is not None

    def test_get_path_status(self):
        resource = cqllibrary()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = cqllibrary()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_type(self):
        resource = cqllibrary()
        resource.type_ = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_date(self):
        resource = cqllibrary()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = cqllibrary()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = cqllibrary()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = cqllibrary()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = cqllibrary()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = cqllibrary()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_purpose(self):
        resource = cqllibrary()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_usage(self):
        resource = cqllibrary()
        resource.usage = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'usage')
        assert result is not None

    def test_get_path_copyright(self):
        resource = cqllibrary()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_approval_date(self):
        resource = cqllibrary()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'approvalDate')
        assert result is not None

    def test_get_path_last_review_date(self):
        resource = cqllibrary()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lastReviewDate')
        assert result is not None

    def test_get_path_effective_period(self):
        resource = cqllibrary()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'effectivePeriod')
        assert result is not None

    def test_get_path_topic(self):
        resource = cqllibrary()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'topic')
        assert result is not None

    def test_get_path_author(self):
        resource = cqllibrary()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_editor(self):
        resource = cqllibrary()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'editor')
        assert result is not None

    def test_get_path_reviewer(self):
        resource = cqllibrary()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reviewer')
        assert result is not None

    def test_get_path_endorser(self):
        resource = cqllibrary()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'endorser')
        assert result is not None

    def test_get_path_related_artifact(self):
        resource = cqllibrary()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relatedArtifact')
        assert result is not None

    def test_get_path_parameter(self):
        resource = cqllibrary()
        resource.parameter = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'parameter')
        assert result is not None

    def test_get_path_data_requirement(self):
        resource = cqllibrary()
        resource.dataRequirement = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dataRequirement')
        assert result is not None

    def test_get_path_content(self):
        resource = cqllibrary()
        resource.content = [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'content')
        assert result is not None


class TestSetPathcqllibrary:

    def test_set_path_id(self):
        resource = cqllibrary()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = cqllibrary()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'cqllibrary.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = cqllibrary()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = cqllibrary()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = cqllibrary()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = cqllibrary()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = cqllibrary()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = cqllibrary()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = cqllibrary()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = cqllibrary()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_identifier(self):
        resource = cqllibrary()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_version(self):
        resource = cqllibrary()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = cqllibrary()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = cqllibrary()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_subtitle(self):
        resource = cqllibrary()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subtitle', value)
        assert result is True
        assert resource.subtitle is not None

    def test_set_path_status(self):
        resource = cqllibrary()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = cqllibrary()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_type(self):
        resource = cqllibrary()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_date(self):
        resource = cqllibrary()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = cqllibrary()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = cqllibrary()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = cqllibrary()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = cqllibrary()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = cqllibrary()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_purpose(self):
        resource = cqllibrary()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_usage(self):
        resource = cqllibrary()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'usage', value)
        assert result is True
        assert resource.usage is not None

    def test_set_path_copyright(self):
        resource = cqllibrary()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_approval_date(self):
        resource = cqllibrary()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'approvalDate', value)
        assert result is True
        assert resource.approvalDate is not None

    def test_set_path_last_review_date(self):
        resource = cqllibrary()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lastReviewDate', value)
        assert result is True
        assert resource.lastReviewDate is not None

    def test_set_path_effective_period(self):
        resource = cqllibrary()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'effectivePeriod', value)
        assert result is True
        assert resource.effectivePeriod is not None

    def test_set_path_topic(self):
        resource = cqllibrary()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'topic', value)
        assert result is True
        assert resource.topic is not None

    def test_set_path_author(self):
        resource = cqllibrary()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_editor(self):
        resource = cqllibrary()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'editor', value)
        assert result is True
        assert resource.editor is not None

    def test_set_path_reviewer(self):
        resource = cqllibrary()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reviewer', value)
        assert result is True
        assert resource.reviewer is not None

    def test_set_path_endorser(self):
        resource = cqllibrary()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'endorser', value)
        assert result is True
        assert resource.endorser is not None

    def test_set_path_related_artifact(self):
        resource = cqllibrary()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relatedArtifact', value)
        assert result is True
        assert resource.relatedArtifact is not None

    def test_set_path_parameter(self):
        resource = cqllibrary()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'parameter', value)
        assert result is True
        assert resource.parameter is not None

    def test_set_path_data_requirement(self):
        resource = cqllibrary()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dataRequirement', value)
        assert result is True
        assert resource.dataRequirement is not None

    def test_set_path_content(self):
        resource = cqllibrary()
        value = [{'contentType': 'text/plain', 'data': 'SGVsbG8='}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'content', value)
        assert result is True
        assert resource.content is not None


class TestParsePathcqllibrary:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('cqllibrary.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('cqllibrary.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('cqllibrary.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
