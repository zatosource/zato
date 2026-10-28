# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# pytest
import pytest

# Zato
from live_db import start_child, Type_MySQL, Type_PostgreSQL
from zato.common.b2b.common.clock import ManualClock
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.b2b.common.recovery import Recovery_Page_Size
from zato.common.b2b.common.scheduler import DeliveryScheduler, EntryKind, recover_pages
from zato.common.b2b.common.send_log import SendLog
from zato.common.test.b2b_write_path import Server, Source, Start_Time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_db import LiveDB
    from zato.common.b2b.common.send_log import SentMessage
    LiveDB = LiveDB
    SentMessage = SentMessage

# ################################################################################################################################
# ################################################################################################################################

# How long the writer of a test waits between two commits, in milliseconds.
_interval_ms = 10

# How many open exchanges the recovery reads, and how many of them the child records at a time.
_open_exchanges = 20_000
_seed_batch_size = 1000

# How long the child that records them is waited for, in seconds.
_seed_seconds = 600

# ################################################################################################################################
# ################################################################################################################################

class TestPagedRecovery:
    """ The open exchanges of a server are recovered page by page into the scheduler without blocking the event loop.
    """

    @pytest.mark.parametrize('database', [Type_MySQL, Type_PostgreSQL], indirect=True)
    def test_recover_into_scheduler(self, database:'LiveDB') -> 'None':

        # The exchanges are recorded by another process, outside of what the event loop monitor measures.
        child = start_child(database, 'seed-open', str(_open_exchanges), str(_seed_batch_size))
        stdout, stderr = child.communicate(timeout=_seed_seconds)

        assert child.returncode == 0, stderr

        report = json.loads(stdout.strip().splitlines()[-1])
        assert report['open'] == _open_exchanges

        writer = GroupCommitWriter(database.engine, interval_ms=_interval_ms)
        send_log = SendLog(Source, Server, ManualClock(Start_Time), writer)

        scheduler = DeliveryScheduler(ManualClock(Start_Time))

        def schedule(sent:'SentMessage') -> 'None':
            due_at = sent.retry_state.last_attempt_at + sent.policy.retry_interval
            scheduler.schedule(EntryKind.Delivery, sent.message_id, due_at)

        recovered = recover_pages(send_log.recover_page, schedule, Recovery_Page_Size, 0)

        assert recovered == _open_exchanges
        assert len(scheduler) == _open_exchanges
        assert len(send_log.outstanding(_open_exchanges)) == _open_exchanges

        writer.stop()

# ################################################################################################################################
# ################################################################################################################################
