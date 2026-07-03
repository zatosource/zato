# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Measure


class TestToDictMeasure:

    def test_to_dict_empty(self):
        resource = Measure()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Measure'

    def test_to_dict_with_id(self):
        resource = Measure()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Measure()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Measure)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Measure()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Measure()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Measure()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Measure()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Measure()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Measure()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Measure()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Measure()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_url(self):
        resource = Measure()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'url' in result

    def test_to_dict_identifier(self):
        resource = Measure()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_version(self):
        resource = Measure()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'version' in result

    def test_to_dict_name(self):
        resource = Measure()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'name' in result

    def test_to_dict_title(self):
        resource = Measure()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_subtitle(self):
        resource = Measure()
        resource.subtitle = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subtitle' in result

    def test_to_dict_status(self):
        resource = Measure()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_experimental(self):
        resource = Measure()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'experimental' in result

    def test_to_dict_date(self):
        resource = Measure()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'date' in result

    def test_to_dict_publisher(self):
        resource = Measure()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'publisher' in result

    def test_to_dict_contact(self):
        resource = Measure()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_description(self):
        resource = Measure()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_use_context(self):
        resource = Measure()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'useContext' in result

    def test_to_dict_jurisdiction(self):
        resource = Measure()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'jurisdiction' in result

    def test_to_dict_purpose(self):
        resource = Measure()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'purpose' in result

    def test_to_dict_usage(self):
        resource = Measure()
        resource.usage = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'usage' in result

    def test_to_dict_copyright(self):
        resource = Measure()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'copyright' in result

    def test_to_dict_approval_date(self):
        resource = Measure()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'approvalDate' in result

    def test_to_dict_last_review_date(self):
        resource = Measure()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'lastReviewDate' in result

    def test_to_dict_effective_period(self):
        resource = Measure()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'effectivePeriod' in result

    def test_to_dict_topic(self):
        resource = Measure()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'topic' in result

    def test_to_dict_author(self):
        resource = Measure()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'author' in result

    def test_to_dict_editor(self):
        resource = Measure()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'editor' in result

    def test_to_dict_reviewer(self):
        resource = Measure()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reviewer' in result

    def test_to_dict_endorser(self):
        resource = Measure()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'endorser' in result

    def test_to_dict_related_artifact(self):
        resource = Measure()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relatedArtifact' in result

    def test_to_dict_library(self):
        resource = Measure()
        resource.library = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'library' in result

    def test_to_dict_disclaimer(self):
        resource = Measure()
        resource.disclaimer = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'disclaimer' in result

    def test_to_dict_scoring(self):
        resource = Measure()
        resource.scoring = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'scoring' in result

    def test_to_dict_composite_scoring(self):
        resource = Measure()
        resource.compositeScoring = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'compositeScoring' in result

    def test_to_dict_type(self):
        resource = Measure()
        resource.type_ = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'type' in result

    def test_to_dict_risk_adjustment(self):
        resource = Measure()
        resource.riskAdjustment = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'riskAdjustment' in result

    def test_to_dict_rate_aggregation(self):
        resource = Measure()
        resource.rateAggregation = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'rateAggregation' in result

    def test_to_dict_rationale(self):
        resource = Measure()
        resource.rationale = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'rationale' in result

    def test_to_dict_clinical_recommendation_statement(self):
        resource = Measure()
        resource.clinicalRecommendationStatement = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'clinicalRecommendationStatement' in result

    def test_to_dict_improvement_notation(self):
        resource = Measure()
        resource.improvementNotation = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'improvementNotation' in result

    def test_to_dict_definition(self):
        resource = Measure()
        resource.definition = ['active']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'definition' in result

    def test_to_dict_guidance(self):
        resource = Measure()
        resource.guidance = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'guidance' in result

    def test_to_dict_group(self):
        resource = Measure()
        resource.group = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'group' in result

    def test_to_dict_supplemental_data(self):
        resource = Measure()
        resource.supplementalData = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supplementalData' in result


class TestFromDictMeasure:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Measure', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert isinstance(result, Measure)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Measure'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert isinstance(result, Measure)

    def test_from_dict_id(self):
        data = {'resourceType': 'Measure', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Measure', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Measure', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Measure', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Measure', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Measure', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Measure', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Measure', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.modifierExtension is not None

    def test_from_dict_url(self):
        data = {'resourceType': 'Measure', 'url': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.url is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'Measure', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.identifier is not None

    def test_from_dict_version(self):
        data = {'resourceType': 'Measure', 'version': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.version is not None

    def test_from_dict_name(self):
        data = {'resourceType': 'Measure', 'name': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.name is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'Measure', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.title is not None

    def test_from_dict_subtitle(self):
        data = {'resourceType': 'Measure', 'subtitle': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.subtitle is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Measure', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.status is not None

    def test_from_dict_experimental(self):
        data = {'resourceType': 'Measure', 'experimental': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.experimental is not None

    def test_from_dict_date(self):
        data = {'resourceType': 'Measure', 'date': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.date is not None

    def test_from_dict_publisher(self):
        data = {'resourceType': 'Measure', 'publisher': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.publisher is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'Measure', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.contact is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'Measure', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.description is not None

    def test_from_dict_use_context(self):
        data = {'resourceType': 'Measure', 'useContext': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.useContext is not None

    def test_from_dict_jurisdiction(self):
        data = {'jurisdiction': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'Measure'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.jurisdiction is not None

    def test_from_dict_purpose(self):
        data = {'resourceType': 'Measure', 'purpose': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.purpose is not None

    def test_from_dict_usage(self):
        data = {'resourceType': 'Measure', 'usage': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.usage is not None

    def test_from_dict_copyright(self):
        data = {'resourceType': 'Measure', 'copyright': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.copyright is not None

    def test_from_dict_approval_date(self):
        data = {'resourceType': 'Measure', 'approvalDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.approvalDate is not None

    def test_from_dict_last_review_date(self):
        data = {'resourceType': 'Measure', 'lastReviewDate': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.lastReviewDate is not None

    def test_from_dict_effective_period(self):
        data = {'resourceType': 'Measure', 'effectivePeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.effectivePeriod is not None

    def test_from_dict_topic(self):
        data = {'resourceType': 'Measure',
         'topic': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.topic is not None

    def test_from_dict_author(self):
        data = {'resourceType': 'Measure', 'author': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.author is not None

    def test_from_dict_editor(self):
        data = {'resourceType': 'Measure', 'editor': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.editor is not None

    def test_from_dict_reviewer(self):
        data = {'resourceType': 'Measure', 'reviewer': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.reviewer is not None

    def test_from_dict_endorser(self):
        data = {'resourceType': 'Measure', 'endorser': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.endorser is not None

    def test_from_dict_related_artifact(self):
        data = {'resourceType': 'Measure', 'relatedArtifact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.relatedArtifact is not None

    def test_from_dict_library(self):
        data = {'resourceType': 'Measure', 'library': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.library is not None

    def test_from_dict_disclaimer(self):
        data = {'resourceType': 'Measure', 'disclaimer': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.disclaimer is not None

    def test_from_dict_scoring(self):
        data = {'resourceType': 'Measure',
         'scoring': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                     'text': 'Test concept'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.scoring is not None

    def test_from_dict_composite_scoring(self):
        data = {'compositeScoring': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                              'text': 'Test concept'},
         'resourceType': 'Measure'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.compositeScoring is not None

    def test_from_dict_type(self):
        data = {'resourceType': 'Measure',
         'type': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                   'text': 'Test concept'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.type_ is not None

    def test_from_dict_risk_adjustment(self):
        data = {'resourceType': 'Measure', 'riskAdjustment': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.riskAdjustment is not None

    def test_from_dict_rate_aggregation(self):
        data = {'resourceType': 'Measure', 'rateAggregation': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.rateAggregation is not None

    def test_from_dict_rationale(self):
        data = {'resourceType': 'Measure', 'rationale': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.rationale is not None

    def test_from_dict_clinical_recommendation_statement(self):
        data = {'resourceType': 'Measure', 'clinicalRecommendationStatement': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.clinicalRecommendationStatement is not None

    def test_from_dict_improvement_notation(self):
        data = {'improvementNotation': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                 'text': 'Test concept'},
         'resourceType': 'Measure'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.improvementNotation is not None

    def test_from_dict_definition(self):
        data = {'resourceType': 'Measure', 'definition': ['active']}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.definition is not None

    def test_from_dict_guidance(self):
        data = {'resourceType': 'Measure', 'guidance': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.guidance is not None

    def test_from_dict_group(self):
        data = {'resourceType': 'Measure', 'group': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.group is not None

    def test_from_dict_supplemental_data(self):
        data = {'resourceType': 'Measure', 'supplementalData': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Measure)
        assert result.supplementalData is not None


class TestGetPathMeasure:

    def test_get_path_id(self):
        resource = Measure()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Measure()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Measure()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Measure.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Measure()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Measure()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Measure()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Measure()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Measure()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Measure()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Measure()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_url(self):
        resource = Measure()
        resource.url = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'url')
        assert result is not None

    def test_get_path_identifier(self):
        resource = Measure()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_version(self):
        resource = Measure()
        resource.version = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'version')
        assert result is not None

    def test_get_path_name(self):
        resource = Measure()
        resource.name = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'name')
        assert result is not None

    def test_get_path_title(self):
        resource = Measure()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_subtitle(self):
        resource = Measure()
        resource.subtitle = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subtitle')
        assert result is not None

    def test_get_path_status(self):
        resource = Measure()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_experimental(self):
        resource = Measure()
        resource.experimental = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'experimental')
        assert result is not None

    def test_get_path_date(self):
        resource = Measure()
        resource.date = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'date')
        assert result is not None

    def test_get_path_publisher(self):
        resource = Measure()
        resource.publisher = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'publisher')
        assert result is not None

    def test_get_path_contact(self):
        resource = Measure()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_description(self):
        resource = Measure()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_use_context(self):
        resource = Measure()
        resource.useContext = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'useContext')
        assert result is not None

    def test_get_path_jurisdiction(self):
        resource = Measure()
        resource.jurisdiction = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'jurisdiction')
        assert result is not None

    def test_get_path_purpose(self):
        resource = Measure()
        resource.purpose = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'purpose')
        assert result is not None

    def test_get_path_usage(self):
        resource = Measure()
        resource.usage = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'usage')
        assert result is not None

    def test_get_path_copyright(self):
        resource = Measure()
        resource.copyright = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'copyright')
        assert result is not None

    def test_get_path_approval_date(self):
        resource = Measure()
        resource.approvalDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'approvalDate')
        assert result is not None

    def test_get_path_last_review_date(self):
        resource = Measure()
        resource.lastReviewDate = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'lastReviewDate')
        assert result is not None

    def test_get_path_effective_period(self):
        resource = Measure()
        resource.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'effectivePeriod')
        assert result is not None

    def test_get_path_topic(self):
        resource = Measure()
        resource.topic = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'topic')
        assert result is not None

    def test_get_path_author(self):
        resource = Measure()
        resource.author = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'author')
        assert result is not None

    def test_get_path_editor(self):
        resource = Measure()
        resource.editor = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'editor')
        assert result is not None

    def test_get_path_reviewer(self):
        resource = Measure()
        resource.reviewer = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reviewer')
        assert result is not None

    def test_get_path_endorser(self):
        resource = Measure()
        resource.endorser = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'endorser')
        assert result is not None

    def test_get_path_related_artifact(self):
        resource = Measure()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relatedArtifact')
        assert result is not None

    def test_get_path_library(self):
        resource = Measure()
        resource.library = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'library')
        assert result is not None

    def test_get_path_disclaimer(self):
        resource = Measure()
        resource.disclaimer = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'disclaimer')
        assert result is not None

    def test_get_path_scoring(self):
        resource = Measure()
        resource.scoring = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'scoring')
        assert result is not None

    def test_get_path_composite_scoring(self):
        resource = Measure()
        resource.compositeScoring = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'compositeScoring')
        assert result is not None

    def test_get_path_type(self):
        resource = Measure()
        resource.type_ = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'type')
        assert result is not None

    def test_get_path_risk_adjustment(self):
        resource = Measure()
        resource.riskAdjustment = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'riskAdjustment')
        assert result is not None

    def test_get_path_rate_aggregation(self):
        resource = Measure()
        resource.rateAggregation = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'rateAggregation')
        assert result is not None

    def test_get_path_rationale(self):
        resource = Measure()
        resource.rationale = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'rationale')
        assert result is not None

    def test_get_path_clinical_recommendation_statement(self):
        resource = Measure()
        resource.clinicalRecommendationStatement = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'clinicalRecommendationStatement')
        assert result is not None

    def test_get_path_improvement_notation(self):
        resource = Measure()
        resource.improvementNotation = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'improvementNotation')
        assert result is not None

    def test_get_path_definition(self):
        resource = Measure()
        resource.definition = ['active']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'definition')
        assert result is not None

    def test_get_path_guidance(self):
        resource = Measure()
        resource.guidance = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'guidance')
        assert result is not None

    def test_get_path_group(self):
        resource = Measure()
        resource.group = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'group')
        assert result is not None

    def test_get_path_supplemental_data(self):
        resource = Measure()
        resource.supplementalData = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supplementalData')
        assert result is not None


class TestSetPathMeasure:

    def test_set_path_id(self):
        resource = Measure()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Measure()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Measure.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Measure()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Measure()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Measure()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Measure()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Measure()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Measure()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_url(self):
        resource = Measure()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'url', value)
        assert result is True
        assert resource.url is not None

    def test_set_path_identifier(self):
        resource = Measure()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_version(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'version', value)
        assert result is True
        assert resource.version is not None

    def test_set_path_name(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'name', value)
        assert result is True
        assert resource.name is not None

    def test_set_path_title(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_subtitle(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subtitle', value)
        assert result is True
        assert resource.subtitle is not None

    def test_set_path_status(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_experimental(self):
        resource = Measure()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'experimental', value)
        assert result is True
        assert resource.experimental is not None

    def test_set_path_date(self):
        resource = Measure()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'date', value)
        assert result is True
        assert resource.date is not None

    def test_set_path_publisher(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'publisher', value)
        assert result is True
        assert resource.publisher is not None

    def test_set_path_contact(self):
        resource = Measure()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_description(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_use_context(self):
        resource = Measure()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'useContext', value)
        assert result is True
        assert resource.useContext is not None

    def test_set_path_jurisdiction(self):
        resource = Measure()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'jurisdiction', value)
        assert result is True
        assert resource.jurisdiction is not None

    def test_set_path_purpose(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'purpose', value)
        assert result is True
        assert resource.purpose is not None

    def test_set_path_usage(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'usage', value)
        assert result is True
        assert resource.usage is not None

    def test_set_path_copyright(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'copyright', value)
        assert result is True
        assert resource.copyright is not None

    def test_set_path_approval_date(self):
        resource = Measure()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'approvalDate', value)
        assert result is True
        assert resource.approvalDate is not None

    def test_set_path_last_review_date(self):
        resource = Measure()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'lastReviewDate', value)
        assert result is True
        assert resource.lastReviewDate is not None

    def test_set_path_effective_period(self):
        resource = Measure()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'effectivePeriod', value)
        assert result is True
        assert resource.effectivePeriod is not None

    def test_set_path_topic(self):
        resource = Measure()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'topic', value)
        assert result is True
        assert resource.topic is not None

    def test_set_path_author(self):
        resource = Measure()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'author', value)
        assert result is True
        assert resource.author is not None

    def test_set_path_editor(self):
        resource = Measure()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'editor', value)
        assert result is True
        assert resource.editor is not None

    def test_set_path_reviewer(self):
        resource = Measure()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reviewer', value)
        assert result is True
        assert resource.reviewer is not None

    def test_set_path_endorser(self):
        resource = Measure()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'endorser', value)
        assert result is True
        assert resource.endorser is not None

    def test_set_path_related_artifact(self):
        resource = Measure()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relatedArtifact', value)
        assert result is True
        assert resource.relatedArtifact is not None

    def test_set_path_library(self):
        resource = Measure()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'library', value)
        assert result is True
        assert resource.library is not None

    def test_set_path_disclaimer(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'disclaimer', value)
        assert result is True
        assert resource.disclaimer is not None

    def test_set_path_scoring(self):
        resource = Measure()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'scoring', value)
        assert result is True
        assert resource.scoring is not None

    def test_set_path_composite_scoring(self):
        resource = Measure()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'compositeScoring', value)
        assert result is True
        assert resource.compositeScoring is not None

    def test_set_path_type(self):
        resource = Measure()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'type', value)
        assert result is True
        assert resource.type_ is not None

    def test_set_path_risk_adjustment(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'riskAdjustment', value)
        assert result is True
        assert resource.riskAdjustment is not None

    def test_set_path_rate_aggregation(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'rateAggregation', value)
        assert result is True
        assert resource.rateAggregation is not None

    def test_set_path_rationale(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'rationale', value)
        assert result is True
        assert resource.rationale is not None

    def test_set_path_clinical_recommendation_statement(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'clinicalRecommendationStatement', value)
        assert result is True
        assert resource.clinicalRecommendationStatement is not None

    def test_set_path_improvement_notation(self):
        resource = Measure()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'improvementNotation', value)
        assert result is True
        assert resource.improvementNotation is not None

    def test_set_path_definition(self):
        resource = Measure()
        value = ['active']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'definition', value)
        assert result is True
        assert resource.definition is not None

    def test_set_path_guidance(self):
        resource = Measure()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'guidance', value)
        assert result is True
        assert resource.guidance is not None

    def test_set_path_group(self):
        resource = Measure()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'group', value)
        assert result is True
        assert resource.group is not None

    def test_set_path_supplemental_data(self):
        resource = Measure()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supplementalData', value)
        assert result is True
        assert resource.supplementalData is not None


class TestParsePathMeasure:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Measure.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Measure.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Measure.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
