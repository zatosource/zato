# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections.abc import Callable
from http.client import SERVICE_UNAVAILABLE
from json import dumps
from random import Random
from time import time

# gevent
from gevent import spawn

# Zato
from zato.common.audit_log.common import AuditSource
from zato.common.b2b.common.business_log import BusinessLog
from zato.common.b2b.common.clock import SystemClock
from zato.common.b2b.common.commit_group import get_writer
from zato.common.b2b.common.retry import RetryAction
from zato.common.b2b.common.scheduler import DeliveryScheduler, EntryKind
from zato.common.b2b.common.send_log import SendLog
from zato.common.b2b.common.store import MessageStore, new_memory_store
from zato.common.b2b.ebms2.business_signals import accept_business_message, build_signal, BusinessSignal, \
    new_business_message, new_ebbp_signal
from zato.common.b2b.ebms2.inbound import receive
from zato.common.b2b.ebms2.inbound_common import HTTPResponse, new_delivery, new_receive_log, read_message
from zato.common.b2b.ebms2.outbound import accept_no_answer, accept_response, build, give_up, next_action, OutboundState, \
    SendOptions
from zato.common.b2b.ebms2.outbound_record import new_sent_message, restore_outbound
from zato.common.test.b2b_perf_common import FaultType, Host_Name, Host_Server_Name, MessageKind, Notification_Action, \
    Notification_Service, Partner_Name, Partner_Server_Name, PerfPath, PerfRole, RecordType, Request_Action, \
    Request_Response_Service, Response_Action
from zato.common.test.b2b_perf_support import http_post, load_agreement, load_keys, new_payloads, resolve_binding, \
    StatementCounter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from io import TextIOWrapper
    from zato.common.b2b.common.business_state import BusinessMessage
    from zato.common.b2b.common.receive_log import ReceivedMessage
    from zato.common.b2b.common.send_log import SentMessage
    from zato.common.b2b.ebms2.agreement import Agreement, Binding
    from zato.common.b2b.ebms2.header import MessageHeader
    from zato.common.b2b.ebms2.inbound_common import Delivery
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    from zato.common.test.b2b_perf_common import PartyConfig
    from zato.common.typing_ import any_, anytuple, callable_, stranydict, strstrdict
    Agreement = Agreement
    any_ = any_
    anytuple = anytuple
    Binding = Binding
    BusinessMessage = BusinessMessage
    callable_ = callable_
    datetime = datetime
    Delivery = Delivery
    MessageHeader = MessageHeader
    OutboundMessage = OutboundMessage
    PartyConfig = PartyConfig
    ReceivedMessage = ReceivedMessage
    SentMessage = SentMessage
    stranydict = stranydict
    strstrdict = strstrdict
    TextIOWrapper = TextIOWrapper

# ################################################################################################################################
# ################################################################################################################################

processor_func = Callable[['MessageHeader', 'Delivery'], None]

delivery_list     = list['Delivery']
strbindingdict    = dict[str, 'Binding']
stragreementdict  = dict[str, 'Agreement']
strprocessordict  = dict[str, processor_func]

# ################################################################################################################################
# ################################################################################################################################

# The faults of the partner follow the same sequence in every run.
_fault_seed = 20261028

# The kind of each message by its action.
_kinds = {
    Request_Action: MessageKind.Request,
    Response_Action: MessageKind.Response,
    Notification_Action: MessageKind.Notification,
    BusinessSignal.Receipt_Acknowledgement: MessageKind.Signal,
}

# ################################################################################################################################
# ################################################################################################################################

class PerfExchange:
    """ The messages of one party of a performance run - the host, whose audit log is in the database of the run,
    or the partner, whose messages are recorded in memory.
    """

    def __init__(self, config:'PartyConfig') -> 'None':

        self.config = config
        self.clock = SystemClock()
        self.local_keys = load_keys(config)
        self.random = Random(_fault_seed)
        self.payloads = new_payloads(config.document_size)

        # Each event of each message is appended as one line, which reaches the file even if the process is killed.
        self.records:'TextIOWrapper' = open(config.records_path, 'a', buffering=1, encoding='utf8')

        # Each agreement is found by the path its messages arrive at, and by its CPA identifier for the messages sent.
        self.agreements_by_path:'stragreementdict' = {}
        self.agreements_by_cpa_id:'stragreementdict' = {}

        for path, cpa_path in config.agreements.items():
            agreement = load_agreement(cpa_path)
            self.agreements_by_path[path] = agreement
            self.agreements_by_cpa_id[agreement.cpa_id] = agreement

        self.bindings_by_kind = self.new_bindings()

        # The host records everything in the audit log database of the run ..
        if config.role == PerfRole.Host:
            writer = get_writer()
            self.store = MessageStore(writer)
            server_name = Host_Server_Name

        # .. and the partner in memory.
        else:
            self.store = new_memory_store()
            writer = self.store.writer
            server_name = Partner_Server_Name

        self.writer = writer
        self.counter = StatementCounter(writer.engine)

        self.receive_log = new_receive_log(self.store, server_name)
        self.business_log = BusinessLog(AuditSource.EbMS2, server_name, writer)
        self.send_log = SendLog(AuditSource.EbMS2, server_name, self.clock, writer, self.business_log)

        self.scheduler = DeliveryScheduler(self.clock)
        self.scheduler.set_handler(EntryKind.Delivery, self._on_delivery_due)

        # What the processing of each kind of message received consists of.
        self.processors:'strprocessordict' = {
            MessageKind.Request: self._answer_request,
            MessageKind.Response: self._match_reply,
            MessageKind.Notification: self._acknowledge_notification,
            MessageKind.Signal: self._match_reply,
        }

        # How many greenlets send, resend or process messages at the moment.
        self.busy = 0
        self.resends = 0

# ################################################################################################################################

    def new_bindings(self) -> 'strbindingdict':
        """ Returns the binding of each kind of message the party starts or answers with.
        """
        request_response = self.agreements_by_path[PerfPath.Request_Response]
        notification = self.agreements_by_path[PerfPath.Notification]

        request_binding = resolve_binding(request_response, Partner_Name, Host_Name, Request_Response_Service, Request_Action)
        response_binding = resolve_binding(request_response, Host_Name, Partner_Name, Request_Response_Service, Response_Action)
        notification_binding = resolve_binding(notification, Host_Name, Partner_Name, Notification_Service, Notification_Action)

        out:'strbindingdict' = {
            MessageKind.Request: request_binding,
            MessageKind.Response: response_binding,
            MessageKind.Notification: notification_binding,
        }

        return out

# ################################################################################################################################

    def kind_of(self, action:'str') -> 'str':
        """ Returns the kind of a received message by its action.
        """
        out = _kinds[action]
        return out

# ################################################################################################################################

    def write(self, record:'stranydict') -> 'None':
        record['at'] = time()
        line = dumps(record)
        _ = self.records.write(line + '\n')

# ################################################################################################################################

    def _write_message(self, record_type:'str', message_id:'str') -> 'None':

        record:'stranydict' = {
            'type': record_type,
            'id': message_id,
        }

        self.write(record)

# ################################################################################################################################

    def _write_fault(self, message_id:'str', fault:'str') -> 'None':

        record:'stranydict' = {
            'type': RecordType.Fault,
            'id': message_id,
            'fault': fault,
        }

        self.write(record)

# ################################################################################################################################

    def spawn_busy(self, func:'callable_', *args:'any_') -> 'None':
        self.busy += 1
        _ = spawn(self._run_busy, func, args)

# ################################################################################################################################

    def _run_busy(self, func:'callable_', args:'anytuple') -> 'None':
        try:
            func(*args)
        finally:
            self.busy -= 1

# ################################################################################################################################

    def _is_fault(self, percent:'float') -> 'bool':

        if not percent:
            return False

        draw = self.random.random()
        drawn_percent = draw * 100

        out = drawn_percent < percent
        return out

# ################################################################################################################################

    def receive(self, path:'str', content_type:'str', body:'bytes') -> 'HTTPResponse':
        """ Receives one message and returns what the connection it arrived on is answered with.
        """
        arrived_at = time()
        agreement = self.agreements_by_path[path]
        headers = {'Content-Type': content_type}

        # The partner refuses some deliveries before it reads them ..
        if self._is_fault(self.config.refuse_percent):
            _, header, _ = read_message(headers, body)
            message_id = header.message_data.message_id
            self._write_fault(message_id, FaultType.Refused)

            out = HTTPResponse()
            out.status_code = SERVICE_UNAVAILABLE
            return out

        result = receive(agreement, self.local_keys, headers, body, self.receive_log, self.clock)

        # .. the application processes each message once its acknowledgment is on the way ..
        if header := result.header:
            if result.deliveries:
                self.spawn_busy(self._deliver, header, result.deliveries)

        # .. and the partner discards the acknowledgment of some messages it received.
        if header := result.header:
            if self._is_fault(self.config.drop_ack_percent):
                message_id = header.message_data.message_id
                self._write_fault(message_id, FaultType.Ack_Dropped)

                out = HTTPResponse()
                out.status_code = SERVICE_UNAVAILABLE
                return out

        # A message that is answered is recorded with the moment it arrived, while the record itself says when it was answered.
        if header := result.header:

            record:'stranydict' = {
                'type': RecordType.Received,
                'id': header.message_data.message_id,
                'arrived_at': arrived_at,
            }

            self.write(record)

        out = result.response
        return out

# ################################################################################################################################

    def _deliver(self, header:'MessageHeader', deliveries:'delivery_list') -> 'None':
        """ Processes each delivered message and confirms its delivery once it was processed.
        """
        for delivery in deliveries:
            kind = self.kind_of(delivery.action)

            record:'stranydict' = {
                'type': RecordType.Delivered,
                'id': delivery.message_id,
                'kind': kind,
                'ref': delivery.ref_to_message_id,
                'is_possible_duplicate': delivery.is_possible_duplicate,
            }

            self.write(record)

            processor = self.processors[kind]
            processor(header, delivery)

            self.receive_log.confirm(delivery.identity, delivery.cpa_id)

# ################################################################################################################################

    def deliver_recovered(self, message:'ReceivedMessage') -> 'None':
        """ Processes again a received message whose delivery was not confirmed before the process ended.
        """
        headers = {'Content-Type': message.content_type}
        _, header, payloads = read_message(headers, message.body)

        delivery = new_delivery(message.identity, message.cpa_id, header, payloads, True)
        delivery.record_id = message.record_id

        self.spawn_busy(self._deliver, header, [delivery])

# ################################################################################################################################

    def _answer_request(self, header:'MessageHeader', delivery:'Delivery') -> 'None':

        binding = self.bindings_by_kind[MessageKind.Response]

        options = SendOptions()
        options.conversation_id = header.conversation_id
        options.ref_to_message_id = header.message_data.message_id

        outbound = build(binding.agreement, self.local_keys, binding, self.payloads, self.clock, options)
        self._send(outbound, MessageKind.Response, None)

# ################################################################################################################################

    def _acknowledge_notification(self, header:'MessageHeader', delivery:'Delivery') -> 'None':

        kind = BusinessSignal.Receipt_Acknowledgement
        agreement = self.agreements_by_cpa_id[delivery.cpa_id]
        now = self.clock.now()

        document = new_ebbp_signal(kind, header, now, [])

        outbound = build_signal(agreement, self.local_keys, header, kind, document, self.clock)
        self._send(outbound, MessageKind.Signal, None)

# ################################################################################################################################

    def _match_reply(self, header:'MessageHeader', delivery:'Delivery') -> 'None':
        """ Moves the business transaction of the message a response or a signal refers to.
        """
        outcome = accept_business_message(self.business_log, header, delivery.payloads, self.clock)

        if outcome:
            state = outcome.state
        else:
            state = ''

        record:'stranydict' = {
            'type': RecordType.Matched,
            'id': delivery.message_id,
            'ref': delivery.ref_to_message_id,
            'state': state,
        }

        self.write(record)

# ################################################################################################################################

    def send_new(self, kind:'str') -> 'None':
        """ Sends a message that starts a business transaction.
        """
        binding = self.bindings_by_kind[kind]

        outbound = build(binding.agreement, self.local_keys, binding, self.payloads, self.clock)
        business = new_business_message(outbound)

        self._send(outbound, kind, business)

# ################################################################################################################################

    def _send(self, outbound:'OutboundMessage', kind:'str', business:'BusinessMessage | None') -> 'None':
        """ Records a message with its first delivery, makes the delivery, and schedules the next one if it is needed.
        """
        message_id = outbound.message_id
        ref = outbound.header.message_data.ref_to_message_id
        started_at = time()

        sent = new_sent_message(outbound, outbound.package)
        self.send_log.record_first_attempt(sent, business)

        # A message is recorded as sent once its record is committed, from the moment it was handed over.
        record:'stranydict' = {
            'type': RecordType.Sent,
            'id': message_id,
            'kind': kind,
            'ref': ref,
            'started_at': started_at,
        }

        self.write(record)

        self._post(message_id)
        self._schedule_if_open(message_id)

# ################################################################################################################################

    def _schedule_if_open(self, message_id:'str') -> 'None':
        if self.send_log.is_open(message_id):
            now = self.clock.now()
            self.scheduler.schedule(EntryKind.Delivery, message_id, now)

# ################################################################################################################################

    def schedule_recovered(self, sent:'SentMessage') -> 'None':
        now = self.clock.now()
        self.scheduler.schedule(EntryKind.Delivery, sent.message_id, now)

# ################################################################################################################################

    def _post(self, message_id:'str') -> 'None':
        """ Posts the stored wire form of a message and records what the response answered it with.
        """
        sent = self.send_log.get(message_id)
        body = self.send_log.wire_body(message_id)

        response = http_post(sent.endpoint, sent.wire_headers, body)

        # The partner posts some of its messages a second time.
        if self._is_fault(self.config.duplicate_percent):
            self._write_fault(message_id, FaultType.Duplicated)
            _ = http_post(sent.endpoint, sent.wire_headers, body)

        sent = self.send_log.get(message_id)
        agreement = self.agreements_by_cpa_id[sent.cpa_id]
        outbound = restore_outbound(agreement, self.local_keys, sent)

        if response is None:
            accept_no_answer(outbound)
            self._record_answer(sent, outbound, {}, b'')
        else:
            _ = accept_response(outbound, response.status_code, response.headers, response.body, self.clock)
            self._record_answer(sent, outbound, response.headers, response.body)

# ################################################################################################################################

    def _record_answer(self, sent:'SentMessage', outbound:'OutboundMessage', headers:'strstrdict', body:'bytes') -> 'None':
        """ Records the signal a message was answered with and, if the answer ended its exchange, the end of the exchange.
        """
        outcome = outbound.outcome

        if body:
            self.send_log.record_signal(sent, headers, body, outcome.signal_kind, outcome.error_code, outcome.error_severity)

        # An exchange that ended before this answer arrived ended with the answer that ended it ..
        if outbound.state != OutboundState.Pending:
            if not sent.retry_state.is_answered:
                self.send_log.record_completion(sent, outcome)

                if outbound.state == OutboundState.Failed:
                    self._write_message(RecordType.Failed, sent.message_id)
                else:
                    self._write_message(RecordType.Ack, sent.message_id)

        # .. while one that continues keeps the cause of the failure of this delivery.
        elif outcome.failure_cause:
            self.send_log.record_attempt_failure(sent, outcome.failure_cause, outcome.failure_detail)

# ################################################################################################################################

    def _on_delivery_due(self, message_id:'str', now:'datetime') -> 'datetime | None':
        """ Makes the delivery of a message that is due, as its record in the send log says, and returns when the record
        is to be read again, or None once its exchange ended or a resend was started, which schedules the message again.
        """
        if not self.send_log.is_open(message_id):
            return None

        sent = self.send_log.get(message_id)
        agreement = self.agreements_by_cpa_id[sent.cpa_id]
        outbound = restore_outbound(agreement, self.local_keys, sent)
        decision = next_action(outbound, self.clock)

        if decision.action == RetryAction.Give_Up:
            give_up(outbound)
            self.send_log.record_completion(sent, outbound.outcome)
            self._write_message(RecordType.Failed, message_id)
            return None

        # An answered message is not delivered again ..
        if decision.action == RetryAction.Done:
            return None

        # .. one that is not due yet has its record read again when it is ..
        if decision.action != RetryAction.Resend:
            return decision.at

        # .. and one that is due is resent in a greenlet of its own, so that the other deliveries do not wait for it.
        self.send_log.record_resend(sent)
        self.resends += 1
        self._write_message(RecordType.Attempt, message_id)
        self.spawn_busy(self._resend, message_id)

        return None

# ################################################################################################################################

    def _resend(self, message_id:'str') -> 'None':
        self._post(message_id)
        self._schedule_if_open(message_id)

# ################################################################################################################################
# ################################################################################################################################
