# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Reading back what was sent and what has answered it. An AS4 receipt may arrive on its own, long
after the push it belongs to and on a channel of its own, so the only thing tying the two halves
together is the eb:RefToMessageId the receipt echoes. This is what resolves it: the sent message
one receipt refers to, and every message that is still waiting for one.

The store is the shared audit log, whose AuditSource.AS4 events already hold both halves - the
message-sent event with the eb:MessageId, the party pair, the eb:Service, the eb:Action and the
conversation, and the receipt-received event recorded under the same message id.
"""

from __future__ import annotations

# stdlib
from dataclasses import dataclass

# SQLAlchemy
from sqlalchemy import and_, exists, select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditSource, event_attr_table, event_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Connection
    from zato.common.typing_ import any_, anydict, anylist, strstrdict
    any_ = any_
    anydict = anydict
    anylist = anylist
    Connection = Connection
    datetime = datetime
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
pending_receipt_list = list['PendingReceipt']

# ################################################################################################################################
# ################################################################################################################################

# The server name the store records under when none is given.
Default_Server_Name = 'as4-reconciler'

# How many open messages one call to outstanding may return. A partner outage over a weekend would
# otherwise have the caller read every unanswered message at once - a bounded batch keeps a long
# outage from turning into a memory event, with the next run picking up where this one stopped.
Max_Outstanding = 5_000

# ################################################################################################################################

class ReconcileAttr:
    """ The searchable attributes a message-sent event carries. They are columns of their own rather
    than fields inside the event data because the data of a message-sent event also holds every
    payload that went out, and resolving one receipt is not a reason to read a whole message
    out of the database.
    """
    Service         = 'service'
    Action          = 'action'
    Conversation_ID = 'conversation_id'

# ################################################################################################################################

# Everything one open message is described by, beyond what its own event row says.
reconcile_attr_names = (
    ReconcileAttr.Service,
    ReconcileAttr.Action,
    ReconcileAttr.Conversation_ID,
)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PendingReceipt:
    """ One user message that was pushed and whose receipt has not arrived.
    """
    # The party pair the message went out under, which is the pair its receipt belongs to as well.
    from_party: str = ''
    to_party:   str = ''

    message_id:      str = ''
    conversation_id: str = ''
    service:         str = ''
    action:          str = ''

    # When the message left and under which correlation id, so an operator reaches
    # the whole exchange from what the store returns.
    sent_time_iso: str = ''
    cid:           str = ''

# ################################################################################################################################
# ################################################################################################################################

def _new_empty_attrs() -> 'strstrdict':
    """ The attribute set of one event before the database has said anything about it, so that
    an event recorded without an attribute reads the same as one whose attribute is empty.
    """
    out:'strstrdict' = {}

    for name in reconcile_attr_names:
        out[name] = ''

    return out

# ################################################################################################################################

def _new_pending(object_name:'str', msg_id:'str', event_time_iso:'str', cid:'str', attrs:'strstrdict') -> 'PendingReceipt':
    """ Turns one message-sent event and its attributes into the open message they describe.
    """
    from_party, to_party = object_name.split(':', 1)

    out = PendingReceipt()

    out.from_party = from_party
    out.to_party = to_party
    out.message_id = msg_id
    out.sent_time_iso = event_time_iso
    out.cid = cid

    out.service = attrs[ReconcileAttr.Service]
    out.action = attrs[ReconcileAttr.Action]
    out.conversation_id = attrs[ReconcileAttr.Conversation_ID]

    return out

# ################################################################################################################################
# ################################################################################################################################

class ReceiptReconciler:
    """ Resolves the sent message one receipt refers to and lists the messages
    that are still waiting for theirs.
    """

    def __init__(self, server_name:'str' = Default_Server_Name) -> 'None':
        self.audit_log = AuditLog(server_name)

# ################################################################################################################################

    def _no_receipt_arrived(self) -> 'any_':
        """ The condition selecting a message-sent event no receipt has answered yet - a receipt
        matches on the message id it echoed, whichever attempt at the message earned it.
        """
        receipt = event_table.alias('receipt')

        receipt_conditions = and_(
            receipt.c.source == AuditSource.AS4,
            receipt.c.event_type == AuditEvent.Receipt_Received,
            receipt.c.msg_id == event_table.c.msg_id,
        )
        receipt_select = select(receipt.c.id).where(receipt_conditions)
        receipt_exists = exists(receipt_select)

        out = ~receipt_exists
        return out

# ################################################################################################################################

    def _read_attrs(self, connection:'Connection', event_ids:'anylist') -> 'anydict':
        """ Reads the reconciliation attributes of the given events, one query for all of them,
        with every event described whether the database had anything to say about it or not.
        """
        out:'anydict' = {}

        for event_id in event_ids:
            out[event_id] = _new_empty_attrs()

        # Nothing was found, so there is nothing to describe.
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

    def _select_sent(self) -> 'any_':
        """ The columns every read of a sent message needs, in the order the readers unpack them.
        """
        out = select(
            event_table.c.id,
            event_table.c.object_name,
            event_table.c.msg_id,
            event_table.c.event_time_iso,
            event_table.c.cid,
        )

        return out

# ################################################################################################################################

    def match(self, message_id:'str') -> 'PendingReceipt | None':
        """ Returns the sent message the given eb:MessageId belongs to, provided its receipt has
        not arrived yet, or None for a message id this side never sent or already reconciled.

        A receipt that matches nothing is still recorded by the caller - an unexpected receipt is
        logged, never errored, because a partner that repeats one is not a reason to fail a request.
        """

        # A signal that echoed no message id refers to nothing that can be resolved.
        if not message_id:
            return None

        no_receipt_arrived = self._no_receipt_arrived()

        conditions = and_(
            event_table.c.source == AuditSource.AS4,
            event_table.c.event_type == AuditEvent.Message_Sent,
            event_table.c.msg_id == message_id,
            no_receipt_arrived,
        )

        statement = self._select_sent().where(conditions).order_by(event_table.c.id)

        with self.audit_log.engine.connect() as connection:

            result = connection.execute(statement)
            row = result.first()

            # An unknown or already-reconciled message id matches nothing ..
            if row is None:
                return None

            # .. and an open one has what it was sent with in its attributes.
            event_id, object_name, msg_id, event_time_iso, cid = row
            attrs_by_event_id = self._read_attrs(connection, [event_id])

        attrs = attrs_by_event_id[event_id]

        out = _new_pending(object_name, msg_id, event_time_iso, cid, attrs)
        return out

# ################################################################################################################################

    def outstanding(self, older_than:'datetime', limit:'int' = Max_Outstanding) -> 'pending_receipt_list':
        """ Returns every message pushed before the given moment whose receipt has not arrived,
        up to the given limit, oldest first.

        One message is one entry no matter how many attempts it took, and the entry describes the
        most recent attempt. Every attempt records its own message-sent event under the same message
        id, so a resent message would otherwise come back once per attempt.
        """
        cutoff_iso = older_than.isoformat()
        no_receipt_arrived = self._no_receipt_arrived()

        conditions = and_(
            event_table.c.source == AuditSource.AS4,
            event_table.c.event_type == AuditEvent.Message_Sent,
            event_table.c.event_time_iso < cutoff_iso,
            no_receipt_arrived,
        )

        statement = self._select_sent().where(conditions).order_by(event_table.c.id).limit(limit)

        with self.audit_log.engine.connect() as connection:

            result = connection.execute(statement)
            rows = result.fetchall()

            event_ids:'anylist' = []

            for row in rows:
                event_ids.append(row[0])

            attrs_by_event_id = self._read_attrs(connection, event_ids)

        # The rows arrive oldest first, so each attempt overwrites the earlier one under the same
        # message id and what remains per key is the most recent attempt, in the order the messages
        # were first sent.
        latest_by_message_id:'anydict' = {}

        for row in rows:
            msg_id = row[2]
            latest_by_message_id[msg_id] = row

        # Our response to produce
        out:'pending_receipt_list' = []

        for row in latest_by_message_id.values():
            event_id, object_name, msg_id, event_time_iso, cid = row
            attrs = attrs_by_event_id[event_id]

            item = _new_pending(object_name, msg_id, event_time_iso, cid, attrs)
            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
