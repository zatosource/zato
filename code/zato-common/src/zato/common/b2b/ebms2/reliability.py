# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import timedelta

# Zato
from zato.common.b2b.common.store import MessageIdentity
from zato.common.b2b.ebms2.common import Default, EbMS2Exception, ErrorCode, Max_Sequence_Number, MessageOrderSemantics, \
    PerMessage, Protocol_Name, SequenceStatus
from zato.common.b2b.ebms2.xml_ import location

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.common.store import HeldMessage, MessageStore
    from zato.common.b2b.ebms2.agreement import Binding
    from zato.common.b2b.ebms2.header import MessageHeader, MessageOrder
    Binding = Binding
    HeldMessage = HeldMessage
    MessageHeader = MessageHeader
    MessageOrder = MessageOrder
    MessageStore = MessageStore

# ################################################################################################################################
# ################################################################################################################################

# How many sequence numbers there are before the numbering restarts from zero.
_sequence_modulus = Max_Sequence_Number + 1

# A sequence number less than half of the numbering ahead of the expected one is ahead of it,
# anything else is behind it, which is what lets the comparison work across the restart from zero.
_sequence_half = _sequence_modulus // 2

_message_order_location = location('MessageOrder')

# ################################################################################################################################
# ################################################################################################################################

class OrderAction:
    """ What happens to a message of an ordered conversation.
    """
    Deliver = 'deliver'
    Hold    = 'hold'
    Skip    = 'skip'

# ################################################################################################################################

held_message_list = list['HeldMessage']

@dataclass(init=False)
class OrderDecision:
    """ Whether a message of an ordered conversation is delivered now, and which held messages it releases.
    """
    action:   str
    released: 'held_message_list'

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

def decide_order(
    store:'MessageStore',
    key:'str',
    message_order:'MessageOrder | None',
    held:'HeldMessage',
    ) -> 'OrderDecision':
    """ Decides whether a message of an ordered conversation is delivered now, held until the messages before it
    arrive, or skipped as one delivered already. A delivered message releases the held ones that follow it.
    """

    # Our response to produce
    out = OrderDecision()

    if message_order is None:
        raise EbMS2Exception(ErrorCode.Inconsistent, 'The agreement guarantees message order and MessageOrder is missing',
            _message_order_location)

    sequence_number = message_order.sequence_number

    # A reset starts the conversation over from the number it carries ..
    if message_order.status == SequenceStatus.Reset:
        expected = sequence_number

    # .. and a conversation with no state yet starts from zero.
    elif (expected := store.get_next_sequence(key)) is None:
        expected = 0

    distance = (sequence_number - expected) % _sequence_modulus

    if distance == 0:
        out.action = OrderAction.Deliver

    elif distance < _sequence_half:
        out.action = OrderAction.Hold
        store.hold(key, sequence_number, held)

    else:
        out.action = OrderAction.Skip

    # A delivered message lets through every held one that directly follows it.
    if out.action == OrderAction.Deliver:

        following = next_sequence_number(sequence_number)

        while released := store.release(key, following):
            out.released.append(released)
            following = next_sequence_number(following)

        store.set_next_sequence(key, following)

    return out

# ################################################################################################################################
# ################################################################################################################################
