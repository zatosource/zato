# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from dataclasses import dataclass
from threading import Lock

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, is_audit_log_enabled, ModuleCtx as AuditLogCtx
from zato.common.audit_log.attachment import build_attachment
from zato.common.audit_log.common import AuditLink, B2BAttr
from zato.common.b2b.common.business_state import business_data, business_sent_attrs, Data_Business
from zato.common.b2b.common.commit_group import get_writer
from zato.common.b2b.common.commit_sql import EventWrite
from zato.common.b2b.common.exceptions import B2BException
from zato.common.b2b.common.limits import Limits
from zato.common.b2b.common.outcome import FinalState, outcome_to_dict
from zato.common.b2b.common.recovery import page_of, read_bodies, read_open_page, Recovery_Page_Size
from zato.common.b2b.common.schema import OpenKind
from zato.common.b2b.common.send_record import read_stored, SentData, SentInternalData, SentMessage, sent_message_list
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.b2b.common.business_log import BusinessLog
    from zato.common.b2b.common.business_state import BusinessMessage
    from zato.common.b2b.common.clock import Clock
    from zato.common.b2b.common.commit_group import GroupCommitWriter
    from zato.common.b2b.common.outcome import Outcome
    from zato.common.b2b.common.recovery import RecoveredPage
    from zato.common.typing_ import anydict, anylist, stranydict, strlist, strstrdict
    anydict = anydict
    anylist = anylist
    BusinessLog = BusinessLog
    BusinessMessage = BusinessMessage
    Clock = Clock
    Connection = Connection
    Engine = Engine
    GroupCommitWriter = GroupCommitWriter
    Outcome = Outcome
    RecoveredPage = RecoveredPage
    stranydict = stranydict
    strlist = strlist
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The names and the content type of the stored message and of a stored signal.
_wire_file_name     = 'message'
_signal_file_name   = 'signal'
_body_content_type  = 'application/octet-stream'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _Exchange:
    """ An exchange that has not ended, held in memory with the deliveries and the signals that did not end it.
    """
    sent: 'SentMessage'

    # When each delivery was made.
    attempts: 'strlist'

    # The signals that answered the message, and their bytes.
    signals: 'anylist'
    signal_bodies: 'list[bytes]'

    def __init__(self) -> 'None':
        self.attempts = []
        self.signals = []
        self.signal_bodies = []

# ################################################################################################################################
# ################################################################################################################################

class SendLog:
    """ The record of every message a server sends under a B2B protocol, kept in the audit log - the first delivery
    of each message with its bytes, and the end of each exchange with its deliveries and signals. The exchanges that
    have not ended are held in memory, and recover() reads them again from the audit log when a server starts.
    """

    def __init__(
        self,
        source:'str',
        server_name:'str',
        clock:'Clock',
        writer:'GroupCommitWriter | None' = None,
        business_log:'BusinessLog | None' = None,
        ) -> 'None':

        # A turned-off audit log drops every event, and the delivery of a message cannot continue without its record.
        if not is_audit_log_enabled():
            raise B2BException(f'The audit log is turned off through `{AuditLogCtx.Env_Enabled}` and no message can be sent')

        if writer is None:
            writer = get_writer()

        self.source = source
        self.server_name = server_name
        self.clock = clock
        self.writer:'GroupCommitWriter' = writer

        # The business transactions of the business messages this log sends.
        self.business_log = business_log

        # Builds the events that the writer commits.
        self.audit_log = AuditLog(server_name, flush_max_size=1)

        # Each exchange that has not ended, by its message identifier.
        self._lock = Lock()
        self._open:'dict[str, _Exchange]' = {}

        self.writer.add_event_source(source)

# ################################################################################################################################

    @property
    def engine(self) -> 'Engine':
        out = self.writer.engine
        return out

# ################################################################################################################################

    def _party_attrs(self, sent:'SentMessage') -> 'stranydict':
        """ Returns the attributes every event of a message has.
        """
        out:'stranydict' = {
            B2BAttr.From_Party: sent.from_party,
            B2BAttr.To_Party: sent.to_party,
        }
        out.update(sent.attrs)

        return out

# ################################################################################################################################

    def _write(self, write:'EventWrite') -> 'int':
        """ Commits one event through the writer and returns its identifier.
        """
        ticket = self.writer.submit(write, write.row_count)

        out = ticket.wait()
        return out

# ################################################################################################################################

    def is_open(self, message_id:'str') -> 'bool':
        """ Says whether the exchange of a message has not ended.
        """
        with self._lock:
            out = message_id in self._open

        return out

# ################################################################################################################################

    def record_first_attempt(
        self,
        sent:'SentMessage',
        business:'BusinessMessage | None'=None,
        resubmit_of:'int'=0,
        ) -> 'None':
        """ Records the first delivery of a message together with everything its later deliveries and the rebuilding
        of the message require - the retry policy, the expiry, the protocol's details and the wire form itself.
        A business message is recorded as sent with its business transaction in the same event. A delivery is recorded
        before it is made, so that a signal which answers it before its response arrives finds the message, and the call
        returns once the record is committed. A first delivery under a MessageId that is open already starts the record anew.
        A message that reprocesses another one is linked to the first delivery of that one, given by its event.
        """
        parents:'list[int]' = []

        if resubmit_of:
            parents.append(resubmit_of)

        wire_size = len(sent.wire_body)
        max_size = Limits.Max_Message_Size_Bytes

        # A resend sends the same bytes again, so they are always stored, up to the size a message may have.
        if wire_size > max_size:
            raise B2BException(f'Message `{sent.message_id}` has {wire_size} bytes, more than the {max_size} a message may have')

        if business and not self.business_log:
            raise B2BException(f'Message `{sent.message_id}` is a business message and the send log has no business log')

        retry_state = sent.retry_state

        if expires_at := retry_state.expires_at:
            expires_at = expires_at.isoformat()

        initial_outcome = outcome_to_dict(sent.outcome)

        data:'stranydict' = {
            SentData.Retries: sent.policy.retries,
            SentData.Retry_Interval: sent.policy.retry_interval.total_seconds(),
            SentData.Expires_At: expires_at,
            SentData.Headers: sent.wire_headers,
            SentData.Details: sent.details,
            SentData.Outcome: initial_outcome,
        }

        internal_data:'stranydict' = {
            SentInternalData.Details: sent.internal_details,
            SentInternalData.Payload_Digests: sent.outcome.payload_digests,
        }

        now = self.clock.now()
        attempt_at = now.isoformat()

        attrs = self._party_attrs(sent)
        attrs[B2BAttr.Attempt] = 1
        attrs[B2BAttr.Attempt_At] = attempt_at

        write = EventWrite()

        if self.is_open(sent.message_id):
            write.closes.append(OpenKind.Exchange)

        write.opens.append(OpenKind.Exchange)

        # A business message opens its business transaction in the same event.
        if business:
            data[Data_Business] = business_data(business)
            attrs.update(business_sent_attrs(business))
            write.opens.append(OpenKind.Transaction)

        attachment = build_attachment(_wire_file_name, _body_content_type, sent.wire_body, max_size=max_size)

        write.pending = self.audit_log.new_pending_event(self.source, AuditEvent.Message_Sent, sent.cpa_id,
            cid=sent.message_id, msg_id=sent.message_id, endpoint=sent.endpoint, size=wire_size, outcome=AuditOutcome.OK,
            data=dumps(data), internal_data=dumps(internal_data), attrs=attrs, attachments=[attachment], parents=parents,
            parent_link_type=AuditLink.Resubmit_Of)

        event_id = self._write(write)

        sent.wire_event_id = event_id

        retry_state.attempt_count = 1
        retry_state.last_attempt_at = now

        exchange = _Exchange()
        exchange.sent = sent
        exchange.attempts.append(attempt_at)

        with self._lock:
            self._open[sent.message_id] = exchange

        if business and self.business_log:
            self.business_log.track(business)

# ################################################################################################################################

    def _read_wire_body(self, event_id:'int') -> 'bytes':
        with self.engine.connect() as connection:
            bodies = read_bodies(connection, event_id)

        out = bodies[0]
        return out

# ################################################################################################################################

    def wire_body(self, message_id:'str') -> 'bytes':
        """ Returns the bytes of a message for its delivery. The first delivery takes the bytes held since the message
        was recorded and they are no longer held after it, and each later delivery reads them with one select
        by the identifier of the event they are stored with.
        """
        with self._lock:
            if exchange := self._open.get(message_id):
                sent = exchange.sent
                out = sent.wire_body
                sent.wire_body = b''
                event_id = sent.wire_event_id
            else:
                out = b''
                event_id = 0

        if not out:

            # A message whose exchange ended is read from the audit log first.
            if not event_id:
                sent = self.get(message_id)
                event_id = sent.wire_event_id

            out = self.writer.call(self._read_wire_body, event_id)

        return out

# ################################################################################################################################

    def record_resend(self, sent:'SentMessage') -> 'None':
        """ Records in memory that a message is delivered again. The deliveries are recorded in the audit log
        with the end of the exchange.
        """
        now = self.clock.now()

        with self._lock:
            if exchange := self._open.get(sent.message_id):
                attempt_at = now.isoformat()
                exchange.attempts.append(attempt_at)

                retry_state = exchange.sent.retry_state
                retry_state.attempt_count += 1
                retry_state.last_attempt_at = now

                exchange.sent.outcome.retry_count = retry_state.attempt_count - 1

# ################################################################################################################################

    def resend(self, message_id:'str') -> 'SentMessage':
        """ Sends a message again on behalf of an operator, with the bytes and the MessageId of its first delivery.
        The exchange starts a new retry budget, and an exchange that ended is reopened. The resend is recorded before
        it is made, and the message is returned as its record stands once the record is committed.
        """
        is_open = self.is_open(message_id)
        sent = self.get(message_id)

        now = self.clock.now()
        attempt_at = now.isoformat()

        attrs = self._party_attrs(sent)
        attrs[B2BAttr.Attempt_At] = attempt_at

        data = dumps({SentData.Attempt_At: attempt_at})

        write = EventWrite()
        write.pending = self.audit_log.new_pending_event(self.source, AuditEvent.Message_Resent, sent.cpa_id,
            cid=message_id, msg_id=message_id, endpoint=sent.endpoint, outcome=AuditOutcome.OK, data=data, attrs=attrs)

        # An exchange that ended is open again from its resend.
        if not is_open:
            write.opens.append(OpenKind.Exchange)

        _ = self._write(write)

        # The message is read as the resend left it, and the signals that did not end an open exchange stay with it.
        with self._lock:
            previous = self._open.pop(message_id, None)

        out = self.get(message_id)

        exchange = _Exchange()
        exchange.sent = out
        exchange.attempts.append(attempt_at)

        if previous:
            exchange.signals = previous.signals
            exchange.signal_bodies = previous.signal_bodies

        with self._lock:
            self._open[message_id] = exchange

        return out

# ################################################################################################################################

    def record_reprocess(self, original:'SentMessage', sent:'SentMessage') -> 'None':
        """ Records the first delivery of a message that sends the payloads of another one again under a new MessageId,
        linked to the first delivery of the other one. An exchange of the other one that has not ended ends as superseded.
        """
        self.record_first_attempt(sent, resubmit_of=original.wire_event_id)

        if self.is_open(original.message_id):
            outcome = deepcopy(original.outcome)
            outcome.final_state = FinalState.Superseded

            self.record_completion(original, outcome)

# ################################################################################################################################

    def record_attempt_failure(self, sent:'SentMessage', failure_cause:'str', failure_detail:'str') -> 'None':
        """ Records in memory why the latest delivery of a message failed. The cause is recorded in the audit log
        with the end of the exchange.
        """
        with self._lock:
            if exchange := self._open.get(sent.message_id):
                exchange.sent.outcome.failure_cause = failure_cause
                exchange.sent.outcome.failure_detail = failure_detail

# ################################################################################################################################

    def record_signal(
        self,
        sent:'SentMessage',
        headers:'strstrdict',
        body:'bytes',
        signal_kind:'str',
        error_code:'str',
        severity:'str',
        ) -> 'None':
        """ Records a signal that answers a message. A signal of an exchange that has not ended is held in memory
        and recorded with the end of the exchange, and one that arrives after the end is recorded in an event of its own.
        """
        signal:'stranydict' = {
            SentData.Headers: headers,
            SentData.Signal_Kind: signal_kind,
            SentData.Error_Code: error_code,
            SentData.Severity: severity,
        }

        with self._lock:
            if exchange := self._open.get(sent.message_id):
                exchange.signals.append(signal)
                exchange.signal_bodies.append(body)

                # A signal that reports an error and does not end the exchange is part of where the exchange stands.
                if error_code:
                    exchange.sent.outcome.error_code = error_code
                    exchange.sent.outcome.error_severity = severity

                return

        attrs = self._party_attrs(sent)
        attrs[B2BAttr.Signal_Kind] = signal_kind
        attrs[B2BAttr.Error_Code] = error_code

        attachment = build_attachment(_signal_file_name, _body_content_type, body, max_size=Limits.Max_Message_Size_Bytes)
        body_size = len(body)

        write = EventWrite()
        write.pending = self.audit_log.new_pending_event(self.source, AuditEvent.Signal_Received, sent.cpa_id,
            cid=sent.message_id, msg_id=sent.message_id, size=body_size, data=dumps(signal), attrs=attrs,
            attachments=[attachment])

        _ = self._write(write)

# ################################################################################################################################

    def record_completion(self, sent:'SentMessage', outcome:'Outcome') -> 'None':
        """ Records the end of the exchange of a message with its deliveries and the signals that answered it,
        the signal that ended it included, after which it is no longer outstanding. An exchange that failed
        ends the business transaction of its message with the cause of the last delivery. The call returns once
        the record is committed.
        """
        with self._lock:
            exchange = self._open.get(sent.message_id)

        if exchange:
            attempts = exchange.attempts
            signals = exchange.signals
            signal_bodies = exchange.signal_bodies
        else:
            attempts = []
            signals = []
            signal_bodies = []

        attrs = self._party_attrs(sent)
        attrs[B2BAttr.Final_State] = outcome.final_state
        attrs[B2BAttr.Signal_Kind] = outcome.signal_kind
        attrs[B2BAttr.Error_Code] = outcome.error_code

        data = dumps({
            SentData.Outcome: outcome_to_dict(outcome),
            SentData.Attempts: attempts,
            SentData.Signals: signals,
        })

        internal_data = dumps({
            SentInternalData.Payload_Digests: outcome.payload_digests,
        })

        if outcome.error_code:
            audit_outcome = AuditOutcome.Error
        else:
            audit_outcome = AuditOutcome.OK

        attachments:'anylist' = []

        for signal_body in signal_bodies:
            attachment = build_attachment(_signal_file_name, _body_content_type, signal_body,
                max_size=Limits.Max_Message_Size_Bytes)
            attachments.append(attachment)

        write = EventWrite()
        write.pending = self.audit_log.new_pending_event(self.source, AuditEvent.Message_Completed, sent.cpa_id,
            cid=sent.message_id, msg_id=sent.message_id, status=outcome.final_state, outcome=audit_outcome, data=data,
            internal_data=internal_data, attrs=attrs, attachments=attachments)

        if exchange:
            write.closes.append(OpenKind.Exchange)

        _ = self._write(write)

        with self._lock:
            _ = self._open.pop(sent.message_id, None)

        sent.retry_state.is_answered = True
        sent.outcome = outcome

        if outcome.final_state == FinalState.Failed:
            if self.business_log:
                self.business_log.record_delivery_failed(sent.message_id, outcome.failure_cause, outcome.failure_detail)

# ################################################################################################################################

    def _read_one(self, message_id:'str') -> 'SentMessage | None':
        with self.engine.connect() as connection:
            messages = read_stored(connection, self.source, self.server_name, [message_id])

        if messages:
            out = messages[0]
        else:
            out = None

        return out

# ################################################################################################################################

    def read(self, message_id:'str') -> 'SentMessage | None':
        """ Returns one message as it stands, or None if this server did not send it. A message whose exchange
        has not ended is returned from memory as the send log holds it, and one whose exchange ended is read
        from the audit log.
        """
        with self._lock:
            if exchange := self._open.get(message_id):
                out = exchange.sent
            else:
                out = None

        if out is None:
            out = self.writer.call(self._read_one, message_id)

        return out

# ################################################################################################################################

    def get(self, message_id:'str') -> 'SentMessage':
        """ Returns one message this server sent as it stands.
        """
        out = self.read(message_id)

        if out is None:
            raise B2BException(f'Message `{message_id}` was not sent by server `{self.server_name}`')

        return out

# ################################################################################################################################

    def outstanding(self, limit:'int') -> 'sent_message_list':
        """ Returns, up to the limit, the messages whose exchange has not ended, the earliest one first.
        """
        with self._lock:
            exchanges = list(self._open.values())

        ordered:'anylist' = []

        for exchange in exchanges:
            sent = exchange.sent
            ordered.append((sent.wire_event_id, sent))

        ordered.sort()

        out:'sent_message_list' = []

        for _, sent in ordered[:limit]:
            out.append(sent)

        return out

# ################################################################################################################################

    def _recover_page(self, after_id:'int', limit:'int') -> 'RecoveredPage':

        with self.engine.connect() as connection:
            records = read_open_page(connection, OpenKind.Exchange, self.source, self.server_name, after_id, limit)

            message_ids:'strlist' = []

            for record in records:
                message_ids.append(record.message_id)

            messages = read_stored(connection, self.source, self.server_name, message_ids)

        out = page_of(messages, records, after_id, limit)
        return out

# ################################################################################################################################

    def recover_page(self, limit:'int', after_id:'int'=0) -> 'RecoveredPage':
        """ Reads, up to the limit, the exchanges that have not ended from the audit log into memory, in the order
        they were opened and starting after the open record with the given identifier, so that their deliveries
        and the matching of their signals continue from them.
        """
        out = self.writer.call(self._recover_page, after_id, limit)

        with self._lock:
            for sent in out.items:
                exchange = _Exchange()
                exchange.sent = sent
                exchange.attempts.append(sent.retry_state.last_attempt_at.isoformat())
                self._open[sent.message_id] = exchange

        return out

# ################################################################################################################################

    def recover(self, page_size:'int'=Recovery_Page_Size) -> 'int':
        """ Reads every exchange that has not ended from the audit log into memory, page by page,
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
