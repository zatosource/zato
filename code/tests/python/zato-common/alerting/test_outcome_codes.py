# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The OperationOutcome issue codes an outgoing FHIR connection alerts on - the text a person types parses into
# FHIR IssueType codes and refuses anything else, the matching counts sum the named codes alone, and the sweep's
# derivation reads a connection's own codes over the rule's default.

# pytest
import pytest

# Zato
from zato.common.alerting.collectors.common import new_fact
from zato.common.alerting.config_map import Outcome_Codes_Default
from zato.common.alerting.outcome_codes import apply_outcome_codes, count_matching_outcomes, parse_outcome_codes, \
    Outcome_Code_Counts_Key, Outcome_Count_Key
from zato.common.alerting.seed.rules_fhir import fhir_rules
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

_ruleset_name = 'alerts_fhir'
_conn_name = 'ehr.fhir'

# The codes the shipped rule alerts on - the ones that say the server itself is in trouble
_default_codes = ['exception', 'transient', 'timeout', 'throttled', 'lock-error', 'no-store', 'too-costly']

# ################################################################################################################################

def _load_rule(name:'str') -> 'Rule':
    """ One of the seeded fhir rules as a runtime rule.
    """
    documents, errors = parse_data_details(fhir_rules, _ruleset_name)
    assert errors == []

    loaded = load_documents(documents)

    out = loaded.manager[f'{_ruleset_name}_{name}']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestParseOutcomeCodes:

    def test_the_issue_codes_parse_with_whatever_spacing(self) -> 'None':
        assert parse_outcome_codes('exception, not-found, too-costly') == ['exception', 'not-found', 'too-costly']
        assert parse_outcome_codes('exception,timeout') == ['exception', 'timeout']
        assert parse_outcome_codes('  exception ') == ['exception']
        assert parse_outcome_codes(', '.join(_default_codes)) == _default_codes

    def test_an_entry_is_kept_once(self) -> 'None':
        assert parse_outcome_codes('exception, exception, timeout') == ['exception', 'timeout']

    def test_empty_entries_name_nothing(self) -> 'None':
        assert parse_outcome_codes('') == []
        assert parse_outcome_codes('exception,, timeout,') == ['exception', 'timeout']

    @pytest.mark.parametrize('text', ['500', '5xx', 'Receiver', 'Not Found', 'not found', '-found', 'x:Timeout', 'not_found'])
    def test_anything_else_is_refused(self, text:'str') -> 'None':
        with pytest.raises(ValueError) as context:
            _ = parse_outcome_codes(text)

        assert text in str(context.value)

# ################################################################################################################################
# ################################################################################################################################

class TestCountMatchingOutcomes:

    def test_the_counts_are_summed_by_the_named_codes_alone(self) -> 'None':
        outcome_counts = {'exception': 2, 'not-found': 1, 'timeout': 3}

        matching = count_matching_outcomes(outcome_counts, ['exception', 'timeout'])

        assert matching == {'exception': 2, 'timeout': 3}
        assert sum(matching.values()) == 5

    def test_nothing_matches_nothing(self) -> 'None':
        assert count_matching_outcomes({'not-found': 4}, ['exception']) == {}
        assert count_matching_outcomes({}, ['exception']) == {}

# ################################################################################################################################
# ################################################################################################################################

class TestApplyOutcomeCodes:

    def test_the_rules_default_codes_apply_when_the_connection_has_none_of_its_own(self) -> 'None':
        rule = _load_rule('Operation_Outcomes')

        fact = new_fact(AuditSource.FHIR, _conn_name)
        fact['fault_counts'] = {'exception': 2, 'not-found': 1, 'timeout': 3}

        derived = apply_outcome_codes(fact, rule, {})

        # The default is the processing family - a missing resource is not among them
        assert derived[Outcome_Count_Key] == 5
        assert derived[Outcome_Code_Counts_Key] == {'exception': 2, 'timeout': 3}

        # The fact handed in is left as it was, since every rule reads it
        assert fact[Outcome_Count_Key] == 0
        assert fact[Outcome_Code_Counts_Key] == {}

    def test_the_connections_own_codes_stand_in_for_the_default(self) -> 'None':
        rule = _load_rule('Operation_Outcomes')

        fact = new_fact(AuditSource.FHIR, _conn_name)
        fact['fault_counts'] = {'exception': 2, 'not-found': 1, 'timeout': 3}

        derived = apply_outcome_codes(fact, rule, {Outcome_Codes_Default: 'not-found'})

        assert derived[Outcome_Count_Key] == 1
        assert derived[Outcome_Code_Counts_Key] == {'not-found': 1}

    def test_a_fact_without_outcome_counts_is_handed_back_as_it_is(self) -> 'None':
        rule = _load_rule('Operation_Outcomes')
        fact = new_fact(AuditSource.FHIR, _conn_name)

        assert apply_outcome_codes(fact, rule, {}) is fact

    def test_a_rule_without_outcome_codes_is_not_its_business(self) -> 'None':
        rule = _load_rule('Status_Codes')

        fact = new_fact(AuditSource.FHIR, _conn_name)
        fact['fault_counts'] = {'exception': 4}

        assert apply_outcome_codes(fact, rule, {}) is fact

# ################################################################################################################################
# ################################################################################################################################
