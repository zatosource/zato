# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# gevent
from gevent import sleep
from gevent.event import Event

# Zato
from zato.common.b2b.common.clock import ManualClock, SystemClock
from zato.common.b2b.common.recovery import RecoveredPage
from zato.common.b2b.common.scheduler import DeliveryScheduler, Due_Batch_Size, EntryKind, Failed_Entry_Delay, \
    recover_pages

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

_start = datetime(2026, 1, 1, tzinfo=timezone.utc)

# How many entries the volume test schedules, and how many items one page of the paging test holds.
_volume_entries = 10_000
_page_size = 3
_paged_items = 10

# How long a test waits for the scheduler greenlet, in seconds.
_wait_seconds = 5

# The delay of the entry a later one overtakes, in seconds.
_far_seconds = 3600

# ################################################################################################################################
# ################################################################################################################################

def _after(seconds:'float') -> 'datetime':
    out = _start + timedelta(seconds=seconds)
    return out

# ################################################################################################################################

class _Recorder:
    """ Records the keys of the entries that ran, and returns for each the time it is due next, if any.
    """
    def __init__(self) -> 'None':
        self.keys:'strlist' = []
        self.next_due:'dict[str, datetime]' = {}
        self.ran = Event()

    def __call__(self, key:'str', now:'datetime') -> 'datetime | None':
        self.keys.append(key)
        self.ran.set()

        if key in self.next_due:
            out = self.next_due.pop(key)
        else:
            out = None

        return out

# ################################################################################################################################

def _scheduler(recorder:'_Recorder') -> 'DeliveryScheduler':
    out = DeliveryScheduler(ManualClock(_start))
    out.set_handler(EntryKind.Delivery, recorder)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOrdering:
    """ Entries run in the order of their due times, and only once due.
    """

    def test_due_order(self) -> 'None':
        recorder = _Recorder()
        scheduler = _scheduler(recorder)

        scheduler.schedule(EntryKind.Delivery, 'third', _after(30))
        scheduler.schedule(EntryKind.Delivery, 'first', _after(10))
        scheduler.schedule(EntryKind.Delivery, 'second', _after(20))

        assert scheduler.run_due(_after(5)) == 0
        assert scheduler.run_due(_after(20)) == 2
        assert recorder.keys == ['first', 'second']

        assert scheduler.run_due(_after(30)) == 1
        assert recorder.keys == ['first', 'second', 'third']
        assert len(scheduler) == 0

    def test_rescheduled_by_handler(self) -> 'None':
        recorder = _Recorder()
        recorder.next_due['message-1'] = _after(60)

        scheduler = _scheduler(recorder)
        scheduler.schedule(EntryKind.Delivery, 'message-1', _after(0))

        assert scheduler.run_due(_after(0)) == 1
        assert scheduler.due_at(EntryKind.Delivery, 'message-1') == _after(60)

        assert scheduler.run_due(_after(60)) == 1
        assert scheduler.due_at(EntryKind.Delivery, 'message-1') is None

    def test_replace_and_cancel(self) -> 'None':
        recorder = _Recorder()
        scheduler = _scheduler(recorder)

        scheduler.schedule(EntryKind.Delivery, 'replaced', _after(10))
        scheduler.schedule(EntryKind.Delivery, 'replaced', _after(50))
        scheduler.schedule(EntryKind.Delivery, 'cancelled', _after(10))
        scheduler.cancel(EntryKind.Delivery, 'cancelled')

        assert scheduler.run_due(_after(10)) == 0
        assert scheduler.run_due(_after(50)) == 1
        assert recorder.keys == ['replaced']

    def test_failed_entry_runs_again(self) -> 'None':
        scheduler = DeliveryScheduler(ManualClock(_start))

        calls:'strlist' = []

        def fail(key:'str', now:'datetime') -> 'None':
            calls.append(key)
            raise Exception('Delivery failed')

        scheduler.set_handler(EntryKind.Probe, fail)
        scheduler.schedule(EntryKind.Probe, 'address-1', _after(0))

        assert scheduler.run_due(_after(0)) == 1
        assert scheduler.due_at(EntryKind.Probe, 'address-1') == _after(0) + Failed_Entry_Delay

# ################################################################################################################################
# ################################################################################################################################

class TestBatches:
    """ Due entries run in batches.
    """

    def test_batch_size(self) -> 'None':
        recorder = _Recorder()
        scheduler = _scheduler(recorder)

        count = Due_Batch_Size + 5

        for idx in range(count):
            scheduler.schedule(EntryKind.Delivery, f'message-{idx}', _after(0))

        assert scheduler.run_due(_after(0)) == Due_Batch_Size
        assert scheduler.run_due(_after(0)) == 5

# ################################################################################################################################
# ################################################################################################################################

class TestGreenlet:
    """ The greenlet sleeps until the earliest entry and wakes when an earlier one arrives.
    """

    def test_wake_on_earlier_entry(self) -> 'None':
        recorder = _Recorder()
        clock = SystemClock()

        scheduler = DeliveryScheduler(clock)
        scheduler.set_handler(EntryKind.Delivery, recorder)
        scheduler.start()

        now = clock.now()
        far = now + timedelta(seconds=_far_seconds)

        scheduler.schedule(EntryKind.Delivery, 'later', far)
        sleep(0)

        scheduler.schedule(EntryKind.Delivery, 'now', now)

        assert recorder.ran.wait(_wait_seconds)
        assert recorder.keys == ['now']

        scheduler.stop()

    def test_volume(self) -> 'None':
        recorder = _Recorder()
        clock = SystemClock()

        scheduler = DeliveryScheduler(clock)
        scheduler.set_handler(EntryKind.Delivery, recorder)

        now = clock.now()

        for idx in range(_volume_entries):
            scheduler.schedule(EntryKind.Delivery, f'message-{idx}', now)

            # The caller yields as it schedules, as a recovery does between its pages.
            if idx % Due_Batch_Size == 0:
                sleep(0)

        scheduler.start()

        while len(recorder.keys) < _volume_entries:
            sleep(0.01)

        scheduler.stop()

        assert len(recorder.keys) == _volume_entries
        assert len(scheduler) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestRecoverPages:
    """ A recovery reads its pages one after another, from the cursor of the page before.
    """

    def test_pages(self) -> 'None':
        items = list(range(_paged_items))
        cursors:'list[int]' = []

        def read_page(limit:'int', after:'int') -> 'RecoveredPage':
            cursors.append(after)

            page_items = items[after:after + limit]

            out = RecoveredPage()
            out.items = page_items
            out.last_id = after + len(page_items)
            out.is_last = len(page_items) < limit

            return out

        seen:'list[int]' = []

        assert recover_pages(read_page, seen.append, _page_size, 0) == _paged_items
        assert seen == items
        assert cursors == [0, 3, 6, 9]

# ################################################################################################################################
# ################################################################################################################################
