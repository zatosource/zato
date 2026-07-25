# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The automatic same-Message-ID resend - the reliability half of AS2, and what the EDIINT-Features
# header advertises when it names AS2-Reliability.
#
# A message whose MDN never arrived is in the one state AS2 cannot resolve on its own: the sender
# does not know whether the partner processed the document and lost the receipt, or never received
# the document at all. The specification's answer is to deliver the same content again under the
# same Message-ID and let the receiver's duplicate detection decide - a partner that already has
# the message replays its stored receipt, and one that never had it processes it now. That is why
# the Message-ID must not change, and why a resend is a different thing from the operator resubmit
# in resubmit.py, which deliberately delivers the content as a new message.
#
# The state this runs on is the reconciliation store, so nothing here needs its own bookkeeping:
# the attempts already made are the message-sent events under one Message-ID, and an MDN arriving
# at any point removes the message from the outstanding set and with it from this module's reach.

from __future__ import annotations

# stdlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import getLogger

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.api import AS2
from zato.common.as2.audit import decode_payload_documents
from zato.common.as2.common import DeliveryKind
from zato.common.as2.outbound import PayloadItem
from zato.common.as2.reconcile import MDNReconciler
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table
from zato.common.json_internal import loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.reconcile import PendingMDN
    from zato.common.typing_ import any_, anydict, anydictnone, anylist, anytuple, dictlist, strnone
    any_ = any_
    anydict = anydict
    anydictnone = anydictnone
    anylist = anylist
    anytuple = anytuple
    dictlist = dictlist
    PendingMDN = PendingMDN
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
resend_candidate_list = list['ResendCandidate']

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ResendCandidate:
    """ One message whose MDN is overdue and which is to go out again unchanged.
    """
    # Which connection the message travels back through and who it travels between.
    connection_name: str = ''
    as2_from:        str = ''
    as2_to:          str = ''

    # The Message-ID the content goes out under again, which is the original one.
    message_id: str = ''

    # Whether this is a retry of an attempt the partner never accepted or a resend of one
    # it accepted and then never answered.
    delivery_kind: str = ''

    # How many attempts this message has already had, the original one included.
    attempt_count: int = 0

    # The documents to deliver again - one payload for a single-document message,
    # the whole list for a multi-attachment one.
    payload: 'anylist'

    # The filename of a single-document message, which a multi-attachment one
    # carries inside its own documents instead.
    filename: 'strnone' = None

# ################################################################################################################################
# ################################################################################################################################

def get_max_retries(config:'anydictnone') -> 'int':
    """ Returns how many resends one partner's messages get - its own resend_max_retries
    or the job's default when the partner does not set one.
    """
    if config:
        if max_retries := config['resend_max_retries']:
            out = max_retries
            return out

    out = AS2.Resend.Default_Max_Retries
    return out

# ################################################################################################################################

def _get_overdue_seconds(config:'anydictnone') -> 'int':
    """ Returns the window after which one partner's missing MDN counts as overdue - its own
    ack_overdue_after or the alerting default, which is the same window the alerting job
    raises its findings on, so an operator never sees a resend for something not yet flagged.
    """
    if config:
        if window := config['ack_overdue_after']:
            out = window
            return out

    out = AS2.Alerting.Default_Ack_Overdue_Seconds
    return out

# ################################################################################################################################

def _index_configs_by_pair(configs:'dictlist') -> 'anydict':
    """ Indexes the AS2 connections by their identity pair, built once per run so that matching
    a pending message to its partner does not walk the whole connection list per message.
    """
    out:'anydict' = {}

    for config in configs:
        pair = (config['as2_from'], config['as2_to'])
        out[pair] = config

    return out

# ################################################################################################################################
# ################################################################################################################################

def count_attempts(reconciler:'MDNReconciler', message_id:'str') -> 'int':
    """ Returns how many delivery attempts one Message-ID has already had.

    Every attempt records its own message-sent event under the same Message-ID, so counting the
    events is counting the attempts - which is exactly the state a restart must not lose and
    the reason the count is not held in memory anywhere.
    """
    statement = select(func.count(event_table.c.id)).where(and_(
        event_table.c.source == AuditSource.AS2,
        event_table.c.event_type == AuditEvent.Message_Sent,
        event_table.c.msg_id == message_id,
    ))

    with reconciler.engine.connect() as connection:
        result = connection.execute(statement)
        out = result.scalar()

    return out

# ################################################################################################################################

def _get_stored_documents(reconciler:'MDNReconciler', message_id:'str') -> 'anylist':
    """ Returns every document of the most recent attempt at one Message-ID, each as a
    (bytes, content type, filename) tuple - what the next attempt delivers again.
    """
    statement = select(
        event_table.c.data,
    ).where(and_(
        event_table.c.source == AuditSource.AS2,
        event_table.c.event_type == AuditEvent.Message_Sent,
        event_table.c.msg_id == message_id,
    )).order_by(event_table.c.id.desc())

    with reconciler.engine.connect() as connection:
        result = connection.execute(statement)
        row = result.first()

    # A message with no event behind it is not resendable, which the caller reads
    # from the empty list rather than from an exception - a run over the whole
    # outstanding set must not stop at one unusable entry.
    if row is None:
        return []

    data = row[0]

    if not data:
        return []

    details = loads(data)

    out = decode_payload_documents(details)
    return out

# ################################################################################################################################

def _build_payload(documents:'anylist') -> 'anytuple':
    """ Turns the stored documents of one message into the payload and filename it goes back out
    with - a single document travels the way it did originally, while a multi-attachment message
    goes back out as one delivery with each document keeping its own content type and filename.
    """
    document_count = len(documents)
    first_data, _, first_filename = documents[0]

    if document_count == 1:
        payload:'any_' = first_data
        filename:'strnone' = first_filename

        if not filename:
            filename = None

    else:
        items:'anylist' = []

        for data, content_type, item_filename in documents:
            item = PayloadItem(data, content_type, item_filename)
            items.append(item)

        payload = items
        filename = None

    out = payload, filename
    return out

# ################################################################################################################################

def _get_delivery_kind(pending:'PendingMDN') -> 'str':
    """ Tells whether the next attempt is a retry or a resend.

    A previous attempt whose HTTP exchange never succeeded did not reach the partner at all, so
    repeating it is a retry. One the partner answered with a success status did reach it, and the
    thing that went missing is the receipt, so repeating it is a resend. The distinction matters
    to whoever reads the evidence later: a retry says the transport failed, a resend says the
    partner has the document and owes a receipt for it.
    """
    is_accepted = 200 <= pending.http_status < 300

    if is_accepted:
        out = DeliveryKind.Resend
    else:
        out = DeliveryKind.Retry

    return out

# ################################################################################################################################
# ################################################################################################################################

def collect_candidates(
    configs:'dictlist',
    now:'datetime',
    server_name:'str',
    limit:'int'=AS2.Resend.Batch_Size,
    ) -> 'resend_candidate_list':
    """ Returns the messages whose MDN is overdue and which have attempts left, up to one batch.

    The batch is what keeps a partner outage from turning one run into a burst of every message
    sent during it - the rest stays outstanding and the next run picks it up.
    """

    # Our response to produce
    out:'resend_candidate_list' = []

    reconciler = MDNReconciler(server_name)
    configs_by_pair = _index_configs_by_pair(configs)

    for pending in reconciler.outstanding(now):

        # A message with no connection behind it cannot be resent - the partner was deleted
        # or renamed, and the operator resubmit is what remains for it.
        pair = (pending.as2_from, pending.as2_to)
        config = configs_by_pair.get(pair)

        if config is None:
            continue

        # A message younger than its partner's window is merely pending, not overdue.
        sent_time = datetime.fromisoformat(pending.sent_time_iso)
        overdue_seconds = _get_overdue_seconds(config)
        overdue_from = sent_time + timedelta(seconds=overdue_seconds)

        if now < overdue_from:
            continue

        # The original attempt is one of the attempts, so a partner allowing three resends
        # stops at four events under the Message-ID.
        attempt_count = count_attempts(reconciler, pending.message_id)
        max_retries = get_max_retries(config)

        if attempt_count > max_retries:
            continue

        # A message whose documents were not stored - a connection with its audit log turned off
        # records no payload to work from - has nothing to deliver again.
        documents = _get_stored_documents(reconciler, pending.message_id)

        if not documents:
            logger.info('AS2 message `%s` is overdue with no stored documents to resend', pending.message_id)
            continue

        payload, filename = _build_payload(documents)

        candidate = ResendCandidate()

        candidate.connection_name = config['name']
        candidate.as2_from = pending.as2_from
        candidate.as2_to = pending.as2_to
        candidate.message_id = pending.message_id
        candidate.delivery_kind = _get_delivery_kind(pending)
        candidate.attempt_count = attempt_count
        candidate.payload = payload
        candidate.filename = filename

        out.append(candidate)

        candidate_count = len(out)

        if candidate_count >= limit:
            break

    return out

# ################################################################################################################################
# ################################################################################################################################
