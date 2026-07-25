# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The reconciliation store - what was sent, which receipts arrived, and everything that is still
waiting for one. Storage is the same shared audit-log component the X12 acknowledgment
reconciliation reuses, with AuditSource.AS2 events.
"""

# SQLAlchemy
from sqlalchemy import and_, exists, select

# Zato
from zato.common.as2.common import DeliveryKind
from zato.common.as2.mdn import normalize_message_id
from zato.common.as2.reconcile.common import Default_Server_Name, Max_Outstanding, new_empty_attrs, new_pending, \
    pair_key, reconcile_attr_names, ReconcileAttr
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource, event_attr_table, event_table
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.as2.reconcile.common import pending_mdn_list, PendingMDN
    from zato.common.typing_ import any_, anydict, anylist, anylistnone
    any_ = any_
    anydict = anydict
    anylist = anylist
    anylistnone = anylistnone
    datetime = datetime
    pending_mdn_list = pending_mdn_list
    PendingMDN = PendingMDN

# ################################################################################################################################
# ################################################################################################################################

class MDNReconciler:
    """ Records what was sent and which MDNs arrived, exposing everything
    that is still waiting for its receipt.
    """

    def __init__(self, server_name:'str' = Default_Server_Name) -> 'None':
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
        pair = pair_key(as2_from, as2_to)
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
        pending:'PendingMDN | None',
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
            pair = pair_key(pending.as2_from, pending.as2_to)
        else:
            pair = ''

        values = {'cid': cid, 'msg_id': message_id, 'outcome': outcome, 'data': data}

        self.audit_log.insert(AuditSource.AS2, AuditEvent.MDN_Received, pair, **values)

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
            out[event_id] = new_empty_attrs()

        if not event_ids:
            return out

        is_wanted_event = event_attr_table.c.event_id.in_(event_ids)
        is_wanted_attr = event_attr_table.c.name.in_(reconcile_attr_names)
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

    def match(self, message_id:'str') -> 'PendingMDN | None':
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

        out = new_pending(object_name, msg_id, event_time_iso, cid, attrs)
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

            item = new_pending(object_name, msg_id, event_time_iso, cid, attrs)
            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
