# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# local
import _agent
import _constants
import _diag
import _helpers
from _helpers import call_and_read_event as _call_and_read_event

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anytuple

# ################################################################################################################################
# ################################################################################################################################

# The IMEIs of the main record's devices, in the order the record lists them
_device_imeis = [
    _constants.Customer_IMEI_Compact,
    _constants.Customer_IMEI_Dashed,
    _constants.Customer_IMEI_Spaced,
    _constants.Customer_IMEI_Invalid,
]

# What the PII stage puts in place of the record's first IMEI with stable replacements on
_replacement_imei_stable = 'REPLACED_IMEI_1'

# ################################################################################################################################
# ################################################################################################################################

def _get_customer_record(
    zato_server:'anydict',
    url_path:'str',
    gateway_name:'str',
    customer_id:'str' = _constants.Customer_ID,
    ) -> 'anytuple':
    """ One call for a customer through the given gateway, returning the record
    and the audit data document of the call's event.
    """

    body, event_data = _call_and_read_event(
        zato_server, url_path, gateway_name,
        _constants.Service_Customer_Get, {'customer_id': customer_id})

    data = _helpers.get_result_data(body)

    out = data, event_data
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDataMasking:
    """ The masking stage replaces the whole value of every field a gateway names, whatever the value
    holds, and the audit trace counts how many fields it masked.
    """

# ################################################################################################################################

    def test_the_fields_of_a_set_are_masked(self, zato_server:'anydict') -> 'None':

        data, _event_data = _get_customer_record(zato_server, _constants.Path_Masking, _constants.Gateway_Masking)

        # The set's fields are masked at the top level ..
        assert data['email'] == _constants.Masked_Value, data
        assert data['city'] == _constants.Masked_Value, data

        # .. and inside every element of an array ..
        for device in data['devices']:
            assert device['imei'] == _constants.Masked_Value, data

        # .. while the fields the set does not name arrive as the service built them.
        assert data['name'] == _constants.Customer_Name, data
        assert data['devices'][0]['label'] == 'phone-main', data

        # No original value survives anywhere in the response.
        data_text = dumps(data)

        for value in [_constants.Customer_Email, _constants.Customer_City, *_device_imeis]:
            assert value not in data_text, data_text

# ################################################################################################################################

    def test_nested_objects_are_masked(self, zato_server:'anydict') -> 'None':

        data, _event_data = _get_customer_record(
            zato_server, _constants.Path_Masking, _constants.Gateway_Masking, _constants.Customer_ID_Japanese)

        # The IMEI two objects deep is masked like a top-level one
        assert data['profile']['device']['imei'] == _constants.Masked_Value, data
        assert _constants.Customer_IMEI_Japanese not in dumps(data), data

# ################################################################################################################################

    def test_an_excluded_field_is_delivered(self, zato_server:'anydict') -> 'None':

        data, _event_data = _get_customer_record(
            zato_server, _constants.Path_Masking_Custom, _constants.Gateway_Masking_Custom)

        # The exclusion is written in another case than the key and still leaves the city alone ..
        assert data['city'] == _constants.Customer_City, data

        # .. while the rest of the set is masked.
        assert data['email'] == _constants.Masked_Value, data

# ################################################################################################################################

    def test_custom_fields_are_masked_without_regard_to_case(self, zato_server:'anydict') -> 'None':

        data, _event_data = _get_customer_record(
            zato_server, _constants.Path_Masking_Custom, _constants.Gateway_Masking_Custom)

        # The custom fields are configured in another case than the record's keys
        assert data['name'] == _constants.Masked_Value, data
        assert data['network'] == _constants.Masked_Value, data
        assert _constants.Customer_IPv4 not in dumps(data), data

# ################################################################################################################################

    def test_custom_fields_switched_off_are_delivered(self, zato_server:'anydict') -> 'None':

        data, _event_data = _get_customer_record(
            zato_server, _constants.Path_Masking_Custom_Off, _constants.Gateway_Masking_Custom_Off)

        # The custom fields are kept in the configuration and not masked ..
        assert data['name'] == _constants.Customer_Name, data
        assert _constants.Customer_IPv4 in data['network'], data

        # .. while the set is masked as usual.
        assert data['email'] == _constants.Masked_Value, data

# ################################################################################################################################

    def test_masking_runs_ahead_of_pii_removal(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_Masking_PII, _constants.Gateway_Masking_PII)

        # The masked field holds the masking value, not a PII replacement ..
        assert data['email'] == _constants.Masked_Value, data

        # .. PII removal still finds what masking left in place ..
        assert data['devices'][0]['imei'] == _replacement_imei_stable, data

        # .. and the trace counts each stage on its own, the masked email never counted as PII.
        assert event_data['fields_masked'] == _constants.Masking_Count_PII, event_data
        assert 'email' not in event_data['pii_removed'], event_data

# ################################################################################################################################

    def test_the_trace_counts_the_masked_fields(self, zato_server:'anydict') -> 'None':

        _data, event_data = _get_customer_record(zato_server, _constants.Path_Masking, _constants.Gateway_Masking)
        assert event_data['fields_masked'] == _constants.Masking_Count_Set, event_data

        _data, event_data = _get_customer_record(
            zato_server, _constants.Path_Masking_Custom, _constants.Gateway_Masking_Custom)
        assert event_data['fields_masked'] == _constants.Masking_Count_Custom, event_data

# ################################################################################################################################

    def test_a_gateway_without_masking_delivers_everything(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_Main, _constants.Gateway_Main)

        assert data['email'] == _constants.Customer_Email, data
        assert data['city'] == _constants.Customer_City, data
        assert 'fields_masked' not in event_data, event_data

# ################################################################################################################################
# ################################################################################################################################

class TestMaskingThroughModel:
    """ The model wire - every chat request and the final answer carry the masking value only,
    never a value of a masked field.
    """

# ################################################################################################################################

    def test_masked_values_never_reach_the_model(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Masking)

        task = 'Fetch the record of customer CRM-1001 and tell me their name, email address, city and device IMEIs.'
        result = _agent.run_agent(client, task)

        # Every chat request the conversation sent is free of the masked values ..
        chat_requests = _diag.get_entries('chat_request')
        assert chat_requests, 'No chat requests were logged'

        masked_values = [_constants.Customer_Email, _constants.Customer_City, *_device_imeis]

        for entry in chat_requests:
            request_text = dumps(entry['payload'], ensure_ascii=False)

            for value in masked_values:
                assert value not in request_text, value

        # .. at least one of them carries the masking value itself ..
        all_requests_text = dumps(chat_requests, ensure_ascii=False)
        assert _constants.Masked_Value in all_requests_text, all_requests_text

        # .. the model still received what was not masked ..
        assert _helpers.text_contains(result.final_text, _constants.Customer_Name), result.final_text

        # .. and the final answer is as free of the masked values as the requests were.
        for value in masked_values:
            assert value not in result.final_text, result.final_text

# ################################################################################################################################
# ################################################################################################################################
