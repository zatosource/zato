# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from datetime import timedelta

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome
from zato.common.b2b.common.commit_ticket import TransactionResult
from zato.common.b2b.common.commit_sql import write_events
from zato.common.b2b.common.exceptions import B2BException
from zato.common.b2b.common.receive_log import read_received
from zato.common.b2b.common.recovery import RecoveredPage
from zato.common.b2b.common.sequence import discard_held, earliest_held, gap_conversations, get_next_sequence, \
    held_messages, open_delivery, set_reported, take_held
from zato.common.b2b.ebms2.common import Max_Sequence_Number
from zato.common.b2b.ebms2.reliability import release_following

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Connection
    from zato.common.b2b.common.receive_log import ReceiveLog, ReceivedMessage, received_message_list
    from zato.common.b2b.common.sequence import HeldRow
    from zato.common.typing_ import intlist, stranydict
    Connection = Connection
    datetime = datetime
    HeldRow = HeldRow
    intlist = intlist
    ReceivedMessage = ReceivedMessage
    ReceiveLog = ReceiveLog
    received_message_list = received_message_list
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

gap_list = list['Gap']

# The environment variable with the time, in seconds, that a gap is given beyond the retries of its sender.
Env_Gap_Grace_Seconds = 'Zato_B2B_Gap_Grace_Seconds'

# The default of the time given to a gap beyond the retries of its sender, in seconds.
Default_Gap_Grace_Seconds = 300

# How many sequence numbers there are before the numbering restarts from zero.
_sequence_modulus = Max_Sequence_Number + 1

# ################################################################################################################################
# ################################################################################################################################

class _Gap_Data:
    """ The keys of the data document of the events of a sequence gap.
    """
    Conversation = 'conversation'
    Expected     = 'expected_sequence_number'
    First_Held   = 'first_held_sequence_number'
    Held_Count   = 'held_count'
    Deadline     = 'deadline'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Gap:
    """ A sequence gap of an ordered conversation - when it times out, and whether its timeout was reported.
    """
    conversation: str
    deadline:     'datetime'
    is_reported:  bool

# ################################################################################################################################
# ################################################################################################################################

def get_gap_grace() -> 'timedelta':
    """ Returns how long a gap is given beyond the retries of the sender before it times out.
    """
    if value := os.environ.get(Env_Gap_Grace_Seconds, ''):
        seconds = int(value)
    else:
        seconds = Default_Gap_Grace_Seconds

    out = timedelta(seconds=seconds)
    return out

# ################################################################################################################################

def gap_deadline(first_held:'HeldRow', grace:'timedelta') -> 'datetime':
    """ Returns when a gap times out - the time its first held message was held, plus the time the sender keeps
    sending the missing messages, plus the grace.
    """
    retry_window = timedelta(milliseconds=first_held.retry_window_ms)

    out = first_held.held_at + retry_window + grace
    return out

# ################################################################################################################################

def _expected(connection:'Connection', conversation:'str') -> 'int':
    """ Returns the sequence number a conversation expects next, which is zero for one that has not delivered any.
    """
    if (out := get_next_sequence(connection, conversation)) is None:
        out = 0

    return out

# ################################################################################################################################

@dataclass(init=False)
class _GapState:
    """ Where the sequence of a conversation with a gap stands - the number it expects next, its held messages,
    and the held message nearest after the expected number.
    """
    conversation: str
    expected:     int
    held:         'list[HeldRow]'
    nearest:      'HeldRow'

    def data(self) -> 'stranydict':
        """ Returns the data document of an event of the gap.
        """
        out:'stranydict' = {
            _Gap_Data.Conversation: self.conversation,
            _Gap_Data.Expected: self.expected,
            _Gap_Data.First_Held: self.nearest.sequence_number,
            _Gap_Data.Held_Count: len(self.held),
        }

        return out

# ################################################################################################################################

def _gap_state(connection:'Connection', conversation:'str') -> '_GapState':
    """ Returns where the sequence of a conversation with a gap stands.
    """
    out = _GapState()
    out.conversation = conversation
    out.expected = _expected(connection, conversation)
    out.held = held_messages(connection, conversation)
    out.nearest = _nearest_held(out.held, out.expected)

    return out

# ################################################################################################################################

def _nearest_held(held:'list[HeldRow]', expected:'int') -> 'HeldRow':
    """ Returns the held message that is the nearest after the expected number, counting across the restart from zero.
    """
    out = held[0]
    out_distance = (out.sequence_number - expected) % _sequence_modulus

    for row in held:
        distance = (row.sequence_number - expected) % _sequence_modulus
        if distance < out_distance:
            out = row
            out_distance = distance

    return out

# ################################################################################################################################

def _require_first_held(connection:'Connection', conversation:'str') -> 'HeldRow':
    """ Returns the held message that opened the gap of a conversation, which is to have one.
    """
    if (out := earliest_held(connection, conversation)) is None:
        raise B2BException(f'Conversation `{conversation}` has no held messages')

    return out

# ################################################################################################################################

def _gap_event_message(connection:'Connection', first_held:'HeldRow') -> 'ReceivedMessage':
    """ Returns the received message whose identity the events of a gap carry, which is the one that opened the gap.
    """
    received = read_received(connection, [first_held.event_id])

    out = received[first_held.event_id]
    return out

# ################################################################################################################################
# ################################################################################################################################

def _read_gaps(connection:'Connection', after:'str', limit:'int', grace:'timedelta') -> 'gap_list':

    out:'gap_list' = []

    for conversation in gap_conversations(connection, after, limit):
        first_held = _require_first_held(connection, conversation)

        gap = Gap()
        gap.conversation = conversation
        gap.deadline = gap_deadline(first_held, grace)
        gap.is_reported = first_held.reported_at is not None

        out.append(gap)

    return out

# ################################################################################################################################

def read_gaps(receive_log:'ReceiveLog', limit:'int', after:'str'='') -> 'gap_list':
    """ Returns, up to the limit, the sequence gaps of the conversations that hold messages, in the order
    of the conversations, starting after the given one. Each deadline is computed from the time the first message
    of its gap was held, which keeps it the same across a restart.
    """
    grace = get_gap_grace()

    with receive_log.writer.engine.connect() as connection:
        out = _read_gaps(connection, after, limit, grace)

    return out

# ################################################################################################################################

def read_gap_page(receive_log:'ReceiveLog', limit:'int', after:'str'='') -> 'RecoveredPage':
    """ Returns one page of the sequence gaps, whose cursor is the last conversation of the page.
    """
    gaps = read_gaps(receive_log, limit, after)

    out = RecoveredPage()
    out.items = gaps
    out.is_last = len(gaps) < limit

    if gaps:
        out.last_id = gaps[-1].conversation
    else:
        out.last_id = after

    return out

# ################################################################################################################################
# ################################################################################################################################

def _report_timed_out(
    connection:'Connection',
    commit_id:'str',
    receive_log:'ReceiveLog',
    conversation:'str',
    now:'datetime',
    ) -> 'TransactionResult':

    out = TransactionResult()
    out.value = False

    # A gap that was closed in the meantime has nothing to report ..
    if not (first_held := earliest_held(connection, conversation)):
        return out

    # .. and neither has one reported already or one whose deadline has not passed.
    if first_held.reported_at is not None:
        return out

    grace = get_gap_grace()
    deadline = gap_deadline(first_held, grace)

    if deadline > now:
        return out

    message = _gap_event_message(connection, first_held)
    state = _gap_state(connection, conversation)

    data = state.data()
    data[_Gap_Data.Deadline] = deadline.isoformat()

    event = receive_log.new_event(AuditEvent.Sequence_Gap_Timed_Out, message.identity, message.cpa_id, data,
        AuditOutcome.Error)

    _ = write_events(connection, [event], commit_id)
    set_reported(connection, first_held.id, now)

    out.value = True
    out.event_writes.append(event)

    return out

# ################################################################################################################################

def report_timed_out(receive_log:'ReceiveLog', conversation:'str', now:'datetime') -> 'bool':
    """ Records the timeout of the sequence gap of a conversation once its deadline has passed, and returns True
    if it was recorded now. A gap is reported once, whatever the number of calls.
    """
    out = receive_log.writer.run_transaction(_report_timed_out, receive_log, conversation, now)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _release_gap(
    connection:'Connection',
    commit_id:'str',
    receive_log:'ReceiveLog',
    conversation:'str',
    ) -> 'TransactionResult':

    first_held = _require_first_held(connection, conversation)
    message = _gap_event_message(connection, first_held)

    state = _gap_state(connection, conversation)
    data = state.data()
    nearest = state.nearest

    # The delivery skips the missing numbers and starts from the nearest held message ..
    _ = take_held(connection, conversation, nearest.sequence_number)
    open_delivery(connection, receive_log.source, receive_log.server_name, nearest.message_id, nearest.event_id)

    # .. and goes on with every held message that directly follows it.
    following = release_following(connection, receive_log, conversation, nearest.sequence_number)

    event_ids:'intlist' = [nearest.event_id]
    event_ids.extend(following)

    event = receive_log.new_event(AuditEvent.Sequence_Gap_Released, message.identity, message.cpa_id, data)
    _ = write_events(connection, [event], commit_id)

    released = read_received(connection, event_ids)

    value:'received_message_list' = []

    for event_id in event_ids:
        value.append(released[event_id])

    out = TransactionResult()
    out.value = value
    out.event_writes.append(event)

    return out

# ################################################################################################################################

def release_gap(receive_log:'ReceiveLog', conversation:'str') -> 'received_message_list':
    """ Gives up waiting for the missing messages of a conversation. The held messages are delivered from the nearest
    one after the number expected next, up to the next missing number, which the conversation expects from then on.
    Returns the released messages in their order, each with its delivery record open.
    """
    out = receive_log.writer.run_transaction(_release_gap, receive_log, conversation)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _discard_conversation(
    connection:'Connection',
    commit_id:'str',
    receive_log:'ReceiveLog',
    conversation:'str',
    ) -> 'TransactionResult':

    first_held = _require_first_held(connection, conversation)
    message = _gap_event_message(connection, first_held)

    state = _gap_state(connection, conversation)
    data = state.data()

    event = receive_log.new_event(AuditEvent.Conversation_Discarded, message.identity, message.cpa_id, data)
    _ = write_events(connection, [event], commit_id)

    out = TransactionResult()
    out.value = discard_held(connection, conversation)
    out.event_writes.append(event)

    return out

# ################################################################################################################################

def discard_conversation(receive_log:'ReceiveLog', conversation:'str') -> 'int':
    """ Deletes the held messages and the sequence state of a conversation, which starts over from zero,
    and returns how many messages were held.
    """
    out = receive_log.writer.run_transaction(_discard_conversation, receive_log, conversation)
    return out

# ################################################################################################################################
# ################################################################################################################################
