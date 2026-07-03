# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import EffectEvidenceSynthesis


class TestToDictEffectEvidenceSynthesis:

    def test_to_dict_empty(self):
        resource = EffectEvidenceSynthesis()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'EffectEvidenceSynthesis'

    def test_to_dict_with_id(self):
        resource = EffectEvidenceSynthesis()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = EffectEvidenceSynthesis()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, EffectEvidenceSynthesis)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = EffectEvidenceSynthesis()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = EffectEvidenceSynthesis()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = EffectEvidenceSynthesis()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = EffectEvidenceSynthesis()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = EffectEvidenceSynthesis()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = EffectEvidenceSynthesis()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = EffectEvidenceSynthesis()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = EffectEvidenceSynthesis()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = EffectEvidenceSynthesis()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_identifier(self):
        resource = EffectEvidenceSynthesis()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_version(self):
        resource = EffectEvidenceSynthesis()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = EffectEvidenceSynthesis()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = EffectEvidenceSynthesis()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_status(self):
        resource = EffectEvidenceSynthesis()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_date(self):
        resource = EffectEvidenceSynthesis()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = EffectEvidenceSynthesis()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = EffectEvidenceSynthesis()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = EffectEvidenceSynthesis()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_note(self):
        resource = EffectEvidenceSynthesis()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_use_context(self):
        resource = EffectEvidenceSynthesis()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = EffectEvidenceSynthesis()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_copyright(self):
        resource = EffectEvidenceSynthesis()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_approval_date(self):
        resource = EffectEvidenceSynthesis()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'approvalDate' in result

    def test_to_dict_last_review_date(self):
        resource = EffectEvidenceSynthesis()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lastReviewDate' in result

    def test_to_dict_effective_period(self):
        resource = EffectEvidenceSynthesis()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'effectivePeriod' in result

    def test_to_dict_topic(self):
        resource = EffectEvidenceSynthesis()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'topic' in result

    def test_to_dict_author(self):
        resource = EffectEvidenceSynthesis()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_editor(self):
        resource = EffectEvidenceSynthesis()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'editor' in result

    def test_to_dict_reviewer(self):
        resource = EffectEvidenceSynthesis()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reviewer' in result

    def test_to_dict_endorser(self):
        resource = EffectEvidenceSynthesis()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'endorser' in result

    def test_to_dict_related_artifact(self):
        resource = EffectEvidenceSynthesis()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relatedArtifact' in result

    def test_to_dict_synthesis_type(self):
        resource = EffectEvidenceSynthesis()
        resource.synthesisType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'synthesisType' in result

    def test_to_dict_study_type(self):
        resource = EffectEvidenceSynthesis()
        resource.studyType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'studyType' in result

    def test_to_dict_population(self):
        resource = EffectEvidenceSynthesis()
        resource.population = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'population' in result

    def test_to_dict_exposure(self):
        resource = EffectEvidenceSynthesis()
        resource.exposure = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'exposure' in result

    def test_to_dict_exposure_alternative(self):
        resource = EffectEvidenceSynthesis()
        resource.exposureAlternative = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'exposureAlternative' in result

    def test_to_dict_outcome(self):
        resource = EffectEvidenceSynthesis()
        resource.outcome = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'outcome' in result

    def test_to_dict_sample_size(self):
        resource = EffectEvidenceSynthesis()
        resource.sampleSize = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'sampleSize' in result

    def test_to_dict_results_by_exposure(self):
        resource = EffectEvidenceSynthesis()
        resource.resultsByExposure = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'resultsByExposure' in result

    def test_to_dict_effect_estimate(self):
        resource = EffectEvidenceSynthesis()
        resource.effectEstimate = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'effectEstimate' in result

    def test_to_dict_certainty(self):
        resource = EffectEvidenceSynthesis()
        resource.certainty = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'certainty' in result


class TestFromDictEffectEvidenceSynthesis:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert isinstance(result, EffectEvidenceSynthesis)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'EffectEvidenceSynthesis'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert isinstance(result, EffectEvidenceSynthesis)

    def test_from_dict_id(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.url is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.identifier is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.title is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.status is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.description is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.note is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'EffectEvidenceSynthesis'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.jurisdiction is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.copyright is not None

    def test_from_dict_approval_date(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'approvalDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.approvalDate is not None

    def test_from_dict_last_review_date(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'lastReviewDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.lastReviewDate is not None

    def test_from_dict_effective_period(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'effectivePeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.effectivePeriod is not None

    def test_from_dict_topic(self):
        data = {'resourceType': 'EffectEvidenceSynthesis',
         'topic': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.topic is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'author': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.author is not None

    def test_from_dict_editor(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'editor': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.editor is not None

    def test_from_dict_reviewer(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'reviewer': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.reviewer is not None

    def test_from_dict_endorser(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'endorser': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.endorser is not None

    def test_from_dict_related_artifact(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'relatedArtifact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.relatedArtifact is not None

    def test_from_dict_synthesis_type(self):
        data = {'resourceType': 'EffectEvidenceSynthesis',
         'synthesisType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.synthesisType is not None

    def test_from_dict_study_type(self):
        data = {'resourceType': 'EffectEvidenceSynthesis',
         'studyType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.studyType is not None

    def test_from_dict_population(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'population': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.population is not None

    def test_from_dict_exposure(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'exposure': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.exposure is not None

    def test_from_dict_exposure_alternative(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'exposureAlternative': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.exposureAlternative is not None

    def test_from_dict_outcome(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'outcome': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.outcome is not None

    def test_from_dict_sample_size(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'sampleSize': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.sampleSize is not None

    def test_from_dict_results_by_exposure(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'resultsByExposure': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.resultsByExposure is not None

    def test_from_dict_effect_estimate(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'effectEstimate': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.effectEstimate is not None

    def test_from_dict_certainty(self):
        data = {'resourceType': 'EffectEvidenceSynthesis', 'certainty': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, EffectEvidenceSynthesis)
        assert result.certainty is not None


class TestGetPathEffectEvidenceSynthesis:

    def test_get_path_id(self):
        resource = EffectEvidenceSynthesis()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = EffectEvidenceSynthesis()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = EffectEvidenceSynthesis()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'EffectEvidenceSynthesis.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = EffectEvidenceSynthesis()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = EffectEvidenceSynthesis()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = EffectEvidenceSynthesis()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = EffectEvidenceSynthesis()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = EffectEvidenceSynthesis()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = EffectEvidenceSynthesis()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = EffectEvidenceSynthesis()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = EffectEvidenceSynthesis()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_identifier(self):
        resource = EffectEvidenceSynthesis()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_version(self):
        resource = EffectEvidenceSynthesis()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = EffectEvidenceSynthesis()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = EffectEvidenceSynthesis()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_status(self):
        resource = EffectEvidenceSynthesis()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_date(self):
        resource = EffectEvidenceSynthesis()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = EffectEvidenceSynthesis()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = EffectEvidenceSynthesis()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = EffectEvidenceSynthesis()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_note(self):
        resource = EffectEvidenceSynthesis()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_use_context(self):
        resource = EffectEvidenceSynthesis()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = EffectEvidenceSynthesis()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_copyright(self):
        resource = EffectEvidenceSynthesis()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_approval_date(self):
        resource = EffectEvidenceSynthesis()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'approvalDate')
        assert result is not None

    def test_get_path_last_review_date(self):
        resource = EffectEvidenceSynthesis()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lastReviewDate')
        assert result is not None

    def test_get_path_effective_period(self):
        resource = EffectEvidenceSynthesis()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'effectivePeriod')
        assert result is not None

    def test_get_path_topic(self):
        resource = EffectEvidenceSynthesis()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'topic')
        assert result is not None

    def test_get_path_author(self):
        resource = EffectEvidenceSynthesis()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_editor(self):
        resource = EffectEvidenceSynthesis()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'editor')
        assert result is not None

    def test_get_path_reviewer(self):
        resource = EffectEvidenceSynthesis()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reviewer')
        assert result is not None

    def test_get_path_endorser(self):
        resource = EffectEvidenceSynthesis()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'endorser')
        assert result is not None

    def test_get_path_related_artifact(self):
        resource = EffectEvidenceSynthesis()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relatedArtifact')
        assert result is not None

    def test_get_path_synthesis_type(self):
        resource = EffectEvidenceSynthesis()
        resource.synthesisType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'synthesisType')
        assert result is not None

    def test_get_path_study_type(self):
        resource = EffectEvidenceSynthesis()
        resource.studyType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'studyType')
        assert result is not None

    def test_get_path_population(self):
        resource = EffectEvidenceSynthesis()
        resource.population = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'population')
        assert result is not None

    def test_get_path_exposure(self):
        resource = EffectEvidenceSynthesis()
        resource.exposure = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'exposure')
        assert result is not None

    def test_get_path_exposure_alternative(self):
        resource = EffectEvidenceSynthesis()
        resource.exposureAlternative = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'exposureAlternative')
        assert result is not None

    def test_get_path_outcome(self):
        resource = EffectEvidenceSynthesis()
        resource.outcome = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'outcome')
        assert result is not None

    def test_get_path_sample_size(self):
        resource = EffectEvidenceSynthesis()
        resource.sampleSize = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'sampleSize')
        assert result is not None

    def test_get_path_results_by_exposure(self):
        resource = EffectEvidenceSynthesis()
        resource.resultsByExposure = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'resultsByExposure')
        assert result is not None

    def test_get_path_effect_estimate(self):
        resource = EffectEvidenceSynthesis()
        resource.effectEstimate = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'effectEstimate')
        assert result is not None

    def test_get_path_certainty(self):
        resource = EffectEvidenceSynthesis()
        resource.certainty = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'certainty')
        assert result is not None


class TestSetPathEffectEvidenceSynthesis:

    def test_set_path_id(self):
        resource = EffectEvidenceSynthesis()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = EffectEvidenceSynthesis()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'EffectEvidenceSynthesis.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = EffectEvidenceSynthesis()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = EffectEvidenceSynthesis()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = EffectEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = EffectEvidenceSynthesis()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = EffectEvidenceSynthesis()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = EffectEvidenceSynthesis()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = EffectEvidenceSynthesis()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = EffectEvidenceSynthesis()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_identifier(self):
        resource = EffectEvidenceSynthesis()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_version(self):
        resource = EffectEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = EffectEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = EffectEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_status(self):
        resource = EffectEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_date(self):
        resource = EffectEvidenceSynthesis()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = EffectEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = EffectEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = EffectEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_note(self):
        resource = EffectEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_use_context(self):
        resource = EffectEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = EffectEvidenceSynthesis()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_copyright(self):
        resource = EffectEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_approval_date(self):
        resource = EffectEvidenceSynthesis()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'approvalDate', value)
        assert result is True
        assert resource.approvalDate is not None

    def test_set_path_last_review_date(self):
        resource = EffectEvidenceSynthesis()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lastReviewDate', value)
        assert result is True
        assert resource.lastReviewDate is not None

    def test_set_path_effective_period(self):
        resource = EffectEvidenceSynthesis()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'effectivePeriod', value)
        assert result is True
        assert resource.effectivePeriod is not None

    def test_set_path_topic(self):
        resource = EffectEvidenceSynthesis()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'topic', value)
        assert result is True
        assert resource.topic is not None

    def test_set_path_author(self):
        resource = EffectEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_editor(self):
        resource = EffectEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'editor', value)
        assert result is True
        assert resource.editor is not None

    def test_set_path_reviewer(self):
        resource = EffectEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reviewer', value)
        assert result is True
        assert resource.reviewer is not None

    def test_set_path_endorser(self):
        resource = EffectEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'endorser', value)
        assert result is True
        assert resource.endorser is not None

    def test_set_path_related_artifact(self):
        resource = EffectEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relatedArtifact', value)
        assert result is True
        assert resource.relatedArtifact is not None

    def test_set_path_synthesis_type(self):
        resource = EffectEvidenceSynthesis()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'synthesisType', value)
        assert result is True
        assert resource.synthesisType is not None

    def test_set_path_study_type(self):
        resource = EffectEvidenceSynthesis()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'studyType', value)
        assert result is True
        assert resource.studyType is not None

    def test_set_path_population(self):
        resource = EffectEvidenceSynthesis()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'population', value)
        assert result is True
        assert resource.population is not None

    def test_set_path_exposure(self):
        resource = EffectEvidenceSynthesis()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'exposure', value)
        assert result is True
        assert resource.exposure is not None

    def test_set_path_exposure_alternative(self):
        resource = EffectEvidenceSynthesis()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'exposureAlternative', value)
        assert result is True
        assert resource.exposureAlternative is not None

    def test_set_path_outcome(self):
        resource = EffectEvidenceSynthesis()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'outcome', value)
        assert result is True
        assert resource.outcome is not None

    def test_set_path_sample_size(self):
        resource = EffectEvidenceSynthesis()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'sampleSize', value)
        assert result is True
        assert resource.sampleSize is not None

    def test_set_path_results_by_exposure(self):
        resource = EffectEvidenceSynthesis()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'resultsByExposure', value)
        assert result is True
        assert resource.resultsByExposure is not None

    def test_set_path_effect_estimate(self):
        resource = EffectEvidenceSynthesis()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'effectEstimate', value)
        assert result is True
        assert resource.effectEstimate is not None

    def test_set_path_certainty(self):
        resource = EffectEvidenceSynthesis()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'certainty', value)
        assert result is True
        assert resource.certainty is not None


class TestParsePathEffectEvidenceSynthesis:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('EffectEvidenceSynthesis.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('EffectEvidenceSynthesis.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('EffectEvidenceSynthesis.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
