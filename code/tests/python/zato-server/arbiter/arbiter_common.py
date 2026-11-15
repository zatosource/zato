# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The workers, the arbiter process and the conditions that the tests of the arbiter share.

# stdlib
import gc
import logging
import os
import signal
import sys
import threading
import time
from multiprocessing import get_context
from tempfile import gettempdir

# gevent
import gevent
from gevent.event import Event

# Zato
from writer_common import new_message_values
from zato.common.db_env.process_queue import ProcessQueue
from zato.common.hl7.mllp.dedup import Default_Max_Entries, MessageDeduplicator
from zato.common.pubsub.sql.config import ModuleCtx as PubSubConfigCtx
from zato.common.pubsub.sql.writes import new_pending_publication
from zato.common.pubsub.writer_process.remote import new_pubsub_writer, start_writer_client
from zato.common.worker_count import ServerWorkers
from zato.common.worker_slot import ModuleCtx as WorkerSlotCtx
from zato.server.arbiter import Arbiter
from zato.server.arbiter_config import ArbiterConfig, ModuleCtx as ArbiterCtx
from zato.server.control.client import ControlClient
from zato.server.control.hub import EntryStatus
from zato.server.metrics_region import get_counter
from zato.server.outgoing_region import get_outgoing_binding, SharedPublishLock
from zato.server.process_instance import get_process_binding
from zato.server.worker_liveness import reopen_worker_logs, write_heartbeat
from zato_ipc_core.zato_ipc_core import SharedRegion, STATE_READY

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.context import ForkProcess
    from zato.common.typing_ import any_, anydict, anylist, anytuple, callable_, intlist, list_, strcalldict
    from zato.server.arbiter import WorkerContext
    from zato.server.control.envelope import Message

    any_ = any_
    anydict = anydict
    anylist = anylist
    anytuple = anytuple
    callable_ = callable_
    ForkProcess = ForkProcess
    intlist = intlist
    Message = Message
    strcalldict = strcalldict
    WorkerContext = WorkerContext

    processlist = list_[ForkProcess]

# ################################################################################################################################
# ################################################################################################################################

# The arbiter runs in a process of its own, so that its workers are its children and its signals are its own
_context = get_context('fork')

Slot_Count = 3

Region_Config = {
    'slot_count': Slot_Count,
    'wake_capacity': 8,
    'cell_capacity': 8,
    'queue_count': 2,
    'metric_count': 9,
    'series_capacity': 16,
    'series_key_bytes': 16 * 256 * Slot_Count,
    'dedup_capacity': 16,
    'breaker_capacity': 0,
    'lock_capacity': 4,
    'start_id': 1,
}

# The metric that the workers of a test record through the metric objects of the server, and its label value
Requests_Counter = get_counter('zato_test_arbiter_requests_total', 'Requests by channel', ('channel_name',))
Requests_Channel = 'orders'

# The MLLP channel on which every worker of a test receives the same message, and the control ID of the message
Received_Channel = 'hl7.orders'
Received_Control_ID = 'MSG-00001'
Received_TTL_Seconds = 3600.0

# The queue through which a worker of a test writes, and the metrics through which the workers report what they received
Queue = 0
Writes_Metric = 0
Events_Metric = 1
Reloads_Metric = 2
Query_Metric = 3
Drains_Metric = 4
Published_Metric = 5
Grace_Metric = 6
Lock_Metric = 7

# How many generations of the first slot the test allowed to report ready
Release_Metric = 8

# Each pinned worker reports its CPU, counted from one, in the byte of the metric at the position of its slot
CPU_Byte_Bits = 8

# An object that the arbiter of a test loads before it forks, which the collector of a worker sees only if it is not frozen
_freeze_probe:'anylist' = []

# The outgoing queue whose publish lock the workers of a test take
Lock_Sub_Key = 'zpsk.outconn-rest.1'

# The slot whose worker a test terminates or misconfigures, and the slot that waits behind it, neither of which
# is the first slot, before which no other slot starts
Tested_Slot = 1
Waiting_Slot = 2

# How many events the tested worker publishes
Event_Count = 20

# How many messages each worker publishes through the pub/sub writer process, and how often, in seconds
Writer_Message_Count = 40
Writer_Publish_Interval = 0.02

# The grace period of the traces that the arbiter of a test passes to its workers and its writer, in seconds
Trace_Grace_Seconds = 600

# How often a worker of a test writes its heartbeat, in seconds
Heartbeat_Interval = 0.05

# How often the arbiter of a test compares the sizes of the log files with their limits, in seconds
Log_Check_Interval = 0.02

# How long a test waits for a condition, in seconds
Condition_Timeout = 20.0

# How often a test reads the region while it waits for a condition, in seconds
Condition_Interval = 0.02

# The arbiters that the current test started, which a failed test leaves running
_started_arbiters:'processlist' = []

# ################################################################################################################################
# ################################################################################################################################

def new_config(tmp_dir:'str', cpu_max_path:'str'=ServerWorkers.CPU_Max_Path) -> 'ArbiterConfig':
    out = ArbiterConfig()

    out.respawn_delay_initial   = 0.1
    out.respawn_delay_max       = 0.4
    out.failure_count_max       = 3
    out.failure_window          = 10.0
    out.heartbeat_threshold     = 0.5
    out.startup_timeout         = 1.0
    out.grace_period            = 0.5
    out.loop_interval           = 0.05
    out.log_check_interval      = Log_Check_Interval
    out.query_timeout           = 1.0
    out.writer_deadline         = 5.0
    out.trace_grace_seconds     = Trace_Grace_Seconds
    out.native_log_files        = []
    out.native_log_max_bytes    = ArbiterCtx.Native_Log_Max_Bytes
    out.native_log_backup_count = ArbiterCtx.Native_Log_Backup_Count
    out.tmp_dir                 = tmp_dir
    out.socket_dir              = gettempdir()
    out.cpu_max_path            = cpu_max_path

    return out

# ################################################################################################################################

def wait_until(condition:'callable_', args:'anytuple', timeout:'float'=Condition_Timeout) -> 'bool':
    """ Returns whether a condition held within the timeout.
    """
    now = time.monotonic()
    deadline = now + timeout

    out = condition(*args)

    while not out:
        if time.monotonic() >= deadline:
            break

        time.sleep(Condition_Interval)
        out = condition(*args)

    return out

# ################################################################################################################################

def is_running(pid:'int') -> 'bool':
    """ Returns whether a process exists and is not a zombie.
    """
    try:
        with open(f'/proc/{pid}/stat') as stat_file:
            stat = stat_file.read()

    # The process exited before its entry was opened, or between the open and the read
    except (FileNotFoundError, ProcessLookupError):
        out = False

    else:
        _, _, after_name = stat.rpartition(')')
        fields = after_name.split()
        state = fields[0]
        out = state != 'Z'

    return out

# ################################################################################################################################

def none_running(pids:'intlist') -> 'bool':
    out = True

    for pid in pids:
        if is_running(pid):
            out = False

    return out

# ################################################################################################################################

def all_slots_ready(region:'SharedRegion') -> 'bool':
    out = True

    for slot in range(Slot_Count):
        if region.slot_state(slot) != STATE_READY:
            out = False

    return out

# ################################################################################################################################

def slot_replaced(region:'SharedRegion', slot:'int', generation:'int') -> 'bool':
    """ Returns whether a slot reached a generation and its worker reported ready.
    """
    out = False

    if region.slot_generation(slot) >= generation:
        if region.slot_state(slot) == STATE_READY:
            out = True

    return out

# ################################################################################################################################

def metric_reached(region:'SharedRegion', metric:'int', value:'int') -> 'bool':
    out = region.metric_sum(metric) == value
    return out

# ################################################################################################################################

def get_pids(region:'SharedRegion') -> 'intlist':
    out:'intlist' = []

    for slot in range(Slot_Count):
        pid = region.slot_pid(slot)
        out.append(pid)

    return out

# ################################################################################################################################
# ################################################################################################################################

class WorkerUnderTest:
    """ A worker that serves the control channel, writes its heartbeat and reports what it receives in the metrics.
    """

    def __init__(self, region:'SharedRegion', ctx:'WorkerContext', is_drain_honored:'bool') -> 'None':
        self.region = region
        self.ctx = ctx
        self.is_drain_honored = is_drain_honored

        # The body of the next event that this worker expects from the tested slot
        self.expected_event = 0

        # An event that arrives before the worker reported ready is applied before the initial load
        self.is_ready = False

        self.drained = Event()
        self.client = ControlClient(
            ctx.control_fd, ctx.body_dir, self.on_event, self.on_query, self.on_drain, self.on_reload, reopen_worker_logs)

        _ = self.client.start()

    def on_event(self, message:'Message') -> 'None':
        """ Counts an event only if it is the next one of the tested slot and the worker reported ready,
        so the metric shows the order of delivery and that no event preceded the initial load.
        """
        if not self.is_ready:
            return

        if message.slot == Tested_Slot:
            if message.body == self.expected_event:
                self.region.metric_add(self.ctx.slot, Events_Metric, 1)
                self.expected_event += 1

    def on_query(self, _body:'any_') -> 'anydict':
        out = {'pid': os.getpid()}
        return out

    def on_drain(self) -> 'None':
        if self.is_drain_honored:
            self.region.metric_add(self.ctx.slot, Drains_Metric, 1)
            self.drained.set()

    def on_reload(self) -> 'None':
        self.region.metric_add(self.ctx.slot, Reloads_Metric, 1)

    def report_ready(self) -> 'None':
        self.is_ready = True
        self.client.report_ready()

    def serve(self) -> 'None':
        """ Writes the heartbeat until the arbiter drains the worker.
        """
        while not self.drained.is_set():
            write_heartbeat(self.region, self.ctx.slot)
            gevent.sleep(Heartbeat_Interval)

    def wait_for_all_ready(self) -> 'None':
        while not all_slots_ready(self.region):
            gevent.sleep(Condition_Interval)

    def count_responses(self, entries:'anylist') -> 'None':
        """ Reports how many slots responded to a query with the process ID that the region holds for them.
        """
        for entry in entries:
            if entry['status'] == EntryStatus.OK:
                if entry['body']['pid'] == self.region.slot_pid(entry['slot']):
                    self.region.metric_add(self.ctx.slot, Query_Metric, 1)

# ################################################################################################################################
# ################################################################################################################################

def _write_behind_holder(region:'SharedRegion', slot:'int') -> 'None':
    """ Takes a place in the queue once the worker of the tested slot holds its turn, and reports the write.
    """
    assert wait_until(region.queue_has_place, (Queue, Tested_Slot))

    process_queue = ProcessQueue(region, Queue, slot, Condition_Timeout)
    write_args = (slot, Writes_Metric, 1)

    _ = process_queue.run(region.metric_add, write_args)

# ################################################################################################################################

def _ignore_reconnect() -> 'None':
    """ A worker of a test has no wake counters to increment after the writer accepts a new connection.
    """

# ################################################################################################################################

def _new_worker_main(region:'SharedRegion', mode:'str') -> 'callable_':
    """ Returns the worker of a test, in which the tested slot behaves as the mode states and the others serve.
    """

    def hold_turn(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, True)

        # The first worker of the tested slot holds the turn of the queue until it is terminated ..
        if ctx.slot == Tested_Slot:
            if ctx.generation == 1:
                _ = region.queue_enter(Queue, ctx.slot)
                assert region.queue_poll(Queue, ctx.slot)

        # .. and the worker of the next slot waits for the turn in a thread, while its heartbeat continues.
        if ctx.slot == Waiting_Slot:
            thread = threading.Thread(target=_write_behind_holder, args=(region, ctx.slot))
            thread.start()

        worker.report_ready()
        worker.serve()

    def no_heartbeat(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, True)
        worker.report_ready()

        # The sleep blocks the hub of the worker, as a service that never yields does
        if ctx.slot == Tested_Slot:
            if ctx.generation == 1:
                time.sleep(Condition_Timeout)

        worker.serve()

    def never_ready(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, True)

        if ctx.slot == Tested_Slot:
            if ctx.generation == 1:
                time.sleep(Condition_Timeout)

        worker.report_ready()
        worker.serve()

    def exit_at_once(ctx:'WorkerContext') -> 'None':
        if ctx.slot == Tested_Slot:
            sys.exit(1)

        worker = WorkerUnderTest(region, ctx, True)
        worker.report_ready()
        worker.serve()

    def ignore_drain(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, False)
        worker.report_ready()
        worker.serve()

    def publish(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, True)

        # The tested slot publishes its events at once, so a slot that has not reported ready receives them later ..
        if ctx.slot == Tested_Slot:
            for body in range(Event_Count):
                worker.client.publish(body)

        # .. and the slot after it reports ready only once the tested slot has published every event.
        if ctx.slot == Waiting_Slot:
            while region.metric_sum(Events_Metric) != Event_Count:
                gevent.sleep(Condition_Interval)

        worker.report_ready()
        worker.serve()

    def query(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, True)
        worker.report_ready()

        if ctx.slot == Tested_Slot:
            worker.wait_for_all_ready()
            entries = worker.client.query(None)
            worker.count_responses(entries)

        worker.serve()

    def serve(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, True)
        worker.report_ready()
        worker.serve()

    def publish_to_writer(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, True)

        # The worker inherited the grace period of the traces that the arbiter set for the writer ..
        if os.environ[PubSubConfigCtx.Env_Trace_Grace_Seconds] == str(Trace_Grace_Seconds):
            region.metric_add(ctx.slot, Grace_Metric, 1)

        # .. it connects to the writer ..
        address = ctx.writer_address
        assert address is not None

        _ = start_writer_client(address, ctx.writer_deadline, _ignore_reconnect)
        writer = new_pubsub_writer()

        # .. and publishes its messages through it, reporting each publication that succeeded.
        def publish_messages() -> 'None':
            for index in range(Writer_Message_Count):
                message_values = new_message_values(f'msg-{ctx.slot}-{index}')
                writer.publish(new_pending_publication(message_values))

                region.metric_add(ctx.slot, Published_Metric, 1)
                gevent.sleep(Writer_Publish_Interval)

        worker.report_ready()
        _ = gevent.spawn(publish_messages)

        worker.serve()

    def record_metric(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, True)

        # Each worker counts one more request than the slot before it, through the metric objects of the server
        Requests_Counter.labels(Requests_Channel).inc(ctx.slot + 1)

        worker.report_ready()
        worker.serve()

    def receive_control_id(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, True)

        # Each worker receives the same message, and reports whether it invoked the service of the channel
        deduplicator = MessageDeduplicator(Received_TTL_Seconds, Default_Max_Entries, Received_Channel)

        if not deduplicator.is_duplicate(Received_Control_ID):
            region.metric_add(ctx.slot, Writes_Metric, 1)

        worker.report_ready()
        worker.serve()

    def report_process_instance(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, True)

        # Each worker reports whether its process instance names the arbiter of the region, its slot and its generation
        binding = get_process_binding()
        instance = {'start_id': region.start_id, 'slot': ctx.slot, 'generation': ctx.generation}

        if binding is not None and binding.instance == instance:
            region.metric_add(ctx.slot, Writes_Metric, 1)

        worker.report_ready()
        worker.serve()

    def hold_publish_lock(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, True)

        binding = get_outgoing_binding()
        assert binding is not None

        lock = SharedPublishLock(binding, Lock_Sub_Key)

        # The first worker of the tested slot takes the publish lock and holds it until it is terminated ..
        if ctx.slot == Tested_Slot:
            if ctx.generation == 1:
                lock.__enter__()
                region.metric_add(ctx.slot, Lock_Metric, 1)

        # .. and the worker of the next slot waits for the lock in a greenlet, while its heartbeat continues.
        if ctx.slot == Waiting_Slot:

            def publish_behind_holder() -> 'None':
                while region.metric_sum(Lock_Metric) == 0:
                    gevent.sleep(Condition_Interval)

                with lock:
                    region.metric_add(ctx.slot, Writes_Metric, 1)

            _ = gevent.spawn(publish_behind_holder)

        worker.report_ready()
        worker.serve()

    def publish_on_sigterm(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, False)

        address = ctx.writer_address
        assert address is not None

        _ = start_writer_client(address, ctx.writer_deadline, _ignore_reconnect)
        writer = new_pubsub_writer()

        # The worker drains on its own SIGTERM, as under killpg, and publishes one message while it drains ..
        def drain() -> 'None':
            message_values = new_message_values(f'drain-{ctx.slot}')
            writer.publish(new_pending_publication(message_values))

            region.metric_add(ctx.slot, Published_Metric, 1)
            worker.drained.set()

        def on_sigterm() -> 'None':
            _ = gevent.spawn(drain)

        _ = gevent.signal_handler(signal.SIGTERM, on_sigterm)

        # .. and it ignores the drain command of the arbiter, which follows its own.
        worker.report_ready()
        worker.serve()

    def first_slot_late(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, True)

        # Each generation of the first slot reports ready only once the test allowed it, writing its heartbeat meanwhile
        if ctx.slot == ArbiterCtx.First_Slot:
            while region.metric_sum(Release_Metric) < ctx.generation:
                write_heartbeat(region, ctx.slot)
                gevent.sleep(Condition_Interval)

        worker.report_ready()
        worker.serve()

    def report_cpus(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, True)

        # Each worker reports whether it inherited the objects that the arbiter froze before the fork ..
        is_probe_visible = any(item is _freeze_probe for item in gc.get_objects())

        if not is_probe_visible:
            region.metric_add(ctx.slot, Writes_Metric, 1)

        # .. how many CPUs it may run on ..
        cpus = sorted(os.sched_getaffinity(0))
        region.metric_add(ctx.slot, Events_Metric, len(cpus))

        # .. and the CPU to which it is pinned, if it is.
        if len(cpus) == 1:
            cpu_value = (cpus[0] + 1) << (CPU_Byte_Bits * ctx.slot)
            region.metric_add(ctx.slot, Query_Metric, cpu_value)

        worker.report_ready()
        worker.serve()

    def report_log_slot(ctx:'WorkerContext') -> 'None':
        worker = WorkerUnderTest(region, ctx, True)

        # Each worker reports whether its log records name its slot
        logger = logging.getLogger(__name__)
        record = logger.makeRecord(logger.name, logging.INFO, __file__, 0, 'Worker started', (), None)

        if record.__dict__[WorkerSlotCtx.Attr_Name] == ctx.slot:
            region.metric_add(ctx.slot, Writes_Metric, 1)

        worker.report_ready()
        worker.serve()

    modes:'strcalldict' = {
        'hold_turn': hold_turn,
        'no_heartbeat': no_heartbeat,
        'never_ready': never_ready,
        'exit_at_once': exit_at_once,
        'ignore_drain': ignore_drain,
        'publish': publish,
        'query': query,
        'serve': serve,
        'publish_to_writer': publish_to_writer,
        'publish_on_sigterm': publish_on_sigterm,
        'record_metric': record_metric,
        'receive_control_id': receive_control_id,
        'report_process_instance': report_process_instance,
        'hold_publish_lock': hold_publish_lock,
        'first_slot_late': first_slot_late,
        'report_cpus': report_cpus,
        'report_log_slot': report_log_slot,
    }

    out = modes[mode]
    return out

# ################################################################################################################################

def _run_arbiter(
    region:'SharedRegion',
    mode:'str',
    tmp_dir:'str',
    writer_main:'callable_ | None',
    cpu_max_path:'str',
) -> 'None':
    worker_main = _new_worker_main(region, mode)
    config = new_config(tmp_dir, cpu_max_path)

    arbiter = Arbiter(region, worker_main, config, writer_main)
    exit_code = arbiter.run()

    sys.exit(exit_code)

# ################################################################################################################################

def start_arbiter_process(
    region:'SharedRegion',
    mode:'str',
    tmp_dir:'str',
    writer_main:'callable_ | None'=None,
    cpu_max_path:'str'=ServerWorkers.CPU_Max_Path,
) -> 'ForkProcess':
    out = _context.Process(target=_run_arbiter, args=(region, mode, tmp_dir, writer_main, cpu_max_path))
    out.start()

    _started_arbiters.append(out)

    return out

# ################################################################################################################################

def terminate_started_arbiters() -> 'None':
    """ Terminates with SIGKILL each arbiter of the current test that still runs, whose workers the kernel then terminates.
    """
    for arbiter in _started_arbiters:
        if arbiter.is_alive():
            arbiter.kill()
            arbiter.join(Condition_Timeout)

    _started_arbiters.clear()

# ################################################################################################################################

def start_arbiter(
    region:'SharedRegion',
    mode:'str',
    tmp_dir:'str',
    writer_main:'callable_ | None'=None,
    cpu_max_path:'str'=ServerWorkers.CPU_Max_Path,
) -> 'ForkProcess':
    """ Starts the arbiter and waits until every slot has a worker that reported ready.
    """
    out = start_arbiter_process(region, mode, tmp_dir, writer_main, cpu_max_path)
    assert wait_until(all_slots_ready, (region,))

    return out

# ################################################################################################################################

def stop_arbiter(arbiter:'ForkProcess', pids:'intlist', tmp_dir:'str') -> 'None':
    """ Stops the arbiter with SIGTERM and confirms that it exited with status 0, that no worker remains,
    and that the arbiter removed its control bodies.
    """
    os.kill(arbiter.pid, signal.SIGTERM)
    arbiter.join(Condition_Timeout)

    assert arbiter.exitcode == 0
    assert none_running(pids)
    assert os.listdir(tmp_dir) == []

# ################################################################################################################################
# ################################################################################################################################
