# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explanation of a channel's alert - a REST channel and a SOAP channel are explained with the same
# skill, the Object section says what each of them is, a SOAP channel with its action and version, and
# a REST channel and a SOAP channel sharing a name are each described from their own row.

# stdlib
import json

# Zato
from zato.common.alerting.explain.evidence import Heading_Object
from zato.common.alerting.model import AlertAction
from zato.common.alerting.object_config import storage_name
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.odb.model import Cluster, HTTPBasicAuth, HTTPSOAP, Service

# Test helpers
from explain_helpers import _cluster_id, _explanation_text, _llm_conn_name, _new_payload, _new_service, _new_session, \
    _object_section, _server_name, _stored_explanation, _LLMFacade, LLMTestHandler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The channel the channel tests describe, the service behind it, the security definition its callers use
_channel_name = 'orders.api'
_channel_service_name = 'orders.get'
_channel_security_name = 'Partner API'

# What the SOAP channel of the name answers to and speaks
_soap_url_path = '/soap/orders'
_soap_action = 'urn:orders'
_soap_version = '1.1'
_soap_fault_string = 'Server was unable to process request'

# The title line of the one skill both channel kinds are explained with
_channel_skill_title = '# REST and SOAP channel explanation'

# ################################################################################################################################

def _seed_channel(
    session_maker:'any_',
    *,
    transport:'str'='plain_http',
    url_path:'str'='/orders',
    with_security:'bool'=True,
) -> 'None':
    """ One channel of the transport with its service, a Basic Auth definition and alert settings of its own.
    A SOAP channel carries its action and version as well.
    """
    opaque = {
        'is_audit_log_active': True,
        storage_name('is_active'): True,
        storage_name('auth_failures'): 3,
        storage_name('use_llm'): True,
    }

    session = session_maker()
    cluster = session.query(Cluster).filter(Cluster.id==_cluster_id).one()

    # A REST and a SOAP channel of one name share the service and the security definition
    service = session.query(Service).filter(Service.name==_channel_service_name).first()
    if service is None:
        service = Service(None, _channel_service_name, True, 'orders.OrdersGet', False, cluster)
        session.add(service)

    if with_security:
        security = session.query(HTTPBasicAuth).filter(HTTPBasicAuth.name==_channel_security_name).first()
        if security is None:
            security = HTTPBasicAuth(None, _channel_security_name, True, 'partner', 'Zato', 'never-shown', cluster)
            session.add(security)
    else:
        security = None

    row = HTTPSOAP()
    row.name = _channel_name
    row.is_active = True
    row.is_internal = False
    row.connection = 'channel'
    row.transport = transport
    row.url_path = url_path
    row.method = 'POST'
    row.data_format = 'json'
    row.service = service
    row.security = security
    row.cluster = cluster
    row.opaque1 = json.dumps(opaque)

    if transport == 'soap':
        row.soap_action = _soap_action
        row.soap_version = _soap_version
    else:
        row.soap_action = ''

    session.add(row)
    session.commit()
    session.close()

# ################################################################################################################################

def _seed_channel_failures(source:'str'=AuditSource.REST_Channel, error_text:'str'='Invalid credentials') -> 'None':
    """ The calls a channel answered with an error - the request halves arrive fine, the responses
    carry the status and the caller.
    """
    audit_log = AuditLog(_server_name)

    for index in range(3):
        _ = audit_log.insert(source, AuditEvent.Request_Received, _channel_name, cid=f'call-{index}',
            outcome=AuditOutcome.OK, ext_client_id=_channel_security_name)
        _ = audit_log.insert(source, AuditEvent.Response_Sent, _channel_name, cid=f'call-{index}',
            outcome=AuditOutcome.Error, status='401 Unauthorized', data=error_text,
            ext_client_id=_channel_security_name, endpoint=_channel_service_name)

# ################################################################################################################################

def _explain_channel(session:'any_', repo_dir:'str', llm_address:'any_', source:'str') -> 'str':
    """ Explains one auth failures alert of the channel of the source and gives back the prompt the model saw.
    """
    service = _new_service(
        _new_payload(AlertAction.Email_Digest, {}, source, object_name=_channel_name, measures=['auth_failure_count']),
        session,
        repo_dir,
        llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
    )

    service.handle()

    assert len(LLMTestHandler.prompts) == 1

    out = LLMTestHandler.prompts[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRestChannel:

    def test_a_rest_channel_alert_is_explained_with_the_channel_skill(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_channel_failures()

        session = _new_session()
        _seed_channel(session)

        prompt = _explain_channel(session, repo_dir, llm_address, AuditSource.REST_Channel)
        assert prompt.startswith(_channel_skill_title)

        # The channel's skill allows no remediation, so the reply's resubmit is dropped and the rest is kept
        explanation = _stored_explanation(session)

        assert explanation['source'] == AuditSource.REST_Channel
        assert explanation['explanation'] == _explanation_text
        assert explanation['is_parsed'] is True
        assert explanation['remediation'] is None

# ################################################################################################################################

    def test_the_object_section_describes_the_channel(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_channel_failures()

        session = _new_session()
        _seed_channel(session)

        prompt = _explain_channel(session, repo_dir, llm_address, AuditSource.REST_Channel)
        section = _object_section(prompt)

        assert f'Name: {_channel_name}' in section
        assert 'Transport: REST' in section
        assert 'Active: yes' in section
        assert 'URL path: /orders' in section
        assert 'Method: POST' in section
        assert f'Service: {_channel_service_name}' in section
        assert f'Security: {_channel_security_name} (Basic Auth)' in section
        assert 'Data format: json' in section
        assert 'Audit log: on' in section
        assert 'Alerts: on' in section
        assert 'Alert settings of its own: Auth failures 3' in section

        # A REST channel has no SOAP lines
        assert 'SOAP action' not in section
        assert 'SOAP version' not in section

        assert 'never-shown' not in prompt

        # The failures name the callers and the service, the baseline counts the responses
        assert '1. 401 Unauthorized - Invalid credentials' in prompt
        assert f'Service: {_channel_service_name}' in prompt
        assert f'Caller: {_channel_security_name}' in prompt
        assert 'OK events in the window: 0' in prompt

# ################################################################################################################################

    def test_a_channel_without_security_or_own_settings_says_so(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_channel_failures()

        session = _new_session()
        _seed_channel(session, with_security=False)

        # The channel's own settings are the defaults
        with session() as s:
            row = s.query(HTTPSOAP).filter(HTTPSOAP.name==_channel_name).one()
            row.opaque1 = json.dumps({storage_name('is_active'): True})
            s.commit()

        prompt = _explain_channel(session, repo_dir, llm_address, AuditSource.REST_Channel)
        section = _object_section(prompt)

        assert 'Security: None' in section
        assert 'Alert settings of its own: none, the defaults apply' in section

# ################################################################################################################################

    def test_a_channel_that_is_not_in_the_odb_contributes_its_name_alone(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_channel_failures()

        session = _new_session()

        prompt = _explain_channel(session, repo_dir, llm_address, AuditSource.REST_Channel)
        section = _object_section(prompt)

        assert section.strip() == f'{Heading_Object}\n\nName: {_channel_name}'

# ################################################################################################################################
# ################################################################################################################################

class TestSoapChannel:

    def test_a_soap_channel_alert_is_explained_with_the_channel_skill(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_channel_failures(AuditSource.SOAP_Channel, _soap_fault_string)

        session = _new_session()
        _seed_channel(session, transport='soap', url_path=_soap_url_path)

        prompt = _explain_channel(session, repo_dir, llm_address, AuditSource.SOAP_Channel)
        assert prompt.startswith(_channel_skill_title)

        explanation = _stored_explanation(session)

        assert explanation['source'] == AuditSource.SOAP_Channel
        assert explanation['explanation'] == _explanation_text
        assert explanation['is_parsed'] is True
        assert explanation['remediation'] is None

# ################################################################################################################################

    def test_the_object_section_describes_the_soap_channel(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_channel_failures(AuditSource.SOAP_Channel, _soap_fault_string)

        session = _new_session()
        _seed_channel(session, transport='soap', url_path=_soap_url_path)

        prompt = _explain_channel(session, repo_dir, llm_address, AuditSource.SOAP_Channel)
        section = _object_section(prompt)

        assert f'Name: {_channel_name}' in section
        assert 'Transport: SOAP' in section
        assert f'URL path: {_soap_url_path}' in section
        assert f'SOAP action: {_soap_action}' in section
        assert f'SOAP version: {_soap_version}' in section
        assert 'Method: POST' in section
        assert f'Service: {_channel_service_name}' in section
        assert f'Security: {_channel_security_name} (Basic Auth)' in section
        assert 'Alert settings of its own: Auth failures 3' in section

        # The SOAP lines sit between the path and the method
        assert section.index('URL path:') < section.index('SOAP action:') < section.index('SOAP version:') < section.index('Method:')

        # The fault string is the error text of the failures
        assert f'1. 401 Unauthorized - {_soap_fault_string}' in prompt

# ################################################################################################################################

    def test_a_rest_and_a_soap_channel_of_one_name_are_each_described_from_their_own_row(
        self,
        llm_address:'any_',
        repo_dir:'str',
    ) -> 'None':

        _seed_channel_failures(AuditSource.SOAP_Channel, _soap_fault_string)

        session = _new_session()
        _seed_channel(session)
        _seed_channel(session, transport='soap', url_path=_soap_url_path)

        prompt = _explain_channel(session, repo_dir, llm_address, AuditSource.SOAP_Channel)
        section = _object_section(prompt)

        # The SOAP channel's row, not the REST channel's one of the same name
        assert 'Transport: SOAP' in section
        assert f'URL path: {_soap_url_path}' in section
        assert 'URL path: /orders' not in section

# ################################################################################################################################
# ################################################################################################################################
