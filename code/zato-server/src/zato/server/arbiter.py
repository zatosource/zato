# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The arbiter of a server. It forks the config process, which commits every change of configuration, and once
# the config process is ready, the worker, which processes the messages. It respawns a process that terminated,
# terminates a worker whose heartbeat stopped, relays the control channel between the two processes,
# rotates the log files, and drains both processes on shutdown.

# stdlib
import gc
import os
import signal
from logging import getLogger
from select import POLLIN
from shutil import rmtree
from tempfile import mkdtemp
from time import monotonic

# gevent
import gevent
from gevent.monkey import get_original

# Zato
from zato.common.typing_ import cast_
from zato.common.util.log_rotation import get_worker_handlers, LogRotator, WorkerFileHandler
from zato.common.worker_slot import ModuleCtx as WorkerSlotCtx, set_process_slot
from zato.server.arbiter_config import ModuleCtx, new_worker_slot, WorkerContext, WorkerState
from zato.server.arbiter_config_process import ConfigSupervisor
from zato.server.control.hub import ControlHub
from zato.server.outgoing_region import bind_outgoing
from zato.server.worker_liveness import now_us, set_parent_death_signal, write_heartbeat
from zato_server_core.zato_server_core import set_process_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_, list_
    from zato.server.arbiter_config import ArbiterConfig, WorkerSlot
    from zato_ipc_core.zato_ipc_core import SharedRegion

    ArbiterConfig = ArbiterConfig
    callable_ = callable_
    SharedRegion = SharedRegion
    WorkerSlot = WorkerSlot

    floatlist = list_[float]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The originals of the operating system calls, which gevent replaces when it patches the standard library
_fork    = get_original('os', 'fork')
_waitpid = get_original('os', 'waitpid')
_poll    = get_original('select', 'poll')
_signal  = get_original('signal', 'signal')

# ################################################################################################################################
# ################################################################################################################################

class Arbiter:
    """ Forks and supervises the config process and the worker of one server.
    """

    def __init__(
        self,
        region:'SharedRegion',
        worker_main:'callable_',
        config:'ArbiterConfig',
        config_main:'callable_ | None' = None,
        ) -> 'None':

        # The worker and the config process are called with their WorkerContext
        self.region      = region
        self.worker_main = worker_main
        self.config      = config

        self.pid = os.getpid()
        self.is_stopping = False

        # Whether the worker has been ready at least once
        self.has_started = False

        # The record of the worker, its state and the generation of its current process
        self.worker = new_worker_slot(WorkerSlotCtx.Worker_Slot, 'workers')
        self.worker_state = WorkerState.Stopped
        self.worker_generation = 0

        # Signals and stop requests write to this pipe, so that the wait of the main loop returns at once
        self.wake_read, self.wake_write = os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC)

        self.body_dir = mkdtemp(prefix=ModuleCtx.Body_Dir_Prefix, dir=config.tmp_dir)
        self.hub = ControlHub(self.body_dir, config.query_timeout, self._on_ready, self._on_logs_reopened, self._on_replaced)

        # The arbiter renames the log files that every process appends to, through the handlers that it configured
        # before the fork and through a handler of each file of zato_server_core that it does not write to itself,
        # and the first check follows one interval after the start
        handlers = get_worker_handlers()

        for path in config.native_log_files:
            handler = WorkerFileHandler(path, maxBytes=config.native_log_max_bytes, backupCount=config.native_log_backup_count)
            handlers.append(handler)

        self.log_rotator = LogRotator(handlers, self.hub.broadcast_reopen_logs)
        self.log_check_at = monotonic() + config.log_check_interval

        # The config process, which a server always runs and which an arbiter under test may run without
        self.config_process:'ConfigSupervisor | None' = None

        if config_main:
            self.config_process = ConfigSupervisor(self, config_main)

# ################################################################################################################################

    def request_stop(self) -> 'None':
        """ Asks the main loop to drain the processes and return.
        """
        self.is_stopping = True
        _ = os.write(self.wake_write, b'\0')

# ################################################################################################################################

    def _on_signal(self, signal_number:'int', _frame:'object') -> 'None':
        if signal_number == signal.SIGTERM:
            self.is_stopping = True

# ################################################################################################################################

    def _install_signals(self) -> 'None':
        _ = signal.set_wakeup_fd(self.wake_write)
        _ = _signal(signal.SIGCHLD, self._on_signal)
        _ = _signal(signal.SIGTERM, self._on_signal)

# ################################################################################################################################

    def reset_signals_in_child(self) -> 'None':
        _ = signal.set_wakeup_fd(-1)
        _ = _signal(signal.SIGCHLD, signal.SIG_DFL)
        _ = _signal(signal.SIGTERM, signal.SIG_DFL)

        os.close(self.wake_read)
        os.close(self.wake_write)

# ################################################################################################################################

    def reinit_hub_in_child(self) -> 'None':
        """ Prepares the hub of a forked process. The SIGCHLD handler that the child watchers of the hub depend on
        is replaced in reset_signals_in_child, so it is installed again, without which no subprocess
        that the process starts is ever reported as terminated.
        """
        gevent.reinit()

        loop = gevent.get_hub().loop
        loop.reset_sigchld() # type: ignore
        loop.install_sigchld()

# ################################################################################################################################

    def _on_ready(self, slot:'int') -> 'None':
        """ Records that the worker, or the config process, reported ready, unless the worker is draining already.
        """
        if slot == WorkerSlotCtx.Config_Slot:
            config_process = cast_('ConfigSupervisor', self.config_process)
            config_process.on_ready()
            return

        if self.worker_state == WorkerState.Starting:
            self.worker_state = WorkerState.Ready

            if not self.has_started:
                self.has_started = True
                logger.info('Worker is ready')

# ################################################################################################################################

    def _on_logs_reopened(self, slot:'int', rotation_id:'int') -> 'None':
        self.log_rotator.on_reopened(slot, rotation_id)

# ################################################################################################################################

    def _on_replaced(self, slot:'int') -> 'None':
        """ Drains the processes once one of them learned that another server took over the pub/sub database,
        because the generation that the arbiter raised is no longer current for this server.
        """
        logger.warning('Process of slot %s reported that another server took over the pub/sub database, stopping', slot)
        self.request_stop()

# ################################################################################################################################

    def _rotate_logs_due(self) -> 'None':
        """ Renames the log files that reached their limits, once each interval.
        """
        now = monotonic()

        if now >= self.log_check_at:
            self.log_check_at = now + self.config.log_check_interval
            _ = self.log_rotator.rotate_due()

# ################################################################################################################################

    def _run_worker(self, ctx:'WorkerContext') -> 'None':
        """ Runs in the forked process and never returns.
        """
        exit_code = ModuleCtx.Exit_Code_Worker_Error

        try:

            # The worker terminates with the arbiter, including an arbiter that terminated before this call ..
            set_parent_death_signal()

            if os.getppid() != self.pid:
                exit_code = ModuleCtx.Exit_Code_Parent_Gone

            # .. its signals, its hub and its control socket are its own ..
            else:
                set_process_name(ModuleCtx.Process_Name_Worker)
                self.reset_signals_in_child()
                self.hub.close_in_worker()
                self.reinit_hub_in_child()

                # .. it knows its slot and generation, and its publications to outgoing queues take the publish locks
                # of the region under the place of the worker ..
                set_process_slot(ctx.slot, ctx.generation)
                bind_outgoing(self.region, self.region.worker_place)

                # .. and it runs until it returns.
                self.worker_main(ctx)
                exit_code = ModuleCtx.Exit_Code_OK

        except BaseException:
            logger.exception('Worker terminated with an exception')

        finally:
            os._exit(exit_code)

# ################################################################################################################################

    def _spawn(self) -> 'None':
        """ Starts the next generation of the worker.
        """
        worker = self.worker

        # The new generation and a fresh heartbeat are in place before the worker exists ..
        self.worker_generation += 1
        write_heartbeat(self.region)
        self.worker_state = WorkerState.Starting
        worker_end = self.hub.open_slot(worker.slot)

        ctx = WorkerContext()
        ctx.slot       = worker.slot
        ctx.generation = self.worker_generation
        ctx.control_fd = worker_end.fileno()
        ctx.body_dir   = self.body_dir

        # .. the worker is forked ..
        pid = _fork()

        if pid == 0:
            self._run_worker(ctx)

        # .. and the arbiter records it.
        worker_end.close()

        worker.pid = pid
        worker.respawn_at = None
        worker.is_killed = False

        logger.info('Started worker, generation %s, PID %s', self.worker_generation, pid)

# ################################################################################################################################

    def get_respawn_delay(self, process:'WorkerSlot', now:'float') -> 'float':
        """ Records a termination of a process and returns how long the arbiter waits before it starts the next one.
        """
        window_start = now - self.config.failure_window
        failure_times:'floatlist' = []

        for failure_time in process.failure_times:
            if failure_time >= window_start:
                failure_times.append(failure_time)

        failure_times.append(now)
        process.failure_times = failure_times

        # Each termination within the window doubles the delay, up to its ceiling ..
        failure_count = len(failure_times)
        exponent = failure_count - 1
        multiplier = 2 ** exponent
        delay = self.config.respawn_delay_initial * multiplier
        delay = min(delay, self.config.respawn_delay_max)

        # .. and a process that terminates too often is reported and waits for the ceiling.
        if failure_count > self.config.failure_count_max:
            delay = self.config.respawn_delay_max
            logger.error('The %s terminated %s times within %ss, the next one starts after the maximum delay',
                process.label, failure_count, self.config.failure_window)

        out = delay
        return out

# ################################################################################################################################

    def _on_worker_exit(self, status:'int') -> 'None':
        """ Withdraws the places of a terminated worker in every queue and schedules its replacement.
        """
        worker = self.worker
        worker_place = self.region.worker_place

        # The places of the worker in the queues of the SQLite writes and in the queues of the keyed locks
        # are withdrawn before its replacement starts ..
        for queue in range(self.region.queue_count):
            self.region.queue_abandon(queue, worker_place)

        for entry in range(self.region.lock_capacity):
            self.region.lock_abandon(entry, worker_place)

        self.hub.close_slot(worker.slot)
        self.worker_state = WorkerState.Stopped
        self.log_rotator.on_process_exit(worker.slot)
        exit_code = os.waitstatus_to_exitcode(status)

        logger.info('Worker, PID %s, terminated with exit code %s', worker.pid, exit_code)
        worker.pid = 0

        # .. and a replacement is scheduled unless the server is stopping.
        if self.is_stopping:
            return

        now = monotonic()
        delay = self.get_respawn_delay(worker, now)
        worker.respawn_at = now + delay

# ################################################################################################################################

    def _reap(self, options:'int') -> 'None':
        """ Collects the worker if it terminated, waiting for it when options are 0.
        """
        if self.worker.pid:
            pid, status = _waitpid(self.worker.pid, options)

            if pid:
                self._on_worker_exit(status)

        # The config process is never waited for here, because on stop it runs until the worker is reaped
        if self.config_process:
            self.config_process.reap(os.WNOHANG)

# ################################################################################################################################

    def _check_heartbeat(self) -> 'None':
        """ Terminates the worker with SIGKILL if its heartbeat is older than the threshold of its state.
        """
        worker = self.worker

        if not worker.pid:
            return

        if worker.is_killed:
            return

        # A starting worker loads its services with its hub blocked, so it has the startup timeout,
        # counted from the heartbeat that the arbiter wrote when it forked the worker.
        if self.worker_state == WorkerState.Starting:
            threshold_seconds = self.config.startup_timeout
        else:
            threshold_seconds = self.config.heartbeat_threshold

        threshold_us = threshold_seconds * ModuleCtx.Microseconds_Per_Second
        age_us = now_us() - self.region.heartbeat()

        if age_us > threshold_us:
            age_seconds = age_us / ModuleCtx.Microseconds_Per_Second
            logger.error('Worker, PID %s, sent no heartbeat for %.1fs, terminating it', worker.pid, age_seconds)

            os.kill(worker.pid, signal.SIGKILL)
            worker.is_killed = True

# ################################################################################################################################

    def _can_spawn(self) -> 'bool':
        """ Says whether the worker may start, which it does once the config process, which commits the startup writes,
        is ready, or at once in an arbiter without a config process.
        """
        if self.config_process:
            out = self.config_process.is_ready
        else:
            out = True

        return out

# ################################################################################################################################

    def _respawn_due(self) -> 'None':
        now = monotonic()

        if self.config_process:
            self.config_process.respawn_due(now)

        if self.worker.respawn_at is None:
            return

        if not self._can_spawn():
            return

        if self.worker.respawn_at <= now:
            self._spawn()

# ################################################################################################################################

    def wait(self, timeout:'float') -> 'None':
        """ Serves the control channel until a signal, a stop request, the deadline of a query or the timeout.
        """
        poller = _poll()
        poller.register(self.wake_read, POLLIN)

        for fd, events in self.hub.get_poll_requests():
            poller.register(fd, events)

        # A pending query is answered at its deadline even when nothing else wakes the arbiter
        now = monotonic()
        deadline = self.hub.get_next_deadline()

        if deadline is not None:
            remaining = max(deadline - now, 0)
            timeout = min(timeout, remaining)

        timeout_ms = timeout * ModuleCtx.Milliseconds_Per_Second
        poll_events = poller.poll(timeout_ms)

        self.hub.handle_poll_events(poll_events)

        now = monotonic()
        self.hub.expire_queries(now)

        # Each signal wrote one byte, and all of them are handled by the step that follows
        try:
            while os.read(self.wake_read, ModuleCtx.Wake_Read_Size):
                pass
        except BlockingIOError:
            pass

# ################################################################################################################################

    def _stop(self) -> 'None':
        """ Sends a drain command to the worker and terminates it with SIGKILL if it remains after the grace period,
        then stops the config process.
        """
        worker = self.worker

        # The worker receives its drain command ..
        if worker.pid:
            self.worker_state = WorkerState.Draining
            self.hub.send_drain(worker.slot)

        now = monotonic()
        deadline = now + self.config.grace_period

        # .. it exits within the grace period ..
        while worker.pid:
            now = monotonic()
            remaining = deadline - now

            if remaining <= 0:
                break

            timeout = min(remaining, self.config.loop_interval)
            self.wait(timeout)
            self._reap(os.WNOHANG)

        # .. or it is terminated ..
        if worker.pid:
            logger.warning('Worker, PID %s, did not exit within %ss, terminating it', worker.pid, self.config.grace_period)
            os.kill(worker.pid, signal.SIGKILL)

        self._reap(0)

        # .. and the config process stops once the worker can no longer forward an invocation to it.
        if self.config_process:
            self.config_process.stop()

# ################################################################################################################################

    def run(self) -> 'int':
        """ Starts the processes, supervises them until a stop is requested, and returns the exit code of the arbiter.
        """
        set_process_name(ModuleCtx.Process_Name_Arbiter)
        self._install_signals()

        # The collector of a forked process never visits the objects loaded before the fork, so it writes none of their pages,
        # which remain shared with the arbiter ..
        _ = gc.collect()
        gc.freeze()

        # .. the collector, disabled while the server started, runs again in the arbiter and in every process it forks ..
        gc.enable()

        # .. the config process starts first, and the worker once it is ready ..
        if self.config_process:
            self.config_process.spawn()

        if self._can_spawn():
            self._spawn()
        else:
            self.worker.respawn_at = monotonic()

        # .. the processes are supervised ..
        while not self.is_stopping:
            self.wait(self.config.loop_interval)
            self._reap(os.WNOHANG)
            self._check_heartbeat()
            self._rotate_logs_due()

            if not self.is_stopping:
                self._respawn_due()

        # .. and drained when the server stops.
        self._stop()

        self.hub.close_all()
        rmtree(self.body_dir)

        out = ModuleCtx.Exit_Code_OK
        return out

# ################################################################################################################################
# ################################################################################################################################
