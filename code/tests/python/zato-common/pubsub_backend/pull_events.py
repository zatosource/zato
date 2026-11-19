# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The audit events that record the messages that pulls hand out, column by column, with the pulls that record none
# and the events that the export receives.

# stdlib
import os
from time import sleep

# Zato
from common import delete_all_rows, delete_audit_rows, get_event_ids, get_received_event_rows
from zato.common.audit_log.api import event_attr_table, event_body_table, event_link_table, AuditEvent, AuditOutcome, \
    AuditSource
from zato.common.audit_log.export.api import set_audit_export
from zato.common.config_db import Env_Audit_Log_Enabled
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.config import ModuleCtx
from zato.common.test.audit_log_ import new_test_audit_log, ModuleCtx as AuditModuleCtx, RecordingAuditExport
from zato.common.util.time_ import parse_utc, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

Env_Pull_Lease_Seconds = ModuleCtx.Env_Pull_Lease_Seconds

# The topics and subscribers of the scenario
_topic_events   = 'pubsub.backend.test.pull-events.events'
_topic_off      = 'pubsub.backend.test.pull-events.off'
_topic_switch   = 'pubsub.backend.test.pull-events.switch'
_topic_export   = 'pubsub.backend.test.pull-events.export'

_sub_key_events = 'zpsk.test.pull-events.events'
_sub_key_off    = 'zpsk.test.pull-events.off'
_sub_key_switch = 'zpsk.test.pull-events.switch'
_sub_key_export = 'zpsk.test.pull-events.export'

# The values of the published messages
_cid = 'cid-pull-events-1'
_correl_id = 'correl-pull-events-1'
_ext_client_id = 'client-maria-johnson'
_priority = 7

# A payload whose length in characters differs from its length in bytes
_payload_non_ascii = 'Zamówienie dla Marii Johnson – 5,50 € Jürgen'
_payload_non_ascii_size = 44

# A payload of ASCII text
_payload_ascii = 'Order ORD-0042 for Maria Johnson'

# The value of the switch that turns the audit log off
_audit_log_disabled = 'false'

# ################################################################################################################################
# ################################################################################################################################

def _new_backend() -> 'SQLPubSubBackend':
    """ Returns a backend with an audit log of its own, starting from empty tables.
    """
    delete_all_rows()
    delete_audit_rows()

    out = SQLPubSubBackend(audit_log=new_test_audit_log())
    return out

# ################################################################################################################################

def _assert_event(event:'anydict', message:'anydict', cid:'str', pull_start:'any_', pull_end:'any_') -> 'None':
    """ The event of one message that a pull handed out records it with these values.
    """
    expected:'anydict' = {
        'cid': cid,
        'source': AuditSource.PubSub,
        'event_type': AuditEvent.Received,
        'object_name': message['topic_name'],
        'msg_id': message['msg_id'],
        'correl_id': '',
        'ext_client_id': '',
        'pub_time': parse_utc(message['pub_time_iso']),
        'server_name': AuditModuleCtx.Server_Name,
        'endpoint': '',
        'sub_key': _sub_key_events,
        'size': len(message['data']),
        'priority': message['priority'],
        'outcome': AuditOutcome.OK,
        'application_outcome': '',
        'classification': '',
        'status': '',
        'duration_ms': 0,
        'internal_data': '',
        'data': message['data'],
    }

    for key, value in expected.items():
        assert event[key] == value, (key, event[key], value)

    assert pull_start <= event['event_time'] <= pull_end, (pull_start, event['event_time'], pull_end)

# ################################################################################################################################

def _run_event_values(backend:'SQLPubSubBackend') -> 'None':
    """ Each message of a pull has one event with the values of the message and of its subscriber,
    and none of the companion rows of other events.
    """
    backend.subscribe(_sub_key_events, _topic_events)

    _ = backend.publish(_topic_events, _payload_non_ascii, priority=_priority, cid=_cid, correl_id=_correl_id,
        ext_client_id=_ext_client_id)
    _ = backend.publish(_topic_events, _payload_ascii)

    pull_start = utcnow()
    messages = backend.pull_messages(_sub_key_events)
    pull_end = utcnow()

    events = get_received_event_rows(_topic_events)

    assert len(messages) == 2, messages
    assert len(events) == 2, events

    # The message with a cid has an event with its cid, the next sequence after its publication,
    # .. and a size in characters, not in bytes ..
    _assert_event(events[0], messages[0], _cid, pull_start, pull_end)

    assert events[0]['size'] == _payload_non_ascii_size
    assert events[0]['priority'] == _priority
    assert events[0]['cid_sequence'] == 2

    # .. and the message without one has an event with no cid and no sequence.
    _assert_event(events[1], messages[1], '', pull_start, pull_end)

    assert events[1]['cid_sequence'] == 0

    # No event of a pull has a row in any companion table.
    event_ids = {events[0]['id'], events[1]['id']}

    companion_columns = (
        event_attr_table.c.event_id,
        event_body_table.c.event_id,
        event_link_table.c.child_event_id,
        event_link_table.c.parent_event_id,
    )

    for column in companion_columns:
        companion_ids = get_event_ids(column)
        assert not event_ids & companion_ids, column

# ################################################################################################################################

def _run_repeated_copy(backend:'SQLPubSubBackend') -> 'None':
    """ A copy handed out again after its lease ran out has an event of its own, with the next sequence of its cid.
    """
    backend.subscribe(_sub_key_events, _topic_events)

    _ = backend.publish(_topic_events, _payload_ascii, cid=_cid)

    # A lease of zero seconds runs out as soon as the clock moves on ..
    os.environ[Env_Pull_Lease_Seconds] = '0'

    try:
        first = backend.pull_messages(_sub_key_events)
        sleep(0.01)
        second = backend.pull_messages(_sub_key_events)
    finally:
        del os.environ[Env_Pull_Lease_Seconds]

    assert len(first) == 1
    assert len(second) == 1

    # .. so each pull recorded its copy, the second one with the sequence that follows the first.
    events = get_received_event_rows(_topic_events)

    assert len(events) == 2, events
    assert events[0]['msg_id'] == first[0]['msg_id']
    assert events[1]['msg_id'] == second[0]['msg_id']
    assert events[0]['cid'] == _cid
    assert events[1]['cid'] == _cid
    assert events[1]['cid_sequence'] == events[0]['cid_sequence'] + 1

# ################################################################################################################################

def _run_topic_audit_off(backend:'SQLPubSubBackend') -> 'None':
    """ A pull from a topic whose audit log is off records nothing.
    """
    backend.set_topic_audit_flag(_topic_off, False)
    backend.subscribe(_sub_key_off, _topic_off)

    _ = backend.publish(_topic_off, _payload_ascii)

    messages = backend.pull_messages(_sub_key_off)

    assert len(messages) == 1
    assert get_received_event_rows(_topic_off) == []

# ################################################################################################################################

def _run_audit_log_switched_off(backend:'SQLPubSubBackend') -> 'None':
    """ A pull while the audit log is switched off records nothing.
    """
    backend.subscribe(_sub_key_switch, _topic_switch)

    _ = backend.publish(_topic_switch, _payload_ascii)

    old_value = os.environ.get(Env_Audit_Log_Enabled)
    os.environ[Env_Audit_Log_Enabled] = _audit_log_disabled

    try:
        messages = backend.pull_messages(_sub_key_switch)
    finally:
        if old_value is None:
            del os.environ[Env_Audit_Log_Enabled]
        else:
            os.environ[Env_Audit_Log_Enabled] = old_value

    assert len(messages) == 1
    assert get_received_event_rows(_topic_switch) == []

# ################################################################################################################################

def _run_empty_pull(backend:'SQLPubSubBackend') -> 'None':
    """ A pull that leases nothing records nothing.
    """
    backend.subscribe(_sub_key_events, _topic_events)

    messages = backend.pull_messages(_sub_key_events)

    assert messages == []
    assert get_received_event_rows(_topic_events) == []

# ################################################################################################################################

def _get_received_exports(export:'RecordingAuditExport') -> 'anylist':
    """ Returns the events of pulls that the export received, in the order it received them.
    """
    out:'anylist' = []

    for event in export.events:
        if event.values['event_type'] == AuditEvent.Received:
            out.append(event)

    return out

# ################################################################################################################################

def _run_export(backend:'SQLPubSubBackend') -> 'None':
    """ The export receives each event of a pull with its id, and with its payload when its topic exports payloads.
    """
    backend.set_topic_payload_flag(_topic_export, True)
    backend.subscribe(_sub_key_export, _topic_export)

    _ = backend.publish(_topic_export, _payload_non_ascii)
    _ = backend.publish(_topic_export, _payload_ascii)

    export = RecordingAuditExport()
    set_audit_export(export)

    try:
        messages = backend.pull_messages(_sub_key_export)
    finally:
        set_audit_export(None)

    events = get_received_event_rows(_topic_export)
    exported = _get_received_exports(export)

    assert len(messages) == 2, messages
    assert len(events) == 2, events
    assert len(exported) == 2, exported

    for message, event, exported_event in zip(messages, events, exported):
        assert exported_event.event_id == event['id'], (exported_event.event_id, event['id'])
        assert exported_event.is_export_payload_active
        assert exported_event.values['msg_id'] == message['msg_id']
        assert exported_event.values['data'] == message['data']

# ################################################################################################################################

def run_pull_events_scenario() -> 'None':
    """ The audit events of the messages that pulls hand out, each part starting from empty tables.
    """
    _run_event_values(_new_backend())
    _run_repeated_copy(_new_backend())
    _run_topic_audit_off(_new_backend())
    _run_audit_log_switched_off(_new_backend())
    _run_empty_pull(_new_backend())
    _run_export(_new_backend())

# ################################################################################################################################
# ################################################################################################################################
