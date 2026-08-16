# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The full delivery loop - audit events cross the seeded thresholds, the seeded rules
# load from a real SQL rule store, one sweep runs with real transports, and what each
# receiver holds afterwards is asserted payload by payload. The plain webhook is an
# HTTP receiver of its own and email arrives over real SMTP. Slack and Teams deliver
# through the chat connections behind their transports, so here the transports record
# the channel and the rendered text - the wire itself belongs to the chat framework
# and its own suites.

# stdlib
import json
import os
import smtplib
import sys
import threading
from datetime import timedelta
from email.mime.text import MIMEText
from http.client import OK
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Generator
from urllib.parse import quote

# The port helper is shared with the rule engine jobs suite
# and the SMTP receiver with the other zato-common suites.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'rule_engine_jobs', 'lib')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

# pytest
import pytest

# requests
import requests

# SQLAlchemy
from sqlalchemy import select, update
from sqlalchemy.engine import Engine

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.common.alerting.engine import process_findings, AlertDefaults, AlertTransports
from zato.common.alerting.model import new_finding, new_rule, AlertAction
from zato.common.alerting.seed import build_ruleset_document, ensure_alerting_definitions
from zato.common.alerting.sweep import load_alert_rules, run_sweep
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.rule_engine.sql import create_database_engine, create_schema, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset
from zato.common.util.api import utcnow

# Test helpers
from chat_simulators import find_free_port
from hl7_client.smtp_receiver import SMTPReceiver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict
    any_ = any_
    anylist = anylist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

engine_generator:TypeAlias = Generator[Engine, None, None]

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-full-loop-server'

# Who the test says made the rule store changes
_actor = 'test-full-loop'

# The connections the tests seed events for
_rest_conn_name = 'CRM API'
_sql_conn_name = 'Billing DB'

# The default email addressing - what the sweep job's extra would carry
_addresses = ['ops@example.com']
_email_from = 'zato@example.com'

# The channel the Slack rule posts to and the team and channel the Teams rule sends to
_slack_channel = '#zato-alerts'
_teams_to = 'Zato Ops/Alerts'

# How long a webhook post may take before it is abandoned, in seconds -
# the same wait the server's own transport applies.
_webhook_timeout = 10

# The extra ruleset the full loop adds next to the seeded ones - the seeded rules
# all deliver by email, so the other channels get rules of their own,
# loaded from the same store the seeded ones load from.
_extra_ruleset_name = 'alerts_full_loop'

_extra_rules_text = """
rule
    Slack_On_Errors
docs
    A REST outgoing connection erroring on at least half its traffic is posted to Slack.
defaults
    error_rate_threshold = 0.5
when
    alert.source is 'rest-outgoing' and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'slack'
    outcome.severity = 'warning'
    outcome.slack_channel = '#zato-alerts'

rule
    Teams_On_Errors
docs
    A REST outgoing connection erroring on at least half its traffic is posted to Teams as critical.
defaults
    error_rate_threshold = 0.5
when
    alert.source is 'rest-outgoing' and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'teams'
    outcome.severity = 'critical'
    outcome.teams_to = 'Zato Ops/Alerts'

rule
    Webhook_On_Errors
docs
    A REST outgoing connection erroring on at least half its traffic is posted to the workflow webhook.
defaults
    error_rate_threshold = 0.5
when
    alert.source is 'rest-outgoing' and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'webhook'
    outcome.severity = 'warning'
""".strip()

# ################################################################################################################################
# ################################################################################################################################

class WebhookTestHandler(BaseHTTPRequestHandler):
    """ One webhook receiver - every JSON post lands in its server's own list,
    so each running instance keeps its deliveries to itself.
    """

    def log_message(self, format:'str', *args:'any_') -> 'None':
        pass

    def do_POST(self) -> 'None':

        content_length = int(self.headers['Content-Length'])
        payload = json.loads(self.rfile.read(content_length))

        self.server.received.append({'path': self.path, 'payload': payload}) # type: ignore[attr-defined]

        data = json.dumps({'ok': True}).encode('utf-8')

        self.send_response(OK)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        _ = self.wfile.write(data)

# ################################################################################################################################

def start_webhook_server(port:'int') -> 'ThreadingHTTPServer':
    """ Starts one webhook receiver in a background thread.
    """
    out = ThreadingHTTPServer(('127.0.0.1', port), WebhookTestHandler)
    out.received = [] # type: ignore[attr-defined]

    thread = threading.Thread(target=out.serve_forever, daemon=True)
    thread.start()

    return out

# ################################################################################################################################
# ################################################################################################################################

class _ServiceRecorder:
    """ The transports with no wire of their own in this suite - the service invoker,
    pub/sub and the two chat connections - recorded instead of delivered.
    """
    def __init__(self) -> 'None':
        self.invocations:'anylist' = []
        self.publications:'anylist' = []
        self.slack_messages:'anylist' = []
        self.teams_messages:'anylist' = []

# ################################################################################################################################

def build_transports(smtp_port:'int', recorder:'_ServiceRecorder') -> 'AlertTransports':
    """ The delivery callables - email over real SMTP and the plain webhook over
    real HTTP, the same way the server's own transports deliver, with the chat
    connections recorded.
    """

    def send_email(addresses:'anylist', subject:'str', body:'str') -> 'None':
        mime = MIMEText(body)
        mime['Subject'] = subject
        mime['From'] = _email_from
        mime['To'] = ', '.join(addresses)

        client = smtplib.SMTP('127.0.0.1', smtp_port)
        _ = client.sendmail(_email_from, addresses, mime.as_string())
        _ = client.quit()

    def invoke_service(service_name:'str', payload:'stranydict') -> 'None':
        recorder.invocations.append((service_name, payload))

    def publish(topic_name:'str', payload:'stranydict') -> 'None':
        recorder.publications.append((topic_name, payload))

    def send_slack(channel:'str', text:'str') -> 'None':
        recorder.slack_messages.append((channel, text))

    def send_teams(to:'str', html:'str') -> 'None':
        recorder.teams_messages.append((to, html))

    def http_post(url:'str', payload:'stranydict') -> 'None':
        response = requests.post(url, json=payload, timeout=_webhook_timeout)
        assert response.ok, (url, response.status_code, response.text)

    # Our response to produce
    out = AlertTransports()

    out.send_email = send_email
    out.invoke_service = invoke_service
    out.publish = publish
    out.send_slack = send_slack
    out.send_teams = send_teams
    out.http_post = http_post

    return out

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
    """ Returns the complete backend over the isolated test database, with the default
    alerting definitions seeded and the full loop's own webhook ruleset next to them.
    """
    out = RuleSQLBackend.from_engine(rule_database_engine)
    ensure_alerting_definitions(out)

    # The extra ruleset goes live the same way the seeded ones do
    document = build_ruleset_document(_extra_ruleset_name, _extra_rules_text)
    definition = out.definitions.create(
        name=_extra_ruleset_name,
        object_type=Definition_Type_Ruleset,
        document=document,
        author=_actor,
        comment='The full loop webhook rules',
    )
    _ = out.versions.publish(definition_id=definition.id, version=definition.current_version, actor=_actor)

    return out

# ################################################################################################################################

@pytest.fixture
def webhook_server() -> 'any_':
    """ A running plain webhook receiver - e.g. a workflow backend's automation webhook.
    """
    server = start_webhook_server(find_free_port())

    yield server

    server.shutdown()

# ################################################################################################################################

@pytest.fixture
def smtp_receiver() -> 'any_':
    """ A running aiosmtpd receiver recording every email delivered to it.
    """
    receiver = SMTPReceiver()
    receiver.start()

    yield receiver

    receiver.stop()

# ################################################################################################################################
# ################################################################################################################################

def _server_url(server:'any_', path:'str') -> 'str':
    """ The address one webhook receiver listens on, with the given path.
    """
    port = server.server_address[1]
    out = f'http://127.0.0.1:{port}{path}'
    return out

# ################################################################################################################################

def _build_defaults(webhook_server:'any_') -> 'AlertDefaults':
    """ The deployment-level targets - what the sweep job's extra would carry,
    the plain webhook pointing at its simulated receiver.
    """
    out = AlertDefaults()

    out.email_to = _addresses
    out.webhook_url = _server_url(webhook_server, '/hooks/zato')

    return out

# ################################################################################################################################

def _seed_events() -> 'None':
    """ Audit events that cross the seeded thresholds for two types at once -
    a REST outgoing connection failing on all of its traffic and a database
    connection whose queries average well past the slow-query threshold.
    """
    audit_log = AuditLog(_server_name)

    # Twelve failed calls - an error rate of 100% over at least ten events,
    # with the three newest making the consecutive-failures streak
    for index in range(12):
        _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Response_Received, _rest_conn_name,
            cid=f'rest-{index}', outcome=AuditOutcome.Error, data='HTTP 503 Service Unavailable')

    # Three healthy but slow queries - an 8-second average against the 5-second threshold,
    # and too few events for any error-rate rule to speak
    for index in range(3):
        _ = audit_log.insert(AuditSource.SQL_Outgoing, AuditEvent.Response_Received, _sql_conn_name,
            cid=f'sql-{index}', outcome=AuditOutcome.OK, duration_ms=8000)

# ################################################################################################################################

def _get_raised_events() -> 'list':
    """ Every alert-raised event the audit log holds.
    """
    engine = get_audit_engine()

    query = select(event_table).where(event_table.c.event_type == AuditEvent.Alert_Raised)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestFullLoop:

    def test_one_sweep_delivers_through_every_channel(
        self,
        backend:'RuleSQLBackend',
        webhook_server:'any_',
        smtp_receiver:'any_',
        ) -> 'None':

        _seed_events()

        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        recorder = _ServiceRecorder()
        transports = build_transports(smtp_receiver.port, recorder)
        defaults = _build_defaults(webhook_server)

        rules = load_alert_rules(backend)

        result = run_sweep(engine, rules, {}, AuditSource.REST_Outgoing, transports, audit_log, 'cid-loop-1', now,
            defaults=defaults)

        # Two facts - the failing REST connection and the slow database - and seven
        # matches between them: four seeded rules and the three webhook-riding ones
        assert result.fact_count == 2
        assert result.finding_count == 7
        assert result.raised_count == 7
        assert result.deduplicated_count == 0

        assert sorted(result.dispatched) == [
            ('Connection_Down', AlertAction.Email_Digest),
            ('Error_Rate', AlertAction.Email_Digest),
            ('Error_Rate_Diagnose', AlertAction.Invoke_Service),
            ('Slack_On_Errors', AlertAction.Slack),
            ('Slow_Queries', AlertAction.Email_Digest),
            ('Teams_On_Errors', AlertAction.Teams),
            ('Webhook_On_Errors', AlertAction.Webhook),
        ]

        # What every message about the REST connection says
        rest_measures = 'error rate 100% (12 of 12 over 300s), 3 consecutive failures'

        # Where every message about the REST connection points - the audit log page
        # filtered down to the connection. Its failures are response events, a type
        # no source declares resubmittable, so no event is deep-linked.
        rest_link = f'/zato/audit-log/?source=rest-outgoing&object_name={quote(_rest_conn_name)}&cluster=1'

        # Slack received exactly one message - the rendered slack template,
        # sent to the channel the rule names
        assert len(recorder.slack_messages) == 1

        slack_channel, slack_text = recorder.slack_messages[0]
        assert slack_channel == _slack_channel
        assert slack_text == (
            f'Rule `Slack_On_Errors` matched `{_rest_conn_name}` (REST outgoing) - {rest_measures}\n{rest_link}')

        # Teams received exactly one message - the rendered teams template as HTML,
        # sent to the team and channel the rule names
        assert len(recorder.teams_messages) == 1

        teams_to, teams_html = recorder.teams_messages[0]
        teams_message = f'Rule `Teams_On_Errors` matched `{_rest_conn_name}` (REST outgoing) - {rest_measures}'

        assert teams_to == _teams_to
        assert teams_html == f'{teams_message}<br/><br/>{rest_link}'

        # The plain webhook received the whole structured payload,
        # rendered by the webhook template
        assert len(webhook_server.received) == 1

        webhook_delivery = webhook_server.received[0]
        assert webhook_delivery['path'] == '/hooks/zato'

        webhook_payload = webhook_delivery['payload']
        webhook_message = f'Rule `Webhook_On_Errors` matched `{_rest_conn_name}` (REST outgoing) - {rest_measures}'

        alert_id = webhook_payload.pop('alert_id')
        assert isinstance(alert_id, int)

        assert webhook_payload == {
            'rule': 'Webhook_On_Errors',
            'kind': 'Webhook_On_Errors',
            'source': AuditSource.REST_Outgoing,
            'object_name': _rest_conn_name,
            'message': webhook_message,
            'link': rest_link,
            'severity': 'warning',
            'count': 1,
            'action_config': {},
        }

        # Email received three messages - the connection-down and error-rate alerts
        # about the REST connection and the slow-query one about the database -
        # each to the default addresses, each subject the alert's own message
        assert len(smtp_receiver.messages) == 3

        subjects = sorted(message.subject for message in smtp_receiver.messages)

        assert subjects == [
            f'Rule `Connection_Down` matched `{_rest_conn_name}` (REST outgoing) - {rest_measures}',
            f'Rule `Error_Rate` matched `{_rest_conn_name}` (REST outgoing) - {rest_measures}',
            f'Rule `Slow_Queries` matched `{_sql_conn_name}` (SQL) - error rate 0% (0 of 3 over 300s), average duration 8000ms',
        ]

        for message in smtp_receiver.messages:
            assert message.sender == _email_from
            assert message.recipients == _addresses

        # The diagnose outcome went to the diagnosis service with its payload whole
        assert len(recorder.invocations) == 1

        service_name, payload = recorder.invocations[0]
        assert service_name == 'zato.alerting.diagnose'
        assert payload['object_name'] == _rest_conn_name
        assert payload['severity'] == 'critical'

        # And every occurrence landed in the audit trail as an alert-raised event
        raised = _get_raised_events()
        assert len(raised) == 7

        raised_objects = {event['object_name'] for event in raised}
        assert raised_objects == {_rest_conn_name, _sql_conn_name}

# ################################################################################################################################

    def test_a_second_sweep_in_the_window_delivers_only_the_critical_findings(
        self,
        backend:'RuleSQLBackend',
        webhook_server:'any_',
        smtp_receiver:'any_',
        ) -> 'None':

        _seed_events()

        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        recorder = _ServiceRecorder()
        transports = build_transports(smtp_receiver.port, recorder)
        defaults = _build_defaults(webhook_server)

        rules = load_alert_rules(backend)

        # The first sweep raises and delivers everything ..
        result = run_sweep(engine, rules, {}, AuditSource.REST_Outgoing, transports, audit_log, 'cid-window-1', now,
            defaults=defaults)

        assert result.raised_count == 7

        # .. and the second one, still inside the dedup window, deduplicates every
        # finding and delivers only the critical ones - those are never suppressed.
        result_2 = run_sweep(engine, rules, {}, AuditSource.REST_Outgoing, transports, audit_log, 'cid-window-2', now,
            defaults=defaults)

        assert result_2.raised_count == 0
        assert result_2.deduplicated_count == 7

        assert sorted(result_2.dispatched) == [
            ('Connection_Down', AlertAction.Email_Digest),
            ('Error_Rate_Diagnose', AlertAction.Invoke_Service),
            ('Teams_On_Errors', AlertAction.Teams),
        ]

        # The warning channels heard nothing new ..
        assert len(recorder.slack_messages) == 1
        assert len(webhook_server.received) == 1

        # .. while the critical ones delivered again - Teams, the connection-down
        # email and the diagnosis service.
        assert len(recorder.teams_messages) == 2
        assert len(recorder.invocations) == 2
        assert len(smtp_receiver.messages) == 4

        # A repetition speaks with its count
        assert recorder.teams_messages[1][1].startswith('[2x] Rule `Teams_On_Errors`')

        # Every occurrence landed in the audit trail, deduplicated or not
        raised = _get_raised_events()
        assert len(raised) == 14

# ################################################################################################################################

    def test_an_unmatched_finding_reaches_the_default_sink_digest(
        self,
        smtp_receiver:'any_',
        ) -> 'None':

        audit_log = AuditLog(_server_name)
        now = utcnow()

        recorder = _ServiceRecorder()
        transports = build_transports(smtp_receiver.port, recorder)

        defaults = AlertDefaults()
        defaults.email_to = _addresses

        # A finding of a kind no rule knows about - e.g. a rule was deleted
        # between the match and the dispatch
        rule = new_rule('Some_Other_Rule', 'Some_Other_Rule', action=AlertAction.Slack)
        finding = new_finding('Nobody_Matches_This', AuditSource.REST_Outgoing, _rest_conn_name,
            'a finding no rule matches', link='/zato/audit-log/')

        result = process_findings([rule], [finding], transports, audit_log, 'cid-sink-1', now,
            defaults=defaults, dashboard_url='https://dashboard.example.com')

        # Nothing was raised or dispatched - the finding went to the default sink ..
        assert result.raised_count == 0
        assert result.dispatched == []
        assert len(result.unmatched) == 1

        # .. which emailed it as the catch-all digest, the dashboard link included.
        assert len(smtp_receiver.messages) == 1

        digest = smtp_receiver.messages[0]
        assert digest.recipients == _addresses
        assert digest.subject == 'Zato alert digest - 1 finding'
        assert 'a finding no rule matches' in digest.body
        assert 'https://dashboard.example.com/zato/audit-log/' in digest.body

# ################################################################################################################################

    def test_a_missed_arrival_reaches_email_through_the_seeded_rule(
        self,
        backend:'RuleSQLBackend',
        smtp_receiver:'any_',
        ) -> 'None':

        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        recorder = _ServiceRecorder()
        transports = build_transports(smtp_receiver.port, recorder)

        defaults = AlertDefaults()
        defaults.email_to = _addresses

        schedule_name = 'Daily results'

        # The schedule's newest arrival, ten minutes back on a five-minute window
        event_id = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Delivered, 'sftp.backups',
            cid='loop-arrival-1', outcome=AuditOutcome.OK, attrs={'schedule': schedule_name})

        statement = update(event_table)
        statement = statement.where(event_table.c.id == event_id)
        statement = statement.values(event_time_iso=(now - timedelta(seconds=600)).isoformat())

        with engine.begin() as connection:
            _ = connection.execute(statement)

        rules = load_alert_rules(backend)

        result = run_sweep(engine, rules, {}, AuditSource.REST_Outgoing, transports, audit_log, 'cid-arrival-1', now,
            defaults=defaults, arrival_windows={schedule_name: 300})

        # The seeded arrival rule fired and nothing else did
        assert result.dispatched == [('Arrival_Overdue', AlertAction.Email_Digest)]

        assert len(smtp_receiver.messages) == 1

        message = smtp_receiver.messages[0]
        assert message.recipients == _addresses
        assert 'Arrival_Overdue' in message.subject
        assert schedule_name in message.subject
        assert 'no file for 600s' in message.subject

# ################################################################################################################################
# ################################################################################################################################
