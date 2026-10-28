# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, is_audit_log_enabled, ModuleCtx as AuditLogCtx
from zato.common.audit_log.attachment import build_attachment, Env_Max_Attachment_Size, get_max_attachment_size
from zato.common.audit_log.common import B2BAttr
from zato.common.b2b.common.business_state import business_data, business_sent_attrs, Data_Business
from zato.common.b2b.common.commit_group import get_writer
from zato.common.b2b.common.commit_sql import EventWrite
from zato.common.b2b.common.exceptions import B2BException
from zato.common.b2b.common.outcome import FinalState, outcome_from_dict, outcome_to_dict
from zato.common.b2b.common.recovery import read_attrs, read_bodies, read_events, read_open
from zato.common.b2b.common.retry import RetryPolicy, RetryState
from zato.common.b2b.common.schema import OpenKind
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.b2b.common.business_log import BusinessLog
    from zato.common.b2b.common.business_state import BusinessMessage
    from zato.common.b2b.common.clock import Clock
    from zato.common.b2b.common.commit_group import GroupCommitWriter
    from zato.common.b2b.common.outcome import Outcome
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
    stranydict = stranydict
    strlist = strlist
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

sent_message_list = list['SentMessage']

# ################################################################################################################################
# ################################################################################################################################

class _Data:
    """ The keys of the data documents the events of a sent message have.
    """
    Retries        = 'retries'
    Retry_Interval = 'retry_interval_seconds'
    Expires_At     = 'expires_at'
    Headers        = 'headers'
    Details        = 'details'
    Outcome        = 'outcome'
    Severity       = 'severity'
    Attempts       = 'attempts'
    Signals        = 'signals'
    Signal_Kind    = 'signal_kind'
    Error_Code     = 'error_code'

# ################################################################################################################################
# ################################################################################################################################

# The names and the content type of the stored message and of a stored signal.
_wire_file_name     = 'message'
_signal_file_name   = 'signal'
_body_content_type  = 'application/octet-stream'

# The event types that make up the record of one sent message.
_message_event_types = (AuditEvent.Message_Sent, AuditEvent.Message_Completed)

# The attributes the first delivery of every message has, whatever its protocol.
_common_attr_names = {B2BAttr.From_Party, B2BAttr.To_Party, B2BAttr.Attempt, B2BAttr.Attempt_At, B2BAttr.Deadline_At}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SentMessage:
    """ One outgoing message as its send log records it - who it is from and to, how it is retried,
    where its delivery stands and what went on the wire.
    """
    message_id: str
    cpa_id:     str
    from_party: str
    to_party:   str
    endpoint:   str

    # The protocol's own searchable attributes of the message.
    attrs: 'stranydict'

    policy:      'RetryPolicy'
    retry_state: 'RetryState'
    outcome:     'Outcome'

    # The protocol's own data that rebuilding the message requires.
    details: 'stranydict'

    # The wire form of the message. The bytes are held only until the first delivery takes them,
    # and are read again by the identifier of the event they are stored with.
    wire_headers:  'strstrdict'
    wire_body:     bytes
    wire_event_id: int = 0

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

    def record_first_attempt(self, sent:'SentMessage', business:'BusinessMessage | None'=None) -> 'None':
        """ Records the first delivery of a message together with everything its later deliveries and the rebuilding
        of the message require - the retry policy, the expiry, the protocol's details and the wire form itself.
        A business message is recorded as sent with its business transaction in the same event. A delivery is recorded
        before it is made, so that a signal which answers it before its response arrives finds the message, and the call
        returns once the record is committed. A first delivery under a MessageId that is open already starts the record anew.
        """
        wire_size = len(sent.wire_body)
        max_size = get_max_attachment_size()

        # A resend sends the same bytes again, which is possible only if they are stored.
        if wire_size > max_size:
            raise B2BException(f'Message `{sent.message_id}` has {wire_size} bytes, ' +
                f'more than the {max_size} that `{Env_Max_Attachment_Size}` allows to be stored')

        if business and not self.business_log:
            raise B2BException(f'Message `{sent.message_id}` is a business message and the send log has no business log')

        retry_state = sent.retry_state

        if expires_at := retry_state.expires_at:
            expires_at = expires_at.isoformat()

        initial_outcome = outcome_to_dict(sent.outcome)

        data:'stranydict' = {
            _Data.Retries: sent.policy.retries,
            _Data.Retry_Interval: sent.policy.retry_interval.total_seconds(),
            _Data.Expires_At: expires_at,
            _Data.Headers: sent.wire_headers,
            _Data.Details: sent.details,
            _Data.Outcome: initial_outcome,
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

        attachment = build_attachment(_wire_file_name, _body_content_type, sent.wire_body)

        write.pending = self.audit_log.new_pending_event(self.source, AuditEvent.Message_Sent, sent.cpa_id,
            cid=sent.message_id, msg_id=sent.message_id, endpoint=sent.endpoint, size=wire_size, outcome=AuditOutcome.OK,
            data=dumps(data), attrs=attrs, attachments=[attachment])

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
            _Data.Headers: headers,
            _Data.Signal_Kind: signal_kind,
            _Data.Error_Code: error_code,
            _Data.Severity: severity,
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

        attachment = build_attachment(_signal_file_name, _body_content_type, body)
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
            _Data.Outcome: outcome_to_dict(outcome),
            _Data.Attempts: attempts,
            _Data.Signals: signals,
        })

        if outcome.error_code:
            audit_outcome = AuditOutcome.Error
        else:
            audit_outcome = AuditOutcome.OK

        attachments:'anylist' = []

        for signal_body in signal_bodies:
            attachment = build_attachment(_signal_file_name, _body_content_type, signal_body)
            attachments.append(attachment)

        write = EventWrite()
        write.pending = self.audit_log.new_pending_event(self.source, AuditEvent.Message_Completed, sent.cpa_id,
            cid=sent.message_id, msg_id=sent.message_id, status=outcome.final_state, outcome=audit_outcome, data=data,
            attrs=attrs, attachments=attachments)

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

    def _new_sent_message(self, events:'anylist', attrs:'stranydict') -> 'SentMessage':
        """ Builds a message out of its events, the first of which is its first delivery.
        """
        first = events[0]
        first_data = loads(first.data)

        completion = None

        for event in events[1:]:
            if event.event_type == AuditEvent.Message_Completed:
                completion = event
                break

        # The searchable attributes of the protocol are those the record has on top of the ones every message has.
        protocol_attrs:'stranydict' = {}

        for name, value in attrs.items():
            if name not in _common_attr_names:
                protocol_attrs[name] = value

        policy = RetryPolicy()
        policy.retries = first_data[_Data.Retries]
        policy.retry_interval = timedelta(seconds=first_data[_Data.Retry_Interval])

        retry_state = RetryState()
        retry_state.attempt_count = 1
        retry_state.last_attempt_at = datetime.fromisoformat(attrs[B2BAttr.Attempt_At])

        if expires_at := first_data[_Data.Expires_At]:
            retry_state.expires_at = datetime.fromisoformat(expires_at)

        # A completed message has the outcome its exchange ended with and the deliveries it was made in ..
        if completion:
            completion_data = loads(completion.data)
            outcome = outcome_from_dict(completion_data[_Data.Outcome])

            if attempts := completion_data[_Data.Attempts]:
                retry_state.attempt_count = len(attempts)
                retry_state.last_attempt_at = datetime.fromisoformat(attempts[-1])

            retry_state.is_answered = True

        # .. while a pending one has the outcome it was sent with.
        else:
            outcome = outcome_from_dict(first_data[_Data.Outcome])

        out = SentMessage()
        out.message_id = first.msg_id
        out.cpa_id = first.object_name
        out.from_party = attrs[B2BAttr.From_Party]
        out.to_party = attrs[B2BAttr.To_Party]
        out.endpoint = first.endpoint
        out.attrs = protocol_attrs
        out.policy = policy
        out.retry_state = retry_state
        out.outcome = outcome
        out.details = first_data[_Data.Details]
        out.wire_headers = first_data[_Data.Headers]
        out.wire_body = b''
        out.wire_event_id = first.id

        return out

# ################################################################################################################################

    def _read_stored(self, connection:'Connection', message_ids:'strlist') -> 'sent_message_list':
        """ Reads the given messages from the audit log, each from its latest first delivery onwards.
        """
        events_by_message = read_events(connection, self.source, self.server_name, message_ids, _message_event_types)

        message_events:'dict[str, anylist]' = {}
        first_event_ids:'list[int]' = []

        for message_id, events in events_by_message.items():

            current:'anylist' = []

            # A first delivery starts the record anew, and everything recorded after it belongs to it.
            for event in events:
                if event.event_type == AuditEvent.Message_Sent:
                    current = []
                current.append(event)

            if current:
                message_events[message_id] = current
                first_event_ids.append(current[0].id)

        attrs_by_event = read_attrs(connection, first_event_ids)

        out:'sent_message_list' = []

        for events in message_events.values():
            first = events[0]
            attrs = attrs_by_event[first.id]
            sent = self._new_sent_message(events, attrs)
            out.append(sent)

        return out

# ################################################################################################################################

    def _read_one(self, message_id:'str') -> 'SentMessage | None':
        with self.engine.connect() as connection:
            messages = self._read_stored(connection, [message_id])

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

    def _recover(self) -> 'sent_message_list':
        with self.engine.connect() as connection:
            open_records = read_open(connection, OpenKind.Exchange, self.source, self.server_name)
            message_ids = list(open_records)
            out = self._read_stored(connection, message_ids)

        return out

# ################################################################################################################################

    def recover(self) -> 'int':
        """ Reads the exchanges that have not ended from the audit log into memory, so that their deliveries
        and the matching of their signals continue from them, and returns how many there are.
        """
        messages = self.writer.call(self._recover)

        with self._lock:
            for sent in messages:
                exchange = _Exchange()
                exchange.sent = sent
                exchange.attempts.append(sent.retry_state.last_attempt_at.isoformat())
                self._open[sent.message_id] = exchange

        out = len(messages)
        return out

# ################################################################################################################################
# ################################################################################################################################
