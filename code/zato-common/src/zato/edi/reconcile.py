# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Acknowledgment reconciliation - a small state tracker persisting sent interchange
# control numbers and matching incoming TA1/997/999/CONTRL acknowledgments against them,
# so a missing acknowledgment is detectable. Storage is the same shared audit-log
# component the REST channel audit log reuses, with AuditSource.X12 events.

from __future__ import annotations

# SQLAlchemy
from sqlalchemy import and_, exists, select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditSource, event_table
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    datetime = datetime

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
outstanding_list = list['OutstandingInterchange']

# ################################################################################################################################
# ################################################################################################################################

# The server name reconciliation events are recorded under when none is given.
Default_Server_Name = 'edi-reconciler'

# ################################################################################################################################
# ################################################################################################################################

def _pair_key(sender:'str', receiver:'str') -> 'str':
    """ Builds the storage key of one sender-receiver identifier pair.
    """
    out = f'{sender.strip()}:{receiver.strip()}'
    return out

# ################################################################################################################################

def _normalize_control_number(value:'str') -> 'str':
    """ Normalizes a control number for matching - the zero-padded ISA13 of an outbound
    interchange and its echo in a TA1 or AK1 must compare equal, so numeric values
    lose their padding while alphanumeric EDIFACT references stay verbatim.
    """
    value = value.strip()

    if value.isdigit():
        out = str(int(value))
    else:
        out = value

    return out

# ################################################################################################################################
# ################################################################################################################################

class OutstandingInterchange:
    """ One sent interchange whose acknowledgment has not arrived.
    """

    def __init__(self) -> 'None':
        self.sender:'str' = ''
        self.receiver:'str' = ''
        self.control_number:'str' = ''
        self.sent_time_iso:'str' = ''
        self.cid:'str' = ''

# ################################################################################################################################

    def __repr__(self) -> 'str':
        out = f'<OutstandingInterchange {self.sender}:{self.receiver} {self.control_number} sent {self.sent_time_iso}>'
        return out

# ################################################################################################################################
# ################################################################################################################################

class Reconciler:
    """ Records what was sent and what was acknowledged, exposing everything
    that is still waiting for its acknowledgment.
    """

    def __init__(self, server_name:'str'=Default_Server_Name) -> 'None':
        self.audit_log = AuditLog(server_name)
        self.engine = self.audit_log.engine

# ################################################################################################################################

    def _record(
        self,
        event_type:'str',
        sender:'str',
        receiver:'str',
        control_number:'str',
        cid:'str',
        data:'str',
        doc_type:'str' = '',
        outcome:'str' = '',
        ) -> 'None':
        """ Writes one reconciliation event - the pair is the object name
        and the normalized control number is the message id. A document type
        joins the event's JSON data, which is what the business-document
        timing guard of the alerting job runs on.
        """
        pair = _pair_key(sender, receiver)
        msg_id = _normalize_control_number(control_number)

        # The document type joins whatever JSON data the caller gave - callers passing
        # a doc_type must pass JSON data or none at all.
        if doc_type:
            if data:
                details = loads(data)
            else:
                details = {}

            details['doc_type'] = doc_type
            data = dumps(details)

        self.audit_log.insert(AuditSource.X12, event_type, pair, cid=cid, msg_id=msg_id, outcome=outcome, data=data)

# ################################################################################################################################

    def record_interchange_sent(
        self,
        sender:'str',
        receiver:'str',
        control_number:'str',
        cid:'str' = '',
        data:'str' = '',
        doc_type:'str' = '',
        ) -> 'None':
        """ Records that an interchange left for the partner - the send half
        of the reconciliation pair.
        """
        self._record(AuditEvent.Interchange_Sent, sender, receiver, control_number, cid, data, doc_type)

# ################################################################################################################################

    def record_interchange_received(
        self,
        sender:'str',
        receiver:'str',
        control_number:'str',
        cid:'str' = '',
        data:'str' = '',
        doc_type:'str' = '',
        ) -> 'None':
        """ Records that an interchange arrived from the partner.
        """
        self._record(AuditEvent.Interchange_Received, sender, receiver, control_number, cid, data, doc_type)

# ################################################################################################################################

    def record_ack_sent(
        self,
        sender:'str',
        receiver:'str',
        control_number:'str',
        cid:'str' = '',
        data:'str' = '',
        ) -> 'None':
        """ Records that an acknowledgment was sent for an interchange received earlier -
        the control number is the one being acknowledged.
        """
        self._record(AuditEvent.Ack_Sent, sender, receiver, control_number, cid, data)

# ################################################################################################################################

    def record_ack_received(
        self,
        sender:'str',
        receiver:'str',
        control_number:'str',
        cid:'str' = '',
        data:'str' = '',
        outcome:'str' = '',
        ) -> 'None':
        """ Records that a TA1, 997, 999 or CONTRL arrived for an interchange sent earlier -
        the sender and receiver are the ones of the original outbound interchange
        and the control number is the one the acknowledgment echoes. An acknowledgment
        that rejected what it answered is recorded with an error outcome, which is
        what the reports count rejected 997/999 acknowledgments from.
        """
        self._record(AuditEvent.Ack_Received, sender, receiver, control_number, cid, data, outcome=outcome)

# ################################################################################################################################

    def outstanding(self, older_than:'datetime') -> 'outstanding_list':
        """ Returns every interchange sent before the given moment whose acknowledgment
        has not arrived - what an alerting job runs on to detect missing acknowledgments.
        """
        cutoff_iso = older_than.isoformat()

        # An acknowledgment matches on the same pair and control number
        ack = event_table.alias('ack')

        ack_exists = exists(
            select(ack.c.id).where(and_(
                ack.c.source == AuditSource.X12,
                ack.c.event_type == AuditEvent.Ack_Received,
                ack.c.object_name == event_table.c.object_name,
                ack.c.msg_id == event_table.c.msg_id,
            )))

        stmt = select(
            event_table.c.object_name,
            event_table.c.msg_id,
            event_table.c.event_time_iso,
            event_table.c.cid,
        ).where(and_(
            event_table.c.source == AuditSource.X12,
            event_table.c.event_type == AuditEvent.Interchange_Sent,
            event_table.c.event_time_iso < cutoff_iso,
            ~ack_exists,
        )).order_by(event_table.c.id)

        with self.engine.connect() as connection:
            rows = connection.execute(stmt).fetchall()

        # Our response to produce
        out:'outstanding_list' = []

        for object_name, msg_id, event_time_iso, cid in rows:
            sender, receiver = object_name.split(':', 1)

            item = OutstandingInterchange()
            item.sender = sender
            item.receiver = receiver
            item.control_number = msg_id
            item.sent_time_iso = event_time_iso
            item.cid = cid

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
