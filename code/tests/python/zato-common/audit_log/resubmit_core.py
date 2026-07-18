# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import select

# Zato
from common import delete_all_events
from zato.common.audit_log.api import event_link_table, event_table, get_audit_engine, \
    AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.dedup import acquire_dedup_key, build_dedup_key, complete_dedup_key, get_in_doubt, \
    release_dedup_key
from zato.common.audit_log.resubmit import bulk_repair, find_event_ids, get_resubmit_handler, get_stored_payload, \
    load_event, register_resubmit_handler, require_event_type, resend_hop, Action_Reprocess, Action_Resend, \
    RepairFilter, ResubmitException, Row_Error, Row_Resubmitted, Row_Would_Resubmit
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-audit-log-server'

# The connection the per-hop resend checks deliver through
_hop_connection_name = 'audit.test.core.hop'

# The connection the bulk repair checks deliver through
_bulk_connection_name = 'audit.test.core.bulk'

# ################################################################################################################################
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

def _run_load_event_checks(audit_log:'AuditLog') -> 'None':
    """ Confirms a stored event is read back whole, and that the ways an event
    can be unresubmittable - missing, non-JSON, payloadless - are each reported.
    """
    event_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, 'audit.test.core.load',
        cid='cid-core-load-1', msg_id='msg-core-load-1', outcome=AuditOutcome.OK,
        data=dumps({'payload': 'the-stored-payload'}))

    event = load_event(event_id)

    assert event.id == event_id
    assert event.cid == 'cid-core-load-1'
    assert event.source == AuditSource.REST_Outgoing
    assert event.event_type == AuditEvent.Request_Sent
    assert event.object_name == 'audit.test.core.load'
    assert event.msg_id == 'msg-core-load-1'
    assert get_stored_payload(event) == 'the-stored-payload'

    # The type gate lets the right type through and names the wrong one ..
    require_event_type(event, AuditEvent.Request_Sent, 'resent per hop')

    try:
        require_event_type(event, AuditEvent.Message_Received, 'reprocessed')
    except ResubmitException as e:
        assert 'reprocessed' in str(e)
        assert AuditEvent.Request_Sent in str(e)
    else:
        raise Exception('A type mismatch was expected to be rejected')

    # .. an event that does not exist cannot be resubmitted ..
    try:
        _ = load_event(event_id + 1_000_000)
    except ResubmitException as e:
        assert 'was not found' in str(e)
    else:
        raise Exception('A missing event was expected to be rejected')

    # .. an event without JSON data cannot be resubmitted ..
    raw_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, 'audit.test.core.load',
        cid='cid-core-load-2', data='this is not JSON')

    try:
        _ = load_event(raw_id)
    except ResubmitException as e:
        assert 'does not carry JSON data' in str(e)
    else:
        raise Exception('Non-JSON data was expected to be rejected')

    # .. and an event whose data has no payload inside cannot be resubmitted either.
    payloadless_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, 'audit.test.core.load',
        cid='cid-core-load-3', data=dumps({'note': 'a reconciliation-only entry'}))

    payloadless = load_event(payloadless_id)

    try:
        _ = get_stored_payload(payloadless)
    except ResubmitException as e:
        assert 'does not carry a payload' in str(e)
    else:
        raise Exception('A payloadless event was expected to be rejected')

# ################################################################################################################################

def _run_registry_checks() -> 'None':
    """ Confirms the handler registry hands back what a source registered
    and rejects a lookup nothing was registered for.
    """
    def handler() -> 'None':
        pass

    register_resubmit_handler('audit-test-core', Action_Resend, handler)

    assert get_resubmit_handler('audit-test-core', Action_Resend) is handler

    try:
        _ = get_resubmit_handler('audit-test-core', Action_Reprocess)
    except ResubmitException as e:
        assert Action_Reprocess in str(e)
        assert 'audit-test-core' in str(e)
    else:
        raise Exception('An unregistered handler was expected to be rejected')

# ################################################################################################################################

def _run_hop_resend_checks(audit_log:'AuditLog') -> 'None':
    """ Confirms a per-hop resend delivers the exact stored payload, records the attempt
    as its own event linked to the original, and records a failed attempt too.
    """
    original_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _hop_connection_name,
        cid='cid-core-hop-orig', msg_id='msg-core-hop-1', outcome=AuditOutcome.Error,
        status='Connection timeout', data=dumps({'payload': 'hop-payload'}))

    sent:'anylist' = []

    def send(payload:'str') -> 'str':
        sent.append(payload)
        return 'hop-response'

    result = resend_hop(load_event(original_id), send, audit_log, 'cid-core-hop-new')

    # The exact stored payload went out and the target's answer came back ..
    assert sent == ['hop-payload']
    assert result.response == 'hop-response'

    # .. the attempt is its own outgoing event linked to the original ..
    row = _get_event_row(result.event_id)

    assert row['event_type'] == AuditEvent.Request_Sent
    assert row['object_name'] == _hop_connection_name
    assert row['cid'] == 'cid-core-hop-new'
    assert row['correl_id'] == 'cid-core-hop-orig'
    assert row['msg_id'] == 'msg-core-hop-1'
    assert row['outcome'] == AuditOutcome.OK
    assert loads(row['data']) == {'payload': 'hop-payload'}

    assert _get_parent_ids(result.event_id) == [original_id]

    # .. only outgoing events can be resent per hop ..
    inbound_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Message_Received, _hop_connection_name,
        cid='cid-core-hop-inbound', data=dumps({'payload': 'inbound-payload'}))

    try:
        _ = resend_hop(load_event(inbound_id), send, audit_log, 'cid-core-hop-rejected')
    except ResubmitException:
        pass
    else:
        raise Exception('An inbound event was expected to be rejected')

    # .. and a failed attempt is recorded as its own error event before the caller learns about it.
    def failing_send(payload:'str') -> 'str':
        raise ValueError('The hop target is down')

    try:
        _ = resend_hop(load_event(original_id), failing_send, audit_log, 'cid-core-hop-fail')
    except ValueError:
        pass
    else:
        raise Exception('A failed send was expected to propagate')

    engine = get_audit_engine()

    query = select(event_table)
    query = query.where(event_table.c.cid == 'cid-core-hop-fail')

    with engine.connect() as connection:
        result_rows = connection.execute(query).fetchall()

    assert len(result_rows) == 1

    error_row = dict(result_rows[0]._mapping)
    assert error_row['outcome'] == AuditOutcome.Error
    assert error_row['status'] == 'The hop target is down'
    assert error_row['correl_id'] == 'cid-core-hop-orig'

# ################################################################################################################################

def _run_dedup_checks() -> 'None':
    """ Confirms the dedup ledger - deterministic keys, atomic single acquisition,
    in-doubt detection of interrupted resubmits, and release making a key acquirable again.
    """
    engine = get_audit_engine()

    # The same operation always hashes to the same key, a different one never does ..
    first_key = build_dedup_key(Action_Resend, 123, 'payload-a')

    assert first_key == build_dedup_key(Action_Resend, 123, 'payload-a')
    assert first_key != build_dedup_key(Action_Resend, 123, 'payload-b')
    assert first_key != build_dedup_key(Action_Resend, 124, 'payload-a')
    assert first_key != build_dedup_key(Action_Reprocess, 123, 'payload-a')

    # .. a key is claimed exactly once ..
    assert acquire_dedup_key(engine, first_key, 'cid-core-dedup-1', Action_Resend) is True
    assert acquire_dedup_key(engine, first_key, 'cid-core-dedup-2', Action_Resend) is False

    # .. a claimed key without an outcome is an interrupted resubmit - in doubt ..
    in_doubt = get_in_doubt(engine)

    assert len(in_doubt) == 1
    assert in_doubt[0]['dedup_key'] == first_key
    assert in_doubt[0]['cid'] == 'cid-core-dedup-1'
    assert in_doubt[0]['action'] == Action_Resend

    # .. recording the outcome takes it out of doubt while keeping it claimed ..
    complete_dedup_key(engine, first_key, AuditOutcome.OK)

    assert get_in_doubt(engine) == []
    assert acquire_dedup_key(engine, first_key, 'cid-core-dedup-3', Action_Resend) is False

    # .. and a released key is acquirable again - what a failed resubmit does.
    second_key = build_dedup_key(Action_Resend, 125, 'payload-c')

    assert acquire_dedup_key(engine, second_key, 'cid-core-dedup-4', Action_Resend) is True

    release_dedup_key(engine, second_key)

    assert acquire_dedup_key(engine, second_key, 'cid-core-dedup-5', Action_Resend) is True

    # Completed so the bulk repair checks later in the scenario start with nothing in doubt
    complete_dedup_key(engine, second_key, AuditOutcome.OK)

# ################################################################################################################################

def _run_bulk_repair_checks(audit_log:'AuditLog') -> 'None':
    """ Confirms bulk repair end to end - server-side filtering in id order, the dry run,
    per-row outcomes with one failure not aborting the rest, the payload transform,
    dedup preventing double-apply, a failed row staying retryable, and the one
    audit event recording the whole operation.
    """
    engine = get_audit_engine()

    payloads = ['bulk-one', 'bulk-two-bad', 'bulk-three']
    seeded_ids:'anylist' = []

    for index, payload in enumerate(payloads):
        event_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _bulk_connection_name,
            cid=f'cid-core-bulk-{index}', outcome=AuditOutcome.Error, status='Connection timeout',
            data=dumps({'payload': payload}))
        seeded_ids.append(event_id)

    repair_filter = RepairFilter()
    repair_filter.source = AuditSource.REST_Outgoing
    repair_filter.event_type = AuditEvent.Request_Sent
    repair_filter.object_name = _bulk_connection_name
    repair_filter.outcome = AuditOutcome.Error

    # The filter matches the seeded events in id order ..
    assert find_event_ids(repair_filter) == seeded_ids

    resubmitted:'anylist' = []

    def resubmit_one(event:'anydict', payload:'str') -> 'None':

        # The marker arrives uppercased because the repair transform ran first
        if 'BAD' in payload:
            raise ValueError('This payload cannot be delivered')

        resubmitted.append(payload)

    # .. a dry run reports every row without sending anything ..
    dry_result = bulk_repair(repair_filter, resubmit_one, audit_log, 'cid-core-bulk-dry',
        transform=str.upper, dry_run=True)

    assert dry_result.is_dry_run is True
    assert dry_result.total == 3
    assert dry_result.resubmitted_count == 0
    assert dry_result.bulk_event_id is None
    assert resubmitted == []

    for row in dry_result.rows:
        assert row['result'] == Row_Would_Resubmit

    # .. the real run transforms and delivers, and the one failing row does not abort the rest ..
    first_result = bulk_repair(repair_filter, resubmit_one, audit_log, 'cid-core-bulk-first',
        transform=str.upper)

    assert first_result.total == 3
    assert first_result.resubmitted_count == 2
    assert first_result.error_count == 1
    assert first_result.duplicate_count == 0
    assert resubmitted == ['BULK-ONE', 'BULK-THREE']

    results_by_id = {row['event_id']: row['result'] for row in first_result.rows}

    assert results_by_id[seeded_ids[0]] == Row_Resubmitted
    assert results_by_id[seeded_ids[1]] == Row_Error
    assert results_by_id[seeded_ids[2]] == Row_Resubmitted

    # .. the whole operation is one audit event with the per-row outcomes inside ..
    bulk_row = _get_event_row(first_result.bulk_event_id)

    assert bulk_row['event_type'] == AuditEvent.Bulk_Repair
    assert bulk_row['outcome'] == AuditOutcome.Error
    assert loads(bulk_row['data']) == {'rows': first_result.rows}

    # .. rerunning catches the already-applied rows while the failed one stays retryable ..
    def fixed_resubmit_one(event:'anydict', payload:'str') -> 'None':
        resubmitted.append(payload)

    second_result = bulk_repair(repair_filter, fixed_resubmit_one, audit_log, 'cid-core-bulk-second',
        transform=str.upper)

    assert second_result.resubmitted_count == 1
    assert second_result.duplicate_count == 2
    assert second_result.error_count == 0
    assert resubmitted == ['BULK-ONE', 'BULK-THREE', 'BULK-TWO-BAD']

    bulk_row = _get_event_row(second_result.bulk_event_id)
    assert bulk_row['outcome'] == AuditOutcome.OK

    # .. a third identical run applies nothing at all ..
    third_result = bulk_repair(repair_filter, fixed_resubmit_one, audit_log, 'cid-core-bulk-third',
        transform=str.upper)

    assert third_result.resubmitted_count == 0
    assert third_result.duplicate_count == 3
    assert len(resubmitted) == 3

    # .. and nothing is left in doubt - every claimed key recorded its outcome.
    assert get_in_doubt(engine) == []

# ################################################################################################################################
# ################################################################################################################################

def run_resubmit_core_scenario() -> 'None':
    """ The shared resubmit core scenario every backend must pass: loading stored events
    back with every rejection path, the per-source handler registry, the per-hop resend,
    the dedup ledger and bulk repair with dry runs and double-apply prevention.
    """
    delete_all_events()

    audit_log = AuditLog(_server_name)

    _run_load_event_checks(audit_log)
    _run_registry_checks()
    _run_hop_resend_checks(audit_log)
    _run_dedup_checks()
    _run_bulk_repair_checks(audit_log)

# ################################################################################################################################
# ################################################################################################################################
