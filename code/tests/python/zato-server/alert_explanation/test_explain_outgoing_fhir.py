# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explanation of an outgoing FHIR connection's alert - the fhir skill explains it and a health check's alert alike,
# the Object section is read off the connection's generic row with its address, its security definition, its health check
# and the outcome codes it alerts on, and the failures group by their status and the OperationOutcome issue code.

# stdlib
import json

# Zato
from zato.common.alerting.model import AlertAction
from zato.common.alerting.object_config import storage_name
from zato.common.api import GENERIC, HTTP_SOAP
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.odb.model import Cluster, GenericConn, HTTPBasicAuth
from zato.common.typing_ import cast_

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

_health_check = HTTP_SOAP.HealthCheck

# The connection the tests describe and the security definition it calls with
_conn_name = 'ehr.fhir'
_conn_address = 'https://ehr.example.com/fhir/r4'
_security_name = 'EHR Basic Auth'

# The codes the connection alerts on, its own rather than the default
_own_outcome_codes = 'exception, not-found'

# The title line of the skill an outgoing FHIR connection is explained with
_fhir_skill_title = '# FHIR outgoing connection explanation'

# What the failed calls came back with - three OperationOutcomes of `exception` on a 500 and one bare 503 from a proxy
_outcome_status = '500 Internal Server Error'
_outcome_code = 'exception'
_outcome_diagnostics = 'The patient store is unavailable'
_outcome_text = json.dumps({
    'resourceType': 'OperationOutcome',
    'issue': [{'severity': 'error', 'code': _outcome_code, 'diagnostics': _outcome_diagnostics}],
})
_proxy_status = '503 Service Unavailable'
_proxy_text = '<html>Service Unavailable</html>'

# What a call reads and what a health check reads
_endpoint = 'GET Patient/1'
_ping_endpoint = 'GET /CapabilityStatement'

# ################################################################################################################################

def _seed_connection(session_maker:'any_') -> 'None':
    """ One outgoing FHIR connection with a Basic Auth definition, a health check every five minutes
    and alert settings of its own.
    """
    session = session_maker()
    cluster = session.query(Cluster).filter(Cluster.id==_cluster_id).one()

    security = HTTPBasicAuth(None, _security_name, True, 'ehr', 'Zato', 'never-shown', cluster)
    session.add(security)
    session.flush()

    opaque = {
        'security_id': security.id,
        'auth_type': 'basic_auth',
        'is_audit_log_active': True,
        _health_check.Field_Run_Every: 5,
        _health_check.Field_Run_Unit: 'minutes',
        storage_name('is_active'): True,
        storage_name('outcome_codes'): _own_outcome_codes,
        storage_name('outcome_threshold'): 5,
        storage_name('use_llm'): True,
    }

    row = cast_('any_', GenericConn())
    row.name = _conn_name
    row.type_ = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR
    row.is_active = True
    row.is_internal = False
    row.is_channel = False
    row.is_outconn = True
    row.address = _conn_address
    row.pool_size = 10
    row.cluster = cluster
    row.opaque1 = json.dumps(opaque)

    session.add(row)
    session.commit()
    session.close()

# ################################################################################################################################

def _seed_outcomes(source:'str'=AuditSource.FHIR, endpoint:'str'=_endpoint) -> 'None':
    """ The calls the connection made that failed - three answered with an OperationOutcome of `exception` on a 500,
    each recorded by its issue code, and one bare 503 from a proxy in front of the server, recorded by its status alone.
    """
    audit_log = AuditLog(_server_name)

    _ = audit_log.insert(source, AuditEvent.Request_Sent, _conn_name, cid='proxy-1',
        outcome=AuditOutcome.OK, endpoint=endpoint)
    _ = audit_log.insert(source, AuditEvent.Response_Received, _conn_name, cid='proxy-1',
        outcome=AuditOutcome.Error, status=_proxy_status, data=_proxy_text, endpoint=endpoint)

    for index in range(3):
        _ = audit_log.insert(source, AuditEvent.Request_Sent, _conn_name, cid=f'outcome-{index}',
            outcome=AuditOutcome.OK, endpoint=endpoint)
        _ = audit_log.insert(source, AuditEvent.Response_Received, _conn_name, cid=f'outcome-{index}',
            outcome=AuditOutcome.Error, status=_outcome_status, application_outcome=_outcome_code, data=_outcome_text,
            endpoint=endpoint)

# ################################################################################################################################

def _explain(session:'any_', repo_dir:'str', llm_address:'any_', source:'str', measure:'str') -> 'str':
    """ Explains one alert of the connection under the source and gives back the prompt the model saw.
    """
    service = _new_service(
        _new_payload(AlertAction.Email_Digest, {}, source, object_name=_conn_name, measures=[measure]),
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

class TestOutgoingFhir:

    def test_an_outgoing_fhir_alert_is_explained_with_the_fhir_skill(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_outcomes()

        session = _new_session()
        _seed_connection(session)

        prompt = _explain(session, repo_dir, llm_address, AuditSource.FHIR, 'outcome_count')
        assert prompt.startswith(_fhir_skill_title)

        explanation = _stored_explanation(session)

        assert explanation['source'] == AuditSource.FHIR
        assert explanation['is_parsed'] is True

# ################################################################################################################################

    def test_a_fhir_health_check_alert_is_explained_with_the_fhir_skill(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_outcomes(AuditSource.FHIR_Health, _ping_endpoint)

        session = _new_session()
        _seed_connection(session)

        prompt = _explain(session, repo_dir, llm_address, AuditSource.FHIR_Health, 'consecutive_failures')
        section = _object_section(prompt)

        assert prompt.startswith(_fhir_skill_title)
        assert 'Type: FHIR' in section

        explanation = _stored_explanation(session)
        assert explanation['source'] == AuditSource.FHIR_Health

# ################################################################################################################################

    def test_the_object_section_carries_the_address_the_security_and_the_outcome_codes(self, llm_address:'any_',
        repo_dir:'str') -> 'None':

        _seed_outcomes()

        session = _new_session()
        _seed_connection(session)

        prompt = _explain(session, repo_dir, llm_address, AuditSource.FHIR, 'outcome_count')
        section = _object_section(prompt)

        assert f'Name: {_conn_name}' in section
        assert 'Type: FHIR' in section
        assert 'Active: yes' in section
        assert f'Address: {_conn_address}' in section
        assert 'Pool size: 10' in section
        assert f'Security: {_security_name} (Basic Auth)' in section
        assert 'Audit log: on' in section
        assert 'Health check: every 5 minutes' in section

        # The connection's own codes and threshold are the settings that differ from the defaults
        assert f'Outcome codes {_own_outcome_codes}' in section
        assert 'Alerts: on' in section

# ################################################################################################################################

    def test_the_failures_group_an_outcome_under_its_status_and_issue_code(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_outcomes()

        session = _new_session()
        _seed_connection(session)

        prompt = _explain(session, repo_dir, llm_address, AuditSource.FHIR, 'outcome_count')

        # The three outcomes lead as one group named by the status and the issue code, the bare 503 by its status alone
        assert f'1. {_outcome_status} - {_outcome_code} - {_outcome_text}' in prompt
        assert 'Count: 3' in prompt
        assert f'2. {_proxy_status} - {_proxy_text}' in prompt

        # The outcome's own diagnostics reach the reader
        assert _outcome_diagnostics in prompt

# ################################################################################################################################
# ################################################################################################################################
