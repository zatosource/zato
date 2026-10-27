# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import timedelta

# lxml
from lxml.etree import Element, SubElement, tostring

# Zato
from zato.common.b2b.common.business_log import BusinessMessage, BusinessState, can_change, new_business_outcome, time_out
from zato.common.b2b.common.exceptions import B2BException
from zato.common.b2b.ebms2.common import Direction, NS
from zato.common.b2b.ebms2.cpa.xml_ import parse_duration_text
from zato.common.b2b.ebms2.outbound import build, SendOptions
from zato.common.b2b.ebms2.packaging import Payload
from zato.common.util.xml_.core import parse_xml, qname, to_timestamp, XMLException

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.b2b.common.business_log import BusinessLog, BusinessOutcome
    from zato.common.b2b.common.clock import Clock
    from zato.common.b2b.common.keys import LocalKeys
    from zato.common.b2b.ebms2.agreement import Agreement, Binding
    from zato.common.b2b.ebms2.common import party_id_list
    from zato.common.b2b.ebms2.header import MessageHeader
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    from zato.common.b2b.ebms2.packaging import payload_list
    from zato.common.typing_ import any_, dtnone, strlist
    Agreement = Agreement
    any_ = any_
    Binding = Binding
    BusinessLog = BusinessLog
    BusinessOutcome = BusinessOutcome
    Clock = Clock
    datetime = datetime
    dtnone = dtnone
    LocalKeys = LocalKeys
    MessageHeader = MessageHeader
    OutboundMessage = OutboundMessage
    party_id_list = party_id_list
    payload_list = payload_list
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class BusinessSignal:
    """ The actions of the business signals of ebBP 2.0 that a party sends about a business message it received.
    Under CPPA 2.0 section 8.4.12.1, a business signal sent on its own is a message of the service of the message
    it refers to, with an action of its own, bound by the CanSend and CanReceive elements of that action.
    """
    Receipt_Acknowledgement              = 'ReceiptAcknowledgement'
    Receipt_Acknowledgement_Exception    = 'ReceiptAcknowledgementException'
    Acceptance_Acknowledgement_Exception = 'AcceptanceAcknowledgementException'

# ################################################################################################################################

class ReceiptExceptionType:
    """ The values of ReceiptException in an ebBP 2.0 Exception signal.
    """
    Syntax        = 'Syntax'
    Authorization = 'Authorization'
    Signature     = 'Signature'
    Sequence      = 'Sequence'

# ################################################################################################################################

class AcceptanceExceptionType:
    """ The values of AcceptanceException in an ebBP 2.0 Exception signal.
    """
    Business    = 'Business'
    Performance = 'Performance'

# ################################################################################################################################

class TransactionCharacteristic:
    """ The attributes of BusinessTransactionCharacteristics that the deadlines of a business transaction are read from.
    """
    Time_To_Acknowledge_Receipt = 'timeToAcknowledgeReceipt'
    Time_To_Perform             = 'timeToPerform'

# ################################################################################################################################
# ################################################################################################################################

# The Content-Type of the document of a business signal.
Signal_Content_Type = 'application/xml'

# The root element of the ebBP 2.0 document of each signal.
_signal_roots = {
    BusinessSignal.Receipt_Acknowledgement:              'ReceiptAcknowledgement',
    BusinessSignal.Receipt_Acknowledgement_Exception:    'Exception',
    BusinessSignal.Acceptance_Acknowledgement_Exception: 'Exception',
}

# The ExceptionType child of each exception signal, with the value it has when the caller does not name one.
_exception_types = {
    BusinessSignal.Receipt_Acknowledgement_Exception:    ('ReceiptException', ReceiptExceptionType.Syntax),
    BusinessSignal.Acceptance_Acknowledgement_Exception: ('AcceptanceException', AcceptanceExceptionType.Business),
}

# The state each signal moves the business transaction of the message it refers to into.
_signal_states = {
    BusinessSignal.Receipt_Acknowledgement:              BusinessState.Receipted,
    BusinessSignal.Receipt_Acknowledgement_Exception:    BusinessState.Receipt_Refused,
    BusinessSignal.Acceptance_Acknowledgement_Exception: BusinessState.Acceptance_Refused,
}

_nsmap = {
    'bpssignal': NS.EBBP_Signals,
}

_exception_tag = qname(NS.EBBP_Signals, 'Exception')
_reason_tag = qname(NS.EBBP_Signals, 'Reason')
_exception_message_tag = qname(NS.EBBP_Signals, 'ExceptionMessage')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BusinessDeadlines:
    """ By when the receipt signal and the response to a business message are to arrive, None for a deadline
    that does not apply.
    """
    receipt:  'dtnone' = None
    response: 'dtnone' = None

# ################################################################################################################################
# ################################################################################################################################

def _add(parent:'any_', name:'str', text:'str') -> 'any_':
    child_tag = qname(NS.EBBP_Signals, name)

    out = SubElement(parent, child_tag)
    out.text = text

    return out

# ################################################################################################################################

def _add_party_info(parent:'any_', name:'str', party_ids:'party_id_list') -> 'None':
    party_id = party_ids[0]
    element = _add(parent, name, party_id.value)

    if party_id.id_type:
        element.set('type', party_id.id_type)

# ################################################################################################################################

def new_ebbp_signal(
    kind:'str',
    original_header:'MessageHeader',
    now:'datetime',
    errors:'strlist',
    exception_type:'str'='',
    ) -> 'bytes':
    """ Returns the ebBP 2.0 document of a business signal about a received message. The first error is the Reason
    of an exception signal and any further ones are the lines of its ExceptionMessage.
    """
    root_name = _signal_roots[kind]
    root_tag = qname(NS.EBBP_Signals, root_name)

    original_data = original_header.message_data
    original_timestamp = to_timestamp(original_data.timestamp)
    this_timestamp = to_timestamp(now)

    root = Element(root_tag, nsmap=_nsmap)

    # The signal goes from the receiver of the original message back to its sender.
    _ = _add(root, 'OriginalMessageIdentifier', original_data.message_id)
    _ = _add(root, 'OriginalMessageDateTime', original_timestamp)
    _ = _add(root, 'ThisMessageDateTime', this_timestamp)
    _add_party_info(root, 'FromPartyInfo', original_header.to_party.party_ids)
    _add_party_info(root, 'ToPartyInfo', original_header.from_party.party_ids)
    _ = _add(root, 'CollaborationIdentifier', original_header.conversation_id)
    _ = _add(root, 'BusinessActivityIdentifier', original_header.action)

    if exception := _exception_types.get(kind):

        if not errors:
            raise B2BException(f'Signal `{kind}` requires at least one error description')

        type_name, default_type = exception

        if not exception_type:
            exception_type = default_type

        exception_type_element = _add(root, 'ExceptionType', '')
        _ = _add(exception_type_element, type_name, exception_type)

        reason = errors[0]
        further_errors = errors[1:]

        _ = _add(root, 'Reason', reason)

        if further_errors:
            exception_message = '\n'.join(further_errors)
            _ = _add(root, 'ExceptionMessage', exception_message)

    out = tostring(root, xml_declaration=True, encoding='UTF-8')
    return out

# ################################################################################################################################

def signal_errors(payloads:'payload_list') -> 'strlist':
    """ Returns the error descriptions of an exception signal whose document is in the ebBP 2.0 format - the Reason
    followed by each line of the ExceptionMessage. A document in any other format has no error descriptions.
    """

    # Our response to produce
    out:'strlist' = []

    if not payloads:
        return out

    document = payloads[0]

    # A document that is not XML is not in the ebBP 2.0 format.
    try:
        root = parse_xml(document.data)
    except XMLException:
        return out

    if root.tag != _exception_tag:
        return out

    if (reason := root.find(_reason_tag)) is not None:
        out.append(reason.text)

    if (exception_message := root.find(_exception_message_tag)) is not None:
        lines = exception_message.text.splitlines()
        out.extend(lines)

    return out

# ################################################################################################################################
# ################################################################################################################################

def build_signal(
    agreement:'Agreement',
    local_keys:'LocalKeys',
    received_header:'MessageHeader',
    kind:'str',
    document:'bytes',
    clock:'Clock',
    ) -> 'OutboundMessage':
    """ Builds a business signal about a received business message. It is a message of the original service,
    under the action of the signal, from the receiver of the original message back to its sender, in the original
    conversation and with a RefToMessageId of the original message. It is sent, acknowledged and resent
    as any other business message.
    """
    binding = agreement.resolve(
        received_header.to_party.party_ids,
        received_header.from_party.party_ids,
        received_header.service,
        received_header.service_type,
        kind,
        Direction.Send,
    )

    payload = Payload()
    payload.content_id = ''
    payload.content_type = Signal_Content_Type
    payload.data = document

    options = SendOptions()
    options.conversation_id = received_header.conversation_id
    options.ref_to_message_id = received_header.message_data.message_id

    out = build(agreement, local_keys, binding, [payload], clock, options)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _deadline(binding:'Binding', name:'str', sent_at:'datetime') -> 'dtnone':
    """ Returns the moment a duration of the transaction characteristics of a binding ends, counted from when
    the message was sent, or None when the duration is absent or zero.
    """
    send_binding = binding.send_binding

    if send_binding is None:
        raise B2BException(f'Action `{binding.action}` has no business transaction characteristics')

    if text := send_binding.characteristics.get(name):
        duration = parse_duration_text(text, name)
        period = duration.value
    else:
        period = timedelta()

    if period:
        out = sent_at + period
    else:
        out = None

    return out

# ################################################################################################################################

def business_deadlines(binding:'Binding', sent_at:'datetime') -> 'BusinessDeadlines':
    """ Returns by when the receipt signal and the response to a business message sent under a binding are to arrive,
    from timeToAcknowledgeReceipt and timeToPerform of its transaction characteristics.
    """
    out = BusinessDeadlines()
    out.receipt = _deadline(binding, TransactionCharacteristic.Time_To_Acknowledge_Receipt, sent_at)
    out.response = _deadline(binding, TransactionCharacteristic.Time_To_Perform, sent_at)

    return out

# ################################################################################################################################

def new_business_message(outbound:'OutboundMessage') -> 'BusinessMessage':
    """ Returns how a business message that was built is recorded in a business log, with the deadlines
    of its business transaction counted from its timestamp.
    """
    binding = outbound.binding
    header = outbound.header
    sent_at = header.message_data.timestamp

    deadlines = business_deadlines(binding, sent_at)

    out = BusinessMessage()
    out.message_id = outbound.message_id
    out.cpa_id = header.cpa_id
    out.conversation_id = header.conversation_id
    out.from_party = binding.from_party.party_name
    out.to_party = binding.to_party.party_name
    out.service = header.service
    out.action = header.action
    out.sent_at = sent_at
    out.receipt_deadline = deadlines.receipt
    out.response_deadline = deadlines.response

    return out

# ################################################################################################################################
# ################################################################################################################################

def accept_business_message(
    business_log:'BusinessLog',
    header:'MessageHeader',
    payloads:'payload_list',
    clock:'Clock',
    ) -> 'BusinessOutcome | None':
    """ Matches a received business message against the business messages sent earlier. A business signal moves
    the transaction of the message it refers to into the state of the signal, and any other message that refers
    to a message sent earlier is its response. Returns where the transaction stands, or None when the message
    refers to no message in the log.
    """
    if not (ref_to_message_id := header.message_data.ref_to_message_id):
        return None

    if not (message := business_log.read(ref_to_message_id)):
        return None

    # A signal or a response that arrives after its deadline does not change a transaction that is already over ..
    now = clock.now()

    if message.is_past_deadline(now):
        out = time_out(business_log, message)
        return out

    # .. while one that arrives in time moves it on, unless the transaction is already past that point.
    if not (state := _signal_states.get(header.action)):
        state = BusinessState.Answered

    if can_change(message.state, state):

        reply_message_id = header.message_data.message_id

        if header.action in _exception_types:
            errors = signal_errors(payloads)
        else:
            errors = []

        business_log.record_reply(message, state, reply_message_id, errors)

        message.state = state
        message.reply_message_id = reply_message_id
        message.errors = errors

    out = new_business_outcome(message)
    return out

# ################################################################################################################################
# ################################################################################################################################
