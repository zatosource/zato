# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explanation of an MLLP channel's alert - the mllp-channel skill explains it, the Object section is read off the
# channel's generic row with the MSH fields it matches on, its service, its destinations, what produces its reply and
# the acknowledgment codes it alerts on, and the failures group by their MSA-1 code and the ACK message together,
# naming the sending facilities the messages came from.

# stdlib
import json

# Zato
from zato.common.alerting.model import AlertAction
from zato.common.alerting.object_config import storage_name
from zato.common.api import GENERIC
from zato.common.audit_log.api import AuditLog, AuditSource
from zato.common.hl7.audit import audit_ack_sent, audit_message_received
from zato.common.odb.model import Cluster, GenericConn

# Test helpers
from explain_helpers import _cluster_id, _llm_conn_name, _new_payload, _new_service, _new_session, _object_section, \
    _server_name, _stored_explanation, _LLMFacade, LLMTestHandler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The channel the tests describe, the service its messages reach and the destination it delivers to
_channel_name = 'adt.intake'
_service_name = 'adt.process'
_destination_name = 'Archive'
_destination_connection = 'archive.rest'

# The sending application the channel matches on and the facilities the messages came from
_sending_app = 'ADT_SYSTEM'
_facility_a = 'GENERAL_HOSPITAL'
_facility_b = 'NORTH_CLINIC'

# The codes the channel alerts on, its own rather than the default
_own_ack_codes = 'AR, CR'

# The title line of the skill an MLLP channel is explained with
_mllp_skill_title = '# MLLP channel explanation'

# What the failed messages were answered with - three rejects with one MSA-3 text and one application error
_reject_code = 'AR'
_reject_reason = 'Unsupported message type ORM^O01'
_error_code = 'AE'
_error_reason = 'KeyError: PID.3'

_message_text = 'MSH|^~\\&|ADT_SYSTEM|{facility}|ZATO|ZATO|20260914||ADT^A01|MSG-1|P|2.5\rPID|||123'
_ack_text = 'MSH|^~\\&|ZATO|ZATO|ADT_SYSTEM|{facility}|20260914||ACK^A01|ACK-1|P|2.5\rMSA|{code}|MSG-1|{reason}'

# ################################################################################################################################

def _seed_channel(session_maker:'any_') -> 'None':
    """ One MLLP channel matching one sending application, with a service, a destination and alert settings of its own.
    """
    session = session_maker()
    cluster = session.query(Cluster).filter(Cluster.id==_cluster_id).one()

    destinations = [{
        'name': _destination_name,
        'type': 'rest',
        'connection': _destination_connection,
        'is_active': True,
    }]

    opaque = {
        'msh3_sending_app': _sending_app,
        'service': _service_name,
        'destinations': json.dumps(destinations),
        'respond_from': 'service',
        'delivery_mode': 'same-time',
        'is_audit_log_active': True,
        storage_name('is_active'): True,
        storage_name('ack_codes'): _own_ack_codes,
        storage_name('ack_threshold'): 5,
        storage_name('use_llm'): True,
    }

    row = GenericConn()
    row.name = _channel_name
    row.type_ = GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP
    row.is_active = True
    row.is_internal = False
    row.is_channel = True
    row.is_outconn = False
    row.pool_size = 1
    row.cluster = cluster
    row.opaque1 = json.dumps(opaque)

    session.add(row)
    session.commit()
    session.close()

# ################################################################################################################################

def _seed_message(audit_log:'AuditLog', cid:'str', ack_code:'str', reason:'str', facility:'str') -> 'None':
    """ One message the channel received and the acknowledgment it answered with.
    """
    attrs = {'msg_type': 'ADT^A01', 'mrn': '123', 'facility': facility, 'ack_status': ''}

    _ = audit_message_received(audit_log, _channel_name, _message_text.format(facility=facility), cid=cid, msg_id=cid,
        attrs=attrs)

    ack_text = _ack_text.format(facility=facility, code=ack_code, reason=reason)

    _ = audit_ack_sent(audit_log, _channel_name, ack_code, ack_text, cid=cid, msg_id=cid, facility=facility,
        duration_ms=20)

# ################################################################################################################################

def _seed_acks() -> 'None':
    """ The messages the channel acknowledged negatively - three rejects of one reason from two facilities
    and one application error - with one accepted message before them all.
    """
    audit_log = AuditLog(_server_name)

    _seed_message(audit_log, 'ok-1', 'AA', '', _facility_a)
    _seed_message(audit_log, 'error-1', _error_code, _error_reason, _facility_a)

    for index in range(3):
        facility = _facility_a if index else _facility_b
        _seed_message(audit_log, f'reject-{index}', _reject_code, _reject_reason, facility)

# ################################################################################################################################

def _explain(session:'any_', repo_dir:'str', llm_address:'any_', measure:'str') -> 'str':
    """ Explains one alert of the channel and gives back the prompt the model saw.
    """
    service = _new_service(
        _new_payload(AlertAction.Email_Digest, {}, AuditSource.MLLP_Channel, object_name=_channel_name, measures=[measure]),
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

class TestMllpChannel:

    def test_an_mllp_channel_alert_is_explained_with_the_mllp_skill(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_acks()

        session = _new_session()
        _seed_channel(session)

        prompt = _explain(session, repo_dir, llm_address, 'ack_count')
        assert prompt.startswith(_mllp_skill_title)

        explanation = _stored_explanation(session)

        assert explanation['source'] == AuditSource.MLLP_Channel
        assert explanation['is_parsed'] is True

# ################################################################################################################################

    def test_the_object_section_carries_the_match_the_service_the_destinations_and_the_codes(self, llm_address:'any_',
        repo_dir:'str') -> 'None':

        _seed_acks()

        session = _new_session()
        _seed_channel(session)

        prompt = _explain(session, repo_dir, llm_address, 'ack_count')
        section = _object_section(prompt)

        assert f'Name: {_channel_name}' in section
        assert 'Type: MLLP channel' in section
        assert 'Active: yes' in section
        assert f'Match: MSH-3 = {_sending_app}' in section
        assert 'Default channel: no' in section
        assert f'Service: {_service_name}' in section
        assert f'Destination: {_destination_name} - rest through {_destination_connection}' in section
        assert 'Reply produced by: the service' in section
        assert 'Delivery mode: same-time' in section
        assert 'Audit log: on' in section

        # The channel's own codes and threshold are the settings that differ from the defaults
        assert 'Alerts: on' in section
        assert f'Ack codes {_own_ack_codes}' in section
        assert 'Acknowledgments 5' in section

# ################################################################################################################################

    def test_the_failures_group_an_ack_under_its_code_and_text_and_name_the_facilities(self, llm_address:'any_',
        repo_dir:'str') -> 'None':

        _seed_acks()

        session = _new_session()
        _seed_channel(session)

        prompt = _explain(session, repo_dir, llm_address, 'ack_count')

        # The three rejects lead as one group named by the code and the ACK message, the error after them
        reject_text = _ack_text.format(facility=_facility_a, code=_reject_code, reason=_reject_reason)
        error_text = _ack_text.format(facility=_facility_a, code=_error_code, reason=_error_reason)

        assert f'1. {_reject_code} - {reject_text}' in prompt
        assert 'Count: 2' in prompt
        assert f'{_error_code} - {error_text}' in prompt
        assert _reject_reason in prompt
        assert _error_reason in prompt

        # The accepted message is nowhere among the failures
        assert 'MSA|AA' not in prompt

        # The facilities the rejected messages came from are the callers
        assert _facility_a in prompt
        assert _facility_b in prompt

# ################################################################################################################################
# ################################################################################################################################
