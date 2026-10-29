# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from heapq import heappop, heappush
from itertools import count
from threading import Lock

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, is_audit_log_enabled, ModuleCtx as AuditLogCtx
from zato.common.audit_log.common import B2BAttr
from zato.common.b2b.common.business_state import business_attrs, business_data, BusinessData, BusinessMessage, \
    business_sent_attrs, BusinessState, can_change, Data_Business, ends_transaction, new_business_outcome, parse_time
from zato.common.b2b.common.commit_group import get_writer
from zato.common.b2b.common.commit_sql import EventWrite
from zato.common.b2b.common.exceptions import B2BException
from zato.common.b2b.common.recovery import page_of, read_attrs, read_events, read_open_page, Recovery_Page_Size
from zato.common.b2b.common.schema import OpenKind
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.b2b.common.business_state import BusinessOutcome
    from zato.common.b2b.common.commit_group import GroupCommitWriter
    from zato.common.b2b.common.commit_ticket import CommitTicket
    from zato.common.b2b.common.recovery import RecoveredPage
    from zato.common.typing_ import anylist, stranydict, strlist
    anylist = anylist
    BusinessOutcome = BusinessOutcome
    CommitTicket = CommitTicket
    Connection = Connection
    GroupCommitWriter = GroupCommitWriter
    RecoveredPage = RecoveredPage
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

business_message_list = list['BusinessMessage']
business_outcome_list = list['BusinessOutcome']

# How many transactions with a deadline one check of the deadlines looks at.
Expiry_Batch_Size = 1000

# The event types that make up the record of one business message, a message sent through a send log included.
_business_event_types = (
    AuditEvent.Business_Message_Sent,
    AuditEvent.Message_Sent,
    AuditEvent.Business_Reply_Received,
    AuditEvent.Business_Timed_Out,
    AuditEvent.Business_Delivery_Failed,
)

# The event types that record a business message as sent.
_sent_event_types = (AuditEvent.Business_Message_Sent, AuditEvent.Message_Sent)

# ################################################################################################################################
# ################################################################################################################################

class BusinessLog:
    """ The record of the business transaction of every business message a server sends under a B2B protocol,
    kept in the audit log - the message with its deadlines, each signal and response that refers to it,
    the passing of a deadline and the failure of its delivery. The transactions that await a signal or a response
    are held in memory with their deadlines, and recover() reads them again from the audit log when a server starts.
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
            BusinessData.Reply_Message_ID: reply_message_id,
            BusinessData.Errors: errors,
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

        is_final = ends_transaction(state, message.response_deadline)

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

    def record_delivery_failed(self, message_id:'str', failure_cause:'str', failure_detail:'str') -> 'None':
        """ Ends the transaction of a business message whose delivery failed, with the cause of its last delivery,
        and returns once the record is committed. A message that has no transaction awaiting a signal
        or a response has nothing to end.
        """
        with self._lock:
            message = self._awaiting.get(message_id)

        if message is None:
            return

        # A message receipted by its partner was delivered, whatever became of its acknowledgment.
        if not can_change(message.state, BusinessState.Delivery_Failed):
            return

        data = dumps({
            BusinessData.Failure_Cause: failure_cause,
            BusinessData.Failure_Detail: failure_detail,
        })

        attrs = business_attrs(message)

        write = EventWrite()
        write.pending = self.audit_log.new_pending_event(self.source, AuditEvent.Business_Delivery_Failed,
            message.cpa_id, cid=message.message_id, msg_id=message.message_id, status=BusinessState.Delivery_Failed,
            outcome=AuditOutcome.Error, data=data, attrs=attrs)
        write.closes.append(OpenKind.Transaction)

        ticket = self._write(write)
        _ = ticket.wait()

        message.state = BusinessState.Delivery_Failed
        message.reply_message_id = ''
        message.errors = []
        message.failure_cause = failure_cause
        message.failure_detail = failure_detail

        self._forget(message_id)

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
        out.conversation_id = business[BusinessData.Conversation_ID]
        out.service = business[BusinessData.Service]
        out.action = business[BusinessData.Action]
        out.sent_at = datetime.fromisoformat(business[BusinessData.Sent_At])
        out.receipt_deadline = parse_time(business[BusinessData.Receipt_Deadline])
        out.response_deadline = parse_time(business[BusinessData.Response_Deadline])
        out.from_party = attrs[B2BAttr.From_Party]
        out.to_party = attrs[B2BAttr.To_Party]

        # Each later event of the transaction is a change of state, and the latest one says where the transaction stands.
        for event in events[start + 1:]:

            if event.event_type == AuditEvent.Business_Reply_Received:
                reply_data = loads(event.data)
                out.state = event.status
                out.reply_message_id = reply_data[BusinessData.Reply_Message_ID]
                out.errors = reply_data[BusinessData.Errors]

            elif event.event_type == AuditEvent.Business_Timed_Out:
                out.state = event.status
                out.reply_message_id = ''
                out.errors = []

            elif event.event_type == AuditEvent.Business_Delivery_Failed:
                failure_data = loads(event.data)
                out.state = event.status
                out.reply_message_id = ''
                out.errors = []
                out.failure_cause = failure_data[BusinessData.Failure_Cause]
                out.failure_detail = failure_data[BusinessData.Failure_Detail]

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

    def _recover_page(self, after_id:'int', limit:'int') -> 'RecoveredPage':

        with self.writer.engine.connect() as connection:
            records = read_open_page(connection, OpenKind.Transaction, self.source, self.server_name, after_id, limit)

            message_ids:'strlist' = []

            for record in records:
                message_ids.append(record.message_id)

            messages = self._read_stored(connection, message_ids)

        out = page_of(messages, records, after_id, limit)
        return out

# ################################################################################################################################

    def recover_page(self, limit:'int', after_id:'int'=0) -> 'RecoveredPage':
        """ Reads, up to the limit, the transactions that have not ended from the audit log into memory, in the order
        they were opened and starting after the open record with the given identifier, so that signal matching
        and expiry continue from them.
        """
        out = self.writer.call(self._recover_page, after_id, limit)

        for message in out.items:
            if not ends_transaction(message.state, message.response_deadline):
                self.track(message)

        return out

# ################################################################################################################################

    def recover(self, page_size:'int'=Recovery_Page_Size) -> 'int':
        """ Reads every transaction that has not ended from the audit log into memory, page by page,
        and returns how many there are.
        """
        out = 0
        after_id = 0

        while True:
            page = self.recover_page(page_size, after_id)
            out += len(page.items)
            after_id = page.last_id

            if page.is_last:
                break

        return out

# ################################################################################################################################
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
