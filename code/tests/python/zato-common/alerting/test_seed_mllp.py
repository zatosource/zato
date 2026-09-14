# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The seeded MLLP channel ruleset - the five rules it ships with their defaults, the silence rule inactive and the
# others active, each rule reached by a fact of the measure it reads, and none of them reached by an HTTP channel,
# nor an MLLP channel reached by the HTTP channel rules.

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
from zato.common.alerting.collectors import new_fact
from zato.common.alerting.seed import ensure_alerting_definitions
from zato.common.alerting.sweep import load_alert_rules, Fact_Entity
from zato.common.audit_log.api import AuditSource
from zato.common.rule_engine.sql import create_database_engine, create_schema, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleDefinitionRecord
    from zato.common.typing_ import stranydict
    RuleDefinitionRecord = RuleDefinitionRecord
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

engine_generator:TypeAlias = Generator[Engine, None, None]

# ################################################################################################################################
# ################################################################################################################################

_ruleset_name = 'alerts_mllp_channel'
_channels_ruleset_name = 'alerts_channels'
_silent_full_name = 'alerts_mllp_channel_Channel_Silent'
_channel_name = 'adt.intake'

# The five rules the ruleset ships, with the defaults each one carries
_rule_defaults = {
    'Channel_Failing': {'max_consecutive_failures': 3},
    'Error_Rate':      {'error_rate_threshold': 0.1, 'min_events': 10, 'window_seconds': 300},
    'Negative_Acks':   {'ack_codes': 'AE, AR, CE, CR', 'ack_threshold': 3, 'window_seconds': 300},
    'Slow_Responses':  {'max_avg_duration_ms': 5000, 'window_seconds': 300},
    'Channel_Silent':  {'silence_seconds': 3600},
}

# One fact per rule, each crafted to clear the rule's default threshold
_rule_measures = {
    'Channel_Failing': {'consecutive_failures': 3},
    'Error_Rate':      {'total_count': 20, 'error_count': 4, 'error_rate': 0.2},
    'Negative_Acks':   {'ack_count': 3},
    'Slow_Responses':  {'avg_duration_ms': 5000},
    'Channel_Silent':  {'silent_seconds': 3600},
}

# The HTTP channel rules, with a fact each - none of them may read an MLLP channel
_channel_rule_measures = {
    'Channel_Failing': {'consecutive_failures': 3},
    'Server_Errors':   {'total_count': 20, 'server_error_rate': 0.05},
    'Slow_Responses':  {'avg_duration_ms': 5000},
    'Auth_Failures':   {'auth_failure_count': 10},
    'Client_Errors':   {'client_error_count': 50},
    'Channel_Silent':  {'silent_seconds': 3600},
}

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

def _get_documents(backend:'RuleSQLBackend', name:'str') -> 'stranydict':
    """ The rule documents of one seeded ruleset.
    """
    matches = backend.definitions.find_by_name(name=name, object_type=Definition_Type_Ruleset)
    assert len(matches) == 1

    out = deserialize_document(matches[0].document)[Documents_Key]
    return out

# ################################################################################################################################

def _default_values(rule_document:'stranydict') -> 'stranydict':
    """ The defaults of one stored rule as plain values, without the literal wrappers the store keeps.
    """
    out = {}

    for name, default in rule_document['defaults'].items():
        out[name] = default['value']

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMllpChannelRules:

    def test_the_ruleset_ships_five_rules_with_their_defaults(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        documents = _get_documents(backend, _ruleset_name)

        assert sorted(documents) == sorted(f'{_ruleset_name}_{name}' for name in _rule_defaults)

        for rule_name, defaults in _rule_defaults.items():
            rule_document = documents[f'{_ruleset_name}_{rule_name}']
            assert _default_values(rule_document) == defaults, rule_name

# ################################################################################################################################

    def test_the_silence_rule_ships_inactive_and_the_rest_active(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        documents = _get_documents(backend, _ruleset_name)

        assert documents[_silent_full_name]['is_active'] is False

        # A rule that ships active carries no switch at all - only the inactive one is marked
        for full_name, rule_document in documents.items():
            if full_name != _silent_full_name:
                assert 'is_active' not in rule_document, full_name

# ################################################################################################################################

    def test_a_fact_from_each_measure_reaches_its_rule(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        rules = load_alert_rules(backend)
        rules_by_full_name = {rule.full_name: rule for rule in rules}

        for rule_name, measures in _rule_measures.items():
            rule = rules_by_full_name[f'{_ruleset_name}_{rule_name}']

            fact = new_fact(AuditSource.MLLP_Channel, _channel_name)
            fact.update(measures)
            assert rule.match({Fact_Entity: fact}), f'Expected {rule_name} to match {fact}'

            # The same measures on an HTTP channel are the HTTP channel rules' business
            for source in (AuditSource.REST_Channel, AuditSource.SOAP_Channel):
                fact = new_fact(source, _channel_name)
                fact.update(measures)
                assert not rule.match({Fact_Entity: fact}), f'Expected {rule_name} not to match {fact}'

# ################################################################################################################################

    def test_no_http_channel_rule_reads_an_mllp_channel(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        rules = load_alert_rules(backend)
        rules_by_full_name = {rule.full_name: rule for rule in rules}

        for rule_name, measures in _channel_rule_measures.items():
            rule = rules_by_full_name[f'{_channels_ruleset_name}_{rule_name}']

            fact = new_fact(AuditSource.MLLP_Channel, _channel_name)
            fact.update(measures)
            assert not rule.match({Fact_Entity: fact}), f'Expected {rule_name} not to match {fact}'

        # The error rate rule of the HTTP channels dropped the MLLP source when the MLLP ruleset gained one of its own
        error_rate = rules_by_full_name[f'{_channels_ruleset_name}_Channel_Error_Rate']

        fact = new_fact(AuditSource.MLLP_Channel, _channel_name)
        fact.update(_rule_measures['Error_Rate'])
        assert not error_rate.match({Fact_Entity: fact})

# ################################################################################################################################
# ################################################################################################################################
