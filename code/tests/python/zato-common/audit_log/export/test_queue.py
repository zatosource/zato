# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic
from unittest import TestCase

# Zato
from support import attributes_of, build_config, build_queue, build_queued, build_stopped_queue, decode_records, wait_for_attempts, \
    wait_for_bodies, wait_for_exported, wait_for_paused, Endpoint, FakeSender
from zato.common.audit_log.export.mapping import ModuleCtx as MappingCtx
from zato.common.audit_log.export.queue import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.export.queue import ExportQueue
    from zato.common.typing_ import intlist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The logger every line of the queue goes to
_logger_name = 'zato.common.audit_log.export.queue'

# A backoff short enough for a test to see several retries
_test_backoff_min = 0.02
_test_backoff_max = 0.05

# ################################################################################################################################
# ################################################################################################################################

def _ids_of(body:'bytes') -> 'intlist':
    """ The event ids of the records in one body, in order.
    """
    out:'intlist' = []

    for record in decode_records(body):
        attributes = attributes_of(record)
        out.append(attributes[MappingCtx.Event_ID])

    return out

# ################################################################################################################################

def _queued_ids(queue:'ExportQueue') -> 'intlist':
    out:'intlist' = []

    for event in queue._queue:
        out.append(event.event_id)

    return out

# ################################################################################################################################

def _lines_starting_with(messages:'strlist', prefix:'str') -> 'strlist':
    out:'strlist' = []

    for message in messages:
        if message.startswith(prefix):
            out.append(message)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestBound(TestCase):

    def test_full_queue_drops_the_oldest(self) -> 'None':

        sender = FakeSender()
        config = build_config(queue_size=5, batch_size=64)
        queue = build_stopped_queue(config, sender)

        with self.assertLogs(_logger_name, level='WARNING') as logs:
            for event_id in range(1, 9):
                queue.add(build_queued(event_id=event_id))

        # The newest five are kept, the oldest three were dropped ..
        self.assertEqual(len(queue), 5)
        self.assertEqual(_queued_ids(queue), [4, 5, 6, 7, 8])

        stats = queue.get_stats()
        self.assertEqual(stats['emitted'], 8)
        self.assertEqual(stats['dropped'], 3)

        # .. and the first drop logged once, naming the bound.
        full_lines = _lines_starting_with(logs.output, f'WARNING:{_logger_name}:Audit export queue full at 5 events, dropping the oldest')
        self.assertEqual(len(full_lines), 1)
        self.assertEqual(len(logs.output), 1)

# ################################################################################################################################
# ################################################################################################################################

class TestRetry(TestCase):

    def test_refused_batch_is_resent_as_the_same_bytes(self) -> 'None':

        sender = FakeSender()
        sender.is_refusing = True

        config = build_config(batch_size=64)
        queue = build_stopped_queue(config, sender)

        for event_id in range(1, 4):
            queue.add(build_queued(event_id=event_id))

        # The batch leaves the queue and is refused ..
        queue._take_batch()
        self.assertEqual(len(queue), 0)

        with self.assertLogs(_logger_name, level='WARNING') as logs:
            self.assertFalse(queue._send_in_flight())
            queue._on_refused()

        self.assertEqual(len(logs.output), 1)
        self.assertIn(f'Audit export to {Endpoint} paused - HTTP 503 Service Unavailable', logs.output[0])

        # .. stays in flight and is sent again as the very same bytes ..
        self.assertEqual(queue.get_stats()['in_flight'], 3)
        self.assertFalse(queue._send_in_flight())
        queue._on_refused()

        self.assertEqual(len(sender.attempts), 2)
        self.assertEqual(sender.attempts[0], sender.attempts[1])
        self.assertEqual(queue.get_stats()['batches_failed'], 2)

        # .. and once accepted, it is the same bytes the collector took.
        sender.is_refusing = False

        with self.assertLogs(_logger_name, level='WARNING') as logs:
            self.assertTrue(queue._send_in_flight())
            queue._on_accepted()

        self.assertEqual(len(logs.output), 1)
        self.assertIn(f'Audit export to {Endpoint} resumed', logs.output[0])
        self.assertNotIn('dropped', logs.output[0])

        self.assertEqual(sender.bodies, [sender.attempts[0]])
        self.assertEqual(_ids_of(sender.bodies[0]), [1, 2, 3])

        stats = queue.get_stats()
        self.assertEqual(stats['in_flight'], 0)
        self.assertEqual(stats['exported'], 3)
        self.assertEqual(stats['batches_ok'], 1)
        self.assertFalse(stats['is_paused'])

# ################################################################################################################################

    def test_nothing_is_logged_while_the_collector_takes_everything(self) -> 'None':

        sender = FakeSender()
        config = build_config(batch_size=64)
        queue = build_stopped_queue(config, sender)

        for event_id in range(1, 4):
            queue.add(build_queued(event_id=event_id))

        with self.assertNoLogs(_logger_name, level='WARNING'):
            queue._take_batch()
            self.assertTrue(queue._send_in_flight())
            queue._on_accepted()

        self.assertEqual(_ids_of(sender.bodies[0]), [1, 2, 3])

# ################################################################################################################################
# ################################################################################################################################

class TestOutage(TestCase):
    """ A long outage against a refusing sender, with the worker running and a short backoff.
    """

    def setUp(self) -> 'None':
        self.backoff_min = ModuleCtx.Backoff_Min_Seconds
        self.backoff_max = ModuleCtx.Backoff_Max_Seconds

        ModuleCtx.Backoff_Min_Seconds = _test_backoff_min
        ModuleCtx.Backoff_Max_Seconds = _test_backoff_max

    def tearDown(self) -> 'None':
        ModuleCtx.Backoff_Min_Seconds = self.backoff_min
        ModuleCtx.Backoff_Max_Seconds = self.backoff_max

# ################################################################################################################################

    def test_each_line_is_logged_once(self) -> 'None':

        sender = FakeSender()
        sender.is_refusing = True

        config = build_config(batch_size=2, max_batch_size=64, flush_interval_ms=20, queue_size=4)
        queue = build_queue(config, sender)

        with self.assertLogs(_logger_name, level='WARNING') as logs:

            # The first batch is taken and refused, again and again ..
            queue.add(build_queued(event_id=1))
            queue.add(build_queued(event_id=2))

            self.assertTrue(wait_for_attempts(sender, 4))
            self.assertTrue(queue.get_stats()['is_paused'])
            self.assertEqual(queue.get_stats()['in_flight'], 2)

            # .. events keep arriving and the queue fills up, dropping the oldest ..
            for event_id in range(3, 9):
                queue.add(build_queued(event_id=event_id))

            self.assertEqual(_queued_ids(queue), [5, 6, 7, 8])
            self.assertEqual(queue.get_stats()['dropped'], 2)

            # .. the collector comes back and everything still held is delivered.
            sender.is_refusing = False

            self.assertTrue(wait_for_exported(queue, 6))

        queue.flush_and_stop(1.0)

        # The refused batch went out as the same bytes it was first refused with ..
        self.assertEqual(sender.bodies[0], sender.attempts[0])
        self.assertEqual(_ids_of(sender.bodies[0]), [1, 2])
        self.assertEqual(_ids_of(sender.bodies[1]), [5, 6, 7, 8])

        # .. and the outage wrote exactly three lines.
        paused = _lines_starting_with(logs.output, f'WARNING:{_logger_name}:Audit export to {Endpoint} paused - HTTP 503 Service Unavailable')
        full = _lines_starting_with(logs.output, f'WARNING:{_logger_name}:Audit export queue full at 4 events, dropping the oldest')
        resumed = _lines_starting_with(logs.output, f'WARNING:{_logger_name}:Audit export to {Endpoint} resumed, 2 events dropped, ids 3 to 4')

        self.assertEqual(len(paused), 1, logs.output)
        self.assertEqual(len(full), 1, logs.output)
        self.assertEqual(len(resumed), 1, logs.output)
        self.assertEqual(len(logs.output), 3, logs.output)

        self.assertFalse(queue.get_stats()['is_paused'])

# ################################################################################################################################

    def test_one_dropped_event_is_singular(self) -> 'None':

        sender = FakeSender()
        sender.is_refusing = True

        config = build_config(batch_size=1, flush_interval_ms=20, queue_size=1)
        queue = build_queue(config, sender)

        with self.assertLogs(_logger_name, level='WARNING') as logs:

            queue.add(build_queued(event_id=1))
            self.assertTrue(wait_for_attempts(sender, 2))

            queue.add(build_queued(event_id=2))
            queue.add(build_queued(event_id=3))

            sender.is_refusing = False
            self.assertTrue(wait_for_exported(queue, 2))

        queue.flush_and_stop(1.0)

        full = _lines_starting_with(logs.output, f'WARNING:{_logger_name}:Audit export queue full at 1 event, dropping the oldest')
        resumed = _lines_starting_with(logs.output, f'WARNING:{_logger_name}:Audit export to {Endpoint} resumed, 1 event dropped, ids 2 to 2')

        self.assertEqual(len(full), 1, logs.output)
        self.assertEqual(len(resumed), 1, logs.output)

# ################################################################################################################################

    def test_resume_without_drops(self) -> 'None':

        sender = FakeSender()
        sender.is_refusing = True

        config = build_config(batch_size=1, flush_interval_ms=20)
        queue = build_queue(config, sender)

        with self.assertLogs(_logger_name, level='WARNING') as logs:

            queue.add(build_queued(event_id=1))
            self.assertTrue(wait_for_attempts(sender, 2))

            sender.is_refusing = False
            self.assertTrue(wait_for_exported(queue, 1))

        queue.flush_and_stop(1.0)

        self.assertEqual(len(logs.output), 2, logs.output)
        self.assertTrue(logs.output[0].endswith(f'Audit export to {Endpoint} paused - HTTP 503 Service Unavailable'))
        self.assertTrue(logs.output[1].endswith(f'Audit export to {Endpoint} resumed'))

# ################################################################################################################################

    def test_a_second_outage_logs_again(self) -> 'None':

        sender = FakeSender()
        config = build_config(batch_size=1, flush_interval_ms=20)
        queue = build_queue(config, sender)

        with self.assertLogs(_logger_name, level='WARNING') as logs:

            for event_id in (1, 2):
                sender.is_refusing = True
                queue.add(build_queued(event_id=event_id))
                self.assertTrue(wait_for_paused(queue))

                sender.is_refusing = False
                self.assertTrue(wait_for_exported(queue, event_id))

        queue.flush_and_stop(1.0)

        paused = _lines_starting_with(logs.output, f'WARNING:{_logger_name}:Audit export to {Endpoint} paused')
        resumed = _lines_starting_with(logs.output, f'WARNING:{_logger_name}:Audit export to {Endpoint} resumed')

        self.assertEqual(len(paused), 2)
        self.assertEqual(len(resumed), 2)

# ################################################################################################################################
# ################################################################################################################################

class TestWorker(TestCase):

    def test_full_batch_is_sent_at_once_and_a_partial_one_on_the_interval(self) -> 'None':

        sender = FakeSender()
        config = build_config(batch_size=3, flush_interval_ms=100)
        queue = build_queue(config, sender)

        for event_id in range(1, 4):
            queue.add(build_queued(event_id=event_id))

        self.assertTrue(wait_for_bodies(sender, 1))
        self.assertEqual(_ids_of(sender.bodies[0]), [1, 2, 3])

        queue.add(build_queued(event_id=4))

        self.assertTrue(wait_for_bodies(sender, 2))
        self.assertEqual(_ids_of(sender.bodies[1]), [4])

        queue.flush_and_stop(1.0)
        self.assertTrue(sender.is_closed)

# ################################################################################################################################

    def test_batch_grows_to_the_maximum_and_shrinks_back(self) -> 'None':

        sender = FakeSender()
        config = build_config(batch_size=4, max_batch_size=16, queue_size=1000)
        queue = build_stopped_queue(config, sender)

        # A backed-up queue drains in batches of the maximum ..
        for event_id in range(1, 41):
            queue.add(build_queued(event_id=event_id))

        sizes = []

        while len(queue):
            queue._take_batch()
            self.assertTrue(queue._send_in_flight())
            sizes.append(len(queue._in_flight))
            queue._on_accepted()

        self.assertEqual(sizes, [16, 16, 8])

        # .. and one that is not sends what it has.
        for event_id in range(41, 45):
            queue.add(build_queued(event_id=event_id))

        queue._take_batch()
        self.assertEqual(len(queue._in_flight), 4)
        self.assertTrue(queue._send_in_flight())
        queue._on_accepted()

        self.assertEqual(_ids_of(sender.bodies[-1]), [41, 42, 43, 44])
        self.assertEqual(queue.get_stats()['exported'], 44)

# ################################################################################################################################

    def test_batch_that_cannot_be_built_is_dropped(self) -> 'None':

        sender = FakeSender()
        config = build_config(batch_size=64)
        queue = build_stopped_queue(config, sender)

        queue.add(build_queued(event_id=1))
        queue.add(build_queued(event_id=2, event_time_iso='not a time'))

        with self.assertLogs(_logger_name, level='ERROR') as logs:
            queue._take_batch()

        self.assertEqual(len(logs.output), 1)
        self.assertIn('Audit export dropped a batch it could not build, event ids [1, 2]', logs.output[0])

        # Nothing is in flight, nothing is queued and the next batch goes through
        self.assertEqual(queue.get_stats()['in_flight'], 0)
        self.assertEqual(len(queue), 0)
        self.assertEqual(sender.attempts, [])

        queue.add(build_queued(event_id=3))
        queue._take_batch()
        self.assertTrue(queue._send_in_flight())
        queue._on_accepted()

        self.assertEqual(_ids_of(sender.bodies[0]), [3])

# ################################################################################################################################

    def test_records_are_built_in_slices(self) -> 'None':

        self.assertEqual(ModuleCtx.Records_Per_Slice, 8)
        self.assertGreater(ModuleCtx.Slice_Pause_Seconds, 0)

        sender = FakeSender()
        config = build_config(batch_size=64, max_batch_size=64)
        queue = build_stopped_queue(config, sender)

        for event_id in range(1, 21):
            queue.add(build_queued(event_id=event_id))

        queue._take_batch()
        self.assertTrue(queue._send_in_flight())
        queue._on_accepted()

        self.assertEqual(_ids_of(sender.bodies[0]), list(range(1, 21)))

# ################################################################################################################################
# ################################################################################################################################

class TestShutdown(TestCase):

    def test_flush_sends_what_is_queued_and_closes_the_sender(self) -> 'None':

        sender = FakeSender()
        config = build_config(batch_size=64)
        queue = build_stopped_queue(config, sender)

        for event_id in range(1, 11):
            queue.add(build_queued(event_id=event_id))

        queue.flush_and_stop(2.0)

        self.assertEqual(len(sender.bodies), 1)
        self.assertEqual(_ids_of(sender.bodies[0]), list(range(1, 11)))
        self.assertEqual(len(queue), 0)
        self.assertTrue(sender.is_closed)

# ################################################################################################################################

    def test_flush_stops_the_worker(self) -> 'None':

        sender = FakeSender()
        config = build_config(batch_size=64, flush_interval_ms=50)
        queue = build_queue(config, sender)

        queue.add(build_queued(event_id=1))
        self.assertTrue(wait_for_bodies(sender, 1))

        worker = queue._worker
        self.assertIsNotNone(worker)

        queue.flush_and_stop(2.0)

        if worker:
            self.assertFalse(worker.is_alive())

        self.assertTrue(sender.is_closed)

# ################################################################################################################################

    def test_flush_gives_up_when_the_collector_refuses(self) -> 'None':

        sender = FakeSender()
        sender.is_refusing = True

        config = build_config(batch_size=64)
        queue = build_stopped_queue(config, sender)

        for event_id in range(1, 4):
            queue.add(build_queued(event_id=event_id))

        start = monotonic()
        queue.flush_and_stop(0.5)
        elapsed = monotonic() - start

        # One attempt, then the sender is closed without waiting for the whole timeout
        self.assertLess(elapsed, 0.5)
        self.assertEqual(len(sender.attempts), 1)
        self.assertEqual(sender.bodies, [])
        self.assertTrue(sender.is_closed)

# ################################################################################################################################

    def test_flush_stops_at_the_deadline(self) -> 'None':

        sender = FakeSender()
        config = build_config(batch_size=64, max_batch_size=1)
        queue = build_stopped_queue(config, sender)

        for event_id in range(1, 4):
            queue.add(build_queued(event_id=event_id))

        queue.flush_and_stop(0.0)

        # No time at all means nothing more is sent, the sender is still closed
        self.assertEqual(sender.bodies, [])
        self.assertTrue(sender.is_closed)

# ################################################################################################################################
# ################################################################################################################################
