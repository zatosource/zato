# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import AuditEvent, event_table, ModuleCtx as AuditLogCtx
from zato.common.b2b.common.business_log import BusinessLog
from zato.common.b2b.common.business_state import BusinessState
from zato.common.b2b.common.clock import ManualClock
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.b2b.common.outcome import FailureCause, FinalState, Outcome, SignalKind
from zato.common.b2b.common.send_log import SendLog
from zato.common.test.b2b_write_path import new_business_message, new_memory_engine, new_sent_message, receipt_outcome, \
    Server, Source, Start_Time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pytest import MonkeyPatch
    from zato.common.typing_ import strlist
    MonkeyPatch = MonkeyPatch
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The error code of an exchange that ran out of retries, and that of an error message from the partner.
_delivery_failure = 'DeliveryFailure'
_value_not_recognized = 'ValueNotRecognized'

# Each cause of the failure of a delivery, with the detail it is recorded with and the error code the exchange ends with.
_causes = [
    (FailureCause.No_Answer, '', _delivery_failure),
    (FailureCause.HTTP_Error, '503', _delivery_failure),
    (FailureCause.Protocol_Error, _value_not_recognized, _value_not_recognized),
]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def writer(monkeypatch:'MonkeyPatch') -> 'GroupCommitWriter':
    """ A writer that commits each write as it is submitted, into an in-memory database.
    """
    monkeypatch.setenv(AuditLogCtx.Env_Enabled, 'True')

    out = GroupCommitWriter(new_memory_engine(), interval_ms=0, is_started=False)
    return out

# ################################################################################################################################

def _failed_outcome(error_code:'str', failure_cause:'str', failure_detail:'str') -> 'Outcome':
    """ Returns the outcome of an exchange that ended without a delivery.
    """
    out = Outcome()
    out.signal_kind = SignalKind.Error
    out.error_code = error_code
    out.final_state = FinalState.Failed
    out.failure_cause = failure_cause
    out.failure_detail = failure_detail

    return out

# ################################################################################################################################

def _event_types(writer:'GroupCommitWriter', message_id:'str') -> 'strlist':
    """ Returns the type of each audit event of a message, in the order they were stored.
    """
    query = select(event_table.c.event_type).where(event_table.c.msg_id == message_id).order_by(event_table.c.id)

    with writer.engine.connect() as connection:
        out = list(connection.execute(query).scalars())

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDeliveryFailed:
    """ A business message whose exchange ends without a delivery ends its business transaction
    with the cause of the last delivery.
    """

    @pytest.mark.parametrize(('failure_cause', 'failure_detail', 'error_code'), _causes)
    def test_cause(self, writer:'GroupCommitWriter', failure_cause:'str', failure_detail:'str', error_code:'str') -> 'None':
        business_log = BusinessLog(Source, Server, writer)
        send_log = SendLog(Source, Server, ManualClock(Start_Time), writer, business_log)

        sent = new_sent_message('message-1')
        business = new_business_message('message-1', response_seconds=60)

        send_log.record_first_attempt(sent, business)
        send_log.record_attempt_failure(sent, failure_cause, failure_detail)

        held = send_log.get('message-1')
        outcome = _failed_outcome(error_code, held.outcome.failure_cause, held.outcome.failure_detail)
        send_log.record_completion(sent, outcome)

        assert _event_types(writer, 'message-1') == [
            AuditEvent.Message_Sent,
            AuditEvent.Message_Completed,
            AuditEvent.Business_Delivery_Failed,
        ]

        # The transaction ended, so it is read from the audit log ..
        assert business_log.awaiting(10) == []

        stored = business_log.read('message-1')

        assert stored is not None
        assert stored.state == BusinessState.Delivery_Failed
        assert stored.failure_cause == failure_cause
        assert stored.failure_detail == failure_detail

        # .. and the exchange keeps the cause with its outcome.
        completed = send_log.get('message-1')

        assert completed.outcome.failure_cause == failure_cause
        assert completed.outcome.failure_detail == failure_detail

    def test_not_recovered(self, writer:'GroupCommitWriter') -> 'None':
        business_log = BusinessLog(Source, Server, writer)
        send_log = SendLog(Source, Server, ManualClock(Start_Time), writer, business_log)

        sent = new_sent_message('message-1')
        business = new_business_message('message-1', receipt_seconds=30)

        send_log.record_first_attempt(sent, business)
        send_log.record_completion(sent, _failed_outcome(_delivery_failure, FailureCause.No_Answer, ''))

        restarted = BusinessLog(Source, Server, writer)

        assert restarted.recover() == 0
        assert restarted.awaiting(10) == []

        stored = restarted.read('message-1')

        assert stored is not None
        assert stored.state == BusinessState.Delivery_Failed
        assert stored.failure_cause == FailureCause.No_Answer

    def test_receipted_message(self, writer:'GroupCommitWriter') -> 'None':
        business_log = BusinessLog(Source, Server, writer)
        send_log = SendLog(Source, Server, ManualClock(Start_Time), writer, business_log)

        sent = new_sent_message('message-1')
        business = new_business_message('message-1', response_seconds=60)

        send_log.record_first_attempt(sent, business)
        business_log.record_reply(business, BusinessState.Receipted, 'receipt-1', [])
        send_log.record_completion(sent, _failed_outcome(_delivery_failure, FailureCause.No_Answer, ''))

        stored = business_log.read('message-1')

        assert stored is not None
        assert stored.state == BusinessState.Receipted
        assert stored.failure_cause == ''
        assert AuditEvent.Business_Delivery_Failed not in _event_types(writer, 'message-1')

    def test_delivered_message(self, writer:'GroupCommitWriter') -> 'None':
        business_log = BusinessLog(Source, Server, writer)
        send_log = SendLog(Source, Server, ManualClock(Start_Time), writer, business_log)

        sent = new_sent_message('message-1')
        business = new_business_message('message-1', response_seconds=60)

        send_log.record_first_attempt(sent, business)
        send_log.record_attempt_failure(sent, FailureCause.HTTP_Error, '503')
        send_log.record_completion(sent, receipt_outcome())

        stored = business_log.read('message-1')

        assert stored is not None
        assert stored.state == BusinessState.Sent

    def test_message_without_transaction(self, writer:'GroupCommitWriter') -> 'None':
        business_log = BusinessLog(Source, Server, writer)
        send_log = SendLog(Source, Server, ManualClock(Start_Time), writer, business_log)

        sent = new_sent_message('message-1')

        send_log.record_first_attempt(sent)
        send_log.record_completion(sent, _failed_outcome(_delivery_failure, FailureCause.No_Answer, ''))

        assert business_log.read('message-1') is None
        assert _event_types(writer, 'message-1') == [AuditEvent.Message_Sent, AuditEvent.Message_Completed]

# ################################################################################################################################
# ################################################################################################################################
