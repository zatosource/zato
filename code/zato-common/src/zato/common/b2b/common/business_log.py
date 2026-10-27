# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime

# SQLAlchemy
from sqlalchemy import and_, exists, select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, event_attr_table, event_table, \
    is_audit_log_enabled, ModuleCtx as AuditLogCtx
from zato.common.audit_log.common import B2BAttr
from zato.common.b2b.common.exceptions import B2BException
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.typing_ import anylist, dtnone, stranydict, strlist, strnone
    anylist = anylist
    Connection = Connection
    dtnone = dtnone
    Engine = Engine
    stranydict = stranydict
    strlist = strlist
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

business_message_list = list['BusinessMessage']
business_outcome_list = list['BusinessOutcome']

# How many transactions with a deadline one check of the deadlines looks at.
Expiry_Batch_Size = 1000

# ################################################################################################################################
# ################################################################################################################################

class BusinessState:
    """ Where the business transaction of one message sent stands - waiting for its signals and its response,
    receipted, refused at receipt or at acceptance, answered, or past a deadline without what it waited for.
    """
    Sent               = 'sent'
    Receipted          = 'receipted'
    Receipt_Refused    = 'receipt-refused'
    Acceptance_Refused = 'acceptance-refused'
    Answered           = 'answered'
    Timed_Out          = 'timed-out'

# The states each state can change to when a signal or a response arrives.
_next_states = {
    BusinessState.Sent: {
        BusinessState.Receipted,
        BusinessState.Receipt_Refused,
        BusinessState.Acceptance_Refused,
        BusinessState.Answered,
    },
    BusinessState.Receipted: {
        BusinessState.Acceptance_Refused,
        BusinessState.Answered,
    },
}

# The states after which nothing changes the transaction any more.
_final_states = (
    BusinessState.Receipt_Refused,
    BusinessState.Acceptance_Refused,
    BusinessState.Answered,
    BusinessState.Timed_Out,
)

# The event types that make up the record of one business message.
_business_event_types = (AuditEvent.Business_Message_Sent, AuditEvent.Business_Reply_Received, AuditEvent.Business_Timed_Out)

# ################################################################################################################################
# ################################################################################################################################

class _Data:
    """ The keys of the data documents the events of a business message have.
    """
    Conversation_ID   = 'conversation_id'
    Service           = 'service'
    Action            = 'action'
    Sent_At           = 'sent_at'
    Receipt_Deadline  = 'receipt_deadline'
    Response_Deadline = 'response_deadline'
    Reply_Message_ID  = 'reply_message_id'
    Errors            = 'errors'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BusinessMessage:
    """ One business message sent, with the deadlines of its business transaction and where the transaction stands.
    """
    message_id:      str
    cpa_id:          str
    conversation_id: str
    from_party:      str
    to_party:        str
    service:         str
    action:          str
    sent_at:         'datetime'

    # By when the receipt signal and the response are to arrive, None for a deadline that does not apply.
    receipt_deadline:  'dtnone' = None
    response_deadline: 'dtnone' = None

    state: str = BusinessState.Sent

    # The latest signal or response that changed the state, and the errors of an exception signal.
    reply_message_id: str = ''
    errors: 'strlist'

    def __init__(self) -> 'None':
        self.errors = []

# ################################################################################################################################

    @property
    def earliest_deadline(self) -> 'dtnone':
        """ The first deadline of the transaction, or None when no deadline applies to it.
        """
        deadlines:'anylist' = []

        for deadline in (self.receipt_deadline, self.response_deadline):
            if deadline:
                deadlines.append(deadline)

        if deadlines:
            out = min(deadlines)
        else:
            out = None

        return out

# ################################################################################################################################

    def is_past_deadline(self, now:'datetime') -> 'bool':
        """ Says whether a deadline of the transaction passed without what it waits for - the receipt signal
        while the message is not receipted, or the response while it is not answered.
        """

        # Our response to produce
        out = False

        # A transaction that ended has no deadline any more ..
        if self.state in _final_states:
            return out

        # .. the receipt is awaited only until the message is receipted ..
        if self.state == BusinessState.Sent:
            if receipt_deadline := self.receipt_deadline:
                if now > receipt_deadline:
                    out = True

        # .. and the response until the message is answered.
        if response_deadline := self.response_deadline:
            if now > response_deadline:
                out = True

        return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BusinessOutcome:
    """ What a signal, a response or a deadline did to the business transaction of one message sent.
    """
    message_id: str
    state:      str

    # The signal or the response that refers to the message, empty when a deadline passed.
    reply_message_id: str = ''

    # The error descriptions of an exception signal.
    errors: 'strlist'

    def __init__(self) -> 'None':
        self.errors = []

# ################################################################################################################################
# ################################################################################################################################

def can_change(current:'str', new:'str') -> 'bool':
    """ Says whether a transaction in the current state changes to the new one when a signal or a response arrives.
    """
    if allowed := _next_states.get(current):
        out = new in allowed
    else:
        out = False

    return out

# ################################################################################################################################

def _parse_time(value:'strnone') -> 'dtnone':
    if value:
        out = datetime.fromisoformat(value)
    else:
        out = None

    return out

# ################################################################################################################################

def _format_time(value:'dtnone') -> 'strnone':
    if value:
        out = value.isoformat()
    else:
        out = None

    return out

# ################################################################################################################################
# ################################################################################################################################

class BusinessLog:
    """ The record of the business transaction of every business message a server sends under a B2B protocol,
    kept in the audit log - the message with its deadlines, each signal and response that refers to it,
    and the passing of a deadline. Nothing is held in memory, so a transaction continues from the record after a restart.
    """

    def __init__(self, source:'str', server_name:'str') -> 'None':

        # A turned-off audit log drops every event, and a transaction cannot be followed without its record.
        if not is_audit_log_enabled():
            raise B2BException(f'The audit log is turned off through `{AuditLogCtx.Env_Enabled}` and no business ' +
                'transaction can be recorded')

        self.source = source
        self.server_name = server_name

        # Each event is committed at the moment it is recorded.
        self.audit_log = AuditLog(server_name, flush_max_size=1)

# ################################################################################################################################

    @property
    def engine(self) -> 'Engine':
        out = self.audit_log.engine
        return out

# ################################################################################################################################

    def _attrs(self, message:'BusinessMessage') -> 'stranydict':
        out:'stranydict' = {
            B2BAttr.From_Party: message.from_party,
            B2BAttr.To_Party: message.to_party,
            B2BAttr.Service: message.service,
            B2BAttr.Action: message.action,
        }

        return out

# ################################################################################################################################

    def record_sent(self, message:'BusinessMessage') -> 'None':
        """ Records a business message sent with the deadlines of its business transaction.
        """
        receipt_deadline = _format_time(message.receipt_deadline)
        response_deadline = _format_time(message.response_deadline)
        sent_at = message.sent_at.isoformat()

        data = dumps({
            _Data.Conversation_ID: message.conversation_id,
            _Data.Service: message.service,
            _Data.Action: message.action,
            _Data.Sent_At: sent_at,
            _Data.Receipt_Deadline: receipt_deadline,
            _Data.Response_Deadline: response_deadline,
        })

        attrs = self._attrs(message)

        # Only a message with a deadline is looked at again when deadlines are checked.
        if earliest_deadline := message.earliest_deadline:
            attrs[B2BAttr.Deadline_At] = earliest_deadline.isoformat()

        _ = self.audit_log.insert(self.source, AuditEvent.Business_Message_Sent, message.cpa_id, cid=message.message_id,
            msg_id=message.message_id, status=BusinessState.Sent, outcome=AuditOutcome.OK, data=data, attrs=attrs)

# ################################################################################################################################

    def record_reply(self, message:'BusinessMessage', state:'str', reply_message_id:'str', errors:'strlist') -> 'None':
        """ Records a signal or a response that changed the state of the transaction of a message.
        """
        data = dumps({
            _Data.Reply_Message_ID: reply_message_id,
            _Data.Errors: errors,
        })

        if errors:
            audit_outcome = AuditOutcome.Error
        else:
            audit_outcome = AuditOutcome.OK

        attrs = self._attrs(message)

        _ = self.audit_log.insert(self.source, AuditEvent.Business_Reply_Received, message.cpa_id, cid=message.message_id,
            msg_id=message.message_id, correl_id=reply_message_id, status=state, outcome=audit_outcome, data=data,
            attrs=attrs)

# ################################################################################################################################

    def record_timed_out(self, message:'BusinessMessage') -> 'None':
        """ Records that a deadline of the transaction of a message passed without what it waited for.
        """
        attrs = self._attrs(message)

        _ = self.audit_log.insert(self.source, AuditEvent.Business_Timed_Out, message.cpa_id, cid=message.message_id,
            msg_id=message.message_id, status=BusinessState.Timed_Out, outcome=AuditOutcome.Expired, attrs=attrs)

# ################################################################################################################################

    def _message_events(self, connection:'Connection', message_id:'str') -> 'anylist':
        """ Returns the events of one message this server sent, in the order they were recorded,
        from its latest recording as sent onwards.
        """
        conditions = and_(
            event_table.c.msg_id == message_id,
            event_table.c.source == self.source,
            event_table.c.server_name == self.server_name,
            event_table.c.event_type.in_(_business_event_types),
        )
        statement = select(event_table).where(conditions).order_by(event_table.c.id)

        result = connection.execute(statement)
        events = result.fetchall()

        # Our response to produce
        out:'anylist' = []

        for event in events:

            # A message recorded as sent again starts its record anew ..
            if event.event_type == AuditEvent.Business_Message_Sent:
                out = []

            # .. and everything recorded after it belongs to it.
            out.append(event)

        return out

# ################################################################################################################################

    def _new_message(self, events:'anylist') -> 'BusinessMessage':
        """ Builds a message out of its events, the first of which records it as sent.
        """
        first = events[0]
        first_data = loads(first.data)

        out = BusinessMessage()
        out.message_id = first.msg_id
        out.cpa_id = first.object_name
        out.conversation_id = first_data[_Data.Conversation_ID]
        out.service = first_data[_Data.Service]
        out.action = first_data[_Data.Action]
        out.sent_at = datetime.fromisoformat(first_data[_Data.Sent_At])
        out.receipt_deadline = _parse_time(first_data[_Data.Receipt_Deadline])
        out.response_deadline = _parse_time(first_data[_Data.Response_Deadline])

        # Each later event is a change of state, and the latest one says where the transaction stands.
        for event in events[1:]:
            out.state = event.status

            if event.event_type == AuditEvent.Business_Reply_Received:
                reply_data = loads(event.data)
                out.reply_message_id = reply_data[_Data.Reply_Message_ID]
                out.errors = reply_data[_Data.Errors]

        return out

# ################################################################################################################################

    def _fill_parties(self, connection:'Connection', event_id:'int', message:'BusinessMessage') -> 'None':
        """ Fills in the parties of a message from the attributes it was recorded with.
        """
        statement = select(event_attr_table.c.name, event_attr_table.c.value).where(event_attr_table.c.event_id == event_id)

        for row in connection.execute(statement):
            if row.name == B2BAttr.From_Party:
                message.from_party = row.value
            elif row.name == B2BAttr.To_Party:
                message.to_party = row.value

# ################################################################################################################################

    def _from_events(self, connection:'Connection', events:'anylist') -> 'BusinessMessage':
        """ Builds a message out of its events together with the parties it was recorded with.
        """
        first = events[0]

        out = self._new_message(events)
        self._fill_parties(connection, first.id, out)

        return out

# ################################################################################################################################

    def read(self, message_id:'str') -> 'BusinessMessage | None':
        """ Returns one business message as its transaction stands, or None if this server did not record it as sent.
        """
        with self.engine.connect() as connection:
            events = self._message_events(connection, message_id)

            # A message that was not recorded as sent is not one this server sent ..
            if not events:
                out = None

            # .. and one that was is read from its events.
            else:
                out = self._from_events(connection, events)

        return out

# ################################################################################################################################

    def awaiting(self, limit:'int') -> 'business_message_list':
        """ Returns the business messages this server sent whose transaction has a deadline and has not ended,
        the earliest one first.
        """
        later = event_table.alias()

        # A transaction ends with a final state, and a message recorded as sent again starts a new one.
        is_closing = and_(
            later.c.msg_id == event_table.c.msg_id,
            later.c.source == self.source,
            later.c.server_name == self.server_name,
            later.c.id > event_table.c.id,
            later.c.event_type.in_(_business_event_types),
            later.c.status.in_(_final_states + (BusinessState.Sent,)),
        )
        closing_select = select(later.c.id).where(is_closing)
        is_closed = exists(closing_select)

        has_deadline_conditions = and_(
            event_attr_table.c.event_id == event_table.c.id,
            event_attr_table.c.name == B2BAttr.Deadline_At,
        )
        deadline_select = select(event_attr_table.c.id).where(has_deadline_conditions)
        has_deadline = exists(deadline_select)

        conditions = and_(
            event_table.c.source == self.source,
            event_table.c.server_name == self.server_name,
            event_table.c.event_type == AuditEvent.Business_Message_Sent,
            has_deadline,
            ~is_closed,
        )

        statement = select(event_table.c.msg_id).where(conditions).order_by(event_table.c.id).limit(limit)

        out:'business_message_list' = []

        with self.engine.connect() as connection:
            result = connection.execute(statement)
            rows = result.fetchall()

            for row in rows:
                events = self._message_events(connection, row.msg_id)
                message = self._from_events(connection, events)
                out.append(message)

        return out

# ################################################################################################################################
# ################################################################################################################################

def new_business_outcome(message:'BusinessMessage') -> 'BusinessOutcome':
    """ Returns the outcome that says where the transaction of a message stands.
    """
    out = BusinessOutcome()
    out.message_id = message.message_id
    out.state = message.state
    out.reply_message_id = message.reply_message_id
    out.errors = message.errors

    return out

# ################################################################################################################################

def time_out(business_log:'BusinessLog', message:'BusinessMessage') -> 'BusinessOutcome':
    """ Ends the transaction of a message whose deadline passed.
    """
    business_log.record_timed_out(message)

    message.state = BusinessState.Timed_Out
    message.reply_message_id = ''
    message.errors = []

    out = new_business_outcome(message)
    return out

# ################################################################################################################################

def expired(business_log:'BusinessLog', now:'datetime', limit:'int'=Expiry_Batch_Size) -> 'business_outcome_list':
    """ Ends the transaction of every message whose deadline passed without the signal or the response it waits for,
    and returns the outcome of each.
    """
    out:'business_outcome_list' = []

    for message in business_log.awaiting(limit):
        if message.is_past_deadline(now):
            outcome = time_out(business_log, message)
            out.append(outcome)

    return out

# ################################################################################################################################
# ################################################################################################################################
