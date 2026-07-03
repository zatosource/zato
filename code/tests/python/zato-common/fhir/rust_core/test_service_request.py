# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import ServiceRequest


class TestToDictServiceRequest:

    def test_to_dict_empty(self):
        resource = ServiceRequest()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'ServiceRequest'

    def test_to_dict_with_id(self):
        resource = ServiceRequest()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = ServiceRequest()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, ServiceRequest)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = ServiceRequest()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = ServiceRequest()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = ServiceRequest()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = ServiceRequest()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = ServiceRequest()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = ServiceRequest()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = ServiceRequest()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = ServiceRequest()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_identifier(self):
        resource = ServiceRequest()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'identifier' in result

    def test_to_dict_instantiates_canonical(self):
        resource = ServiceRequest()
        resource.instantiatesCanonical = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesCanonical' in result

    def test_to_dict_instantiates_uri(self):
        resource = ServiceRequest()
        resource.instantiatesUri = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'instantiatesUri' in result

    def test_to_dict_based_on(self):
        resource = ServiceRequest()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'basedOn' in result

    def test_to_dict_replaces(self):
        resource = ServiceRequest()
        resource.replaces = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'replaces' in result

    def test_to_dict_requisition(self):
        resource = ServiceRequest()
        resource.requisition = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'requisition' in result

    def test_to_dict_status(self):
        resource = ServiceRequest()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_intent(self):
        resource = ServiceRequest()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'intent' in result

    def test_to_dict_category(self):
        resource = ServiceRequest()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'category' in result

    def test_to_dict_priority(self):
        resource = ServiceRequest()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'priority' in result

    def test_to_dict_do_not_perform(self):
        resource = ServiceRequest()
        resource.doNotPerform = True
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'doNotPerform' in result

    def test_to_dict_code(self):
        resource = ServiceRequest()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'code' in result

    def test_to_dict_order_detail(self):
        resource = ServiceRequest()
        resource.orderDetail = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'orderDetail' in result

    def test_to_dict_subject(self):
        resource = ServiceRequest()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'subject' in result

    def test_to_dict_encounter(self):
        resource = ServiceRequest()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'encounter' in result

    def test_to_dict_authored_on(self):
        resource = ServiceRequest()
        resource.authoredOn = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'authoredOn' in result

    def test_to_dict_requester(self):
        resource = ServiceRequest()
        resource.requester = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'requester' in result

    def test_to_dict_performer_type(self):
        resource = ServiceRequest()
        resource.performerType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performerType' in result

    def test_to_dict_performer(self):
        resource = ServiceRequest()
        resource.performer = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'performer' in result

    def test_to_dict_location_code(self):
        resource = ServiceRequest()
        resource.locationCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'locationCode' in result

    def test_to_dict_location_reference(self):
        resource = ServiceRequest()
        resource.locationReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'locationReference' in result

    def test_to_dict_reason_code(self):
        resource = ServiceRequest()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonCode' in result

    def test_to_dict_reason_reference(self):
        resource = ServiceRequest()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reasonReference' in result

    def test_to_dict_insurance(self):
        resource = ServiceRequest()
        resource.insurance = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'insurance' in result

    def test_to_dict_supporting_info(self):
        resource = ServiceRequest()
        resource.supportingInfo = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'supportingInfo' in result

    def test_to_dict_specimen(self):
        resource = ServiceRequest()
        resource.specimen = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'specimen' in result

    def test_to_dict_body_site(self):
        resource = ServiceRequest()
        resource.bodySite = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'bodySite' in result

    def test_to_dict_note(self):
        resource = ServiceRequest()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'note' in result

    def test_to_dict_patient_instruction(self):
        resource = ServiceRequest()
        resource.patientInstruction = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'patientInstruction' in result

    def test_to_dict_relevant_history(self):
        resource = ServiceRequest()
        resource.relevantHistory = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'relevantHistory' in result


class TestFromDictServiceRequest:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'ServiceRequest', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert isinstance(result, ServiceRequest)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'ServiceRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert isinstance(result, ServiceRequest)

    def test_from_dict_id(self):
        data = {'resourceType': 'ServiceRequest', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'ServiceRequest', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'ServiceRequest', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'ServiceRequest', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'ServiceRequest', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'ServiceRequest', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'ServiceRequest', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'ServiceRequest', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.modifierExtension is not None

    def test_from_dict_identifier(self):
        data = {'resourceType': 'ServiceRequest', 'identifier': [{'system': 'http://example.org/id', 'value': 'ID-12345'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.identifier is not None

    def test_from_dict_instantiates_canonical(self):
        data = {'resourceType': 'ServiceRequest', 'instantiatesCanonical': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.instantiatesCanonical is not None

    def test_from_dict_instantiates_uri(self):
        data = {'resourceType': 'ServiceRequest', 'instantiatesUri': ['http://example.org/test']}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.instantiatesUri is not None

    def test_from_dict_based_on(self):
        data = {'resourceType': 'ServiceRequest', 'basedOn': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.basedOn is not None

    def test_from_dict_replaces(self):
        data = {'resourceType': 'ServiceRequest', 'replaces': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.replaces is not None

    def test_from_dict_requisition(self):
        data = {'resourceType': 'ServiceRequest', 'requisition': {'system': 'http://example.org/id', 'value': 'ID-12345'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.requisition is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'ServiceRequest', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.status is not None

    def test_from_dict_intent(self):
        data = {'resourceType': 'ServiceRequest', 'intent': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.intent is not None

    def test_from_dict_category(self):
        data = {'category': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'ServiceRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.category is not None

    def test_from_dict_priority(self):
        data = {'resourceType': 'ServiceRequest', 'priority': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.priority is not None

    def test_from_dict_do_not_perform(self):
        data = {'resourceType': 'ServiceRequest', 'doNotPerform': True}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.doNotPerform is not None

    def test_from_dict_code(self):
        data = {'code': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}], 'text': 'Test concept'},
         'resourceType': 'ServiceRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.code is not None

    def test_from_dict_order_detail(self):
        data = {'orderDetail': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                          'text': 'Test concept'}],
         'resourceType': 'ServiceRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.orderDetail is not None

    def test_from_dict_subject(self):
        data = {'resourceType': 'ServiceRequest', 'subject': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.subject is not None

    def test_from_dict_encounter(self):
        data = {'resourceType': 'ServiceRequest', 'encounter': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.encounter is not None

    def test_from_dict_authored_on(self):
        data = {'resourceType': 'ServiceRequest', 'authoredOn': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.authoredOn is not None

    def test_from_dict_requester(self):
        data = {'resourceType': 'ServiceRequest', 'requester': {'reference': 'Patient/123', 'display': 'Test Patient'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.requester is not None

    def test_from_dict_performer_type(self):
        data = {'performerType': {'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'},
         'resourceType': 'ServiceRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.performerType is not None

    def test_from_dict_performer(self):
        data = {'resourceType': 'ServiceRequest', 'performer': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.performer is not None

    def test_from_dict_location_code(self):
        data = {'locationCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                           'text': 'Test concept'}],
         'resourceType': 'ServiceRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.locationCode is not None

    def test_from_dict_location_reference(self):
        data = {'resourceType': 'ServiceRequest', 'locationReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.locationReference is not None

    def test_from_dict_reason_code(self):
        data = {'reasonCode': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                         'text': 'Test concept'}],
         'resourceType': 'ServiceRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.reasonCode is not None

    def test_from_dict_reason_reference(self):
        data = {'resourceType': 'ServiceRequest', 'reasonReference': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.reasonReference is not None

    def test_from_dict_insurance(self):
        data = {'resourceType': 'ServiceRequest', 'insurance': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.insurance is not None

    def test_from_dict_supporting_info(self):
        data = {'resourceType': 'ServiceRequest', 'supportingInfo': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.supportingInfo is not None

    def test_from_dict_specimen(self):
        data = {'resourceType': 'ServiceRequest', 'specimen': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.specimen is not None

    def test_from_dict_body_site(self):
        data = {'bodySite': [{'coding': [{'code': 'test-code', 'display': 'Test', 'system': 'http://example.org'}],
                       'text': 'Test concept'}],
         'resourceType': 'ServiceRequest'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.bodySite is not None

    def test_from_dict_note(self):
        data = {'resourceType': 'ServiceRequest', 'note': [{'value': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.note is not None

    def test_from_dict_patient_instruction(self):
        data = {'resourceType': 'ServiceRequest', 'patientInstruction': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.patientInstruction is not None

    def test_from_dict_relevant_history(self):
        data = {'resourceType': 'ServiceRequest', 'relevantHistory': [{'reference': 'Patient/123', 'display': 'Test Patient'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, ServiceRequest)
        assert result.relevantHistory is not None


class TestGetPathServiceRequest:

    def test_get_path_id(self):
        resource = ServiceRequest()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = ServiceRequest()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = ServiceRequest()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'ServiceRequest.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = ServiceRequest()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = ServiceRequest()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = ServiceRequest()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = ServiceRequest()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = ServiceRequest()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = ServiceRequest()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = ServiceRequest()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_identifier(self):
        resource = ServiceRequest()
        resource.identifier = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'identifier')
        assert result is not None

    def test_get_path_instantiates_canonical(self):
        resource = ServiceRequest()
        resource.instantiatesCanonical = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesCanonical')
        assert result is not None

    def test_get_path_instantiates_uri(self):
        resource = ServiceRequest()
        resource.instantiatesUri = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.get_path(resource, 'instantiatesUri')
        assert result is not None

    def test_get_path_based_on(self):
        resource = ServiceRequest()
        resource.basedOn = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'basedOn')
        assert result is not None

    def test_get_path_replaces(self):
        resource = ServiceRequest()
        resource.replaces = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'replaces')
        assert result is not None

    def test_get_path_requisition(self):
        resource = ServiceRequest()
        resource.requisition = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'requisition')
        assert result is not None

    def test_get_path_status(self):
        resource = ServiceRequest()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_intent(self):
        resource = ServiceRequest()
        resource.intent = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'intent')
        assert result is not None

    def test_get_path_category(self):
        resource = ServiceRequest()
        resource.category = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'category')
        assert result is not None

    def test_get_path_priority(self):
        resource = ServiceRequest()
        resource.priority = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'priority')
        assert result is not None

    def test_get_path_do_not_perform(self):
        resource = ServiceRequest()
        resource.doNotPerform = True
        result = zato.fhir_r4_0_1_core.get_path(resource, 'doNotPerform')
        assert result is not None

    def test_get_path_code(self):
        resource = ServiceRequest()
        resource.code = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'code')
        assert result is not None

    def test_get_path_order_detail(self):
        resource = ServiceRequest()
        resource.orderDetail = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'orderDetail')
        assert result is not None

    def test_get_path_subject(self):
        resource = ServiceRequest()
        resource.subject = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'subject')
        assert result is not None

    def test_get_path_encounter(self):
        resource = ServiceRequest()
        resource.encounter = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'encounter')
        assert result is not None

    def test_get_path_authored_on(self):
        resource = ServiceRequest()
        resource.authoredOn = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'authoredOn')
        assert result is not None

    def test_get_path_requester(self):
        resource = ServiceRequest()
        resource.requester = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'requester')
        assert result is not None

    def test_get_path_performer_type(self):
        resource = ServiceRequest()
        resource.performerType = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performerType')
        assert result is not None

    def test_get_path_performer(self):
        resource = ServiceRequest()
        resource.performer = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'performer')
        assert result is not None

    def test_get_path_location_code(self):
        resource = ServiceRequest()
        resource.locationCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'locationCode')
        assert result is not None

    def test_get_path_location_reference(self):
        resource = ServiceRequest()
        resource.locationReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'locationReference')
        assert result is not None

    def test_get_path_reason_code(self):
        resource = ServiceRequest()
        resource.reasonCode = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonCode')
        assert result is not None

    def test_get_path_reason_reference(self):
        resource = ServiceRequest()
        resource.reasonReference = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reasonReference')
        assert result is not None

    def test_get_path_insurance(self):
        resource = ServiceRequest()
        resource.insurance = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'insurance')
        assert result is not None

    def test_get_path_supporting_info(self):
        resource = ServiceRequest()
        resource.supportingInfo = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'supportingInfo')
        assert result is not None

    def test_get_path_specimen(self):
        resource = ServiceRequest()
        resource.specimen = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'specimen')
        assert result is not None

    def test_get_path_body_site(self):
        resource = ServiceRequest()
        resource.bodySite = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'bodySite')
        assert result is not None

    def test_get_path_note(self):
        resource = ServiceRequest()
        resource.note = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'note')
        assert result is not None

    def test_get_path_patient_instruction(self):
        resource = ServiceRequest()
        resource.patientInstruction = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'patientInstruction')
        assert result is not None

    def test_get_path_relevant_history(self):
        resource = ServiceRequest()
        resource.relevantHistory = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'relevantHistory')
        assert result is not None


class TestSetPathServiceRequest:

    def test_set_path_id(self):
        resource = ServiceRequest()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = ServiceRequest()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'ServiceRequest.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = ServiceRequest()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = ServiceRequest()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = ServiceRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = ServiceRequest()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = ServiceRequest()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = ServiceRequest()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = ServiceRequest()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_identifier(self):
        resource = ServiceRequest()
        value = [{'system': 'http://example.org/id', 'value': 'ID-12345'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'identifier', value)
        assert result is True
        assert resource.identifier is not None

    def test_set_path_instantiates_canonical(self):
        resource = ServiceRequest()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesCanonical', value)
        assert result is True
        assert resource.instantiatesCanonical is not None

    def test_set_path_instantiates_uri(self):
        resource = ServiceRequest()
        value = ['http://example.org/test']
        result = zato.fhir_r4_0_1_core.set_path(resource, 'instantiatesUri', value)
        assert result is True
        assert resource.instantiatesUri is not None

    def test_set_path_based_on(self):
        resource = ServiceRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'basedOn', value)
        assert result is True
        assert resource.basedOn is not None

    def test_set_path_replaces(self):
        resource = ServiceRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'replaces', value)
        assert result is True
        assert resource.replaces is not None

    def test_set_path_requisition(self):
        resource = ServiceRequest()
        value = {'system': 'http://example.org/id', 'value': 'ID-12345'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'requisition', value)
        assert result is True
        assert resource.requisition is not None

    def test_set_path_status(self):
        resource = ServiceRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_intent(self):
        resource = ServiceRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'intent', value)
        assert result is True
        assert resource.intent is not None

    def test_set_path_category(self):
        resource = ServiceRequest()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'category', value)
        assert result is True
        assert resource.category is not None

    def test_set_path_priority(self):
        resource = ServiceRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'priority', value)
        assert result is True
        assert resource.priority is not None

    def test_set_path_do_not_perform(self):
        resource = ServiceRequest()
        value = True
        result = zato.fhir_r4_0_1_core.set_path(resource, 'doNotPerform', value)
        assert result is True
        assert resource.doNotPerform is not None

    def test_set_path_code(self):
        resource = ServiceRequest()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'code', value)
        assert result is True
        assert resource.code is not None

    def test_set_path_order_detail(self):
        resource = ServiceRequest()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'orderDetail', value)
        assert result is True
        assert resource.orderDetail is not None

    def test_set_path_subject(self):
        resource = ServiceRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'subject', value)
        assert result is True
        assert resource.subject is not None

    def test_set_path_encounter(self):
        resource = ServiceRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'encounter', value)
        assert result is True
        assert resource.encounter is not None

    def test_set_path_authored_on(self):
        resource = ServiceRequest()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'authoredOn', value)
        assert result is True
        assert resource.authoredOn is not None

    def test_set_path_requester(self):
        resource = ServiceRequest()
        value = {'reference': 'Patient/123', 'display': 'Test Patient'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'requester', value)
        assert result is True
        assert resource.requester is not None

    def test_set_path_performer_type(self):
        resource = ServiceRequest()
        value = {'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performerType', value)
        assert result is True
        assert resource.performerType is not None

    def test_set_path_performer(self):
        resource = ServiceRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'performer', value)
        assert result is True
        assert resource.performer is not None

    def test_set_path_location_code(self):
        resource = ServiceRequest()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'locationCode', value)
        assert result is True
        assert resource.locationCode is not None

    def test_set_path_location_reference(self):
        resource = ServiceRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'locationReference', value)
        assert result is True
        assert resource.locationReference is not None

    def test_set_path_reason_code(self):
        resource = ServiceRequest()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonCode', value)
        assert result is True
        assert resource.reasonCode is not None

    def test_set_path_reason_reference(self):
        resource = ServiceRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reasonReference', value)
        assert result is True
        assert resource.reasonReference is not None

    def test_set_path_insurance(self):
        resource = ServiceRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'insurance', value)
        assert result is True
        assert resource.insurance is not None

    def test_set_path_supporting_info(self):
        resource = ServiceRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'supportingInfo', value)
        assert result is True
        assert resource.supportingInfo is not None

    def test_set_path_specimen(self):
        resource = ServiceRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'specimen', value)
        assert result is True
        assert resource.specimen is not None

    def test_set_path_body_site(self):
        resource = ServiceRequest()
        value = [{'coding': [{'system': 'http://example.org', 'code': 'test-code', 'display': 'Test'}], 'text': 'Test concept'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'bodySite', value)
        assert result is True
        assert resource.bodySite is not None

    def test_set_path_note(self):
        resource = ServiceRequest()
        value = [{'value': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'note', value)
        assert result is True
        assert resource.note is not None

    def test_set_path_patient_instruction(self):
        resource = ServiceRequest()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'patientInstruction', value)
        assert result is True
        assert resource.patientInstruction is not None

    def test_set_path_relevant_history(self):
        resource = ServiceRequest()
        value = [{'reference': 'Patient/123', 'display': 'Test Patient'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'relevantHistory', value)
        assert result is True
        assert resource.relevantHistory is not None


class TestParsePathServiceRequest:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('ServiceRequest.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('ServiceRequest.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('ServiceRequest.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
