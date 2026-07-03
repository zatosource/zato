# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import RiskEvidenceSynthesis


class TestToDictRiskEvidenceSynthesis:

    def test_to_dict_empty(self):
        resource = RiskEvidenceSynthesis()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'RiskEvidenceSynthesis'

    def test_to_dict_with_id(self):
        resource = RiskEvidenceSynthesis()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = RiskEvidenceSynthesis()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, RiskEvidenceSynthesis)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = RiskEvidenceSynthesis()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = RiskEvidenceSynthesis()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = RiskEvidenceSynthesis()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = RiskEvidenceSynthesis()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = RiskEvidenceSynthesis()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = RiskEvidenceSynthesis()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = RiskEvidenceSynthesis()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = RiskEvidenceSynthesis()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = RiskEvidenceSynthesis()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_identifier(self):
        resource = RiskEvidenceSynthesis()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_version(self):
        resource = RiskEvidenceSynthesis()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = RiskEvidenceSynthesis()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = RiskEvidenceSynthesis()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_status(self):
        resource = RiskEvidenceSynthesis()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_date(self):
        resource = RiskEvidenceSynthesis()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = RiskEvidenceSynthesis()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = RiskEvidenceSynthesis()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = RiskEvidenceSynthesis()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_note(self):
        resource = RiskEvidenceSynthesis()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_use_context(self):
        resource = RiskEvidenceSynthesis()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = RiskEvidenceSynthesis()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_copyright(self):
        resource = RiskEvidenceSynthesis()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_approval_date(self):
        resource = RiskEvidenceSynthesis()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'approvalDate' in result

    def test_to_dict_last_review_date(self):
        resource = RiskEvidenceSynthesis()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lastReviewDate' in result

    def test_to_dict_effective_period(self):
        resource = RiskEvidenceSynthesis()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'effectivePeriod' in result

    def test_to_dict_topic(self):
        resource = RiskEvidenceSynthesis()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'topic' in result

    def test_to_dict_author(self):
        resource = RiskEvidenceSynthesis()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_editor(self):
        resource = RiskEvidenceSynthesis()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'editor' in result

    def test_to_dict_reviewer(self):
        resource = RiskEvidenceSynthesis()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reviewer' in result

    def test_to_dict_endorser(self):
        resource = RiskEvidenceSynthesis()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'endorser' in result

    def test_to_dict_related_artifact(self):
        resource = RiskEvidenceSynthesis()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relatedArtifact' in result

    def test_to_dict_synthesis_type(self):
        resource = RiskEvidenceSynthesis()
        resource.synthesisType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'synthesisType' in result

    def test_to_dict_study_type(self):
        resource = RiskEvidenceSynthesis()
        resource.studyType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'studyType' in result

    def test_to_dict_population(self):
        resource = RiskEvidenceSynthesis()
        resource.population = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'population' in result

    def test_to_dict_exposure(self):
        resource = RiskEvidenceSynthesis()
        resource.exposure = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'exposure' in result

    def test_to_dict_outcome(self):
        resource = RiskEvidenceSynthesis()
        resource.outcome = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'outcome' in result

    def test_to_dict_sample_size(self):
        resource = RiskEvidenceSynthesis()
        resource.sampleSize = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'sampleSize' in result

    def test_to_dict_risk_estimate(self):
        resource = RiskEvidenceSynthesis()
        resource.riskEstimate = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'riskEstimate' in result

    def test_to_dict_certainty(self):
        resource = RiskEvidenceSynthesis()
        resource.certainty = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'certainty' in result


class TestFromDictRiskEvidenceSynthesis:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert isinstance(result, RiskEvidenceSynthesis)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'RiskEvidenceSynthesis'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert isinstance(result, RiskEvidenceSynthesis)

    def test_from_dict_id(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.url is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.identifier is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.title is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.status is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.description is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.note is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'RiskEvidenceSynthesis'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.jurisdiction is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.copyright is not None

    def test_from_dict_approval_date(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'approvalDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.approvalDate is not None

    def test_from_dict_last_review_date(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'lastReviewDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.lastReviewDate is not None

    def test_from_dict_effective_period(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'effectivePeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.effectivePeriod is not None

    def test_from_dict_topic(self):
        data = {'resourceType': 'RiskEvidenceSynthesis',
         'topic': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.topic is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'author': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.author is not None

    def test_from_dict_editor(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'editor': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.editor is not None

    def test_from_dict_reviewer(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'reviewer': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.reviewer is not None

    def test_from_dict_endorser(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'endorser': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.endorser is not None

    def test_from_dict_related_artifact(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'relatedArtifact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.relatedArtifact is not None

    def test_from_dict_synthesis_type(self):
        data = {'resourceType': 'RiskEvidenceSynthesis',
         'synthesisType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.synthesisType is not None

    def test_from_dict_study_type(self):
        data = {'resourceType': 'RiskEvidenceSynthesis',
         'studyType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.studyType is not None

    def test_from_dict_population(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'population': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.population is not None

    def test_from_dict_exposure(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'exposure': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.exposure is not None

    def test_from_dict_outcome(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'outcome': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.outcome is not None

    def test_from_dict_sample_size(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'sampleSize': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.sampleSize is not None

    def test_from_dict_risk_estimate(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'riskEstimate': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.riskEstimate is not None

    def test_from_dict_certainty(self):
        data = {'resourceType': 'RiskEvidenceSynthesis', 'certainty': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, RiskEvidenceSynthesis)
        assert result.certainty is not None


class TestGetPathRiskEvidenceSynthesis:

    def test_get_path_id(self):
        resource = RiskEvidenceSynthesis()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = RiskEvidenceSynthesis()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = RiskEvidenceSynthesis()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'RiskEvidenceSynthesis.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = RiskEvidenceSynthesis()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = RiskEvidenceSynthesis()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = RiskEvidenceSynthesis()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = RiskEvidenceSynthesis()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = RiskEvidenceSynthesis()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = RiskEvidenceSynthesis()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = RiskEvidenceSynthesis()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = RiskEvidenceSynthesis()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_identifier(self):
        resource = RiskEvidenceSynthesis()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_version(self):
        resource = RiskEvidenceSynthesis()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = RiskEvidenceSynthesis()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = RiskEvidenceSynthesis()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_status(self):
        resource = RiskEvidenceSynthesis()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_date(self):
        resource = RiskEvidenceSynthesis()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = RiskEvidenceSynthesis()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = RiskEvidenceSynthesis()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = RiskEvidenceSynthesis()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_note(self):
        resource = RiskEvidenceSynthesis()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_use_context(self):
        resource = RiskEvidenceSynthesis()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = RiskEvidenceSynthesis()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_copyright(self):
        resource = RiskEvidenceSynthesis()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_approval_date(self):
        resource = RiskEvidenceSynthesis()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'approvalDate')
        assert result is not None

    def test_get_path_last_review_date(self):
        resource = RiskEvidenceSynthesis()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lastReviewDate')
        assert result is not None

    def test_get_path_effective_period(self):
        resource = RiskEvidenceSynthesis()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'effectivePeriod')
        assert result is not None

    def test_get_path_topic(self):
        resource = RiskEvidenceSynthesis()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'topic')
        assert result is not None

    def test_get_path_author(self):
        resource = RiskEvidenceSynthesis()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_editor(self):
        resource = RiskEvidenceSynthesis()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'editor')
        assert result is not None

    def test_get_path_reviewer(self):
        resource = RiskEvidenceSynthesis()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reviewer')
        assert result is not None

    def test_get_path_endorser(self):
        resource = RiskEvidenceSynthesis()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'endorser')
        assert result is not None

    def test_get_path_related_artifact(self):
        resource = RiskEvidenceSynthesis()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relatedArtifact')
        assert result is not None

    def test_get_path_synthesis_type(self):
        resource = RiskEvidenceSynthesis()
        resource.synthesisType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'synthesisType')
        assert result is not None

    def test_get_path_study_type(self):
        resource = RiskEvidenceSynthesis()
        resource.studyType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'studyType')
        assert result is not None

    def test_get_path_population(self):
        resource = RiskEvidenceSynthesis()
        resource.population = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'population')
        assert result is not None

    def test_get_path_exposure(self):
        resource = RiskEvidenceSynthesis()
        resource.exposure = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'exposure')
        assert result is not None

    def test_get_path_outcome(self):
        resource = RiskEvidenceSynthesis()
        resource.outcome = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'outcome')
        assert result is not None

    def test_get_path_sample_size(self):
        resource = RiskEvidenceSynthesis()
        resource.sampleSize = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'sampleSize')
        assert result is not None

    def test_get_path_risk_estimate(self):
        resource = RiskEvidenceSynthesis()
        resource.riskEstimate = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'riskEstimate')
        assert result is not None

    def test_get_path_certainty(self):
        resource = RiskEvidenceSynthesis()
        resource.certainty = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'certainty')
        assert result is not None


class TestSetPathRiskEvidenceSynthesis:

    def test_set_path_id(self):
        resource = RiskEvidenceSynthesis()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = RiskEvidenceSynthesis()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'RiskEvidenceSynthesis.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = RiskEvidenceSynthesis()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = RiskEvidenceSynthesis()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = RiskEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = RiskEvidenceSynthesis()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = RiskEvidenceSynthesis()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = RiskEvidenceSynthesis()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = RiskEvidenceSynthesis()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = RiskEvidenceSynthesis()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_identifier(self):
        resource = RiskEvidenceSynthesis()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_version(self):
        resource = RiskEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = RiskEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = RiskEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_status(self):
        resource = RiskEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_date(self):
        resource = RiskEvidenceSynthesis()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = RiskEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = RiskEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = RiskEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_note(self):
        resource = RiskEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_use_context(self):
        resource = RiskEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = RiskEvidenceSynthesis()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_copyright(self):
        resource = RiskEvidenceSynthesis()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_approval_date(self):
        resource = RiskEvidenceSynthesis()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'approvalDate', value)
        assert result is True
        assert resource.approvalDate is not None

    def test_set_path_last_review_date(self):
        resource = RiskEvidenceSynthesis()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lastReviewDate', value)
        assert result is True
        assert resource.lastReviewDate is not None

    def test_set_path_effective_period(self):
        resource = RiskEvidenceSynthesis()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'effectivePeriod', value)
        assert result is True
        assert resource.effectivePeriod is not None

    def test_set_path_topic(self):
        resource = RiskEvidenceSynthesis()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'topic', value)
        assert result is True
        assert resource.topic is not None

    def test_set_path_author(self):
        resource = RiskEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_editor(self):
        resource = RiskEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'editor', value)
        assert result is True
        assert resource.editor is not None

    def test_set_path_reviewer(self):
        resource = RiskEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reviewer', value)
        assert result is True
        assert resource.reviewer is not None

    def test_set_path_endorser(self):
        resource = RiskEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'endorser', value)
        assert result is True
        assert resource.endorser is not None

    def test_set_path_related_artifact(self):
        resource = RiskEvidenceSynthesis()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relatedArtifact', value)
        assert result is True
        assert resource.relatedArtifact is not None

    def test_set_path_synthesis_type(self):
        resource = RiskEvidenceSynthesis()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'synthesisType', value)
        assert result is True
        assert resource.synthesisType is not None

    def test_set_path_study_type(self):
        resource = RiskEvidenceSynthesis()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'studyType', value)
        assert result is True
        assert resource.studyType is not None

    def test_set_path_population(self):
        resource = RiskEvidenceSynthesis()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'population', value)
        assert result is True
        assert resource.population is not None

    def test_set_path_exposure(self):
        resource = RiskEvidenceSynthesis()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'exposure', value)
        assert result is True
        assert resource.exposure is not None

    def test_set_path_outcome(self):
        resource = RiskEvidenceSynthesis()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'outcome', value)
        assert result is True
        assert resource.outcome is not None

    def test_set_path_sample_size(self):
        resource = RiskEvidenceSynthesis()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'sampleSize', value)
        assert result is True
        assert resource.sampleSize is not None

    def test_set_path_risk_estimate(self):
        resource = RiskEvidenceSynthesis()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'riskEstimate', value)
        assert result is True
        assert resource.riskEstimate is not None

    def test_set_path_certainty(self):
        resource = RiskEvidenceSynthesis()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'certainty', value)
        assert result is True
        assert resource.certainty is not None


class TestParsePathRiskEvidenceSynthesis:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('RiskEvidenceSynthesis.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('RiskEvidenceSynthesis.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('RiskEvidenceSynthesis.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
