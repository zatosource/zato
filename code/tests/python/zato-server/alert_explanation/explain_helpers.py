# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the explain service tests share - the simulated LLM API, the facade stand-ins for
# Slack, Microsoft Teams and email, the payload the alerting engine hands the service
# and the service itself with its collaborators in place.

# stdlib
import json
import logging
import smtplib
import threading
from email.mime.text import MIMEText
from http.client import OK
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

# requests
import requests

# SQLAlchemy
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

# urllib3
import urllib3

# Zato
from zato.common.alerting.model import Default_Dedup_Window_Seconds
from zato.common.api import SMTPMessage
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.crypto.api import CryptoManager
from zato.common.odb.model import Base, Cluster, GenericConn, GenericObject, HTTPBasicAuth, HTTPSOAP, SecurityBase, Service
from zato.server.service.internal.alerting import Explain

# Test helpers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The Teams simulator serves TLS with a self-signed certificate, so its warnings say nothing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# The cluster and server the tests run under
_cluster_id = 1
_server_name = 'test-explanation-server'

# The correlation id the explanation runs under
_cid = 'cid-explanation-1'

# The connection the alerts are about
_conn_name = 'CRM API'

# The alert the payloads carry - the sweep already made the link absolute
_alert_id = 1234

# The LLM connection the deployment's alerting config names for explanations
_llm_conn_name = 'ops.alerts.llm'
_rule_name = 'Error_Rate'
_alert_message = 'error rate 100% (12 of 12 over 300s) on `CRM API`'
_alert_link = 'https://dashboard.example.com/zato/audit-log/?object=CRM+API'

# What the simulated LLM answers with
_explanation_text = 'The remote server replied with HTTP 503 for every call.'
_llm_reply = json.dumps({
    'explanation': _explanation_text,
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

# The deployment-level email addressing the sweep job's extra carries
_email_to = ['ops@example.com', 'oncall@example.com']
_email_from = 'zato@example.com'

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
    remembering which connection each explanation went through.
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

def _new_session() -> 'any_':
    """ A sessionmaker over a fresh in-memory database with the tables the explain service reads.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        Service.__table__,
        SecurityBase.__table__,
        HTTPBasicAuth.__table__,
        GenericObject.__table__,
        GenericConn.__table__,
        HTTPSOAP.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    out = sessionmaker(bind=engine)

    # A REST channel's row points to its cluster, so the cluster is there for the channel tests
    session = out()
    session.add(Cluster(_cluster_id, 'test-cluster', '', 'sqlite'))
    session.commit()
    session.close()

    return out

# ################################################################################################################################

def _new_payload(
    action:'str',
    action_config:'anydict',
    source:'str'=AuditSource.REST_Outgoing,
    *,
    email_to:'list | None'=None,
    object_name:'str'=_conn_name,
    measures:'list | None'=None,
    ) -> 'stranydict':
    """ The payload the alerting engine hands the explain service - the alert, the fact it was
    raised from, the rule's own action and the deployment-level targets to deliver with.
    """
    if measures is None:
        measures = ['error_rate']

    fact = {
        'source': source,
        'object_name': object_name,
        'error_rate': 1.0,
        'error_count': 12,
        'total_count': 12,
        'window_seconds': 300,
        'window_seconds_by_measure': {'error_rate': 300},
        'consecutive_failures': 3,
    }

    # A rule only ever compares measures the fact has
    for measure in measures:
        if measure not in fact:
            fact[measure] = 1

    out = {
        'alert_id': _alert_id,
        'rule': _rule_name,
        'kind': _rule_name,
        'source': source,
        'object_name': object_name,
        'message': _alert_message,
        'link': _alert_link,
        'severity': 'error',
        'count': 3,
        'action': action,
        'action_config': action_config,
        'dedup_window_seconds': Default_Dedup_Window_Seconds,
        'defaults': {
            'email_to': email_to,
            'email_from': _email_from,
            'webhook_url': '',
            'llm_connection': _llm_conn_name,
        },
        'explanation': '',
        'confidence': '',
        'remediation': None,
        'fact': fact,
        'thresholds': {'error_rate_threshold': 0.5},
        'measures': measures,
    }

    return out

# ################################################################################################################################

def _seed_error_events(source:'str'=AuditSource.REST_Outgoing, object_name:'str'=_conn_name) -> 'None':
    """ Enough failed calls in the audit log for the evidence document to have something to say.
    """
    audit_log = AuditLog(_server_name)

    for index in range(3):
        _ = audit_log.insert(source, AuditEvent.Response_Received, object_name,
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
    """ The explanation service with its collaborators in place - the connectors it
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
    service:'any_' = Explain.__new__(Explain)

    service.cid = _cid
    service.logger = logging.getLogger('test-alert-explanation')
    service.request = SimpleNamespace(payload=payload)
    service.odb = SimpleNamespace(session=session)
    service.server = SimpleNamespace(cluster_id=_cluster_id, name=_server_name, repo_location=repo_dir,
        invoke=None, pubsub_backend=None)
    service.out = SimpleNamespace(rest={_conn_name: SimpleNamespace(config=rest_config)})
    service.llm = llm
    service.slack = slack
    service.microsoft = SimpleNamespace(teams=teams)
    service.email = email

    return service

# ################################################################################################################################

def _get_explained_events() -> 'list':
    """ Every alert-explained event the audit log holds.
    """
    engine = get_audit_engine()

    query = select(event_table).where(event_table.c.event_type == AuditEvent.Alert_Explained)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    return out

# ################################################################################################################################
# ################################################################################################################################

