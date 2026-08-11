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
from zato.common.alerting.collectors import new_fact
from zato.common.alerting.engine import AlertTransports
from zato.common.alerting.seed import alerting_vocabulary, build_ruleset_document, default_rulesets, \
    ensure_alerting_definitions
from zato.common.alerting.sweep import load_alert_rules, run_sweep, Fact_Entity
from zato.common.api import Alerting, Incidents
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.rule_engine.sql import create_database_engine, create_schema, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Definition_Type_Vocabulary, Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleDefinitionRecord
    from zato.common.typing_ import anylist, stranydict
    anylist = anylist
    RuleDefinitionRecord = RuleDefinitionRecord
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

engine_generator:TypeAlias = Generator[Engine, None, None]

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-seed-server'

# The connection the sweep test seeds error events for
_conn_name = 'CRM'

# The ruleset the sweep test's rule lives in and the rule it expects to fire
_rest_ruleset_name = 'alerts_rest'
_incident_rule_name = 'Error_Rate_Incident'

# The rule that ships inactive - the canary writes to remote systems, activating it is the opt-in
_canary_full_name = 'alerts_file_transfer_Canary_Failing'

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
# ################################################################################################################################

class TestEnsureAlertingDefinitions:

    def test_a_new_environment_gains_every_definition_published(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        # Every default ruleset is stored and its first version is already the live one ..
        for ruleset_name, _ in default_rulesets:
            ruleset = _get_ruleset(backend, ruleset_name)
            assert ruleset.current_version == 1, ruleset_name
            assert ruleset.live_version == 1, ruleset_name

        # .. and so is the vocabulary the rules are written in.
        matches = backend.definitions.find_by_name(name=Alerting.Vocabulary_Name, object_type=Definition_Type_Vocabulary)
        assert len(matches) == 1
        assert matches[0].live_version == 1

# ################################################################################################################################

    def test_the_seeded_documents_are_the_canonical_ones(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        for ruleset_name, zrules_contents in default_rulesets:
            ruleset = _get_ruleset(backend, ruleset_name)
            document = deserialize_document(ruleset.document)

            expected = build_ruleset_document(ruleset_name, zrules_contents)
            assert document[Documents_Key] == expected[Documents_Key], ruleset_name

        vocabulary = backend.definitions.find_by_name(
            name=Alerting.Vocabulary_Name, object_type=Definition_Type_Vocabulary)[0]
        vocabulary_document = deserialize_document(vocabulary.document)

        assert vocabulary_document == alerting_vocabulary()

# ################################################################################################################################

    def test_a_second_run_changes_nothing(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)
        ensure_alerting_definitions(backend)

        for ruleset_name, _ in default_rulesets:
            ruleset = _get_ruleset(backend, ruleset_name)
            assert ruleset.current_version == 1, ruleset_name

# ################################################################################################################################

    def test_a_persons_edit_is_never_touched(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        # A person deletes every rule but one, as the listing screen would ..
        ruleset = _get_ruleset(backend, _rest_ruleset_name)
        document = deserialize_document(ruleset.document)
        documents = document[Documents_Key]

        kept_key = f'{_rest_ruleset_name}_{_incident_rule_name}'
        edited = {kept_key: documents[kept_key]}

        _ = backend.versions.create(
            definition_id=ruleset.id,
            expected_current_version=ruleset.current_version,
            document={Documents_Key: edited},
            author='test',
            comment='Edited by a person',
        )

        # .. and re-seeding leaves the edit exactly as it was.
        ensure_alerting_definitions(backend)

        ruleset = _get_ruleset(backend, _rest_ruleset_name)
        assert ruleset.current_version == 2

        document = deserialize_document(ruleset.document)
        assert list(document[Documents_Key]) == [kept_key]

# ################################################################################################################################

    def test_the_canary_rule_ships_inactive(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        ruleset = _get_ruleset(backend, 'alerts_file_transfer')
        document = deserialize_document(ruleset.document)

        canary = document[Documents_Key][_canary_full_name]
        assert canary['is_active'] is False

# ################################################################################################################################
# ################################################################################################################################

class _TransportRecorder:
    """ A stand-in for the real transports, remembering everything that went out.
    """
    def __init__(self) -> 'None':
        self.emails:'anylist' = []
        self.invocations:'anylist' = []

    def make(self) -> 'AlertTransports':
        out = AlertTransports()

        def send_email(addresses:'anylist', subject:'str', body:'str') -> 'None':
            self.emails.append((addresses, subject, body))

        def invoke_service(service:'str', payload:'stranydict') -> 'None':
            self.invocations.append((service, payload))

        out.send_email = send_email
        out.invoke_service = invoke_service

        return out

# ################################################################################################################################
# ################################################################################################################################

class TestSweepOverSeededRules:

    def test_the_sweep_runs_against_the_default_rules_unmodified(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        # The seeded rules load straight from the live versions of every default ruleset
        rules = load_alert_rules(backend)
        rule_names = [rule.name for rule in rules]
        assert _incident_rule_name in rule_names

        audit_log = AuditLog(_server_name)
        audit_engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        # A REST outgoing connection erroring on all its traffic, with enough of it
        # to clear the thin-traffic guard - above the default quarter threshold
        for index in range(12):
            _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Response_Received, _conn_name,
                cid=f'seed-sweep-{index}', outcome=AuditOutcome.Error)

        result = run_sweep(
            audit_engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, 'cid-seed-1', now,
            default_email=['ops@example.com'])

        # The incident rule fired and dispatched the incident diagnosis
        assert result.raised_count >= 1

        incident_invocations = [item for item in recorder.invocations if item[0] == Incidents.Service_Diagnose]
        assert len(incident_invocations) == 1

        service, payload = incident_invocations[0]
        assert service == Incidents.Service_Diagnose
        assert payload['rule'] == _incident_rule_name
        assert payload['object_name'] == _conn_name

# ################################################################################################################################
# ################################################################################################################################

class TestEachFamilyReachesItsRule:

    # One fact per family, each crafted to clear one representative rule's default
    # thresholds, with the full name of the rule it must reach. The facts start
    # from new_fact so every measure a rule may reference is present.
    def _family_cases(self) -> 'anylist':

        cases = []

        def case(full_name:'str', source:'str', **measures:'object') -> 'None':
            fact = new_fact(source, 'test-object')
            fact.update(measures)
            cases.append((full_name, fact))

        case('alerts_common_Outstanding_Backlog', AuditSource.MLLP_Outgoing, outstanding=100)
        case('alerts_common_Certificate_Expiring', AuditSource.Certificate, cert_days_left=3)
        case('alerts_channels_Channel_Error_Rate', AuditSource.REST_Channel, total_count=20, error_count=4, error_rate=0.2)
        case('alerts_rest_Connection_Down', AuditSource.REST_Outgoing, consecutive_failures=3)
        case('alerts_sql_Slow_Queries', AuditSource.SQL_Outgoing, avg_duration_ms=6000)
        case('alerts_llm_Slow_Completions', AuditSource.LLM, avg_duration_ms=12000)
        case('alerts_mcp_Server_Down', AuditSource.MCP, consecutive_failures=3)
        case('alerts_microsoft_Service_Degraded', AuditSource.Microsoft_Health, health_state='degraded')
        case('alerts_email_Auth_Failures', AuditSource.Email_SMTP, auth_failure_count=3)
        case('alerts_odoo_Connection_Down', AuditSource.Odoo, consecutive_failures=3)
        case('alerts_file_transfer_Transfer_Failures', AuditSource.File_Outgoing,
            total_count=30, error_count=12, error_rate=0.4)
        case('alerts_scheduler_Missed_Run', AuditSource.Scheduler, overdue_ratio=2.5)

        return cases

# ################################################################################################################################

    def test_a_fact_from_each_family_reaches_its_rule(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        rules = load_alert_rules(backend)
        rules_by_full_name = {rule.full_name: rule for rule in rules}

        for full_name, fact in self._family_cases():

            rule = rules_by_full_name[full_name]
            match_result = rule.match({Fact_Entity: fact})

            assert match_result, f'Expected {full_name} to match {fact}'

# ################################################################################################################################
# ################################################################################################################################
