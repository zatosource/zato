# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.common import AuditClassification
from zato.common.audit_log.request_context import Key_Headers, Key_Payload, Key_Payload_Kind, Key_Redacted, \
    Payload_Kind_Described, Redacted_Value
from zato.common.audit_log.resubmit import load_event, require_resendable_request, resend_hop, run_once, \
    Action_Resend, DuplicateResubmitException, ResubmitException
from zato.common.destination.model import new_send_result
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.destination.model import HopSendResult
    from zato.common.typing_ import anydict, anylist
    anydict = anydict
    anylist = anylist
    AuditLog = AuditLog
    HopSendResult = HopSendResult

# ################################################################################################################################
# ################################################################################################################################

# The connection these checks record against
_connection_name = 'audit.test.core.hop'

# Who asks for the resubmits in this scenario
_actor = 'resubmit.operator'

# The HL7 message the MLLP hop checks send, and the two answers it comes back with
_mllp_message = 'MSH|^~\\&|HIS|HOSP|LAB|CENTRAL|20260115103000||ADT^A01^ADT_A01|MSG-ACK-1|P|2.5\r'
_mllp_ack_accepted = 'MSH|^~\\&|LAB|CENTRAL|HIS|HOSP|20260115103001||ACK|ACK-1|P|2.5\rMSA|AA|MSG-ACK-1\r'
_mllp_ack_rejected = (
    'MSH|^~\\&|LAB|CENTRAL|HIS|HOSP|20260115103001||ACK|ACK-2|P|2.5\r'
    'MSA|AR|MSG-ACK-1|Unknown patient\r')

# What a described payload reads as in the log
_described_payload = '<MultipartEncoder object at 0x1>'

# ################################################################################################################################
# ################################################################################################################################

def get_event_rows(cid:'str', event_type:'str') -> 'anylist':
    """ Returns the rows of one type written under one correlation id, oldest first.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.where(event_table.c.cid == cid)
    query = query.where(event_table.c.event_type == event_type)
    query = query.order_by(event_table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(dict(row._mapping))

    return out

# ################################################################################################################################

def run_request_context_checks(audit_log:'AuditLog') -> 'None':
    """ Confirms a call the log could not keep whole refuses to go out again.
    """

    # A header that carried a credential is named in the refusal, whatever case it arrived in ..
    for header_name in ('Authorization', 'X-Api-Key'):

        redacted_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _connection_name,
            cid=f'cid-core-redacted-{header_name}', outcome=AuditOutcome.Error,
            data=dumps({
                Key_Payload: 'the-body',
                Key_Headers: {header_name: Redacted_Value},
                Key_Redacted: [header_name],
            }))

        try:
            require_resendable_request(load_event(redacted_id))
        except ResubmitException as e:
            assert header_name in str(e)
            assert 'cannot be resubmitted' in str(e)
        else:
            raise Exception(f'A call redacted of `{header_name}` was expected to be refused')

    # .. and a body the log described rather than kept cannot go back out either.
    described_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _connection_name,
        cid='cid-core-described', outcome=AuditOutcome.Error,
        data=dumps({
            Key_Payload: _described_payload,
            Key_Payload_Kind: Payload_Kind_Described,
        }))

    try:
        require_resendable_request(load_event(described_id))
    except ResubmitException as e:
        assert 'describes its request body' in str(e)
    else:
        raise Exception('A described body was expected to be refused')

    # A call the log kept whole passes the very same gate.
    whole_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _connection_name,
        cid='cid-core-whole', outcome=AuditOutcome.Error,
        data=dumps({Key_Payload: 'the-body', Key_Headers: {'Accept': 'application/json'}}))

    require_resendable_request(load_event(whole_id))

# ################################################################################################################################

def run_hop_ack_checks(audit_log:'AuditLog') -> 'None':
    """ Confirms a repeated MLLP delivery records the acknowledgment it brought back, an accepted
    one and a rejected one alike.
    """
    original_id = audit_log.insert(AuditSource.MLLP_Outgoing, AuditEvent.Request_Sent, _connection_name,
        cid='cid-core-hop-ack-orig', msg_id='MSG-ACK-1', outcome=AuditOutcome.Error,
        status='Connection timeout', data=dumps({Key_Payload: _mllp_message}))

    def accepting_send(payload:'str') -> 'HopSendResult':
        out = new_send_result(_mllp_ack_accepted, response_text=_mllp_ack_accepted)
        return out

    accepted = resend_hop(load_event(original_id), accepting_send, audit_log, 'cid-core-hop-ack-ok')

    ack_rows = get_event_rows('cid-core-hop-ack-ok', AuditEvent.Ack_Received)
    ack_row = ack_rows[0]

    assert len(ack_rows) == 1
    assert ack_row['outcome'] == AuditOutcome.OK
    assert ack_row['correl_id'] == 'cid-core-hop-ack-orig'
    assert ack_row['msg_id'] == 'MSG-ACK-1'
    assert accepted.event_id is not None

    # A receiver saying no is recorded as its own acknowledgment row too.
    def rejecting_send(payload:'str') -> 'HopSendResult':
        out = new_send_result(_mllp_ack_rejected, is_rejected=True, status='HL7 ack rejected AR',
            response_text=_mllp_ack_rejected, classification=AuditClassification.Permanent)
        return out

    try:
        _ = resend_hop(load_event(original_id), rejecting_send, audit_log, 'cid-core-hop-ack-no')
    except ResubmitException:
        pass
    else:
        raise Exception('A rejected acknowledgment was expected to be reported as a failed resend')

    rejected_ack_rows = get_event_rows('cid-core-hop-ack-no', AuditEvent.Ack_Received)
    rejected_ack_row = rejected_ack_rows[0]

    assert len(rejected_ack_rows) == 1
    assert rejected_ack_row['outcome'] == AuditOutcome.Error

    # A connection of any other kind leaves no acknowledgment row behind.
    rest_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _connection_name,
        cid='cid-core-hop-ack-rest-orig', outcome=AuditOutcome.Error, data=dumps({Key_Payload: 'rest-payload'}))

    def rest_send(payload:'str') -> 'HopSendResult':
        out = new_send_result('rest-response', response_text='rest-response')
        return out

    _ = resend_hop(load_event(rest_id), rest_send, audit_log, 'cid-core-hop-ack-rest')

    assert get_event_rows('cid-core-hop-ack-rest', AuditEvent.Ack_Received) == []

# ################################################################################################################################

def run_run_once_checks(audit_log:'AuditLog') -> 'None':
    """ Confirms one row goes out again exactly once, while an attempt that failed leaves the
    row pressable again.
    """
    event_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _connection_name,
        cid='cid-core-once-orig', outcome=AuditOutcome.Error, data=dumps({Key_Payload: 'once-payload'}))

    attempts:'anylist' = []

    def resubmit_one() -> 'str':
        attempts.append('sent')
        return 'done'

    assert run_once(Action_Resend, event_id, 'once-payload', 'cid-core-once-1', _actor, resubmit_one) == 'done'

    # The second press of the same button on the same row sends nothing ..
    try:
        _ = run_once(Action_Resend, event_id, 'once-payload', 'cid-core-once-2', _actor, resubmit_one)
    except DuplicateResubmitException as e:
        assert 'was already resubmitted' in str(e)
    else:
        raise Exception('A second identical resubmit was expected to be refused')

    assert attempts == ['sent']

    # .. an attempt that did not go through leaves nothing behind, so the row stays pressable ..
    other_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _connection_name,
        cid='cid-core-once-other', outcome=AuditOutcome.Error, data=dumps({Key_Payload: 'other-payload'}))

    def failing_resubmit_one() -> 'str':
        raise Exception('The target is down')

    try:
        _ = run_once(Action_Resend, other_id, 'other-payload', 'cid-core-once-3', _actor, failing_resubmit_one)
    except Exception as e:
        assert str(e) == 'The target is down'
    else:
        raise Exception('A failed resubmit was expected to propagate')

    assert run_once(Action_Resend, other_id, 'other-payload', 'cid-core-once-4', _actor, resubmit_one) == 'done'
    assert attempts == ['sent', 'sent']

    # .. and the attempt row a resend created is a row of its own, so sending that one again works.
    attempt_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _connection_name,
        cid='cid-core-once-attempt', correl_id='cid-core-once-orig', outcome=AuditOutcome.Error,
        data=dumps({Key_Payload: 'once-payload'}))

    assert run_once(Action_Resend, attempt_id, 'once-payload', 'cid-core-once-5', _actor, resubmit_one) == 'done'
    assert attempts == ['sent', 'sent', 'sent']

# ################################################################################################################################
# ################################################################################################################################
