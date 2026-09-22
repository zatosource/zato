# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The seeded outgoing MLLP ruleset - the five rules it ships with their defaults, all of them active, each rule
# reached by a fact of the measure it reads and none of them reached by an MLLP channel or an HTTP outgoing
# connection, the MLLP channel rules leaving an outgoing connection alone, and an environment seeded before the
# ruleset existed gaining it on upgrade.

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
from zato.common.alerting.seed import build_ruleset_document, ensure_alerting_definitions
from zato.common.alerting.seed.rules_mllp import mllp_channel_rules, mllp_outgoing_rules
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

_ruleset_name = 'alerts_mllp_outgoing'
_channel_ruleset_name = 'alerts_mllp_channel'
_conn_name = 'lab.results'

# The seven rules the ruleset ships, with the defaults each one carries
_rule_defaults = {
    'Connection_Down':     {'max_consecutive_failures': 3},
    'Error_Rate':          {'error_rate_threshold': 0.1, 'min_events': 10, 'window_seconds': 300},
    'Negative_Acks':       {'ack_codes': 'AE, AR, CE, CR', 'ack_threshold': 3, 'window_seconds': 300},
    'Connection_Failures': {'connection_failure_threshold': 3, 'window_seconds': 300},
    'Slow_Responses':      {'max_avg_duration_ms': 5000, 'window_seconds': 300},
    'DLQ_Messages':        {'dlq_threshold': 1},
    'Queue_Backlog':       {'queue_depth_threshold': 1000},
}

# One fact per rule, each crafted to clear the rule's default threshold
_rule_measures = {
    'Connection_Down':     {'consecutive_failures': 3},
    'Error_Rate':          {'total_count': 20, 'error_count': 4, 'error_rate': 0.2},
    'Negative_Acks':       {'ack_count': 3},
    'Connection_Failures': {'connection_failure_count': 3},
    'Slow_Responses':      {'avg_duration_ms': 5000},
    'DLQ_Messages':        {'dlq_depth': 1},
    'Queue_Backlog':       {'queue_depth': 1000},
}

# The MLLP channel rules, with a fact each - none of them may read an outgoing connection
_channel_rule_measures = {
    'Channel_Failing': {'consecutive_failures': 3},
    'Error_Rate':      {'total_count': 20, 'error_count': 4, 'error_rate': 0.2},
    'Negative_Acks':   {'ack_count': 3},
    'Slow_Responses':  {'avg_duration_ms': 5000},
    'Channel_Silent':  {'silent_seconds': 3600},
}

# The sources the outgoing rules must leave alone, whatever the measures say
_other_sources = (AuditSource.MLLP_Channel, AuditSource.REST_Outgoing, AuditSource.SOAP_Outgoing, AuditSource.FHIR)

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

def _seed_channel_ruleset_alone(backend:'RuleSQLBackend') -> 'RuleDefinitionRecord':
    """ The MLLP channel ruleset as the release before this one seeded it, with no outgoing ruleset next to it.
    """
    document = build_ruleset_document(_channel_ruleset_name, mllp_channel_rules)

    out = backend.definitions.create(
        name=_channel_ruleset_name,
        object_type=Definition_Type_Ruleset,
        document=document,
        author='test',
        comment='From before the outgoing MLLP rules',
    )
    _ = backend.versions.publish(definition_id=out.id, version=out.current_version, actor='test')

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMllpOutgoingRules:

    def test_the_ruleset_ships_seven_rules_with_their_defaults(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        documents = _get_documents(backend, _ruleset_name)

        assert sorted(documents) == sorted(f'{_ruleset_name}_{name}' for name in _rule_defaults)

        for rule_name, defaults in _rule_defaults.items():
            rule_document = documents[f'{_ruleset_name}_{rule_name}']
            assert _default_values(rule_document) == defaults, rule_name

# ################################################################################################################################

    def test_every_rule_ships_active(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        documents = _get_documents(backend, _ruleset_name)

        # A rule that ships active carries no switch at all
        for full_name, rule_document in documents.items():
            assert 'is_active' not in rule_document, full_name

# ################################################################################################################################

    def test_a_fact_from_each_measure_reaches_its_rule(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        rules = load_alert_rules(backend)
        rules_by_full_name = {rule.full_name: rule for rule in rules}

        for rule_name, measures in _rule_measures.items():
            rule = rules_by_full_name[f'{_ruleset_name}_{rule_name}']

            fact = new_fact(AuditSource.MLLP_Outgoing, _conn_name)
            fact.update(measures)
            assert rule.match({Fact_Entity: fact}), f'Expected {rule_name} to match {fact}'

            # The same measures on a channel or on an HTTP connection are their own rulesets' business
            for source in _other_sources:
                fact = new_fact(source, _conn_name)
                fact.update(measures)
                assert not rule.match({Fact_Entity: fact}), f'Expected {rule_name} not to match {fact}'

# ################################################################################################################################

    def test_no_mllp_channel_rule_reads_an_outgoing_connection(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        rules = load_alert_rules(backend)
        rules_by_full_name = {rule.full_name: rule for rule in rules}

        for rule_name, measures in _channel_rule_measures.items():
            rule = rules_by_full_name[f'{_channel_ruleset_name}_{rule_name}']

            fact = new_fact(AuditSource.MLLP_Outgoing, _conn_name)
            fact.update(measures)
            assert not rule.match({Fact_Entity: fact}), f'Expected {rule_name} not to match {fact}'

# ################################################################################################################################

    def test_the_ruleset_arrives_on_upgrade(self, backend:'RuleSQLBackend') -> 'None':

        # The release before this one had the channel ruleset and no outgoing one
        _ = _seed_channel_ruleset_alone(backend)
        assert backend.definitions.find_by_name(name=_ruleset_name, object_type=Definition_Type_Ruleset) == []

        ensure_alerting_definitions(backend)

        documents = _get_documents(backend, _ruleset_name)
        assert documents == build_ruleset_document(_ruleset_name, mllp_outgoing_rules)[Documents_Key]

# ################################################################################################################################
# ################################################################################################################################
