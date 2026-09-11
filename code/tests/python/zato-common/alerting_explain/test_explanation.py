# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.alerting.explain.explanation import parse_explanation
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

# The remediations a skill of the kind under test allows
_remediations = ['resubmit']

# A well-formed reply proposing the one allowed remediation.
_reply = dumps({
    'explanation': 'The remote server replied with HTTP 503 for every call in the window.',
    'confidence': 'high',
    'remediation': {'action': 'resubmit'},
})

# ################################################################################################################################
# ################################################################################################################################

class TestParseExplanation:

    def test_a_well_formed_reply_is_parsed_in_full(self) -> 'None':
        result = parse_explanation(_reply, _remediations)

        assert result['is_parsed'] is True
        assert result['explanation'] == 'The remote server replied with HTTP 503 for every call in the window.'
        assert result['confidence'] == 'high'
        assert result['remediation'] == {'action': 'resubmit'}

    def test_a_reply_wrapped_in_a_code_fence_is_parsed(self) -> 'None':
        fenced = '```json\n' + _reply + '\n```'

        result = parse_explanation(fenced, _remediations)

        assert result['is_parsed'] is True
        assert result['confidence'] == 'high'

    def test_a_prose_reply_is_kept_as_the_explanation(self) -> 'None':
        text = 'The connection appears to be down and a person should verify the address.'

        result = parse_explanation(text, _remediations)

        assert result['is_parsed'] is False
        assert result['explanation'] == text
        assert result['confidence'] == ''
        assert result['remediation'] is None

    def test_a_json_reply_that_is_not_an_object_is_kept_as_prose(self) -> 'None':
        result = parse_explanation('["not", "an", "object"]', _remediations)

        assert result['is_parsed'] is False
        assert result['remediation'] is None

    def test_an_unrecognized_confidence_level_is_dropped(self) -> 'None':
        reply = dumps({'explanation': 'Test explanation text.', 'confidence': 'absolutely certain'})

        result = parse_explanation(reply, _remediations)

        assert result['is_parsed'] is True
        assert result['confidence'] == ''

    def test_a_remediation_the_skill_does_not_name_is_dropped(self) -> 'None':
        reply = dumps({'explanation': 'Test explanation text.', 'remediation': {'action': 'delete-the-connection'}})

        result = parse_explanation(reply, _remediations)

        assert result['is_parsed'] is True
        assert result['remediation'] is None

    def test_a_skill_without_remediations_keeps_none(self) -> 'None':
        result = parse_explanation(_reply, [])

        assert result['is_parsed'] is True
        assert result['remediation'] is None

    def test_a_reply_without_a_explanation_is_kept_as_prose(self) -> 'None':
        reply = dumps({'confidence': 'high'})

        result = parse_explanation(reply, _remediations)

        assert result['is_parsed'] is False
        assert result['explanation'] == reply

# ################################################################################################################################
# ################################################################################################################################
