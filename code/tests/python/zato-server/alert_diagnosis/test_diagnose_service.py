# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The diagnosed alert path end to end - a rule outcome saying diagnose invokes the
# diagnosis service, which collects evidence from the audit log, has the LLM diagnose
# it over real HTTP against a threaded simulator, stores the diagnosis next to the
# alert and notifies through Slack, Microsoft Teams and email, each one a real
# simulated server of its own.

# stdlib
import json
import logging
import smtplib
import threading
from email.mime.text import MIMEText
from http.client import OK
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from shutil import copytree
from types import SimpleNamespace

# pytest
import pytest

# requests
import requests

# SQLAlchemy
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

# urllib3
import urllib3

# Zato
from zato.common.alerting.rendering import get_default_template_dir, Template_Dir_Name
from zato.common.api import Incidents, SMTPMessage
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.crypto.api import CryptoManager
from zato.common.incidents.skill import load_skill
from zato.common.incidents.store import IncidentStore
from zato.common.odb.model import Base, GenericObject
from zato.server.service.internal.incidents import Diagnose

# Test helpers
from chat_simulators import find_free_port, SlackTestHandler, start_slack_server
from hl7_client.smtp_receiver import SMTPReceiver
from teams_simulator import start_teams_server, TeamsGraphTestHandler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_, anydict, stranydict
    any_ = any_
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

# The Teams simulator serves TLS with a self-signed certificate, so its warnings say nothing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# The cluster and server the tests run under
_cluster_id = 1
_server_name = 'test-diagnosis-server'

# The correlation id the diagnosis runs under
_cid = 'cid-diagnosis-1'

# The connection the alerts are about
_conn_name = 'CRM API'

# The alert the payloads carry
_alert_id = 1234
_rule_name = 'alerts_rest_Error_Rate_Diagnose'
_alert_message = 'error rate 100% (12 of 12 over 300s) on `CRM API`'
_alert_link = '/zato/audit-log/?object=CRM+API'

# What the simulated LLM answers with
_diagnosis_text = 'The remote server replied with HTTP 503 for every call.'
_llm_reply = json.dumps({
    'diagnosis': _diagnosis_text,
    'confidence': 'high',
    'remediation': {'action': 'resubmit'},
})

# What the error events the evidence pack collects carry
_error_data = 'HTTP 503 Service Unavailable'

# The Slack workspace's details
_slack_channel = 'alerts'
_slack_token = 'xoxb-test-' + CryptoManager.generate_hex_string()

# The Teams tenant's details
_teams_tenant_id = 'tenant-' + CryptoManager.generate_hex_string()
_teams_client_id = 'client-' + CryptoManager.generate_hex_string()
_teams_client_secret = 'secret-' + CryptoManager.generate_hex_string()
_teams_team_id = 'team-001'
_teams_channel_id = 'channel-001'

# The email addressing the rules configure
_email_to = 'ops@example.com, oncall@example.com'
_email_from = 'zato@example.com'

# Where the notification links point to
_dashboard_url = 'https://dashboard.example.com'

# ################################################################################################################################
# ################################################################################################################################

class LLMTestHandler(BaseHTTPRequestHandler):
    """ A local LLM HTTP API - one POST endpoint answering every prompt with the configured reply.
    """

    # What every completion answers with
    reply:'str' = ''

    # Every prompt received so far
    prompts:'list' = []

    def log_message(self, format:'str', *args:'any_') -> 'None':
        pass

    def do_POST(self) -> 'None':

        content_length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(content_length))

        LLMTestHandler.prompts.append(body['prompt'])

        data = json.dumps({'text': self.reply}).encode('utf-8')

        self.send_response(OK)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        _ = self.wfile.write(data)

# ################################################################################################################################

def start_llm_server(port:'int', reply:'str') -> 'ThreadingHTTPServer':
    """ Starts the simulated LLM API in a background thread, over plain HTTP.
    """
    LLMTestHandler.reply = reply
    LLMTestHandler.prompts = []

    out = ThreadingHTTPServer(('127.0.0.1', port), LLMTestHandler)

    thread = threading.Thread(target=out.serve_forever, daemon=True)
    thread.start()

    return out

# ################################################################################################################################
# ################################################################################################################################

class _LLMClient:
    """ What self.llm[name] hands back - its invoke speaks real HTTP to the simulator.
    """
    def __init__(self, address:'str') -> 'None':
        self.address = address

    def invoke(self, prompt:'str') -> 'stranydict':
        response = requests.post(self.address, json={'prompt': prompt})
        out = response.json()
        return out

# ################################################################################################################################

class _LLMFacade:
    """ A self.llm stand-in - the same conn_dict shape and lookup the real facade keeps,
    remembering which connection each diagnosis went through.
    """
    def __init__(self, conn_dict:'anydict', address:'str') -> 'None':
        self.conn_dict = conn_dict
        self.address = address
        self.invoked_names:'list' = []

    def __getitem__(self, name:'str') -> '_LLMClient':
        self.invoked_names.append(name)
        out = _LLMClient(self.address)
        return out

# ################################################################################################################################

class _SlackFacade:
    """ A self.slack stand-in whose send posts to the simulated workspace
    the way the real Slack client does - the Web API over HTTP.
    """
    def __init__(self, conn_dict:'anydict', address:'str', token:'str') -> 'None':
        self.conn_dict = conn_dict
        self.address = address
        self.token = token

    def send(self, name:'str', channel:'str', text:'str') -> 'stranydict':
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(self.address + '/chat.postMessage', json={'channel': channel, 'text': text}, headers=headers)

        out = response.json()
        assert out['ok'] is True, out

        return out

# ################################################################################################################################

class _TeamsFacade:
    """ A self.microsoft.teams stand-in whose send speaks to the simulated Graph
    the way the real client does - a client-credentials token first,
    then the channel messages endpoint.
    """
    def __init__(self, conn_dict:'anydict', address:'str') -> 'None':
        self.conn_dict = conn_dict
        self.address = address

    def send(self, name:'str', to:'str', html:'str') -> 'stranydict':

        token_url = f'{self.address}/{_teams_tenant_id}/oauth2/v2.0/token'
        credentials = {
            'client_id': _teams_client_id,
            'client_secret': _teams_client_secret,
            'grant_type': 'client_credentials',
        }
        response = requests.post(token_url, data=credentials, verify=False)
        token = response.json()['access_token']

        messages_url = f'{self.address}/v1.0/teams/{_teams_team_id}/channels/{_teams_channel_id}/messages'
        payload = {'body': {'contentType': 'html', 'content': html}}
        headers = {'Authorization': f'Bearer {token}'}

        response = requests.post(messages_url, json=payload, headers=headers, verify=False)

        out = response.json()
        return out

# ################################################################################################################################

class _SMTPConnection:
    """ What smtp_item.conn hands back - its send delivers to the aiosmtpd receiver over real SMTP.
    """
    def __init__(self, port:'int') -> 'None':
        self.port = port

    def send(self, message:'SMTPMessage') -> 'None':

        mime = MIMEText(message.body)
        mime['Subject'] = message.subject
        mime['From'] = message.from_
        mime['To'] = ', '.join(message.to)

        client = smtplib.SMTP('127.0.0.1', self.port)
        _ = client.sendmail(message.from_, message.to, mime.as_string())
        _ = client.quit()

# ################################################################################################################################

class _SMTPStore:
    """ What self.email.smtp answers a get with - one connection definition.
    """
    def __init__(self, item:'any_') -> 'None':
        self.item = item

    def get(self, name:'str', needs_connect:'bool') -> 'any_':
        out = self.item
        return out

# ################################################################################################################################

class _EmailAPI:
    """ A self.email stand-in - just the SMTP store the notification path reads.
    """
    def __init__(self, port:'int') -> 'None':
        item = SimpleNamespace(config={'is_active': True}, conn=_SMTPConnection(port))
        self.smtp = _SMTPStore(item)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def llm_address() -> 'any_':
    """ A running simulated LLM API answering every prompt with the canned diagnosis.
    """
    port = find_free_port()
    server = start_llm_server(port, _llm_reply)

    yield f'http://127.0.0.1:{port}'

    server.shutdown()

# ################################################################################################################################

@pytest.fixture()
def slack_address() -> 'any_':
    """ A running simulated Slack workspace.
    """
    port = find_free_port()
    server = start_slack_server(port, _slack_token, [_slack_channel])

    yield f'http://127.0.0.1:{port}'

    server.shutdown()

# ################################################################################################################################

@pytest.fixture()
def teams_address() -> 'any_':
    """ A running simulated Microsoft Graph.
    """
    port = find_free_port()
    teams = [
        {
            'id': _teams_team_id,
            'displayName': 'Operations',
            'channels': [
                {'id': _teams_channel_id, 'displayName': 'Alerts'},
            ],
        },
    ]
    server = start_teams_server(port, _teams_tenant_id, _teams_client_id, _teams_client_secret, teams)

    yield f'https://127.0.0.1:{port}'

    server.shutdown()

# ################################################################################################################################

@pytest.fixture()
def smtp_receiver() -> 'any_':
    """ A running aiosmtpd receiver recording every email delivered to it.
    """
    receiver = SMTPReceiver()
    receiver.start()

    yield receiver

    receiver.stop()

# ################################################################################################################################

@pytest.fixture()
def repo_dir(tmp_path:'Path') -> 'str':
    """ A server repo directory with the alert templates copied in,
    the way create_server.py copies them.
    """
    repo = tmp_path / 'repo'
    repo.mkdir()

    _ = copytree(get_default_template_dir(), str(repo / Template_Dir_Name))

    out = str(repo)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _new_session() -> 'any_':
    """ A sessionmaker over a fresh in-memory database with just the generic_object table.
    """
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine, tables=[GenericObject.__table__])

    out = sessionmaker(bind=engine)
    return out

# ################################################################################################################################

def _new_payload(action_config:'anydict', source:'str'=AuditSource.REST_Outgoing) -> 'stranydict':
    """ The payload the alerting engine's invoke-service transport carries
    when a diagnose outcome fires.
    """
    out = {
        'alert_id': _alert_id,
        'rule': _rule_name,
        'kind': 'Error_Rate_Diagnose',
        'source': source,
        'object_name': _conn_name,
        'message': _alert_message,
        'link': _alert_link,
        'severity': 'critical',
        'count': 3,
        'action_config': action_config,
    }

    return out

# ################################################################################################################################

def _seed_error_events(source:'str'=AuditSource.REST_Outgoing) -> 'None':
    """ Enough failed calls in the audit log for the evidence pack to have something to say.
    """
    audit_log = AuditLog(_server_name)

    for index in range(3):
        _ = audit_log.insert(source, AuditEvent.Response_Received, _conn_name,
            cid=f'call-{index}', outcome=AuditOutcome.Error, data=_error_data)

# ################################################################################################################################

def _new_service(
    payload:'stranydict',
    session:'any_',
    repo_dir:'str',
    llm:'_LLMFacade',
    slack:'_SlackFacade | None' = None,
    teams:'_TeamsFacade | None' = None,
    email:'_EmailAPI | None' = None,
    ) -> 'any_':
    """ The diagnosis service with its collaborators in place - the connectors it
    speaks through are the simulator-backed stand-ins the test hands it.
    """
    rest_config = {
        'name': _conn_name,
        'is_active': True,
        'address_host': 'https://crm.example.com',
        'address_url_path': '/api/v1',
        'timeout': 10,
    }

    if slack is None:
        slack = _SlackFacade({}, '', '')

    if teams is None:
        teams = _TeamsFacade({}, '')

    # The service is built without __init__ and typed as any_ so the test doubles
    # can stand where the runtime collaborators would
    service:'any_' = Diagnose.__new__(Diagnose)

    service.cid = _cid
    service.logger = logging.getLogger('test-alert-diagnosis')
    service.request = SimpleNamespace(payload=payload)
    service.odb = SimpleNamespace(session=session)
    service.server = SimpleNamespace(cluster_id=_cluster_id, name=_server_name, repo_location=repo_dir)
    service.out = SimpleNamespace(rest={_conn_name: SimpleNamespace(config=rest_config)})
    service.llm = llm
    service.slack = slack
    service.microsoft = SimpleNamespace(teams=teams)
    service.email = email

    return service

# ################################################################################################################################

def _get_diagnosed_events() -> 'list':
    """ Every alert-diagnosed event the audit log holds.
    """
    engine = get_audit_engine()

    query = select(event_table).where(event_table.c.event_type == AuditEvent.Alert_Diagnosed)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDiagnosePath:

    def test_a_rule_named_connection_diagnoses_and_every_channel_hears_about_it(
        self,
        llm_address:'any_',
        slack_address:'any_',
        teams_address:'any_',
        smtp_receiver:'any_',
        repo_dir:'str',
        ) -> 'None':

        _seed_error_events()

        # The rule names its own LLM connection and every notification target
        action_config = {
            'llm_connection': 'CRM Diagnostics LLM',
            'slack_channel': _slack_channel,
            'teams_to': 'Alerts',
            'email_to': _email_to,
            'email_from': _email_from,
            'dashboard_url': _dashboard_url,
        }

        conn_name = Incidents.Notification_Conn_Name
        active = {conn_name: {'is_active': True}}

        session = _new_session()

        service = _new_service(
            _new_payload(action_config),
            session,
            repo_dir,
            llm=_LLMFacade({}, llm_address),
            slack=_SlackFacade(active, slack_address, _slack_token),
            teams=_TeamsFacade(active, teams_address),
            email=_EmailAPI(smtp_receiver.port),
        )

        service.handle()

        # The diagnosis went through the connection the rule named ..
        assert service.llm.invoked_names == ['CRM Diagnostics LLM']

        # .. with the evidence pack in the prompt - the errors' own text included ..
        assert len(LLMTestHandler.prompts) == 1
        assert _error_data in LLMTestHandler.prompts[0]
        assert '# Evidence' in LLMTestHandler.prompts[0]

        # .. the diagnosis is stored next to the alert ..
        store = IncidentStore(session, _cluster_id)
        diagnosis = store.get(f'alert.{_alert_id}')

        assert diagnosis is not None
        assert diagnosis['alert_id'] == _alert_id
        assert diagnosis['diagnosis'] == _diagnosis_text
        assert diagnosis['confidence'] == 'high'
        assert diagnosis['remediation'] == {'action': 'resubmit'}
        assert diagnosis['is_parsed'] is True

        # .. the audit log says the alert was diagnosed ..
        events = _get_diagnosed_events()
        assert len(events) == 1
        assert events[0]['object_name'] == _conn_name
        assert events[0]['data'] == _alert_message

        # .. Slack heard about it, diagnosis and dashboard link included ..
        assert len(SlackTestHandler.messages) == 1

        slack_message = SlackTestHandler.messages[0]
        assert slack_message['channel'] == _slack_channel
        assert _alert_message in slack_message['text']
        assert _diagnosis_text in slack_message['text']
        assert _dashboard_url + _alert_link in slack_message['text']

        # .. so did Teams, as HTML ..
        assert len(TeamsGraphTestHandler.messages) == 1

        teams_content = TeamsGraphTestHandler.messages[0]['payload']['body']['content']
        assert _diagnosis_text in teams_content
        assert '<br/>' in teams_content

        # .. and so did email, one message to both addresses.
        assert len(smtp_receiver.messages) == 1

        received = smtp_receiver.messages[0]
        assert received.sender == _email_from
        assert received.recipients == ['ops@example.com', 'oncall@example.com']
        assert received.subject == _alert_message
        assert _diagnosis_text in received.body
        assert _dashboard_url + _alert_link in received.body

# ################################################################################################################################

    def test_the_default_connection_answers_when_the_rule_names_none(
        self,
        llm_address:'any_',
        slack_address:'any_',
        repo_dir:'str',
        ) -> 'None':

        _seed_error_events()

        # The rule names no LLM connection of its own, only where Slack delivers
        action_config = {
            'slack_channel': _slack_channel,
        }

        conn_name = Incidents.Notification_Conn_Name

        # The default LLM connection exists and a person already activated it
        llm_connections = {Incidents.LLM_Connection_Name: {'is_active': True}}

        session = _new_session()

        service = _new_service(
            _new_payload(action_config),
            session,
            repo_dir,
            llm=_LLMFacade(llm_connections, llm_address),
            slack=_SlackFacade({conn_name: {'is_active': True}}, slack_address, _slack_token),
        )

        service.handle()

        # The diagnosis went through the default connection ..
        assert service.llm.invoked_names == [Incidents.LLM_Connection_Name]

        # .. and it reads back parsed in full.
        store = IncidentStore(session, _cluster_id)
        diagnosis = store.get(f'alert.{_alert_id}')

        assert diagnosis is not None
        assert diagnosis['diagnosis'] == _diagnosis_text
        assert diagnosis['is_parsed'] is True

# ################################################################################################################################

    def test_an_inactive_default_stores_the_alert_undiagnosed(
        self,
        llm_address:'any_',
        slack_address:'any_',
        repo_dir:'str',
        ) -> 'None':

        _seed_error_events()

        action_config = {
            'slack_channel': _slack_channel,
        }

        conn_name = Incidents.Notification_Conn_Name

        # The default LLM connection is there but still inactive, the way it ships
        llm_connections = {Incidents.LLM_Connection_Name: {'is_active': False}}

        session = _new_session()

        service = _new_service(
            _new_payload(action_config),
            session,
            repo_dir,
            llm=_LLMFacade(llm_connections, llm_address),
            slack=_SlackFacade({conn_name: {'is_active': True}}, slack_address, _slack_token),
        )

        service.handle()

        # No LLM was called ..
        assert service.llm.invoked_names == []
        assert LLMTestHandler.prompts == []

        # .. the alert is stored without a diagnosis ..
        store = IncidentStore(session, _cluster_id)
        diagnosis = store.get(f'alert.{_alert_id}')

        assert diagnosis is not None
        assert diagnosis['diagnosis'] == ''
        assert diagnosis['is_parsed'] is False

        # .. and the notification still went out, just without a diagnosis line.
        assert len(SlackTestHandler.messages) == 1
        assert _alert_message in SlackTestHandler.messages[0]['text']
        assert 'Diagnosis' not in SlackTestHandler.messages[0]['text']

# ################################################################################################################################

    def test_one_alert_produces_one_diagnosis(
        self,
        llm_address:'any_',
        slack_address:'any_',
        repo_dir:'str',
        ) -> 'None':

        _seed_error_events()

        action_config = {
            'llm_connection': 'CRM Diagnostics LLM',
            'slack_channel': _slack_channel,
        }

        conn_name = Incidents.Notification_Conn_Name

        session = _new_session()

        service = _new_service(
            _new_payload(action_config),
            session,
            repo_dir,
            llm=_LLMFacade({}, llm_address),
            slack=_SlackFacade({conn_name: {'is_active': True}}, slack_address, _slack_token),
        )

        # The same alert arrives twice - e.g. a critical finding is dispatched
        # on every sweep - and only the first one is diagnosed
        service.handle()
        service.handle()

        store = IncidentStore(session, _cluster_id)
        assert len(store.get_list()) == 1

        assert service.llm.invoked_names == ['CRM Diagnostics LLM']
        assert len(SlackTestHandler.messages) == 1

# ################################################################################################################################
# ################################################################################################################################

# The sources that ship a diagnostic skill of their own - each one produces
# a diagnosis instead of being skipped for having no skill.
_diagnosable_sources = (
    AuditSource.SQL_Outgoing,
    AuditSource.LLM,
    AuditSource.MCP,
    AuditSource.Microsoft_Cloud,
    AuditSource.Email_SMTP,
    AuditSource.Email_IMAP,
    AuditSource.Odoo,
    AuditSource.File_Outgoing,
    AuditSource.Scheduler,
)

# ################################################################################################################################
# ################################################################################################################################

class TestDiagnosePerSource:

    @pytest.mark.parametrize('source', _diagnosable_sources)
    def test_a_non_rest_source_produces_a_diagnosis(
        self,
        source:'str',
        llm_address:'any_',
        repo_dir:'str',
        ) -> 'None':

        _seed_error_events(source)

        # The rule names its own LLM connection and no notification targets -
        # this test is about the diagnosis itself, not the delivery.
        action_config = {
            'llm_connection': 'Diagnostics LLM',
        }

        session = _new_session()

        # The llm source's own config lookup reads the facade's conn_dict,
        # so the connection under diagnosis is in there too.
        llm_connections = {_conn_name: {'name': _conn_name, 'is_active': True}}

        service = _new_service(
            _new_payload(action_config, source),
            session,
            repo_dir,
            llm=_LLMFacade(llm_connections, llm_address),
        )

        service.handle()

        # The diagnosis went through the connection the rule named ..
        assert service.llm.invoked_names == ['Diagnostics LLM']

        # .. with the source's own skill leading the prompt and the errors' text in the evidence ..
        skill = load_skill(source)
        assert skill is not None

        assert len(LLMTestHandler.prompts) == 1
        assert LLMTestHandler.prompts[0].startswith(skill.instructions)
        assert _error_data in LLMTestHandler.prompts[0]

        # .. the diagnosis is stored next to the alert ..
        store = IncidentStore(session, _cluster_id)
        diagnosis = store.get(f'alert.{_alert_id}')

        assert diagnosis is not None
        assert diagnosis['source'] == source
        assert diagnosis['diagnosis'] == _diagnosis_text
        assert diagnosis['is_parsed'] is True

        # .. and the audit log says the alert was diagnosed.
        events = _get_diagnosed_events()
        assert len(events) == 1
        assert events[0]['source'] == source
        assert events[0]['object_name'] == _conn_name

# ################################################################################################################################
# ################################################################################################################################
