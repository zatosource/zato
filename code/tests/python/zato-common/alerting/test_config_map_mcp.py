# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The config map for the mcp type - the size kind that splits a byte count into kilobytes, megabytes or gigabytes
# for the screen and joins back into bytes, the seven windows of its seeded rules each landing on its own measure,
# the two latencies that read in seconds off rules that speak milliseconds and the one field with no window at all.

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.collectors.common import Measure_Auth_Failures, Measure_Error_Rate, Measure_Invalid_Calls, \
    Measure_Latency, Measure_MCP_Truncations, Measure_Rejections, Measure_Repeat_Calls, Measure_Silence, Measure_Throttled, \
    Measure_Volume
from zato.common.alerting.seed import ensure_alerting_definitions
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document

# Test helpers
from test_config_map import _field, backend, rule_database_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleSQLBackend
    RuleSQLBackend = RuleSQLBackend

# ################################################################################################################################
# ################################################################################################################################

# The fixtures are imported for pytest to find them under this module too
backend = backend
rule_database_engine = rule_database_engine

# The type and ruleset the tests speak through
_mcp_type = 'mcp'
_mcp_ruleset = 'alerts_mcp'

# ################################################################################################################################
# ################################################################################################################################

def _seeded_documents(backend:'RuleSQLBackend') -> 'dict':
    """ The rule documents of the seeded MCP ruleset.
    """
    ensure_alerting_definitions(backend)

    matches = backend.definitions.find_by_name(name=_mcp_ruleset, object_type=Definition_Type_Ruleset)
    document = deserialize_document(matches[0].document)

    out = document[Documents_Key]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSizesOfMCP:

    def test_the_volume_budget_is_a_size(self) -> 'None':
        field = _field(_mcp_type, 'volume_budget')
        assert field['kind'] == config_map.Kind_Size

# ################################################################################################################################

    def test_a_size_splits_into_its_largest_unit_and_joins_back(self) -> 'None':

        assert config_map.split_size(100000000) == (100, 'megabyte')
        assert config_map.split_size(1500000000) == (1.5, 'gigabyte')
        assert config_map.split_size(2000) == (2, 'kilobyte')

        # Below the smallest unit the count is a fraction of a kilobyte
        assert config_map.split_size(500) == (0.5, 'kilobyte')

        assert config_map.join_size(100, 'megabyte') == 100000000
        assert config_map.join_size(1.5, 'gigabyte') == 1500000000
        assert config_map.join_size(2, 'kilobyte') == 2000
        assert config_map.join_size(0.5, 'kilobyte') == 500

        # Every split joins back into what it came from
        for byte_count in (500, 999, 1000, 2000, 100000000, 1500000000, 2500000000):
            count, unit_name = config_map.split_size(byte_count)
            assert config_map.join_size(count, unit_name) == byte_count, byte_count

# ################################################################################################################################

    def test_a_size_formats_as_a_person_reads_it(self) -> 'None':

        assert config_map.format_size(100000000) == '100 megabytes'
        assert config_map.format_size(1000000000) == '1 gigabyte'
        assert config_map.format_size(2500000000) == '2.5 gigabytes'
        assert config_map.format_size(2000) == '2 kilobytes'

# ################################################################################################################################

    def test_the_budget_reads_and_writes_as_a_plain_byte_count(self) -> 'None':
        field = _field(_mcp_type, 'volume_budget')

        documents = {
            config_map.rule_full_name(_mcp_ruleset, 'Response_Volume'): {
                'name': 'Response_Volume',
                'defaults': {'volume_budget': {'value': 100000000}, 'window_seconds': {'value': 86400}},
            },
        }

        # The rule and the screen agree on the count itself - the unit is the screen's own business
        assert config_map.read_number(documents, _mcp_ruleset, field) == 100000000

        changed = config_map.write_number(documents, _mcp_ruleset, field, 2000000000)
        assert changed is True
        assert config_map.read_number(documents, _mcp_ruleset, field) == 2000000000

        changed = config_map.write_number(documents, _mcp_ruleset, field, 2000000000)
        assert changed is False

# ################################################################################################################################
# ################################################################################################################################

class TestWindowsOfMCP:

    def test_the_seeded_mcp_rules_hand_each_of_the_seven_windows_to_its_measure(self, backend:'RuleSQLBackend') -> 'None':
        documents = _seeded_documents(backend)

        by_measure = config_map.read_window_seconds_by_measure(documents, _mcp_type)

        assert by_measure == {
            Measure_Error_Rate: 300,
            Measure_Invalid_Calls: 300,
            Measure_Rejections: 300,
            Measure_Auth_Failures: 300,
            Measure_Throttled: 300,
            Measure_Repeat_Calls: 300,
            Measure_Latency: 300,
            Measure_MCP_Truncations: 300,
            Measure_Volume: 86400,
            Measure_Silence: 3600,
        }

        # A window written on its own lands on its own measure alone
        new_values = {'repeat_calls_window': 900, 'volume_budget_window': 3600}
        _ = config_map.write_type_values(_mcp_type, documents, new_values)

        by_measure = config_map.read_window_seconds_by_measure(documents, _mcp_type)

        assert by_measure[Measure_Repeat_Calls] == 900
        assert by_measure[Measure_Volume] == 3600
        assert by_measure[Measure_Invalid_Calls] == 300
        assert by_measure[Measure_Error_Rate] == 300

# ################################################################################################################################

    def test_the_seeded_values_read_in_screen_units(self, backend:'RuleSQLBackend') -> 'None':
        documents = _seeded_documents(backend)

        values = config_map.read_type_values(_mcp_type, documents)

        assert values['consecutive_failures'] == 3
        assert values['error_rate'] == 10
        assert values['window'] == 300
        assert values['invalid_calls'] == 5
        assert values['rejections'] == 3
        assert values['auth_failures'] == 10
        assert values['throttled_calls'] == 10
        assert values['repeat_calls'] == 20
        assert values['warning_latency'] == 5
        assert values['error_latency'] == 15
        assert values['truncations'] == 5
        assert values['volume_budget'] == 100000000
        assert values['volume_budget_window'] == 86400
        assert values['traffic_expected'] is False
        assert values['silence_window'] == 3600
        assert values['max_tools'] == 25
        assert values['use_llm'] is True

# ################################################################################################################################

    def test_the_tool_count_has_no_window(self) -> 'None':
        field = _field(_mcp_type, 'max_tools')

        assert field['kind'] == config_map.Kind_Number

        # The slots field is the one with no rule at all, every other field names its rules
        for candidate in config_map.type_fields[_mcp_type]:
            if 'Too_Many_Tools' in candidate.get('rules', []):
                assert candidate['name'] == 'max_tools', candidate

# ################################################################################################################################
# ################################################################################################################################

class TestSecondsOfMCP:

    def test_a_latency_reads_in_seconds_and_writes_back_in_milliseconds(self) -> 'None':
        warning_field = _field(_mcp_type, 'warning_latency')
        error_field = _field(_mcp_type, 'error_latency')

        assert warning_field['kind'] == config_map.Kind_Seconds
        assert error_field['kind'] == config_map.Kind_Seconds

        documents = {
            config_map.rule_full_name(_mcp_ruleset, 'Slow_Tool_Calls'): {
                'name': 'Slow_Tool_Calls',
                'defaults': {
                    'warning_avg_duration_ms': {'value': 5000},
                    'error_avg_duration_ms': {'value': 15000},
                },
            },
            config_map.rule_full_name(_mcp_ruleset, 'Slow_Tool_Calls_Error'): {
                'name': 'Slow_Tool_Calls_Error',
                'defaults': {'error_avg_duration_ms': {'value': 15000}},
            },
        }

        assert config_map.read_number(documents, _mcp_ruleset, warning_field) == 5
        assert config_map.read_number(documents, _mcp_ruleset, error_field) == 15

        # Seven and a half seconds write back as 7500 milliseconds ..
        changed = config_map.write_number(documents, _mcp_ruleset, warning_field, 7.5)
        assert changed is True

        slow = documents[config_map.rule_full_name(_mcp_ruleset, 'Slow_Tool_Calls')]
        assert slow['defaults']['warning_avg_duration_ms']['value'] == 7500

        # .. and the error latency lives in two rules and both take the write.
        changed = config_map.write_number(documents, _mcp_ruleset, error_field, 20)
        assert changed is True

        slow_error = documents[config_map.rule_full_name(_mcp_ruleset, 'Slow_Tool_Calls_Error')]
        assert slow['defaults']['error_avg_duration_ms']['value'] == 20000
        assert slow_error['defaults']['error_avg_duration_ms']['value'] == 20000

# ################################################################################################################################
# ################################################################################################################################
