# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.incidents.diagnosis import build_prompt, parse_diagnosis
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

# A well-formed reply proposing the one allowed remediation.
_reply = dumps({
    'diagnosis': 'The remote server replied with HTTP 503 for every call in the window.',
    'confidence': 'high',
    'remediation': {'action': 'resubmit'},
})

# ################################################################################################################################
# ################################################################################################################################

class TestBuildPrompt:

    def test_the_prompt_carries_the_instructions_and_the_evidence(self) -> 'None':
        evidence = {'connection': {'name': 'CRM API'}, 'audit_trail': []}

        prompt = build_prompt('Diagnose the connection.', evidence)

        assert prompt.startswith('Diagnose the connection.')
        assert '# Evidence' in prompt
        assert 'CRM API' in prompt

# ################################################################################################################################
# ################################################################################################################################

class TestParseDiagnosis:

    def test_a_well_formed_reply_is_parsed_in_full(self) -> 'None':
        result = parse_diagnosis(_reply)

        assert result['is_parsed'] is True
        assert result['diagnosis'] == 'The remote server replied with HTTP 503 for every call in the window.'
        assert result['confidence'] == 'high'
        assert result['remediation'] == {'action': 'resubmit'}

    def test_a_reply_wrapped_in_a_code_fence_is_parsed(self) -> 'None':
        fenced = '```json\n' + _reply + '\n```'

        result = parse_diagnosis(fenced)

        assert result['is_parsed'] is True
        assert result['confidence'] == 'high'

    def test_a_prose_reply_is_kept_as_the_diagnosis(self) -> 'None':
        text = 'The connection appears to be down and a person should verify the address.'

        result = parse_diagnosis(text)

        assert result['is_parsed'] is False
        assert result['diagnosis'] == text
        assert result['confidence'] == ''
        assert result['remediation'] is None

    def test_a_json_reply_that_is_not_an_object_is_kept_as_prose(self) -> 'None':
        result = parse_diagnosis('["not", "an", "object"]')

        assert result['is_parsed'] is False
        assert result['remediation'] is None

    def test_an_unrecognized_confidence_level_is_dropped(self) -> 'None':
        reply = dumps({'diagnosis': 'Test diagnosis text.', 'confidence': 'absolutely certain'})

        result = parse_diagnosis(reply)

        assert result['is_parsed'] is True
        assert result['confidence'] == ''

    def test_a_remediation_outside_the_catalog_is_dropped(self) -> 'None':
        reply = dumps({'diagnosis': 'Test diagnosis text.', 'remediation': {'action': 'delete-the-connection'}})

        result = parse_diagnosis(reply)

        assert result['is_parsed'] is True
        assert result['remediation'] is None

    def test_a_reply_without_a_diagnosis_is_kept_as_prose(self) -> 'None':
        reply = dumps({'confidence': 'high'})

        result = parse_diagnosis(reply)

        assert result['is_parsed'] is False
        assert result['diagnosis'] == reply

# ################################################################################################################################
# ################################################################################################################################
