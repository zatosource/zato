# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from zato.common.b2b.portal.config import Local_Host
from zato.common.b2b.portal.sample.agreements import Agreements
from zato.common.b2b.portal.sample.common import minutes_ago, Tone
from zato.common.b2b.portal.sample.parties import Partner_By_Key, Service_By_Name
from zato.common.b2b.portal.sample.protocol.common import Business_Service, Vocabularies

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.b2b.portal.sample.parties import Partner, Service
    from zato.common.b2b.portal.sample.protocol.common import Vocabulary
    from zato.common.typing_ import anydict, anylist, anytuple, dictlist
    anylist = anylist
    anytuple = anytuple
    datetime = datetime
    dictlist = dictlist
    Partner = Partner
    Service = Service
    Vocabulary = Vocabulary

# ################################################################################################################################
# ################################################################################################################################

# The actions of the business signals
Receipt_Action         = 'ReceiptAcknowledgement'
Receipt_Refused_Action = 'ReceiptAcknowledgementException'
Acceptance_Refused     = 'AcceptanceAcknowledgementException'

class Kind:
    Document     = 'Business document'
    Response     = 'Business response'
    Notification = 'Notification'
    Signal       = 'Business signal'
    Ack          = 'Acknowledgment'
    Error        = 'Message error'

class Scenario:
    Answered           = 'answered'
    Pending            = 'pending'
    Receipt_Refused    = 'receipt-refused'
    Acceptance_Refused = 'acceptance-refused'
    Notify             = 'notify'
    Notify_Retrying    = 'notify-retrying'
    Notify_Failed      = 'notify-failed'
    Receipt_Overdue    = 'receipt-overdue'
    Duplicate          = 'duplicate'
    Signature_Failed   = 'signature-failed'

# How long after the previous message of a conversation each kind of message follows it, in seconds
_ack_delay      = 1
_receipt_delay  = 14
_response_delay = 52

# The retry interval of every agreement in the sample data, in minutes
_retry_minutes = 5

# ################################################################################################################################
# ################################################################################################################################

# Minutes ago, partner, product, service, scenario, the partner's order or complaint reference
_seeds = [
    (4,    'harborlight', 'Orders',     'SubmitOrderv2',              Scenario.Answered,           'HLW-PO-55102'),
    (11,   'redwood',     'Orders',     'SubmitOrderv2',              Scenario.Pending,            '88231'),
    (19,   'harborlight', 'Complaints', 'FileComplaintv2',            Scenario.Answered,           'HLW-CMP-20417'),
    (27,   'lakeshore',   'Orders',     'NotifyOfOrderStatusv2',      Scenario.Notify_Retrying,    'LKC-ORD-7712'),
    (38,   'redwood',     'Orders',     'CancelOrderv2',              Scenario.Acceptance_Refused, '88190'),
    (52,   'harborlight', 'Orders',     'NotifyOfOrderStatusv2',      Scenario.Notify,             'HLW-PO-55087'),
    (75,   'prairie',     'Orders',     'SubmitOrderv2',              Scenario.Signature_Failed,   '100421'),
    (96,   'harborlight', 'Orders',     'ChangeOrderv2',              Scenario.Duplicate,          'HLW-PO-55064'),
    (140,  'harborlight', 'Complaints', 'FileComplaintv2',            Scenario.Receipt_Refused,    'HLW-CMP-20398'),
    (260,  'redwood',     'Orders',     'NotifyOfOrderStatusv2',      Scenario.Notify_Failed,      '88102'),
    (410,  'lakeshore',   'Orders',     'SubmitOrderv2',              Scenario.Answered,           'LKC-ORD-7698'),
    (900,  'harborlight', 'Complaints', 'NotifyOfComplaintStatusv2',  Scenario.Receipt_Overdue,    'HLW-CMP-20366'),
    (1500, 'harborlight', 'Orders',     'QueryOrderDetailsv2',        Scenario.Answered,           'HLW-PO-54980'),
    (2900, 'lakeshore',   'Orders',     'ScheduleInstallationv2',     Scenario.Answered,           'LKC-ORD-7640'),
    (5200, 'redwood',     'Orders',     'SubmitOrderv2',              Scenario.Answered,           '87911'),
]

# ################################################################################################################################
# ################################################################################################################################

def _agreement_id(partner_key:'str', product:'str') -> 'str':

    for agreement in Agreements:
        if agreement.partner_key == partner_key:
            if agreement.product == product:
                out = agreement.agreement_id
                break
    else:
        raise Exception(f'No agreement for `{partner_key}` and `{product}`')

    return out

# ################################################################################################################################

def _message_id(prefix:'str', moment:'datetime', number:'int', host:'str') -> 'str':
    milliseconds = (number * 37) % 1000
    stamp = moment.strftime('%Y%m%d%H%M%S')
    serial = 4096 + number * 7919
    out = f'{prefix}{stamp}{milliseconds:03d}.{serial:x}@{host}'
    return out

# ################################################################################################################################
# ################################################################################################################################

class _Conversation:
    """ Builds the messages of one conversation in the order they were exchanged.
    """
    def __init__(self, index:'int', seed:'anytuple') -> 'None':

        started_minutes, partner_key, product, service_name, scenario, reference = seed

        self.index = index
        self.partner:'Partner' = Partner_By_Key[partner_key]
        self.service:'Service' = Service_By_Name[service_name]
        self.vocabulary:'Vocabulary' = Vocabularies[self.partner.protocol]
        self.agreement_id = _agreement_id(partner_key, product)
        self.scenario = scenario
        self.reference = reference
        self.moment = minutes_ago(started_minutes)
        self.messages:'dictlist' = []

        # A notification starts with us, everything else with the partner
        host = Local_Host if self.service.is_notification else self.partner.host
        self.conversation_id = _message_id('C', self.moment, index, host)

# ################################################################################################################################

    def add(
        self,
        *,
        delay:'int',
        is_inbound:'bool',
        action:'str',
        kind:'str',
        state:'str',
        ref_to:'str'='',
        is_business:'bool'=True,
        ) -> 'anydict':

        self.moment = self.moment + timedelta(seconds=delay)

        host = self.partner.host if is_inbound else Local_Host
        prefix = 'M' if is_inbound else 'G'
        number = self.index * 10 + len(self.messages)
        attempts:'anylist' = []

        # A business message names its own service ..
        if is_business:
            service = self.service.name

        # .. so does an AS2 MDN or an AS4 signal, which have no service of their own ..
        elif self.vocabulary.messaging_service == Business_Service:
            service = self.service.name

        # .. while a message of the ebXML messaging layer names the service of that layer.
        else:
            service = self.vocabulary.messaging_service

        out = {
            'id': _message_id(prefix, self.moment, number, host),
            'conversation_id': self.conversation_id,
            'moment': self.moment,
            'direction': 'Inbound' if is_inbound else 'Outbound',
            'partner_key': self.partner.key,
            'protocol': self.partner.protocol,
            'agreement_id': self.agreement_id,
            'service': service,
            'action': action,
            'ref_to': ref_to,
            'state': state,
            'kind': kind,
            'reference': self.reference,
            'attempts': attempts,
            'error_code': '',
            'error': '',
            'tip': '',
        }

        # An outbound message is delivered on the first attempt unless its scenario says otherwise
        if not is_inbound:
            attempts.append(_attempt(1, self.moment, 'HTTP 200', Tone.Green, ''))

        self.messages.append(out)
        return out

# ################################################################################################################################

    def ack(self, message:'anydict', state:'str'='') -> 'anydict':
        """ The acknowledgment of a message, sent by the side that received it - an ebXML Acknowledgment, an AS2 MDN
        or an AS4 Receipt.
        """
        is_inbound = message['direction'] == 'Outbound'
        if not state:
            state = 'Received' if is_inbound else 'Delivered'

        out = self.add(delay=_ack_delay, is_inbound=is_inbound, action=self.vocabulary.ack_action, kind=Kind.Ack,
            state=state, ref_to=message['id'], is_business=False)
        return out

# ################################################################################################################################

    def has_receipt_signal(self) -> 'bool':
        """ Whether the service asks for a receipt acknowledgement signal, which an AS2 MDN stands in for.
        """
        out = False

        if self.service.receipt_seconds:
            if self.vocabulary.has_business_signals:
                out = True

        return out

# ################################################################################################################################
# ################################################################################################################################

def _attempt(number:'int', moment:'datetime', outcome:'str', tone:'str', tip:'str') -> 'anydict':
    out = {'number': number, 'moment': moment, 'outcome': outcome, 'tone': tone, 'tip': tip}
    return out

# ################################################################################################################################

def _retries(message:'anydict', count:'int') -> 'None':
    """ Replaces the single successful attempt of an outbound message with failed ones, one per retry interval.
    """
    outcomes = [
        ('HTTP 503', 'Service Unavailable'),
        ('Timeout', 'No response within 30 seconds'),
        ('HTTP 503', 'Service Unavailable'),
        ('Connection refused', 'The endpoint refused the TCP connection'),
    ]

    message['attempts'] = []

    for index in range(count):
        moment = message['moment'] + timedelta(minutes=index * _retry_minutes)
        outcome, tip = outcomes[index]
        message['attempts'].append(_attempt(index + 1, moment, outcome, Tone.Red, tip))

# ################################################################################################################################

def _answered(conversation:'_Conversation') -> 'anydict':

    request = conversation.add(delay=0, is_inbound=True, action=conversation.service.request, kind=Kind.Document,
        state='Received')
    _ = conversation.ack(request)

    if conversation.has_receipt_signal():
        receipt = conversation.add(delay=_receipt_delay, is_inbound=False, action=Receipt_Action, kind=Kind.Signal,
            state='Delivered', ref_to=request['id'])
        _ = conversation.ack(receipt)

    response = conversation.add(delay=_response_delay, is_inbound=False, action=conversation.service.response,
        kind=Kind.Response, state='Delivered', ref_to=request['id'])
    _ = conversation.ack(response)

    out = {'state': 'Answered'}
    return out

# ################################################################################################################################

def _pending(conversation:'_Conversation') -> 'anydict':

    request = conversation.add(delay=0, is_inbound=True, action=conversation.service.request, kind=Kind.Document,
        state='Received')
    _ = conversation.ack(request)

    out = {'state': 'Acknowledged'}
    return out

# ################################################################################################################################

def _refused(conversation:'_Conversation', action:'str', code:'str', error:'str') -> 'anydict':

    request = conversation.add(delay=0, is_inbound=True, action=conversation.service.request, kind=Kind.Document,
        state='Refused')
    request['error_code'] = code
    request['error'] = error
    _ = conversation.ack(request)

    signal = conversation.add(delay=_receipt_delay, is_inbound=False, action=action, kind=Kind.Signal, state='Delivered',
        ref_to=request['id'])
    signal['error_code'] = code
    signal['error'] = error
    _ = conversation.ack(signal)

    out = {'state': 'Failed'}
    return out

# ################################################################################################################################

def _notify(conversation:'_Conversation') -> 'anydict':

    notification = conversation.add(delay=0, is_inbound=False, action=conversation.service.request, kind=Kind.Notification,
        state='Delivered')
    _ = conversation.ack(notification)

    if conversation.has_receipt_signal():
        receipt = conversation.add(delay=_receipt_delay, is_inbound=True, action=Receipt_Action, kind=Kind.Signal,
            state='Received', ref_to=notification['id'])
        _ = conversation.ack(receipt)

    out = {'state': 'Answered'}
    return out

# ################################################################################################################################

def _notify_undelivered(conversation:'_Conversation', is_final:'bool') -> 'anydict':

    state = 'Failed' if is_final else 'Retrying'

    notification = conversation.add(delay=0, is_inbound=False, action=conversation.service.request, kind=Kind.Notification,
        state=state)

    # The first attempt and three retries, or as many of them as have taken place so far
    count = 4 if is_final else 2
    _retries(notification, count)

    if is_final:
        notification['error_code'] = conversation.vocabulary.delivery_failure_code
        notification['error'] = f'No {conversation.vocabulary.ack_noun} after 3 retries at 5-minute intervals'
        out = {'state': 'Failed'}
    else:
        next_attempt = notification['moment'] + timedelta(minutes=count * _retry_minutes)
        tip = 'Retry 2 of 3 at ' + next_attempt.strftime('%H:%M:%S')
        notification['tip'] = tip
        out = {'state': 'Sent'}

    return out

# ################################################################################################################################

def _receipt_overdue(conversation:'_Conversation') -> 'anydict':

    notification = conversation.add(delay=0, is_inbound=False, action=conversation.service.request, kind=Kind.Notification,
        state='Delivered')
    notification['error_code'] = conversation.vocabulary.receipt_overdue_code
    notification['error'] = f'No {conversation.vocabulary.receipt_noun} within 5 minutes'
    _ = conversation.ack(notification)

    out = {'state': 'Failed'}
    return out

# ################################################################################################################################

def _duplicate(conversation:'_Conversation') -> 'anydict':

    out = _answered(conversation)

    # The partner resends the request after the acknowledgment did not reach it in time
    request = conversation.messages[0]
    copy = dict(request)
    copy['moment'] = request['moment'] + timedelta(seconds=31)
    copy['state'] = 'Duplicate'
    copy['attempts'] = []
    copy['error_code'] = conversation.vocabulary.duplicate_code
    copy['error'] = 'Identical to a message received at ' + request['moment'].strftime('%H:%M:%S')

    conversation.messages.insert(2, copy)
    return out

# ################################################################################################################################

def _signature_failed(conversation:'_Conversation') -> 'anydict':

    request = conversation.add(delay=0, is_inbound=True, action=conversation.service.request, kind=Kind.Document,
        state='Refused')
    request['error_code'] = conversation.vocabulary.security_failure_code
    request['error'] = 'The signature does not verify against the partner signing certificate'

    error = conversation.add(delay=_ack_delay, is_inbound=False, action=conversation.vocabulary.error_action, kind=Kind.Error,
        state='Delivered', ref_to=request['id'], is_business=False)
    error['error_code'] = request['error_code']
    error['error'] = request['error']

    out = {'state': 'Failed'}
    return out

# ################################################################################################################################
# ################################################################################################################################

def _build() -> 'dictlist':
    """ Builds the conversations of the sample data, most recent first.
    """
    out:'dictlist' = []

    for index, seed in enumerate(_seeds):

        conversation = _Conversation(index, seed)
        scenario = conversation.scenario

        if scenario == Scenario.Answered:
            result = _answered(conversation)

        elif scenario == Scenario.Pending:
            result = _pending(conversation)

        elif scenario == Scenario.Receipt_Refused:
            result = _refused(conversation, Receipt_Refused_Action, 'InvalidContent',
                'The complaint reference does not match an open complaint')

        elif scenario == Scenario.Acceptance_Refused:
            result = _refused(conversation, Acceptance_Refused, 'OrderNotCancellable',
                'The order has already been fulfilled')

        elif scenario == Scenario.Notify:
            result = _notify(conversation)

        elif scenario == Scenario.Notify_Retrying:
            result = _notify_undelivered(conversation, False)

        elif scenario == Scenario.Notify_Failed:
            result = _notify_undelivered(conversation, True)

        elif scenario == Scenario.Receipt_Overdue:
            result = _receipt_overdue(conversation)

        elif scenario == Scenario.Duplicate:
            result = _duplicate(conversation)

        elif scenario == Scenario.Signature_Failed:
            result = _signature_failed(conversation)

        # .. anything else is a seed with a scenario that has no builder.
        else:
            raise Exception(f'Unknown scenario `{scenario}`')

        out.append({
            'id': conversation.conversation_id,
            'partner_key': conversation.partner.key,
            'agreement_id': conversation.agreement_id,
            'service': conversation.service.name,
            'reference': conversation.reference,
            'state': result['state'],
            'messages': conversation.messages,
        })

    return out

# ################################################################################################################################

Conversations = _build()

Conversation_By_ID = {}

Messages:'dictlist' = []

for _conversation in Conversations:
    Conversation_By_ID[_conversation['id']] = _conversation
    for _message in _conversation['messages']:
        _message['key'] = f'{len(Messages) + 1:04d}'
        Messages.append(_message)

# ################################################################################################################################
# ################################################################################################################################
