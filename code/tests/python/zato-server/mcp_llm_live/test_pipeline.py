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

# Zato
from zato.common.util.safeguards.common import Base64_Marker_Template
from zato.common.util.truncate.common import Truncation_Marker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# A roster of this many customers goes over the pipeline gateways' cap
_oversized_count = '100'

# The replacement every email of the roster turns into - the pipeline gateways
# use the default replacement format
_email_token_prefix = '{{EMAIL_'

# A truncated text must never end inside a replacement token
_dangling_token = re.compile(r'\{\{[A-Z0-9_]*$')

# A complete replacement token, e.g. {{EMAIL_1}}
_whole_token = re.compile(r'\{\{[A-Z0-9_]+\}\}')

# What the markup rejection audits as
_reject_kind_markup = 'markup'

# The detector name and the first stable replacement of the one email
# the mixed-script record carries
_detector_email = 'intl_email'
_token_email_first = '{{EMAIL_1}}'

# The code point range UTF-16 surrogates occupy - a lone one means half an astral character
_surrogate_first = 0xD800
_surrogate_last  = 0xDFFF

# The avatar blob as the fixture builds it - the base64 marker must name exactly its length
_avatar_blob = 'data:image/png;base64,' + 'QUJDREVG' * 40

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

        # .. every one of them whole - each opening starts a complete token
        # and the cut never ends inside one.
        opening_count = text.count('{{')
        whole_tokens = _whole_token.findall(text)

        assert opening_count == len(whole_tokens), text
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

class TestScriptsThroughThePipeline:
    """ Multi-script data through the cut and through every stage at once - the truncation
    boundary never splits a character and a mixed-script record is exact end to end.
    """

# ################################################################################################################################

    def test_truncation_never_splits_a_character(self, zato_server:'anydict') -> 'None':

        body, event_data = _call_and_read_event(
            zato_server, _constants.Path_Shaping_Truncate, _constants.Gateway_Shaping_Truncate,
            _constants.Service_Customer_Get, {'customer_id': _constants.Customer_ID_Reactions})

        assert event_data['was_truncated'] is True, event_data

        # The whole content is valid text - no half of an astral character anywhere,
        # which is the only way a code point can break in transit ..
        text = _helpers.get_result_text(body)

        for character in text:
            assert not _surrogate_first <= ord(character) <= _surrogate_last, hex(ord(character))

        _ = text.encode('utf8')

        # .. and the cut field consists of whole reaction tokens alone - the emoji,
        # the skin-tone pair, the joiner sequence, the diacritics and the combining
        # sequence each survive complete or are gone complete, plus the end marker.
        data = _helpers.get_result_data(body)
        reactions = data['reactions']

        suffix = ' ' + Truncation_Marker
        assert reactions.endswith(suffix), reactions[-64:]

        kept_tokens = reactions[:-len(suffix)].split(' ')
        assert kept_tokens, reactions[:64]

        for token in kept_tokens:
            assert token in _constants.Reaction_Tokens, repr(token)

# ################################################################################################################################

    def test_a_mixed_script_response_through_every_stage(self, zato_server:'anydict') -> 'None':

        body, event_data = _call_and_read_event(
            zato_server, _constants.Path_Pipeline, _constants.Gateway_Pipeline,
            _constants.Service_Customer_Get, {'customer_id': _constants.Customer_ID_Mixed})

        data = _helpers.get_result_data(body)

        # The record is deterministic end to end - the multi-script fields nothing applied
        # to decode to their original values byte for byte, and every touched field
        # reads exactly what its one stage leaves behind.
        expected = {
            'name': _constants.Customer_Name_Mixed,
            'city': _constants.Customer_City_Mixed,
            'motto': _constants.Customer_Motto_Mixed,
            'note': _constants.Customer_Note_Mixed_Collapsed,
            'email': _token_email_first,
            'banner': _constants.Customer_Banner_Mixed_Clean,
            'links': _constants.Customer_Links_Mixed_Clean,
            'attachment': Base64_Marker_Template.format(size=len(_avatar_blob)),
            'customer_id': _constants.Customer_ID_Mixed,
            'found': True,
        }

        assert data == expected, data

        # Every stage's trace is exact - one null, the note's two whitespace runs,
        # one blob, one email, one script element and one disallowed URL.
        assert event_data['nulls_removed'] == 1, event_data
        assert event_data['whitespace_chars_removed'] == _constants.Mixed_Whitespace_Removed, event_data
        assert event_data['base64_blobs_removed'] == 1, event_data
        assert event_data['pii_removed'] == {_detector_email: 1}, event_data
        assert event_data['markup_items_removed'] == 1, event_data
        assert event_data['urls_flagged'] == 1, event_data

        # Nothing else ran - no smuggled characters, no truncation, no rejection.
        assert 'unicode_chars_removed' not in event_data, event_data
        assert 'was_truncated' not in event_data, event_data
        assert 'reject_kind' not in event_data, event_data

# ################################################################################################################################
# ################################################################################################################################
