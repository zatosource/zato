# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode
from dataclasses import dataclass
from datetime import datetime, timedelta

# SQLAlchemy
from sqlalchemy import and_, exists, or_, select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, event_attr_table, event_body_table, event_table, \
    is_audit_log_enabled, ModuleCtx as AuditLogCtx
from zato.common.audit_log.attachment import build_attachment, Env_Max_Attachment_Size, get_max_attachment_size
from zato.common.audit_log.common import AuditBody, B2BAttr
from zato.common.b2b.common.exceptions import B2BException
from zato.common.b2b.common.outcome import Outcome
from zato.common.b2b.common.retry import RetryPolicy, RetryState
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.b2b.common.clock import Clock
    from zato.common.typing_ import anylist, intanydict, intlist, stranydict, strstrdict
    anylist = anylist
    Clock = Clock
    Connection = Connection
    Engine = Engine
    intanydict = intanydict
    intlist = intlist
    stranydict = stranydict
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

# ################################################################################################################################
# ################################################################################################################################

# The names and the content type of the stored message and of a stored signal.
_wire_file_name     = 'message'
_signal_file_name   = 'signal'
_body_content_type  = 'application/octet-stream'

# The event types that make up the record of one sent message.
_message_event_types = (AuditEvent.Message_Sent, AuditEvent.Signal_Received, AuditEvent.Message_Completed)

# The attributes the first delivery of every message has, whatever its protocol.
_common_attr_names = {B2BAttr.From_Party, B2BAttr.To_Party, B2BAttr.Attempt, B2BAttr.Attempt_At}

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

    wire_headers: 'strstrdict'
    wire_body:    bytes

# ################################################################################################################################
# ################################################################################################################################

def _outcome_to_dict(outcome:'Outcome') -> 'stranydict':
    out = {
        'delivered': outcome.delivered,
        'payload_digests': outcome.payload_digests,
        'signal_kind': outcome.signal_kind,
        'error_code': outcome.error_code,
        'error_severity': outcome.error_severity,
        'signature_verified': outcome.signature_verified,
        'duplicate': outcome.duplicate,
        'retry_count': outcome.retry_count,
        'final_state': outcome.final_state,
    }

    return out

# ################################################################################################################################

def _outcome_from_dict(data:'stranydict') -> 'Outcome':

    out = Outcome()
    out.delivered = data['delivered']
    out.payload_digests = data['payload_digests']
    out.signal_kind = data['signal_kind']
    out.error_code = data['error_code']
    out.error_severity = data['error_severity']
    out.signature_verified = data['signature_verified']
    out.duplicate = data['duplicate']
    out.retry_count = data['retry_count']
    out.final_state = data['final_state']

    return out

# ################################################################################################################################
# ################################################################################################################################

class SendLog:
    """ The record of every message a server sends under a B2B protocol, kept in the audit log - each delivery
    attempt, each signal that answers a message and the end of each exchange. Nothing about a message is held
    in memory, so its delivery continues from the record after a restart.
    """

    def __init__(self, source:'str', server_name:'str', clock:'Clock') -> 'None':

        # A turned-off audit log drops every event, and the delivery of a message cannot continue without its record.
        if not is_audit_log_enabled():
            raise B2BException(f'The audit log is turned off through `{AuditLogCtx.Env_Enabled}` and no message can be sent')

        self.source = source
        self.server_name = server_name
        self.clock = clock

        # Each event is committed at the moment it is recorded.
        self.audit_log = AuditLog(server_name, flush_max_size=1)

# ################################################################################################################################

    @property
    def engine(self) -> 'Engine':
        out = self.audit_log.engine
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

    def _attempt_attrs(self, sent:'SentMessage', attempt:'int') -> 'stranydict':
        """ Returns the attributes of one delivery attempt, its time taken from the clock of the sender.
        """
        now = self.clock.now()

        out = self._party_attrs(sent)
        out[B2BAttr.Attempt] = attempt
        out[B2BAttr.Attempt_At] = now.isoformat()

        return out

# ################################################################################################################################

    def record_first_attempt(self, sent:'SentMessage') -> 'None':
        """ Records the first delivery of a message together with everything its later deliveries and the rebuilding
        of the message require - the retry policy, the expiry, the protocol's details and the wire form itself.
        A delivery is recorded before it is made, so that a signal which answers it before its response arrives
        finds the message. A first delivery under a MessageId that is already recorded starts the record anew.
        """
        wire_size = len(sent.wire_body)
        max_size = get_max_attachment_size()

        # A resend sends the same bytes again, which is possible only if they are stored.
        if wire_size > max_size:
            raise B2BException(f'Message `{sent.message_id}` has {wire_size} bytes, ' +
                f'more than the {max_size} that `{Env_Max_Attachment_Size}` allows to be stored')

        retry_state = sent.retry_state

        if expires_at := retry_state.expires_at:
            expires_at = expires_at.isoformat()

        initial_outcome = _outcome_to_dict(sent.outcome)

        data = dumps({
            _Data.Retries: sent.policy.retries,
            _Data.Retry_Interval: sent.policy.retry_interval.total_seconds(),
            _Data.Expires_At: expires_at,
            _Data.Headers: sent.wire_headers,
            _Data.Details: sent.details,
            _Data.Outcome: initial_outcome,
        })

        attrs = self._attempt_attrs(sent, 1)
        attachment = build_attachment(_wire_file_name, _body_content_type, sent.wire_body)

        _ = self.audit_log.insert(self.source, AuditEvent.Message_Sent, sent.cpa_id, cid=sent.message_id,
            msg_id=sent.message_id, endpoint=sent.endpoint, size=wire_size, outcome=AuditOutcome.OK, data=data,
            attrs=attrs, attachments=[attachment])

# ################################################################################################################################

    def record_resend(self, sent:'SentMessage') -> 'None':
        """ Records that a message is delivered again, with the bytes stored with its first delivery.
        """
        attempt = sent.retry_state.attempt_count + 1

        attrs = self._attempt_attrs(sent, attempt)
        wire_size = len(sent.wire_body)

        _ = self.audit_log.insert(self.source, AuditEvent.Message_Sent, sent.cpa_id, cid=sent.message_id,
            msg_id=sent.message_id, endpoint=sent.endpoint, size=wire_size, outcome=AuditOutcome.OK, attrs=attrs)

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
        """ Records a signal that answers a message, its bytes kept as they arrived.
        """
        attrs = self._party_attrs(sent)
        attrs[B2BAttr.Signal_Kind] = signal_kind
        attrs[B2BAttr.Error_Code] = error_code

        data = dumps({
            _Data.Headers: headers,
            _Data.Severity: severity,
        })

        attachment = build_attachment(_signal_file_name, _body_content_type, body)
        body_size = len(body)

        _ = self.audit_log.insert(self.source, AuditEvent.Signal_Received, sent.cpa_id, cid=sent.message_id,
            msg_id=sent.message_id, size=body_size, data=data, attrs=attrs, attachments=[attachment])

# ################################################################################################################################

    def record_completion(self, sent:'SentMessage', outcome:'Outcome') -> 'None':
        """ Records the end of the exchange of a message, after which it is no longer outstanding.
        """
        attrs = self._party_attrs(sent)
        attrs[B2BAttr.Final_State] = outcome.final_state
        attrs[B2BAttr.Signal_Kind] = outcome.signal_kind
        attrs[B2BAttr.Error_Code] = outcome.error_code

        outcome_data = _outcome_to_dict(outcome)
        data = dumps({_Data.Outcome: outcome_data})

        if outcome.error_code:
            audit_outcome = AuditOutcome.Error
        else:
            audit_outcome = AuditOutcome.OK

        _ = self.audit_log.insert(self.source, AuditEvent.Message_Completed, sent.cpa_id, cid=sent.message_id,
            msg_id=sent.message_id, status=outcome.final_state, outcome=audit_outcome, data=data, attrs=attrs)

# ################################################################################################################################

    def _read_attrs(self, connection:'Connection', event_ids:'intlist') -> 'intanydict':
        """ Returns the attributes of each of the given events, by the event's id.
        """
        out:'intanydict' = {}

        for event_id in event_ids:
            out[event_id] = {}

        is_wanted = event_attr_table.c.event_id.in_(event_ids)
        statement = select(event_attr_table.c.event_id, event_attr_table.c.name, event_attr_table.c.value).where(is_wanted)

        for row in connection.execute(statement):
            event_attrs = out[row.event_id]
            event_attrs[row.name] = row.value

        return out

# ################################################################################################################################

    def _read_wire_body(self, connection:'Connection', event_id:'int') -> 'bytes':
        """ Returns the bytes stored with the first delivery of a message.
        """
        conditions = and_(
            event_body_table.c.event_id == event_id,
            event_body_table.c.kind == AuditBody.Attachment,
        )
        statement = select(event_body_table.c.data).where(conditions)

        result = connection.execute(statement)
        row = result.one()

        envelope = loads(row.data)
        content = envelope['content']

        out = b64decode(content)
        return out

# ################################################################################################################################

    def _message_events(self, connection:'Connection', message_id:'str') -> 'anylist':
        """ Returns the events of one message this server sent, in the order they were recorded,
        from its latest first delivery onwards.
        """
        conditions = and_(
            event_table.c.msg_id == message_id,
            event_table.c.source == self.source,
            event_table.c.server_name == self.server_name,
            event_table.c.event_type.in_(_message_event_types),
        )
        statement = select(event_table).where(conditions).order_by(event_table.c.id)

        result = connection.execute(statement)
        events = result.fetchall()

        # Our response to produce
        out:'anylist' = []

        for event in events:

            # A first delivery is the only one with a data document, and it starts the record anew ..
            if event.event_type == AuditEvent.Message_Sent:
                if event.data:
                    out = []

            # .. and everything recorded after it belongs to it.
            out.append(event)

        return out

# ################################################################################################################################

    def read(self, message_id:'str') -> 'SentMessage | None':
        """ Returns one message as it stands, or None if this server did not send it.
        """
        with self.engine.connect() as connection:
            events = self._message_events(connection, message_id)

            # A message that has no delivery is not one this server sent ..
            if not events:
                out = None

            # .. and one that has is read from its events.
            else:
                out = self._new_sent_message(connection, message_id, events)

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

    def _new_sent_message(self, connection:'Connection', message_id:'str', events:'anylist') -> 'SentMessage':
        """ Builds a message out of its events, the first of which is its first delivery.
        """
        attempts:'anylist' = []
        signals:'anylist' = []
        completions:'anylist' = []

        for event in events:
            if event.event_type == AuditEvent.Message_Sent:
                attempts.append(event)
            elif event.event_type == AuditEvent.Signal_Received:
                signals.append(event)
            else:
                completions.append(event)

        first = attempts[0]
        last = attempts[-1]

        event_ids = [first.id, last.id]

        for signal in signals:
            event_ids.append(signal.id)

        attrs_by_event = self._read_attrs(connection, event_ids)
        wire_body = self._read_wire_body(connection, first.id)

        first_attrs = attrs_by_event[first.id]
        last_attrs = attrs_by_event[last.id]
        first_data = loads(first.data)

        # The searchable attributes of the protocol are those the record has on top of the ones every message has.
        protocol_attrs:'stranydict' = {}

        for name, value in first_attrs.items():
            if name not in _common_attr_names:
                protocol_attrs[name] = value

        policy = RetryPolicy()
        policy.retries = first_data[_Data.Retries]
        policy.retry_interval = timedelta(seconds=first_data[_Data.Retry_Interval])

        attempt_count = len(attempts)
        last_attempt_at = last_attrs[B2BAttr.Attempt_At]

        retry_state = RetryState()
        retry_state.attempt_count = attempt_count
        retry_state.last_attempt_at = datetime.fromisoformat(last_attempt_at)

        if expires_at := first_data[_Data.Expires_At]:
            retry_state.expires_at = datetime.fromisoformat(expires_at)

        # A completed message has the outcome its exchange ended with, the first one if it ended more than once ..
        if completions:
            completion = completions[0]
            completion_data = loads(completion.data)
            outcome = _outcome_from_dict(completion_data[_Data.Outcome])
            retry_state.is_answered = True

        # .. while a pending one has the outcome it was sent with, its retries and the error of a signal that did not end it.
        else:
            outcome = _outcome_from_dict(first_data[_Data.Outcome])
            outcome.retry_count = attempt_count - 1

            if signals:
                signal = signals[-1]
                signal_data = loads(signal.data)
                signal_attrs = attrs_by_event[signal.id]

                if error_code := signal_attrs[B2BAttr.Error_Code]:
                    outcome.error_code = error_code
                    outcome.error_severity = signal_data[_Data.Severity]

        out = SentMessage()
        out.message_id = message_id
        out.cpa_id = first.object_name
        out.from_party = first_attrs[B2BAttr.From_Party]
        out.to_party = first_attrs[B2BAttr.To_Party]
        out.endpoint = first.endpoint
        out.attrs = protocol_attrs
        out.policy = policy
        out.retry_state = retry_state
        out.outcome = outcome
        out.details = first_data[_Data.Details]
        out.wire_headers = first_data[_Data.Headers]
        out.wire_body = wire_body

        return out

# ################################################################################################################################

    def outstanding(self, limit:'int') -> 'sent_message_list':
        """ Returns the messages this server sent whose exchange has not ended, the earliest one first.
        """
        later = event_table.alias()

        # A message is no longer outstanding once its exchange ended, and a first delivery is no longer
        # the start of a record once another first delivery under the same MessageId follows it.
        is_later_first_attempt = and_(
            later.c.event_type == AuditEvent.Message_Sent,
            later.c.data != '',
        )
        is_closing = or_(
            later.c.event_type == AuditEvent.Message_Completed,
            is_later_first_attempt,
        )
        closing_conditions = and_(
            later.c.msg_id == event_table.c.msg_id,
            later.c.source == self.source,
            later.c.server_name == self.server_name,
            later.c.id > event_table.c.id,
            is_closing,
        )
        closing_select = select(later.c.id).where(closing_conditions)
        is_closed = exists(closing_select)

        conditions = and_(
            event_table.c.source == self.source,
            event_table.c.server_name == self.server_name,
            event_table.c.event_type == AuditEvent.Message_Sent,
            event_table.c.data != '',
            ~is_closed,
        )

        statement = select(event_table.c.msg_id).where(conditions).order_by(event_table.c.id).limit(limit)

        out:'sent_message_list' = []

        with self.engine.connect() as connection:
            result = connection.execute(statement)
            rows = result.fetchall()

            for row in rows:
                events = self._message_events(connection, row.msg_id)
                sent = self._new_sent_message(connection, row.msg_id, events)
                out.append(sent)

        return out

# ################################################################################################################################
# ################################################################################################################################
