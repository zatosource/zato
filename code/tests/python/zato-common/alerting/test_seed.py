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
from zato.common.alerting.engine import AlertTransports
from zato.common.alerting.seed import alerting_vocabulary, alerts_ruleset, ensure_alerting_definitions
from zato.common.alerting.sweep import load_alert_rules, run_sweep
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

# The default rule the sweep test expects to fire
_rest_rule_name = 'REST_Outgoing_Error_Rate'

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

def _get_ruleset(backend:'RuleSQLBackend') -> 'RuleDefinitionRecord':
    """ Returns the seeded alerts ruleset definition, or fails when there is none.
    """
    matches = backend.definitions.find_by_name(name=Alerting.Ruleset_Name, object_type=Definition_Type_Ruleset)
    assert len(matches) == 1

    out = matches[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestEnsureAlertingDefinitions:

    def test_a_new_environment_gains_both_definitions_published(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        # The ruleset is stored and its first version is already the live one ..
        ruleset = _get_ruleset(backend)
        assert ruleset.current_version == 1
        assert ruleset.live_version == 1

        # .. and so is the vocabulary the rules are written in.
        matches = backend.definitions.find_by_name(name=Alerting.Vocabulary_Name, object_type=Definition_Type_Vocabulary)
        assert len(matches) == 1
        assert matches[0].live_version == 1

# ################################################################################################################################

    def test_the_seeded_documents_are_the_canonical_ones(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        ruleset = _get_ruleset(backend)
        document = deserialize_document(ruleset.document)

        expected = alerts_ruleset()
        assert document[Documents_Key] == expected[Documents_Key]

        vocabulary = backend.definitions.find_by_name(
            name=Alerting.Vocabulary_Name, object_type=Definition_Type_Vocabulary)[0]
        vocabulary_document = deserialize_document(vocabulary.document)

        assert vocabulary_document == alerting_vocabulary()

# ################################################################################################################################

    def test_a_second_run_changes_nothing(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)
        ensure_alerting_definitions(backend)

        ruleset = _get_ruleset(backend)
        assert ruleset.current_version == 1

# ################################################################################################################################

    def test_a_persons_edit_is_never_touched(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        # A person deletes every rule but one, as the listing screen would ..
        ruleset = _get_ruleset(backend)
        document = deserialize_document(ruleset.document)
        documents = document[Documents_Key]

        kept_key = f'{Alerting.Ruleset_Name}_{_rest_rule_name}'
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

        ruleset = _get_ruleset(backend)
        assert ruleset.current_version == 2

        document = deserialize_document(ruleset.document)
        assert list(document[Documents_Key]) == [kept_key]

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

        # The seeded rules load straight from the live version
        rules = load_alert_rules(backend)
        rule_names = [rule.name for rule in rules]
        assert _rest_rule_name in rule_names

        audit_log = AuditLog(_server_name)
        audit_engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        # A REST outgoing connection erroring on all its traffic - above the default quarter
        _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _conn_name,
            cid='seed-sweep-1', outcome=AuditOutcome.Error)
        _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _conn_name,
            cid='seed-sweep-2', outcome=AuditOutcome.Error)

        result = run_sweep(
            audit_engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, 'cid-seed-1', now,
            default_email=['ops@example.com'])

        # The REST outgoing rule fired and dispatched the incident diagnosis
        assert result.raised_count == 1
        assert len(recorder.invocations) == 1

        service, payload = recorder.invocations[0]
        assert service == Incidents.Service_Diagnose
        assert payload['rule'] == _rest_rule_name
        assert payload['object_name'] == _conn_name

# ################################################################################################################################
# ################################################################################################################################
