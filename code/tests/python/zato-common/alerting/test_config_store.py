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
from zato.common.alerting.config_store import apply_type_config, get_type_definition, NoSuchRulesetError
from zato.common.alerting.seed import ensure_alerting_definitions
from zato.common.alerting.sweep import load_alert_rules
from zato.common.rule_engine.sql import create_database_engine, create_schema, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document

# ################################################################################################################################
# ################################################################################################################################

engine_generator:TypeAlias = Generator[Engine, None, None]

# ################################################################################################################################
# ################################################################################################################################

# Who the test says made the changes
_actor = 'test-config-store'

# The type and ruleset most of the tests speak through
_rest_type = 'rest'
_rest_ruleset = 'alerts_rest'

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
    """ Returns the complete backend over the isolated test database, with
    the default alerting definitions already seeded and live.
    """
    out = RuleSQLBackend.from_engine(rule_database_engine)
    ensure_alerting_definitions(out)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestApplyTypeConfig:

    def test_a_save_round_trip_reaches_the_sweep(self, backend:'RuleSQLBackend') -> 'None':

        # The same post-shaped input the config screen's popover sends
        values = {
            'consecutive_failures': 7,
            'error_rate': 30,
        }
        changed = apply_type_config(backend, _rest_type, actor=_actor, values=values)
        assert changed is True

        # The new version is stored and already the live one
        definition = get_type_definition(backend, _rest_type)
        assert definition.current_version == 2
        assert definition.live_version == 2

        # The sweep loads its rules from the live versions, so it already
        # runs with the new thresholds
        rules = load_alert_rules(backend)
        rules_by_full_name = {rule.full_name: rule for rule in rules}

        down_rule = rules_by_full_name[f'{_rest_ruleset}_Connection_Down']
        assert down_rule.defaults['max_consecutive_failures'] == 7

        error_rule = rules_by_full_name[f'{_rest_ruleset}_Error_Rate']
        assert error_rule.defaults['error_rate_threshold'] == 0.3

# ################################################################################################################################

    def test_saving_what_is_already_there_stores_nothing(self, backend:'RuleSQLBackend') -> 'None':

        # The seeded values, in screen units
        values = {
            'consecutive_failures': 3,
            'error_rate': 10,
        }
        changed = apply_type_config(backend, _rest_type, actor=_actor, values=values)
        assert changed is False

        # No new version appeared
        definition = get_type_definition(backend, _rest_type)
        assert definition.current_version == 1

# ################################################################################################################################

    def test_a_type_toggle_flips_every_rule(self, backend:'RuleSQLBackend') -> 'None':

        changed = apply_type_config(backend, _rest_type, actor=_actor, is_active=False)
        assert changed is True

        definition = get_type_definition(backend, _rest_type)
        document = deserialize_document(definition.document)
        documents = document[Documents_Key]

        for rule_document in documents.values():
            assert rule_document['is_active'] is False

        assert config_map.is_type_active(documents) is False

        # And back on again, through the same path
        changed = apply_type_config(backend, _rest_type, actor=_actor, is_active=True)
        assert changed is True

        definition = get_type_definition(backend, _rest_type)
        document = deserialize_document(definition.document)

        assert config_map.is_type_active(document[Documents_Key]) is True

# ################################################################################################################################

    def test_values_and_the_toggle_save_as_one_version(self, backend:'RuleSQLBackend') -> 'None':

        values = {'max_latency': 8000}
        changed = apply_type_config(backend, _rest_type, actor=_actor, values=values, is_active=False)
        assert changed is True

        # Both changes landed in a single new version
        definition = get_type_definition(backend, _rest_type)
        assert definition.current_version == 2

        document = deserialize_document(definition.document)
        documents = document[Documents_Key]

        assert config_map.is_type_active(documents) is False

        slow_rule = documents[f'{_rest_ruleset}_Slow_Responses']
        assert slow_rule['defaults']['max_avg_duration_ms']['value'] == 8000

# ################################################################################################################################

    def test_the_use_llm_checkbox_follows_the_diagnose_rule(self, backend:'RuleSQLBackend') -> 'None':

        # The same post-shaped input the Use LLM checkbox sends - off first ..
        changed = apply_type_config(backend, _rest_type, actor=_actor, values={'use_llm': False})
        assert changed is True

        definition = get_type_definition(backend, _rest_type)
        document = deserialize_document(definition.document)
        documents = document[Documents_Key]

        # .. only the diagnose rule flipped, the other rules stayed as they were ..
        assert documents[f'{_rest_ruleset}_Error_Rate_Diagnose']['is_active'] is False
        assert config_map.is_rule_active(documents[f'{_rest_ruleset}_Connection_Down']) is True

        # .. and the checkbox reads back off.
        values = config_map.read_type_values(_rest_type, documents)
        assert values['use_llm'] is False

        # Back on again, through the same path
        changed = apply_type_config(backend, _rest_type, actor=_actor, values={'use_llm': True})
        assert changed is True

        definition = get_type_definition(backend, _rest_type)
        document = deserialize_document(definition.document)

        values = config_map.read_type_values(_rest_type, document[Documents_Key])
        assert values['use_llm'] is True

# ################################################################################################################################

    def test_a_missing_ruleset_is_its_own_error(self, backend:'RuleSQLBackend') -> 'None':

        # A store without the ruleset answers with the error the view turns
        # into a bad request, not with a silent no-op
        definition = get_type_definition(backend, _rest_type)
        backend.definitions.archive(definition_id=definition.id, actor=_actor)

        with pytest.raises(NoSuchRulesetError):
            _ = apply_type_config(backend, _rest_type, actor=_actor, values={'error_rate': 20})

# ################################################################################################################################
# ################################################################################################################################
