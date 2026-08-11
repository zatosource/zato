# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The source-agnostic core of every resubmit - loading a stored event back, the registry
# of per-source handlers, the per-hop resend over outgoing events, and bulk resubmit.
# Each source contributes its own resend and reprocess semantics on top of this module,
# the way zato.common.as2.resubmit and zato.common.hl7.resubmit do.

from __future__ import annotations

# stdlib
from dataclasses import dataclass
from traceback import format_exc

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource, event_body_table, event_table, get_audit_engine
from zato.common.audit_log.common import AuditBody
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
Row_Resubmitted    = 'resubmitted'
Row_Would_Resubmit = 'would-resubmit'
Row_Duplicate      = 'duplicate'
Row_Error          = 'error'

# ################################################################################################################################
# ################################################################################################################################

# What every resubmit action reads to the operator - the service behind it is what
# tells a resend from a reprocess.
Resubmit_Label = 'Resubmit'

# Per-source resubmit actions - each source declares which of its events are resubmittable,
# how the row action is labelled and which service performs it. The audit log page renders
# its per-row actions out of this catalog and the alerting collectors read it to say whether
# an alert's newest failing event can be sent again, which is what turns the alert's link
# into a deep link at that event.
_as2_actions = {
    AuditEvent.Message_Sent:     {'label': Resubmit_Label, 'service': 'zato.audit-log.as2.resend'},
    AuditEvent.Message_Received: {'label': Resubmit_Label, 'service': 'zato.audit-log.as2.reprocess'},
}

_as4_actions = {
    AuditEvent.Message_Sent:     {'label': Resubmit_Label, 'service': 'zato.audit-log.as4.resend'},
    AuditEvent.Message_Received: {'label': Resubmit_Label, 'service': 'zato.audit-log.as4.reprocess'},
}

# What a channel received is re-run through the channel's own machinery
_mllp_channel_actions = {
    AuditEvent.Message_Received: {'label': Resubmit_Label, 'service': 'zato.audit-log.hl7.reprocess'},
}

# What an outgoing connection delivered is sent through it again, and a message a channel
# fanned out to one of its destinations is repeated per hop, that one delivery going out
# again without the rest of the destinations being involved
_mllp_outgoing_actions = {
    AuditEvent.Message_Sent: {'label': Resubmit_Label, 'service': 'zato.audit-log.hl7.resend'},
    AuditEvent.Request_Sent: {'label': Resubmit_Label, 'service': 'zato.audit-log.resend-hop'},
}

# One recorded delivery to one destination is repeated on its own, whatever kind of connection
# it went through - the row says which destination it went to and what repeating it needs.
_hop_actions = {
    AuditEvent.Request_Sent: {'label': Resubmit_Label, 'service': 'zato.audit-log.resend-hop'},
}

# The sources whose events carry resubmit actions at all, each with its own catalog
source_resubmit_actions = {
    AuditSource.AS2: _as2_actions,
    AuditSource.AS4: _as4_actions,
    AuditSource.MLLP_Channel: _mllp_channel_actions,
    AuditSource.MLLP_Outgoing: _mllp_outgoing_actions,
    AuditSource.FHIR: _hop_actions,
    AuditSource.REST_Outgoing: _hop_actions,
    AuditSource.Email_SMTP: _hop_actions,
}

# ################################################################################################################################

def is_event_type_resubmittable(source:'str', event_type:'str') -> 'bool':
    """ Whether one source declared one event type resubmittable - what says whether
    an alert about a failure of that type can offer to send the message again.
    """
    actions = source_resubmit_actions.get(source)

    # A source with no resubmit catalog of its own has nothing to send again
    if actions is None:
        return False

    out = event_type in actions
    return out

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

    # The data of a resubmittable event, when there is any, is always a JSON document.
    if data:
        try:
            details = loads(data)
        except ValueError:
            raise ResubmitException(f'Audit event `{event_id}` does not carry JSON data')
    else:
        details = {}

    # A producer that stores its payload by reference keeps it in the body table
    # under the request kind - it becomes the payload the resubmit works with.
    if 'payload' not in details:

        body_statement = select(event_body_table.c.data).where(
            event_body_table.c.event_id == event_id).where(
            event_body_table.c.kind == AuditBody.Request)

        with engine.connect() as connection:
            body_result = connection.execute(body_statement)
            body_row = body_result.first()

        if body_row is not None:
            details['payload'] = body_row[0]

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
    e.g. a reconciliation-only entry, cannot be resubmitted. An empty payload is
    a payload too - a GET request goes out with no body and resends the same way.
    """
    if 'payload' in event.details:
        out = event.details['payload']
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

def resend_hop(event:'StoredEvent', send:'callable_', audit_log:'AuditLog', cid:'str', actor:'str'='') -> 'HopResendResult':
    """ Sends the exact payload stored with one outgoing event through the same connection again -
    repeating a single delivery to one destination without re-running the service that produced it
    and without involving any other destination. The attempt is recorded as its own outgoing event
    linked to the original by the correlation id, regardless of the outcome. The actor is who
    asked for the resend, recorded with the new event so the trail says by whom.
    """
    require_event_type(event, AuditEvent.Request_Sent, 'resent per hop')

    payload = get_stored_payload(event)

    # The attempt is recorded with everything the original carried, the payload included, which is
    # what keeps it as repeatable as the original was - a resend of a resend goes to the same place.
    stored_details = dict(event.details)
    stored_details['payload'] = payload

    # The recording is shared by both branches - only the outcome fields differ
    values:'stranydict' = {
        'cid': cid,
        'msg_id': event.msg_id,
        'correl_id': event.cid,
        'size': len(payload),
        'data': dumps(stored_details),
        'parents': [event.id],
    }

    # Who asked for the resend is a searchable attribute of the new event
    if actor:
        values['attrs'] = {'actor': actor}

    # Deliver the payload through the connection the original went through ..
    try:
        response = send(payload)

    # .. a failed attempt is recorded too, as its own row with an error outcome,
    # so the per-destination delivery history has no holes - then the caller learns about it.
    except Exception as e:
        error_status = str(e)

        error_options = {
            'outcome': AuditOutcome.Error,
            'status': error_status,
        }
        error_options.update(values)

        _ = audit_log.insert(event.source, AuditEvent.Request_Sent, event.object_name, **error_options)

        raise

    # Our response to produce
    out = HopResendResult()
    out.response = response

    ok_options = {'outcome': AuditOutcome.OK}
    ok_options.update(values)

    out.event_id = audit_log.insert(event.source, AuditEvent.Request_Sent, event.object_name, **ok_options)

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ResubmitFilter:
    """ Which stored events one bulk resubmit applies to.
    """
    source: str = ''
    event_type: str = ''
    object_name: str = ''
    classification: str = ''
    outcome: str = ''

# ################################################################################################################################

@dataclass(init=False)
class BulkResubmitResult:
    """ What one bulk resubmit did, row by row.
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

def find_event_ids(resubmit_filter:'ResubmitFilter') -> 'intlist':
    """ Returns the ids of the events one bulk resubmit applies to, oldest first,
    so resubmission preserves the original order.
    """
    statement = select(event_table.c.id)

    statement = statement.where(event_table.c.source == resubmit_filter.source)
    statement = statement.where(event_table.c.event_type == resubmit_filter.event_type)

    # The optional criteria narrow the match only when set
    if resubmit_filter.object_name:
        statement = statement.where(event_table.c.object_name == resubmit_filter.object_name)

    if resubmit_filter.classification:
        statement = statement.where(event_table.c.classification == resubmit_filter.classification)

    if resubmit_filter.outcome:
        statement = statement.where(event_table.c.outcome == resubmit_filter.outcome)

    statement = statement.order_by(event_table.c.id)

    engine = get_audit_engine()

    out:'intlist' = []

    with engine.connect() as connection:
        for row in connection.execute(statement):
            out.append(row[0])

    return out

# ################################################################################################################################

def bulk_resubmit(
    resubmit_filter:'ResubmitFilter',
    resubmit_one:'callable_',
    audit_log:'AuditLog',
    cid:'str',
    *,
    transform:'callable_ | None' = None,
    dry_run:'bool' = False,
    actor:'str' = '',
    ) -> 'BulkResubmitResult':
    """ Applies one filter server-side and resubmits every matched event sequentially,
    optionally transforming each payload first - one audited operation with per-row outcomes.
    A dry run reports what would be resubmitted, per row, without sending anything.
    Every real row is guarded by a dedup key, so overlapping bulk operations
    cannot double-apply one message. The actor is who asked for the resubmit,
    recorded on each ledger row and on the bulk event itself.
    """

    # Our response to produce - the rows are assigned here because init=False
    # means the field factory never runs
    out = BulkResubmitResult()
    out.is_dry_run = dry_run
    out.rows = []

    engine = get_audit_engine()

    event_ids = find_event_ids(resubmit_filter)
    out.total = len(event_ids)

    # Sequential, in id order, so downstream systems see the original order preserved
    for event_id in event_ids:

        row:'stranydict' = {'event_id': event_id, 'result': '', 'detail': ''}
        out.rows.append(row)

        event = load_event(event_id)
        payload = get_stored_payload(event)

        # The optional transform happens before anything is sent or reported
        if transform:
            payload = transform(payload)

        # A dry run stops here - the row reports what would happen
        if dry_run:
            row['result'] = Row_Would_Resubmit
            continue

        # The dedup key covers the exact payload, so resubmitting an edited message
        # is a new operation while resubmitting it identically twice is caught
        dedup_key = build_dedup_key(Action_Resend, event_id, payload)

        if not acquire_dedup_key(engine, dedup_key, cid, AuditEvent.Bulk_Resubmit, actor):
            row['result'] = Row_Duplicate
            out.duplicate_count += 1
            continue

        # One failing row never aborts the rest of the operation - and a failed row
        # releases its key, so the same resubmit remains retryable later,
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

    rows_json = dumps({'rows': out.rows})

    bulk_options = {
        'cid': cid,
        'outcome': bulk_outcome,
        'data': rows_json,
    }

    # Who asked for the resubmit is a searchable attribute of the bulk event
    if actor:
        bulk_options['attrs'] = {'actor': actor}

    out.bulk_event_id = audit_log.insert(
        resubmit_filter.source, AuditEvent.Bulk_Resubmit, resubmit_filter.object_name, **bulk_options)

    return out

# ################################################################################################################################
# ################################################################################################################################
