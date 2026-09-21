# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explanation of an outgoing MLLP connection's alert - the mllp-outgoing skill explains it, the Object section is
# read off the connection's generic row with its address, its TLS, its pool, its retries and its circuit breaker, and
# the acknowledgment codes it alerts on, and the failures group by the text and the MSA-1 code of the acknowledgment
# the remote system answered, a message no acknowledgment came back for reading as its timeout status.

# stdlib
import json

# Zato
from zato.common.alerting.model import AlertAction
from zato.common.alerting.object_config import storage_name
from zato.common.api import GENERIC
from zato.common.audit_log.api import AuditLog, AuditSource
from zato.common.hl7.audit import audit_ack_received, audit_message_sent, ACKStatus
from zato.common.odb.model import Cluster, GenericConn
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

# The connection the tests describe and the remote system it sends to
_conn_name = 'lab.results'
_address = 'lab.example.com:2575'

# The codes the connection alerts on, its own rather than the default, and how many failures it tolerates
_own_ack_codes = 'AR, CR'
_own_connection_failures = 5

# The title line of the skill an outgoing MLLP connection is explained with
_mllp_skill_title = '# MLLP outgoing connection explanation'

# What the failed messages were answered with - three rejects with one MSA-3 text and one application error
_reject_code = 'AR'
_reject_reason = 'Unknown patient'
_error_code = 'AE'
_error_reason = 'NullPointerException in OrderProcessor'

_message_text = 'MSH|^~\\&|ZATO|ZATO|LAB|LAB_SYSTEM|20260914||ORU^R01|MSG-1|P|2.5\rPID|||123'

# ################################################################################################################################

def _seed_connection(session_maker:'any_') -> 'None':
    """ One outgoing MLLP connection over TLS, with retries and a breaker of its own and alert settings of its own.
    """
    session = session_maker()
    cluster = session.query(Cluster).filter(Cluster.id==_cluster_id).one()

    opaque = {
        'max_wait_time': 5,
        'max_retries': 7,
        'retry_sleep_time': 2,
        'retry_backoff_threshold': 120,
        'use_queue': True,
        'circuit_breaker_threshold_percent': 50,
        'circuit_breaker_window_seconds': 60,
        'circuit_breaker_reset_seconds': 90,
        'tls_ca_path': '/etc/zato/ca.pem',
        'is_audit_log_active': True,
        storage_name('is_active'): True,
        storage_name('ack_codes'): _own_ack_codes,
        storage_name('connection_failures'): _own_connection_failures,
        storage_name('use_llm'): True,
    }

    row = cast_('any_', GenericConn())
    row.name = _conn_name
    row.type_ = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP
    row.address = _address
    row.is_active = True
    row.is_internal = False
    row.is_channel = False
    row.is_outconn = True
    row.pool_size = 4
    row.cluster = cluster
    row.opaque1 = json.dumps(opaque)

    session.add(row)
    session.commit()
    session.close()

# ################################################################################################################################

def _seed_message(audit_log:'AuditLog', cid:'str', ack_code:'str', reason:'str') -> 'None':
    """ One message the connection sent and the acknowledgment it was answered, or the timeout marker when none came.
    """
    attrs = {'msg_type': 'ORU^R01', 'mrn': '123', 'facility': 'ZATO'}

    _ = audit_message_sent(audit_log, _conn_name, _message_text, cid=cid, msg_id=cid, attrs=attrs, endpoint=_address)
    _ = audit_ack_received(audit_log, _conn_name, ack_code, cid=cid, msg_id=cid, duration_ms=20, error_text=reason)

# ################################################################################################################################

def _seed_acks() -> 'None':
    """ The messages the connection had fail - three rejects of one reason, one application error and one message
    no acknowledgment came back for - with one accepted message before them all.
    """
    audit_log = AuditLog(_server_name)

    _seed_message(audit_log, 'ok-1', 'AA', '')
    _seed_message(audit_log, 'error-1', _error_code, _error_reason)
    _seed_message(audit_log, 'timeout-1', ACKStatus.Timeout, '')

    for index in range(3):
        _seed_message(audit_log, f'reject-{index}', _reject_code, _reject_reason)

# ################################################################################################################################

def _explain(session:'any_', repo_dir:'str', llm_address:'any_', measure:'str') -> 'str':
    """ Explains one alert of the connection and gives back the prompt the model saw.
    """
    service = _new_service(
        _new_payload(AlertAction.Email_Digest, {}, AuditSource.MLLP_Outgoing, object_name=_conn_name, measures=[measure]),
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

class TestMllpOutgoing:

    def test_an_outgoing_mllp_alert_is_explained_with_the_mllp_outgoing_skill(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_acks()

        session = _new_session()
        _seed_connection(session)

        prompt = _explain(session, repo_dir, llm_address, 'ack_count')
        assert prompt.startswith(_mllp_skill_title)

        explanation = _stored_explanation(session)

        assert explanation['source'] == AuditSource.MLLP_Outgoing
        assert explanation['is_parsed'] is True

# ################################################################################################################################

    def test_the_object_section_carries_the_address_the_tls_the_retries_the_breaker_and_the_codes(self, llm_address:'any_',
        repo_dir:'str') -> 'None':

        _seed_acks()

        session = _new_session()
        _seed_connection(session)

        prompt = _explain(session, repo_dir, llm_address, 'ack_count')
        section = _object_section(prompt)

        assert f'Name: {_conn_name}' in section
        assert 'Type: MLLP outgoing connection' in section
        assert 'Active: yes' in section
        assert f'Address: {_address}' in section
        assert 'TLS: on' in section
        assert 'Connections kept open: 4' in section
        assert 'Ack wait: 5s' in section
        assert 'Retries: 7, waiting from 2s, up to 120s in total' in section
        assert 'Queue: on' in section
        assert 'Sending pauses: at 50% failures in 60s, for 90s' in section
        assert 'Audit log: on' in section

        # The connection's own codes and failures are the settings that differ from the defaults
        assert 'Alerts: on' in section
        assert f'Ack codes {_own_ack_codes}' in section
        assert f'Connection failures {_own_connection_failures}' in section

# ################################################################################################################################

    def test_the_failures_group_an_ack_under_its_text_and_code_and_a_timeout_under_its_status(self, llm_address:'any_',
        repo_dir:'str') -> 'None':

        _seed_acks()

        session = _new_session()
        _seed_connection(session)

        prompt = _explain(session, repo_dir, llm_address, 'ack_count')

        # The three rejects lead as one group named by the acknowledgment's text and code, the error and the timeout after them
        assert f'1. {_reject_reason} - {_reject_code}' in prompt
        assert 'Count: 3' in prompt
        assert f'{_error_reason} - {_error_code}' in prompt

        # A message no acknowledgment came back for says nothing in its status - its ack status is what it reads as
        assert f'. {ACKStatus.Timeout}\n' in prompt

        # The accepted message is nowhere among the failures
        assert 'AA' not in prompt.split('Failures')[1].split('Baseline')[0]

        # The endpoint the messages went to is named
        assert _address in prompt

# ################################################################################################################################
# ################################################################################################################################
