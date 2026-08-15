# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re

# local
import _constants
import _helpers
from _helpers import call_and_read_event as _call_and_read_event

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# A roster of this many customers goes over the pipeline gateways' cap
_oversized_count = '100'

# The token every tokenized email of the roster starts with
_email_token_prefix = '{{INTL_EMAIL'

# A truncated text must never end inside a replacement token
_dangling_token = re.compile(r'\{\{[A-Z0-9_]*$')

# What the markup rejection audits as
_reject_kind_markup = 'markup'

# ################################################################################################################################
# ################################################################################################################################

class TestPipelineInterplay:
    """ How the pipeline's stages compose - one response through every stage at once,
    filters after safeguards, filters against the cap, the cut's boundary
    and the one-rejection rule.
    """

# ################################################################################################################################

    def test_one_response_through_every_stage_at_once(self, zato_server:'anydict') -> 'None':

        body, event_data = _call_and_read_event(
            zato_server, _constants.Path_Pipeline, _constants.Gateway_Pipeline,
            _constants.Service_Customer_List, {'count': _oversized_count})

        # Every stage found something and left its trace keys in the one event ..
        assert event_data['nulls_removed'] == int(_oversized_count), event_data
        assert event_data['whitespace_chars_removed'] > 0, event_data
        assert event_data['base64_blobs_removed'] == 1, event_data
        assert event_data['pii_removed'], event_data
        assert event_data['markup_items_removed'] >= 1, event_data
        assert event_data['urls_flagged'] >= 1, event_data

        # .. the sizes are consistent with the order compaction, PII, safety, shaping ..
        assert event_data['was_truncated'] is True, event_data
        assert event_data['tokens_after'] <= _constants.Pipeline_Cap_Tokens, event_data
        assert event_data['tokens_before'] > _constants.Pipeline_Cap_Tokens, event_data

        # .. and what the client received is the shaped result, replacements included.
        text = _helpers.get_result_text(body)
        assert _email_token_prefix in text, text

# ################################################################################################################################

    def test_client_filters_run_after_safeguards(self, zato_server:'anydict') -> 'None':

        arguments = {
            'customer_id': _constants.Customer_ID,
            'response_filter': 'email',
        }

        body, event_data = _call_and_read_event(
            zato_server, _constants.Path_Pipeline, _constants.Gateway_Pipeline,
            _constants.Service_Customer_Get, arguments)

        # The projection of the email field returns its replacement, never the raw value ..
        text = _helpers.get_result_text(body)

        assert _email_token_prefix in text, text
        assert _constants.Customer_Email not in text, text

        # .. and the trace records both the removal and the filter.
        assert event_data['pii_removed'], event_data
        assert event_data['client_filter'] == 'email', event_data

# ################################################################################################################################

    def test_a_filter_can_make_truncation_unnecessary(self, zato_server:'anydict') -> 'None':

        # The oversized call truncates when no filter shapes it ..
        _, event_data = _call_and_read_event(
            zato_server, _constants.Path_Pipeline, _constants.Gateway_Pipeline,
            _constants.Service_Customer_List, {'count': _oversized_count})

        assert event_data['was_truncated'] is True, event_data

        # .. and passes untruncated when the filter projects it below the cap.
        arguments = {
            'count': _oversized_count,
            'response_filter': 'count',
        }

        body, event_data = _call_and_read_event(
            zato_server, _constants.Path_Pipeline, _constants.Gateway_Pipeline,
            _constants.Service_Customer_List, arguments)

        text = _helpers.get_result_text(body)
        assert text == _oversized_count, text

        assert event_data['client_filter'] == 'count', event_data
        assert 'was_truncated' not in event_data, event_data

# ################################################################################################################################

    def test_truncation_never_cuts_a_token_in_half(self, zato_server:'anydict') -> 'None':

        body, event_data = _call_and_read_event(
            zato_server, _constants.Path_PII_Truncate, _constants.Gateway_PII_Truncate,
            _constants.Service_Customer_List, {'count': _oversized_count})

        assert event_data['was_truncated'] is True, event_data

        # The truncated content carries replacement tokens ..
        text = _helpers.get_result_text(body)
        assert _email_token_prefix in text, text

        # .. every one of them whole - openings and closings pair up
        # and the cut never ends inside one.
        opening_count = text.count('{{')
        closing_count = text.count('}}')

        assert opening_count == closing_count, text
        assert not _dangling_token.search(text), text

# ################################################################################################################################

    def test_one_rejection_one_kind(self, zato_server:'anydict') -> 'None':

        body, event_data = _call_and_read_event(
            zato_server, _constants.Path_Reject_Both, _constants.Gateway_Reject_Both,
            _constants.Service_Customer_List, {'count': _oversized_count})

        # The client sees exactly one error, named after the earlier stage ..
        result = body['result']
        assert result['isError'] is True, body

        text = _helpers.get_result_text(body)
        assert _reject_kind_markup in text, text

        # .. and the audit event carries exactly one rejection kind -
        # the cap never ran, so no size keys are in the trace.
        assert event_data['reject_kind'] == _reject_kind_markup, event_data
        assert 'tokens_before' not in event_data, event_data

# ################################################################################################################################
# ################################################################################################################################
