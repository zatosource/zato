# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ResearchDefinition


class TestToDictResearchDefinition:

    def test_to_dict_empty(self):
        resource = ResearchDefinition()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ResearchDefinition'

    def test_to_dict_with_id(self):
        resource = ResearchDefinition()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ResearchDefinition()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ResearchDefinition)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ResearchDefinition()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ResearchDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ResearchDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ResearchDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ResearchDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ResearchDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ResearchDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ResearchDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = ResearchDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_identifier(self):
        resource = ResearchDefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_version(self):
        resource = ResearchDefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = ResearchDefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = ResearchDefinition()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_short_title(self):
        resource = ResearchDefinition()
        resource.shortTitle = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'shortTitle' in result

    def test_to_dict_subtitle(self):
        resource = ResearchDefinition()
        resource.subtitle = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subtitle' in result

    def test_to_dict_status(self):
        resource = ResearchDefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = ResearchDefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = ResearchDefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = ResearchDefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = ResearchDefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = ResearchDefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_comment(self):
        resource = ResearchDefinition()
        resource.comment = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'comment' in result

    def test_to_dict_use_context(self):
        resource = ResearchDefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = ResearchDefinition()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_purpose(self):
        resource = ResearchDefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_usage(self):
        resource = ResearchDefinition()
        resource.usage = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'usage' in result

    def test_to_dict_copyright(self):
        resource = ResearchDefinition()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_approval_date(self):
        resource = ResearchDefinition()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'approvalDate' in result

    def test_to_dict_last_review_date(self):
        resource = ResearchDefinition()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lastReviewDate' in result

    def test_to_dict_effective_period(self):
        resource = ResearchDefinition()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'effectivePeriod' in result

    def test_to_dict_topic(self):
        resource = ResearchDefinition()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'topic' in result

    def test_to_dict_author(self):
        resource = ResearchDefinition()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_editor(self):
        resource = ResearchDefinition()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'editor' in result

    def test_to_dict_reviewer(self):
        resource = ResearchDefinition()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reviewer' in result

    def test_to_dict_endorser(self):
        resource = ResearchDefinition()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'endorser' in result

    def test_to_dict_related_artifact(self):
        resource = ResearchDefinition()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relatedArtifact' in result

    def test_to_dict_library(self):
        resource = ResearchDefinition()
        resource.library = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'library' in result

    def test_to_dict_population(self):
        resource = ResearchDefinition()
        resource.population = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'population' in result

    def test_to_dict_exposure(self):
        resource = ResearchDefinition()
        resource.exposure = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'exposure' in result

    def test_to_dict_exposure_alternative(self):
        resource = ResearchDefinition()
        resource.exposureAlternative = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'exposureAlternative' in result

    def test_to_dict_outcome(self):
        resource = ResearchDefinition()
        resource.outcome = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'outcome' in result


class TestFromDictResearchDefinition:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ResearchDefinition', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert isinstance(result, ResearchDefinition)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ResearchDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert isinstance(result, ResearchDefinition)

    def test_from_dict_id(self):
        data = {'resourceType': 'ResearchDefinition', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ResearchDefinition', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ResearchDefinition', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ResearchDefinition', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ResearchDefinition', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ResearchDefinition', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ResearchDefinition', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ResearchDefinition', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'ResearchDefinition', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.url is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'ResearchDefinition', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.identifier is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'ResearchDefinition', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'ResearchDefinition', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'ResearchDefinition', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.title is not None

    def test_from_dict_short_title(self):
        data = {'resourceType': 'ResearchDefinition', 'shortTitle': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.shortTitle is not None

    def test_from_dict_subtitle(self):
        data = {'resourceType': 'ResearchDefinition', 'subtitle': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.subtitle is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'ResearchDefinition', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'ResearchDefinition', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'ResearchDefinition', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'ResearchDefinition', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'ResearchDefinition', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'ResearchDefinition', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.description is not None

    def test_from_dict_comment(self):
        data = {'resourceType': 'ResearchDefinition', 'comment': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.comment is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'ResearchDefinition', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'ResearchDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.jurisdiction is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'ResearchDefinition', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.purpose is not None

    def test_from_dict_usage(self):
        data = {'resourceType': 'ResearchDefinition', 'usage': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.usage is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'ResearchDefinition', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.copyright is not None

    def test_from_dict_approval_date(self):
        data = {'resourceType': 'ResearchDefinition', 'approvalDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.approvalDate is not None

    def test_from_dict_last_review_date(self):
        data = {'resourceType': 'ResearchDefinition', 'lastReviewDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.lastReviewDate is not None

    def test_from_dict_effective_period(self):
        data = {'resourceType': 'ResearchDefinition', 'effectivePeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.effectivePeriod is not None

    def test_from_dict_topic(self):
        data = {'resourceType': 'ResearchDefinition',
         'topic': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.topic is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'ResearchDefinition', 'author': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.author is not None

    def test_from_dict_editor(self):
        data = {'resourceType': 'ResearchDefinition', 'editor': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.editor is not None

    def test_from_dict_reviewer(self):
        data = {'resourceType': 'ResearchDefinition', 'reviewer': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.reviewer is not None

    def test_from_dict_endorser(self):
        data = {'resourceType': 'ResearchDefinition', 'endorser': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.endorser is not None

    def test_from_dict_related_artifact(self):
        data = {'resourceType': 'ResearchDefinition', 'relatedArtifact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.relatedArtifact is not None

    def test_from_dict_library(self):
        data = {'resourceType': 'ResearchDefinition', 'library': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.library is not None

    def test_from_dict_population(self):
        data = {'resourceType': 'ResearchDefinition', 'population': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.population is not None

    def test_from_dict_exposure(self):
        data = {'resourceType': 'ResearchDefinition', 'exposure': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.exposure is not None

    def test_from_dict_exposure_alternative(self):
        data = {'resourceType': 'ResearchDefinition', 'exposureAlternative': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.exposureAlternative is not None

    def test_from_dict_outcome(self):
        data = {'resourceType': 'ResearchDefinition', 'outcome': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchDefinition)
        assert result.outcome is not None


class TestGetPathResearchDefinition:

    def test_get_path_id(self):
        resource = ResearchDefinition()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ResearchDefinition()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ResearchDefinition()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ResearchDefinition.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ResearchDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ResearchDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ResearchDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ResearchDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ResearchDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ResearchDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ResearchDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = ResearchDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_identifier(self):
        resource = ResearchDefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_version(self):
        resource = ResearchDefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = ResearchDefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = ResearchDefinition()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_short_title(self):
        resource = ResearchDefinition()
        resource.shortTitle = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'shortTitle')
        assert result is not None

    def test_get_path_subtitle(self):
        resource = ResearchDefinition()
        resource.subtitle = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subtitle')
        assert result is not None

    def test_get_path_status(self):
        resource = ResearchDefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = ResearchDefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = ResearchDefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = ResearchDefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = ResearchDefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = ResearchDefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_comment(self):
        resource = ResearchDefinition()
        resource.comment = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'comment')
        assert result is not None

    def test_get_path_use_context(self):
        resource = ResearchDefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = ResearchDefinition()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_purpose(self):
        resource = ResearchDefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_usage(self):
        resource = ResearchDefinition()
        resource.usage = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'usage')
        assert result is not None

    def test_get_path_copyright(self):
        resource = ResearchDefinition()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_approval_date(self):
        resource = ResearchDefinition()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'approvalDate')
        assert result is not None

    def test_get_path_last_review_date(self):
        resource = ResearchDefinition()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lastReviewDate')
        assert result is not None

    def test_get_path_effective_period(self):
        resource = ResearchDefinition()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'effectivePeriod')
        assert result is not None

    def test_get_path_topic(self):
        resource = ResearchDefinition()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'topic')
        assert result is not None

    def test_get_path_author(self):
        resource = ResearchDefinition()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_editor(self):
        resource = ResearchDefinition()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'editor')
        assert result is not None

    def test_get_path_reviewer(self):
        resource = ResearchDefinition()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reviewer')
        assert result is not None

    def test_get_path_endorser(self):
        resource = ResearchDefinition()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'endorser')
        assert result is not None

    def test_get_path_related_artifact(self):
        resource = ResearchDefinition()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relatedArtifact')
        assert result is not None

    def test_get_path_library(self):
        resource = ResearchDefinition()
        resource.library = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'library')
        assert result is not None

    def test_get_path_population(self):
        resource = ResearchDefinition()
        resource.population = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'population')
        assert result is not None

    def test_get_path_exposure(self):
        resource = ResearchDefinition()
        resource.exposure = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'exposure')
        assert result is not None

    def test_get_path_exposure_alternative(self):
        resource = ResearchDefinition()
        resource.exposureAlternative = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'exposureAlternative')
        assert result is not None

    def test_get_path_outcome(self):
        resource = ResearchDefinition()
        resource.outcome = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'outcome')
        assert result is not None


class TestSetPathResearchDefinition:

    def test_set_path_id(self):
        resource = ResearchDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ResearchDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ResearchDefinition.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ResearchDefinition()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ResearchDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ResearchDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ResearchDefinition()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ResearchDefinition()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ResearchDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ResearchDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = ResearchDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_identifier(self):
        resource = ResearchDefinition()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_version(self):
        resource = ResearchDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = ResearchDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = ResearchDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_short_title(self):
        resource = ResearchDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'shortTitle', value)
        assert result is True
        assert resource.shortTitle is not None

    def test_set_path_subtitle(self):
        resource = ResearchDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subtitle', value)
        assert result is True
        assert resource.subtitle is not None

    def test_set_path_status(self):
        resource = ResearchDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = ResearchDefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = ResearchDefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = ResearchDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = ResearchDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = ResearchDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_comment(self):
        resource = ResearchDefinition()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'comment', value)
        assert result is True
        assert resource.comment is not None

    def test_set_path_use_context(self):
        resource = ResearchDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = ResearchDefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_purpose(self):
        resource = ResearchDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_usage(self):
        resource = ResearchDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'usage', value)
        assert result is True
        assert resource.usage is not None

    def test_set_path_copyright(self):
        resource = ResearchDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_approval_date(self):
        resource = ResearchDefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'approvalDate', value)
        assert result is True
        assert resource.approvalDate is not None

    def test_set_path_last_review_date(self):
        resource = ResearchDefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lastReviewDate', value)
        assert result is True
        assert resource.lastReviewDate is not None

    def test_set_path_effective_period(self):
        resource = ResearchDefinition()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'effectivePeriod', value)
        assert result is True
        assert resource.effectivePeriod is not None

    def test_set_path_topic(self):
        resource = ResearchDefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'topic', value)
        assert result is True
        assert resource.topic is not None

    def test_set_path_author(self):
        resource = ResearchDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_editor(self):
        resource = ResearchDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'editor', value)
        assert result is True
        assert resource.editor is not None

    def test_set_path_reviewer(self):
        resource = ResearchDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reviewer', value)
        assert result is True
        assert resource.reviewer is not None

    def test_set_path_endorser(self):
        resource = ResearchDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'endorser', value)
        assert result is True
        assert resource.endorser is not None

    def test_set_path_related_artifact(self):
        resource = ResearchDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relatedArtifact', value)
        assert result is True
        assert resource.relatedArtifact is not None

    def test_set_path_library(self):
        resource = ResearchDefinition()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'library', value)
        assert result is True
        assert resource.library is not None

    def test_set_path_population(self):
        resource = ResearchDefinition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'population', value)
        assert result is True
        assert resource.population is not None

    def test_set_path_exposure(self):
        resource = ResearchDefinition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'exposure', value)
        assert result is True
        assert resource.exposure is not None

    def test_set_path_exposure_alternative(self):
        resource = ResearchDefinition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'exposureAlternative', value)
        assert result is True
        assert resource.exposureAlternative is not None

    def test_set_path_outcome(self):
        resource = ResearchDefinition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'outcome', value)
        assert result is True
        assert resource.outcome is not None


class TestParsePathResearchDefinition:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ResearchDefinition.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ResearchDefinition.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ResearchDefinition.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
