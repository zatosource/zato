# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_attr_table, event_link_table, event_table, get_audit_engine, \
    AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.audit_log.resubmit import get_resubmit_handler, load_event, Action_Reprocess, Action_Resend, \
    ResubmitException
from zato.common.hl7.resubmit import reprocess, resend, validate_payload
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-hl7-resubmit-server'

# The MLLP connections the tests deliver through
_outconn_name = 'hl7.test.outconn'
_channel_name = 'hl7.test.channel'

# The service the reprocess tests re-route to
_service_name = 'hl7.test.service'

# An admission - what an outbound event stores and a resend delivers again
_adt_a01 = (
    'MSH|^~\\&|HIS|GENERAL_HOSPITAL|LAB_SYSTEM|CENTRAL_LAB|20260115103000||ADT^A01^ADT_A01|MSG000001|P|2.9\r'
    'EVN|A01|20260115103000\r'
    'PID|1||445566^^^GENERAL_HOSPITAL^MR||SMITH^JOHN^A||19850315|M\r'
    'PV1|1|I|ICU^101^A\r'
)

# The same admission after an operator edit - a new control id and a new patient identifier
_adt_a01_edited = _adt_a01.replace('MSG000001', 'MSG000099').replace('445566', '999888')

# A positive acknowledgment for the admission above
_ack_aa = (
    'MSH|^~\\&|LAB_SYSTEM|CENTRAL_LAB|HIS|GENERAL_HOSPITAL|20260115103005||ACK^A01^ACK|ACK000001|P|2.9\r'
    'MSA|AA|MSG000001\r'
)

# A negative acknowledgment - the receiving application reported an error
_ack_ae = (
    'MSH|^~\\&|LAB_SYSTEM|CENTRAL_LAB|HIS|GENERAL_HOSPITAL|20260115103005||ACK^A01^ACK|ACK000002|P|2.9\r'
    'MSA|AE|MSG000001\r'
)

# An admission broken enough to fail validation - its PID has no patient name
_adt_a01_invalid = (
    'MSH|^~\\&|HIS|GENERAL_HOSPITAL|LAB_SYSTEM|CENTRAL_LAB|20260115103000||ADT^A01^ADT_A01|MSG000001|P|2.9\r'
    'PID|1||445566\r'
)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def audit_db_env(tmp_path:'os.PathLike') -> 'any_':
    """ Points the audit database at a per-test SQLite file so every test
    runs on its own isolated database.
    """
    database_path = os.path.join(str(tmp_path), 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = database_path

    yield database_path

    del os.environ[AuditLogCtx.Env_Type]
    del os.environ[AuditLogCtx.Env_Name]

# ################################################################################################################################
# ################################################################################################################################

def _seed_event(audit_log:'AuditLog', event_type:'str', object_name:'str', payload:'str') -> 'int':
    """ Stores one original event the way the live pipeline would have recorded it.
    """
    out = audit_log.insert(AuditSource.HL7, event_type, object_name,
        cid='cid-original', msg_id='MSG000001', outcome=AuditOutcome.Error,
        status='Connection timeout', data=dumps({'payload': payload}))

    return out

# ################################################################################################################################

def _get_event_row(event_id:'int') -> 'anydict':
    """ Returns one event row as a dict.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.where(event_table.c.id == event_id)

    with engine.connect() as connection:
        result = connection.execute(query)
        row = result.first()

    out = dict(row._mapping)
    return out

# ################################################################################################################################

def _get_attr_map(event_id:'int') -> 'anydict':
    """ Returns the attributes of one event as a dict of name to value.
    """
    engine = get_audit_engine()

    query = select(event_attr_table.c.name, event_attr_table.c.value)
    query = query.where(event_attr_table.c.event_id == event_id)

    out:'anydict' = {}

    with engine.connect() as connection:
        for row in connection.execute(query):
            out[row.name] = row.value

    return out

# ################################################################################################################################

def _get_parent_ids(child_event_id:'int') -> 'anylist':
    """ Returns the lineage parents of one child event.
    """
    engine = get_audit_engine()

    query = select(event_link_table.c.parent_event_id)
    query = query.where(event_link_table.c.child_event_id == child_event_id)
    query = query.order_by(event_link_table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(row[0])

    return out

# ################################################################################################################################

def _get_events(event_type:'str') -> 'anylist':
    """ Returns all events of one type, oldest first, each as a dict.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.where(event_table.c.event_type == event_type)
    query = query.order_by(event_table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(dict(row._mapping))

    return out

# ################################################################################################################################
# ################################################################################################################################

class _SendRecorder:
    """ A stand-in for an MLLP outgoing connection's send method, remembering
    what it was given and answering with a preconfigured acknowledgment.
    """
    def __init__(self, response:'any_'=None) -> 'None':
        self.response = response
        self.sent:'anylist' = []

    def __call__(self, payload:'str') -> 'any_':
        self.sent.append(payload)
        return self.response

# ################################################################################################################################

class _InvokeRecorder:
    """ A stand-in for the server's service invoker, remembering what was re-routed where.
    """
    def __init__(self) -> 'None':
        self.invoked:'anylist' = []

    def __call__(self, service_name:'str', payload:'str') -> 'None':
        self.invoked.append((service_name, payload))

# ################################################################################################################################
# ################################################################################################################################

class TestResend:

    def test_resend_delivers_stored_payload_and_records_the_ack(self) -> 'None':
        audit_log = AuditLog(_server_name)
        original_id = _seed_event(audit_log, AuditEvent.Message_Sent, _outconn_name, _adt_a01)

        send = _SendRecorder(response=_ack_aa)
        result = resend(load_event(original_id), send, audit_log, 'cid-resend-1')

        # The exact stored payload went out ..
        assert send.sent == [_adt_a01]

        # .. the result names the control id and the interpreted acknowledgment ..
        assert result.control_id == 'MSG000001'
        assert result.ack_status == 'AA'
        assert result.ack_outcome == AuditOutcome.OK

        # .. the attempt is its own message-sent event linked to the original ..
        row = _get_event_row(result.event_id)

        assert row['event_type'] == AuditEvent.Message_Sent
        assert row['object_name'] == _outconn_name
        assert row['cid'] == 'cid-resend-1'
        assert row['correl_id'] == 'cid-original'
        assert row['msg_id'] == 'MSG000001'
        assert row['outcome'] == AuditOutcome.OK
        assert loads(row['data']) == {'payload': _adt_a01}

        assert _get_parent_ids(result.event_id) == [original_id]

        # .. its attributes were extracted afresh, so the resend is searchable ..
        attr_map = _get_attr_map(result.event_id)

        assert attr_map['msg_type'] == 'ADT^A01'
        assert attr_map['mrn'] == '445566'
        assert attr_map['facility'] == 'GENERAL_HOSPITAL'

        # .. and the acknowledgment landed as its own event on the same cid.
        ack_events = _get_events(AuditEvent.Ack_Received)

        assert len(ack_events) == 1
        assert ack_events[0]['cid'] == 'cid-resend-1'
        assert ack_events[0]['msg_id'] == 'MSG000001'
        assert ack_events[0]['outcome'] == AuditOutcome.OK

# ################################################################################################################################

    def test_resend_with_an_edited_payload_is_searchable_by_the_edit(self) -> 'None':
        audit_log = AuditLog(_server_name)
        original_id = _seed_event(audit_log, AuditEvent.Message_Sent, _outconn_name, _adt_a01)

        send = _SendRecorder()
        result = resend(load_event(original_id), send, audit_log, 'cid-resend-2', payload=_adt_a01_edited)

        # The edited payload went out, not the stored one ..
        assert send.sent == [_adt_a01_edited]

        # .. and the new event carries what the edit says now, not what the original said.
        assert result.control_id == 'MSG000099'

        row = _get_event_row(result.event_id)

        assert row['msg_id'] == 'MSG000099'
        assert loads(row['data']) == {'payload': _adt_a01_edited}

        attr_map = _get_attr_map(result.event_id)
        assert attr_map['mrn'] == '999888'

# ################################################################################################################################

    def test_resend_without_an_ack_records_no_ack_event(self) -> 'None':
        audit_log = AuditLog(_server_name)
        original_id = _seed_event(audit_log, AuditEvent.Message_Sent, _outconn_name, _adt_a01)

        send = _SendRecorder()
        result = resend(load_event(original_id), send, audit_log, 'cid-resend-3')

        assert result.ack_status == ''
        assert result.ack_outcome == ''
        assert _get_events(AuditEvent.Ack_Received) == []

# ################################################################################################################################

    def test_resend_records_a_negative_ack_as_an_error(self) -> 'None':
        audit_log = AuditLog(_server_name)
        original_id = _seed_event(audit_log, AuditEvent.Message_Sent, _outconn_name, _adt_a01)

        send = _SendRecorder(response=_ack_ae)
        result = resend(load_event(original_id), send, audit_log, 'cid-resend-4')

        # The send itself worked - only the receiving application said no.
        assert result.ack_status == 'AE'
        assert result.ack_outcome == AuditOutcome.Error

        ack_events = _get_events(AuditEvent.Ack_Received)

        assert len(ack_events) == 1
        assert ack_events[0]['outcome'] == AuditOutcome.Error
        assert ack_events[0]['application_outcome'] == 'AE'

# ################################################################################################################################

    def test_a_failed_resend_is_recorded_before_it_propagates(self) -> 'None':
        audit_log = AuditLog(_server_name)
        original_id = _seed_event(audit_log, AuditEvent.Message_Sent, _outconn_name, _adt_a01)

        def failing_send(payload:'str') -> 'None':
            raise ValueError('The receiving system is down')

        with pytest.raises(ValueError):
            _ = resend(load_event(original_id), failing_send, audit_log, 'cid-resend-5')

        # The delivery history has no holes - the failed attempt is its own error event.
        sent_events = _get_events(AuditEvent.Message_Sent)

        assert len(sent_events) == 2
        assert sent_events[1]['cid'] == 'cid-resend-5'
        assert sent_events[1]['outcome'] == AuditOutcome.Error
        assert sent_events[1]['status'] == 'The receiving system is down'

# ################################################################################################################################

    def test_only_outbound_events_can_be_resent(self) -> 'None':
        audit_log = AuditLog(_server_name)
        inbound_id = _seed_event(audit_log, AuditEvent.Message_Received, _channel_name, _adt_a01)

        send = _SendRecorder()

        with pytest.raises(ResubmitException):
            _ = resend(load_event(inbound_id), send, audit_log, 'cid-resend-6')

        assert send.sent == []

# ################################################################################################################################
# ################################################################################################################################

class TestReprocess:

    def test_reprocess_re_routes_the_stored_payload_to_the_service(self) -> 'None':
        audit_log = AuditLog(_server_name)
        original_id = _seed_event(audit_log, AuditEvent.Message_Received, _channel_name, _adt_a01)

        invoke = _InvokeRecorder()
        result = reprocess(load_event(original_id), _service_name, invoke, audit_log, 'cid-reprocess-1')

        # The channel's service received the message the way a live delivery would arrive ..
        assert invoke.invoked == [(_service_name, _adt_a01)]

        # .. and the result names what happened.
        assert result.control_id == 'MSG000001'
        assert result.service_name == _service_name

        # The attempt is its own message-received event linked to the original.
        row = _get_event_row(result.event_id)

        assert row['event_type'] == AuditEvent.Message_Received
        assert row['object_name'] == _channel_name
        assert row['cid'] == 'cid-reprocess-1'
        assert row['correl_id'] == 'cid-original'
        assert row['outcome'] == AuditOutcome.OK

        assert _get_parent_ids(result.event_id) == [original_id]

        attr_map = _get_attr_map(result.event_id)
        assert attr_map['mrn'] == '445566'

# ################################################################################################################################

    def test_reprocess_with_an_edited_payload(self) -> 'None':
        audit_log = AuditLog(_server_name)
        original_id = _seed_event(audit_log, AuditEvent.Message_Received, _channel_name, _adt_a01)

        invoke = _InvokeRecorder()
        result = reprocess(load_event(original_id), _service_name, invoke, audit_log, 'cid-reprocess-2',
            payload=_adt_a01_edited)

        assert invoke.invoked == [(_service_name, _adt_a01_edited)]
        assert result.control_id == 'MSG000099'

        attr_map = _get_attr_map(result.event_id)
        assert attr_map['mrn'] == '999888'

# ################################################################################################################################

    def test_only_inbound_events_can_be_reprocessed(self) -> 'None':
        audit_log = AuditLog(_server_name)
        outbound_id = _seed_event(audit_log, AuditEvent.Message_Sent, _outconn_name, _adt_a01)

        invoke = _InvokeRecorder()

        with pytest.raises(ResubmitException):
            _ = reprocess(load_event(outbound_id), _service_name, invoke, audit_log, 'cid-reprocess-3')

        assert invoke.invoked == []

# ################################################################################################################################
# ################################################################################################################################

class TestValidate:

    def test_a_valid_payload_passes(self) -> 'None':
        result = validate_payload(_adt_a01)

        assert result.is_valid is True
        assert list(result.errors) == []

# ################################################################################################################################

    def test_a_broken_payload_reports_its_errors(self) -> 'None':
        result = validate_payload(_adt_a01_invalid)

        assert result.is_valid is False
        assert len(result.errors) > 0

# ################################################################################################################################
# ################################################################################################################################

class TestRegistry:

    def test_the_hl7_handlers_are_registered(self) -> 'None':

        # The service layer finds the HL7 semantics through the shared registry.
        assert get_resubmit_handler(AuditSource.HL7, Action_Resend) is resend
        assert get_resubmit_handler(AuditSource.HL7, Action_Reprocess) is reprocess

# ################################################################################################################################
# ################################################################################################################################
