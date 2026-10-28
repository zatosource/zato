# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from live_db import count_rows
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.b2b.common.outcome import FinalState
from zato.common.b2b.common.schema import held_message_table, sequence_table
from zato.common.b2b.common.store import MessageStore
from zato.common.b2b.ebms2.common import MessageOrderSemantics, SequenceStatus, SyncReplyMode
from zato.common.b2b.ebms2.inbound_common import new_receive_log, pending_deliveries
from zato.common.b2b.ebms2.outbound import SendOptions
from zato.common.b2b.ebms2.sequence_gap import Default_Gap_Grace_Seconds, discard_conversation, read_gaps, release_gap, \
    report_timed_out
from zato.common.test.b2b_cpa import new_settings
from zato.common.test.b2b_ebms2 import deliver, new_exchange, new_payload, send, Server_Name, Start_Time, use_store

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_db import LiveDB
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.test.b2b_pki import TestParties
    LiveDB = LiveDB
    Exchange = Exchange
    OutboundMessage = OutboundMessage
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# How long the writer of a test waits between two commits, in milliseconds.
_interval_ms = 10

_conversation_id = 'b2b-live-gap-conversation'

# The retries of the sender and their interval, which the agreement of the tests declares.
_retries = 3
_retry_interval_seconds = 30

# How long a gap waits, with the default grace, from the moment its first message was held.
_gap_seconds = _retries * _retry_interval_seconds + Default_Gap_Grace_Seconds

# How long after the first held message the second one is held, in seconds.
_second_hold_seconds = 60

# How many gaps one read returns at most, and how many deliveries one page of a recovery holds.
_gap_limit = 100
_page_size = 10

# ################################################################################################################################
# ################################################################################################################################

def _ordered(parties:'TestParties', writer:'GroupCommitWriter') -> 'Exchange':
    settings = new_settings(parties, Start_Time)
    settings.business_channel.sync_reply_mode = SyncReplyMode.MSH_Signals_Only
    settings.message_order = MessageOrderSemantics.Guaranteed
    settings.retries = _retries
    settings.retry_interval = f'PT{_retry_interval_seconds}S'

    out = new_exchange(parties, settings)
    use_store(out.receiver, MessageStore(writer))

    return out

# ################################################################################################################################

def _hold(exchange:'Exchange', sequence_number:'int') -> 'OutboundMessage':
    """ Delivers a message of an ordered conversation that the receiver holds, and returns it.
    """
    options = SendOptions()
    options.conversation_id = _conversation_id
    options.sequence_number = sequence_number
    options.sequence_status = SequenceStatus.Continue

    data = f'<Order><Id>{sequence_number}</Id></Order>'.encode('ascii')
    payload = new_payload(data)

    out = send(exchange, [payload], options)
    result = deliver(exchange, out)

    assert result.outcome.final_state == FinalState.Held

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSequenceGap:
    """ The deadline of a gap survives a restart, and an operator releases or discards a conversation.
    """

    def test_deadline_after_restart(self, database:'LiveDB', writer:'GroupCommitWriter', parties:'TestParties') -> 'None':
        exchange = _ordered(parties, writer)

        _ = _hold(exchange, 1)

        exchange.clock.advance(_second_hold_seconds)
        _ = _hold(exchange, 2)

        writer.stop()

        # Another process starts on the same database and computes the same deadline from the stored hold times.
        new_writer = GroupCommitWriter(database.engine, interval_ms=_interval_ms)
        receive_log = new_receive_log(MessageStore(new_writer), Server_Name)

        gaps = read_gaps(receive_log, _gap_limit)

        assert len(gaps) == 1

        gap = gaps[0]
        deadline = Start_Time + timedelta(seconds=_gap_seconds)

        assert gap.deadline == deadline
        assert not gap.is_reported

        assert report_timed_out(receive_log, gap.conversation, deadline)
        assert not report_timed_out(receive_log, gap.conversation, deadline)

        new_writer.stop()

    def test_release(self, database:'LiveDB', writer:'GroupCommitWriter', parties:'TestParties') -> 'None':
        exchange = _ordered(parties, writer)

        first = _hold(exchange, 1)
        second = _hold(exchange, 2)

        receive_log = exchange.receiver.receive_log
        gaps = read_gaps(receive_log, _gap_limit)

        _ = release_gap(receive_log, gaps[0].conversation)

        pending_ids:'list[str]' = []

        for delivery in pending_deliveries(receive_log, _page_size):
            pending_ids.append(delivery.message_id)

        assert pending_ids == [first.message_id, second.message_id]
        assert count_rows(database.engine, held_message_table) == 0

    def test_discard(self, database:'LiveDB', writer:'GroupCommitWriter', parties:'TestParties') -> 'None':
        exchange = _ordered(parties, writer)

        _ = _hold(exchange, 1)
        _ = _hold(exchange, 2)

        receive_log = exchange.receiver.receive_log
        gaps = read_gaps(receive_log, _gap_limit)

        assert discard_conversation(receive_log, gaps[0].conversation) == 2

        assert count_rows(database.engine, held_message_table) == 0
        assert count_rows(database.engine, sequence_table) == 0
        assert pending_deliveries(receive_log, _page_size) == []

# ################################################################################################################################
# ################################################################################################################################
