# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The source-agnostic core of every resubmit - loading a stored event back, the registry
# of per-source handlers, the per-hop resend over outgoing events, and bulk repair.
# Each source contributes its own resend and reprocess semantics on top of this module,
# the way zato.common.as2.resubmit and zato.common.hl7.resubmit do.

from __future__ import annotations

# stdlib
from dataclasses import dataclass
from traceback import format_exc

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome, event_table, get_audit_engine
from zato.common.audit_log.dedup import acquire_dedup_key, build_dedup_key, complete_dedup_key, release_dedup_key
from zato.common.json_internal import dumps, loads
from zato.common.typing_ import dict_field, list_field

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import any_, anydict, anylist, callable_, intlist, intnone, stranydict, strnone
    any_ = any_
    anydict = anydict
    anylist = anylist
    AuditLog = AuditLog
    callable_ = callable_
    intlist = intlist
    intnone = intnone
    stranydict = stranydict
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# The two directions every source's handlers come in.
Action_Resend    = 'resend'
Action_Reprocess = 'reprocess'

# What one row of a bulk operation ended up as.
Row_Resubmitted     = 'resubmitted'
Row_Would_Resubmit  = 'would-resubmit'
Row_Duplicate       = 'duplicate'
Row_Error           = 'error'

# ################################################################################################################################
# ################################################################################################################################

class ResubmitException(Exception):
    """ Raised when a stored event cannot be resubmitted.
    """

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class StoredEvent:
    """ One audit event read back for resubmission, with its JSON data already parsed.
    """
    id: int = 0
    cid: str = ''
    source: str = ''
    event_type: str = ''
    object_name: str = ''
    msg_id: str = ''

    # What the event recorded - this is where the stored payload lives.
    details: 'stranydict' = dict_field()

# ################################################################################################################################
# ################################################################################################################################

def load_event(event_id:'int') -> 'StoredEvent':
    """ Reads one audit event by its id, along with its parsed JSON data.
    """
    statement = select(
        event_table.c.id,
        event_table.c.cid,
        event_table.c.source,
        event_table.c.event_type,
        event_table.c.object_name,
        event_table.c.msg_id,
        event_table.c.data,
    ).where(event_table.c.id == event_id)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        row = result.first()

    # There is nothing to resubmit if the event does not exist, e.g. retention already deleted it.
    if row is None:
        raise ResubmitException(f'Audit event `{event_id}` was not found')

    event_id, cid, source, event_type, object_name, msg_id, data = row

    # The data of a resubmittable event is always a JSON document with the payload inside.
    try:
        details = loads(data)
    except ValueError:
        raise ResubmitException(f'Audit event `{event_id}` does not carry JSON data')

    out = StoredEvent()
    out.id = event_id
    out.cid = cid
    out.source = source
    out.event_type = event_type
    out.object_name = object_name
    out.msg_id = msg_id
    out.details = details

    return out

# ################################################################################################################################

def get_stored_payload(event:'StoredEvent') -> 'str':
    """ Returns the payload stored with an event - an event recorded without one,
    e.g. a reconciliation-only entry, cannot be resubmitted.
    """
    if payload := event.details.get('payload'):
        out = payload
    else:
        raise ResubmitException(f'Audit event `{event.id}` does not carry a payload to resubmit')

    return out

# ################################################################################################################################

def require_event_type(event:'StoredEvent', expected:'str', action:'str') -> 'None':
    """ Confirms an event is of the one type an action applies to.
    """
    if event.event_type != expected:
        raise ResubmitException(f'Only `{expected}` events can be {action}, not `{event.event_type}`')

# ################################################################################################################################
# ################################################################################################################################

# Per-source handlers keyed by (source, action) - how the service layer finds
# what resend or reprocess means for each source. A handler is an opaque callable,
# its signature belongs to the source that registered it.
_handler_registry:'anydict' = {}

# ################################################################################################################################

def register_resubmit_handler(source:'str', action:'str', handler:'callable_') -> 'None':
    """ Registers what one action means for one audit source.
    """
    _handler_registry[(source, action)] = handler

# ################################################################################################################################

def get_resubmit_handler(source:'str', action:'str') -> 'callable_':
    """ Returns the handler one source registered for one action.
    """
    key = (source, action)

    if key not in _handler_registry:
        raise ResubmitException(f'No `{action}` handler is registered for source `{source}`')

    out = _handler_registry[key]
    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class HopResendResult:
    """ What one per-hop resend did - the id of the new event and whatever the target answered.
    """
    event_id: 'intnone' = None
    response: 'any_' = None

# ################################################################################################################################

def resend_hop(event:'StoredEvent', send:'callable_', audit_log:'AuditLog', cid:'str') -> 'HopResendResult':
    """ Sends the exact payload stored with one outgoing event through the same connection again -
    repeating a single delivery to one destination without re-running the service that produced it
    and without involving any other destination. The attempt is recorded as its own outgoing event
    linked to the original by the correlation id, regardless of the outcome.
    """
    require_event_type(event, AuditEvent.Request_Sent, 'resent per hop')

    payload = get_stored_payload(event)

    # The recording is shared by both branches - only the outcome fields differ
    values:'stranydict' = {
        'cid': cid,
        'msg_id': event.msg_id,
        'correl_id': event.cid,
        'size': len(payload),
        'data': dumps({'payload': payload}),
        'parents': [event.id],
    }

    # Deliver the payload through the connection the original went through ..
    try:
        response = send(payload)

    # .. a failed attempt is recorded too, as its own row with an error outcome,
    # so the per-destination delivery history has no holes - then the caller learns about it.
    except Exception as e:
        _ = audit_log.insert(
            event.source, AuditEvent.Request_Sent, event.object_name,
            outcome=AuditOutcome.Error, status=str(e), **values)
        raise

    # Our response to produce
    out = HopResendResult()
    out.response = response

    out.event_id = audit_log.insert(
        event.source, AuditEvent.Request_Sent, event.object_name,
        outcome=AuditOutcome.OK, **values)

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RepairFilter:
    """ Which stored events one bulk repair applies to.
    """
    source: str = ''
    event_type: str = ''
    object_name: str = ''
    classification: str = ''
    outcome: str = ''

# ################################################################################################################################

@dataclass(init=False)
class BulkRepairResult:
    """ What one bulk repair did, row by row.
    """
    is_dry_run: bool = False
    total: int = 0
    resubmitted_count: int = 0
    duplicate_count: int = 0
    error_count: int = 0

    # One entry per matched event: its id and what happened to it
    rows: 'anylist' = list_field()

    # The id of the one audit event recording the whole operation
    bulk_event_id: 'intnone' = None

# ################################################################################################################################

def find_event_ids(repair_filter:'RepairFilter') -> 'intlist':
    """ Returns the ids of the events one bulk repair applies to, oldest first,
    so resubmission preserves the original order.
    """
    statement = select(event_table.c.id)

    statement = statement.where(event_table.c.source == repair_filter.source)
    statement = statement.where(event_table.c.event_type == repair_filter.event_type)

    # The optional criteria narrow the match only when set
    if repair_filter.object_name:
        statement = statement.where(event_table.c.object_name == repair_filter.object_name)

    if repair_filter.classification:
        statement = statement.where(event_table.c.classification == repair_filter.classification)

    if repair_filter.outcome:
        statement = statement.where(event_table.c.outcome == repair_filter.outcome)

    statement = statement.order_by(event_table.c.id)

    engine = get_audit_engine()

    out:'intlist' = []

    with engine.connect() as connection:
        for row in connection.execute(statement):
            out.append(row[0])

    return out

# ################################################################################################################################

def bulk_repair(
    repair_filter:'RepairFilter',
    resubmit_one:'callable_',
    audit_log:'AuditLog',
    cid:'str',
    *,
    transform:'callable_ | None' = None,
    dry_run:'bool' = False,
    ) -> 'BulkRepairResult':
    """ Applies one filter server-side and resubmits every matched event sequentially,
    optionally transforming each payload first - one audited operation with per-row outcomes.
    A dry run reports what would be resubmitted, per row, without sending anything.
    Every real row is guarded by a dedup key, so overlapping bulk operations
    cannot double-apply one message.
    """

    # Our response to produce - the rows are assigned here because init=False
    # means the field factory never runs
    out = BulkRepairResult()
    out.is_dry_run = dry_run
    out.rows = []

    engine = get_audit_engine()

    event_ids = find_event_ids(repair_filter)
    out.total = len(event_ids)

    # Sequential, in id order, so downstream systems see the original order preserved
    for event_id in event_ids:

        row:'stranydict' = {'event_id': event_id, 'result': '', 'detail': ''}
        out.rows.append(row)

        event = load_event(event_id)
        payload = get_stored_payload(event)

        # The optional repair happens before anything is sent or reported
        if transform:
            payload = transform(payload)

        # A dry run stops here - the row reports what would happen
        if dry_run:
            row['result'] = Row_Would_Resubmit
            continue

        # The dedup key covers the exact payload, so repairing a message differently
        # is a new operation while resubmitting it identically twice is caught
        dedup_key = build_dedup_key(Action_Resend, event_id, payload)

        if not acquire_dedup_key(engine, dedup_key, cid, AuditEvent.Bulk_Repair):
            row['result'] = Row_Duplicate
            out.duplicate_count += 1
            continue

        # One failing row never aborts the rest of the operation - and a failed row
        # releases its key, so the same repair remains retryable later,
        # while a successful one remains claimed permanently.
        try:
            resubmit_one(event, payload)
        except Exception:
            row['result'] = Row_Error
            row['detail'] = format_exc()
            out.error_count += 1
            release_dedup_key(engine, dedup_key)
        else:
            row['result'] = Row_Resubmitted
            out.resubmitted_count += 1
            complete_dedup_key(engine, dedup_key, AuditOutcome.OK)

    # A dry run reports only - the audit trail records operations, not previews
    if dry_run:
        return out

    # The whole operation is one audit event with the per-row outcomes inside
    if out.error_count:
        bulk_outcome = AuditOutcome.Error
    else:
        bulk_outcome = AuditOutcome.OK

    out.bulk_event_id = audit_log.insert(
        repair_filter.source, AuditEvent.Bulk_Repair, repair_filter.object_name,
        cid=cid,
        outcome=bulk_outcome,
        data=dumps({'rows': out.rows}),
    )

    return out

# ################################################################################################################################
# ################################################################################################################################
