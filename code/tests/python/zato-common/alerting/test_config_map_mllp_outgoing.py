# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The config map for the mllp_outgoing type - its one text, the acknowledgment codes, and the four windows of its
# seeded rules, the type carrying no silence and nothing HTTP. The fixtures and the field lookup are the ones the
# rest of the config map tests share.

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.collectors.common import Measure_Ack_Codes, Measure_Connection_Failures, Measure_Error_Rate, \
    Measure_Latency
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
_mllp_type = 'mllp_outgoing'
_mllp_ruleset = 'alerts_mllp_outgoing'

# ################################################################################################################################
# ################################################################################################################################

class TestTextsAndWindowsOfMllpOutgoing:

    def test_the_type_maps_to_its_ruleset(self) -> 'None':
        assert config_map.type_to_ruleset[_mllp_type] == _mllp_ruleset

# ################################################################################################################################

    def test_the_ack_codes_text_reads_off_its_rule_and_writes_back_into_it(self) -> 'None':
        ack_field = _field(_mllp_type, 'ack_codes')

        assert ack_field['kind'] == config_map.Kind_Text

        documents = {
            config_map.rule_full_name(_mllp_ruleset, 'Negative_Acks'): {
                'name': 'Negative_Acks',
                'defaults': {'ack_codes': {'value': 'AE, AR, CE, CR'}},
            },
        }

        assert config_map.read_text(documents, _mllp_ruleset, ack_field) == 'AE, AR, CE, CR'

        changed = config_map.write_text(documents, _mllp_ruleset, ack_field, 'AR, CR')
        assert changed is True
        assert config_map.read_text(documents, _mllp_ruleset, ack_field) == 'AR, CR'

        changed = config_map.write_text(documents, _mllp_ruleset, ack_field, 'AR, CR')
        assert changed is False

# ################################################################################################################################

    def test_the_type_has_the_acks_and_the_failures_and_nothing_else(self) -> 'None':
        names = [field['name'] for field in config_map.type_fields[_mllp_type]]

        for name in ('consecutive_failures', 'error_rate', 'window', 'ack_codes', 'ack_threshold', 'acks_window',
            'connection_failures', 'connection_failures_window', 'max_latency', 'latency_window', 'use_llm'):
            assert name in names, name

        # No silence - an outgoing connection has no traffic it expects - and nothing HTTP
        for name in ('traffic_expected', 'silence_window', 'auth_failures', 'client_errors', 'server_error_rate',
            'status_codes', 'status_code_threshold', 'fault_codes', 'outcome_codes'):
            assert name not in names, name

# ################################################################################################################################

    def test_the_seeded_rules_hand_each_of_the_four_windows_to_its_measure(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        matches = backend.definitions.find_by_name(name=_mllp_ruleset, object_type=Definition_Type_Ruleset)
        document = deserialize_document(matches[0].document)
        documents = document[Documents_Key]

        by_measure = config_map.read_window_seconds_by_measure(documents, _mllp_type)

        assert by_measure == {
            Measure_Error_Rate: 300,
            Measure_Ack_Codes: 300,
            Measure_Connection_Failures: 300,
            Measure_Latency: 300,
        }

        # Each window is written on its own and lands on its own measure alone
        new_values = {'acks_window': 600, 'connection_failures_window': 900}
        _ = config_map.write_type_values(_mllp_type, documents, new_values)

        by_measure = config_map.read_window_seconds_by_measure(documents, _mllp_type)

        assert by_measure[Measure_Ack_Codes] == 600
        assert by_measure[Measure_Connection_Failures] == 900
        assert by_measure[Measure_Error_Rate] == 300
        assert by_measure[Measure_Latency] == 300

# ################################################################################################################################
# ################################################################################################################################
