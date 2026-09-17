# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The seeded LLM ruleset - the nine rules it ships with their defaults, all of them active, each rule reached by
# a fact of the measure it reads and none of them reached by any other outgoing connection, and an environment
# seeded with the four rules of the release before gaining the five new ones on upgrade.

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
from zato.common.alerting.seed.rules_llm import llm_rules
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

_ruleset_name = 'alerts_llm'
_conn_name = 'support.assistant'

# The nine rules the ruleset ships, with the defaults each one carries
_rule_defaults = {
    'Connection_Down':        {'max_consecutive_failures': 3},
    'Slow_Completions':       {'warning_avg_duration_ms': 10000, 'error_avg_duration_ms': 15000, 'window_seconds': 300},
    'Slow_Completions_Error': {'error_avg_duration_ms': 15000, 'window_seconds': 300},
    'Error_Rate':             {'error_rate_threshold': 0.1, 'min_events': 10, 'window_seconds': 300},
    'Status_Codes':           {'status_codes': '429, 401, 403, 5xx', 'status_code_threshold': 3, 'window_seconds': 300},
    'Connection_Failures':    {'connection_failure_threshold': 3, 'window_seconds': 300},
    'Truncated_Completions':  {'truncation_threshold': 3, 'window_seconds': 300},
    'Refusals':               {'refusal_threshold': 3, 'window_seconds': 300},
    'Token_Budget':           {'token_budget': 10000000, 'window_seconds': 86400},
}

# One fact per rule, each crafted to clear the rule's default threshold
_rule_measures = {
    'Connection_Down':        {'consecutive_failures': 3},
    'Slow_Completions':       {'avg_duration_ms': 12000},
    'Slow_Completions_Error': {'avg_duration_ms': 15000},
    'Error_Rate':             {'total_count': 20, 'error_count': 4, 'error_rate': 0.2},
    'Status_Codes':           {'status_code_count': 3},
    'Connection_Failures':    {'connection_failure_count': 3},
    'Truncated_Completions':  {'truncation_count': 3},
    'Refusals':               {'refusal_count': 3},
    'Token_Budget':           {'token_count': 10000000},
}

# The sources the LLM rules must leave alone, whatever the measures say
_other_sources = (AuditSource.REST_Outgoing, AuditSource.SOAP_Outgoing, AuditSource.FHIR, AuditSource.MCP)

# The ruleset as the release before this one seeded it - the four rules with no status codes, completions or tokens
_old_llm_rules = """
rule
    Connection_Down
docs
    An LLM connection that failed three consecutive times is considered down and raises an error email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'llm' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Slow_Completions
docs
    An LLM connection whose average completion time within the window exceeds ten seconds raises a warning email alert.
defaults
    warning_avg_duration_ms = 10000
    error_avg_duration_ms = 15000
    window_seconds = 300
when
    alert.source is 'llm' and
    alert.avg_duration_ms is at least default.warning_avg_duration_ms and
    alert.avg_duration_ms is less than default.error_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Slow_Completions_Error
docs
    An LLM connection whose average completion time within the window exceeds fifteen seconds raises an error email alert.
defaults
    error_avg_duration_ms = 15000
    window_seconds = 300
when
    alert.source is 'llm' and
    alert.avg_duration_ms is at least default.error_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Error_Rate
docs
    An LLM connection whose failed-completion share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
    window_seconds = 300
when
    alert.source is 'llm' and
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

def _seed_old_llm_ruleset(backend:'RuleSQLBackend') -> 'RuleDefinitionRecord':
    """ The LLM ruleset as the release before this one seeded it.
    """
    document = build_ruleset_document(_ruleset_name, _old_llm_rules)

    out = backend.definitions.create(
        name=_ruleset_name,
        object_type=Definition_Type_Ruleset,
        document=document,
        author='test',
        comment='From before the completion and token rules',
    )
    _ = backend.versions.publish(definition_id=out.id, version=out.current_version, actor='test')

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestLLMRules:

    def test_the_ruleset_ships_nine_rules_with_their_defaults(self, backend:'RuleSQLBackend') -> 'None':
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

            fact = new_fact(AuditSource.LLM, _conn_name)
            fact.update(measures)
            assert rule.match({Fact_Entity: fact}), f'Expected {rule_name} to match {fact}'

            # The same measures on another outgoing connection are its own ruleset's business
            for source in _other_sources:
                fact = new_fact(source, _conn_name)
                fact.update(measures)
                assert not rule.match({Fact_Entity: fact}), f'Expected {rule_name} not to match {fact}'

# ################################################################################################################################

    def test_a_truncation_and_a_refusal_are_told_apart(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        rules = load_alert_rules(backend)
        rules_by_full_name = {rule.full_name: rule for rule in rules}

        truncations = rules_by_full_name[f'{_ruleset_name}_Truncated_Completions']
        refusals = rules_by_full_name[f'{_ruleset_name}_Refusals']

        fact = new_fact(AuditSource.LLM, _conn_name)
        fact['truncation_count'] = 3

        assert truncations.match({Fact_Entity: fact})
        assert not refusals.match({Fact_Entity: fact})

        fact = new_fact(AuditSource.LLM, _conn_name)
        fact['refusal_count'] = 3

        assert refusals.match({Fact_Entity: fact})
        assert not truncations.match({Fact_Entity: fact})

# ################################################################################################################################

    def test_an_old_llm_ruleset_gains_the_five_rules_on_upgrade(self, backend:'RuleSQLBackend') -> 'None':
        _ = _seed_old_llm_ruleset(backend)

        assert len(_get_documents(backend, _ruleset_name)) == 4

        ensure_alerting_definitions(backend)

        ruleset = _get_ruleset(backend, _ruleset_name)
        assert ruleset.current_version == 2
        assert ruleset.live_version == 2

        # Every rule now reads exactly as this release ships it - the five new ones arrived
        # and the untouched four read as they do today
        documents = deserialize_document(ruleset.document)[Documents_Key]
        shipped = build_ruleset_document(_ruleset_name, llm_rules)[Documents_Key]

        assert documents == shipped

        # A second run has nothing left to refresh
        ensure_alerting_definitions(backend)
        assert _get_ruleset(backend, _ruleset_name).current_version == 2

# ################################################################################################################################
# ################################################################################################################################
