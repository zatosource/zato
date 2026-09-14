# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The negative acknowledgment codes an MLLP channel alerts on - the text a person types parses into the four
# HL7 codes in any case and refuses anything else, the matching counts sum the named codes alone, and the sweep's
# derivation reads a channel's own codes over the rule's default.

# pytest
import pytest

# Zato
from zato.common.alerting.ack_codes import apply_ack_codes, count_matching_acks, parse_ack_codes, Ack_Code_Counts_Key, \
    Ack_Count_Key
from zato.common.alerting.collectors.common import new_fact
from zato.common.alerting.config_map import Ack_Codes_Default
from zato.common.alerting.seed.rules_mllp import mllp_channel_rules
from zato.common.audit_log.api import AuditSource
from zato.common.rule_engine.loading import load_documents
from zato.common.rule_engine.parser import parse_data_details

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.models import Rule
    Rule = Rule

# ################################################################################################################################
# ################################################################################################################################

_ruleset_name = 'alerts_mllp_channel'
_channel_name = 'adt.intake'

# The codes the shipped rule alerts on - every negative one
_default_codes = ['AE', 'AR', 'CE', 'CR']

# ################################################################################################################################

def _load_rule(name:'str') -> 'Rule':
    """ One of the seeded MLLP channel rules as a runtime rule.
    """
    documents, errors = parse_data_details(mllp_channel_rules, _ruleset_name)
    assert errors == []

    loaded = load_documents(documents)

    out = loaded.manager[f'{_ruleset_name}_{name}']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestParseAckCodes:

    def test_the_codes_parse_with_whatever_spacing(self) -> 'None':
        assert parse_ack_codes('AE, AR, CE, CR') == _default_codes
        assert parse_ack_codes('AR,CR') == ['AR', 'CR']
        assert parse_ack_codes('  AE ') == ['AE']

    def test_the_case_does_not_matter(self) -> 'None':
        assert parse_ack_codes('ar, Cr') == ['AR', 'CR']

    def test_an_entry_is_kept_once(self) -> 'None':
        assert parse_ack_codes('AR, ar, CR') == ['AR', 'CR']

    def test_empty_entries_name_nothing(self) -> 'None':
        assert parse_ack_codes('') == []
        assert parse_ack_codes('AE,, AR,') == ['AE', 'AR']

    @pytest.mark.parametrize('text', ['AA', 'CA', '500', 'Receiver', 'exception', 'A', 'AER'])
    def test_anything_else_is_refused(self, text:'str') -> 'None':
        with pytest.raises(ValueError) as context:
            _ = parse_ack_codes(text)

        assert text.upper() in str(context.value)

# ################################################################################################################################
# ################################################################################################################################

class TestCountMatchingAcks:

    def test_the_counts_are_summed_by_the_named_codes_alone(self) -> 'None':
        ack_counts = {'AE': 2, 'AR': 1, 'CR': 3}

        matching = count_matching_acks(ack_counts, ['AR', 'CR'])

        assert matching == {'AR': 1, 'CR': 3}
        assert sum(matching.values()) == 4

    def test_nothing_matches_nothing(self) -> 'None':
        assert count_matching_acks({'AE': 4}, ['AR']) == {}
        assert count_matching_acks({}, ['AR']) == {}

# ################################################################################################################################
# ################################################################################################################################

class TestApplyAckCodes:

    def test_the_rules_default_codes_apply_when_the_channel_has_none_of_its_own(self) -> 'None':
        rule = _load_rule('Negative_Acks')

        fact = new_fact(AuditSource.MLLP_Channel, _channel_name)
        fact['fault_counts'] = {'AE': 2, 'AR': 1}

        derived = apply_ack_codes(fact, rule, {})

        # The default is every negative code
        assert derived[Ack_Count_Key] == 3
        assert derived[Ack_Code_Counts_Key] == {'AE': 2, 'AR': 1}

        # The fact handed in is left as it was, since every rule reads it
        assert fact[Ack_Count_Key] == 0
        assert fact[Ack_Code_Counts_Key] == {}

    def test_the_channels_own_codes_stand_in_for_the_default(self) -> 'None':
        rule = _load_rule('Negative_Acks')

        fact = new_fact(AuditSource.MLLP_Channel, _channel_name)
        fact['fault_counts'] = {'AE': 2, 'AR': 1}

        derived = apply_ack_codes(fact, rule, {Ack_Codes_Default: 'AR, CR'})

        assert derived[Ack_Count_Key] == 1
        assert derived[Ack_Code_Counts_Key] == {'AR': 1}

    def test_a_fact_without_ack_counts_is_handed_back_as_it_is(self) -> 'None':
        rule = _load_rule('Negative_Acks')
        fact = new_fact(AuditSource.MLLP_Channel, _channel_name)

        assert apply_ack_codes(fact, rule, {}) is fact

    def test_a_rule_without_ack_codes_is_not_its_business(self) -> 'None':
        rule = _load_rule('Error_Rate')

        fact = new_fact(AuditSource.MLLP_Channel, _channel_name)
        fact['fault_counts'] = {'AE': 4}

        assert apply_ack_codes(fact, rule, {}) is fact

# ################################################################################################################################
# ################################################################################################################################
