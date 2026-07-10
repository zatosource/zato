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
from zato.common.as2.common import AS2Exception
from zato.common.as2.mdn import DispositionType, ModifierKind, normalize_message_id, parse_mdn
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource, event_table
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.as2.mdn import MDNInfo
    from zato.common.util.xml_.keystore import certificate_list, Keystore
    certificate_list = certificate_list
    datetime = datetime
    Keystore = Keystore
    MDNInfo = MDNInfo

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
pending_mdn_list = list['PendingMDN']

# ################################################################################################################################
# ################################################################################################################################

# The server name reconciliation events are recorded under when none is given.
Default_Server_Name = 'as2-reconciler'

# ################################################################################################################################
# ################################################################################################################################

def _pair_key(as2_from:'str', as2_to:'str') -> 'str':
    """ Builds the storage key of one AS2 identity pair.
    """
    out = f'{as2_from.strip()}:{as2_to.strip()}'
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
    mdn: 'MDNInfo | None' = None

    # The sent message the MDN answered, when one matched.
    pending: 'PendingMDN | None' = None

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
        ) -> 'None':
        """ Records that a message left for the partner - the send half of the reconciliation pair.
        The MIC computed at send time and the URL an asynchronous MDN is expected on travel
        in the event data, so the returned MDN can reconcile against them. The clear payload
        and its filename travel there too, which is what a later resend runs on, and an operator
        resend of a stored message links back to the original event through the correlation id.
        The raw MIME body that went over the wire is kept alongside as delivery evidence.
        """
        pair = _pair_key(as2_from, as2_to)
        message_id = normalize_message_id(message_id)

        data = dumps({'mic': mic, 'async_mdn_url': async_mdn_url, 'payload': payload, 'filename': filename,
            'raw_mime': raw_mime})

        self.audit_log.insert(
            AuditSource.AS2, AuditEvent.Message_Sent, pair, cid=cid, msg_id=message_id, correl_id=correl_id, data=data)

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

        # The pair of the original message names the event when one is known.
        if pending := self.match(message_id):
            pair = _pair_key(pending.as2_from, pending.as2_to)
        else:
            pair = ''

        self.audit_log.insert(
            AuditSource.AS2, AuditEvent.MDN_Received, pair, cid=cid, msg_id=message_id, outcome=outcome, data=data)

# ################################################################################################################################

    def match(self, message_id:'str') -> 'PendingMDN | None':
        """ Returns the sent message the given Message-ID belongs to, provided its MDN
        has not arrived yet, or None for an unknown or already-reconciled one.
        """
        message_id = normalize_message_id(message_id)

        # An already-arrived MDN matches on the same Message-ID.
        mdn = event_table.alias('mdn')

        mdn_exists = exists(
            select(mdn.c.id).where(and_(
                mdn.c.source == AuditSource.AS2,
                mdn.c.event_type == AuditEvent.MDN_Received,
                mdn.c.msg_id == event_table.c.msg_id,
            )))

        stmt = select(
            event_table.c.object_name,
            event_table.c.msg_id,
            event_table.c.event_time_iso,
            event_table.c.cid,
            event_table.c.data,
        ).where(and_(
            event_table.c.source == AuditSource.AS2,
            event_table.c.event_type == AuditEvent.Message_Sent,
            event_table.c.msg_id == message_id,
            ~mdn_exists,
        )).order_by(event_table.c.id)

        with self.engine.connect() as connection:
            row = connection.execute(stmt).first()

        # An unknown or already-reconciled Message-ID matches nothing ..
        if row is None:
            return None

        # .. a pending one comes back with everything recorded at send time.
        object_name, msg_id, event_time_iso, cid, data = row
        as2_from, as2_to = object_name.split(':', 1)

        details = loads(data)

        out = PendingMDN()
        out.as2_from = as2_from
        out.as2_to = as2_to
        out.message_id = msg_id
        out.mic = details['mic']
        out.async_mdn_url = details['async_mdn_url']
        out.sent_time_iso = event_time_iso
        out.cid = cid

        return out

# ################################################################################################################################

    def outstanding(self, older_than:'datetime') -> 'pending_mdn_list':
        """ Returns every message sent before the given moment whose MDN has not arrived -
        what an alerting job runs on to detect missing receipts.
        """
        cutoff_iso = older_than.isoformat()

        # An MDN matches on the same Message-ID.
        mdn = event_table.alias('mdn')

        mdn_exists = exists(
            select(mdn.c.id).where(and_(
                mdn.c.source == AuditSource.AS2,
                mdn.c.event_type == AuditEvent.MDN_Received,
                mdn.c.msg_id == event_table.c.msg_id,
            )))

        stmt = select(
            event_table.c.object_name,
            event_table.c.msg_id,
            event_table.c.event_time_iso,
            event_table.c.cid,
            event_table.c.data,
        ).where(and_(
            event_table.c.source == AuditSource.AS2,
            event_table.c.event_type == AuditEvent.Message_Sent,
            event_table.c.event_time_iso < cutoff_iso,
            ~mdn_exists,
        )).order_by(event_table.c.id)

        with self.engine.connect() as connection:
            rows = connection.execute(stmt).fetchall()

        # Our response to produce
        out:'pending_mdn_list' = []

        for object_name, msg_id, event_time_iso, cid, data in rows:
            as2_from, as2_to = object_name.split(':', 1)

            details = loads(data)

            item = PendingMDN()
            item.as2_from = as2_from
            item.as2_to = as2_to
            item.message_id = msg_id
            item.mic = details['mic']
            item.async_mdn_url = details['async_mdn_url']
            item.sent_time_iso = event_time_iso
            item.cid = cid

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################

def _is_mdn_ok(mdn:'MDNInfo', pending:'PendingMDN') -> 'bool':
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

        if mdn.mic != sent_digest:
            return False

        if mdn.mic_algorithm != sent_algorithm:
            return False

    return True

# ################################################################################################################################

def process_incoming_mdn(
    body:'bytes',
    content_type:'str',
    reconciler:'MDNReconciler',
    keystore:'Keystore | None'=None,
    cid:'str'='',
    accepted_certificates:'certificate_list | None'=None,
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

    mdn_data = dumps({'disposition': mdn.disposition, 'modifier_kind': mdn.modifier_kind, 'modifier': mdn.modifier,
        'mic': mdn.mic, 'raw_mime': raw_mime})

    # An unknown or already-reconciled Message-ID is accepted and logged, never errored ..
    pending = reconciler.match(message_id)

    if not pending:
        logger.info('Incoming MDN matched no pending message, original id:`%s`, cid:`%s`', mdn.original_message_id, cid)
        reconciler.record_mdn_received(message_id, cid=cid, data=mdn_data)
        return out

    out.is_matched = True
    out.pending = pending

    # .. a matched one reconciles against the disposition and the MIC computed at send time.
    out.is_ok = _is_mdn_ok(mdn, pending)

    if out.is_ok:
        outcome = AuditOutcome.OK
    else:
        outcome = AuditOutcome.Error

    reconciler.record_mdn_received(message_id, outcome=outcome, cid=cid, data=mdn_data)

    return out

# ################################################################################################################################
# ################################################################################################################################
