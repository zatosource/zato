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

# Zato
from zato.common.as2.audit import decode_payload_documents, encode_payload_document, record_message_received, \
    record_send_result
from zato.common.as2.common import AS2Exception
from zato.common.as2.outbound import PayloadItem
from zato.common.as2.partnership import match_partnership
from zato.common.audit_log.api import AuditEvent, AuditSource
from zato.common.audit_log.resubmit import Action_Reprocess, Action_Resend, load_event as load_event_core, \
    register_resubmit_handler, ResubmitException, StoredEvent
from zato.common.typing_ import dict_field, list_field
from zato.edi.envelope import read_envelope

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.outbound import SendResult
    from zato.common.as2.partnership import partnership_list
    from zato.common.as2.reconcile import MDNReconciler
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import any_, anylist, callable_, dictlist, stranydict, strnone
    any_ = any_
    anylist = anylist
    callable_ = callable_
    dictlist = dictlist
    MDNReconciler = MDNReconciler
    partnership_list = partnership_list
    SendResult = SendResult
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# The kinds of routing targets a reprocessed message can land on.
Target_Service = 'service'
Target_Topic   = 'topic'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ReprocessResult:
    """ What one reprocess did - the messages that were routed and where they went.
    """
    # The first routed message, which is the whole of it for the single-document case
    # every partner but the logistics ones sends.
    message: 'stranydict' = dict_field()

    # Every routed message, one per document of the original delivery.
    messages: 'anylist' = list_field()

    target_kind: str = ''
    target_name: str = ''

# ################################################################################################################################
# ################################################################################################################################

def load_event(event_id:'int') -> 'StoredEvent':
    """ Reads one audit event by its id, along with its parsed JSON data.
    The loading itself lives in the shared resubmit core - this wrapper only keeps
    the AS2 error contract, where everything AS2-related raises AS2Exception.
    """
    try:
        out = load_event_core(event_id)
    except ResubmitException as e:
        raise AS2Exception(e.args[0])

    return out

# ################################################################################################################################

def _get_stored_documents(event:'StoredEvent') -> 'anylist':
    """ Returns every document stored with an event, each as a (bytes, content type, filename)
    tuple - an event recorded without any cannot be resubmitted.
    """
    out = decode_payload_documents(event.details)

    if not out:
        raise AS2Exception(f'Audit event `{event.id}` does not carry a payload to resubmit')

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

def resend(event:'StoredEvent', send:'callable_', reconciler:'MDNReconciler', cid:'str') -> 'SendResult':
    """ Sends the documents stored with an outbound event again, as a fresh AS2 message
    with a new Message-ID - an operator action, unlike the automatic resend that reuses
    the original Message-ID when an MDN is overdue. The new attempt is recorded
    as its own message-sent event linked to the original one by the correlation id,
    which also makes it a fresh open item for MDN reconciliation.
    """

    # Only outbound events carry a payload that can go out again.
    if event.event_type != AuditEvent.Message_Sent:
        raise AS2Exception(f'Only `{AuditEvent.Message_Sent}` events can be resent, not `{event.event_type}`')

    documents = _get_stored_documents(event)

    # The identities of the original exchange say who the message travels between.
    as2_from, as2_to = event.object_name.split(':', 1)

    first_data, _, first_filename = documents[0]
    document_count = len(documents)

    # A single document travels the way it did originally ..
    if document_count == 1:
        payload:'any_' = first_data
        filename:'strnone' = first_filename

        if not filename:
            filename = None

    # .. while a multi-attachment message goes back out as one, each document keeping its own
    # content type and filename, so the partner receives what it received the first time.
    else:
        items:'anylist' = []

        for data, content_type, item_filename in documents:
            item = PayloadItem(data, content_type, item_filename)
            items.append(item)

        payload = items
        filename = None

    # Deliver through the real pipeline - a fresh Message-ID is assigned inside ..
    out = send(payload, filename)

    # .. and the new attempt becomes its own event, linked to the original by its CID,
    # with the synchronous MDN recorded too when one rode back on the response.
    payloads:'anylist' = []

    for data, content_type, item_filename in documents:
        document = encode_payload_document(data, content_type, item_filename)
        payloads.append(document)

    # The readable text field keeps the first document, which is the EDI one - the entries
    # above are what a further resubmit works from.
    first_text = first_data.decode('utf8', 'replace')

    record_send_result(
        reconciler,
        as2_from,
        as2_to,
        out,
        payload=first_text,
        filename=first_filename,
        cid=cid,
        correl_id=event.cid,
        payloads=payloads,
    )

    return out

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
    """ Re-publishes every document stored with an inbound event to the partner's routing target -
    for when the recipient system was down and the already-received documents are to flow again.
    A multi-attachment delivery is routed the way it was the first time, one message per document,
    because a subscriber that received the EDI document and its attached PDF separately must
    receive both of them again. The new attempt is recorded as its own message-received event
    linked to the original one by the correlation id.
    """

    # Only inbound events carry a payload that can be redelivered.
    if event.event_type != AuditEvent.Message_Received:
        raise AS2Exception(f'Only `{AuditEvent.Message_Received}` events can be reprocessed, not `{event.event_type}`')

    documents = _get_stored_documents(event)

    # The identities of the original exchange, as they arrived on the wire.
    as2_from, as2_to = event.object_name.split(':', 1)

    # Our response to produce
    out = ReprocessResult()
    out.messages = []

    # The partner's own routing overrides apply to a reprocess the same way
    # they apply to a live delivery - a partnership that is gone means the defaults.
    partnership = match_partnership(partnerships, as2_from, as2_to)

    if partnership:
        inbound_service = partnership.inbound_service
        inbound_topic = partnership.inbound_topic
    else:
        inbound_service = ''
        inbound_topic = ''

    # The target is decided once and every document goes to it.
    if inbound_service:
        out.target_kind = Target_Service
        out.target_name = inbound_service
    elif inbound_topic:
        out.target_kind = Target_Topic
        out.target_name = inbound_topic
    else:
        out.target_kind = Target_Topic
        out.target_name = default_topic

    payloads:'anylist' = []

    for data, content_type, filename in documents:

        # The same routed shape the channel builds for a live delivery, so subscribers
        # cannot tell a reprocess apart - including the EDI envelope identifiers.
        envelope = read_envelope(data)
        edi = envelope.to_dict()

        message = {
            'message_id': event.msg_id,
            'as2_from': as2_from,
            'as2_to': as2_to,
            'filename': filename,
            'content_type': content_type,
            'data': data.decode('utf8', 'replace'),
            'edi': edi,
        }

        out.messages.append(message)

        document = encode_payload_document(data, content_type, filename)
        payloads.append(document)

        if out.target_kind == Target_Service:
            invoke_service(out.target_name, message)
        else:
            publish(out.target_name, message)

    out.message = out.messages[0]

    first_data, first_content_type, first_filename = documents[0]

    # The readable text field keeps the first document, which is the EDI one - the entries
    # above are what a further resubmit works from.
    first_text = first_data.decode('utf8', 'replace')

    # The new attempt becomes its own event, linked to the original by its CID.
    record_message_received(
        audit_log,
        as2_from,
        as2_to,
        event.msg_id,
        payload=first_text,
        filename=first_filename,
        content_type=first_content_type,
        cid=cid,
        correl_id=event.cid,
        payloads=payloads,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################

# The AS2 handlers are found through the shared registry - the service layer
# supplies the callables when it wires the real connections in.
register_resubmit_handler(AuditSource.AS2, Action_Resend, resend)
register_resubmit_handler(AuditSource.AS2, Action_Reprocess, reprocess)

# ################################################################################################################################
# ################################################################################################################################
