# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The status codes an outgoing connection alerts on - the text a person types parses into codes and classes
# and refuses anything else, the matching counts never count one response twice, and the sweep's derivation
# reads a connection's own codes over the rule's default.

# pytest
import pytest

# Zato
from zato.common.alerting.collectors.common import new_fact
from zato.common.alerting.config_map import Status_Codes_Default
from zato.common.alerting.seed.rules_connections import rest_rules
from zato.common.alerting.status_codes import apply_status_codes, count_matching, is_matching, parse_status_codes, \
    Status_Code_Count_Key, Status_Code_Counts_Key
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

_ruleset_name = 'alerts_rest'
_conn_name = 'crm.api'

# ################################################################################################################################

def _load_rule(name:'str') -> 'Rule':
    """ One of the seeded rest rules as a runtime rule.
    """
    documents, errors = parse_data_details(rest_rules, _ruleset_name)
    assert errors == []

    loaded = load_documents(documents)

    out = loaded.manager[f'{_ruleset_name}_{name}']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestParseStatusCodes:

    def test_codes_and_classes_parse_with_whatever_spacing(self) -> 'None':
        assert parse_status_codes('401, 403, 4xx, 5xx') == ['401', '403', '4xx', '5xx']
        assert parse_status_codes('401,403') == ['401', '403']
        assert parse_status_codes('  503 ') == ['503']

    def test_a_class_reads_the_same_in_either_case_and_an_entry_is_kept_once(self) -> 'None':
        assert parse_status_codes('5XX, 5xx, 401, 401') == ['5xx', '401']

    def test_empty_entries_name_nothing(self) -> 'None':
        assert parse_status_codes('') == []
        assert parse_status_codes('401,, 403,') == ['401', '403']

    @pytest.mark.parametrize('text', ['40', '4000', '6xx', '0xx', 'abc', '4x', '4xy', '401 403'])
    def test_anything_else_is_refused(self, text:'str') -> 'None':
        with pytest.raises(ValueError) as context:
            _ = parse_status_codes(text)

        assert text.split(',')[0].strip() in str(context.value)

# ################################################################################################################################
# ################################################################################################################################

class TestCountMatching:

    def test_a_code_matches_itself_and_its_class(self) -> 'None':
        codes = ['401', '5xx']

        assert is_matching('401', codes) is True
        assert is_matching('503', codes) is True
        assert is_matching('403', codes) is False
        assert is_matching('200', codes) is False

    def test_the_counts_are_summed_by_code_without_double_counting(self) -> 'None':
        status_counts = {'200': 10, '401': 2, '404': 1, '503': 3}

        # 401 is both a code and a member of 4xx - it is counted once
        matching = count_matching(status_counts, ['401', '4xx', '5xx'])

        assert matching == {'401': 2, '404': 1, '503': 3}
        assert sum(matching.values()) == 6

    def test_nothing_matches_nothing(self) -> 'None':
        assert count_matching({'200': 10}, ['5xx']) == {}
        assert count_matching({}, ['5xx']) == {}

# ################################################################################################################################
# ################################################################################################################################

class TestApplyStatusCodes:

    def test_the_rules_default_codes_apply_when_the_connection_has_none_of_its_own(self) -> 'None':
        rule = _load_rule('Status_Codes')

        fact = new_fact(AuditSource.REST_Outgoing, _conn_name)
        fact['status_counts'] = {'200': 5, '401': 2, '404': 1, '503': 1}

        derived = apply_status_codes(fact, rule, {})

        # The default is 401, 403 and 5xx - the 404 is not among them
        assert derived[Status_Code_Count_Key] == 3
        assert derived[Status_Code_Counts_Key] == {'401': 2, '503': 1}

        # The fact handed in is left as it was, since every rule reads it
        assert fact[Status_Code_Count_Key] == 0
        assert fact[Status_Code_Counts_Key] == {}

    def test_the_connections_own_codes_stand_in_for_the_default(self) -> 'None':
        rule = _load_rule('Status_Codes')

        fact = new_fact(AuditSource.REST_Outgoing, _conn_name)
        fact['status_counts'] = {'200': 5, '401': 2, '404': 1, '503': 1}

        derived = apply_status_codes(fact, rule, {Status_Codes_Default: '404'})

        assert derived[Status_Code_Count_Key] == 1
        assert derived[Status_Code_Counts_Key] == {'404': 1}

    def test_a_fact_without_status_counts_is_handed_back_as_it_is(self) -> 'None':
        rule = _load_rule('Status_Codes')
        fact = new_fact(AuditSource.REST_Outgoing, _conn_name)

        assert apply_status_codes(fact, rule, {}) is fact

    def test_a_rule_without_status_codes_is_not_its_business(self) -> 'None':
        rule = _load_rule('Connection_Failures')

        fact = new_fact(AuditSource.REST_Outgoing, _conn_name)
        fact['status_counts'] = {'503': 4}

        assert apply_status_codes(fact, rule, {}) is fact

# ################################################################################################################################
# ################################################################################################################################
