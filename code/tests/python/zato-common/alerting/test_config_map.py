# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from pathlib import Path
from typing import Generator

# pytest
import pytest

# SQLAlchemy
from sqlalchemy.engine import Engine

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.seed import ensure_alerting_definitions
from zato.common.rule_engine.sql import create_database_engine, create_schema, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

engine_generator:TypeAlias = Generator[Engine, None, None]

# ################################################################################################################################
# ################################################################################################################################

# The type and ruleset most of the single-field tests speak through
_rest_type = 'rest'
_rest_ruleset = 'alerts_rest'

# The type whose toggle field the toggle tests speak through
_microsoft_type = 'microsoft'
_microsoft_ruleset = 'alerts_microsoft'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def rule_database_engine(tmp_path:'Path') -> 'engine_generator':
    """ Creates one isolated test-managed rule engine database.
    """
    database_path = tmp_path / 'rule-engine.sqlite'
    database_url = f'sqlite:///{database_path}'
    connection_options = {'check_same_thread': False}
    engine = create_database_engine(database_url, connect_args=connection_options)

    create_schema(engine)

    yield engine

    engine.dispose()

# ################################################################################################################################

@pytest.fixture
def backend(rule_database_engine:'Engine') -> 'RuleSQLBackend':
    """ Returns the complete backend over the isolated test database.
    """
    out = RuleSQLBackend.from_engine(rule_database_engine)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _field(type_name:'str', field_name:'str') -> 'stranydict':
    """ One field's map entry, by the type and name the screen knows it under.
    """
    for candidate in config_map.type_fields[type_name]:
        if candidate['name'] == field_name:
            return candidate

    raise Exception(f'No such field -> {type_name}.{field_name}')

# ################################################################################################################################

def _number_documents(rule_name:'str', default_name:'str', value:'float') -> 'stranydict':
    """ A minimal documents dict holding one rule with one default.
    """
    full_name = config_map.rule_full_name(_rest_ruleset, rule_name)

    out = {
        full_name: {
            'name': rule_name,
            'defaults': {default_name: {'value': value}},
        },
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestUnitConversion:

    def test_a_fraction_reads_as_percent(self) -> 'None':
        assert config_map.to_screen_value(0.1, True) == 10

    def test_a_percent_writes_as_a_fraction(self) -> 'None':
        assert config_map.to_rule_value(10, True) == 0.1

    def test_a_plain_number_stays_as_is(self) -> 'None':
        assert config_map.to_screen_value(5000, False) == 5000
        assert config_map.to_rule_value(5000, False) == 5000

    def test_a_whole_float_reads_as_an_integer(self) -> 'None':
        value = config_map.to_screen_value(3.0, False)
        assert value == 3
        assert isinstance(value, int)

# ################################################################################################################################

    def test_a_duration_splits_into_the_largest_even_unit(self) -> 'None':
        assert config_map.split_duration(86400) == (1, 'day')
        assert config_map.split_duration(172800) == (2, 'day')
        assert config_map.split_duration(3600) == (1, 'hour')
        assert config_map.split_duration(600) == (10, 'minute')
        assert config_map.split_duration(300) == (5, 'minute')

# ################################################################################################################################

    def test_a_duration_no_unit_divides_is_a_fraction_of_the_smallest(self) -> 'None':
        assert config_map.split_duration(90) == (1.5, 'minute')

# ################################################################################################################################

    def test_a_duration_joins_back_into_seconds(self) -> 'None':
        assert config_map.join_duration(1, 'day') == 86400
        assert config_map.join_duration(10, 'minute') == 600
        assert config_map.join_duration(1.5, 'hour') == 5400

# ################################################################################################################################
# ################################################################################################################################

class TestReadHelpers:

    def test_a_number_reads_from_the_first_rule_holding_the_default(self) -> 'None':
        field = _field(_rest_type, 'error_rate')
        documents = _number_documents('Error_Rate', 'error_rate_threshold', 0.1)

        value = config_map.read_number(documents, _rest_ruleset, field)
        assert value == 10

# ################################################################################################################################

    def test_a_number_whose_rule_is_gone_reads_as_none(self) -> 'None':
        field = _field(_rest_type, 'error_rate')

        value = config_map.read_number({}, _rest_ruleset, field)
        assert value is None

# ################################################################################################################################

    def test_a_duration_reads_its_seconds_off_the_rule_default(self) -> 'None':
        field = _field(_rest_type, 'window')
        assert field['kind'] == config_map.Kind_Duration

        documents = _number_documents('Error_Rate', 'window_seconds', 300)

        value = config_map.read_number(documents, _rest_ruleset, field)
        assert value == 300

        window_seconds = config_map.read_window_seconds(documents, _rest_type)
        assert window_seconds == 300

# ################################################################################################################################

    def test_a_type_without_a_window_rule_has_no_window(self) -> 'None':
        assert config_map.read_window_seconds({}, _rest_type) is None
        assert config_map.read_window_seconds({}, 'common') is None

# ################################################################################################################################

    def test_a_toggle_is_on_when_all_its_rules_are_active(self) -> 'None':
        field = _field(_microsoft_type, 'health_alerts')

        documents = {}
        for rule_name in field['rules']:
            full_name = config_map.rule_full_name(_microsoft_ruleset, rule_name)
            documents[full_name] = {'name': rule_name}

        assert config_map.read_toggle(documents, _microsoft_ruleset, field) is True

# ################################################################################################################################

    def test_a_toggle_is_off_when_one_of_its_rules_is_inactive(self) -> 'None':
        field = _field(_microsoft_type, 'health_alerts')

        documents = {}
        for rule_name in field['rules']:
            full_name = config_map.rule_full_name(_microsoft_ruleset, rule_name)
            documents[full_name] = {'name': rule_name}

        # One of the two rules is off, so the toggle reads off
        first_full_name = config_map.rule_full_name(_microsoft_ruleset, field['rules'][0])
        documents[first_full_name]['is_active'] = False

        assert config_map.read_toggle(documents, _microsoft_ruleset, field) is False

# ################################################################################################################################

    def test_a_toggle_is_off_when_a_rule_is_missing(self) -> 'None':
        field = _field(_microsoft_type, 'health_alerts')

        assert config_map.read_toggle({}, _microsoft_ruleset, field) is False

# ################################################################################################################################

    def test_a_ruleset_toggle_reads_the_key_off_the_first_rule(self) -> 'None':
        field = _field(_rest_type, 'use_llm')

        documents = {
            'alerts_rest_A': {'name': 'A', config_map.Explain_With_LLM_Key: True},
            'alerts_rest_B': {'name': 'B', config_map.Explain_With_LLM_Key: True},
        }
        assert config_map.read_ruleset_toggle(documents, field) is True

# ################################################################################################################################

    def test_a_ruleset_toggle_without_the_key_reads_as_off(self) -> 'None':
        field = _field(_rest_type, 'use_llm')

        # A rule a person wrote by hand never had the key, and an empty ruleset has nothing to read
        assert config_map.read_ruleset_toggle({'alerts_rest_A': {'name': 'A'}}, field) is False
        assert config_map.read_ruleset_toggle({}, field) is False

# ################################################################################################################################

    def test_a_type_is_active_when_any_rule_is(self) -> 'None':
        documents = {
            'alerts_rest_A': {'name': 'A', 'is_active': False},
            'alerts_rest_B': {'name': 'B'},
        }
        assert config_map.is_type_active(documents) is True

# ################################################################################################################################

    def test_a_type_is_inactive_when_all_rules_are(self) -> 'None':
        documents = {
            'alerts_rest_A': {'name': 'A', 'is_active': False},
            'alerts_rest_B': {'name': 'B', 'is_active': False},
        }
        assert config_map.is_type_active(documents) is False

# ################################################################################################################################
# ################################################################################################################################

class TestWriteHelpers:

    def test_a_number_writes_into_every_rule_holding_the_default(self) -> 'None':
        field = _field('llm', 'error_latency')

        # Both LLM slowness rules hold the error threshold, so both take the write
        documents = {}
        for rule_name in field['rules']:
            full_name = config_map.rule_full_name('alerts_llm', rule_name)
            documents[full_name] = {
                'name': rule_name,
                'defaults': {'error_avg_duration_ms': {'value': 15000}},
            }

        changed = config_map.write_number(documents, 'alerts_llm', field, 20000)
        assert changed is True

        for rule_document in documents.values():
            assert rule_document['defaults']['error_avg_duration_ms']['value'] == 20000

# ################################################################################################################################

    def test_writing_the_same_number_changes_nothing(self) -> 'None':
        field = _field(_rest_type, 'error_rate')
        documents = _number_documents('Error_Rate', 'error_rate_threshold', 0.1)

        changed = config_map.write_number(documents, _rest_ruleset, field, 10)
        assert changed is False

# ################################################################################################################################

    def test_a_percent_field_writes_in_rule_units(self) -> 'None':
        field = _field(_rest_type, 'error_rate')
        documents = _number_documents('Error_Rate', 'error_rate_threshold', 0.1)

        changed = config_map.write_number(documents, _rest_ruleset, field, 25)
        assert changed is True

        full_name = config_map.rule_full_name(_rest_ruleset, 'Error_Rate')
        assert documents[full_name]['defaults']['error_rate_threshold']['value'] == 0.25

# ################################################################################################################################

    def test_a_duration_writes_its_seconds_into_every_window_rule(self) -> 'None':
        field = _field('file_transfer', 'window')

        documents = {
            'alerts_file_transfer_Transfer_Failures': {
                'name': 'Transfer_Failures',
                'defaults': {'window_seconds': {'value': 86400}},
            },
            'alerts_file_transfer_Transfer_Failures_Error': {
                'name': 'Transfer_Failures_Error',
                'defaults': {'window_seconds': {'value': 86400}},
            },
        }

        changed = config_map.write_number(documents, 'alerts_file_transfer', field, 3600)
        assert changed is True

        assert documents['alerts_file_transfer_Transfer_Failures']['defaults']['window_seconds']['value'] == 3600
        assert documents['alerts_file_transfer_Transfer_Failures_Error']['defaults']['window_seconds']['value'] == 3600

        assert config_map.read_window_seconds(documents, 'file_transfer') == 3600

# ################################################################################################################################

    def test_a_toggle_flips_all_its_rules(self) -> 'None':
        field = _field(_microsoft_type, 'health_alerts')

        documents = {}
        for rule_name in field['rules']:
            full_name = config_map.rule_full_name(_microsoft_ruleset, rule_name)
            documents[full_name] = {'name': rule_name}

        changed = config_map.write_toggle(documents, _microsoft_ruleset, field, False)
        assert changed is True

        for rule_document in documents.values():
            assert rule_document['is_active'] is False

# ################################################################################################################################

    def test_a_ruleset_toggle_writes_the_key_onto_every_rule(self) -> 'None':
        field = _field(_rest_type, 'use_llm')

        documents = {
            'alerts_rest_A': {'name': 'A', config_map.Explain_With_LLM_Key: True},
            'alerts_rest_B': {'name': 'B'},
        }

        changed = config_map.write_ruleset_toggle(documents, field, False)
        assert changed is True

        for rule_document in documents.values():
            assert rule_document[config_map.Explain_With_LLM_Key] is False

        # Writing what is already there changes nothing
        changed = config_map.write_ruleset_toggle(documents, field, False)
        assert changed is False

# ################################################################################################################################

    def test_write_type_values_touches_only_the_given_fields(self) -> 'None':
        documents = _number_documents('Error_Rate', 'error_rate_threshold', 0.1)
        down_full_name = config_map.rule_full_name(_rest_ruleset, 'Connection_Down')
        documents[down_full_name] = {
            'name': 'Connection_Down',
            'defaults': {'max_consecutive_failures': {'value': 3}},
        }

        changed = config_map.write_type_values(_rest_type, documents, {'error_rate': 20})
        assert changed is True

        # The field given changed, the field not given stayed as it was
        error_full_name = config_map.rule_full_name(_rest_ruleset, 'Error_Rate')
        assert documents[error_full_name]['defaults']['error_rate_threshold']['value'] == 0.2
        assert documents[down_full_name]['defaults']['max_consecutive_failures']['value'] == 3

# ################################################################################################################################

    def test_set_type_active_flips_every_rule(self) -> 'None':
        documents = {
            'alerts_rest_A': {'name': 'A'},
            'alerts_rest_B': {'name': 'B', 'is_active': False},
        }
        changed = config_map.set_type_active(documents, False)
        assert changed is True

        for rule_document in documents.values():
            assert rule_document['is_active'] is False

# ################################################################################################################################
# ################################################################################################################################

class TestRoundTripOverSeededRules:

    def test_every_screen_field_resolves_from_the_seeded_documents(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        for type_name, ruleset_name in config_map.type_to_ruleset.items():

            matches = backend.definitions.find_by_name(name=ruleset_name, object_type=Definition_Type_Ruleset)
            assert len(matches) == 1, ruleset_name

            document = deserialize_document(matches[0].document)
            documents = document[Documents_Key]

            values = config_map.read_type_values(type_name, documents)

            # Every field of every type resolves to a value from the live documents
            for field in config_map.type_fields[type_name]:
                assert field['name'] in values, f'{type_name}.{field["name"]} did not resolve'

                value = values[field['name']]

                if field['kind'] in (config_map.Kind_Toggle, config_map.Kind_Ruleset_Toggle):
                    assert isinstance(value, bool), f'{type_name}.{field["name"]} -> {value}'
                elif field['kind'] == config_map.Kind_Time_Slots:
                    assert value == config_map.Time_Slots_Default, f'{type_name}.{field["name"]} -> {value}'
                elif field['kind'] == config_map.Kind_Text:
                    assert isinstance(value, str), f'{type_name}.{field["name"]} -> {value}'
                else:
                    assert isinstance(value, (int, float)), f'{type_name}.{field["name"]} -> {value}'

# ################################################################################################################################

    def test_the_seeded_values_read_in_screen_units(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        matches = backend.definitions.find_by_name(name=_rest_ruleset, object_type=Definition_Type_Ruleset)
        document = deserialize_document(matches[0].document)
        documents = document[Documents_Key]

        values = config_map.read_type_values(_rest_type, documents)

        # The seeded fractions arrive as percentages and the plain numbers as they are
        assert values['consecutive_failures'] == 3
        assert values['error_rate'] == 10
        assert values['max_latency'] == 5000

        # The window arrives in seconds, five minutes out of the box
        assert values['window'] == 300

        # The seeded rules carry the explain key on, so the Use LLM toggle reads on out of the box
        assert values['use_llm'] is True

# ################################################################################################################################

    def test_the_test_transfer_toggle_reads_the_shipped_inactive_state(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        matches = backend.definitions.find_by_name(name='alerts_file_transfer', object_type=Definition_Type_Ruleset)
        document = deserialize_document(matches[0].document)
        documents = document[Documents_Key]

        values = config_map.read_type_values('file_transfer', documents)

        # The test transfer rule ships inactive, so its toggle reads off out of the box
        assert values['test_transfers'] is False

# ################################################################################################################################

    def test_the_arrival_threshold_reads_the_seeded_default(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        matches = backend.definitions.find_by_name(name='alerts_file_transfer', object_type=Definition_Type_Ruleset)
        document = deserialize_document(matches[0].document)
        documents = document[Documents_Key]

        values = config_map.read_type_values('file_transfer', documents)

        # The arrival rule ships firing right at the schedule's own window
        assert values['arrival_overdue'] == 1

# ################################################################################################################################

    def test_the_file_transfer_window_ships_as_one_day(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        matches = backend.definitions.find_by_name(name='alerts_file_transfer', object_type=Definition_Type_Ruleset)
        document = deserialize_document(matches[0].document)
        documents = document[Documents_Key]

        values = config_map.read_type_values('file_transfer', documents)

        assert values['window'] == 86400
        assert config_map.split_duration(values['window']) == (1, 'day')

# ################################################################################################################################

    def test_a_write_read_round_trip_over_the_seeded_documents(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        matches = backend.definitions.find_by_name(name=_rest_ruleset, object_type=Definition_Type_Ruleset)
        document = deserialize_document(matches[0].document)
        documents = document[Documents_Key]

        new_values = {
            'consecutive_failures': 5,
            'error_rate': 20,
            'window': 3600,
            'status_codes': '404, 5xx',
            'status_code_threshold': 7,
            'status_codes_window': 600,
            'connection_failures': 4,
            'connection_failures_window': 900,
            'max_latency': 9000,
            'latency_window': 1800,
            'use_llm': False,
        }

        changed = config_map.write_type_values(_rest_type, documents, new_values)
        assert changed is True

        # What was written is what reads back, in the same screen units
        values = config_map.read_type_values(_rest_type, documents)
        assert values == new_values

# ################################################################################################################################
# ################################################################################################################################
