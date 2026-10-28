# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from http.client import INTERNAL_SERVER_ERROR, OK

# Zato
from zato.common.b2b.common.exceptions import B2BProtocolException
from zato.common.b2b.common.outcome import FinalState, Outcome, SignalKind
from zato.common.b2b.common.store import HeldMessage, MessageIdentity, StoredMessage, StoredResponse
from zato.common.b2b.ebms2.common import Actor, Direction, EbMS2Exception, ErrorCode, MessageStatus, MSHService, \
    Protocol_Name, Root_Content_Type, Severity
from zato.common.b2b.ebms2.header import parse_ack_requested, parse_manifest, parse_message_order, parse_sync_reply
from zato.common.b2b.ebms2.inbound_common import AsyncSignal, Delivery, HTTPResponse, payload_digests, read_message, \
    ReceivedSignal
from zato.common.b2b.ebms2.message import collect_elements, serialize
from zato.common.b2b.ebms2.packaging import normalize_content_id, Package
from zato.common.b2b.ebms2.reliability import conversation_key, decide_order, is_duplicate_elimination, \
    is_order_guaranteed, message_identity, OrderAction, per_message, persist_duration
from zato.common.b2b.ebms2.replies import build_reply, is_sync_reply, Reply, reply_binding, reply_endpoint
from zato.common.b2b.ebms2.security import is_signature_required, verify_message_signature
from zato.common.b2b.ebms2.signals import Acknowledgment, new_error_list, parse_acknowledgment, parse_error_list, \
    parse_status_request, parse_status_response, StatusResponse
from zato.common.b2b.ebms2.xml_ import get_eb_attribute, location
from zato.common.soap.common import FaultCode, SOAPVersion
from zato.common.soap.envelope import build_fault

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.b2b.common.clock import Clock
    from zato.common.b2b.common.keys import LocalKeys
    from zato.common.b2b.common.store import MessageStore
    from zato.common.b2b.ebms2.agreement import Agreement, Binding
    from zato.common.b2b.ebms2.header import MessageHeader
    from zato.common.b2b.ebms2.inbound_common import delivery_list
    from zato.common.b2b.ebms2.message import MessageElements
    from zato.common.b2b.ebms2.packaging import payload_list
    from zato.common.b2b.ebms2.signature import VerifiedSignature
    from zato.common.typing_ import strstrdict
    Agreement = Agreement
    Binding = Binding
    Clock = Clock
    datetime = datetime
    delivery_list = delivery_list
    LocalKeys = LocalKeys
    MessageElements = MessageElements
    MessageHeader = MessageHeader
    MessageStore = MessageStore
    payload_list = payload_list
    strstrdict = strstrdict
    VerifiedSignature = VerifiedSignature

# ################################################################################################################################
# ################################################################################################################################

_time_to_live_location = location('MessageHeader', 'MessageData', 'TimeToLive')
_manifest_location = location('Manifest')
_cpa_id_location = location('MessageHeader', 'CPAId')
_action_location = location('MessageHeader', 'Action')
_status_request_location = location('StatusRequest')

# The kind of signal each message service handler action that answers an earlier message is.
_signal_kinds = {
    MSHService.Acknowledgment:  SignalKind.Receipt,
    MSHService.Message_Error:   SignalKind.Error,
    MSHService.Pong:            SignalKind.Pong,
    MSHService.Status_Response: SignalKind.Status,
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class InboundResult:
    """ What receiving one message produced.
    """
    deliveries:   'delivery_list'
    response:     'HTTPResponse'
    async_signal: 'AsyncSignal | None' = None
    signal:       'ReceivedSignal | None' = None
    header:       'MessageHeader | None' = None
    outcome:      'Outcome'

    def __init__(self) -> 'None':
        self.deliveries = []
        self.response = HTTPResponse()
        self.outcome = Outcome()

# ################################################################################################################################

@dataclass(init=False)
class _Context:
    """ The state of one message as it passes through the steps of receive.
    """
    agreement:  'Agreement'
    local_keys: 'LocalKeys'
    store:      'MessageStore'
    now:        'datetime'

    content_type: str
    body:         bytes

    header:   'MessageHeader'
    elements: 'MessageElements | None' = None
    payloads: 'payload_list'

    binding: 'Binding | None' = None

# ################################################################################################################################
# ################################################################################################################################

def _build_fault(out:'InboundResult', error:'B2BProtocolException') -> 'None':
    """ Answers a message whose MessageHeader cannot be read with a SOAP Fault, since an error message
    is to name the MessageId it refers to.
    """
    reason = f'{error.error_code}: {error.detail}'
    envelope = build_fault(SOAPVersion.V11, FaultCode.Sender, reason)

    out.response.status_code = INTERNAL_SERVER_ERROR
    out.response.content_type = Root_Content_Type
    out.response.body = serialize(envelope)

    out.outcome.signal_kind = SignalKind.Error
    out.outcome.error_code = error.error_code
    out.outcome.final_state = FinalState.Rejected

# ################################################################################################################################

def _place_reply(ctx:'_Context', out:'InboundResult', reply:'Reply', is_sync:'bool') -> 'StoredResponse':
    """ Places a reply in the HTTP response or in an asynchronous signal, and returns it in the form a message store keeps.
    A reply is signed when it is asked to be, or when the agreement requires the replying party to sign its messages.
    """
    if ctx.binding:
        signing_binding = reply_binding(ctx.agreement, ctx.header, reply.action)
        if is_signature_required(signing_binding):
            reply.is_signed = True

    package = build_reply(ctx.agreement, ctx.local_keys, ctx.header, reply, ctx.now)
    content_type = package.headers['Content-Type']

    if is_sync:
        out.response.content_type = content_type
        out.response.body = package.body

    else:
        binding = reply_binding(ctx.agreement, ctx.header, reply.action)

        async_signal = AsyncSignal()
        async_signal.endpoint = reply_endpoint(binding)
        async_signal.package = package
        out.async_signal = async_signal

    stored = StoredResponse()
    stored.status_code = OK
    stored.content_type = content_type
    stored.body = package.body
    stored.is_synchronous = is_sync

    return stored

# ################################################################################################################################

def _is_sync(ctx:'_Context', binding:'Binding') -> 'bool':
    """ Says whether the replies to a message go back on the connection it arrived on.
    """
    if ctx.elements is None:
        out = True

    elif ctx.elements.sync_reply is None:
        out = False

    else:
        parse_sync_reply(ctx.elements.sync_reply)
        out = is_sync_reply(binding)

    return out

# ################################################################################################################################

def _reject(ctx:'_Context', out:'InboundResult', error:'B2BProtocolException') -> 'None':
    """ Answers a message with an error message. A message without a usable binding is answered
    on the connection it arrived on, since there is no channel to send the error message to.
    """
    error_list = new_error_list(error.error_code, error.detail, error.location)

    reply = Reply()
    reply.action = MSHService.Message_Error
    reply.error_list = error_list

    is_sync = True

    if binding := ctx.binding:
        try:
            is_sync = _is_sync(ctx, binding)
        except B2BProtocolException:
            is_sync = True

    try:
        _ = _place_reply(ctx, out, reply, is_sync)
    except B2BProtocolException:
        out.async_signal = None
        _ = _place_reply(ctx, out, reply, True)

    out.outcome.signal_kind = SignalKind.Error
    out.outcome.error_code = error.error_code
    out.outcome.error_severity = error_list.highest_severity
    out.outcome.final_state = FinalState.Rejected

# ################################################################################################################################

def _reports_error(ctx:'_Context') -> 'bool':
    """ Says whether a message is an error message that reports at least one error, which is never answered
    with another error message.
    """
    out = False

    if elements := ctx.elements:
        if elements.error_list is not None:
            highest_severity = get_eb_attribute(elements.error_list, 'highestSeverity')
            out = highest_severity == Severity.Error

    return out

# ################################################################################################################################

def _reject_unanswered(out:'InboundResult', error:'B2BProtocolException') -> 'None':
    """ Rejects an error message in error with an empty HTTP response.
    """
    out.outcome.signal_kind = SignalKind.Error
    out.outcome.error_code = error.error_code
    out.outcome.error_severity = Severity.Error
    out.outcome.final_state = FinalState.Rejected

# ################################################################################################################################
# ################################################################################################################################

def _check_agreement(ctx:'_Context') -> 'None':
    """ Rejects a message that names another agreement, or that arrives outside the period of this one.
    """
    agreement = ctx.agreement

    if ctx.header.cpa_id != agreement.cpa_id:
        raise EbMS2Exception(ErrorCode.Value_Not_Recognized, f'Unknown CPAId `{ctx.header.cpa_id}`', _cpa_id_location)

    is_before = ctx.now < agreement.start
    is_after = ctx.now > agreement.end

    for is_outside in (is_before, is_after):
        if is_outside:
            raise EbMS2Exception(ErrorCode.Inconsistent, f'Agreement `{agreement.cpa_id}` is not in effect', _cpa_id_location)

# ################################################################################################################################

def _check_manifest(elements:'MessageElements', payloads:'payload_list') -> 'None':
    """ Rejects a message whose manifest and payloads do not agree with each other.
    """
    if elements.manifest is None:
        if payloads:
            raise EbMS2Exception(ErrorCode.Inconsistent, 'The message has payloads and no Manifest', _manifest_location)

    else:
        manifest = parse_manifest(elements.manifest)
        content_ids = set()

        for payload in payloads:
            content_ids.add(payload.content_id)

        for reference in manifest.references:
            if reference.href.startswith('cid:'):
                content_id = normalize_content_id(reference.href)
                if content_id not in content_ids:
                    raise EbMS2Exception(
                        ErrorCode.MIME_Problem, f'Manifest reference `{reference.href}` names no MIME part', _manifest_location)

# ################################################################################################################################

def _new_delivery(binding:'Binding', header:'MessageHeader', payloads:'payload_list') -> 'Delivery':
    out = Delivery()
    out.message_id = header.message_data.message_id
    out.conversation_id = header.conversation_id
    out.ref_to_message_id = header.message_data.ref_to_message_id
    out.service = header.service
    out.service_type = header.service_type
    out.action = header.action
    out.from_party = binding.from_party.party_name
    out.to_party = binding.to_party.party_name
    out.payloads = payloads

    return out

# ################################################################################################################################

def _deliver_released(ctx:'_Context', binding:'Binding', held:'HeldMessage', out:'InboundResult') -> 'None':
    """ Delivers a held message of an ordered conversation that the message just received made next in line.
    """
    held_headers = {'Content-Type': held.content_type}
    _, header, payloads = read_message(held_headers, held.body)

    delivery = _new_delivery(binding, header, payloads)
    out.deliveries.append(delivery)

    identity = message_identity(binding, header)
    ctx.store.set_status(identity, MessageStatus.Processed)

# ################################################################################################################################

def _acknowledgment(ctx:'_Context', elements:'MessageElements', binding:'Binding', verified:'VerifiedSignature | None') -> \
    'Reply | None':
    """ Returns the acknowledgment a business message is answered with, if it is to be acknowledged.
    """
    characteristics = binding.characteristics

    if elements.ack_requested is not None:
        ack_requested = parse_ack_requested(elements.ack_requested)
        is_requested = True
        is_signed_requested = ack_requested.signed
        actor = ack_requested.actor
    else:
        is_requested = False
        is_signed_requested = False
        actor = Actor.To_Party_MSH

    if not per_message(characteristics.ack_requested, is_requested):
        out = None

    else:
        is_signed = per_message(characteristics.ack_signature_requested, is_signed_requested)

        acknowledgment = Acknowledgment()
        acknowledgment.timestamp = ctx.now
        acknowledgment.ref_to_message_id = ctx.header.message_data.message_id
        acknowledgment.from_party = ctx.header.to_party

        # The acknowledgment is addressed to the same actor that requested it.
        acknowledgment.actor = actor

        # A signed acknowledgment of a signed message proves what it acknowledges with the references of that signature.
        if is_signed:
            if verified:
                acknowledgment.references = verified.references

        out = Reply()
        out.action = MSHService.Acknowledgment
        out.acknowledgment = acknowledgment
        out.is_signed = is_signed

    return out

# ################################################################################################################################

def _answer_duplicate(ctx:'_Context', out:'InboundResult', identity:'MessageIdentity') -> 'None':
    """ Answers a duplicate with the response stored for the first copy of the message, and delivers nothing.
    """
    out.response = HTTPResponse()
    out.async_signal = None
    out.outcome.duplicate = True
    out.outcome.final_state = FinalState.Duplicate

    if stored := ctx.store.get(identity, ctx.now):

        response = stored.response

        if response.is_synchronous:
            out.response.status_code = response.status_code
            out.response.content_type = response.content_type
            out.response.body = response.body

        else:
            binding = reply_binding(ctx.agreement, ctx.header, MSHService.Acknowledgment)

            package = Package()
            package.body = response.body
            package.headers = {'Content-Type': response.content_type}

            async_signal = AsyncSignal()
            async_signal.endpoint = reply_endpoint(binding)
            async_signal.package = package
            out.async_signal = async_signal

# ################################################################################################################################

def _no_response() -> 'StoredResponse':
    """ Returns the response of a message that is answered with an empty HTTP response.
    """
    out = StoredResponse()
    out.status_code = OK
    out.content_type = ''
    out.body = b''
    out.is_synchronous = True

    return out

# ################################################################################################################################

def _receive_business(ctx:'_Context', elements:'MessageElements', out:'InboundResult') -> 'None':
    """ Receives a business message - the binding, the time to live, the signature, duplicate elimination,
    the order of delivery, the delivery itself and the acknowledgment.
    """
    header = ctx.header

    binding = ctx.agreement.resolve(
        header.from_party.party_ids, header.to_party.party_ids, header.service, header.service_type, header.action,
        Direction.Receive)

    ctx.binding = binding

    # A message that has outlived its time to live is not delivered ..
    if time_to_live := header.message_data.time_to_live:
        if ctx.now > time_to_live:
            raise EbMS2Exception(ErrorCode.Time_To_Live_Expired, 'The message has expired', _time_to_live_location)

    # .. nor is one whose signature does not verify, or that is not signed when it is to be ..
    verified = verify_message_signature(binding, ctx.local_keys, elements.envelope, elements.signature, ctx.payloads)
    out.outcome.signature_verified = verified is not None

    # .. or whose manifest names payloads that are not there.
    _check_manifest(elements, ctx.payloads)

    if elements.message_order is not None:
        message_order = parse_message_order(elements.message_order)
    else:
        message_order = None

    # The acknowledgment is built before the message is recorded, so that a duplicate is answered with the same one.
    is_sync = _is_sync(ctx, binding)

    if acknowledgment := _acknowledgment(ctx, elements, binding, verified):
        stored_response = _place_reply(ctx, out, acknowledgment, is_sync)
        out.outcome.signal_kind = SignalKind.Receipt
    else:
        stored_response = _no_response()

    identity = message_identity(binding, header)
    duration = persist_duration(binding)

    stored = StoredMessage()
    stored.status = MessageStatus.Received
    stored.received_at = ctx.now
    stored.expires_at = ctx.now + duration
    stored.response = stored_response

    # Only the copy that records the message first is delivered, unless duplicates are not eliminated ..
    is_claimed = ctx.store.claim(identity, stored)

    if not is_claimed:
        if is_duplicate_elimination(binding, header):
            _answer_duplicate(ctx, out, identity)
            return

    # .. a message of an ordered conversation waits for the ones before it ..
    if is_order_guaranteed(binding):

        held = HeldMessage()
        held.content_type = ctx.content_type
        held.body = ctx.body

        key = conversation_key(binding, header)
        decision = decide_order(ctx.store, key, message_order, held)

        if decision.action == OrderAction.Hold:
            out.outcome.final_state = FinalState.Held
            return

        if decision.action == OrderAction.Skip:
            out.outcome.duplicate = True
            out.outcome.final_state = FinalState.Duplicate
            return

        released = decision.released

    else:
        released = []

    # .. and any other message is delivered, followed by the held ones it released.
    delivery = _new_delivery(binding, header, ctx.payloads)
    out.deliveries.append(delivery)
    ctx.store.set_status(identity, MessageStatus.Processed)

    for held_message in released:
        _deliver_released(ctx, binding, held_message, out)

    out.outcome.delivered = True
    out.outcome.payload_digests = payload_digests(ctx.payloads)
    out.outcome.final_state = FinalState.Delivered

# ################################################################################################################################
# ################################################################################################################################

def _receive_signal(ctx:'_Context', elements:'MessageElements', binding:'Binding', out:'InboundResult') -> 'None':
    """ Receives a message service handler message that answers a message sent earlier, for the caller to match it.
    """
    signal = ReceivedSignal()
    signal.kind = _signal_kinds[ctx.header.action]
    signal.header = ctx.header
    signal.ref_to_message_id = ctx.header.message_data.ref_to_message_id
    signal.content_type = ctx.content_type
    signal.body = ctx.body

    if elements.acknowledgment is not None:
        signal.acknowledgment = parse_acknowledgment(elements.acknowledgment)

    if elements.error_list is not None:
        signal.error_list = parse_error_list(elements.error_list)

    if elements.status_response is not None:
        signal.status_response = parse_status_response(elements.status_response)

    out.signal = signal
    out.outcome.signal_kind = signal.kind
    out.outcome.final_state = FinalState.Answered

# ################################################################################################################################

def _answer_status_request(ctx:'_Context', elements:'MessageElements', binding:'Binding') -> 'Reply':
    """ Returns the status of a message that the party asking for it sent earlier.
    """
    if elements.status_request is None:
        raise EbMS2Exception(ErrorCode.Inconsistent, 'Element `StatusRequest` is missing', _status_request_location)

    status_request = parse_status_request(elements.status_request)

    # The message asked about is one that the asking party sent to this one.
    from_party = binding.from_party.party_name
    to_party = binding.to_party.party_name
    identity = MessageIdentity(Protocol_Name, from_party, to_party, status_request.ref_to_message_id)

    status_response = StatusResponse()
    status_response.ref_to_message_id = status_request.ref_to_message_id

    if stored := ctx.store.get(identity, ctx.now):
        status_response.message_status = stored.status
        status_response.timestamp = stored.received_at
    else:
        status_response.message_status = MessageStatus.Not_Recognized

    out = Reply()
    out.action = MSHService.Status_Response
    out.status_response = status_response

    return out

# ################################################################################################################################

def _receive_msh(ctx:'_Context', elements:'MessageElements', out:'InboundResult') -> 'None':
    """ Receives a message of the message service handler service - a Ping or a StatusRequest that is answered,
    or a signal that answers a message sent earlier.
    """
    header = ctx.header

    binding = ctx.agreement.resolve(
        header.from_party.party_ids, header.to_party.party_ids, MSHService.Service, '', header.action, Direction.Receive)

    ctx.binding = binding

    # A signature on a message service handler message is verified whenever there is one.
    if elements.signature is not None:
        verified = verify_message_signature(binding, ctx.local_keys, elements.envelope, elements.signature, ctx.payloads)
        out.outcome.signature_verified = verified is not None

    if header.action in _signal_kinds:
        _receive_signal(ctx, elements, binding, out)

    elif header.action == MSHService.Ping:

        reply = Reply()
        reply.action = MSHService.Pong

        is_sync = _is_sync(ctx, binding)
        _ = _place_reply(ctx, out, reply, is_sync)

        out.outcome.signal_kind = SignalKind.Pong
        out.outcome.final_state = FinalState.Answered

    elif header.action == MSHService.Status_Request:

        reply = _answer_status_request(ctx, elements, binding)

        is_sync = _is_sync(ctx, binding)
        _ = _place_reply(ctx, out, reply, is_sync)

        out.outcome.signal_kind = SignalKind.Status
        out.outcome.final_state = FinalState.Answered

    else:
        raise EbMS2Exception(ErrorCode.Not_Supported, f'Action `{header.action}` of the MSH service is not supported',
            _action_location)

# ################################################################################################################################
# ################################################################################################################################

def receive(
    agreement:'Agreement',
    local_keys:'LocalKeys',
    headers:'strstrdict',
    body:'bytes',
    store:'MessageStore',
    clock:'Clock',
    ) -> 'InboundResult':
    """ Receives one ebMS 2.0 message that arrived over HTTP and returns what is to be delivered and what is to be answered.
    The steps run in this order - packaging, envelope and header, binding resolution, the CanReceive check,
    time to live, signature, duplicate elimination, message order, delivery and the reply signals.
    """

    # Our response to produce
    out = InboundResult()

    now = clock.now()

    # A message whose MessageHeader cannot be read is answered with a SOAP Fault ..
    try:
        envelope, header, payloads = read_message(headers, body)
    except B2BProtocolException as e:
        _build_fault(out, e)
        return out

    out.header = header

    ctx = _Context()
    ctx.agreement = agreement
    ctx.local_keys = local_keys
    ctx.store = store
    ctx.now = now
    ctx.content_type = _content_type(headers)
    ctx.body = body
    ctx.header = header
    ctx.payloads = payloads

    # .. and any other message that cannot be processed is answered with an error message,
    # unless it is an error message that reports errors itself.
    try:
        elements = collect_elements(envelope)
        ctx.elements = elements

        _check_agreement(ctx)

        if header.service == MSHService.Service:
            _receive_msh(ctx, elements, out)
        else:
            _receive_business(ctx, elements, out)

    except B2BProtocolException as e:
        out.deliveries = []
        out.response = HTTPResponse()
        out.async_signal = None

        if _reports_error(ctx):
            _reject_unanswered(out, e)
        else:
            _reject(ctx, out, e)

    return out

# ################################################################################################################################

def _content_type(headers:'strstrdict') -> 'str':
    """ Returns the Content-Type of a message, whatever the case of the header name.
    """
    for name, value in headers.items():
        if name.lower() == 'content-type':
            out = value
            break
    else:
        out = ''

    return out

# ################################################################################################################################
# ################################################################################################################################
