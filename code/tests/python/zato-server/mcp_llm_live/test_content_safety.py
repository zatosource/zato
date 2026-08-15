# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
import _agent
import _audit
import _constants
import _helpers
from _helpers import call_and_read_event as _call_and_read_event

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anytuple

# ################################################################################################################################
# ################################################################################################################################

# The zero-width space the customer notes carry and the decomposed name they spell
_zero_width_space = '\u200b'
_decomposed_name = 'Mu\u0308ller'
_composed_name = 'M\u00fcller'

# What a final answer sounds like when the model reports that something did not work
_failure_words = ('cannot', 'could not', "couldn't", 'unable', 'fail', 'error', 'not possible', 'refused', 'rejected')

# What each rejection kind audits as
_reject_kind_unicode = 'unicode'
_reject_kind_url = 'url'

# What the two disallowed URLs of the customer notes read once they are defanged
_url_disallowed_neutralized = 'hxxps://tracking[.]invalid/pixel'
_url_lookalike_neutralized = 'hxxps://notexample[.]com/kb'

# The subdomain of the allowed host - the suffix rule passes it in every mode
_url_subdomain = 'https://api.example.com/kb'

# ################################################################################################################################
# ################################################################################################################################

def _contains_failure_word(text:'str') -> 'bool':
    """ Whether the text reports a failure in any of the usual wordings.
    """

    out = _helpers.contains_any_word(text, _failure_words)
    return out

# ################################################################################################################################

def _get_customer_call(zato_server:'anydict', url_path:'str', gateway_name:'str') -> 'anytuple':
    """ One customer call through the given gateway, returning the whole response body
    and the audit data document of the call's event.
    """

    out = _call_and_read_event(
        zato_server, url_path, gateway_name,
        _constants.Service_Customer_Get, {'customer_id': _constants.Customer_ID})

    return out

# ################################################################################################################################

def _get_customer_record(zato_server:'anydict', url_path:'str', gateway_name:'str') -> 'anytuple':
    """ One customer call through the given gateway, returning the record
    and the audit data document of the call's event.
    """

    body, event_data = _get_customer_call(zato_server, url_path, gateway_name)

    data = _helpers.get_result_data(body)

    out = data, event_data
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestContentSafety:
    """ Unicode normalization, markup sanitization and the URL policy each clean
    the content and count their findings - and stay silent when off.
    """

# ################################################################################################################################

    def test_unicode_is_normalized_and_counted(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_Safety, _constants.Gateway_Safety)

        notes = data['notes']

        # The zero-width character is gone and the decomposed name is composed now ..
        assert _zero_width_space not in notes, notes
        assert _composed_name in notes, notes
        assert _decomposed_name not in notes, notes

        # .. and only the character that had no business being there was counted.
        assert event_data['unicode_chars_removed'] == 1, event_data

# ################################################################################################################################

    def test_markup_is_sanitized_and_counted(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_Safety, _constants.Gateway_Safety)

        notes = data['notes']

        # The script element is gone from the notes ..
        assert '<script>' not in notes, notes

        # .. and the finding was counted.
        assert event_data['markup_items_removed'] >= 1, event_data

# ################################################################################################################################

    def test_the_url_policy_keeps_only_allowed_hosts(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_Safety, _constants.Gateway_Safety)

        notes = data['notes']

        # The allow-listed URL survives and the other one is handled per the remove mode ..
        assert _constants.Customer_URL_Allowed in notes, notes
        assert _constants.Customer_URL_Disallowed not in notes, notes

        # .. and exactly two URLs were flagged - the disallowed host and the lookalike host.
        assert event_data['urls_flagged'] == 2, event_data

# ################################################################################################################################

    def test_stages_off_leave_the_content_untouched(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_Main, _constants.Gateway_Main)

        notes = data['notes']

        # With every safety stage off, the notes come back as the service built them ..
        assert _zero_width_space in notes, notes
        assert _decomposed_name in notes, notes
        assert '<script>' in notes, notes
        assert _constants.Customer_URL_Allowed in notes, notes
        assert _constants.Customer_URL_Disallowed in notes, notes

        # .. and the audit event carries no safety keys at all.
        assert 'unicode_chars_removed' not in event_data, event_data
        assert 'markup_items_removed' not in event_data, event_data
        assert 'urls_flagged' not in event_data, event_data

# ################################################################################################################################
# ################################################################################################################################

class TestRejectModeWithLLM:
    """ Reject mode refuses the whole response and the model reports the refusal
    instead of describing data it never saw.
    """

# ################################################################################################################################

    def test_a_rejected_response_is_reported(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Safety_Reject)

        task = (
            f'What is the name of customer {_constants.Customer_ID}? Use the tools '
            'and if they cannot give you the data, say so plainly.')

        result = _agent.run_agent(client, task)

        # The gateway refused the customer record over its markup ..
        rejected_calls = []

        for call in result.tool_calls:
            if call.tool_name == _constants.Service_Customer_Get:
                if call.is_error:
                    rejected_calls.append(call)

        assert rejected_calls, result.messages
        assert 'markup' in rejected_calls[0].result_text.lower(), rejected_calls[0].result_text

        # .. the model reported the refusal and never learned the customer's name ..
        assert _contains_failure_word(result.final_text), result.final_text
        assert not _helpers.text_contains(result.final_text, _constants.Customer_Name), result.final_text

        # .. and the refusal is audited with its kind and an error outcome.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Safety_Reject,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        rejected_events = []

        for event in events:
            if event['data'].get('reject_kind') == 'markup':
                rejected_events.append(event)

        assert rejected_events, events
        assert rejected_events[0]['outcome'] == AuditOutcome.Error, rejected_events

# ################################################################################################################################
# ################################################################################################################################

class TestContentSafetyModes:
    """ The remaining safety modes and rules - unicode in reject mode, the two other
    URL modes, the suffix rule and the untouched clean payload.
    """

# ################################################################################################################################

    def test_unicode_reject_refuses(self, zato_server:'anydict') -> 'None':

        # The payload the clean gateway normalizes is refused whole here ..
        body, event_data = _get_customer_call(
            zato_server, _constants.Path_Unicode_Reject, _constants.Gateway_Unicode_Reject)

        result = body['result']
        assert result['isError'] is True, body

        text = _helpers.get_result_text(body)
        assert _reject_kind_unicode in text, body

        # .. with the unicode reject kind audited.
        assert event_data['reject_kind'] == _reject_kind_unicode, event_data

# ################################################################################################################################

    def test_the_two_other_url_modes(self, zato_server:'anydict') -> 'None':

        # The same disallowed URL is defanged under neutralize ..
        body, event_data = _get_customer_call(
            zato_server, _constants.Path_URL_Neutralize, _constants.Gateway_URL_Neutralize)

        data = _helpers.get_result_data(body)
        notes = data['notes']

        assert _url_disallowed_neutralized in notes, notes
        assert _constants.Customer_URL_Disallowed not in notes, notes

        assert event_data['urls_flagged'] == 2, event_data
        assert 'reject_kind' not in event_data, event_data

        # .. and refused whole under reject, each mode with its own trace.
        body, event_data = _get_customer_call(
            zato_server, _constants.Path_URL_Reject, _constants.Gateway_URL_Reject)

        result = body['result']
        assert result['isError'] is True, body

        text = _helpers.get_result_text(body)
        assert _reject_kind_url in text, body

        assert event_data['reject_kind'] == _reject_kind_url, event_data

# ################################################################################################################################

    def test_the_allow_list_matches_suffixes(self, zato_server:'anydict') -> 'None':

        body, _ = _get_customer_call(
            zato_server, _constants.Path_URL_Neutralize, _constants.Gateway_URL_Neutralize)

        data = _helpers.get_result_data(body)
        notes = data['notes']

        # A subdomain of the allowed host passes untouched ..
        assert _url_subdomain in notes, notes

        # .. while a host that merely ends with the same characters is defanged -
        # the rule matches suffixes at dot boundaries, not substrings.
        assert _url_lookalike_neutralized in notes, notes

# ################################################################################################################################

    def test_clean_content_is_untouched(self, zato_server:'anydict') -> 'None':

        # A payload violating nothing passes the everything-on safety gateway as it is ..
        body, event_data = _call_and_read_event(
            zato_server, _constants.Path_Safety, _constants.Gateway_Safety,
            _constants.Service_Order_Status, {'order_id': _constants.Order_ID})

        data = _helpers.get_result_data(body)

        expected = {
            'order_id': _constants.Order_ID,
            'status': _constants.Order_Status,
            'carrier': _constants.Order_Carrier,
            'eta_days': 3,
        }

        assert data == expected, data

        # .. with no safety trace keys in the audit event.
        assert 'unicode_chars_removed' not in event_data, event_data
        assert 'markup_items_removed' not in event_data, event_data
        assert 'urls_flagged' not in event_data, event_data
        assert 'reject_kind' not in event_data, event_data

# ################################################################################################################################
# ################################################################################################################################
