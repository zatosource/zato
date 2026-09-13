# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The outgoing REST rules the rest ruleset ships - the two rules about status codes and connection failures with
# their defaults, the window the slow responses rule gained, an old ruleset gaining all of that on upgrade, and a
# fact from each measure reaching its rule for a REST connection and not for a SOAP one.

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
from zato.common.alerting.seed.rules_connections import rest_rules, soap_rules
from zato.common.alerting.seed.rules_fhir import fhir_rules
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

# The ruleset the outgoing REST connections are judged by
_rest_ruleset_name = 'alerts_rest'
_soap_ruleset_name = 'alerts_soap'
_fhir_ruleset_name = 'alerts_fhir'

# The rules the rest ruleset ships, with the defaults each one carries
_rest_rule_defaults = {
    'Connection_Down':     {'max_consecutive_failures': 3},
    'Slow_Responses':      {'max_avg_duration_ms': 5000, 'window_seconds': 300},
    'Error_Rate':          {'error_rate_threshold': 0.1, 'min_events': 10, 'window_seconds': 300},
    'Status_Codes':        {'status_codes': '401, 403, 5xx', 'status_code_threshold': 3, 'window_seconds': 300},
    'Connection_Failures': {'connection_failure_threshold': 3, 'window_seconds': 300},
}

# The rules the soap ruleset ships - the rest ones over the SOAP sources and the faults on top
_soap_rule_defaults = dict(_rest_rule_defaults)
_soap_rule_defaults['SOAP_Faults'] = {'fault_codes': 'Receiver, Server, Sender, Client', 'fault_threshold': 3, 'window_seconds': 300}

# The rules the fhir ruleset ships - the rest ones over the FHIR sources and the operation outcomes on top
_fhir_rule_defaults = dict(_rest_rule_defaults)
_fhir_rule_defaults['Operation_Outcomes'] = {
    'outcome_codes': 'exception, transient, timeout, throttled, lock-error, no-store, too-costly',
    'outcome_threshold': 3,
    'window_seconds': 300,
}

# The rest ruleset as the release before this one shipped it - three rules, the slow responses one without a window
_old_rest_rules = """
rule
    Connection_Down
docs
    A REST or SOAP outgoing connection that failed three consecutive times is considered down and raises an error email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source in ['rest-outgoing', 'soap-outgoing', 'rest-outgoing-health', 'soap-outgoing-health'] and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    Slow_Responses
docs
    A REST or SOAP outgoing connection whose average response time within the window exceeds five seconds raises an email alert.
defaults
    max_avg_duration_ms = 5000
when
    alert.source in ['rest-outgoing', 'soap-outgoing', 'rest-outgoing-health', 'soap-outgoing-health'] and
    alert.avg_duration_ms is at least default.max_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate
docs
    A REST or SOAP outgoing connection whose error share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
    window_seconds = 300
when
    alert.source in ['rest-outgoing', 'soap-outgoing', 'rest-outgoing-health', 'soap-outgoing-health'] and
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
    """ Returns one seeded ruleset definition, or fails when there is none.
    """
    matches = backend.definitions.find_by_name(name=name, object_type=Definition_Type_Ruleset)
    assert len(matches) == 1

    out = matches[0]
    return out

# ################################################################################################################################

def _default_values(rule_document:'stranydict') -> 'stranydict':
    """ The defaults of one stored rule document by name, each reduced to its value.
    """
    out = {}

    for name, default in rule_document['defaults'].items():
        out[name] = default['value']

    return out

# ################################################################################################################################

def _seed_old_rest_ruleset(backend:'RuleSQLBackend') -> 'RuleDefinitionRecord':
    """ The rest ruleset as the release before this one seeded it.
    """
    document = build_ruleset_document(_rest_ruleset_name, _old_rest_rules)

    out = backend.definitions.create(
        name=_rest_ruleset_name,
        object_type=Definition_Type_Ruleset,
        document=document,
        author='test',
        comment='From before the status code rules',
    )
    _ = backend.versions.publish(definition_id=out.id, version=out.current_version, actor='test')

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRestRules:

    def test_the_rest_ruleset_ships_five_rules_with_their_defaults(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        ruleset = _get_ruleset(backend, _rest_ruleset_name)
        documents = deserialize_document(ruleset.document)[Documents_Key]

        assert len(documents) == len(_rest_rule_defaults)

        for rule_name, defaults in _rest_rule_defaults.items():
            rule_document = documents[f'{_rest_ruleset_name}_{rule_name}']
            assert _default_values(rule_document) == defaults, rule_name

# ################################################################################################################################

    def test_an_old_rest_ruleset_gains_the_two_rules_and_the_window_on_upgrade(self, backend:'RuleSQLBackend') -> 'None':
        _ = _seed_old_rest_ruleset(backend)

        ensure_alerting_definitions(backend)

        ruleset = _get_ruleset(backend, _rest_ruleset_name)
        assert ruleset.current_version == 2
        assert ruleset.live_version == 2

        # Every rule now reads exactly as this release ships it - the two new ones arrived
        # and the untouched slow responses rule gained its window
        documents = deserialize_document(ruleset.document)[Documents_Key]
        shipped = build_ruleset_document(_rest_ruleset_name, rest_rules)[Documents_Key]

        assert documents == shipped

        for rule_name, defaults in _rest_rule_defaults.items():
            assert _default_values(documents[f'{_rest_ruleset_name}_{rule_name}']) == defaults, rule_name

        # A second run has nothing left to refresh
        ensure_alerting_definitions(backend)
        assert _get_ruleset(backend, _rest_ruleset_name).current_version == 2

# ################################################################################################################################

    def test_the_soap_ruleset_ships_six_rules_with_their_defaults(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        ruleset = _get_ruleset(backend, _soap_ruleset_name)
        documents = deserialize_document(ruleset.document)[Documents_Key]

        assert len(documents) == len(_soap_rule_defaults)

        for rule_name, defaults in _soap_rule_defaults.items():
            rule_document = documents[f'{_soap_ruleset_name}_{rule_name}']
            assert _default_values(rule_document) == defaults, rule_name

# ################################################################################################################################

    def test_the_soap_ruleset_arrives_and_the_rest_one_narrows_on_upgrade(self, backend:'RuleSQLBackend') -> 'None':

        # The release before this one judged SOAP connections by the rest ruleset and had no soap one
        _ = _seed_old_rest_ruleset(backend)
        assert backend.definitions.find_by_name(name=_soap_ruleset_name, object_type=Definition_Type_Ruleset) == []

        ensure_alerting_definitions(backend)

        # The soap ruleset is there now, as this release ships it ..
        soap_ruleset = _get_ruleset(backend, _soap_ruleset_name)
        soap_documents = deserialize_document(soap_ruleset.document)[Documents_Key]
        assert soap_documents == build_ruleset_document(_soap_ruleset_name, soap_rules)[Documents_Key]

        # .. and the rest one no longer speaks of SOAP sources anywhere.
        rest_ruleset = _get_ruleset(backend, _rest_ruleset_name)
        rest_documents = deserialize_document(rest_ruleset.document)[Documents_Key]

        for full_name, document in rest_documents.items():
            assert 'soap' not in str(document['conditions']), full_name

# ################################################################################################################################

    def test_the_fhir_ruleset_ships_six_rules_with_their_defaults(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        ruleset = _get_ruleset(backend, _fhir_ruleset_name)
        documents = deserialize_document(ruleset.document)[Documents_Key]

        assert len(documents) == len(_fhir_rule_defaults)

        for rule_name, defaults in _fhir_rule_defaults.items():
            rule_document = documents[f'{_fhir_ruleset_name}_{rule_name}']
            assert _default_values(rule_document) == defaults, rule_name

        # An OperationOutcome is judged over the connection's traffic alone, the other rules over its check too
        outcomes_document = documents[f'{_fhir_ruleset_name}_Operation_Outcomes']
        assert 'fhir-health' not in str(outcomes_document['conditions'])

        down_document = documents[f'{_fhir_ruleset_name}_Connection_Down']
        assert 'fhir-health' in str(down_document['conditions'])

# ################################################################################################################################

    def test_the_fhir_ruleset_arrives_on_upgrade(self, backend:'RuleSQLBackend') -> 'None':

        # The release before this one had no fhir ruleset
        _ = _seed_old_rest_ruleset(backend)
        assert backend.definitions.find_by_name(name=_fhir_ruleset_name, object_type=Definition_Type_Ruleset) == []

        ensure_alerting_definitions(backend)

        fhir_ruleset = _get_ruleset(backend, _fhir_ruleset_name)
        fhir_documents = deserialize_document(fhir_ruleset.document)[Documents_Key]
        assert fhir_documents == build_ruleset_document(_fhir_ruleset_name, fhir_rules)[Documents_Key]

# ################################################################################################################################

    def test_the_vocabulary_speaks_the_new_connection_terms(self) -> 'None':
        vocabulary = alerting_vocabulary()

        names = set()
        for entity in vocabulary['entities']:
            for attribute in entity['attributes']:
                names.add(attribute['name'])

        assert 'status_code_count' in names
        assert 'connection_failure_count' in names
        assert 'fault_count' in names
        assert 'outcome_count' in names

# ################################################################################################################################

    def test_a_fact_from_each_traffic_measure_reaches_its_rule_for_the_traffic_alone(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        rules = load_alert_rules(backend)
        rules_by_full_name = {rule.full_name: rule for rule in rules}

        cases = [
            ('Status_Codes',        {'status_code_count': 3}),
            ('Connection_Failures', {'connection_failure_count': 3}),
        ]

        # Each outgoing kind is judged by the ruleset of its own type ..
        rulesets_by_source = {
            AuditSource.REST_Outgoing: _rest_ruleset_name,
            AuditSource.SOAP_Outgoing: _soap_ruleset_name,
            AuditSource.FHIR: _fhir_ruleset_name,
        }

        for rule_name, measures in cases:
            for source, ruleset_name in rulesets_by_source.items():

                rule = rules_by_full_name[f'{ruleset_name}_{rule_name}']

                fact = new_fact(source, 'crm.api')
                fact.update(measures)
                assert rule.match({Fact_Entity: fact}), f'Expected {rule_name} to match {fact}'

                # .. never by the other kind's ..
                for other_source in rulesets_by_source:
                    if other_source == source:
                        continue
                    other_fact = new_fact(other_source, 'crm.api')
                    other_fact.update(measures)
                    assert not rule.match({Fact_Entity: other_fact}), f'Expected {rule_name} not to match {other_fact}'

                # .. and a connection's health check is not, it has the rules on streaks, rates and latency for that.
                for health_source in (AuditSource.REST_Outgoing_Health, AuditSource.SOAP_Outgoing_Health, AuditSource.FHIR_Health):
                    health_fact = new_fact(health_source, 'crm.api')
                    health_fact.update(measures)
                    assert not rule.match({Fact_Entity: health_fact}), f'Expected {rule_name} not to match {health_fact}'

# ################################################################################################################################
# ################################################################################################################################
