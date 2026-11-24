# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The processes, the arbiter process and the conditions that the tests of the arbiter share.

# stdlib
import os
import signal
import sys
import time
from multiprocessing import get_context

# gevent
import gevent
from gevent.event import Event

# Zato
from zato.common.worker_slot import ModuleCtx as WorkerSlotCtx
from zato.server.arbiter import Arbiter
from zato.server.arbiter_config import ArbiterConfig, ModuleCtx as ArbiterCtx
from zato.server.control.client import ControlClient
from zato.server.control.hub import EntryStatus
from zato.server.outgoing_region import get_outgoing_binding, SharedPublishLock
from zato.server.worker_liveness import reopen_worker_logs, write_heartbeat
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.context import ForkProcess
    from multiprocessing.sharedctypes import Synchronized, SynchronizedArray
    from zato.common.typing_ import any_, anydict, anytuple, callable_, dict_, intlist, list_
    from zato.server.arbiter import WorkerContext
    from zato.server.control.envelope import Message

    any_ = any_
    anydict = anydict
    anytuple = anytuple
    callable_ = callable_
    ForkProcess = ForkProcess
    intlist = intlist
    Message = Message
    Synchronized = Synchronized
    SynchronizedArray = SynchronizedArray
    WorkerContext = WorkerContext

    processlist = list_[ForkProcess]
    tupledict   = dict_[str, anytuple]

# ################################################################################################################################
# ################################################################################################################################

# The arbiter runs in a process of its own, so that its processes are its children and its signals are its own,
# and the probe of a test is created before the fork, so that the arbiter and its processes inherit it
_context = get_context('fork')

Region_Config = {
    'lock_capacity': 4,
}

# The counts through which the processes of a test report what they did and received
Writes_Metric  = 0
Events_Metric  = 1
Reloads_Metric = 2
Query_Metric   = 3
Drains_Metric  = 4
Lock_Metric    = 5
Starts_Metric  = 6
Metric_Count   = 7

# The positions of the record of the worker that reported ready last
_ready_generation = 0
_ready_pid = 1

# The outgoing queue whose publish lock the processes of a test take
Lock_Sub_Key = 'zpsk.outconn-rest.1'

# How many events the worker publishes
Event_Count = 20

# How often the worker of a test writes its heartbeat, in seconds
Heartbeat_Interval = 0.05

# How often the arbiter of a test compares the sizes of the log files with their limits, in seconds
Log_Check_Interval = 0.02

# How long a test waits for a condition, in seconds
Condition_Timeout = 20.0

# How often a test reads the probe while it waits for a condition, in seconds
Condition_Interval = 0.02

# The arbiters that the current test started, which a failed test leaves running
_started_arbiters:'processlist' = []

# ################################################################################################################################
# ################################################################################################################################

class Probe:
    """ The counts that the processes of a test report, the worker that reported ready last and the config process,
    in memory that the arbiter and its processes inherit from the test.
    """

    def __init__(self) -> 'None':
        self.metrics:'SynchronizedArray[int]' = _context.Array('q', Metric_Count)
        self.worker:'SynchronizedArray[int]' = _context.Array('q', 2)
        self.config_pid:'Synchronized[int]' = _context.Value('q', 0)

    def add(self, metric:'int', value:'int') -> 'None':
        with self.metrics.get_lock():
            self.metrics[metric] += value

    def reached(self, metric:'int', value:'int') -> 'bool':
        out = self.metrics[metric] == value
        return out

    def record_ready(self, generation:'int') -> 'None':
        with self.worker.get_lock():
            self.worker[_ready_generation] = generation
            self.worker[_ready_pid] = os.getpid()

    def worker_generation(self) -> 'int':
        out = self.worker[_ready_generation]
        return out

    def worker_pid(self) -> 'int':
        out = self.worker[_ready_pid]
        return out

# ################################################################################################################################
# ################################################################################################################################

def new_config(tmp_dir:'str') -> 'ArbiterConfig':
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
    out.native_log_files        = []
    out.native_log_max_bytes    = ArbiterCtx.Native_Log_Max_Bytes
    out.native_log_backup_count = ArbiterCtx.Native_Log_Backup_Count
    out.tmp_dir                 = tmp_dir

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

def worker_replaced(probe:'Probe', generation:'int') -> 'bool':
    """ Returns whether the worker of a generation, or of a later one, reported ready.
    """
    out = probe.worker_generation() >= generation
    return out

# ################################################################################################################################

def config_started(probe:'Probe') -> 'bool':
    out = probe.config_pid.value != 0
    return out

# ################################################################################################################################
# ################################################################################################################################

class ProcessUnderTest:
    """ The worker or the config process of a test, which serves the control channel and reports what it receives
    in the probe. The worker also writes its heartbeat.
    """

    def __init__(self, region:'SharedRegion', probe:'Probe', ctx:'WorkerContext', is_drain_honored:'bool') -> 'None':
        self.region = region
        self.probe = probe
        self.ctx = ctx
        self.is_drain_honored = is_drain_honored
        self.is_worker = ctx.slot == WorkerSlotCtx.Worker_Slot

        # The body of the next event that this process expects
        self.expected_event = 0

        # An event that arrives before the process reported ready is applied before the initial load
        self.is_ready = False

        self.drained = Event()
        self.client = ControlClient(
            ctx.control_fd, ctx.body_dir, self.on_event, self.on_query, self.on_drain, self.on_reload, reopen_worker_logs)

        _ = self.client.start()

        if not self.is_worker:
            probe.config_pid.value = os.getpid()

    def on_event(self, message:'Message') -> 'None':
        """ Counts an event only if it is the next one and the process reported ready,
        so the count shows the order of delivery and that no event preceded the initial load.
        """
        if not self.is_ready:
            return

        if message.body == self.expected_event:
            self.probe.add(Events_Metric, 1)
            self.expected_event += 1

    def on_query(self, _body:'any_') -> 'anydict':
        out = {'pid': os.getpid()}
        return out

    def on_drain(self) -> 'None':
        if self.is_drain_honored:
            self.probe.add(Drains_Metric, 1)
            self.drained.set()

    def on_reload(self) -> 'None':
        self.probe.add(Reloads_Metric, 1)

    def report_ready(self) -> 'None':
        self.is_ready = True
        self.client.report_ready()

        if self.is_worker:
            self.probe.record_ready(self.ctx.generation)

    def serve(self) -> 'None':
        """ Runs until the arbiter drains the process, the worker writing its heartbeat meanwhile.
        """
        while not self.drained.is_set():
            if self.is_worker:
                write_heartbeat(self.region)

            gevent.sleep(Heartbeat_Interval)

    def wait_for_worker(self) -> 'None':
        while not worker_replaced(self.probe, 1):
            gevent.sleep(Condition_Interval)

# ################################################################################################################################
# ################################################################################################################################

def _new_mains(region:'SharedRegion', probe:'Probe', mode:'str') -> 'anytuple':
    """ Returns the main function of the worker of a test and that of its config process, if the mode runs one.
    """

    def serve(ctx:'WorkerContext') -> 'None':
        process = ProcessUnderTest(region, probe, ctx, True)
        process.report_ready()
        process.serve()

    def ignore_drain(ctx:'WorkerContext') -> 'None':
        process = ProcessUnderTest(region, probe, ctx, False)
        process.report_ready()
        process.serve()

    def no_heartbeat(ctx:'WorkerContext') -> 'None':
        process = ProcessUnderTest(region, probe, ctx, True)
        process.report_ready()

        # The sleep blocks the hub of the first worker, as a service that never yields does
        if ctx.generation == 1:
            time.sleep(Condition_Timeout)

        process.serve()

    def never_ready(ctx:'WorkerContext') -> 'None':
        process = ProcessUnderTest(region, probe, ctx, True)
        probe.add(Starts_Metric, 1)

        if ctx.generation == 1:
            time.sleep(Condition_Timeout)

        process.report_ready()
        process.serve()

    def exit_at_once(_ctx:'WorkerContext') -> 'None':
        probe.add(Starts_Metric, 1)
        sys.exit(1)

    def publish_worker(ctx:'WorkerContext') -> 'None':
        process = ProcessUnderTest(region, probe, ctx, True)

        for body in range(Event_Count):
            process.client.publish(body)

        process.report_ready()
        process.serve()

    def query_config(ctx:'WorkerContext') -> 'None':
        process = ProcessUnderTest(region, probe, ctx, True)

        # The config process queries the worker once it is ready, and counts a response that carries its process ID
        def query() -> 'None':
            process.wait_for_worker()
            entry = process.client.query(None)

            if entry['status'] == EntryStatus.OK:
                if entry['body']['pid'] == probe.worker_pid():
                    probe.add(Query_Metric, 1)

        _ = gevent.spawn(query)

        process.report_ready()
        process.serve()

    def exit_config_once(ctx:'WorkerContext') -> 'None':
        process = ProcessUnderTest(region, probe, ctx, True)
        process.report_ready()

        # The first config process terminates abnormally once the worker is ready
        if ctx.generation == 1:
            process.wait_for_worker()
            os._exit(1)

        process.serve()

    def hold_publish_lock_worker(ctx:'WorkerContext') -> 'None':
        process = ProcessUnderTest(region, probe, ctx, True)

        binding = get_outgoing_binding()
        assert binding is not None

        # The first worker takes the publish lock and holds it until it is terminated
        if ctx.generation == 1:
            lock = SharedPublishLock(binding, Lock_Sub_Key)
            lock.__enter__()
            probe.add(Lock_Metric, 1)

        process.report_ready()
        process.serve()

    def hold_publish_lock_config(ctx:'WorkerContext') -> 'None':
        process = ProcessUnderTest(region, probe, ctx, True)

        binding = get_outgoing_binding()
        assert binding is not None

        lock = SharedPublishLock(binding, Lock_Sub_Key)

        # The config process waits for the lock in a greenlet, once the worker holds it
        def publish_behind_holder() -> 'None':
            while not probe.reached(Lock_Metric, 1):
                gevent.sleep(Condition_Interval)

            with lock:
                probe.add(Writes_Metric, 1)

        _ = gevent.spawn(publish_behind_holder)

        process.report_ready()
        process.serve()

    modes:'tupledict' = {
        'serve': (serve, None),
        'serve_with_config': (serve, serve),
        'ignore_drain': (ignore_drain, None),
        'no_heartbeat': (no_heartbeat, None),
        'never_ready': (never_ready, None),
        'exit_at_once': (exit_at_once, None),
        'publish': (publish_worker, serve),
        'query': (serve, query_config),
        'exit_config_once': (serve, exit_config_once),
        'hold_publish_lock': (hold_publish_lock_worker, hold_publish_lock_config),
    }

    out = modes[mode]
    return out

# ################################################################################################################################

def _run_arbiter(region:'SharedRegion', probe:'Probe', mode:'str', tmp_dir:'str') -> 'None':
    worker_main, config_main = _new_mains(region, probe, mode)
    config = new_config(tmp_dir)

    arbiter = Arbiter(region, worker_main, config, config_main)
    exit_code = arbiter.run()

    sys.exit(exit_code)

# ################################################################################################################################

def start_arbiter_process(region:'SharedRegion', probe:'Probe', mode:'str', tmp_dir:'str') -> 'ForkProcess':
    out = _context.Process(target=_run_arbiter, args=(region, probe, mode, tmp_dir))
    out.start()

    _started_arbiters.append(out)

    return out

# ################################################################################################################################

def terminate_started_arbiters() -> 'None':
    """ Terminates with SIGKILL each arbiter of the current test that still runs, whose processes the kernel then terminates.
    """
    for arbiter in _started_arbiters:
        if arbiter.is_alive():
            arbiter.kill()
            arbiter.join(Condition_Timeout)

    _started_arbiters.clear()

# ################################################################################################################################

def start_arbiter(region:'SharedRegion', probe:'Probe', mode:'str', tmp_dir:'str') -> 'ForkProcess':
    """ Starts the arbiter and waits until its worker reported ready.
    """
    out = start_arbiter_process(region, probe, mode, tmp_dir)
    assert wait_until(worker_replaced, (probe, 1))

    return out

# ################################################################################################################################

def stop_arbiter(arbiter:'ForkProcess', pids:'intlist', tmp_dir:'str') -> 'None':
    """ Stops the arbiter with SIGTERM and confirms that it exited with status 0, that none of its processes remains,
    and that the arbiter removed its control bodies.
    """
    os.kill(arbiter.pid, signal.SIGTERM)
    arbiter.join(Condition_Timeout)

    assert arbiter.exitcode == 0
    assert none_running(pids)
    assert os.listdir(tmp_dir) == []

# ################################################################################################################################
# ################################################################################################################################
