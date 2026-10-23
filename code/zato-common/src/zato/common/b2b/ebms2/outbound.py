# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta

# Zato
from zato.common.audit_log.common import B2BAttr
from zato.common.b2b.common.exceptions import B2BProtocolException
from zato.common.b2b.common.outcome import FinalState, Outcome, SignalKind
from zato.common.b2b.common.receipts import check_echoed_digests, collect_sent_digests, ReceiptException
from zato.common.b2b.common.retry import next_action as next_retry_action, RetryPolicy, RetryState
from zato.common.b2b.common.send_log import SentMessage
from zato.common.b2b.ebms2.common import Actor, Default, Direction, EbMS2Exception, ErrorCode, MSHService, PartyId, \
    SequenceStatus, Severity
from zato.common.b2b.ebms2.compose import compose, Composition, new_message_header, new_message_id, signing_for
from zato.common.b2b.ebms2.header import AckRequested, MessageOrder
from zato.common.b2b.ebms2.inbound_common import payload_digests, read_message
from zato.common.b2b.ebms2.message import collect_elements, parse_envelope
from zato.common.b2b.ebms2.packaging import Package, Payload, unpack
from zato.common.b2b.ebms2.reliability import is_order_guaranteed, per_message
from zato.common.b2b.ebms2.replies import reply_endpoint, wants_sync_reply
from zato.common.b2b.ebms2.security import is_signature_required, sender_non_repudiation, verify_message_signature
from zato.common.b2b.ebms2.signals import parse_acknowledgment, parse_error_list, parse_status_response, StatusRequest
from zato.common.soap.envelope import parse_fault
from zato.common.util.xml_.mime_ import new_content_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.common.clock import Clock
    from zato.common.b2b.common.keys import LocalKeys
    from zato.common.b2b.common.retry import RetryDecision
    from zato.common.b2b.ebms2.agreement import Agreement, Binding
    from zato.common.b2b.ebms2.common import party_id_list
    from zato.common.b2b.ebms2.header import MessageHeader
    from zato.common.b2b.ebms2.message import MessageElements
    from zato.common.b2b.ebms2.packaging import payload_list
    from zato.common.b2b.ebms2.signals import StatusResponse
    from zato.common.typing_ import any_, anylist, boolnone, dtnone, intnone, stranydict, strstrdict
    Agreement = Agreement
    any_ = any_
    anylist = anylist
    Binding = Binding
    boolnone = boolnone
    Clock = Clock
    dtnone = dtnone
    intnone = intnone
    LocalKeys = LocalKeys
    MessageElements = MessageElements
    MessageHeader = MessageHeader
    party_id_list = party_id_list
    payload_list = payload_list
    RetryDecision = RetryDecision
    StatusResponse = StatusResponse
    stranydict = stranydict
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The range of the HTTP status codes of a successful response.
_success_status_min = 200
_success_status_max = 299

# ################################################################################################################################
# ################################################################################################################################

class _Detail:
    """ The keys of the details a sent message is recorded with, which rebuilding it requires.
    """
    From_Party_IDs             = 'from_party_ids'
    To_Party_IDs               = 'to_party_ids'
    Service                    = 'service'
    Service_Type               = 'service_type'
    Action                     = 'action'
    Conversation_ID            = 'conversation_id'
    Ref_To_Message_ID          = 'ref_to_message_id'
    Timestamp                  = 'timestamp'
    Time_To_Live               = 'time_to_live'
    Duplicate_Elimination      = 'duplicate_elimination'
    Is_Ack_Requested           = 'is_ack_requested'
    Is_Ack_Signature_Requested = 'is_ack_signature_requested'
    Is_Sync_Reply              = 'is_sync_reply'
    Sent_Digests               = 'sent_digests'

# ################################################################################################################################
# ################################################################################################################################

class OutboundState:
    """ Where the exchange of one outgoing message stands.
    """
    Pending      = 'pending'
    Acknowledged = 'acknowledged'
    Answered     = 'answered'
    Failed       = 'failed'

# The state of an exchange that ended, by the final state it ended in.
_completed_states = {
    FinalState.Delivered: OutboundState.Acknowledged,
    FinalState.Answered:  OutboundState.Answered,
    FinalState.Failed:    OutboundState.Failed,
}

# ################################################################################################################################

@dataclass(init=False)
class SendOptions:
    """ What the caller decides about one outgoing message - each perMessage characteristic of the agreement
    and the values the header takes. Anything left at None follows the agreement and the defaults.
    """
    message_id:        str = ''
    conversation_id:   str = ''
    ref_to_message_id: str = ''
    time_to_live:      'dtnone' = None

    ack_requested:           'boolnone' = None
    ack_signature_requested: 'boolnone' = None
    duplicate_elimination:   'boolnone' = None

    # The position of the message in an ordered conversation.
    sequence_number: 'intnone' = None
    sequence_status: str = SequenceStatus.Continue

    # The MessageId a StatusRequest asks about.
    status_request_ref: str = ''

# ################################################################################################################################

@dataclass(init=False)
class OutboundMessage:
    """ One outgoing message with what is needed to send it and to follow its exchange to the end.
    """
    binding:    'Binding'
    local_keys: 'LocalKeys'
    header:     'MessageHeader'
    message_id: str

    # What goes on the wire, and where to.
    package:  'Package'
    endpoint: str

    # The signature of the message, if it is signed, and the digests a signed acknowledgment is to echo.
    signature:    'any_'
    sent_digests: 'strstrdict'

    is_ack_requested:           bool
    is_ack_signature_requested: bool
    is_sync_reply:              bool

    policy:      'RetryPolicy'
    retry_state: 'RetryState'

    state:   str = OutboundState.Pending
    outcome: 'Outcome'

    # The Pong or the StatusResponse a Ping or a StatusRequest was answered with.
    status_response: 'StatusResponse | None' = None

    # When the exchange ended, successfully or not.
    completed_at: 'dtnone' = None

# ################################################################################################################################
# ################################################################################################################################

def _per_message_option(setting:'str', option:'boolnone', default:'bool') -> 'bool':
    """ Resolves an always, never or perMessage characteristic with what the caller decided for the message.
    """
    if option is None:
        option = default

    out = per_message(setting, option)
    return out

# ################################################################################################################################

def _retry_policy(binding:'Binding') -> 'RetryPolicy':
    """ Returns how often and how frequently a message that is not acknowledged is sent again.
    """
    out = RetryPolicy()
    out.retries = 0
    out.retry_interval = timedelta(seconds=Default.Retry_Interval_Seconds)

    if sender_binding := binding.sender_binding:
        if reliable := sender_binding.reliable_messaging:
            if reliable.retries is not None:
                out.retries = reliable.retries
            if reliable.retry_interval:
                out.retry_interval = reliable.retry_interval.value

    return out

# ################################################################################################################################

def build(
    agreement:'Agreement',
    local_keys:'LocalKeys',
    binding:'Binding',
    payloads:'payload_list',
    clock:'Clock',
    options:'SendOptions | None'=None,
    ) -> 'OutboundMessage':
    """ Builds a message that is to be sent under a binding of an agreement. Sending it is left to the caller,
    which then passes what comes back to accept_response or to accept_signal.
    """
    if options is None:
        options = SendOptions()

    if binding.agreement is not agreement:
        raise EbMS2Exception(ErrorCode.Inconsistent, 'The binding belongs to another agreement')

    now = clock.now()

    if not (message_id := options.message_id):
        message_id = new_message_id()

    if not (conversation_id := options.conversation_id):
        conversation_id = new_message_id()

    header = new_message_header(binding, now, conversation_id, message_id, options.ref_to_message_id)
    header.message_data.time_to_live = options.time_to_live

    characteristics = binding.characteristics

    is_ack_requested = _per_message_option(
        characteristics.ack_requested, options.ack_requested, Default.Ack_Requested_Per_Message)

    is_ack_signature_requested = _per_message_option(
        characteristics.ack_signature_requested, options.ack_signature_requested, Default.Ack_Signature_Requested_Per_Message)

    header.duplicate_elimination = _per_message_option(
        characteristics.duplicate_elimination, options.duplicate_elimination, Default.Duplicate_Elimination_Per_Message)

    # Each payload goes into a MIME part of its own, under a Content-ID it is referenced by.
    parts:'payload_list' = []

    for payload in payloads:

        part = Payload()
        part.content_type = payload.content_type
        part.data = payload.data

        if payload.content_id:
            part.content_id = payload.content_id
        else:
            part.content_id = new_content_id()

        parts.append(part)

    composition = Composition()
    composition.header = header
    composition.payloads = parts
    composition.sync_reply = wants_sync_reply(binding)

    if is_ack_requested:

        if not (actor := characteristics.actor):
            actor = Actor.To_Party_MSH

        ack_requested = AckRequested()
        ack_requested.signed = is_ack_signature_requested
        ack_requested.actor = actor
        composition.ack_requested = ack_requested

    if is_order_guaranteed(binding):

        if options.sequence_number is None:
            raise EbMS2Exception(ErrorCode.Inconsistent, 'The agreement guarantees message order and no sequence number is given')

        message_order = MessageOrder()
        message_order.sequence_number = options.sequence_number
        message_order.status = options.sequence_status
        composition.message_order = message_order

    if binding.action == MSHService.Status_Request:
        status_request = StatusRequest()
        status_request.ref_to_message_id = options.status_request_ref
        composition.status_request = status_request

    if is_signature_required(binding):
        non_repudiation = sender_non_repudiation(binding)
        composition.signing = signing_for(non_repudiation, local_keys)

    composed = compose(composition)

    if composed.signature is not None:
        sent_digests = collect_sent_digests(composed.signature)
    else:
        sent_digests = {}

    # The message counts as delivered once when it is built, since the caller sends it right away.
    retry_state = RetryState()
    retry_state.attempt_count = 1
    retry_state.last_attempt_at = now
    retry_state.expires_at = options.time_to_live

    outcome = Outcome()
    outcome.payload_digests = payload_digests(parts)
    outcome.final_state = FinalState.Failed

    out = OutboundMessage()
    out.binding = binding
    out.local_keys = local_keys
    out.header = header
    out.message_id = message_id
    out.package = composed.package
    out.endpoint = reply_endpoint(binding)
    out.signature = composed.signature
    out.sent_digests = sent_digests
    out.is_ack_requested = is_ack_requested
    out.is_ack_signature_requested = is_ack_signature_requested
    out.is_sync_reply = composition.sync_reply
    out.policy = _retry_policy(binding)
    out.retry_state = retry_state
    out.outcome = outcome

    return out

# ################################################################################################################################
# ################################################################################################################################

def _party_ids_to_list(party_ids:'party_id_list') -> 'anylist':
    out:'anylist' = []

    for party_id in party_ids:
        item = [party_id.value, party_id.id_type]
        out.append(item)

    return out

# ################################################################################################################################

def _party_ids_from_list(items:'anylist') -> 'party_id_list':
    out:'party_id_list' = []

    for value, id_type in items:
        party_id = PartyId()
        party_id.value = value
        party_id.id_type = id_type
        out.append(party_id)

    return out

# ################################################################################################################################

def new_sent_message(outbound:'OutboundMessage', wire:'Package') -> 'SentMessage':
    """ Returns how a message that goes on the wire in the given form is recorded in a send log,
    with the details that restore_outbound rebuilds it from.
    """
    binding = outbound.binding
    header = outbound.header
    message_data = header.message_data

    if time_to_live := message_data.time_to_live:
        time_to_live = time_to_live.isoformat()

    from_party_ids = _party_ids_to_list(header.from_party.party_ids)
    to_party_ids = _party_ids_to_list(header.to_party.party_ids)
    timestamp = message_data.timestamp.isoformat()

    details:'stranydict' = {
        _Detail.From_Party_IDs: from_party_ids,
        _Detail.To_Party_IDs: to_party_ids,
        _Detail.Service: header.service,
        _Detail.Service_Type: header.service_type,
        _Detail.Action: header.action,
        _Detail.Conversation_ID: header.conversation_id,
        _Detail.Ref_To_Message_ID: message_data.ref_to_message_id,
        _Detail.Timestamp: timestamp,
        _Detail.Time_To_Live: time_to_live,
        _Detail.Duplicate_Elimination: header.duplicate_elimination,
        _Detail.Is_Ack_Requested: outbound.is_ack_requested,
        _Detail.Is_Ack_Signature_Requested: outbound.is_ack_signature_requested,
        _Detail.Is_Sync_Reply: outbound.is_sync_reply,
        _Detail.Sent_Digests: outbound.sent_digests,
    }

    out = SentMessage()
    out.message_id = outbound.message_id
    out.cpa_id = binding.agreement.cpa_id
    out.from_party = binding.from_party.party_name
    out.to_party = binding.to_party.party_name
    out.endpoint = outbound.endpoint
    out.attrs = {B2BAttr.Service: header.service, B2BAttr.Action: header.action}
    out.policy = outbound.policy
    out.retry_state = outbound.retry_state
    out.outcome = outbound.outcome
    out.details = details
    out.wire_headers = wire.headers
    out.wire_body = wire.body

    return out

# ################################################################################################################################

def restore_outbound(agreement:'Agreement', local_keys:'LocalKeys', sent:'SentMessage') -> 'OutboundMessage':
    """ Rebuilds a message from its record in a send log, so that its exchange continues where the record says it stands.
    The header is rebuilt from the recorded details rather than read from the wire form, which may have been changed
    after the message was built.
    """
    details = sent.details

    # The binding is resolved again from the agreement the message was sent under ..
    from_party_ids = _party_ids_from_list(details[_Detail.From_Party_IDs])
    to_party_ids = _party_ids_from_list(details[_Detail.To_Party_IDs])
    service = details[_Detail.Service]
    service_type = details[_Detail.Service_Type]
    action = details[_Detail.Action]

    binding = agreement.resolve(from_party_ids, to_party_ids, service, service_type, action, Direction.Send)

    # .. the header is rebuilt with the values it was sent with ..
    timestamp = datetime.fromisoformat(details[_Detail.Timestamp])
    conversation_id = details[_Detail.Conversation_ID]
    ref_to_message_id = details[_Detail.Ref_To_Message_ID]

    header = new_message_header(binding, timestamp, conversation_id, sent.message_id, ref_to_message_id)
    header.duplicate_elimination = details[_Detail.Duplicate_Elimination]

    if time_to_live := details[_Detail.Time_To_Live]:
        header.message_data.time_to_live = datetime.fromisoformat(time_to_live)

    # .. the bytes are those of the first delivery ..
    package = Package()
    package.headers = sent.wire_headers
    package.body = sent.wire_body

    # .. and an exchange that ended is in the state its final state says.
    if sent.retry_state.is_answered:
        state = _completed_states[sent.outcome.final_state]
    else:
        state = OutboundState.Pending

    out = OutboundMessage()
    out.binding = binding
    out.local_keys = local_keys
    out.header = header
    out.message_id = sent.message_id
    out.package = package
    out.endpoint = sent.endpoint
    out.signature = None
    out.sent_digests = details[_Detail.Sent_Digests]
    out.is_ack_requested = details[_Detail.Is_Ack_Requested]
    out.is_ack_signature_requested = details[_Detail.Is_Ack_Signature_Requested]
    out.is_sync_reply = details[_Detail.Is_Sync_Reply]
    # The exchange continues on copies, so that the record read from the send log stays as it was read.
    out.policy = deepcopy(sent.policy)
    out.retry_state = deepcopy(sent.retry_state)
    out.state = state
    out.outcome = deepcopy(sent.outcome)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _fail(outbound:'OutboundMessage', error_code:'str', severity:'str'=Severity.Error) -> 'None':
    """ Ends the exchange of a message with an error.
    """
    outbound.state = OutboundState.Failed
    outbound.retry_state.is_answered = True
    outbound.outcome.signal_kind = SignalKind.Error
    outbound.outcome.error_code = error_code
    outbound.outcome.error_severity = severity
    outbound.outcome.final_state = FinalState.Failed

# ################################################################################################################################

def _complete(outbound:'OutboundMessage', state:'str', signal_kind:'str', final_state:'str') -> 'None':
    """ Ends the exchange of a message successfully.
    """
    outbound.state = state
    outbound.retry_state.is_answered = True
    outbound.outcome.signal_kind = signal_kind
    outbound.outcome.final_state = final_state
    outbound.outcome.delivered = final_state == FinalState.Delivered

# ################################################################################################################################

def _accept_acknowledgment(outbound:'OutboundMessage', elements:'MessageElements', header:'MessageHeader', payloads:'any_') \
    -> 'None':
    """ Accepts the acknowledgment of a message, which a signed message requires to be signed and to echo its references.
    """
    acknowledgment = parse_acknowledgment(elements.acknowledgment)

    # An acknowledgment of another message says nothing about this one.
    if acknowledgment.ref_to_message_id != outbound.message_id:
        return

    agreement = outbound.binding.agreement

    signal_binding = agreement.resolve(header.from_party.party_ids, header.to_party.party_ids,
        MSHService.Service, '', MSHService.Acknowledgment, Direction.Receive)

    try:
        verified = verify_message_signature(signal_binding, outbound.local_keys, elements.envelope, elements.signature, payloads)

        if outbound.is_ack_signature_requested:
            if verified is None:
                raise EbMS2Exception(ErrorCode.Security_Failure, 'The acknowledgment is not signed')

        if verified:
            if outbound.sent_digests:
                if acknowledgment.references:
                    check_echoed_digests(acknowledgment.references, outbound.sent_digests)

    except (B2BProtocolException, ReceiptException):
        _fail(outbound, ErrorCode.Security_Failure)
        return

    outbound.outcome.signature_verified = verified is not None
    _complete(outbound, OutboundState.Acknowledged, SignalKind.Receipt, FinalState.Delivered)

# ################################################################################################################################

def _accept_message(outbound:'OutboundMessage', headers:'strstrdict', body:'bytes') -> 'None':
    """ Accepts a message service handler message that answers the outgoing message - an acknowledgment,
    an error message, a Pong or a StatusResponse. Anything that cannot be read leaves the exchange as it was.
    """
    try:
        envelope, header, payloads = read_message(headers, body)
        elements = collect_elements(envelope)
    except B2BProtocolException:
        return

    if elements.acknowledgment is not None:
        _accept_acknowledgment(outbound, elements, header, payloads)
        return

    # An error message about this message ends its exchange, unless all of its errors are warnings.
    if elements.error_list is not None:

        if header.message_data.ref_to_message_id != outbound.message_id:
            return

        error_list = parse_error_list(elements.error_list)
        first_error = error_list.errors[0]

        if error_list.highest_severity == Severity.Error:
            _fail(outbound, first_error.error_code)
        else:
            outbound.outcome.error_code = first_error.error_code
            outbound.outcome.error_severity = Severity.Warning

        return

    if header.message_data.ref_to_message_id != outbound.message_id:
        return

    if header.action == MSHService.Pong:
        _complete(outbound, OutboundState.Answered, SignalKind.Pong, FinalState.Answered)

    elif header.action == MSHService.Status_Response:
        if elements.status_response is not None:
            outbound.status_response = parse_status_response(elements.status_response)
            _complete(outbound, OutboundState.Answered, SignalKind.Status, FinalState.Answered)

# ################################################################################################################################

def _record_completion(outbound:'OutboundMessage', clock:'Clock') -> 'None':
    if outbound.state != OutboundState.Pending:
        if outbound.completed_at is None:
            outbound.completed_at = clock.now()

# ################################################################################################################################

def _is_success(status:'int') -> 'bool':
    if status < _success_status_min:
        out = False
    else:
        out = status <= _success_status_max

    return out

# ################################################################################################################################

def _accept_failure(outbound:'OutboundMessage', headers:'strstrdict', body:'bytes') -> 'None':
    """ Accepts the body of a failed HTTP response - a SOAP Fault, which permanently rejects the message
    and whose reason is the error code followed by the description, or an error message.
    """
    try:
        unpacked = unpack(headers, body)
        envelope = parse_envelope(unpacked.envelope)
    except B2BProtocolException:
        return

    if fault := parse_fault(envelope):
        error_code, _, _ = fault.reason.partition(':')
        error_code = error_code.strip()
        _fail(outbound, error_code)

    else:
        _accept_message(outbound, headers, body)

# ################################################################################################################################

def accept_response(outbound:'OutboundMessage', status:'int', headers:'strstrdict', body:'bytes', clock:'Clock') -> 'Outcome':
    """ Processes the HTTP response a message was answered with - a synchronous acknowledgment, an error message,
    a SOAP Fault or a failure of the transport.
    """
    # A successful response carries a synchronous signal or nothing, and nothing completes a message
    # that expects no acknowledgment ..
    if _is_success(status):
        if body:
            _accept_message(outbound, headers, body)

        elif not outbound.is_ack_requested:
            if not outbound.binding.is_msh:
                _complete(outbound, OutboundState.Acknowledged, SignalKind.No_Signal, FinalState.Delivered)

    # .. a failed one with a body carries a SOAP Fault or an error message ..
    elif body:
        _accept_failure(outbound, headers, body)

    # .. and any other failure leaves the message to be sent again.
    _record_completion(outbound, clock)

    out = outbound.outcome
    return out

# ################################################################################################################################

def accept_signal(outbound:'OutboundMessage', headers:'strstrdict', body:'bytes', clock:'Clock') -> 'Outcome':
    """ Processes a message service handler message that answers the message asynchronously.
    """
    _accept_message(outbound, headers, body)
    _record_completion(outbound, clock)

    out = outbound.outcome
    return out

# ################################################################################################################################
# ################################################################################################################################

def next_action(outbound:'OutboundMessage', clock:'Clock') -> 'RetryDecision':
    """ Returns whether a message is to be sent again, waited on or given up on, and when.
    """
    now = clock.now()

    out = next_retry_action(outbound.policy, outbound.retry_state, now)
    return out

# ################################################################################################################################

def record_resend(outbound:'OutboundMessage', clock:'Clock') -> 'None':
    """ Records that a message was sent again, with the same bytes and the same MessageId.
    """
    outbound.retry_state.attempt_count += 1
    outbound.retry_state.last_attempt_at = clock.now()
    outbound.outcome.retry_count = outbound.retry_state.attempt_count - 1

# ################################################################################################################################

def give_up(outbound:'OutboundMessage') -> 'None':
    """ Ends the exchange of a message that ran out of retries without an acknowledgment.
    """
    _fail(outbound, ErrorCode.Delivery_Failure)

# ################################################################################################################################
# ################################################################################################################################
