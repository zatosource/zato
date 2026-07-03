# zato: ide-skip

import zato.fhir_r4_0_1_core
from zato.fhir.r4_0_1.resources import Subscription


class TestToDictSubscription:

    def test_to_dict_empty(self):
        resource = Subscription()
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert isinstance(result, dict)
        assert result.get('resourceType') == 'Subscription'

    def test_to_dict_with_id(self):
        resource = Subscription()
        resource.id = 'test-id-123'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert result.get('id') == 'test-id-123'

    def test_to_dict_roundtrip(self):
        resource = Subscription()
        resource.id = 'roundtrip-test'
        dict1 = zato.fhir_r4_0_1_core.to_dict(resource)
        resource2 = zato.fhir_r4_0_1_core.from_dict(dict1, Subscription)
        dict2 = zato.fhir_r4_0_1_core.to_dict(resource2)
        assert dict1 == dict2

    def test_to_dict_id(self):
        resource = Subscription()
        resource.id = 'test-string-value'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'id' in result

    def test_to_dict_meta(self):
        resource = Subscription()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'meta' in result

    def test_to_dict_implicit_rules(self):
        resource = Subscription()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'implicitRules' in result

    def test_to_dict_language(self):
        resource = Subscription()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'language' in result

    def test_to_dict_text(self):
        resource = Subscription()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'text' in result

    def test_to_dict_contained(self):
        resource = Subscription()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contained' in result

    def test_to_dict_extension(self):
        resource = Subscription()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'extension' in result

    def test_to_dict_modifier_extension(self):
        resource = Subscription()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'modifierExtension' in result

    def test_to_dict_status(self):
        resource = Subscription()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'status' in result

    def test_to_dict_contact(self):
        resource = Subscription()
        resource.contact = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'contact' in result

    def test_to_dict_end(self):
        resource = Subscription()
        resource.end = '2024-01-15'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'end' in result

    def test_to_dict_reason(self):
        resource = Subscription()
        resource.reason = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'reason' in result

    def test_to_dict_criteria(self):
        resource = Subscription()
        resource.criteria = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'criteria' in result

    def test_to_dict_error(self):
        resource = Subscription()
        resource.error = 'active'
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'error' in result

    def test_to_dict_channel(self):
        resource = Subscription()
        resource.channel = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.to_dict(resource)
        assert 'channel' in result


class TestFromDictSubscription:

    def test_from_dict_minimal(self):
        data = {'resourceType': 'Subscription', 'id': 'test-123'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert isinstance(result, Subscription)
        assert result.id == 'test-123'

    def test_from_dict_empty(self):
        data = {'resourceType': 'Subscription'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert isinstance(result, Subscription)

    def test_from_dict_id(self):
        data = {'resourceType': 'Subscription', 'id': 'test-string-value'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert result.id is not None

    def test_from_dict_meta(self):
        data = {'resourceType': 'Subscription', 'meta': {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert result.meta is not None

    def test_from_dict_implicit_rules(self):
        data = {'resourceType': 'Subscription', 'implicitRules': 'http://example.org/test'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert result.implicitRules is not None

    def test_from_dict_language(self):
        data = {'resourceType': 'Subscription', 'language': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert result.language is not None

    def test_from_dict_text(self):
        data = {'resourceType': 'Subscription', 'text': {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert result.text is not None

    def test_from_dict_contained(self):
        data = {'resourceType': 'Subscription', 'contained': [{'resourceType': 'Basic', 'id': 'nested-resource'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert result.contained is not None

    def test_from_dict_extension(self):
        data = {'resourceType': 'Subscription', 'extension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert result.extension is not None

    def test_from_dict_modifier_extension(self):
        data = {'resourceType': 'Subscription', 'modifierExtension': [{'url': 'http://example.org/ext', 'valueString': 'test'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert result.modifierExtension is not None

    def test_from_dict_status(self):
        data = {'resourceType': 'Subscription', 'status': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert result.status is not None

    def test_from_dict_contact(self):
        data = {'resourceType': 'Subscription', 'contact': [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert result.contact is not None

    def test_from_dict_end(self):
        data = {'resourceType': 'Subscription', 'end': '2024-01-15'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert result.end is not None

    def test_from_dict_reason(self):
        data = {'resourceType': 'Subscription', 'reason': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert result.reason is not None

    def test_from_dict_criteria(self):
        data = {'resourceType': 'Subscription', 'criteria': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert result.criteria is not None

    def test_from_dict_error(self):
        data = {'resourceType': 'Subscription', 'error': 'active'}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert result.error is not None

    def test_from_dict_channel(self):
        data = {'resourceType': 'Subscription', 'channel': {'id': 'bb-1'}}
        result = zato.fhir_r4_0_1_core.from_dict(data, Subscription)
        assert result.channel is not None


class TestGetPathSubscription:

    def test_get_path_id(self):
        resource = Subscription()
        resource.id = 'path-test-id'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'id')
        assert result == 'path-test-id'

    def test_get_path_nonexistent(self):
        resource = Subscription()
        result = zato.fhir_r4_0_1_core.get_path(resource, 'nonexistent_field_xyz')
        assert result is None

    def test_get_path_with_resource_prefix(self):
        resource = Subscription()
        resource.id = 'prefix-test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'Subscription.id')
        assert result == 'prefix-test'

    def test_get_path_meta(self):
        resource = Subscription()
        resource.meta = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'meta')
        assert result is not None

    def test_get_path_implicit_rules(self):
        resource = Subscription()
        resource.implicitRules = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'implicitRules')
        assert result is not None

    def test_get_path_language(self):
        resource = Subscription()
        resource.language = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'language')
        assert result is not None

    def test_get_path_text(self):
        resource = Subscription()
        resource.text = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'text')
        assert result is not None

    def test_get_path_contained(self):
        resource = Subscription()
        resource.contained = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contained')
        assert result is not None

    def test_get_path_extension(self):
        resource = Subscription()
        resource.extension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'extension')
        assert result is not None

    def test_get_path_modifier_extension(self):
        resource = Subscription()
        resource.modifierExtension = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'modifierExtension')
        assert result is not None

    def test_get_path_status(self):
        resource = Subscription()
        resource.status = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'status')
        assert result is not None

    def test_get_path_contact(self):
        resource = Subscription()
        resource.contact = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.get_path(resource, 'contact')
        assert result is not None

    def test_get_path_end(self):
        resource = Subscription()
        resource.end = '2024-01-15'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'end')
        assert result is not None

    def test_get_path_reason(self):
        resource = Subscription()
        resource.reason = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'reason')
        assert result is not None

    def test_get_path_criteria(self):
        resource = Subscription()
        resource.criteria = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'criteria')
        assert result is not None

    def test_get_path_error(self):
        resource = Subscription()
        resource.error = 'active'
        result = zato.fhir_r4_0_1_core.get_path(resource, 'error')
        assert result is not None

    def test_get_path_channel(self):
        resource = Subscription()
        resource.channel = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.get_path(resource, 'channel')
        assert result is not None


class TestSetPathSubscription:

    def test_set_path_id(self):
        resource = Subscription()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'id', 'new-id-value')
        assert result is True
        assert resource.id == 'new-id-value'

    def test_set_path_with_resource_prefix(self):
        resource = Subscription()
        result = zato.fhir_r4_0_1_core.set_path(resource, 'Subscription.id', 'prefixed-id')
        assert result is True
        assert resource.id == 'prefixed-id'

    def test_set_path_meta(self):
        resource = Subscription()
        value = {'versionId': '1', 'lastUpdated': '2024-01-15T10:00:00Z'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'meta', value)
        assert result is True
        assert resource.meta is not None

    def test_set_path_implicit_rules(self):
        resource = Subscription()
        value = 'http://example.org/test'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'implicitRules', value)
        assert result is True
        assert resource.implicitRules is not None

    def test_set_path_language(self):
        resource = Subscription()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'language', value)
        assert result is True
        assert resource.language is not None

    def test_set_path_text(self):
        resource = Subscription()
        value = {'status': 'generated', 'div': '<div xmlns="http://www.w3.org/1999/xhtml">Test</div>'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'text', value)
        assert result is True
        assert resource.text is not None

    def test_set_path_contained(self):
        resource = Subscription()
        value = [{'resourceType': 'Basic', 'id': 'nested-resource'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contained', value)
        assert result is True
        assert resource.contained is not None

    def test_set_path_extension(self):
        resource = Subscription()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'extension', value)
        assert result is True
        assert resource.extension is not None

    def test_set_path_modifier_extension(self):
        resource = Subscription()
        value = [{'url': 'http://example.org/ext', 'valueString': 'test'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'modifierExtension', value)
        assert result is True
        assert resource.modifierExtension is not None

    def test_set_path_status(self):
        resource = Subscription()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'status', value)
        assert result is True
        assert resource.status is not None

    def test_set_path_contact(self):
        resource = Subscription()
        value = [{'system': 'phone', 'value': '555-1234', 'use': 'home'}]
        result = zato.fhir_r4_0_1_core.set_path(resource, 'contact', value)
        assert result is True
        assert resource.contact is not None

    def test_set_path_end(self):
        resource = Subscription()
        value = '2024-01-15'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'end', value)
        assert result is True
        assert resource.end is not None

    def test_set_path_reason(self):
        resource = Subscription()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'reason', value)
        assert result is True
        assert resource.reason is not None

    def test_set_path_criteria(self):
        resource = Subscription()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'criteria', value)
        assert result is True
        assert resource.criteria is not None

    def test_set_path_error(self):
        resource = Subscription()
        value = 'active'
        result = zato.fhir_r4_0_1_core.set_path(resource, 'error', value)
        assert result is True
        assert resource.error is not None

    def test_set_path_channel(self):
        resource = Subscription()
        value = {'id': 'bb-1'}
        result = zato.fhir_r4_0_1_core.set_path(resource, 'channel', value)
        assert result is True
        assert resource.channel is not None


class TestParsePathSubscription:

    def test_parse_path_simple(self):
        result = zato.fhir_r4_0_1_core.parse_path('id')
        assert len(result) == 1
        assert result[0]['type'] == 'field'
        assert result[0]['name'] == 'id'

    def test_parse_path_with_resource_prefix(self):
        result = zato.fhir_r4_0_1_core.parse_path('Subscription.id')
        assert len(result) == 1
        assert result[0]['name'] == 'id'

    def test_parse_path_nested(self):
        result = zato.fhir_r4_0_1_core.parse_path('Subscription.meta.versionId')
        assert len(result) == 2
        assert result[0]['name'] == 'meta'
        assert result[1]['name'] == 'versionId'

    def test_parse_path_with_index(self):
        result = zato.fhir_r4_0_1_core.parse_path('Subscription.identifier[0].value')
        assert len(result) == 3
        assert result[0]['name'] == 'identifier'
        assert result[1]['type'] == 'index'
        assert result[1]['index'] == 0
        assert result[2]['name'] == 'value'
