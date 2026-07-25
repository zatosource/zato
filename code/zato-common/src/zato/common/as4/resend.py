# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The sending half of AS4 reception awareness. A pushed message whose receipt has not arrived within
the P-Mode's retry interval is delivered again under its original eb:MessageId, which is why the
receiving side's duplicate detection is what decides whether the payload is processed once or twice.

Everything a repeat delivery needs comes out of the audit log rather than out of memory - the
message id, the payloads as they were submitted, the eb:Service and eb:Action they went out under
and the four-corner recipient they were addressed to. That is what makes the retries survive a
restart, and what makes an unanswered message eventually reportable rather than silently lost.
"""

from __future__ import annotations

# stdlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import getLogger

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.api import AS4
from zato.common.as4.audit import decode_payload_documents
from zato.common.as4.common import Default
from zato.common.as4.config import apply_reception_awareness, get_text_field, profile_presets
from zato.common.as4.reconcile import ReceiptReconciler
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table
from zato.common.json_internal import loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.pmode import ReceptionAwareness
    from zato.common.as4.reconcile import PendingReceipt
    from zato.common.typing_ import anydict, anylist, dictlist, stranydict
    anydict = anydict
    anylist = anylist
    dictlist = dictlist
    PendingReceipt = PendingReceipt
    ReceptionAwareness = ReceptionAwareness
    stranydict = stranydict

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
    """ One pushed message whose receipt has not arrived and which is to go out again unchanged.
    """
    # Which connection the message travels out through again and who it travels between.
    connection_name: str = ''
    from_party:      str = ''
    to_party:        str = ''

    # The eb:MessageId and eb:ConversationId the payloads go out under again, which are the
    # original ones - a repeat delivery is the same message, not a new one.
    message_id:      str = ''
    conversation_id: str = ''

    # The business information the message went out under, so a connection serving several
    # service and action pairs repeats each message under its own.
    service: str = ''
    action:  str = ''

    # Who the message was addressed to at the four-corner level, which is what a connection
    # using discovery looks the endpoint up by all over again.
    original_sender: str = ''
    final_recipient: str = ''

    # How many deliveries this message has already had, the first one included.
    attempt_count: int = 0

    # The payloads to deliver again, each a (bytes, content type, content id) tuple.
    documents: 'anylist'

# ################################################################################################################################
# ################################################################################################################################

def get_reception_awareness(config:'stranydict') -> 'ReceptionAwareness':
    """ Returns the reception awareness parameters one connection's messages are repeated under -
    the ones its network's profile prescribes, with whatever the connection itself configures
    overlaid on top.

    The preset is asked for directly rather than through a full P-Mode because the parameters are
    the only thing needed here, and a connection whose keystore or party identifiers are still
    incomplete has retry parameters all the same.
    """
    profile = get_text_field(config, 'as4_profile')

    if not profile:
        profile = AS4.Default.Profile

    preset = profile_presets[profile]
    pmode = preset()

    apply_reception_awareness(pmode, config)

    out = pmode.reception_awareness
    return out

# ################################################################################################################################

def _index_configs_by_pair(configs:'dictlist') -> 'anydict':
    """ Indexes the outgoing AS4 connections by their party pair, built once per run so that
    matching an unanswered message to its connection does not walk the whole list per message.
    """

    # Our response to produce
    out:'anydict' = {}

    for config in configs:
        from_party = get_text_field(config, 'as4_from_party')
        to_party = get_text_field(config, 'as4_to_party')

        out[(from_party, to_party)] = config

    return out

# ################################################################################################################################
# ################################################################################################################################

def count_attempts(reconciler:'ReceiptReconciler', message_id:'str') -> 'int':
    """ Returns how many deliveries one eb:MessageId has already had.

    Every attempt records its own message-sent event under the same message id, so counting the
    events is counting the attempts - which is exactly the state a restart must not lose and the
    reason the count is not held in memory anywhere.
    """
    conditions = and_(
        event_table.c.source == AuditSource.AS4,
        event_table.c.event_type == AuditEvent.Message_Sent,
        event_table.c.msg_id == message_id,
    )

    event_count = func.count(event_table.c.id)
    statement = select(event_count).where(conditions)

    with reconciler.audit_log.engine.connect() as connection:
        result = connection.execute(statement)
        out = result.scalar()

    return out

# ################################################################################################################################

def get_stored_details(reconciler:'ReceiptReconciler', message_id:'str') -> 'stranydict':
    """ Returns what the most recent attempt at one eb:MessageId was recorded with - the payloads
    it delivered and the addressing it delivered them under.
    """
    conditions = and_(
        event_table.c.source == AuditSource.AS4,
        event_table.c.event_type == AuditEvent.Message_Sent,
        event_table.c.msg_id == message_id,
    )

    newest_first = event_table.c.id.desc()
    statement = select(event_table.c.data).where(conditions).order_by(newest_first)

    with reconciler.audit_log.engine.connect() as connection:
        result = connection.execute(statement)
        row = result.first()

    # A message with no event behind it, or one whose event kept no data, is not repeatable - the
    # caller reads that from the empty result rather than from an exception, because a run over the
    # whole outstanding set must not stop at one unusable entry.
    if row is None:
        return {}

    data = row[0]

    if not data:
        return {}

    out = loads(data)
    return out

# ################################################################################################################################

def is_pull_message(details:'stranydict') -> 'bool':
    """ Tells whether one recorded message was handed over on a pull request rather than pushed. The
    flag is absent from everything recorded by a push, which is what an unset one means here.
    """
    value = details.get('is_pull')

    out = value is True
    return out

# ################################################################################################################################

def _new_candidate(pending:'PendingReceipt', config:'stranydict', details:'stranydict', documents:'anylist',
    attempt_count:'int') -> 'ResendCandidate':
    """ Turns one unanswered message and what it was sent with into the repeat delivery it becomes.
    """

    # Our response to produce
    out = ResendCandidate()

    out.connection_name = config['name']
    out.from_party = pending.from_party
    out.to_party = pending.to_party
    out.message_id = pending.message_id
    out.conversation_id = pending.conversation_id
    out.service = pending.service
    out.action = pending.action
    out.attempt_count = attempt_count
    out.documents = documents

    # The four-corner endpoints are stored with the send, and a message that was not four-corner
    # was recorded without them.
    out.original_sender = details['original_sender']
    out.final_recipient = details['final_recipient']

    return out

# ################################################################################################################################
# ################################################################################################################################

def collect_candidates(
    configs:'dictlist',
    now:'datetime',
    server_name:'str',
    limit:'int' = AS4.Resend.Batch_Size,
    ) -> 'resend_candidate_list':
    """ Returns the messages whose receipt is overdue and which have attempts left, up to one batch.

    The batch is what keeps a partner outage from turning one run into a burst of every message
    sent during it - the rest stays outstanding and the next run picks it up.
    """

    # Our response to produce
    out:'resend_candidate_list' = []

    reconciler = ReceiptReconciler(server_name)
    configs_by_pair = _index_configs_by_pair(configs)

    for pending in reconciler.outstanding(now):

        # A message with no connection behind it cannot be repeated - the connection was deleted or
        # its parties were changed, and the operator resubmit is what remains for it.
        pair = (pending.from_party, pending.to_party)
        config = configs_by_pair.get(pair)

        if config is None:
            continue

        awareness = get_reception_awareness(config)

        # A connection that does not use the feature delivers once and lets whatever came back stand.
        if not awareness.is_enabled:
            continue

        if not awareness.retry:
            continue

        sent_time = datetime.fromisoformat(pending.sent_time_iso)

        # A message whose last attempt is younger than the retry interval is merely unanswered,
        # not overdue - the partner is still within the window it was given to answer in.
        overdue_from = sent_time + timedelta(seconds=awareness.retry_interval_seconds)

        if now < overdue_from:
            continue

        # Past the point where the receipt counts as missing rather than late, repeating the
        # delivery is no longer what the exchange needs - reporting it is.
        missing_from = sent_time + timedelta(seconds=awareness.missing_receipt_seconds)

        if now >= missing_from:
            continue

        # The first delivery is one of the attempts, so a connection allowing four of them
        # stops once four message-sent events stand under the message id.
        attempt_count = count_attempts(reconciler, pending.message_id)

        if attempt_count >= awareness.retry_max_attempts:
            continue

        # A message whose payloads were not stored - a connection with its audit log turned off
        # records none to work from - has nothing to deliver again.
        details = get_stored_details(reconciler, pending.message_id)

        # A message handed over on a pull goes back on the channel it was queued on for the partner
        # to ask for again, which the pull store's own requeue does - pushing it would deliver it
        # in a direction this exchange does not have.
        if is_pull_message(details):
            continue

        documents = decode_payload_documents(details)

        if not documents:
            logger.info('AS4 message `%s` is overdue with no stored payloads to resend', pending.message_id)
            continue

        candidate = _new_candidate(pending, config, details, documents, attempt_count)
        out.append(candidate)

        candidate_count = len(out)

        if candidate_count >= limit:
            break

    return out

# ################################################################################################################################
# ################################################################################################################################

def collect_missing_receipts(
    configs:'dictlist',
    now:'datetime',
    server_name:'str',
    ) -> 'anylist':
    """ Returns the messages whose receipt never arrived within the window they were given, which
    is the point at which an unanswered exchange stops being a retry matter and becomes one an
    operator has to know about.
    """

    # Our response to produce
    out:'anylist' = []

    reconciler = ReceiptReconciler(server_name)
    configs_by_pair = _index_configs_by_pair(configs)

    for pending in reconciler.outstanding(now):

        pair = (pending.from_party, pending.to_party)
        config = configs_by_pair.get(pair)

        # A message whose connection is gone is still one nobody answered, so the window
        # the profile presets define is what places it.
        if config is None:
            missing_receipt_seconds = Default.Missing_Receipt_Seconds
        else:
            awareness = get_reception_awareness(config)
            missing_receipt_seconds = awareness.missing_receipt_seconds

        sent_time = datetime.fromisoformat(pending.sent_time_iso)
        missing_from = sent_time + timedelta(seconds=missing_receipt_seconds)

        if now < missing_from:
            continue

        out.append(pending)

    return out

# ################################################################################################################################
# ################################################################################################################################
