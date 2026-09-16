# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explanation of an outgoing REST connection's alert - the connection's own skill explains it, the Object
# section is read off the connection's row as a channel's is, with its address, its alert settings and the
# status codes it alerts on, a health check's alert reads the same Object, and the failures group by their
# status - an HTTP status line or a transport status such as a timeout.

# stdlib
import json

# Zato
from zato.common.alerting.explain.evidence import Heading_Object
from zato.common.alerting.model import AlertAction
from zato.common.alerting.object_config import storage_name
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.common import TransportStatus
from zato.common.odb.model import Cluster, HTTPBasicAuth, HTTPSOAP

# Test helpers
from explain_helpers import _cluster_id, _llm_conn_name, _server_name, _LLMFacade, LLMTestHandler, \
    new_payload as _new_payload, new_service as _new_service, new_session as _new_session, \
    object_section as _object_section, stored_explanation as _stored_explanation

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The connection the tests describe and the security definition it calls with
_conn_name = 'crm.api'
_conn_host = 'https://crm.example.com'
_conn_url_path = '/api/v2/customers'
_security_name = 'CRM API Key'

# The codes the connection alerts on, its own rather than the default
_own_status_codes = '401, 403, 4xx, 5xx'

# The title line of the skill an outgoing REST connection is explained with, and the one of a SOAP connection's own
_outgoing_skill_title = '# REST outgoing connection explanation'
_soap_skill_title = '# SOAP outgoing connection explanation'

# The SOAP connection - its action and version, the fault codes of its own and what its faults arrive as
_soap_conn_name = 'crm.soap'
_soap_action = 'urn:crm:GetCustomer'
_soap_version = '1.2'
_own_fault_codes = 'Receiver'
_fault_status = '500 Internal Server Error'
_fault_code = 'Receiver'
_fault_text = '<soap:Envelope><soap:Body><soap:Fault><soap:Reason>An error has occurred</soap:Reason></soap:Fault></soap:Body></soap:Envelope>'

# What the remote side answered the rejected calls with, and what it never got to answer
_rejected_status = '401 Unauthorized'
_rejected_text = '{"error": "invalid api key"}'
_timeout_text = 'Timeout error: HTTPSConnectionPool(host=crm.example.com, port=443): Read timed out.'

# ################################################################################################################################

def _seed_connection(
    session_maker:'any_',
    *,
    with_security:'bool'=True,
    opaque:'dict | None'=None,
    is_soap:'bool'=False,
    ) -> 'None':
    """ One outgoing REST connection with a Basic Auth definition and alert settings of its own,
    or a SOAP one with fault codes of its own on top.
    """
    if opaque is None:
        opaque = {
            'is_audit_log_active': True,
            'validate_tls': True,
            'max_retries': 2,
            storage_name('is_active'): True,
            storage_name('status_codes'): _own_status_codes,
            storage_name('status_code_threshold'): 5,
            storage_name('use_llm'): True,
        }

        if is_soap:
            opaque[storage_name('fault_codes')] = _own_fault_codes

    session = session_maker()
    cluster = session.query(Cluster).filter(Cluster.id==_cluster_id).one()

    if with_security:
        security = HTTPBasicAuth(None, _security_name, True, 'crm', 'Zato', 'never-shown', cluster)
        session.add(security)
    else:
        security = None

    row = HTTPSOAP()
    row.is_active = True
    row.is_internal = False
    row.connection = 'outgoing'

    if is_soap:
        row.name = _soap_conn_name
        row.transport = 'soap'
        row.soap_action = _soap_action
        row.soap_version = _soap_version
    else:
        row.name = _conn_name
        row.transport = 'plain_http'
        row.soap_action = ''
    row.host = _conn_host
    row.url_path = _conn_url_path
    row.method = 'POST'
    row.ping_method = 'GET'
    row.timeout = 15
    row.pool_size = 20
    row.data_format = 'json'
    row.security = security
    row.cluster = cluster
    row.opaque1 = json.dumps(opaque)

    session.add(row)
    session.commit()
    session.close()

# ################################################################################################################################

def _seed_failures(source:'str'=AuditSource.REST_Outgoing) -> 'None':
    """ The calls the connection made that failed - two the remote side rejected and one that timed out,
    each with the request half that went out fine.
    """
    audit_log = AuditLog(_server_name)
    endpoint = f'POST {_conn_host}{_conn_url_path}'

    for index in range(2):
        _ = audit_log.insert(source, AuditEvent.Request_Sent, _conn_name, cid=f'rejected-{index}',
            outcome=AuditOutcome.OK, endpoint=endpoint)
        _ = audit_log.insert(source, AuditEvent.Response_Received, _conn_name, cid=f'rejected-{index}',
            outcome=AuditOutcome.Error, status=_rejected_status, data=_rejected_text, endpoint=endpoint)

    _ = audit_log.insert(source, AuditEvent.Request_Sent, _conn_name, cid='timeout-1',
        outcome=AuditOutcome.OK, endpoint=endpoint)
    _ = audit_log.insert(source, AuditEvent.Response_Received, _conn_name, cid='timeout-1',
        outcome=AuditOutcome.Error, status=TransportStatus.Timeout, data=_timeout_text, endpoint=endpoint)

# ################################################################################################################################

def _seed_faults(source:'str'=AuditSource.SOAP_Outgoing) -> 'None':
    """ The calls the SOAP connection made that failed - three answered with a Receiver fault on a 500, each recorded
    by its fault code, and one bare 503 from a proxy in front of the endpoint, recorded by its status alone.
    """
    audit_log = AuditLog(_server_name)
    endpoint = f'GetCustomer {_conn_host}{_conn_url_path}'

    _ = audit_log.insert(source, AuditEvent.Request_Sent, _soap_conn_name, cid='proxy-1',
        outcome=AuditOutcome.OK, endpoint=endpoint)
    _ = audit_log.insert(source, AuditEvent.Response_Received, _soap_conn_name, cid='proxy-1',
        outcome=AuditOutcome.Error, status='503 Service Unavailable', data='<html>Service Unavailable</html>', endpoint=endpoint)

    for index in range(3):
        _ = audit_log.insert(source, AuditEvent.Request_Sent, _soap_conn_name, cid=f'fault-{index}',
            outcome=AuditOutcome.OK, endpoint=endpoint)
        _ = audit_log.insert(source, AuditEvent.Response_Received, _soap_conn_name, cid=f'fault-{index}',
            outcome=AuditOutcome.Error, status=_fault_status, application_outcome=_fault_code, data=_fault_text,
            endpoint=endpoint)

# ################################################################################################################################

def _explain_outgoing(
    session:'any_',
    repo_dir:'str',
    llm_address:'any_',
    source:'str',
    measure:'str',
    object_name:'str'=_conn_name,
    ) -> 'str':
    """ Explains one alert of the connection under the source and gives back the prompt the model saw.
    """
    service = _new_service(
        _new_payload(AlertAction.Email_Digest, {}, source, object_name=object_name, measures=[measure]),
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

class TestOutgoingRest:

    def test_an_outgoing_rest_alert_is_explained_with_the_outgoing_skill(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_failures()

        session = _new_session()
        _seed_connection(session)

        prompt = _explain_outgoing(session, repo_dir, llm_address, AuditSource.REST_Outgoing, 'status_code_count')
        assert prompt.startswith(_outgoing_skill_title)

        explanation = _stored_explanation(session)

        assert explanation['source'] == AuditSource.REST_Outgoing
        assert explanation['is_parsed'] is True

# ################################################################################################################################

    def test_the_object_section_describes_the_connection(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_failures()

        session = _new_session()
        _seed_connection(session)

        prompt = _explain_outgoing(session, repo_dir, llm_address, AuditSource.REST_Outgoing, 'status_code_count')
        section = _object_section(prompt)

        assert f'Name: {_conn_name}' in section
        assert 'Active: yes' in section
        assert f'Address: {_conn_host}{_conn_url_path}' in section
        assert 'Method: POST' in section
        assert 'Ping method: GET' in section
        assert 'Timeout: 15 s' in section
        assert 'Pool size: 20' in section
        assert 'TLS validation: on' in section
        assert f'Security: {_security_name} (Basic Auth)' in section
        assert 'Data format: json' in section
        assert 'Retries: 2' in section
        assert 'Audit log: on' in section
        assert 'Alerts: on' in section

        # The connection's own codes and threshold are the settings that differ from the defaults
        assert f'Alert settings of its own: Status codes {_own_status_codes}, Responses 5' in section

        assert 'never-shown' not in prompt

# ################################################################################################################################

    def test_the_failures_group_by_status(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_failures()

        session = _new_session()
        _seed_connection(session)

        prompt = _explain_outgoing(session, repo_dir, llm_address, AuditSource.REST_Outgoing, 'connection_failure_count')

        # The newest failure leads - the timeout, with its transport status first, then the two rejections
        assert f'1. {TransportStatus.Timeout} - {_timeout_text}' in prompt
        assert f'2. {_rejected_status} - {_rejected_text}' in prompt
        assert 'Count: 2' in prompt

        # The response halves alone count for the baseline
        assert 'OK events in the window: 0' in prompt

# ################################################################################################################################

    def test_a_connection_without_security_or_own_settings_says_so(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_failures()

        session = _new_session()
        _seed_connection(session, with_security=False, opaque={storage_name('is_active'): True})

        prompt = _explain_outgoing(session, repo_dir, llm_address, AuditSource.REST_Outgoing, 'status_code_count')
        section = _object_section(prompt)

        assert 'Security: None' in section
        assert 'TLS validation: on' in section
        assert 'Audit log: on' in section
        assert 'Retries' not in section
        assert 'Alert settings of its own: none, the defaults apply' in section

# ################################################################################################################################

    def test_a_health_check_alert_reads_the_same_object(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_failures(AuditSource.REST_Outgoing_Health)

        session = _new_session()
        _seed_connection(session)

        prompt = _explain_outgoing(session, repo_dir, llm_address, AuditSource.REST_Outgoing_Health, 'consecutive_failures')
        section = _object_section(prompt)

        # The check's skill is the connection's, and so is its Object
        assert prompt.startswith(_outgoing_skill_title)
        assert f'Address: {_conn_host}{_conn_url_path}' in section
        assert 'Alerts: on' in section

# ################################################################################################################################

    def test_a_connection_that_is_not_in_the_odb_contributes_its_name_alone(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_failures()

        session = _new_session()

        prompt = _explain_outgoing(session, repo_dir, llm_address, AuditSource.REST_Outgoing, 'status_code_count')
        section = _object_section(prompt)

        assert section.strip() == f'{Heading_Object}\n\nName: {_conn_name}'

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingSoap:

    def test_an_outgoing_soap_alert_is_explained_with_the_soap_skill(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_faults()

        session = _new_session()
        _seed_connection(session, is_soap=True)

        prompt = _explain_outgoing(session, repo_dir, llm_address, AuditSource.SOAP_Outgoing, 'fault_count', _soap_conn_name)
        assert prompt.startswith(_soap_skill_title)

        explanation = _stored_explanation(session)

        assert explanation['source'] == AuditSource.SOAP_Outgoing
        assert explanation['is_parsed'] is True

# ################################################################################################################################

    def test_a_soap_health_check_alert_is_explained_with_the_soap_skill(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_faults(AuditSource.SOAP_Outgoing_Health)

        session = _new_session()
        _seed_connection(session, is_soap=True)

        prompt = _explain_outgoing(session, repo_dir, llm_address, AuditSource.SOAP_Outgoing_Health, 'consecutive_failures',
            _soap_conn_name)
        section = _object_section(prompt)

        assert prompt.startswith(_soap_skill_title)
        assert 'Transport: SOAP' in section

# ################################################################################################################################

    def test_the_object_section_carries_the_soap_details_and_the_fault_codes(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_faults()

        session = _new_session()
        _seed_connection(session, is_soap=True)

        prompt = _explain_outgoing(session, repo_dir, llm_address, AuditSource.SOAP_Outgoing, 'fault_count', _soap_conn_name)
        section = _object_section(prompt)

        assert 'Transport: SOAP' in section
        assert f'SOAP action: {_soap_action}' in section
        assert f'SOAP version: {_soap_version}' in section

        # The connection's own codes of both kinds are the settings that differ from the defaults
        assert f'Status codes {_own_status_codes}' in section
        assert f'Fault codes {_own_fault_codes}' in section

# ################################################################################################################################

    def test_the_failures_group_a_fault_under_its_status_and_code(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_faults()

        session = _new_session()
        _seed_connection(session, is_soap=True)

        prompt = _explain_outgoing(session, repo_dir, llm_address, AuditSource.SOAP_Outgoing, 'fault_count', _soap_conn_name)

        # The three faults lead as one group named by the status and the fault code, the bare 503 by its status alone
        assert f'1. {_fault_status} - {_fault_code} - {_fault_text}' in prompt
        assert 'Count: 3' in prompt
        assert '2. 503 Service Unavailable - <html>Service Unavailable</html>' in prompt

        # The fault's own words reach the reader
        assert 'An error has occurred' in prompt

# ################################################################################################################################
# ################################################################################################################################
