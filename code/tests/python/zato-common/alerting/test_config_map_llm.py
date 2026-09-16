# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The config map for the llm type - its status codes text, the five windows of its seeded rules, the two latencies
# that read in seconds off rules that speak milliseconds and the token budget that splits into thousands, millions
# or billions for the screen and joins back into ones. The fixtures and the field lookup are the ones the rest
# of the config map tests share.

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.collectors.common import Measure_Connection_Failures, Measure_Error_Rate, Measure_Latency, \
    Measure_Refusals, Measure_Status_Codes, Measure_Tokens, Measure_Truncations
from zato.common.alerting.seed import ensure_alerting_definitions
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document

# Test helpers
from test_config_map import _field, backend, rule_database_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleSQLBackend
    from zato.common.typing_ import stranydict
    RuleSQLBackend = RuleSQLBackend
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The fixtures are imported for pytest to find them under this module too
backend = backend
rule_database_engine = rule_database_engine

# The type and ruleset the tests speak through
_llm_type = 'llm'
_llm_ruleset = 'alerts_llm'

# ################################################################################################################################
# ################################################################################################################################

def _seeded_documents(backend:'RuleSQLBackend') -> 'dict':
    """ The rule documents of the seeded LLM ruleset.
    """
    ensure_alerting_definitions(backend)

    matches = backend.definitions.find_by_name(name=_llm_ruleset, object_type=Definition_Type_Ruleset)
    document = deserialize_document(matches[0].document)

    out = document[Documents_Key]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestTextAndWindowsOfLLM:

    def test_the_status_codes_text_reads_off_its_rule_and_writes_back_into_it(self) -> 'None':
        status_field = _field(_llm_type, 'status_codes')

        assert status_field['kind'] == config_map.Kind_Text

        documents = {
            config_map.rule_full_name(_llm_ruleset, 'Status_Codes'): {
                'name': 'Status_Codes',
                'defaults': {'status_codes': {'value': '429, 401, 403, 5xx'}},
            },
        }

        assert config_map.read_text(documents, _llm_ruleset, status_field) == '429, 401, 403, 5xx'

        changed = config_map.write_text(documents, _llm_ruleset, status_field, '429, 5xx')
        assert changed is True
        assert config_map.read_text(documents, _llm_ruleset, status_field) == '429, 5xx'

        changed = config_map.write_text(documents, _llm_ruleset, status_field, '429, 5xx')
        assert changed is False

# ################################################################################################################################

    def test_the_seeded_llm_rules_hand_each_of_the_five_windows_to_its_measure(self, backend:'RuleSQLBackend') -> 'None':
        documents = _seeded_documents(backend)

        by_measure = config_map.read_window_seconds_by_measure(documents, _llm_type)

        assert by_measure == {
            Measure_Error_Rate: 300,
            Measure_Status_Codes: 300,
            Measure_Connection_Failures: 300,
            Measure_Truncations: 300,
            Measure_Refusals: 300,
            Measure_Latency: 300,
            Measure_Tokens: 86400,
        }

        # The budget window is written on its own and lands on its own measure alone
        new_values = {'token_budget_window': 3600, 'truncations_window': 600}
        _ = config_map.write_type_values(_llm_type, documents, new_values)

        by_measure = config_map.read_window_seconds_by_measure(documents, _llm_type)

        assert by_measure[Measure_Tokens] == 3600
        assert by_measure[Measure_Truncations] == 600
        assert by_measure[Measure_Refusals] == 300
        assert by_measure[Measure_Status_Codes] == 300

# ################################################################################################################################

    def test_the_seeded_values_read_in_screen_units(self, backend:'RuleSQLBackend') -> 'None':
        documents = _seeded_documents(backend)

        values = config_map.read_type_values(_llm_type, documents)

        assert values['status_codes'] == '429, 401, 403, 5xx'
        assert values['status_code_threshold'] == 3
        assert values['connection_failures'] == 3
        assert values['truncations'] == 3
        assert values['refusals'] == 3
        assert values['warning_latency'] == 10
        assert values['error_latency'] == 15
        assert values['token_budget'] == 10000000
        assert values['token_budget_window'] == 86400

# ################################################################################################################################
# ################################################################################################################################

class TestSecondsOfLLM:

    def test_a_latency_reads_in_seconds_and_writes_back_in_milliseconds(self) -> 'None':
        warning_field = _field(_llm_type, 'warning_latency')
        error_field = _field(_llm_type, 'error_latency')

        assert warning_field['kind'] == config_map.Kind_Seconds
        assert error_field['kind'] == config_map.Kind_Seconds

        documents:'stranydict' = {
            config_map.rule_full_name(_llm_ruleset, 'Slow_Completions'): {
                'name': 'Slow_Completions',
                'defaults': {
                    'warning_avg_duration_ms': {'value': 12500},
                    'error_avg_duration_ms': {'value': 15000},
                },
            },
            config_map.rule_full_name(_llm_ruleset, 'Slow_Completions_Error'): {
                'name': 'Slow_Completions_Error',
                'defaults': {'error_avg_duration_ms': {'value': 15000}},
            },
        }

        # 12500 milliseconds read as twelve and a half seconds ..
        assert config_map.read_number(documents, _llm_ruleset, warning_field) == 12.5
        assert config_map.read_number(documents, _llm_ruleset, error_field) == 15

        # .. and 12.5 seconds write back as 12500 milliseconds
        changed = config_map.write_number(documents, _llm_ruleset, warning_field, 12.5)
        assert changed is False

        changed = config_map.write_number(documents, _llm_ruleset, warning_field, 7.25)
        assert changed is True

        slow = documents[config_map.rule_full_name(_llm_ruleset, 'Slow_Completions')]
        assert slow['defaults']['warning_avg_duration_ms']['value'] == 7250
        assert config_map.read_number(documents, _llm_ruleset, warning_field) == 7.25

        # The error latency lives in two rules and both take the write
        changed = config_map.write_number(documents, _llm_ruleset, error_field, 20)
        assert changed is True

        slow_error = documents[config_map.rule_full_name(_llm_ruleset, 'Slow_Completions_Error')]
        assert slow['defaults']['error_avg_duration_ms']['value'] == 20000
        assert slow_error['defaults']['error_avg_duration_ms']['value'] == 20000

# ################################################################################################################################

    def test_the_screen_and_rule_conversions_are_each_others_inverse(self) -> 'None':
        field = _field(_llm_type, 'warning_latency')

        assert config_map.to_screen_number(field, 10000) == 10
        assert config_map.to_screen_number(field, 12500) == 12.5
        assert config_map.to_rule_number(field, 10) == 10000
        assert config_map.to_rule_number(field, 12.5) == 12500
        assert config_map.to_rule_number(field, 0.5) == 500

        # A field of no particular kind stands as it is
        plain_field = _field(_llm_type, 'truncations')
        assert config_map.to_screen_number(plain_field, 3) == 3
        assert config_map.to_rule_number(plain_field, 3) == 3

# ################################################################################################################################
# ################################################################################################################################

class TestAmountsOfLLM:

    def test_the_budget_is_an_amount(self) -> 'None':
        field = _field(_llm_type, 'token_budget')
        assert field['kind'] == config_map.Kind_Amount

# ################################################################################################################################

    def test_an_amount_splits_into_its_largest_unit_and_joins_back(self) -> 'None':

        assert config_map.split_amount(10000000) == (10, 'million')
        assert config_map.split_amount(1500000) == (1.5, 'million')
        assert config_map.split_amount(2000) == (2, 'thousand')
        assert config_map.split_amount(2500000000) == (2.5, 'billion')

        # Below the smallest unit the count is a fraction of a thousand
        assert config_map.split_amount(500) == (0.5, 'thousand')

        assert config_map.join_amount(10, 'million') == 10000000
        assert config_map.join_amount(1.5, 'million') == 1500000
        assert config_map.join_amount(0.5, 'thousand') == 500
        assert config_map.join_amount(2.5, 'billion') == 2500000000

        # Every split joins back into what it came from
        for count in (500, 999, 1000, 1500000, 10000000, 2500000000):
            split_count, unit_name = config_map.split_amount(count)
            assert config_map.join_amount(split_count, unit_name) == count, count

# ################################################################################################################################

    def test_the_budget_reads_and_writes_as_a_plain_count(self) -> 'None':
        field = _field(_llm_type, 'token_budget')

        documents = {
            config_map.rule_full_name(_llm_ruleset, 'Token_Budget'): {
                'name': 'Token_Budget',
                'defaults': {'token_budget': {'value': 10000000}, 'window_seconds': {'value': 86400}},
            },
        }

        # The rule and the screen agree on the count itself - the unit is the screen's own business
        assert config_map.read_number(documents, _llm_ruleset, field) == 10000000

        changed = config_map.write_number(documents, _llm_ruleset, field, 2000000)
        assert changed is True
        assert config_map.read_number(documents, _llm_ruleset, field) == 2000000

# ################################################################################################################################
# ################################################################################################################################
