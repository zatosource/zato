# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ResearchStudy


class TestToDictResearchStudy:

    def test_to_dict_empty(self):
        resource = ResearchStudy()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ResearchStudy'

    def test_to_dict_with_id(self):
        resource = ResearchStudy()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ResearchStudy()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ResearchStudy)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ResearchStudy()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ResearchStudy()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ResearchStudy()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ResearchStudy()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ResearchStudy()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ResearchStudy()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ResearchStudy()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ResearchStudy()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = ResearchStudy()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_title(self):
        resource = ResearchStudy()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'title' in result

    def test_to_dict_protocol(self):
        resource = ResearchStudy()
        resource.protocol = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'protocol' in result

    def test_to_dict_part_of(self):
        resource = ResearchStudy()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'partOf' in result

    def test_to_dict_status(self):
        resource = ResearchStudy()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_primary_purpose_type(self):
        resource = ResearchStudy()
        resource.primaryPurposeType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'primaryPurposeType' in result

    def test_to_dict_phase(self):
        resource = ResearchStudy()
        resource.phase = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'phase' in result

    def test_to_dict_category(self):
        resource = ResearchStudy()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_focus(self):
        resource = ResearchStudy()
        resource.focus = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'focus' in result

    def test_to_dict_condition(self):
        resource = ResearchStudy()
        resource.condition = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'condition' in result

    def test_to_dict_contact(self):
        resource = ResearchStudy()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_related_artifact(self):
        resource = ResearchStudy()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relatedArtifact' in result

    def test_to_dict_keyword(self):
        resource = ResearchStudy()
        resource.keyword = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'keyword' in result

    def test_to_dict_location(self):
        resource = ResearchStudy()
        resource.location = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'location' in result

    def test_to_dict_description(self):
        resource = ResearchStudy()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'description' in result

    def test_to_dict_enrollment(self):
        resource = ResearchStudy()
        resource.enrollment = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'enrollment' in result

    def test_to_dict_period(self):
        resource = ResearchStudy()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'period' in result

    def test_to_dict_sponsor(self):
        resource = ResearchStudy()
        resource.sponsor = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'sponsor' in result

    def test_to_dict_principal_investigator(self):
        resource = ResearchStudy()
        resource.principalInvestigator = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'principalInvestigator' in result

    def test_to_dict_site(self):
        resource = ResearchStudy()
        resource.site = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'site' in result

    def test_to_dict_reason_stopped(self):
        resource = ResearchStudy()
        resource.reasonStopped = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonStopped' in result

    def test_to_dict_note(self):
        resource = ResearchStudy()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_arm(self):
        resource = ResearchStudy()
        resource.arm = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'arm' in result

    def test_to_dict_objective(self):
        resource = ResearchStudy()
        resource.objective = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'objective' in result


class TestFromDictResearchStudy:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ResearchStudy', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert isinstance(result, ResearchStudy)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ResearchStudy'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert isinstance(result, ResearchStudy)

    def test_from_dict_id(self):
        data = {'resourceType': 'ResearchStudy', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ResearchStudy', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ResearchStudy', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ResearchStudy', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ResearchStudy', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ResearchStudy', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ResearchStudy', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ResearchStudy', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'ResearchStudy', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.identifier is not None

    def test_from_dict_title(self):
        data = {'resourceType': 'ResearchStudy', 'title': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.title is not None

    def test_from_dict_protocol(self):
        data = {'resourceType': 'ResearchStudy', 'protocol': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.protocol is not None

    def test_from_dict_part_of(self):
        data = {'resourceType': 'ResearchStudy', 'partOf': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.partOf is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'ResearchStudy', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.status is not None

    def test_from_dict_primary_purpose_type(self):
        data = {'primaryPurposeType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                                'text': 'Test concept'},
         'resourceType': 'ResearchStudy'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.primaryPurposeType is not None

    def test_from_dict_phase(self):
        data = {'phase': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                   'text': 'Test concept'},
         'resourceType': 'ResearchStudy'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.phase is not None

    def test_from_dict_category(self):
        data = {'category': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'ResearchStudy'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.category is not None

    def test_from_dict_focus(self):
        data = {'focus': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                    'text': 'Test concept'}],
         'resourceType': 'ResearchStudy'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.focus is not None

    def test_from_dict_condition(self):
        data = {'condition': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                        'text': 'Test concept'}],
         'resourceType': 'ResearchStudy'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.condition is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'ResearchStudy', 'contact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.contact is not None

    def test_from_dict_related_artifact(self):
        data = {'resourceType': 'ResearchStudy', 'relatedArtifact': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.relatedArtifact is not None

    def test_from_dict_keyword(self):
        data = {'keyword': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                      'text': 'Test concept'}],
         'resourceType': 'ResearchStudy'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.keyword is not None

    def test_from_dict_location(self):
        data = {'location': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'ResearchStudy'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.location is not None

    def test_from_dict_description(self):
        data = {'resourceType': 'ResearchStudy', 'description': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.description is not None

    def test_from_dict_enrollment(self):
        data = {'resourceType': 'ResearchStudy', 'enrollment': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.enrollment is not None

    def test_from_dict_period(self):
        data = {'resourceType': 'ResearchStudy', 'period': {'start': '2024-01-01', 'end': '2024-12-31'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.period is not None

    def test_from_dict_sponsor(self):
        data = {'resourceType': 'ResearchStudy', 'sponsor': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.sponsor is not None

    def test_from_dict_principal_investigator(self):
        data = {'resourceType': 'ResearchStudy', 'principalInvestigator': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.principalInvestigator is not None

    def test_from_dict_site(self):
        data = {'resourceType': 'ResearchStudy', 'site': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.site is not None

    def test_from_dict_reason_stopped(self):
        data = {'reasonStopped': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'},
         'resourceType': 'ResearchStudy'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.reasonStopped is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'ResearchStudy', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.note is not None

    def test_from_dict_arm(self):
        data = {'resourceType': 'ResearchStudy', 'arm': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.arm is not None

    def test_from_dict_objective(self):
        data = {'resourceType': 'ResearchStudy', 'objective': [{'id': 'bb-1'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ResearchStudy)
        assert result.objective is not None


class TestGetPathResearchStudy:

    def test_get_path_id(self):
        resource = ResearchStudy()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ResearchStudy()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ResearchStudy()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ResearchStudy.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ResearchStudy()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ResearchStudy()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ResearchStudy()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ResearchStudy()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ResearchStudy()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ResearchStudy()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ResearchStudy()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = ResearchStudy()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_title(self):
        resource = ResearchStudy()
        resource.title = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'title')
        assert result is not None

    def test_get_path_protocol(self):
        resource = ResearchStudy()
        resource.protocol = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'protocol')
        assert result is not None

    def test_get_path_part_of(self):
        resource = ResearchStudy()
        resource.partOf = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'partOf')
        assert result is not None

    def test_get_path_status(self):
        resource = ResearchStudy()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_primary_purpose_type(self):
        resource = ResearchStudy()
        resource.primaryPurposeType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'primaryPurposeType')
        assert result is not None

    def test_get_path_phase(self):
        resource = ResearchStudy()
        resource.phase = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'phase')
        assert result is not None

    def test_get_path_category(self):
        resource = ResearchStudy()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_focus(self):
        resource = ResearchStudy()
        resource.focus = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'focus')
        assert result is not None

    def test_get_path_condition(self):
        resource = ResearchStudy()
        resource.condition = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'condition')
        assert result is not None

    def test_get_path_contact(self):
        resource = ResearchStudy()
        resource.contact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_related_artifact(self):
        resource = ResearchStudy()
        resource.relatedArtifact = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relatedArtifact')
        assert result is not None

    def test_get_path_keyword(self):
        resource = ResearchStudy()
        resource.keyword = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'keyword')
        assert result is not None

    def test_get_path_location(self):
        resource = ResearchStudy()
        resource.location = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'location')
        assert result is not None

    def test_get_path_description(self):
        resource = ResearchStudy()
        resource.description = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'description')
        assert result is not None

    def test_get_path_enrollment(self):
        resource = ResearchStudy()
        resource.enrollment = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'enrollment')
        assert result is not None

    def test_get_path_period(self):
        resource = ResearchStudy()
        resource.period = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'period')
        assert result is not None

    def test_get_path_sponsor(self):
        resource = ResearchStudy()
        resource.sponsor = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'sponsor')
        assert result is not None

    def test_get_path_principal_investigator(self):
        resource = ResearchStudy()
        resource.principalInvestigator = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'principalInvestigator')
        assert result is not None

    def test_get_path_site(self):
        resource = ResearchStudy()
        resource.site = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'site')
        assert result is not None

    def test_get_path_reason_stopped(self):
        resource = ResearchStudy()
        resource.reasonStopped = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonStopped')
        assert result is not None

    def test_get_path_note(self):
        resource = ResearchStudy()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_arm(self):
        resource = ResearchStudy()
        resource.arm = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'arm')
        assert result is not None

    def test_get_path_objective(self):
        resource = ResearchStudy()
        resource.objective = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'objective')
        assert result is not None


class TestSetPathResearchStudy:

    def test_set_path_id(self):
        resource = ResearchStudy()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ResearchStudy()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ResearchStudy.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ResearchStudy()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ResearchStudy()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ResearchStudy()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ResearchStudy()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ResearchStudy()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ResearchStudy()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ResearchStudy()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = ResearchStudy()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_title(self):
        resource = ResearchStudy()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'title', value)
        assert result is True
        assert resource.title is not None

    def test_set_path_protocol(self):
        resource = ResearchStudy()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'protocol', value)
        assert result is True
        assert resource.protocol is not None

    def test_set_path_part_of(self):
        resource = ResearchStudy()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'partOf', value)
        assert result is True
        assert resource.partOf is not None

    def test_set_path_status(self):
        resource = ResearchStudy()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_primary_purpose_type(self):
        resource = ResearchStudy()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'primaryPurposeType', value)
        assert result is True
        assert resource.primaryPurposeType is not None

    def test_set_path_phase(self):
        resource = ResearchStudy()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'phase', value)
        assert result is True
        assert resource.phase is not None

    def test_set_path_category(self):
        resource = ResearchStudy()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_focus(self):
        resource = ResearchStudy()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'focus', value)
        assert result is True
        assert resource.focus is not None

    def test_set_path_condition(self):
        resource = ResearchStudy()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'condition', value)
        assert result is True
        assert resource.condition is not None

    def test_set_path_contact(self):
        resource = ResearchStudy()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_related_artifact(self):
        resource = ResearchStudy()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relatedArtifact', value)
        assert result is True
        assert resource.relatedArtifact is not None

    def test_set_path_keyword(self):
        resource = ResearchStudy()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'keyword', value)
        assert result is True
        assert resource.keyword is not None

    def test_set_path_location(self):
        resource = ResearchStudy()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'location', value)
        assert result is True
        assert resource.location is not None

    def test_set_path_description(self):
        resource = ResearchStudy()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'description', value)
        assert result is True
        assert resource.description is not None

    def test_set_path_enrollment(self):
        resource = ResearchStudy()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'enrollment', value)
        assert result is True
        assert resource.enrollment is not None

    def test_set_path_period(self):
        resource = ResearchStudy()
        value = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'period', value)
        assert result is True
        assert resource.period is not None

    def test_set_path_sponsor(self):
        resource = ResearchStudy()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'sponsor', value)
        assert result is True
        assert resource.sponsor is not None

    def test_set_path_principal_investigator(self):
        resource = ResearchStudy()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'principalInvestigator', value)
        assert result is True
        assert resource.principalInvestigator is not None

    def test_set_path_site(self):
        resource = ResearchStudy()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'site', value)
        assert result is True
        assert resource.site is not None

    def test_set_path_reason_stopped(self):
        resource = ResearchStudy()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonStopped', value)
        assert result is True
        assert resource.reasonStopped is not None

    def test_set_path_note(self):
        resource = ResearchStudy()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_arm(self):
        resource = ResearchStudy()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'arm', value)
        assert result is True
        assert resource.arm is not None

    def test_set_path_objective(self):
        resource = ResearchStudy()
        value = [{'id': 'bb-1'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'objective', value)
        assert result is True
        assert resource.objective is not None


class TestParsePathResearchStudy:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ResearchStudy.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ResearchStudy.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ResearchStudy.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
