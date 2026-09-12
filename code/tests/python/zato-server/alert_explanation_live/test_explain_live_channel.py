# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explain service end to end for a REST channel and for a SOAP channel - a real quickstart server
# with a hot-deployed service that raises, a channel of each transport in front of it with the audit log on,
# real HTTP calls that the channel rejects and that the service fails on, one real sweep inside the server,
# and the explained alerts read off the server's own databases and received by a real SMTP receiver.
# Both proofs share every step, each describing its channel to the steps through one object.

# stdlib
import os
from dataclasses import dataclass

# requests
import requests

# SQLAlchemy
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.alerting.explain.evidence import Heading_Object
from zato.common.alerting.explain.store import ExplanationStore
from zato.common.alerting.names import get_notification_conn_name
from zato.common.api import Alerting, EMAIL
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table
from zato.common.defaults import default_cluster_id
from zato.common.test.client import AdminClient

# Test helpers
from live_config import LiveServer
from live_trace import Channel_Channel, Channel_Explain, Channel_SMTP, Received, Sent, separator, trace
from test_explain_live import _assert_sound_explanation, _email_from, _email_to, _trace_delivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class _ChannelDescription:
    """ One channel the proof runs against - what it is called, where it answers, how it is created,
    what a call to it looks like on the wire, under which audit source it logs and what its failures say.
    """
    label:'str'
    name:'str'
    url_path:'str'
    source:'str'
    create_args:'stranydict'
    headers:'strstrdict'
    body:'any_'
    fault_text:'str'

# ################################################################################################################################
# ################################################################################################################################

class TestExplainLiveChannel:

    def test_rest_channel_failures_are_explained(
        self,
        ollama:'any_',
        zato_server:'any_',
        smtp_receiver:'any_',
        ) -> 'None':

        _run_channel_proof(_rest_channel, smtp_receiver)

# ################################################################################################################################

    def test_soap_channel_failures_are_explained(
        self,
        ollama:'any_',
        zato_server:'any_',
        smtp_receiver:'any_',
        ) -> 'None':

        _run_channel_proof(_soap_channel, smtp_receiver)

# ################################################################################################################################
# ################################################################################################################################

def _run_channel_proof(channel:'_ChannelDescription', smtp_receiver:'any_') -> 'None':
    """ The whole proof for one channel - it is created, called, swept, and its explanations are read and checked.
    """
    client = _new_admin_client()

    # The server's own notification connection delivers to the receiver ..
    _point_smtp_at_receiver(client, smtp_receiver)

    # .. the callers of the channel authenticate with this definition ..
    security_id = _ensure_basic_auth(client)

    # .. the channel itself, with the audit log on and thresholds of its own ..
    channel_id = _create_channel(client, channel, security_id)

    # .. and the sweep explains through the LLM connection and mails from the address below.
    notification_config = _new_notification_config()

    # Real calls over HTTP - rejected ones first, then ones the service behind the channel fails on
    _produce_channel_failures(channel)

    # One real sweep inside the server - the collectors, the rules, the explain service and the delivery
    trace(Channel_Channel, Sent, f'{channel.label}: invoke {Alerting.Service} with {notification_config}')
    _ = client.invoke(Alerting.Service, notification_config)

    # The failing calls are on record under the channel ..
    responses = _get_channel_responses(channel)

    assert len(responses) == _channel_call_count * 2

    statuses = set()
    for row in responses:
        statuses.add(row['status'].split(' ')[0])

    assert statuses == {_status_unauthorized, _status_server_error}

    # .. the rules about the rejected callers and the failing calls both fired and were explained ..
    explanations = _get_stored_explanations(channel)
    rules = set()

    for explanation in explanations:
        assert explanation['object_name'] == channel.name
        assert explanation['source'] == channel.source
        rules.add(explanation['rule'])

    assert _rule_channel_failing in rules
    assert _rule_auth_failures in rules

    # .. each explanation came from the channel's evidence, in the shape the skill asks for ..
    by_rule = {}
    for explanation in explanations:
        by_rule[explanation['rule']] = explanation

    failing = by_rule[_rule_channel_failing]
    assert Heading_Object in failing['evidence']
    assert f'Transport: {channel.label}' in failing['evidence']
    assert f'URL path: {channel.url_path}' in failing['evidence']
    assert f'Service: {LiveServer.raising_service}' in failing['evidence']
    assert f'Security: {_security_name} (Basic Auth)' in failing['evidence']
    assert channel.fault_text in failing['evidence']

    for line in _object_lines_by_label[channel.label]:
        assert line in failing['evidence']

    _assert_sound_explanation(failing, _channel_failing_words)

    rejected = by_rule[_rule_auth_failures]
    assert _status_unauthorized in rejected['evidence']
    _assert_sound_explanation(rejected, _channel_auth_words)

    # .. a channel's explanation never proposes a remediation ..
    for explanation in explanations:
        assert explanation['remediation'] is None

    # .. and every explained alert reached the mailbox.
    _trace_delivery(smtp_receiver)

    bodies = []
    for received in smtp_receiver.messages:
        assert received.recipients == _email_to
        bodies.append(received.body)

    for explanation in explanations:
        for body in bodies:
            if explanation['explanation'] in body:
                break
        else:
            raise AssertionError(f'Expected an email carrying {explanation["explanation"]!r}')

    _ = client.delete('zato.http-soap.delete', id=channel_id)

# ################################################################################################################################
# ################################################################################################################################

# Who calls the channels the live server proof creates
_security_name = 'explain.live.partner'
_security_username = 'partner'
_security_password = 'partner-live-secret-1'
_security_wrong_password = 'not-' + _security_password

# How many calls of each kind the proof makes - rejected ones and ones the service fails on
_channel_call_count = 5

# The status codes the channel answers the two kinds of calls with
_status_unauthorized = '401'
_status_server_error = '500'

# The rules the proof expects to fire for the channel
_rule_channel_failing = 'Channel_Failing'
_rule_auth_failures = 'Auth_Failures'

# The words a sound explanation of each failure is expected to use at least one of
_channel_failing_words = ['backend', 'not reachable', 'exception', 'raise', 'service', '500', 'error', 'fault']
_channel_auth_words = ['auth', 'credential', 'password', '401', 'unauthori', 'reject']

# How long one HTTP call of the proof may take, in seconds
_channel_call_timeout = 30

# What the SOAP channel answers to and speaks, and what its callers send
_soap_action = 'urn:explain-live:orders'
_soap_version = '1.1'
_soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <orders xmlns="{_soap_action}">
      <order_id>ORD-1</order_id>
    </orders>
  </soapenv:Body>
</soapenv:Envelope>
"""

# What a SOAP fault the server builds for a service that raised says - a traceback never reaches the caller
_soap_fault_string = 'An error has occurred'

# The lines of the Object section that only a channel of the given transport carries
_object_lines_by_label = {
    'REST': [],
    'SOAP': [f'SOAP action: {_soap_action}', f'SOAP version: {_soap_version}'],
}

# ################################################################################################################################

_rest_channel = _ChannelDescription(
    label='REST',
    name='explain.live.orders',
    url_path='/explain-live/orders',
    source=AuditSource.REST_Channel,
    create_args={
        'transport': 'plain_http',
        'data_format': 'json',
    },
    headers={},
    body={'order_id': 'ORD-1'},
    fault_text=LiveServer.error_text,
)

_soap_channel = _ChannelDescription(
    label='SOAP',
    name='explain.live.orders.soap',
    url_path='/explain-live/orders/soap',
    source=AuditSource.SOAP_Channel,
    create_args={
        'transport': 'soap',
        'data_format': 'xml',
        'soap_action': _soap_action,
        'soap_version': _soap_version,
    },
    headers={
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': f'"{_soap_action}"',
    },
    body=_soap_body,
    fault_text=_soap_fault_string,
)

# ################################################################################################################################
# ################################################################################################################################

def _new_admin_client() -> 'AdminClient':
    """ The client the proof drives the live server's admin services through.
    """
    base_url = f'http://{LiveServer.host}:{LiveServer.server_port}'
    out = AdminClient(base_url, LiveServer.invoke_password)
    return out

# ################################################################################################################################

def _unwrap(response:'anydict') -> 'any_':
    """ Some services wrap their response in a single zato_* root element.
    """
    out = response

    if len(response) == 1:
        key = next(iter(response))
        if key.startswith('zato_'):
            out = response[key]

    return out

# ################################################################################################################################

def _find_by_name(client:'AdminClient', service_name:'str', name:'str') -> 'anydict | None':
    """ One object of a get-list service by its name, or None when the server has none of that name.
    A list service answers with the list itself, unwrapped.
    """
    items, _ = client.get_list(service_name, cluster_id=default_cluster_id)

    for item in items:
        if item['name'] == name:
            return item

    return None

# ################################################################################################################################

def _point_smtp_at_receiver(client:'AdminClient', smtp_receiver:'any_') -> 'None':
    """ The SMTP connection the alerts leave through - the one under the default notification name,
    active and pointed at the receiver. A fresh quickstart has none, so the first proof creates it
    and the next one, with a receiver of its own, points the same connection at that one.
    """
    conn_name = get_notification_conn_name()

    args = {
        'cluster_id': default_cluster_id,
        'name': conn_name,
        'is_active': True,
        'host': '127.0.0.1',
        'port': smtp_receiver.port,
        'timeout': 10,
        'is_debug': False,
        'username': '',
        'mode': EMAIL.SMTP.MODE.PLAIN,
        'ping_address': '',
    }

    existing = _find_by_name(client, 'zato.email.smtp.get-list', conn_name)

    if existing is None:
        _ = client.create('zato.email.smtp.create', **args)
    else:
        _ = client.edit('zato.email.smtp.edit', id=existing['id'], **args)

    trace(Channel_SMTP, Sent, f'connection `{conn_name}` now delivers to 127.0.0.1:{smtp_receiver.port}')
    separator(Channel_SMTP)

# ################################################################################################################################

def _ensure_basic_auth(client:'AdminClient') -> 'int':
    """ The Basic Auth definition the channels' callers authenticate with - created by the first proof,
    found by the next one.
    """
    existing = _find_by_name(client, 'zato.security.basic-auth.get-list', _security_name)

    if existing is not None:
        return existing['id']

    response = _unwrap(client.create('zato.security.basic-auth.create',
        cluster_id=default_cluster_id,
        name=_security_name,
        is_active=True,
        username=_security_username,
        realm='Zato',
    ))
    out = response['id']

    _ = client.invoke('zato.security.basic-auth.change-password', {'id': out, 'password': _security_password})

    return out

# ################################################################################################################################

def _create_channel(client:'AdminClient', channel:'_ChannelDescription', security_id:'int') -> 'int':
    """ The channel in front of the service that raises - the audit log on, the LLM explaining
    its alerts and a threshold of its own for the rejected callers, so five of them are enough.
    """
    response = _unwrap(client.create('zato.http-soap.create',
        cluster_id=default_cluster_id,
        name=channel.name,
        is_active=True,
        is_internal=False,
        connection='channel',
        url_path=channel.url_path,
        service=LiveServer.raising_service,
        security_id=security_id,
        is_audit_log_active=True,
        alert_is_active=True,
        alert_use_llm=True,
        alert_auth_failures=_channel_call_count,
        **channel.create_args,
    ))
    out = response['id']

    trace(Channel_Channel, Sent, f'{channel.label} channel `{channel.name}` at {channel.url_path} -> {LiveServer.raising_service}')
    separator(Channel_Channel)

    return out

# ################################################################################################################################

def _new_notification_config() -> 'stranydict':
    """ Where the sweep explains and delivers - the LLM connection enmasse created and the default addressing.
    The scheduler hands the sweep these values as the job's extra, and here they are its payload.
    """
    out = {
        Alerting.Extra_LLM_Connection: LiveServer.llm_conn_name,
        Alerting.Extra_From: _email_from,
        Alerting.Extra_Default_To: ', '.join(_email_to),
    }
    return out

# ################################################################################################################################

def _produce_channel_failures(channel:'_ChannelDescription') -> 'None':
    """ Real HTTP calls to the channel - ones with the wrong password the channel rejects,
    then ones with the right one that the service behind the channel fails on.
    """
    url = f'http://{LiveServer.host}:{LiveServer.server_port}{channel.url_path}'

    # A REST call carries its body as JSON, a SOAP call as the envelope text with its own headers
    if channel.headers:
        request_args = {'data': channel.body, 'headers': channel.headers}
    else:
        request_args = {'json': channel.body}

    def call(password:'str', expected_status:'str') -> 'None':
        trace(Channel_Channel, Sent, f'{channel.label}: POST {channel.url_path} as {_security_username} with password {password!r}')

        response = requests.post(url, auth=(_security_username, password), timeout=_channel_call_timeout, **request_args)

        trace(Channel_Channel, Received, f'{channel.label}: {response.status_code} {response.reason}')
        trace(Channel_Channel, Received, response.text)
        separator(Channel_Channel)

        assert str(response.status_code) == expected_status, response.text

    for _ in range(_channel_call_count):
        call(_security_wrong_password, _status_unauthorized)

    for _ in range(_channel_call_count):
        call(_security_password, _status_server_error)

# ################################################################################################################################

def _server_audit_engine() -> 'any_':
    """ The audit database of the live server - the one file the server writes and this process reads.
    """
    path = os.path.join(LiveServer.server_directory, 'audit.db')
    out = create_engine(f'sqlite:///{path}')
    return out

# ################################################################################################################################

def _get_channel_responses(channel:'_ChannelDescription') -> 'anylist':
    """ Every response the live channel sent, as the server's audit log recorded it under the channel's source.
    """
    engine = _server_audit_engine()

    query = select(event_table).\
        where(event_table.c.source == channel.source).\
        where(event_table.c.object_name == channel.name).\
        where(event_table.c.event_type == AuditEvent.Response_Sent)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    for row in out:
        trace(Channel_Channel, Received,
            f'{channel.label} audit log: {row["event_time_iso"]} {row["status"]} caller={row["ext_client_id"]!r}')

    separator(Channel_Channel)

    return out

# ################################################################################################################################

def _get_stored_explanations(channel:'_ChannelDescription') -> 'anylist':
    """ Every explanation the live server stored for the channel's source, read off its own ODB - the two proofs
    share the server, so each reads the explanations of its own channel kind alone.
    """
    path = os.path.join(os.path.dirname(LiveServer.server_directory), 'zato.db')
    session_maker = sessionmaker(bind=create_engine(f'sqlite:///{path}'))

    store = ExplanationStore(session_maker, default_cluster_id)

    # Our response to produce
    out:'anylist' = []

    for explanation in store.get_list():
        if explanation['source'] == channel.source:
            out.append(explanation)

    for explanation in out:
        trace(Channel_Explain, Received, f'{channel.label} {explanation["rule"]}: {explanation["explanation"]}')
        trace(Channel_Explain, Received, f'confidence: {explanation["confidence"]}, remediation: {explanation["remediation"]}')
        separator(Channel_Explain)

    return out

# ################################################################################################################################
# ################################################################################################################################
