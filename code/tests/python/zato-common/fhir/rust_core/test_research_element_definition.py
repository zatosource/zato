# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ResearchElementDefinition


class TestToDictResearchElementDefinition:

    def test_to_dict_empty(self):
        resource = ResearchElementDefinition()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ResearchElementDefinition'

    def test_to_dict_with_id(self):
        resource = ResearchElementDefinition()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ResearchElementDefinition()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ResearchElementDefinition)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ResearchElementDefinition()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ResearchElementDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ResearchElementDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ResearchElementDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ResearchElementDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ResearchElementDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ResearchElementDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ResearchElementDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = ResearchElementDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_identifier(self):
        resource = ResearchElementDefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_version(self):
        resource = ResearchElementDefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = ResearchElementDefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = ResearchElementDefinition()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_short_title(self):
        resource = ResearchElementDefinition()
        resource.shortTitle = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'shortTitle' in result

    def test_to_dict_subtitle(self):
        resource = ResearchElementDefinition()
        resource.subtitle = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subtitle' in result

    def test_to_dict_status(self):
        resource = ResearchElementDefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = ResearchElementDefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = ResearchElementDefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = ResearchElementDefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = ResearchElementDefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = ResearchElementDefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_comment(self):
        resource = ResearchElementDefinition()
        resource.comment = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'comment' in result

    def test_to_dict_use_context(self):
        resource = ResearchElementDefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = ResearchElementDefinition()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_purpose(self):
        resource = ResearchElementDefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_usage(self):
        resource = ResearchElementDefinition()
        resource.usage = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'usage' in result

    def test_to_dict_copyright(self):
        resource = ResearchElementDefinition()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_approval_date(self):
        resource = ResearchElementDefinition()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'approvalDate' in result

    def test_to_dict_last_review_date(self):
        resource = ResearchElementDefinition()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lastReviewDate' in result

    def test_to_dict_effective_period(self):
        resource = ResearchElementDefinition()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'effectivePeriod' in result

    def test_to_dict_topic(self):
        resource = ResearchElementDefinition()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'topic' in result

    def test_to_dict_author(self):
        resource = ResearchElementDefinition()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_editor(self):
        resource = ResearchElementDefinition()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'editor' in result

    def test_to_dict_reviewer(self):
        resource = ResearchElementDefinition()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reviewer' in result

    def test_to_dict_endorser(self):
        resource = ResearchElementDefinition()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'endorser' in result

    def test_to_dict_related_artifact(self):
        resource = ResearchElementDefinition()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relatedArtifact' in result

    def test_to_dict_library(self):
        resource = ResearchElementDefinition()
        resource.library = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'library' in result

    def test_to_dict_type(self):
        resource = ResearchElementDefinition()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_variable_type(self):
        resource = ResearchElementDefinition()
        resource.variableType = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'variableType' in result

    def test_to_dict_characteristic(self):
        resource = ResearchElementDefinition()
        resource.characteristic = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'characteristic' in result


class TestFromDictResearchElementDefinition:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ResearchElementDefinition', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert isinstance(result, ResearchElementDefinition)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ResearchElementDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert isinstance(result, ResearchElementDefinition)

    def test_from_dict_id(self):
        data = {'resourceType': 'ResearchElementDefinition', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ResearchElementDefinition', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ResearchElementDefinition', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ResearchElementDefinition', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ResearchElementDefinition', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ResearchElementDefinition', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ResearchElementDefinition', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ResearchElementDefinition', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'ResearchElementDefinition', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.url is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'ResearchElementDefinition', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.identifier is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'ResearchElementDefinition', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'ResearchElementDefinition', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'ResearchElementDefinition', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.title is not None

    def test_from_dict_short_title(self):
        data = {'resourceType': 'ResearchElementDefinition', 'shortTitle': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.shortTitle is not None

    def test_from_dict_subtitle(self):
        data = {'resourceType': 'ResearchElementDefinition', 'subtitle': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.subtitle is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'ResearchElementDefinition', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'ResearchElementDefinition', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'ResearchElementDefinition', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'ResearchElementDefinition', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'ResearchElementDefinition', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'ResearchElementDefinition', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.description is not None

    def test_from_dict_comment(self):
        data = {'resourceType': 'ResearchElementDefinition', 'comment': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.comment is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'ResearchElementDefinition', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'ResearchElementDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.jurisdiction is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'ResearchElementDefinition', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.purpose is not None

    def test_from_dict_usage(self):
        data = {'resourceType': 'ResearchElementDefinition', 'usage': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.usage is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'ResearchElementDefinition', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.copyright is not None

    def test_from_dict_approval_date(self):
        data = {'resourceType': 'ResearchElementDefinition', 'approvalDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.approvalDate is not None

    def test_from_dict_last_review_date(self):
        data = {'resourceType': 'ResearchElementDefinition', 'lastReviewDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.lastReviewDate is not None

    def test_from_dict_effective_period(self):
        data = {'resourceType': 'ResearchElementDefinition', 'effectivePeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.effectivePeriod is not None

    def test_from_dict_topic(self):
        data = {'resourceType': 'ResearchElementDefinition',
         'topic': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.topic is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'ResearchElementDefinition', 'author': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.author is not None

    def test_from_dict_editor(self):
        data = {'resourceType': 'ResearchElementDefinition', 'editor': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.editor is not None

    def test_from_dict_reviewer(self):
        data = {'resourceType': 'ResearchElementDefinition', 'reviewer': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.reviewer is not None

    def test_from_dict_endorser(self):
        data = {'resourceType': 'ResearchElementDefinition', 'endorser': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.endorser is not None

    def test_from_dict_related_artifact(self):
        data = {'resourceType': 'ResearchElementDefinition', 'relatedArtifact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.relatedArtifact is not None

    def test_from_dict_library(self):
        data = {'resourceType': 'ResearchElementDefinition', 'library': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.library is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'ResearchElementDefinition', 'type': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.type_ is not None

    def test_from_dict_variable_type(self):
        data = {'resourceType': 'ResearchElementDefinition', 'variableType': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.variableType is not None

    def test_from_dict_characteristic(self):
        data = {'resourceType': 'ResearchElementDefinition', 'characteristic': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchElementDefinition)
        assert result.characteristic is not None


class TestGetPathResearchElementDefinition:

    def test_get_path_id(self):
        resource = ResearchElementDefinition()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ResearchElementDefinition()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ResearchElementDefinition()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ResearchElementDefinition.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ResearchElementDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ResearchElementDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ResearchElementDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ResearchElementDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ResearchElementDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ResearchElementDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ResearchElementDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = ResearchElementDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_identifier(self):
        resource = ResearchElementDefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_version(self):
        resource = ResearchElementDefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = ResearchElementDefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = ResearchElementDefinition()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_short_title(self):
        resource = ResearchElementDefinition()
        resource.shortTitle = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'shortTitle')
        assert result is not None

    def test_get_path_subtitle(self):
        resource = ResearchElementDefinition()
        resource.subtitle = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subtitle')
        assert result is not None

    def test_get_path_status(self):
        resource = ResearchElementDefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = ResearchElementDefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = ResearchElementDefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = ResearchElementDefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = ResearchElementDefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = ResearchElementDefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_comment(self):
        resource = ResearchElementDefinition()
        resource.comment = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'comment')
        assert result is not None

    def test_get_path_use_context(self):
        resource = ResearchElementDefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = ResearchElementDefinition()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_purpose(self):
        resource = ResearchElementDefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_usage(self):
        resource = ResearchElementDefinition()
        resource.usage = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'usage')
        assert result is not None

    def test_get_path_copyright(self):
        resource = ResearchElementDefinition()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_approval_date(self):
        resource = ResearchElementDefinition()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'approvalDate')
        assert result is not None

    def test_get_path_last_review_date(self):
        resource = ResearchElementDefinition()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lastReviewDate')
        assert result is not None

    def test_get_path_effective_period(self):
        resource = ResearchElementDefinition()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'effectivePeriod')
        assert result is not None

    def test_get_path_topic(self):
        resource = ResearchElementDefinition()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'topic')
        assert result is not None

    def test_get_path_author(self):
        resource = ResearchElementDefinition()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_editor(self):
        resource = ResearchElementDefinition()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'editor')
        assert result is not None

    def test_get_path_reviewer(self):
        resource = ResearchElementDefinition()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reviewer')
        assert result is not None

    def test_get_path_endorser(self):
        resource = ResearchElementDefinition()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'endorser')
        assert result is not None

    def test_get_path_related_artifact(self):
        resource = ResearchElementDefinition()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relatedArtifact')
        assert result is not None

    def test_get_path_library(self):
        resource = ResearchElementDefinition()
        resource.library = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'library')
        assert result is not None

    def test_get_path_type(self):
        resource = ResearchElementDefinition()
        resource.type_ = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_variable_type(self):
        resource = ResearchElementDefinition()
        resource.variableType = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'variableType')
        assert result is not None

    def test_get_path_characteristic(self):
        resource = ResearchElementDefinition()
        resource.characteristic = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'characteristic')
        assert result is not None


class TestSetPathResearchElementDefinition:

    def test_set_path_id(self):
        resource = ResearchElementDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ResearchElementDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ResearchElementDefinition.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ResearchElementDefinition()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ResearchElementDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ResearchElementDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ResearchElementDefinition()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ResearchElementDefinition()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ResearchElementDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ResearchElementDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = ResearchElementDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_identifier(self):
        resource = ResearchElementDefinition()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_version(self):
        resource = ResearchElementDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = ResearchElementDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = ResearchElementDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_short_title(self):
        resource = ResearchElementDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'shortTitle', value)
        assert result is True
        assert resource.shortTitle is not None

    def test_set_path_subtitle(self):
        resource = ResearchElementDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subtitle', value)
        assert result is True
        assert resource.subtitle is not None

    def test_set_path_status(self):
        resource = ResearchElementDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = ResearchElementDefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = ResearchElementDefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = ResearchElementDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = ResearchElementDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = ResearchElementDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_comment(self):
        resource = ResearchElementDefinition()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'comment', value)
        assert result is True
        assert resource.comment is not None

    def test_set_path_use_context(self):
        resource = ResearchElementDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = ResearchElementDefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_purpose(self):
        resource = ResearchElementDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_usage(self):
        resource = ResearchElementDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'usage', value)
        assert result is True
        assert resource.usage is not None

    def test_set_path_copyright(self):
        resource = ResearchElementDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_approval_date(self):
        resource = ResearchElementDefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'approvalDate', value)
        assert result is True
        assert resource.approvalDate is not None

    def test_set_path_last_review_date(self):
        resource = ResearchElementDefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lastReviewDate', value)
        assert result is True
        assert resource.lastReviewDate is not None

    def test_set_path_effective_period(self):
        resource = ResearchElementDefinition()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'effectivePeriod', value)
        assert result is True
        assert resource.effectivePeriod is not None

    def test_set_path_topic(self):
        resource = ResearchElementDefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'topic', value)
        assert result is True
        assert resource.topic is not None

    def test_set_path_author(self):
        resource = ResearchElementDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_editor(self):
        resource = ResearchElementDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'editor', value)
        assert result is True
        assert resource.editor is not None

    def test_set_path_reviewer(self):
        resource = ResearchElementDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reviewer', value)
        assert result is True
        assert resource.reviewer is not None

    def test_set_path_endorser(self):
        resource = ResearchElementDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'endorser', value)
        assert result is True
        assert resource.endorser is not None

    def test_set_path_related_artifact(self):
        resource = ResearchElementDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relatedArtifact', value)
        assert result is True
        assert resource.relatedArtifact is not None

    def test_set_path_library(self):
        resource = ResearchElementDefinition()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'library', value)
        assert result is True
        assert resource.library is not None

    def test_set_path_type(self):
        resource = ResearchElementDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_variable_type(self):
        resource = ResearchElementDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'variableType', value)
        assert result is True
        assert resource.variableType is not None

    def test_set_path_characteristic(self):
        resource = ResearchElementDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'characteristic', value)
        assert result is True
        assert resource.characteristic is not None


class TestParsePathResearchElementDefinition:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ResearchElementDefinition.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ResearchElementDefinition.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ResearchElementDefinition.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
