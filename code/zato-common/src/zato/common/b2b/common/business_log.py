# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime
from heapq import heappop, heappush
from itertools import count
from threading import Lock

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, is_audit_log_enabled, ModuleCtx as AuditLogCtx
from zato.common.audit_log.common import B2BAttr
from zato.common.b2b.common.commit_group import get_writer
from zato.common.b2b.common.commit_sql import EventWrite
from zato.common.b2b.common.exceptions import B2BException
from zato.common.b2b.common.recovery import read_attrs, read_events, read_open
from zato.common.b2b.common.schema import OpenKind
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.b2b.common.commit_group import CommitTicket, GroupCommitWriter
    from zato.common.typing_ import anylist, dtnone, stranydict, strlist, strnone
    anylist = anylist
    CommitTicket = CommitTicket
    Connection = Connection
    dtnone = dtnone
    GroupCommitWriter = GroupCommitWriter
    stranydict = stranydict
    strlist = strlist
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

business_message_list = list['BusinessMessage']
business_outcome_list = list['BusinessOutcome']

# How many transactions with a deadline one check of the deadlines looks at.
Expiry_Batch_Size = 1000

# The key of the data document of a sent event under which the business transaction is recorded.
Data_Business = 'business'

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

# The event types that make up the record of one business message, a message sent through a send log included.
_business_event_types = (
    AuditEvent.Business_Message_Sent,
    AuditEvent.Message_Sent,
    AuditEvent.Business_Reply_Received,
    AuditEvent.Business_Timed_Out,
)

# The event types that record a business message as sent.
_sent_event_types = (AuditEvent.Business_Message_Sent, AuditEvent.Message_Sent)

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

def business_data(message:'BusinessMessage') -> 'stranydict':
    """ Returns the document a business message is recorded with when it is sent.
    """
    out:'stranydict' = {
        _Data.Conversation_ID: message.conversation_id,
        _Data.Service: message.service,
        _Data.Action: message.action,
        _Data.Sent_At: message.sent_at.isoformat(),
        _Data.Receipt_Deadline: _format_time(message.receipt_deadline),
        _Data.Response_Deadline: _format_time(message.response_deadline),
    }

    return out

# ################################################################################################################################

def business_attrs(message:'BusinessMessage') -> 'stranydict':
    """ Returns the searchable attributes of every event of a business message.
    """
    out:'stranydict' = {
        B2BAttr.From_Party: message.from_party,
        B2BAttr.To_Party: message.to_party,
        B2BAttr.Service: message.service,
        B2BAttr.Action: message.action,
    }

    return out

# ################################################################################################################################

def business_sent_attrs(message:'BusinessMessage') -> 'stranydict':
    """ Returns the searchable attributes of the event that records a business message as sent.
    """
    out = business_attrs(message)

    if earliest_deadline := message.earliest_deadline:
        out[B2BAttr.Deadline_At] = earliest_deadline.isoformat()

    return out

# ################################################################################################################################
# ################################################################################################################################

class BusinessLog:
    """ The record of the business transaction of every business message a server sends under a B2B protocol,
    kept in the audit log - the message with its deadlines, each signal and response that refers to it,
    and the passing of a deadline. The transactions that await a signal or a response are held in memory
    with their deadlines, and recover() reads them again from the audit log when a server starts.
    """

    def __init__(self, source:'str', server_name:'str', writer:'GroupCommitWriter | None'=None) -> 'None':

        # A turned-off audit log drops every event, and a transaction cannot be followed without its record.
        if not is_audit_log_enabled():
            raise B2BException(f'The audit log is turned off through `{AuditLogCtx.Env_Enabled}` and no business ' +
                'transaction can be recorded')

        if writer is None:
            writer = get_writer()

        self.source = source
        self.server_name = server_name
        self.writer:'GroupCommitWriter' = writer

        # Builds the events that the writer commits.
        self.audit_log = AuditLog(server_name, flush_max_size=1)

        # Each transaction that has not ended, by its message identifier ..
        self._lock = Lock()
        self._awaiting:'dict[str, BusinessMessage]' = {}

        # .. and the deadlines of the transactions, earliest first, with an order number that breaks ties.
        self._deadlines:'anylist' = []
        self._deadline_order = count()

        self.writer.add_event_source(source)

# ################################################################################################################################

    def track(self, message:'BusinessMessage') -> 'None':
        """ Holds in memory a transaction that awaits a signal or a response.
        """
        with self._lock:
            self._awaiting[message.message_id] = message

            for deadline in (message.receipt_deadline, message.response_deadline):
                if deadline:
                    order = next(self._deadline_order)
                    heappush(self._deadlines, (deadline, order, message.message_id))

# ################################################################################################################################

    def _forget(self, message_id:'str') -> 'None':
        """ Removes from memory a transaction that ended. Its deadlines are skipped when they come up.
        """
        with self._lock:
            _ = self._awaiting.pop(message_id, None)

# ################################################################################################################################

    def _write(self, write:'EventWrite') -> 'CommitTicket':
        out = self.writer.submit(write, write.row_count)
        return out

# ################################################################################################################################

    def record_sent(self, message:'BusinessMessage') -> 'None':
        """ Records a business message sent with the deadlines of its business transaction,
        and returns once the record is committed.
        """
        data = dumps({Data_Business: business_data(message)})
        attrs = business_sent_attrs(message)

        write = EventWrite()
        write.pending = self.audit_log.new_pending_event(self.source, AuditEvent.Business_Message_Sent, message.cpa_id,
            cid=message.message_id, msg_id=message.message_id, status=BusinessState.Sent, outcome=AuditOutcome.OK,
            data=data, attrs=attrs)

        # A message recorded as sent again starts its transaction anew.
        with self._lock:
            if message.message_id in self._awaiting:
                write.closes.append(OpenKind.Transaction)

        write.opens.append(OpenKind.Transaction)

        ticket = self._write(write)
        _ = ticket.wait()

        self.track(message)

# ################################################################################################################################

    def record_reply(self, message:'BusinessMessage', state:'str', reply_message_id:'str', errors:'strlist') -> 'None':
        """ Records a signal or a response that changed the state of the transaction of a message,
        and returns once the record is committed.
        """
        data = dumps({
            _Data.Reply_Message_ID: reply_message_id,
            _Data.Errors: errors,
        })

        if errors:
            audit_outcome = AuditOutcome.Error
        else:
            audit_outcome = AuditOutcome.OK

        attrs = business_attrs(message)

        write = EventWrite()
        write.pending = self.audit_log.new_pending_event(self.source, AuditEvent.Business_Reply_Received,
            message.cpa_id, cid=message.message_id, msg_id=message.message_id, correl_id=reply_message_id, status=state,
            outcome=audit_outcome, data=data, attrs=attrs)

        is_final = state in _final_states

        if is_final:
            write.closes.append(OpenKind.Transaction)

        ticket = self._write(write)
        _ = ticket.wait()

        message.state = state
        message.reply_message_id = reply_message_id
        message.errors = errors

        if is_final:
            self._forget(message.message_id)

# ################################################################################################################################

    def _timed_out_write(self, message:'BusinessMessage') -> 'CommitTicket':
        """ Adds the record of a deadline that passed to the next transaction, without waiting for the commit.
        """
        attrs = business_attrs(message)

        write = EventWrite()
        write.pending = self.audit_log.new_pending_event(self.source, AuditEvent.Business_Timed_Out, message.cpa_id,
            cid=message.message_id, msg_id=message.message_id, status=BusinessState.Timed_Out,
            outcome=AuditOutcome.Expired, attrs=attrs)
        write.closes.append(OpenKind.Transaction)

        out = self._write(write)
        return out

# ################################################################################################################################

    def _end_timed_out(self, message:'BusinessMessage') -> 'None':
        message.state = BusinessState.Timed_Out
        message.reply_message_id = ''
        message.errors = []

        self._forget(message.message_id)

# ################################################################################################################################

    def record_timed_out(self, message:'BusinessMessage') -> 'None':
        """ Records that a deadline of the transaction of a message passed without what it waited for,
        and returns once the record is committed.
        """
        ticket = self._timed_out_write(message)
        _ = ticket.wait()

        self._end_timed_out(message)

# ################################################################################################################################

    def record_timed_out_all(self, messages:'business_message_list') -> 'None':
        """ Records the passing of the deadlines of many transactions in as few commits as the writer makes.
        """
        tickets:'anylist' = []

        for message in messages:
            ticket = self._timed_out_write(message)
            tickets.append(ticket)

        for message, ticket in zip(messages, tickets):
            _ = ticket.wait()
            self._end_timed_out(message)

# ################################################################################################################################

    def due(self, now:'datetime', limit:'int') -> 'business_message_list':
        """ Returns, up to the limit and in the order of their deadlines, the transactions held in memory
        whose deadline passed without the signal or the response it waits for.
        """
        out:'business_message_list' = []
        due_ids:'set[str]' = set()

        with self._lock:

            while self._deadlines and len(out) < limit:

                deadline, _, message_id = self._deadlines[0]

                # The deadlines are ordered, so the first one in the future ends the check.
                if deadline >= now:
                    break

                _ = heappop(self._deadlines)

                # A transaction that ended, or one already due through its other deadline, is skipped,
                # and so is a deadline that passed without consequence, as that of a receipt that arrived.
                if message_id in due_ids:
                    continue

                if not (message := self._awaiting.get(message_id)):
                    continue

                if message.is_past_deadline(now):
                    out.append(message)
                    due_ids.add(message_id)

        return out

# ################################################################################################################################

    def awaiting(self, limit:'int') -> 'business_message_list':
        """ Returns, up to the limit, the transactions held in memory that have a deadline, the earliest one first.
        """
        with self._lock:
            messages = list(self._awaiting.values())

        with_deadline:'anylist' = []

        for message in messages:
            if earliest_deadline := message.earliest_deadline:
                with_deadline.append((earliest_deadline, message.message_id, message))

        with_deadline.sort()

        out:'business_message_list' = []

        for _, _, message in with_deadline[:limit]:
            out.append(message)

        return out

# ################################################################################################################################

    def _message_from_events(self, events:'anylist', attrs:'stranydict') -> 'BusinessMessage | None':
        """ Builds a message out of its events, from its latest recording as sent onwards,
        or returns None when none of them records it as a business message sent.
        """
        start = -1

        for idx, event in enumerate(events):
            if event.event_type in _sent_event_types:
                data = loads(event.data)
                if Data_Business in data:
                    start = idx

        if start == -1:
            return None

        first = events[start]
        first_data = loads(first.data)
        business = first_data[Data_Business]

        out = BusinessMessage()
        out.message_id = first.msg_id
        out.cpa_id = first.object_name
        out.conversation_id = business[_Data.Conversation_ID]
        out.service = business[_Data.Service]
        out.action = business[_Data.Action]
        out.sent_at = datetime.fromisoformat(business[_Data.Sent_At])
        out.receipt_deadline = _parse_time(business[_Data.Receipt_Deadline])
        out.response_deadline = _parse_time(business[_Data.Response_Deadline])
        out.from_party = attrs[B2BAttr.From_Party]
        out.to_party = attrs[B2BAttr.To_Party]

        # Each later event of the transaction is a change of state, and the latest one says where the transaction stands.
        for event in events[start + 1:]:

            if event.event_type == AuditEvent.Business_Reply_Received:
                reply_data = loads(event.data)
                out.state = event.status
                out.reply_message_id = reply_data[_Data.Reply_Message_ID]
                out.errors = reply_data[_Data.Errors]

            elif event.event_type == AuditEvent.Business_Timed_Out:
                out.state = event.status
                out.reply_message_id = ''
                out.errors = []

        return out

# ################################################################################################################################

    def _read_stored(self, connection:'Connection', message_ids:'strlist') -> 'business_message_list':
        """ Reads the given messages from the audit log, each from the event that last recorded it as sent.
        """
        events_by_message = read_events(connection, self.source, self.server_name, message_ids, _business_event_types)

        sent_events:'dict[str, int]' = {}

        for message_id, events in events_by_message.items():
            for event in events:
                if event.event_type in _sent_event_types:
                    sent_events[message_id] = event.id

        attrs_by_event = read_attrs(connection, list(sent_events.values()))

        out:'business_message_list' = []

        for message_id, events in events_by_message.items():

            if not (event_id := sent_events.get(message_id)):
                continue

            attrs = attrs_by_event[event_id]

            if message := self._message_from_events(events, attrs):
                out.append(message)

        return out

# ################################################################################################################################

    def _read_one(self, message_id:'str') -> 'BusinessMessage | None':
        with self.writer.engine.connect() as connection:
            messages = self._read_stored(connection, [message_id])

        if messages:
            out = messages[0]
        else:
            out = None

        return out

# ################################################################################################################################

    def read(self, message_id:'str') -> 'BusinessMessage | None':
        """ Returns one business message as its transaction stands, or None if this server did not record it as sent.
        A transaction that has not ended is read from memory, and one that ended from the audit log.
        """
        with self._lock:
            out = self._awaiting.get(message_id)

        if out is None:
            out = self.writer.call(self._read_one, message_id)

        return out

# ################################################################################################################################

    def _recover(self) -> 'business_message_list':
        with self.writer.engine.connect() as connection:
            open_records = read_open(connection, OpenKind.Transaction, self.source, self.server_name)
            message_ids = list(open_records)
            out = self._read_stored(connection, message_ids)

        return out

# ################################################################################################################################

    def recover(self) -> 'int':
        """ Reads the transactions that have not ended from the audit log into memory, so that signal matching
        and expiry continue from them, and returns how many there are.
        """
        messages = self.writer.call(self._recover)

        for message in messages:
            if message.state not in _final_states:
                self.track(message)

        out = len(messages)
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

    out = new_business_outcome(message)
    return out

# ################################################################################################################################

def expired(business_log:'BusinessLog', now:'datetime', limit:'int'=Expiry_Batch_Size) -> 'business_outcome_list':
    """ Ends the transaction of every message whose deadline passed without the signal or the response it waits for,
    and returns the outcome of each, in the order of the deadlines. The deadlines are read from memory.
    """
    messages = business_log.due(now, limit)
    business_log.record_timed_out_all(messages)

    out:'business_outcome_list' = []

    for message in messages:
        outcome = new_business_outcome(message)
        out.append(outcome)

    return out

# ################################################################################################################################
# ################################################################################################################################
