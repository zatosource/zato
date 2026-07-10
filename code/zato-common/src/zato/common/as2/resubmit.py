# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Resubmit - the operator half of the delivery taxonomy, distinct from the automatic resend
# that reuses the original Message-ID when an MDN is overdue. A resend takes the payload stored
# with an outbound message-sent event and delivers it again as a fresh AS2 message with a new
# Message-ID, and a reprocess takes an inbound message-received event and re-publishes its
# payload to the partner's routing target. Either way, the new attempt lands as its own
# audit event linked to the original one by the correlation id.

from __future__ import annotations

# stdlib
from dataclasses import dataclass

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.as2.common import AS2Exception
from zato.common.as2.mdn import normalize_message_id
from zato.common.as2.partnership import match_partnership
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table, get_audit_engine
from zato.common.json_internal import dumps, loads
from zato.common.typing_ import dict_field
from zato.edi.envelope import read_envelope

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.outbound import SendResult
    from zato.common.as2.partnership import partnership_list
    from zato.common.as2.reconcile import MDNReconciler
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import callable_, dictlist, stranydict
    callable_ = callable_
    dictlist = dictlist
    MDNReconciler = MDNReconciler
    partnership_list = partnership_list
    SendResult = SendResult

# ################################################################################################################################
# ################################################################################################################################

# The kinds of routing targets a reprocessed message can land on.
Target_Service = 'service'
Target_Topic   = 'topic'

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

    # What the event recorded - for AS2 events this is where the clear payload lives.
    details: 'stranydict' = dict_field()

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ReprocessResult:
    """ What one reprocess did - the message that was routed and where it went.
    """
    message: 'stranydict' = dict_field()
    target_kind: str = ''
    target_name: str = ''

# ################################################################################################################################
# ################################################################################################################################

def load_event(event_id:'int') -> 'StoredEvent':
    """ Reads one audit event by its id, along with its parsed JSON data.
    """
    stmt = select(
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
        row = connection.execute(stmt).first()

    # There is nothing to resubmit if the event does not exist, e.g. retention already deleted it.
    if row is None:
        raise AS2Exception(f'Audit event `{event_id}` was not found')

    event_id, cid, source, event_type, object_name, msg_id, data = row

    # The data of a resubmittable event is always a JSON document with the payload inside.
    try:
        details = loads(data)
    except ValueError:
        raise AS2Exception(f'Audit event `{event_id}` does not carry JSON data')

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

def _get_stored_payload(event:'StoredEvent') -> 'str':
    """ Returns the clear payload stored with an event - an event recorded without one,
    e.g. a reconciliation-only entry, cannot be resubmitted.
    """
    if payload := event.details.get('payload'):
        out = payload
    else:
        raise AS2Exception(f'Audit event `{event.id}` does not carry a payload to resubmit')

    return out

# ################################################################################################################################

def _get_stored_filename(event:'StoredEvent') -> 'str | None':
    """ Returns the filename stored alongside the payload - an empty one means
    none was preserved at the time the event was recorded.
    """
    if filename := event.details.get('filename'):
        out = filename
    else:
        out = None

    return out

# ################################################################################################################################

def find_connection_name(configs:'dictlist', as2_from:'str', as2_to:'str') -> 'str':
    """ Returns the name of the outgoing AS2 connection whose identities form the given pair -
    the connection a stored outbound message goes back through on a resend.
    """
    for config in configs:
        if config['as2_from'] == as2_from:
            if config['as2_to'] == as2_to:
                out = config['name']
                break
    else:
        raise AS2Exception(f'No outgoing AS2 connection matches the pair `{as2_from}:{as2_to}`')

    return out

# ################################################################################################################################

def record_message_received(
    audit_log:'AuditLog',
    as2_from:'str',
    as2_to:'str',
    message_id:'str',
    *,
    payload:'str' = '',
    filename:'str' = '',
    content_type:'str' = '',
    cid:'str' = '',
    correl_id:'str' = '',
    ) -> 'None':
    """ Records that a message arrived from the partner, with the clear payload stored alongside
    so a later reprocess can re-publish it. A reprocess of a stored message links back
    to the original event through the correlation id.
    """
    pair = f'{as2_from.strip()}:{as2_to.strip()}'
    message_id = normalize_message_id(message_id)

    data = dumps({'payload': payload, 'filename': filename, 'content_type': content_type})

    audit_log.insert(
        AuditSource.AS2, AuditEvent.Message_Received, pair, cid=cid, msg_id=message_id, correl_id=correl_id, data=data)

# ################################################################################################################################

def resend(event:'StoredEvent', send:'callable_', reconciler:'MDNReconciler', cid:'str') -> 'SendResult':
    """ Sends the payload stored with an outbound event again, as a fresh AS2 message
    with a new Message-ID - an operator action, unlike the automatic resend that reuses
    the original Message-ID when an MDN is overdue. The new attempt is recorded
    as its own message-sent event linked to the original one by the correlation id,
    which also makes it a fresh open item for MDN reconciliation.
    """

    # Only outbound events carry a payload that can go out again.
    if event.event_type != AuditEvent.Message_Sent:
        raise AS2Exception(f'Only `{AuditEvent.Message_Sent}` events can be resent, not `{event.event_type}`')

    payload = _get_stored_payload(event)
    filename = _get_stored_filename(event)

    # The identities of the original exchange say who the message travels between.
    as2_from, as2_to = event.object_name.split(':', 1)

    # Deliver the payload through the real pipeline - a fresh Message-ID is assigned inside ..
    result = send(payload, filename)

    # .. and the new attempt becomes its own event, linked to the original by its CID.
    if filename is None:
        filename = ''

    reconciler.record_message_sent(
        as2_from,
        as2_to,
        result.message_id,
        mic=result.mic,
        cid=cid,
        correl_id=event.cid,
        payload=payload,
        filename=filename,
    )

    return result

# ################################################################################################################################

def reprocess(
    event:'StoredEvent',
    partnerships:'partnership_list',
    invoke_service:'callable_',
    publish:'callable_',
    audit_log:'AuditLog',
    cid:'str',
    default_topic:'str',
    ) -> 'ReprocessResult':
    """ Re-publishes the payload stored with an inbound event to the partner's routing target -
    for when the recipient system was down and the already-received documents are to flow again.
    The new attempt is recorded as its own message-received event linked to the original one
    by the correlation id.
    """

    # Only inbound events carry a payload that can be redelivered.
    if event.event_type != AuditEvent.Message_Received:
        raise AS2Exception(f'Only `{AuditEvent.Message_Received}` events can be reprocessed, not `{event.event_type}`')

    payload = _get_stored_payload(event)
    filename = _get_stored_filename(event)

    if filename is None:
        filename = ''

    # The content type was stored when the message arrived - it is empty for events
    # recorded without one, which subscribers can tell by the field itself.
    content_type = event.details.get('content_type')
    if content_type is None:
        content_type = ''

    # The identities of the original exchange, as they arrived on the wire.
    as2_from, as2_to = event.object_name.split(':', 1)

    # The same routed shape the channel builds for a live delivery, so subscribers
    # cannot tell a reprocess apart - including the EDI envelope identifiers.
    payload_bytes = payload.encode('utf8')
    envelope = read_envelope(payload_bytes)

    message = {
        'message_id': event.msg_id,
        'as2_from': as2_from,
        'as2_to': as2_to,
        'filename': filename,
        'content_type': content_type,
        'data': payload,
        'edi': envelope.to_dict(),
    }

    # Our response to produce
    out = ReprocessResult()
    out.message = message

    # The partner's own routing overrides apply to a reprocess the same way
    # they apply to a live delivery - a partnership that is gone means the defaults.
    partnership = match_partnership(partnerships, as2_from, as2_to)

    if partnership:
        inbound_service = partnership.inbound_service
        inbound_topic = partnership.inbound_topic
    else:
        inbound_service = ''
        inbound_topic = ''

    # The partner's own service receives the message directly ..
    if inbound_service:
        invoke_service(inbound_service, message)
        out.target_kind = Target_Service
        out.target_name = inbound_service

    # .. or the partner's own topic ..
    elif inbound_topic:
        publish(inbound_topic, message)
        out.target_kind = Target_Topic
        out.target_name = inbound_topic

    # .. and by default, the shared inbound topic.
    else:
        publish(default_topic, message)
        out.target_kind = Target_Topic
        out.target_name = default_topic

    # The new attempt becomes its own event, linked to the original by its CID.
    record_message_received(
        audit_log,
        as2_from,
        as2_to,
        event.msg_id,
        payload=payload,
        filename=filename,
        content_type=content_type,
        cid=cid,
        correl_id=event.cid,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################
