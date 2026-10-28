# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, event_table, is_audit_log_enabled, \
    ModuleCtx as AuditLogCtx
from zato.common.audit_log.attachment import build_attachment
from zato.common.audit_log.common import B2BAttr
from zato.common.b2b.common.commit_group import TransactionResult
from zato.common.b2b.common.commit_sql import EventWrite, write_events
from zato.common.b2b.common.exceptions import B2BException
from zato.common.b2b.common.limits import Limits
from zato.common.b2b.common.recovery import read_attrs, read_events_by_id, read_first_attachments, read_open_page, \
    RecoveredPage
from zato.common.b2b.common.records import MessageIdentity
from zato.common.b2b.common.schema import OpenKind
from zato.common.b2b.common.sequence import open_delivery
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.b2b.common.store import MessageStore
    from zato.common.b2b.common.records import StoredMessage
    from zato.common.typing_ import intlist, stranydict
    Connection = Connection
    intlist = intlist
    MessageStore = MessageStore
    StoredMessage = StoredMessage
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

received_message_list = list['ReceivedMessage']

# The name and the content type of the stored bytes of a received message.
_wire_file_name    = 'message'
_body_content_type = 'application/octet-stream'

# ################################################################################################################################
# ################################################################################################################################

class _Data:
    """ The keys of the data document of the event that records the receipt of a message.
    """
    Content_Type = 'content_type'
    Protocol     = 'protocol'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ReceivedMessage:
    """ A received message as the event that recorded its receipt has it, with what the application needs
    to process it again. The record identifier is that of its open delivery record, or 0 when it has none.
    """
    identity:     'MessageIdentity'
    cpa_id:       str
    content_type: str
    body:         bytes
    event_id:     int
    record_id:    int = 0

# ################################################################################################################################
# ################################################################################################################################

def read_received(connection:'Connection', event_ids:'intlist') -> 'dict[int, ReceivedMessage]':
    """ Returns the received messages whose receipt the given events recorded, by the event's identifier.
    """
    events = read_events_by_id(connection, event_ids)
    attrs_by_event = read_attrs(connection, event_ids)
    bodies = read_first_attachments(connection, event_ids)

    out:'dict[int, ReceivedMessage]' = {}

    for event_id, event in events.items():

        data = loads(event.data)
        attrs = attrs_by_event[event_id]

        identity = MessageIdentity(data[_Data.Protocol], attrs[B2BAttr.From_Party], attrs[B2BAttr.To_Party], event.msg_id)

        message = ReceivedMessage()
        message.identity = identity
        message.cpa_id = event.object_name
        message.content_type = data[_Data.Content_Type]
        message.body = bodies[event_id]
        message.event_id = event_id

        out[event_id] = message

    return out

# ################################################################################################################################
# ################################################################################################################################

class ReceiveLog:
    """ The record of every business message a server receives under a B2B protocol, kept in the audit log - the receipt
    of each message with its bytes, committed with its claim, and its delivery to the application, which the application
    confirms. A message whose delivery is not confirmed has an open delivery record, from which it is delivered again
    after a restart.
    """

    def __init__(self, store:'MessageStore', source:'str', server_name:'str', confirmed_status:'str') -> 'None':

        # A turned-off audit log drops every event, and a received message cannot be delivered again without its record.
        if not is_audit_log_enabled():
            raise B2BException(f'The audit log is turned off through `{AuditLogCtx.Env_Enabled}` and no message ' +
                'can be received')

        self.store = store
        self.writer = store.writer
        self.source = source
        self.server_name = server_name

        # The status of the claim of a message once the application confirmed its delivery.
        self.confirmed_status = confirmed_status

        # Builds the events that the writer commits.
        self.audit_log = AuditLog(server_name, flush_max_size=1)

        self.writer.add_event_source(source)

# ################################################################################################################################

    def _party_attrs(self, identity:'MessageIdentity') -> 'stranydict':
        out:'stranydict' = {
            B2BAttr.From_Party: identity.from_party,
            B2BAttr.To_Party: identity.to_party,
        }

        return out

# ################################################################################################################################

    def new_event(
        self,
        event_type:'str',
        identity:'MessageIdentity',
        cpa_id:'str',
        data:'stranydict',
        outcome:'str'=AuditOutcome.OK,
        ) -> 'EventWrite':
        """ Returns an event of a received message, with the parties of the message as its attributes.
        """
        attrs = self._party_attrs(identity)
        data_text = dumps(data)

        out = EventWrite()
        out.pending = self.audit_log.new_pending_event(self.source, event_type, cpa_id, cid=identity.message_id,
            msg_id=identity.message_id, outcome=outcome, data=data_text, attrs=attrs)

        return out

# ################################################################################################################################

    def received_event(
        self,
        identity:'MessageIdentity',
        cpa_id:'str',
        content_type:'str',
        body:'bytes',
        protocol_attrs:'stranydict',
        ) -> 'EventWrite':
        """ Returns the event that records the receipt of a message with its bytes, which its claim commits.
        """
        data = dumps({
            _Data.Content_Type: content_type,
            _Data.Protocol: identity.protocol,
        })

        attrs = self._party_attrs(identity)
        attrs.update(protocol_attrs)

        body_size = len(body)
        attachment = build_attachment(_wire_file_name, _body_content_type, body, max_size=Limits.Max_Message_Size_Bytes)

        out = EventWrite()
        out.pending = self.audit_log.new_pending_event(self.source, AuditEvent.Message_Received, cpa_id,
            cid=identity.message_id, msg_id=identity.message_id, size=body_size, outcome=AuditOutcome.OK, data=data,
            attrs=attrs, attachments=[attachment])

        return out

# ################################################################################################################################

    def claim(self, identity:'MessageIdentity', message:'StoredMessage', event:'EventWrite') -> 'bool':
        """ Claims a received message whose delivery begins at once, committing the claim, the event of its receipt
        and its open delivery record in one transaction. Returns True for the copy that claimed it.
        """
        event.opens.append(OpenKind.Delivery)

        out = self.store.claim(identity, message, event)
        return out

# ################################################################################################################################

    def confirm(self, identity:'MessageIdentity', cpa_id:'str') -> 'None':
        """ Confirms that the application processed a delivered message. The status of its claim, the event
        of its delivery and the closing of its delivery record commit in one transaction, and the call returns
        once they are committed.
        """
        event = self.new_event(AuditEvent.Message_Delivered, identity, cpa_id, {})
        event.closes.append(OpenKind.Delivery)

        self.store.set_status(identity, self.confirmed_status, event)

# ################################################################################################################################

    def _pending(self, page_size:'int', after_id:'int') -> 'received_message_list':

        with self.writer.engine.connect() as connection:

            records = read_open_page(connection, OpenKind.Delivery, self.source, self.server_name, after_id, page_size)

            event_ids:'intlist' = []

            for record in records:
                event_ids.append(record.event_id)

            received = read_received(connection, event_ids)

        out:'received_message_list' = []

        for record in records:
            message = received[record.event_id]
            message.record_id = record.id
            out.append(message)

        return out

# ################################################################################################################################

    def pending(self, page_size:'int', after_id:'int'=0) -> 'received_message_list':
        """ Returns, up to the page size, the received messages whose delivery the application has not confirmed,
        in the order their deliveries began, starting after the delivery record with the given identifier.
        """
        out = self.writer.call(self._pending, page_size, after_id)
        return out

# ################################################################################################################################

    def pending_page(self, page_size:'int', after_id:'int'=0) -> 'RecoveredPage':
        """ Returns one page of the received messages whose delivery the application has not confirmed.
        """
        messages = self.pending(page_size, after_id)

        out = RecoveredPage()
        out.items = messages
        out.is_last = len(messages) < page_size

        if messages:
            out.last_id = messages[-1].record_id
        else:
            out.last_id = after_id

        return out

# ################################################################################################################################

    def _read_last_received(self, message_id:'str') -> 'ReceivedMessage | None':

        conditions = and_(
            event_table.c.source == self.source,
            event_table.c.server_name == self.server_name,
            event_table.c.event_type == AuditEvent.Message_Received,
            event_table.c.msg_id == message_id,
        )
        query = select(event_table.c.id).where(conditions)
        statement = query.order_by(event_table.c.id.desc()).limit(1)

        with self.writer.engine.connect() as connection:
            if event_id := connection.execute(statement).scalar():
                received = read_received(connection, [event_id])
                out = received[event_id]
            else:
                out = None

        return out

# ################################################################################################################################

    def read(self, message_id:'str') -> 'ReceivedMessage':
        """ Returns the most recently received message with the given identifier as the event of its receipt has it.
        """
        out = self.writer.call(self._read_last_received, message_id)

        if out is None:
            raise B2BException(f'Message `{message_id}` was not received by server `{self.server_name}`')

        return out

# ################################################################################################################################

    def _reopen_delivery(self, connection:'Connection', commit_id:'str', message:'ReceivedMessage') -> 'TransactionResult':

        event = self.new_event(AuditEvent.Message_Redelivered, message.identity, message.cpa_id, {})
        event.closes.append(OpenKind.Delivery)

        _ = write_events(connection, [event], commit_id)

        # The delivery record points to the event of the receipt, which holds the bytes of the message.
        open_delivery(connection, self.source, self.server_name, message.identity.message_id, message.event_id)

        out = TransactionResult()
        out.event_writes.append(event)

        return out

# ################################################################################################################################

    def redeliver(self, message_id:'str') -> 'ReceivedMessage':
        """ Returns the most recently received message with the given identifier, read from its stored bytes, for the
        application to process again, and records that it is handed over again before returning it. Its delivery
        is open again until the application confirms it.
        """
        out = self.read(message_id)
        _ = self.writer.run_transaction(self._reopen_delivery, out)

        return out

# ################################################################################################################################
# ################################################################################################################################
