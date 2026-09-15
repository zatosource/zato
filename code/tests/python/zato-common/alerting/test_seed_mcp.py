# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The seeded MCP ruleset - the fourteen rules it ships with their defaults, every one but the silence rule active,
# each rule reached by a fact of the measure it reads and none of them reached by an LLM connection or a channel,
# the vocabulary speaking the gateway's terms, and an environment seeded with the three rules of the release before
# gaining the eleven new ones on upgrade while Server_Down, which that release shipped, is gone.

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
from zato.common.alerting.seed import alerting_vocabulary, build_ruleset_document, ensure_alerting_definitions
from zato.common.alerting.seed.rules_mcp import mcp_rules
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

_ruleset_name = 'alerts_mcp'
_gateway_name = 'orders.gateway'

# The one rule that ships turned off - a gateway has to say it expects traffic first
_silence_rule_name = 'Gateway_Silent'

# The rule the release before this one shipped and this one retired
_retired_rule_name = 'Server_Down'

# The fourteen rules the ruleset ships, with the defaults each one carries
_rule_defaults = {
    'Gateway_Failing':      {'max_consecutive_failures': 3},
    'Error_Rate':           {'error_rate_threshold': 0.1, 'min_events': 10, 'window_seconds': 300},
    'Invalid_Tool_Calls':   {'invalid_call_threshold': 5, 'window_seconds': 300},
    'Rejected_Responses':   {'rejection_threshold': 3, 'window_seconds': 300},
    'Rejected_Callers':     {'auth_failure_threshold': 10, 'window_seconds': 300},
    'Throttled_Callers':    {'throttled_threshold': 10, 'window_seconds': 300},
    'Repeated_Calls':       {'repeat_call_threshold': 20, 'window_seconds': 300},
    'Slow_Tool_Calls':      {'warning_avg_duration_ms': 5000, 'error_avg_duration_ms': 15000, 'window_seconds': 300},
    'Slow_Tool_Calls_Error': {'error_avg_duration_ms': 15000, 'window_seconds': 300},
    'Truncated_Responses':  {'truncation_threshold': 5, 'window_seconds': 300},
    'Response_Volume':      {'volume_budget': 100000000, 'window_seconds': 86400},
    'Gateway_Silent':       {'silence_seconds': 3600},
    'Too_Many_Tools':       {'max_tools': 25},
}

# One fact per rule, each crafted to clear the rule's default threshold
_rule_measures = {
    'Gateway_Failing':      {'consecutive_failures': 3},
    'Error_Rate':           {'total_count': 20, 'error_count': 4, 'error_rate': 0.2},
    'Invalid_Tool_Calls':   {'invalid_call_count': 5},
    'Rejected_Responses':   {'rejection_count': 3},
    'Rejected_Callers':     {'auth_failure_count': 10},
    'Throttled_Callers':    {'throttled_count': 10},
    'Repeated_Calls':       {'repeat_call_count': 20},
    'Slow_Tool_Calls':      {'avg_duration_ms': 6000},
    'Slow_Tool_Calls_Error': {'avg_duration_ms': 15000},
    'Truncated_Responses':  {'truncation_count': 5},
    'Response_Volume':      {'volume_bytes': 100000000},
    'Gateway_Silent':       {'silent_seconds': 3600},
    'Too_Many_Tools':       {'tool_count': 25},
}

# The terms the vocabulary gained for the gateway
_new_terms = (
    'invalid_call_count',
    'rejection_count',
    'throttled_count',
    'repeat_call_count',
    'repeat_call_tool',
    'repeat_call_session',
    'volume_bytes',
    'tool_count',
)

# The sources the MCP rules must leave alone, whatever the measures say
_other_sources = (AuditSource.LLM, AuditSource.REST_Outgoing, AuditSource.REST_Channel, AuditSource.MLLP_Channel)

# The ruleset as the release before this one seeded it - three rules, one of them since retired
_old_mcp_rules = """
rule
    Server_Down
docs
    An MCP gateway that failed three consecutive times is considered down and raises an error email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'mcp' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Slow_Tool_Calls
docs
    An MCP gateway whose average tool-call time within the window exceeds five seconds raises a warning email alert.
defaults
    max_avg_duration_ms = 5000
    window_seconds = 300
when
    alert.source is 'mcp' and
    alert.avg_duration_ms is at least default.max_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate
docs
    An MCP gateway whose failed-request share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
    window_seconds = 300
when
    alert.source is 'mcp' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

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

def _get_ruleset(backend:'RuleSQLBackend', name:'str') -> 'RuleDefinitionRecord':
    """ One seeded ruleset definition, or a failure when there is none.
    """
    matches = backend.definitions.find_by_name(name=name, object_type=Definition_Type_Ruleset)
    assert len(matches) == 1

    out = matches[0]
    return out

# ################################################################################################################################

def _get_documents(backend:'RuleSQLBackend', name:'str') -> 'stranydict':
    """ The rule documents of one seeded ruleset.
    """
    out = deserialize_document(_get_ruleset(backend, name).document)[Documents_Key]
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

def _seed_old_mcp_ruleset(backend:'RuleSQLBackend') -> 'RuleDefinitionRecord':
    """ The MCP ruleset as the release before this one seeded it.
    """
    document = build_ruleset_document(_ruleset_name, _old_mcp_rules)

    out = backend.definitions.create(
        name=_ruleset_name,
        object_type=Definition_Type_Ruleset,
        document=document,
        author='test',
        comment='From before the gateway had rules of its own',
    )
    _ = backend.versions.publish(definition_id=out.id, version=out.current_version, actor='test')

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMCPRules:

    def test_the_ruleset_ships_fourteen_rules_with_their_defaults(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        documents = _get_documents(backend, _ruleset_name)

        assert sorted(documents) == sorted(f'{_ruleset_name}_{name}' for name in _rule_defaults)

        for rule_name, defaults in _rule_defaults.items():
            rule_document = documents[f'{_ruleset_name}_{rule_name}']
            assert _default_values(rule_document) == defaults, rule_name

# ################################################################################################################################

    def test_every_rule_but_the_silence_one_ships_active(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        documents = _get_documents(backend, _ruleset_name)

        # A rule that ships active carries no switch at all, the one that ships off carries it turned off
        for full_name, rule_document in documents.items():
            if full_name == f'{_ruleset_name}_{_silence_rule_name}':
                assert rule_document['is_active'] is False, full_name
            else:
                assert 'is_active' not in rule_document, full_name

# ################################################################################################################################

    def test_a_fact_from_each_measure_reaches_its_rule(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        rules = load_alert_rules(backend)
        rules_by_full_name = {rule.full_name: rule for rule in rules}

        for rule_name, measures in _rule_measures.items():
            rule = rules_by_full_name[f'{_ruleset_name}_{rule_name}']

            fact = new_fact(AuditSource.MCP, _gateway_name)
            fact.update(measures)
            assert rule.match({Fact_Entity: fact}), f'Expected {rule_name} to match {fact}'

            # The same measures on another kind of object are its own ruleset's business
            for source in _other_sources:
                fact = new_fact(source, _gateway_name)
                fact.update(measures)
                assert not rule.match({Fact_Entity: fact}), f'Expected {rule_name} not to match {fact}'

# ################################################################################################################################

    def test_the_two_slow_rules_hand_over_at_the_error_value(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        rules = load_alert_rules(backend)
        rules_by_full_name = {rule.full_name: rule for rule in rules}

        warning = rules_by_full_name[f'{_ruleset_name}_Slow_Tool_Calls']
        error = rules_by_full_name[f'{_ruleset_name}_Slow_Tool_Calls_Error']

        fact = new_fact(AuditSource.MCP, _gateway_name)
        fact['avg_duration_ms'] = 14999

        assert warning.match({Fact_Entity: fact})
        assert not error.match({Fact_Entity: fact})

        fact['avg_duration_ms'] = 15000

        assert not warning.match({Fact_Entity: fact})
        assert error.match({Fact_Entity: fact})

# ################################################################################################################################

    def test_the_vocabulary_speaks_the_gateway_terms(self) -> 'None':
        vocabulary = alerting_vocabulary()

        names = set()
        for entity in vocabulary['entities']:
            for attribute in entity['attributes']:
                names.add(attribute['name'])

        for term in _new_terms:
            assert term in names, term

# ################################################################################################################################

    def test_an_old_mcp_ruleset_gains_the_new_rules_and_loses_server_down_on_upgrade(self, backend:'RuleSQLBackend') -> 'None':
        _ = _seed_old_mcp_ruleset(backend)

        documents = _get_documents(backend, _ruleset_name)
        assert len(documents) == 3
        assert f'{_ruleset_name}_{_retired_rule_name}' in documents

        ensure_alerting_definitions(backend)

        ruleset = _get_ruleset(backend, _ruleset_name)
        assert ruleset.current_version == 2
        assert ruleset.live_version == 2

        # Every rule now reads exactly as this release ships it - the new ones arrived, the retired one is gone
        documents = deserialize_document(ruleset.document)[Documents_Key]
        shipped = build_ruleset_document(_ruleset_name, mcp_rules)[Documents_Key]

        assert documents == shipped
        assert f'{_ruleset_name}_{_retired_rule_name}' not in documents

        # A second run has nothing left to refresh
        ensure_alerting_definitions(backend)
        assert _get_ruleset(backend, _ruleset_name).current_version == 2

# ################################################################################################################################
# ################################################################################################################################
