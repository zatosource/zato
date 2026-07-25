# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# MDN reconciliation - a small state tracker persisting the Message-ID, the expected MIC
# and the asynchronous delivery URL of each sent message, and matching incoming MDNs
# against them, so a missing MDN is detectable. Storage is the same shared audit-log
# component the X12 acknowledgment reconciliation reuses, with AuditSource.AS2 events.

from __future__ import annotations

# stdlib
from dataclasses import dataclass
from logging import getLogger

# SQLAlchemy
from sqlalchemy import and_, exists, select

# Zato
from zato.common.as2.audit import encode_raw_mime
from zato.common.as2.common import AS2Exception, DeliveryKind, is_digest_equal
from zato.common.as2.mdn import DispositionType, ModifierKind, normalize_message_id, parse_mdn
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource, event_attr_table, event_table
from zato.common.json_internal import dumps
from zato.common.typing_ import optional

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.as2.mdn import MDNDetails
    from zato.common.typing_ import any_, anydict, anylist, anylistnone, strstrdict
    from zato.common.util.xml_.keystore import certificate_list, Keystore
    any_ = any_
    anydict = anydict
    anylist = anylist
    anylistnone = anylistnone
    certificate_list = certificate_list
    datetime = datetime
    Keystore = Keystore
    MDNDetails = MDNDetails
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
pending_mdn_list = list['PendingMDN']

certificatelistnone = optional['certificate_list']
keystorenone        = optional['Keystore']
mdndetailsnone      = optional['MDNDetails']
pendingmdnnone      = optional['PendingMDN']

# ################################################################################################################################
# ################################################################################################################################

# The server name reconciliation events are recorded under when none is given.
Default_Server_Name = 'as2-reconciler'

# How many open messages one call to outstanding may return. The alerting job and the automatic
# resend both run on it, and a partner outage over a weekend would otherwise have them read every
# unanswered message at once - a bounded batch keeps a long outage from turning either job into
# a memory event, with the next run picking up where this one stopped.
Max_Outstanding = 5_000

# ################################################################################################################################
# ################################################################################################################################

class ReconcileAttr:
    """ The searchable attributes a message-sent event carries. They are what reconciliation reads,
    which is why they are columns of their own rather than fields inside the event data - the data
    of a message-sent event also holds every document that went out, and reading a digest is not
    a reason to pull a whole interchange out of the database.
    """
    MIC           = 'mic'
    Async_MDN_URL = 'async_mdn_url'
    Delivery_Kind = 'delivery_kind'
    HTTP_Status   = 'http_status'

# ################################################################################################################################

# Everything one open message is described by, in the order the two queries fill it in.
_reconcile_attr_names = (
    ReconcileAttr.MIC,
    ReconcileAttr.Async_MDN_URL,
    ReconcileAttr.Delivery_Kind,
    ReconcileAttr.HTTP_Status,
)

# ################################################################################################################################
# ################################################################################################################################

def _pair_key(as2_from:'str', as2_to:'str') -> 'str':
    """ Builds the storage key of one AS2 identity pair.
    """
    as2_from = as2_from.strip()
    as2_to = as2_to.strip()

    out = f'{as2_from}:{as2_to}'
    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PendingMDN:
    """ One sent message whose MDN has not arrived.
    """
    as2_from:      str = ''
    as2_to:        str = ''
    message_id:    str = ''
    mic:           str = ''
    async_mdn_url: str = ''
    sent_time_iso: str = ''
    cid:           str = ''

    # Which of the reliability taxonomy this attempt was, and what the partner's HTTP layer
    # answered it with - the automatic resend reads both to decide what to do next.
    delivery_kind: str = ''
    http_status:   int = 0

# ################################################################################################################################

def _new_pending(object_name:'str', msg_id:'str', event_time_iso:'str', cid:'str', attrs:'strstrdict') -> 'PendingMDN':
    """ Turns one message-sent event and its attributes into the pending message they describe.
    An attribute an older event was recorded without reads as its own default - no digest to
    reconcile against, no asynchronous destination, and an original attempt whose transport
    outcome is not known.
    """
    as2_from, as2_to = object_name.split(':', 1)

    out = PendingMDN()

    out.as2_from = as2_from
    out.as2_to = as2_to
    out.message_id = msg_id
    out.sent_time_iso = event_time_iso
    out.cid = cid

    out.mic = attrs[ReconcileAttr.MIC]
    out.async_mdn_url = attrs[ReconcileAttr.Async_MDN_URL]

    delivery_kind = attrs[ReconcileAttr.Delivery_Kind]

    if delivery_kind:
        out.delivery_kind = delivery_kind
    else:
        out.delivery_kind = DeliveryKind.Original

    if http_status := attrs[ReconcileAttr.HTTP_Status]:
        out.http_status = int(http_status)

    return out

# ################################################################################################################################

def _new_empty_attrs() -> 'strstrdict':
    """ The attribute set of one event before the database has said anything about it, so that
    an event recorded without an attribute reads the same as one whose attribute is empty.
    """
    out:'strstrdict' = {}

    for name in _reconcile_attr_names:
        out[name] = ''

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MDNMatchResult:
    """ The outcome of matching one incoming MDN against the reconciliation store.
    """
    # Whether the body parsed and verified as an MDN at all.
    is_parsed: bool = False

    # Whether the MDN answered a message the store was waiting for.
    is_matched: bool = False

    # Whether the matched MDN reports clean processing and its MIC agrees
    # with the one computed at send time.
    is_ok: bool = False

    # The parsed MDN, when the body parsed at all.
    mdn: 'mdndetailsnone' = None

    # The sent message the MDN answered, when one matched.
    pending: 'pendingmdnnone' = None

# ################################################################################################################################
# ################################################################################################################################

class MDNReconciler:
    """ Records what was sent and which MDNs arrived, exposing everything
    that is still waiting for its receipt.
    """

    def __init__(self, server_name:'str'=Default_Server_Name) -> 'None':
        self.audit_log = AuditLog(server_name)
        self.engine = self.audit_log.engine

# ################################################################################################################################

    def record_message_sent(
        self,
        as2_from:'str',
        as2_to:'str',
        message_id:'str',
        mic:'str' = '',
        async_mdn_url:'str' = '',
        cid:'str' = '',
        correl_id:'str' = '',
        payload:'str' = '',
        filename:'str' = '',
        raw_mime:'str' = '',
        payloads:'anylistnone' = None,
        delivery_kind:'str' = DeliveryKind.Original,
        http_status:'int' = 0,
        ) -> 'None':
        """ Records that a message left for the partner - the send half of the reconciliation pair.
        The MIC computed at send time and the URL an asynchronous MDN is expected on travel
        in the event data, so the returned MDN can reconcile against them. Every document travels
        there too, which is what a later resend runs on, and an operator resend of a stored message
        links back to the original event through the correlation id. The raw MIME body that went
        over the wire is kept alongside as delivery evidence.

        The delivery kind says which of the reliability taxonomy this attempt was, and the HTTP
        status is what the automatic resend reads to tell a delivery the partner never accepted
        from one it accepted and then never answered.
        """
        pair = _pair_key(as2_from, as2_to)
        message_id = normalize_message_id(message_id)

        if payloads is None:
            payloads = []

        details = {'mic': mic, 'async_mdn_url': async_mdn_url, 'payload': payload, 'filename': filename,
            'raw_mime': raw_mime, 'payloads': payloads, 'delivery_kind': delivery_kind, 'http_status': http_status}
        data = dumps(details)

        # What reconciliation needs goes in as attributes as well as into the data, so that
        # matching a receipt never reads the documents the data carries alongside it.
        attrs = {
            ReconcileAttr.MIC: mic,
            ReconcileAttr.Async_MDN_URL: async_mdn_url,
            ReconcileAttr.Delivery_Kind: delivery_kind,
            ReconcileAttr.HTTP_Status: http_status,
        }

        values = {'cid': cid, 'msg_id': message_id, 'correl_id': correl_id, 'data': data, 'attrs': attrs}

        self.audit_log.insert(AuditSource.AS2, AuditEvent.Message_Sent, pair, **values)

# ################################################################################################################################

    def record_mdn_received(
        self,
        message_id:'str',
        outcome:'str' = AuditOutcome.OK,
        cid:'str' = '',
        data:'str' = '',
        ) -> 'None':
        """ Records that an MDN arrived - matched or not, the arrival is always recorded,
        because an MDN for an unknown or already-reconciled Message-ID is accepted
        and logged, never errored.
        """
        message_id = normalize_message_id(message_id)

        # The sent message this receipt answers names the event by its identity pair.
        pending = self.match(message_id)

        self.record_mdn_received_for(message_id, pending, outcome=outcome, cid=cid, data=data)

# ################################################################################################################################

    def record_mdn_received_for(
        self,
        message_id:'str',
        pending:'pendingmdnnone',
        outcome:'str' = AuditOutcome.OK,
        cid:'str' = '',
        data:'str' = '',
        ) -> 'None':
        """ Records the arrival of an MDN whose sent message the caller has already resolved,
        because the alternative is running the same match query a second time for every
        receipt that arrives.
        """
        message_id = normalize_message_id(message_id)

        # A receipt answering nothing this side sent carries no identity pair at all.
        if pending:
            pair = _pair_key(pending.as2_from, pending.as2_to)
        else:
            pair = ''

        self.audit_log.insert(
            AuditSource.AS2, AuditEvent.MDN_Received, pair, cid=cid, msg_id=message_id, outcome=outcome, data=data)

# ################################################################################################################################

    def _no_mdn_arrived(self) -> 'any_':
        """ The condition selecting a message-sent event no MDN has answered yet - an MDN matches
        on the same Message-ID, whichever attempt at the message earned it.
        """
        mdn = event_table.alias('mdn')

        mdn_conditions = and_(
            mdn.c.source == AuditSource.AS2,
            mdn.c.event_type == AuditEvent.MDN_Received,
            mdn.c.msg_id == event_table.c.msg_id,
        )
        mdn_select = select(mdn.c.id).where(mdn_conditions)
        mdn_exists = exists(mdn_select)

        out = ~mdn_exists
        return out

# ################################################################################################################################

    def _read_attrs(self, connection:'any_', event_ids:'anylist') -> 'anydict':
        """ Reads the reconciliation attributes of the given events, one query for all of them,
        with every event described whether the database had anything to say about it or not.
        """
        out:'anydict' = {}

        for event_id in event_ids:
            out[event_id] = _new_empty_attrs()

        if not event_ids:
            return out

        is_wanted_event = event_attr_table.c.event_id.in_(event_ids)
        is_wanted_attr = event_attr_table.c.name.in_(_reconcile_attr_names)
        conditions = and_(is_wanted_event, is_wanted_attr)

        statement = select(
            event_attr_table.c.event_id,
            event_attr_table.c.name,
            event_attr_table.c.value,
        ).where(conditions)

        result = connection.execute(statement)

        for event_id, name, value in result:
            event_attrs = out[event_id]
            event_attrs[name] = value

        return out

# ################################################################################################################################

    def match(self, message_id:'str') -> 'pendingmdnnone':
        """ Returns the sent message the given Message-ID belongs to, provided its MDN
        has not arrived yet, or None for an unknown or already-reconciled one.
        """
        message_id = normalize_message_id(message_id)
        no_mdn_arrived = self._no_mdn_arrived()

        conditions = and_(
            event_table.c.source == AuditSource.AS2,
            event_table.c.event_type == AuditEvent.Message_Sent,
            event_table.c.msg_id == message_id,
            no_mdn_arrived,
        )

        statement = select(
            event_table.c.id,
            event_table.c.object_name,
            event_table.c.msg_id,
            event_table.c.event_time_iso,
            event_table.c.cid,
        ).where(conditions).order_by(event_table.c.id)

        with self.engine.connect() as connection:

            result = connection.execute(statement)
            row = result.first()

            # An unknown or already-reconciled Message-ID matches nothing ..
            if row is None:
                return None

            # .. and a pending one has what it was sent with in its attributes.
            event_id, object_name, msg_id, event_time_iso, cid = row
            attrs_by_event_id = self._read_attrs(connection, [event_id])

        attrs = attrs_by_event_id[event_id]

        out = _new_pending(object_name, msg_id, event_time_iso, cid, attrs)
        return out

# ################################################################################################################################

    def outstanding(self, older_than:'datetime', limit:'int' = Max_Outstanding) -> 'pending_mdn_list':
        """ Returns every message sent before the given moment whose MDN has not arrived -
        what the alerting job and the automatic resend both run on - up to the given limit,
        oldest first, so a long partner outage is worked through over several runs rather
        than read into memory in one.

        One message is one entry no matter how many attempts it took, and the entry describes the
        most recent attempt. Every attempt records its own message-sent event under the same
        Message-ID, so a resent message would otherwise come back once per attempt - which would
        mean one alert per attempt and, worse, one further resend per attempt.
        """
        cutoff_iso = older_than.isoformat()
        no_mdn_arrived = self._no_mdn_arrived()

        conditions = and_(
            event_table.c.source == AuditSource.AS2,
            event_table.c.event_type == AuditEvent.Message_Sent,
            event_table.c.event_time_iso < cutoff_iso,
            no_mdn_arrived,
        )

        statement = select(
            event_table.c.id,
            event_table.c.object_name,
            event_table.c.msg_id,
            event_table.c.event_time_iso,
            event_table.c.cid,
        ).where(conditions).order_by(event_table.c.id).limit(limit)

        with self.engine.connect() as connection:

            result = connection.execute(statement)
            rows = result.fetchall()

            event_ids:'anylist' = []

            for row in rows:
                event_ids.append(row[0])

            attrs_by_event_id = self._read_attrs(connection, event_ids)

        # The rows arrive oldest first, so each attempt overwrites the earlier one under the same
        # Message-ID and what remains per key is the most recent attempt, in the order the messages
        # were first sent.
        latest_by_message_id:'anydict' = {}

        for row in rows:
            msg_id = row[2]
            latest_by_message_id[msg_id] = row

        # Our response to produce
        out:'pending_mdn_list' = []

        for row in latest_by_message_id.values():
            event_id, object_name, msg_id, event_time_iso, cid = row
            attrs = attrs_by_event_id[event_id]

            item = _new_pending(object_name, msg_id, event_time_iso, cid, attrs)
            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################

def _is_mdn_ok(mdn:'MDNDetails', pending:'PendingMDN') -> 'bool':
    """ Tells whether an MDN reports clean processing of the message it answers,
    with its Received-Content-MIC agreeing with the one computed at send time.
    """

    # The disposition must report clean processing - a warning still counts as processed ..
    if mdn.disposition != DispositionType.Processed:
        return False

    if mdn.modifier_kind == ModifierKind.Error:
        return False

    if mdn.modifier_kind == ModifierKind.Failure:
        return False

    # .. and the Received-Content-MIC must match what was computed at send time.
    if mdn.mic:
        sent_digest, _, sent_algorithm = pending.mic.partition(', ')

        if not is_digest_equal(mdn.mic, sent_digest):
            return False

        if mdn.mic_algorithm != sent_algorithm:
            return False

    return True

# ################################################################################################################################

def process_incoming_mdn(
    body:'bytes',
    content_type:'str',
    reconciler:'MDNReconciler',
    keystore:'keystorenone'=None,
    cid:'str'='',
    accepted_certificates:'certificatelistnone'=None,
    ) -> 'MDNMatchResult':
    """ Parses one asynchronously delivered MDN and reconciles it against the sent messages.
    Never raises - an unparseable body, an unknown Message-ID and an already-reconciled one
    are all accepted and logged, because the answer to an incoming MDN is always a plain 200.
    A non-empty accepted_certificates list is the trust decision for a signed MDN's signer.
    """

    # Our response to produce
    out = MDNMatchResult()

    # A body that does not parse and verify as an MDN is accepted and logged, nothing more.
    try:
        mdn = parse_mdn(body, content_type, keystore, accepted_certificates)
    except AS2Exception as e:
        logger.info('Incoming MDN did not parse, cid:`%s`, e:`%s`', cid, e)
        return out

    out.is_parsed = True
    out.mdn = mdn

    message_id = normalize_message_id(mdn.original_message_id)

    # What the MDN reported, kept alongside the arrival event - the raw MDN bytes
    # are the partner's signed receipt, which is the evidence half of non-repudiation.
    raw_mime = encode_raw_mime(body)

    mdn_details = {'disposition': mdn.disposition, 'modifier_kind': mdn.modifier_kind, 'modifier': mdn.modifier,
        'mic': mdn.mic, 'raw_mime': raw_mime}
    mdn_data = dumps(mdn_details)

    # An unknown or already-reconciled Message-ID is accepted and logged, never errored ..
    pending = reconciler.match(message_id)

    if not pending:
        logger.info('Incoming MDN matched no pending message, original id:`%s`, cid:`%s`', mdn.original_message_id, cid)
        reconciler.record_mdn_received_for(message_id, None, cid=cid, data=mdn_data)
        return out

    out.is_matched = True
    out.pending = pending

    # .. a matched one reconciles against the disposition and the MIC computed at send time.
    out.is_ok = _is_mdn_ok(mdn, pending)

    if out.is_ok:
        outcome = AuditOutcome.OK
    else:
        outcome = AuditOutcome.Error

    reconciler.record_mdn_received_for(message_id, pending, outcome=outcome, cid=cid, data=mdn_data)

    return out

# ################################################################################################################################
# ################################################################################################################################
