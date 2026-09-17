# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The config map for the fhir type - its two texts, the status codes and the outcome codes, and the five windows
# of its seeded rules. The fixtures and the field lookup are the ones the rest of the config map tests share.

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.collectors.common import Measure_Connection_Failures, Measure_Error_Rate, Measure_Latency, \
    Measure_Operation_Outcomes, Measure_Status_Codes
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
_fhir_type = 'fhir'
_fhir_ruleset = 'alerts_fhir'

# ################################################################################################################################
# ################################################################################################################################

class TestTextsAndWindowsOfFhir:

    def test_the_fhir_texts_read_off_their_rules_and_write_back_into_them(self) -> 'None':
        status_field = _field(_fhir_type, 'status_codes')
        outcome_field = _field(_fhir_type, 'outcome_codes')

        assert status_field['kind'] == config_map.Kind_Text
        assert outcome_field['kind'] == config_map.Kind_Text

        documents = {
            config_map.rule_full_name(_fhir_ruleset, 'Status_Codes'): {
                'name': 'Status_Codes',
                'defaults': {'status_codes': {'value': '401, 403, 5xx'}},
            },
            config_map.rule_full_name(_fhir_ruleset, 'Operation_Outcomes'): {
                'name': 'Operation_Outcomes',
                'defaults': {'outcome_codes': {'value': 'exception, timeout'}},
            },
        }

        assert config_map.read_text(documents, _fhir_ruleset, status_field) == '401, 403, 5xx'
        assert config_map.read_text(documents, _fhir_ruleset, outcome_field) == 'exception, timeout'

        # Each text writes into its own rule alone
        changed = config_map.write_text(documents, _fhir_ruleset, outcome_field, 'exception, not-found')
        assert changed is True
        assert config_map.read_text(documents, _fhir_ruleset, outcome_field) == 'exception, not-found'
        assert config_map.read_text(documents, _fhir_ruleset, status_field) == '401, 403, 5xx'

        changed = config_map.write_text(documents, _fhir_ruleset, outcome_field, 'exception, not-found')
        assert changed is False

# ################################################################################################################################

    def test_the_seeded_fhir_rules_hand_each_of_the_five_windows_to_its_measure(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        matches = backend.definitions.find_by_name(name=_fhir_ruleset, object_type=Definition_Type_Ruleset)
        document = deserialize_document(matches[0].document)
        documents = document[Documents_Key]

        by_measure = config_map.read_window_seconds_by_measure(documents, _fhir_type)

        assert by_measure == {
            Measure_Error_Rate: 300,
            Measure_Status_Codes: 300,
            Measure_Operation_Outcomes: 300,
            Measure_Connection_Failures: 300,
            Measure_Latency: 300,
        }

        # The outcomes window is written on its own and lands on its own measure alone
        new_values = {'outcomes_window': 600}
        _ = config_map.write_type_values(_fhir_type, documents, new_values)

        by_measure = config_map.read_window_seconds_by_measure(documents, _fhir_type)

        assert by_measure[Measure_Operation_Outcomes] == 600
        assert by_measure[Measure_Status_Codes] == 300
        assert by_measure[Measure_Connection_Failures] == 300

# ################################################################################################################################
# ################################################################################################################################
