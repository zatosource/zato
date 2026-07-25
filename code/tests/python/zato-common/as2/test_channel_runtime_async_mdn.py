# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from .channel_runtime_helpers import Async_MDN_URL, build_async_wire_message, cleanup_env, make_runtime, \
    Receiver_Identifier, Sender_Identifier
from zato.common.api import AS2
from zato.common.as2.async_mdn import AsyncMDNQueue
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestAsyncMDNQueueing:
    """ A receipt the sender asked to have delivered to a separate URL is persisted before the
    inbound POST is answered. Handing it straight to a greenlet loses it if the process stops
    between accepting the message and delivering the receipt, and the sender is then waiting
    for a receipt nobody will ever send.
    """

    def test_an_async_receipt_is_persisted_before_the_post_is_answered(
        self,
        parties:'TestParties',
        tmp_path:'os.PathLike',
    ) -> 'None':
        try:
            _, runtime = make_runtime(tmp_path, parties)

            body, headers, _, _ = build_async_wire_message(parties)
            result = runtime.handle('cid-1', body, headers)

            assert not result.is_error

            # The receipt did not ride on the response, it is in the queue instead.
            assert result.pending_async_mdn is not None

            queue = AsyncMDNQueue()
            now = utcnow()
            due = queue.due(now)

            due_count = len(due)
            assert due_count == 1

            item = due[0]

            assert item.url == Async_MDN_URL
            assert item.message_id == result.message_id
            assert item.as2_from == Sender_Identifier
            assert item.as2_to == Receiver_Identifier
            assert item.channel_name == AS2.Default.Channel_Name

            # The receipt bytes are the ones the peer is owed, which cannot be rebuilt later.
            assert item.body == result.pending_async_mdn.body

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_a_replay_does_not_queue_a_second_receipt(self, parties:'TestParties', tmp_path:'os.PathLike') -> 'None':
        try:
            _, runtime = make_runtime(tmp_path, parties)

            body, headers, _, _ = build_async_wire_message(parties)

            first = runtime.handle('cid-1', body, headers)
            second = runtime.handle('cid-2', body, headers)

            assert not first.is_duplicate
            assert second.is_duplicate

            # The receipt of the first delivery is the one the peer is owed, so the replay
            # must not put a second one in the queue.
            queue = AsyncMDNQueue()
            now = utcnow()
            due = queue.due(now)

            due_count = len(due)
            assert due_count == 1

        finally:
            cleanup_env()

# ################################################################################################################################
# ################################################################################################################################
