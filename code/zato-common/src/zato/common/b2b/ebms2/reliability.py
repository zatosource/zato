# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import timedelta

# Zato
from zato.common.audit_log.common import AuditEvent
from zato.common.b2b.common.commit_ticket import TransactionResult
from zato.common.b2b.common.commit_sql import write_claims, write_events
from zato.common.b2b.common.receive_log import read_received
from zato.common.b2b.common.retry import RetryPolicy
from zato.common.b2b.common.schema import OpenKind
from zato.common.b2b.common.sequence import get_next_sequence, hold, HeldRow, is_held, open_delivery, set_next_sequence, \
    take_held
from zato.common.b2b.common.store import MessageIdentity
from zato.common.b2b.ebms2.common import Default, EbMS2Exception, ErrorCode, Max_Sequence_Number, MessageOrderSemantics, \
    PerMessage, Protocol_Name, SequenceStatus
from zato.common.b2b.ebms2.xml_ import location

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.b2b.common.commit_sql import ClaimWrite, EventWrite
    from zato.common.b2b.common.receive_log import ReceiveLog, received_message_list
    from zato.common.b2b.ebms2.agreement import Binding
    from zato.common.b2b.ebms2.header import MessageHeader, MessageOrder
    from zato.common.typing_ import intlist
    Binding = Binding
    ClaimWrite = ClaimWrite
    Connection = Connection
    EventWrite = EventWrite
    intlist = intlist
    MessageHeader = MessageHeader
    MessageOrder = MessageOrder
    ReceiveLog = ReceiveLog
    received_message_list = received_message_list

# ################################################################################################################################
# ################################################################################################################################

# How many sequence numbers there are before the numbering restarts from zero.
_sequence_modulus = Max_Sequence_Number + 1

# A sequence number less than half of the numbering ahead of the expected one is ahead of it,
# anything else is behind it, which is what lets the comparison work across the restart from zero.
_sequence_half = _sequence_modulus // 2

_message_order_location = location('MessageOrder')

_one_ms = timedelta(milliseconds=1)

# ################################################################################################################################
# ################################################################################################################################

class OrderAction:
    """ What happens to a message of an ordered conversation.
    """
    Deliver   = 'deliver'
    Hold      = 'hold'
    Skip      = 'skip'
    Duplicate = 'duplicate'

# ################################################################################################################################

class _Held_Data:
    """ The keys of the data document of the event that records a held message.
    """
    Conversation_ID = 'conversation_id'
    Expected        = 'expected_sequence_number'
    Received        = 'received_sequence_number'

# ################################################################################################################################

@dataclass(init=False)
class OrderedClaim:
    """ What ordering a received message requires - its conversation, the event that records its receipt,
    its MessageOrder, and how long its sender keeps sending a message that is not acknowledged.
    """
    key:             str
    cpa_id:          str
    conversation_id: str
    message_order:   'MessageOrder'
    received_event:  'EventWrite'
    retry_window:    'timedelta'

# ################################################################################################################################

@dataclass(init=False)
class OrderDecision:
    """ Whether a message of an ordered conversation is delivered now, and which held messages it releases.
    """
    action:   str
    released: 'received_message_list'

    def __init__(self) -> 'None':
        self.released = []

# ################################################################################################################################
# ################################################################################################################################

def message_identity(binding:'Binding', header:'MessageHeader') -> 'MessageIdentity':
    """ Returns what identifies a received message in the message store.
    """
    out = MessageIdentity(Protocol_Name, binding.from_party.party_name, binding.to_party.party_name,
        header.message_data.message_id)

    return out

# ################################################################################################################################

def persist_duration(binding:'Binding') -> 'timedelta':
    """ Returns how long the receiver of a binding remembers a received message for duplicate elimination.
    """
    if receiver_binding := binding.receiver_binding:
        if duration := receiver_binding.persist_duration:
            out = duration.value
        else:
            out = timedelta(seconds=Default.Persist_Duration_Seconds)
    else:
        out = timedelta(seconds=Default.Persist_Duration_Seconds)

    return out

# ################################################################################################################################

def per_message(setting:'str', message_says:'bool') -> 'bool':
    """ Resolves an always, never or perMessage characteristic for one message.
    """
    if setting == PerMessage.Always:
        out = True

    elif setting == PerMessage.Never:
        out = False

    else:
        out = message_says

    return out

# ################################################################################################################################

def retry_policy(binding:'Binding') -> 'RetryPolicy':
    """ Returns how often and how frequently the sender of a binding sends again a message that is not acknowledged.
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

def retry_window(binding:'Binding') -> 'timedelta':
    """ Returns how long the sender of a binding keeps sending a message that is not acknowledged.
    """
    policy = retry_policy(binding)

    out = policy.retry_interval * policy.retries
    return out

# ################################################################################################################################

def is_duplicate_elimination(binding:'Binding', header:'MessageHeader') -> 'bool':
    """ Says whether duplicates of a received message are eliminated.
    """
    setting = binding.characteristics.duplicate_elimination

    out = per_message(setting, header.duplicate_elimination)
    return out

# ################################################################################################################################

def is_order_guaranteed(binding:'Binding') -> 'bool':
    """ Says whether the messages of a binding are delivered in the order they were sent.
    """

    # Our response to produce
    out = False

    for exchange_binding in (binding.sender_binding, binding.receiver_binding):
        if exchange_binding:
            if reliable := exchange_binding.reliable_messaging:
                if reliable.message_order == MessageOrderSemantics.Guaranteed:
                    out = True

    return out

# ################################################################################################################################

def conversation_key(binding:'Binding', header:'MessageHeader') -> 'str':
    """ Returns what the sequence state of an ordered conversation is kept under.
    """
    cpa_id = binding.agreement.cpa_id
    party_name = binding.from_party.party_name

    out = f'{cpa_id}/{party_name}/{header.conversation_id}'
    return out

# ################################################################################################################################

def next_sequence_number(sequence_number:'int') -> 'int':
    """ Returns the number that follows another one, restarting from zero after the highest one.
    """
    following = sequence_number + 1

    out = following % _sequence_modulus
    return out

# ################################################################################################################################

def order_action(expected:'int', sequence_number:'int') -> 'str':
    """ Decides whether a message of an ordered conversation is delivered now, held until the messages before it
    arrive, or skipped as one delivered already.
    """
    distance = (sequence_number - expected) % _sequence_modulus

    if distance == 0:
        out = OrderAction.Deliver

    elif distance < _sequence_half:
        out = OrderAction.Hold

    else:
        out = OrderAction.Skip

    return out

# ################################################################################################################################

def release_following(connection:'Connection', receive_log:'ReceiveLog', key:'str', sequence_number:'int') -> 'intlist':
    """ Releases every held message that directly follows a delivered one, opening its delivery record,
    advances the number expected next, and returns the events that recorded the receipt of the released messages.
    """
    out:'intlist' = []

    following = next_sequence_number(sequence_number)

    while held := take_held(connection, key, following):
        open_delivery(connection, receive_log.source, receive_log.server_name, held.message_id, held.event_id)
        out.append(held.event_id)
        following = next_sequence_number(following)

    set_next_sequence(connection, key, following)

    return out

# ################################################################################################################################

def _claim_ordered(
    connection:'Connection',
    commit_id:'str',
    receive_log:'ReceiveLog',
    claim:'ClaimWrite',
    order:'OrderedClaim',
    ) -> 'TransactionResult':
    """ Claims a message of an ordered conversation and decides its order in one transaction, so that a claimed message
    is always either delivered, held or skipped.
    """
    decision = OrderDecision()

    out = TransactionResult()
    out.value = decision

    # Duplicates of a message whose order is guaranteed are always eliminated.
    claim_results = write_claims(connection, [claim], commit_id)

    if not claim_results[0]:
        decision.action = OrderAction.Duplicate
        return out

    sequence_number = order.message_order.sequence_number

    # A reset starts the conversation over from the number it carries ..
    if order.message_order.status == SequenceStatus.Reset:
        expected = sequence_number

    # .. and a conversation with no state yet starts from zero.
    elif (expected := get_next_sequence(connection, order.key)) is None:
        expected = 0

    decision.action = order_action(expected, sequence_number)

    received = order.received_event
    out.event_writes.append(received)

    # A delivered message has its delivery record from the start ..
    if decision.action == OrderAction.Deliver:
        received.opens.append(OpenKind.Delivery)

    # .. while a held one is recorded as held, with where the sequence stands.
    elif decision.action == OrderAction.Hold:
        held_data = {
            _Held_Data.Conversation_ID: order.conversation_id,
            _Held_Data.Expected: expected,
            _Held_Data.Received: sequence_number,
        }
        held_event = receive_log.new_event(AuditEvent.Message_Held, claim.identity, order.cpa_id, held_data)
        out.event_writes.append(held_event)

    event_ids = write_events(connection, out.event_writes, commit_id)
    received_event_id = event_ids[0]

    if decision.action == OrderAction.Hold:

        # A message held already under the same number stays as it is.
        if not is_held(connection, order.key, sequence_number):
            held_row = HeldRow()
            held_row.conversation = order.key
            held_row.sequence_number = sequence_number
            held_row.message_id = claim.identity.message_id
            held_row.event_id = received_event_id
            held_row.held_at = claim.message.received_at
            held_row.retry_window_ms = order.retry_window // _one_ms
            hold(connection, held_row)

    # A delivered message lets through every held one that directly follows it.
    elif decision.action == OrderAction.Deliver:
        released_ids = release_following(connection, receive_log, order.key, sequence_number)
        released = read_received(connection, released_ids)

        for event_id in released_ids:
            decision.released.append(released[event_id])

    return out

# ################################################################################################################################

def require_message_order(message_order:'MessageOrder | None') -> 'MessageOrder':
    """ Returns the MessageOrder of a message whose agreement guarantees the order of delivery, which it is to have.
    """
    if message_order is None:
        raise EbMS2Exception(ErrorCode.Inconsistent, 'The agreement guarantees message order and MessageOrder is missing',
            _message_order_location)

    return message_order

# ################################################################################################################################

def claim_ordered(receive_log:'ReceiveLog', claim:'ClaimWrite', order:'OrderedClaim') -> 'OrderDecision':
    """ Claims a received message of an ordered conversation and decides whether it is delivered now, held until
    the messages before it arrive, or skipped as one delivered already, all in one transaction. A delivered message
    releases the held ones that follow it, and the delivery record of each is opened in the same transaction.
    """
    out = receive_log.writer.run_transaction(_claim_ordered, receive_log, claim, order)
    return out

# ################################################################################################################################
# ################################################################################################################################
