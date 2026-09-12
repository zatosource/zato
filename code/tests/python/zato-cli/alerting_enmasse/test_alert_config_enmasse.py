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

# PyYAML
import yaml

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.exporters.alert_config import AlertConfigExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.alert_config import AlertConfigImporter
from zato.common.alerting.config_map import is_rule_active, Explain_With_LLM_Key
from zato.common.alerting.config_store import get_type_definition
from zato.common.alerting.notification_config import parse_extra, read_notification_config
from zato.common.alerting.sweep import load_alert_rules
from zato.common.api import Alerting, GENERIC
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, IntervalBasedJob, Job, Service
from zato.common.rule_engine.sql import create_database_engine, create_schema, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document
from zato.common.util.scheduler import ensure_alerting_job_exists

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

engine_generator:TypeAlias = Generator[Engine, None, None]

# ################################################################################################################################
# ################################################################################################################################

# The cluster the test job belongs to
_cluster_id = 1

# The LLM connection the notifications name as the deployment's default for explanations
_llm_name = 'enmasse.alerts.default.llm'

# The same YAML a person would write - the rule entries carry every field
# of their type so the export at the end can be compared with them whole.
_yaml_text = """
alert_rules:
  - type: rest
    is_active: true
    consecutive_failures: 5
    error_rate: 20
    window: 3600
    status_codes: 401, 403, 429, 5xx
    status_code_threshold: 5
    status_codes_window: 900
    connection_failures: 2
    connection_failures_window: 600
    max_latency: 7000
    latency_window: 1800
    use_llm: false
  - type: file_transfer
    is_active: true
    consecutive_failures: 4
    warning_failures: 12
    error_failures: 24
    window: 43200
    test_transfers: false
    arrival_overdue: 2
    use_llm: true

alert_notifications:
  slack_webhook: https://hooks.slack.example.com/services/T000/B000/XXX
  teams_webhook: https://example.webhook.office.com/webhookb2/abc
  webhook_url: https://example.atlassian.net/automation/webhooks/abc
  email_connection: default.alerts.notifications
  email_to: ops@example.com
  email_from: alerts@example.com
  dashboard_url: https://dashboard.example.com
  llm_connection: enmasse.alerts.default.llm
"""

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def yaml_config() -> 'stranydict':
    out = yaml.safe_load(_yaml_text)
    return out

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
    """ Returns the complete backend over the isolated test database - fresh,
    without the definitions, which is what the importer has to cope with on its own.
    """
    out = RuleSQLBackend.from_engine(rule_database_engine)
    return out

# ################################################################################################################################

@pytest.fixture
def odb_session() -> 'any_':
    """ A real ODB session over an in-memory SQLite database holding
    the scheduler tables, one cluster and the alerting sweep job.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        Service.__table__,
        Job.__table__,
        IntervalBasedJob.__table__,
        GenericConnDef.__table__,
        GenericConn.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)

    llm = GenericConn()
    llm.name = _llm_name
    llm.type_ = GENERIC.CONNECTION.TYPE.OUTCONN_LLM
    llm.is_active = True
    llm.is_internal = False
    llm.is_channel = False
    llm.is_outconn = True
    llm.cluster = cluster
    session.add(llm)

    session.commit()

    _ = ensure_alerting_job_exists(session, _cluster_id)
    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

@pytest.fixture
def alert_config_importer() -> 'AlertConfigImporter':
    out = AlertConfigImporter(EnmasseYAMLImporter())
    return out

# ################################################################################################################################

@pytest.fixture
def alert_config_exporter() -> 'AlertConfigExporter':
    out = AlertConfigExporter(EnmasseYAMLExporter())
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAlertRulesImport:

    def test_an_import_reaches_the_sweep(
        self,
        yaml_config:'stranydict',
        backend:'RuleSQLBackend',
        alert_config_importer:'AlertConfigImporter',
    ) -> 'None':

        created, updated = alert_config_importer.sync_alert_rules(yaml_config['alert_rules'], backend)

        # Rules are never created, only updated - and both entries moved values
        assert created == []
        assert len(updated) == 2

        # The sweep loads its rules from the live versions, so it already
        # runs with the imported thresholds, in rule units
        rules = load_alert_rules(backend)
        rules_by_full_name = {rule.full_name: rule for rule in rules}

        down_rule = rules_by_full_name['alerts_rest_Connection_Down']
        assert down_rule.defaults['max_consecutive_failures'] == 5

        error_rule = rules_by_full_name['alerts_rest_Error_Rate']
        assert error_rule.defaults['error_rate_threshold'] == 0.2

        # The window travels in seconds, straight into the rule default the sweep measures over
        assert error_rule.defaults['window_seconds'] == 3600

        # The Use LLM switch landed on every rule of the type
        for rule in rules:
            if rule.full_name.startswith('alerts_rest_'):
                assert rule.document[Explain_With_LLM_Key] is False, rule.full_name

        slow_rule = rules_by_full_name['alerts_rest_Slow_Responses']
        assert slow_rule.defaults['max_avg_duration_ms'] == 7000

        transfer_rule = rules_by_full_name['alerts_file_transfer_Transfer_Failures']
        assert transfer_rule.defaults['warning_failure_count'] == 12
        assert transfer_rule.defaults['error_failure_count'] == 24
        assert transfer_rule.defaults['window_seconds'] == 43200

        transfer_error_rule = rules_by_full_name['alerts_file_transfer_Transfer_Failures_Error']
        assert transfer_error_rule.defaults['window_seconds'] == 43200

        # The test transfers toggle turned its test transfer rule off while the type
        # itself stays active - the entry's is_active did not overwrite the toggle
        definition = get_type_definition(backend, 'file_transfer')
        documents = deserialize_document(definition.document)[Documents_Key]

        assert documents['alerts_file_transfer_Test_Transfer_Failing']['is_active'] is False
        assert is_rule_active(documents['alerts_file_transfer_Transfer_Failures']) is True

# ################################################################################################################################

    def test_a_re_import_stores_no_new_versions(
        self,
        yaml_config:'stranydict',
        backend:'RuleSQLBackend',
        alert_config_importer:'AlertConfigImporter',
    ) -> 'None':

        _, updated = alert_config_importer.sync_alert_rules(yaml_config['alert_rules'], backend)
        assert len(updated) == 2

        # The versions the first import produced
        versions = {}
        for entry in yaml_config['alert_rules']:
            definition = get_type_definition(backend, entry['type'])
            versions[entry['type']] = definition.current_version

        # The same YAML again - nothing changed, so nothing was stored
        _, updated = alert_config_importer.sync_alert_rules(yaml_config['alert_rules'], backend)
        assert updated == []

        for entry in yaml_config['alert_rules']:
            definition = get_type_definition(backend, entry['type'])
            assert definition.current_version == versions[entry['type']], entry['type']

# ################################################################################################################################
# ################################################################################################################################

class TestAlertNotificationsImport:

    def test_an_import_lands_in_the_sweep_job(
        self,
        yaml_config:'stranydict',
        odb_session:'any_',
        alert_config_importer:'AlertConfigImporter',
    ) -> 'None':

        changed = alert_config_importer.sync_alert_notifications(yaml_config['alert_notifications'], odb_session)
        assert changed is True

        job = odb_session.query(Job).\
            filter(Job.name==Alerting.Job_Name).\
            filter(Job.cluster_id==_cluster_id).\
            one()

        parsed = parse_extra(job.extra)

        # The YAML speaks the screen's vocabulary - the extra keeps its own keys
        assert parsed[Alerting.Extra_Slack_Webhook] == yaml_config['alert_notifications']['slack_webhook']
        assert parsed[Alerting.Extra_Default_To] == yaml_config['alert_notifications']['email_to']
        assert parsed[Alerting.Extra_From] == yaml_config['alert_notifications']['email_from']
        assert parsed[Alerting.Extra_Dashboard_URL] == yaml_config['alert_notifications']['dashboard_url']
        assert parsed[Alerting.Extra_LLM_Connection] == _llm_name

# ################################################################################################################################

    def test_a_missing_llm_connection_is_rejected(
        self,
        yaml_config:'stranydict',
        odb_session:'any_',
        alert_config_importer:'AlertConfigImporter',
    ) -> 'None':

        notifications = dict(yaml_config['alert_notifications'])
        notifications['llm_connection'] = 'enmasse.no.such.llm'

        with pytest.raises(Exception) as context:
            _ = alert_config_importer.sync_alert_notifications(notifications, odb_session)

        assert 'enmasse.no.such.llm' in str(context.value)

# ################################################################################################################################

    def test_an_empty_llm_connection_means_no_default(
        self,
        yaml_config:'stranydict',
        odb_session:'any_',
        alert_config_importer:'AlertConfigImporter',
    ) -> 'None':

        notifications = dict(yaml_config['alert_notifications'])
        notifications['llm_connection'] = ''

        changed = alert_config_importer.sync_alert_notifications(notifications, odb_session)
        assert changed is True

        job = odb_session.query(Job).filter(Job.name==Alerting.Job_Name).one()

        # An empty value is not stored in the extra at all and reads back as empty
        assert Alerting.Extra_LLM_Connection not in parse_extra(job.extra)
        assert read_notification_config(job.extra)[Alerting.Extra_LLM_Connection] == ''

# ################################################################################################################################

    def test_a_re_import_changes_nothing(
        self,
        yaml_config:'stranydict',
        odb_session:'any_',
        alert_config_importer:'AlertConfigImporter',
    ) -> 'None':

        changed = alert_config_importer.sync_alert_notifications(yaml_config['alert_notifications'], odb_session)
        assert changed is True

        changed = alert_config_importer.sync_alert_notifications(yaml_config['alert_notifications'], odb_session)
        assert changed is False

# ################################################################################################################################
# ################################################################################################################################

class TestAlertConfigExport:

    def test_an_export_matches_what_was_imported(
        self,
        yaml_config:'stranydict',
        backend:'RuleSQLBackend',
        odb_session:'any_',
        alert_config_importer:'AlertConfigImporter',
        alert_config_exporter:'AlertConfigExporter',
    ) -> 'None':

        _ = alert_config_importer.sync_alert_rules(yaml_config['alert_rules'], backend)
        _ = alert_config_importer.sync_alert_notifications(yaml_config['alert_notifications'], odb_session)

        # The export covers every type - the two the YAML moved read back
        # exactly as the YAML wrote them, in the screen's units
        exported_rules = alert_config_exporter.export_rules(backend)
        exported_by_type = {entry['type']: entry for entry in exported_rules}

        for entry in yaml_config['alert_rules']:
            assert exported_by_type[entry['type']] == entry, entry['type']

        # And the notification targets travel back under the YAML's own names
        exported_notifications = alert_config_exporter.export_notifications(odb_session, _cluster_id)
        assert exported_notifications == yaml_config['alert_notifications']

# ################################################################################################################################

    def test_an_export_of_a_fresh_store_shows_the_defaults(
        self,
        backend:'RuleSQLBackend',
        alert_config_exporter:'AlertConfigExporter',
    ) -> 'None':

        # A store the server never seeded exports what the config screen
        # would show - the seeded defaults, one entry per type, all active
        exported_rules = alert_config_exporter.export_rules(backend)
        exported_by_type = {entry['type']: entry for entry in exported_rules}

        rest_entry = exported_by_type['rest']

        assert rest_entry['is_active'] is True
        assert rest_entry['consecutive_failures'] == 3
        assert rest_entry['error_rate'] == 10
        assert rest_entry['window'] == 300
        assert rest_entry['max_latency'] == 5000
        assert rest_entry['use_llm'] is True

        # The file transfer window ships as one day, in seconds
        file_transfer_entry = exported_by_type['file_transfer']
        assert file_transfer_entry['window'] == 86400

# ################################################################################################################################
# ################################################################################################################################
