# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ActivityDefinition


class TestToDictActivityDefinition:

    def test_to_dict_empty(self):
        resource = ActivityDefinition()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ActivityDefinition'

    def test_to_dict_with_id(self):
        resource = ActivityDefinition()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ActivityDefinition()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ActivityDefinition)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ActivityDefinition()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ActivityDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ActivityDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ActivityDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ActivityDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ActivityDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ActivityDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ActivityDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = ActivityDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_identifier(self):
        resource = ActivityDefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_version(self):
        resource = ActivityDefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = ActivityDefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = ActivityDefinition()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_subtitle(self):
        resource = ActivityDefinition()
        resource.subtitle = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subtitle' in result

    def test_to_dict_status(self):
        resource = ActivityDefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = ActivityDefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = ActivityDefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = ActivityDefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = ActivityDefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = ActivityDefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = ActivityDefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = ActivityDefinition()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_purpose(self):
        resource = ActivityDefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_usage(self):
        resource = ActivityDefinition()
        resource.usage = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'usage' in result

    def test_to_dict_copyright(self):
        resource = ActivityDefinition()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_approval_date(self):
        resource = ActivityDefinition()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'approvalDate' in result

    def test_to_dict_last_review_date(self):
        resource = ActivityDefinition()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lastReviewDate' in result

    def test_to_dict_effective_period(self):
        resource = ActivityDefinition()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'effectivePeriod' in result

    def test_to_dict_topic(self):
        resource = ActivityDefinition()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'topic' in result

    def test_to_dict_author(self):
        resource = ActivityDefinition()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_editor(self):
        resource = ActivityDefinition()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'editor' in result

    def test_to_dict_reviewer(self):
        resource = ActivityDefinition()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reviewer' in result

    def test_to_dict_endorser(self):
        resource = ActivityDefinition()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'endorser' in result

    def test_to_dict_related_artifact(self):
        resource = ActivityDefinition()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relatedArtifact' in result

    def test_to_dict_library(self):
        resource = ActivityDefinition()
        resource.library = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'library' in result

    def test_to_dict_kind(self):
        resource = ActivityDefinition()
        resource.kind = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'kind' in result

    def test_to_dict_profile(self):
        resource = ActivityDefinition()
        resource.profile = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'profile' in result

    def test_to_dict_code(self):
        resource = ActivityDefinition()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_intent(self):
        resource = ActivityDefinition()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'intent' in result

    def test_to_dict_priority(self):
        resource = ActivityDefinition()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priority' in result

    def test_to_dict_do_not_perform(self):
        resource = ActivityDefinition()
        resource.doNotPerform = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'doNotPerform' in result

    def test_to_dict_location(self):
        resource = ActivityDefinition()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'location' in result

    def test_to_dict_participant(self):
        resource = ActivityDefinition()
        resource.participant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'participant' in result

    def test_to_dict_quantity(self):
        resource = ActivityDefinition()
        resource.quantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'quantity' in result

    def test_to_dict_dosage(self):
        resource = ActivityDefinition()
        resource.dosage = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dosage' in result

    def test_to_dict_body_site(self):
        resource = ActivityDefinition()
        resource.bodySite = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'bodySite' in result

    def test_to_dict_specimen_requirement(self):
        resource = ActivityDefinition()
        resource.specimenRequirement = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'specimenRequirement' in result

    def test_to_dict_observation_requirement(self):
        resource = ActivityDefinition()
        resource.observationRequirement = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'observationRequirement' in result

    def test_to_dict_observation_result_requirement(self):
        resource = ActivityDefinition()
        resource.observationResultRequirement = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'observationResultRequirement' in result

    def test_to_dict_transform(self):
        resource = ActivityDefinition()
        resource.transform = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'transform' in result

    def test_to_dict_dynamic_value(self):
        resource = ActivityDefinition()
        resource.dynamicValue = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dynamicValue' in result


class TestFromDictActivityDefinition:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ActivityDefinition', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert isinstance(result, ActivityDefinition)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ActivityDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert isinstance(result, ActivityDefinition)

    def test_from_dict_id(self):
        data = {'resourceType': 'ActivityDefinition', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ActivityDefinition', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ActivityDefinition', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ActivityDefinition', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ActivityDefinition', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ActivityDefinition', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ActivityDefinition', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ActivityDefinition', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'ActivityDefinition', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.url is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'ActivityDefinition', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.identifier is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'ActivityDefinition', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'ActivityDefinition', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'ActivityDefinition', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.title is not None

    def test_from_dict_subtitle(self):
        data = {'resourceType': 'ActivityDefinition', 'subtitle': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.subtitle is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'ActivityDefinition', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'ActivityDefinition', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'ActivityDefinition', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'ActivityDefinition', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'ActivityDefinition', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'ActivityDefinition', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'ActivityDefinition', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'ActivityDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.jurisdiction is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'ActivityDefinition', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.purpose is not None

    def test_from_dict_usage(self):
        data = {'resourceType': 'ActivityDefinition', 'usage': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.usage is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'ActivityDefinition', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.copyright is not None

    def test_from_dict_approval_date(self):
        data = {'resourceType': 'ActivityDefinition', 'approvalDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.approvalDate is not None

    def test_from_dict_last_review_date(self):
        data = {'resourceType': 'ActivityDefinition', 'lastReviewDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.lastReviewDate is not None

    def test_from_dict_effective_period(self):
        data = {'resourceType': 'ActivityDefinition', 'effectivePeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.effectivePeriod is not None

    def test_from_dict_topic(self):
        data = {'resourceType': 'ActivityDefinition',
         'topic': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.topic is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'ActivityDefinition', 'author': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.author is not None

    def test_from_dict_editor(self):
        data = {'resourceType': 'ActivityDefinition', 'editor': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.editor is not None

    def test_from_dict_reviewer(self):
        data = {'resourceType': 'ActivityDefinition', 'reviewer': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.reviewer is not None

    def test_from_dict_endorser(self):
        data = {'resourceType': 'ActivityDefinition', 'endorser': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.endorser is not None

    def test_from_dict_related_artifact(self):
        data = {'resourceType': 'ActivityDefinition', 'relatedArtifact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.relatedArtifact is not None

    def test_from_dict_library(self):
        data = {'resourceType': 'ActivityDefinition', 'library': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.library is not None

    def test_from_dict_kind(self):
        data = {'resourceType': 'ActivityDefinition', 'kind': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.kind is not None

    def test_from_dict_profile(self):
        data = {'resourceType': 'ActivityDefinition', 'profile': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.profile is not None

    def test_from_dict_code(self):
        data = {'code': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'ActivityDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.code is not None

    def test_from_dict_intent(self):
        data = {'resourceType': 'ActivityDefinition', 'intent': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.intent is not None

    def test_from_dict_priority(self):
        data = {'resourceType': 'ActivityDefinition', 'priority': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.priority is not None

    def test_from_dict_do_not_perform(self):
        data = {'resourceType': 'ActivityDefinition', 'doNotPerform': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.doNotPerform is not None

    def test_from_dict_location(self):
        data = {'resourceType': 'ActivityDefinition', 'location': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.location is not None

    def test_from_dict_participant(self):
        data = {'resourceType': 'ActivityDefinition', 'participant': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.participant is not None

    def test_from_dict_quantity(self):
        data = {'resourceType': 'ActivityDefinition', 'quantity': {'value': 100, 'unit': 'mg'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.quantity is not None

    def test_from_dict_dosage(self):
        data = {'resourceType': 'ActivityDefinition', 'dosage': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.dosage is not None

    def test_from_dict_body_site(self):
        data = {'bodySite': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'ActivityDefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.bodySite is not None

    def test_from_dict_specimen_requirement(self):
        data = {'resourceType': 'ActivityDefinition', 'specimenRequirement': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.specimenRequirement is not None

    def test_from_dict_observation_requirement(self):
        data = {'resourceType': 'ActivityDefinition', 'observationRequirement': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.observationRequirement is not None

    def test_from_dict_observation_result_requirement(self):
        data = {'resourceType': 'ActivityDefinition', 'observationResultRequirement': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.observationResultRequirement is not None

    def test_from_dict_transform(self):
        data = {'resourceType': 'ActivityDefinition', 'transform': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.transform is not None

    def test_from_dict_dynamic_value(self):
        data = {'resourceType': 'ActivityDefinition', 'dynamicValue': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ActivityDefinition)
        assert result.dynamicValue is not None


class TestGetPathActivityDefinition:

    def test_get_path_id(self):
        resource = ActivityDefinition()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ActivityDefinition()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ActivityDefinition()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ActivityDefinition.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ActivityDefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ActivityDefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ActivityDefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ActivityDefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ActivityDefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ActivityDefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ActivityDefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = ActivityDefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_identifier(self):
        resource = ActivityDefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_version(self):
        resource = ActivityDefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = ActivityDefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = ActivityDefinition()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_subtitle(self):
        resource = ActivityDefinition()
        resource.subtitle = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subtitle')
        assert result is not None

    def test_get_path_status(self):
        resource = ActivityDefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = ActivityDefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = ActivityDefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = ActivityDefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = ActivityDefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = ActivityDefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = ActivityDefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = ActivityDefinition()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_purpose(self):
        resource = ActivityDefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_usage(self):
        resource = ActivityDefinition()
        resource.usage = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'usage')
        assert result is not None

    def test_get_path_copyright(self):
        resource = ActivityDefinition()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_approval_date(self):
        resource = ActivityDefinition()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'approvalDate')
        assert result is not None

    def test_get_path_last_review_date(self):
        resource = ActivityDefinition()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lastReviewDate')
        assert result is not None

    def test_get_path_effective_period(self):
        resource = ActivityDefinition()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'effectivePeriod')
        assert result is not None

    def test_get_path_topic(self):
        resource = ActivityDefinition()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'topic')
        assert result is not None

    def test_get_path_author(self):
        resource = ActivityDefinition()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_editor(self):
        resource = ActivityDefinition()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'editor')
        assert result is not None

    def test_get_path_reviewer(self):
        resource = ActivityDefinition()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reviewer')
        assert result is not None

    def test_get_path_endorser(self):
        resource = ActivityDefinition()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'endorser')
        assert result is not None

    def test_get_path_related_artifact(self):
        resource = ActivityDefinition()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relatedArtifact')
        assert result is not None

    def test_get_path_library(self):
        resource = ActivityDefinition()
        resource.library = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'library')
        assert result is not None

    def test_get_path_kind(self):
        resource = ActivityDefinition()
        resource.kind = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'kind')
        assert result is not None

    def test_get_path_profile(self):
        resource = ActivityDefinition()
        resource.profile = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'profile')
        assert result is not None

    def test_get_path_code(self):
        resource = ActivityDefinition()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_intent(self):
        resource = ActivityDefinition()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'intent')
        assert result is not None

    def test_get_path_priority(self):
        resource = ActivityDefinition()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priority')
        assert result is not None

    def test_get_path_do_not_perform(self):
        resource = ActivityDefinition()
        resource.doNotPerform = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'doNotPerform')
        assert result is not None

    def test_get_path_location(self):
        resource = ActivityDefinition()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'location')
        assert result is not None

    def test_get_path_participant(self):
        resource = ActivityDefinition()
        resource.participant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'participant')
        assert result is not None

    def test_get_path_quantity(self):
        resource = ActivityDefinition()
        resource.quantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'quantity')
        assert result is not None

    def test_get_path_dosage(self):
        resource = ActivityDefinition()
        resource.dosage = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dosage')
        assert result is not None

    def test_get_path_body_site(self):
        resource = ActivityDefinition()
        resource.bodySite = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'bodySite')
        assert result is not None

    def test_get_path_specimen_requirement(self):
        resource = ActivityDefinition()
        resource.specimenRequirement = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'specimenRequirement')
        assert result is not None

    def test_get_path_observation_requirement(self):
        resource = ActivityDefinition()
        resource.observationRequirement = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'observationRequirement')
        assert result is not None

    def test_get_path_observation_result_requirement(self):
        resource = ActivityDefinition()
        resource.observationResultRequirement = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'observationResultRequirement')
        assert result is not None

    def test_get_path_transform(self):
        resource = ActivityDefinition()
        resource.transform = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'transform')
        assert result is not None

    def test_get_path_dynamic_value(self):
        resource = ActivityDefinition()
        resource.dynamicValue = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dynamicValue')
        assert result is not None


class TestSetPathActivityDefinition:

    def test_set_path_id(self):
        resource = ActivityDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ActivityDefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ActivityDefinition.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ActivityDefinition()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ActivityDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ActivityDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ActivityDefinition()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ActivityDefinition()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ActivityDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ActivityDefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = ActivityDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_identifier(self):
        resource = ActivityDefinition()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_version(self):
        resource = ActivityDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = ActivityDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = ActivityDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_subtitle(self):
        resource = ActivityDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subtitle', value)
        assert result is True
        assert resource.subtitle is not None

    def test_set_path_status(self):
        resource = ActivityDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = ActivityDefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = ActivityDefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = ActivityDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = ActivityDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = ActivityDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = ActivityDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = ActivityDefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_purpose(self):
        resource = ActivityDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_usage(self):
        resource = ActivityDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'usage', value)
        assert result is True
        assert resource.usage is not None

    def test_set_path_copyright(self):
        resource = ActivityDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_approval_date(self):
        resource = ActivityDefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'approvalDate', value)
        assert result is True
        assert resource.approvalDate is not None

    def test_set_path_last_review_date(self):
        resource = ActivityDefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lastReviewDate', value)
        assert result is True
        assert resource.lastReviewDate is not None

    def test_set_path_effective_period(self):
        resource = ActivityDefinition()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'effectivePeriod', value)
        assert result is True
        assert resource.effectivePeriod is not None

    def test_set_path_topic(self):
        resource = ActivityDefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'topic', value)
        assert result is True
        assert resource.topic is not None

    def test_set_path_author(self):
        resource = ActivityDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_editor(self):
        resource = ActivityDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'editor', value)
        assert result is True
        assert resource.editor is not None

    def test_set_path_reviewer(self):
        resource = ActivityDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reviewer', value)
        assert result is True
        assert resource.reviewer is not None

    def test_set_path_endorser(self):
        resource = ActivityDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'endorser', value)
        assert result is True
        assert resource.endorser is not None

    def test_set_path_related_artifact(self):
        resource = ActivityDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relatedArtifact', value)
        assert result is True
        assert resource.relatedArtifact is not None

    def test_set_path_library(self):
        resource = ActivityDefinition()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'library', value)
        assert result is True
        assert resource.library is not None

    def test_set_path_kind(self):
        resource = ActivityDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'kind', value)
        assert result is True
        assert resource.kind is not None

    def test_set_path_profile(self):
        resource = ActivityDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'profile', value)
        assert result is True
        assert resource.profile is not None

    def test_set_path_code(self):
        resource = ActivityDefinition()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_intent(self):
        resource = ActivityDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'intent', value)
        assert result is True
        assert resource.intent is not None

    def test_set_path_priority(self):
        resource = ActivityDefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priority', value)
        assert result is True
        assert resource.priority is not None

    def test_set_path_do_not_perform(self):
        resource = ActivityDefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'doNotPerform', value)
        assert result is True
        assert resource.doNotPerform is not None

    def test_set_path_location(self):
        resource = ActivityDefinition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'location', value)
        assert result is True
        assert resource.location is not None

    def test_set_path_participant(self):
        resource = ActivityDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'participant', value)
        assert result is True
        assert resource.participant is not None

    def test_set_path_quantity(self):
        resource = ActivityDefinition()
        value = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'quantity', value)
        assert result is True
        assert resource.quantity is not None

    def test_set_path_dosage(self):
        resource = ActivityDefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dosage', value)
        assert result is True
        assert resource.dosage is not None

    def test_set_path_body_site(self):
        resource = ActivityDefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'bodySite', value)
        assert result is True
        assert resource.bodySite is not None

    def test_set_path_specimen_requirement(self):
        resource = ActivityDefinition()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'specimenRequirement', value)
        assert result is True
        assert resource.specimenRequirement is not None

    def test_set_path_observation_requirement(self):
        resource = ActivityDefinition()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'observationRequirement', value)
        assert result is True
        assert resource.observationRequirement is not None

    def test_set_path_observation_result_requirement(self):
        resource = ActivityDefinition()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'observationResultRequirement', value)
        assert result is True
        assert resource.observationResultRequirement is not None

    def test_set_path_transform(self):
        resource = ActivityDefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'transform', value)
        assert result is True
        assert resource.transform is not None

    def test_set_path_dynamic_value(self):
        resource = ActivityDefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dynamicValue', value)
        assert result is True
        assert resource.dynamicValue is not None


class TestParsePathActivityDefinition:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ActivityDefinition.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ActivityDefinition.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ActivityDefinition.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
