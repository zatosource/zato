# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import shareableactivitydefinition


class TestToDictshareableactivitydefinition:

    def test_to_dict_empty(self):
        resource = shareableactivitydefinition()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'shareableactivitydefinition'

    def test_to_dict_with_id(self):
        resource = shareableactivitydefinition()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = shareableactivitydefinition()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, shareableactivitydefinition)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = shareableactivitydefinition()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = shareableactivitydefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = shareableactivitydefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = shareableactivitydefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = shareableactivitydefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = shareableactivitydefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = shareableactivitydefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = shareableactivitydefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = shareableactivitydefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_identifier(self):
        resource = shareableactivitydefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_version(self):
        resource = shareableactivitydefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = shareableactivitydefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = shareableactivitydefinition()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_subtitle(self):
        resource = shareableactivitydefinition()
        resource.subtitle = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subtitle' in result

    def test_to_dict_status(self):
        resource = shareableactivitydefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = shareableactivitydefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = shareableactivitydefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = shareableactivitydefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = shareableactivitydefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = shareableactivitydefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = shareableactivitydefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = shareableactivitydefinition()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_purpose(self):
        resource = shareableactivitydefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_usage(self):
        resource = shareableactivitydefinition()
        resource.usage = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'usage' in result

    def test_to_dict_copyright(self):
        resource = shareableactivitydefinition()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_approval_date(self):
        resource = shareableactivitydefinition()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'approvalDate' in result

    def test_to_dict_last_review_date(self):
        resource = shareableactivitydefinition()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lastReviewDate' in result

    def test_to_dict_effective_period(self):
        resource = shareableactivitydefinition()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'effectivePeriod' in result

    def test_to_dict_topic(self):
        resource = shareableactivitydefinition()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'topic' in result

    def test_to_dict_author(self):
        resource = shareableactivitydefinition()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_editor(self):
        resource = shareableactivitydefinition()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'editor' in result

    def test_to_dict_reviewer(self):
        resource = shareableactivitydefinition()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reviewer' in result

    def test_to_dict_endorser(self):
        resource = shareableactivitydefinition()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'endorser' in result

    def test_to_dict_related_artifact(self):
        resource = shareableactivitydefinition()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relatedArtifact' in result

    def test_to_dict_library(self):
        resource = shareableactivitydefinition()
        resource.library = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'library' in result

    def test_to_dict_kind(self):
        resource = shareableactivitydefinition()
        resource.kind = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'kind' in result

    def test_to_dict_profile(self):
        resource = shareableactivitydefinition()
        resource.profile = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'profile' in result

    def test_to_dict_code(self):
        resource = shareableactivitydefinition()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_intent(self):
        resource = shareableactivitydefinition()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'intent' in result

    def test_to_dict_priority(self):
        resource = shareableactivitydefinition()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priority' in result

    def test_to_dict_do_not_perform(self):
        resource = shareableactivitydefinition()
        resource.doNotPerform = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'doNotPerform' in result

    def test_to_dict_location(self):
        resource = shareableactivitydefinition()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'location' in result

    def test_to_dict_participant(self):
        resource = shareableactivitydefinition()
        resource.participant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'participant' in result

    def test_to_dict_quantity(self):
        resource = shareableactivitydefinition()
        resource.quantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'quantity' in result

    def test_to_dict_dosage(self):
        resource = shareableactivitydefinition()
        resource.dosage = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dosage' in result

    def test_to_dict_body_site(self):
        resource = shareableactivitydefinition()
        resource.bodySite = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'bodySite' in result

    def test_to_dict_specimen_requirement(self):
        resource = shareableactivitydefinition()
        resource.specimenRequirement = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'specimenRequirement' in result

    def test_to_dict_observation_requirement(self):
        resource = shareableactivitydefinition()
        resource.observationRequirement = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'observationRequirement' in result

    def test_to_dict_observation_result_requirement(self):
        resource = shareableactivitydefinition()
        resource.observationResultRequirement = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'observationResultRequirement' in result

    def test_to_dict_transform(self):
        resource = shareableactivitydefinition()
        resource.transform = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'transform' in result

    def test_to_dict_dynamic_value(self):
        resource = shareableactivitydefinition()
        resource.dynamicValue = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'dynamicValue' in result


class TestFromDictshareableactivitydefinition:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'shareableactivitydefinition', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert isinstance(result, shareableactivitydefinition)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'shareableactivitydefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert isinstance(result, shareableactivitydefinition)

    def test_from_dict_id(self):
        data = {'resourceType': 'shareableactivitydefinition', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'shareableactivitydefinition', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'shareableactivitydefinition', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'shareableactivitydefinition', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'shareableactivitydefinition', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'shareableactivitydefinition', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'shareableactivitydefinition', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'shareableactivitydefinition', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'shareableactivitydefinition', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.url is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'shareableactivitydefinition', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.identifier is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'shareableactivitydefinition', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'shareableactivitydefinition', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'shareableactivitydefinition', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.title is not None

    def test_from_dict_subtitle(self):
        data = {'resourceType': 'shareableactivitydefinition', 'subtitle': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.subtitle is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'shareableactivitydefinition', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'shareableactivitydefinition', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'shareableactivitydefinition', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'shareableactivitydefinition', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'shareableactivitydefinition', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'shareableactivitydefinition', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'shareableactivitydefinition', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'shareableactivitydefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.jurisdiction is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'shareableactivitydefinition', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.purpose is not None

    def test_from_dict_usage(self):
        data = {'resourceType': 'shareableactivitydefinition', 'usage': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.usage is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'shareableactivitydefinition', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.copyright is not None

    def test_from_dict_approval_date(self):
        data = {'resourceType': 'shareableactivitydefinition', 'approvalDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.approvalDate is not None

    def test_from_dict_last_review_date(self):
        data = {'resourceType': 'shareableactivitydefinition', 'lastReviewDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.lastReviewDate is not None

    def test_from_dict_effective_period(self):
        data = {'resourceType': 'shareableactivitydefinition', 'effectivePeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.effectivePeriod is not None

    def test_from_dict_topic(self):
        data = {'resourceType': 'shareableactivitydefinition',
         'topic': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.topic is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'shareableactivitydefinition', 'author': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.author is not None

    def test_from_dict_editor(self):
        data = {'resourceType': 'shareableactivitydefinition', 'editor': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.editor is not None

    def test_from_dict_reviewer(self):
        data = {'resourceType': 'shareableactivitydefinition', 'reviewer': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.reviewer is not None

    def test_from_dict_endorser(self):
        data = {'resourceType': 'shareableactivitydefinition', 'endorser': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.endorser is not None

    def test_from_dict_related_artifact(self):
        data = {'resourceType': 'shareableactivitydefinition', 'relatedArtifact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.relatedArtifact is not None

    def test_from_dict_library(self):
        data = {'resourceType': 'shareableactivitydefinition', 'library': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.library is not None

    def test_from_dict_kind(self):
        data = {'resourceType': 'shareableactivitydefinition', 'kind': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.kind is not None

    def test_from_dict_profile(self):
        data = {'resourceType': 'shareableactivitydefinition', 'profile': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.profile is not None

    def test_from_dict_code(self):
        data = {'code': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'shareableactivitydefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.code is not None

    def test_from_dict_intent(self):
        data = {'resourceType': 'shareableactivitydefinition', 'intent': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.intent is not None

    def test_from_dict_priority(self):
        data = {'resourceType': 'shareableactivitydefinition', 'priority': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.priority is not None

    def test_from_dict_do_not_perform(self):
        data = {'resourceType': 'shareableactivitydefinition', 'doNotPerform': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.doNotPerform is not None

    def test_from_dict_location(self):
        data = {'resourceType': 'shareableactivitydefinition', 'location': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.location is not None

    def test_from_dict_participant(self):
        data = {'resourceType': 'shareableactivitydefinition', 'participant': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.participant is not None

    def test_from_dict_quantity(self):
        data = {'resourceType': 'shareableactivitydefinition', 'quantity': {'value': 100, 'unit': 'mg'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.quantity is not None

    def test_from_dict_dosage(self):
        data = {'resourceType': 'shareableactivitydefinition', 'dosage': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.dosage is not None

    def test_from_dict_body_site(self):
        data = {'bodySite': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'shareableactivitydefinition'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.bodySite is not None

    def test_from_dict_specimen_requirement(self):
        data = {'resourceType': 'shareableactivitydefinition', 'specimenRequirement': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.specimenRequirement is not None

    def test_from_dict_observation_requirement(self):
        data = {'resourceType': 'shareableactivitydefinition', 'observationRequirement': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.observationRequirement is not None

    def test_from_dict_observation_result_requirement(self):
        data = {'resourceType': 'shareableactivitydefinition', 'observationResultRequirement': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.observationResultRequirement is not None

    def test_from_dict_transform(self):
        data = {'resourceType': 'shareableactivitydefinition', 'transform': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.transform is not None

    def test_from_dict_dynamic_value(self):
        data = {'resourceType': 'shareableactivitydefinition', 'dynamicValue': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, shareableactivitydefinition)
        assert result.dynamicValue is not None


class TestGetPathshareableactivitydefinition:

    def test_get_path_id(self):
        resource = shareableactivitydefinition()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = shareableactivitydefinition()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = shareableactivitydefinition()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'shareableactivitydefinition.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = shareableactivitydefinition()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = shareableactivitydefinition()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = shareableactivitydefinition()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = shareableactivitydefinition()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = shareableactivitydefinition()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = shareableactivitydefinition()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = shareableactivitydefinition()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = shareableactivitydefinition()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_identifier(self):
        resource = shareableactivitydefinition()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_version(self):
        resource = shareableactivitydefinition()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = shareableactivitydefinition()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = shareableactivitydefinition()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_subtitle(self):
        resource = shareableactivitydefinition()
        resource.subtitle = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subtitle')
        assert result is not None

    def test_get_path_status(self):
        resource = shareableactivitydefinition()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = shareableactivitydefinition()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = shareableactivitydefinition()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = shareableactivitydefinition()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = shareableactivitydefinition()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = shareableactivitydefinition()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = shareableactivitydefinition()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = shareableactivitydefinition()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_purpose(self):
        resource = shareableactivitydefinition()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_usage(self):
        resource = shareableactivitydefinition()
        resource.usage = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'usage')
        assert result is not None

    def test_get_path_copyright(self):
        resource = shareableactivitydefinition()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_approval_date(self):
        resource = shareableactivitydefinition()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'approvalDate')
        assert result is not None

    def test_get_path_last_review_date(self):
        resource = shareableactivitydefinition()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lastReviewDate')
        assert result is not None

    def test_get_path_effective_period(self):
        resource = shareableactivitydefinition()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'effectivePeriod')
        assert result is not None

    def test_get_path_topic(self):
        resource = shareableactivitydefinition()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'topic')
        assert result is not None

    def test_get_path_author(self):
        resource = shareableactivitydefinition()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_editor(self):
        resource = shareableactivitydefinition()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'editor')
        assert result is not None

    def test_get_path_reviewer(self):
        resource = shareableactivitydefinition()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reviewer')
        assert result is not None

    def test_get_path_endorser(self):
        resource = shareableactivitydefinition()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'endorser')
        assert result is not None

    def test_get_path_related_artifact(self):
        resource = shareableactivitydefinition()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relatedArtifact')
        assert result is not None

    def test_get_path_library(self):
        resource = shareableactivitydefinition()
        resource.library = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'library')
        assert result is not None

    def test_get_path_kind(self):
        resource = shareableactivitydefinition()
        resource.kind = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'kind')
        assert result is not None

    def test_get_path_profile(self):
        resource = shareableactivitydefinition()
        resource.profile = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'profile')
        assert result is not None

    def test_get_path_code(self):
        resource = shareableactivitydefinition()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_intent(self):
        resource = shareableactivitydefinition()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'intent')
        assert result is not None

    def test_get_path_priority(self):
        resource = shareableactivitydefinition()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priority')
        assert result is not None

    def test_get_path_do_not_perform(self):
        resource = shareableactivitydefinition()
        resource.doNotPerform = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'doNotPerform')
        assert result is not None

    def test_get_path_location(self):
        resource = shareableactivitydefinition()
        resource.location = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'location')
        assert result is not None

    def test_get_path_participant(self):
        resource = shareableactivitydefinition()
        resource.participant = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'participant')
        assert result is not None

    def test_get_path_quantity(self):
        resource = shareableactivitydefinition()
        resource.quantity = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'quantity')
        assert result is not None

    def test_get_path_dosage(self):
        resource = shareableactivitydefinition()
        resource.dosage = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dosage')
        assert result is not None

    def test_get_path_body_site(self):
        resource = shareableactivitydefinition()
        resource.bodySite = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'bodySite')
        assert result is not None

    def test_get_path_specimen_requirement(self):
        resource = shareableactivitydefinition()
        resource.specimenRequirement = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'specimenRequirement')
        assert result is not None

    def test_get_path_observation_requirement(self):
        resource = shareableactivitydefinition()
        resource.observationRequirement = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'observationRequirement')
        assert result is not None

    def test_get_path_observation_result_requirement(self):
        resource = shareableactivitydefinition()
        resource.observationResultRequirement = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'observationResultRequirement')
        assert result is not None

    def test_get_path_transform(self):
        resource = shareableactivitydefinition()
        resource.transform = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'transform')
        assert result is not None

    def test_get_path_dynamic_value(self):
        resource = shareableactivitydefinition()
        resource.dynamicValue = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'dynamicValue')
        assert result is not None


class TestSetPathshareableactivitydefinition:

    def test_set_path_id(self):
        resource = shareableactivitydefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = shareableactivitydefinition()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'shareableactivitydefinition.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = shareableactivitydefinition()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = shareableactivitydefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = shareableactivitydefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = shareableactivitydefinition()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = shareableactivitydefinition()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = shareableactivitydefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = shareableactivitydefinition()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = shareableactivitydefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_identifier(self):
        resource = shareableactivitydefinition()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_version(self):
        resource = shareableactivitydefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = shareableactivitydefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = shareableactivitydefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_subtitle(self):
        resource = shareableactivitydefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subtitle', value)
        assert result is True
        assert resource.subtitle is not None

    def test_set_path_status(self):
        resource = shareableactivitydefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = shareableactivitydefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = shareableactivitydefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = shareableactivitydefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = shareableactivitydefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = shareableactivitydefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = shareableactivitydefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = shareableactivitydefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_purpose(self):
        resource = shareableactivitydefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_usage(self):
        resource = shareableactivitydefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'usage', value)
        assert result is True
        assert resource.usage is not None

    def test_set_path_copyright(self):
        resource = shareableactivitydefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_approval_date(self):
        resource = shareableactivitydefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'approvalDate', value)
        assert result is True
        assert resource.approvalDate is not None

    def test_set_path_last_review_date(self):
        resource = shareableactivitydefinition()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lastReviewDate', value)
        assert result is True
        assert resource.lastReviewDate is not None

    def test_set_path_effective_period(self):
        resource = shareableactivitydefinition()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'effectivePeriod', value)
        assert result is True
        assert resource.effectivePeriod is not None

    def test_set_path_topic(self):
        resource = shareableactivitydefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'topic', value)
        assert result is True
        assert resource.topic is not None

    def test_set_path_author(self):
        resource = shareableactivitydefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_editor(self):
        resource = shareableactivitydefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'editor', value)
        assert result is True
        assert resource.editor is not None

    def test_set_path_reviewer(self):
        resource = shareableactivitydefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reviewer', value)
        assert result is True
        assert resource.reviewer is not None

    def test_set_path_endorser(self):
        resource = shareableactivitydefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'endorser', value)
        assert result is True
        assert resource.endorser is not None

    def test_set_path_related_artifact(self):
        resource = shareableactivitydefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relatedArtifact', value)
        assert result is True
        assert resource.relatedArtifact is not None

    def test_set_path_library(self):
        resource = shareableactivitydefinition()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'library', value)
        assert result is True
        assert resource.library is not None

    def test_set_path_kind(self):
        resource = shareableactivitydefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'kind', value)
        assert result is True
        assert resource.kind is not None

    def test_set_path_profile(self):
        resource = shareableactivitydefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'profile', value)
        assert result is True
        assert resource.profile is not None

    def test_set_path_code(self):
        resource = shareableactivitydefinition()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_intent(self):
        resource = shareableactivitydefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'intent', value)
        assert result is True
        assert resource.intent is not None

    def test_set_path_priority(self):
        resource = shareableactivitydefinition()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priority', value)
        assert result is True
        assert resource.priority is not None

    def test_set_path_do_not_perform(self):
        resource = shareableactivitydefinition()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'doNotPerform', value)
        assert result is True
        assert resource.doNotPerform is not None

    def test_set_path_location(self):
        resource = shareableactivitydefinition()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'location', value)
        assert result is True
        assert resource.location is not None

    def test_set_path_participant(self):
        resource = shareableactivitydefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'participant', value)
        assert result is True
        assert resource.participant is not None

    def test_set_path_quantity(self):
        resource = shareableactivitydefinition()
        value = {'value': 100, 'unit': 'mg'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'quantity', value)
        assert result is True
        assert resource.quantity is not None

    def test_set_path_dosage(self):
        resource = shareableactivitydefinition()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dosage', value)
        assert result is True
        assert resource.dosage is not None

    def test_set_path_body_site(self):
        resource = shareableactivitydefinition()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'bodySite', value)
        assert result is True
        assert resource.bodySite is not None

    def test_set_path_specimen_requirement(self):
        resource = shareableactivitydefinition()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'specimenRequirement', value)
        assert result is True
        assert resource.specimenRequirement is not None

    def test_set_path_observation_requirement(self):
        resource = shareableactivitydefinition()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'observationRequirement', value)
        assert result is True
        assert resource.observationRequirement is not None

    def test_set_path_observation_result_requirement(self):
        resource = shareableactivitydefinition()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'observationResultRequirement', value)
        assert result is True
        assert resource.observationResultRequirement is not None

    def test_set_path_transform(self):
        resource = shareableactivitydefinition()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'transform', value)
        assert result is True
        assert resource.transform is not None

    def test_set_path_dynamic_value(self):
        resource = shareableactivitydefinition()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'dynamicValue', value)
        assert result is True
        assert resource.dynamicValue is not None


class TestParsePathshareableactivitydefinition:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('shareableactivitydefinition.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('shareableactivitydefinition.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('shareableactivitydefinition.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
