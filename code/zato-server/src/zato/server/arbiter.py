# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The arbiter of a server with several worker processes. It forks one worker into each slot of the shared region,
# respawns a worker that terminated, terminates a worker whose heartbeat stopped, relays the control channel
# between the workers, and drains the workers on shutdown. On SQLite, it also forks the pub/sub writer process,
# holds its listening socket across its restarts and restarts it when it terminates.

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
from zato.common.hl7.mllp.region import bind_mllp
from zato.common.pubsub.sql.config import ModuleCtx as PubSubConfigCtx
from zato.common.pubsub.writer_process.server import new_listening_socket
from zato.common.util.log_rotation import get_worker_handlers, LogRotator, watch_worker_handlers, WorkerFileHandler
from zato.common.worker_count import get_affinity, get_cgroup_cpu_limit, get_worker_cpus
from zato.common.worker_slot import set_worker_generation, set_worker_slot
from zato.server.arbiter_config import ModuleCtx, new_worker_slot, WorkerContext, WriterProcess
from zato.server.control.hub import ControlHub
from zato.server.metrics_region import bind_metrics
from zato.server.outgoing_region import bind_outgoing
from zato.server.process_instance import bind_process_instance
from zato.server.worker_liveness import now_us, set_parent_death_signal, write_heartbeat
from zato_ipc_core.zato_ipc_core import STATE_DRAINING, STATE_READY, STATE_STARTING, STATE_STOPPED
from zato_server_core.zato_server_core import set_process_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_, dict_, list_
    from zato.server.arbiter_config import ArbiterConfig, WorkerSlot
    from zato_ipc_core.zato_ipc_core import SharedRegion

    ArbiterConfig = ArbiterConfig
    callable_ = callable_
    SharedRegion = SharedRegion
    WorkerSlot = WorkerSlot

    floatlist     = list_[float]
    workerlist    = list_['WorkerSlot']
    intworkerdict = dict_[int, 'WorkerSlot']

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
    """ Forks and supervises the worker processes of one server, one in each slot of the shared region.
    """

    def __init__(
        self,
        region:'SharedRegion',
        worker_main:'callable_',
        config:'ArbiterConfig',
        writer_main:'callable_ | None' = None,
        ) -> 'None':

        # The worker is called with its WorkerContext, and the writer, which a server with one worker
        # or with PostgreSQL does not run, with the descriptor of its listening socket
        self.region      = region
        self.worker_main = worker_main
        self.config      = config
        self.writer_main = writer_main

        self.pid = os.getpid()
        self.is_stopping = False

        self.workers:'workerlist' = []
        self.pid_to_worker:'intworkerdict' = {}

        for slot in range(region.slot_count):
            worker = new_worker_slot(slot, f'workers of slot {slot}')
            self.workers.append(worker)

        # With as many workers as CPUs, each worker runs on the CPU at the position of its slot
        cpus = get_affinity()
        cpu_limit = get_cgroup_cpu_limit(config.cpu_max_path)
        self.worker_cpus = get_worker_cpus(region.slot_count, cpus, cpu_limit)

        # Signals and stop requests write to this pipe, so that the wait of the main loop returns at once
        self.wake_read, self.wake_write = os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC)

        self.body_dir = mkdtemp(prefix=ModuleCtx.Body_Dir_Prefix, dir=config.tmp_dir)
        self.hub = ControlHub(self.body_dir, region.slot_count, config.query_timeout, self._on_ready, self._on_logs_reopened,
            self._on_replaced)

        # The arbiter renames the log files that every process appends to, through the handlers that it configured
        # before the fork and through a handler of each file of zato_server_core that it does not write to itself,
        # and the first check follows one interval after the start
        handlers = get_worker_handlers()

        for path in config.native_log_files:
            handler = WorkerFileHandler(path, maxBytes=config.native_log_max_bytes, backupCount=config.native_log_backup_count)
            handlers.append(handler)

        self.log_rotator = LogRotator(handlers, self.hub.broadcast_reopen_logs)
        self.log_check_at = monotonic() + config.log_check_interval

        # The listening socket of the writer exists from before the first fork until the arbiter returns,
        # so that the connections of the workers queue on it while the writer restarts.
        self.writer:'WriterProcess | None' = None

        if writer_main:
            self.writer = WriterProcess()
            self.writer.main = writer_main
            self.writer.socket_dir = mkdtemp(prefix=ModuleCtx.Writer_Dir_Prefix, dir=config.socket_dir)
            self.writer.address = os.path.join(self.writer.socket_dir, ModuleCtx.Writer_Socket_Name)
            self.writer.listener = new_listening_socket(self.writer.address)
            self.writer.process = new_worker_slot(ModuleCtx.Writer_Slot, 'pub/sub writer processes')

# ################################################################################################################################

    def request_stop(self) -> 'None':
        """ Asks the main loop to drain the workers and return.
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

    def _reset_signals_in_worker(self) -> 'None':
        _ = signal.set_wakeup_fd(-1)
        _ = _signal(signal.SIGCHLD, signal.SIG_DFL)
        _ = _signal(signal.SIGTERM, signal.SIG_DFL)

        os.close(self.wake_read)
        os.close(self.wake_write)

# ################################################################################################################################

    def _on_ready(self, slot:'int') -> 'None':
        """ Records that the worker of a slot reported ready, unless the slot is draining already.
        """
        state = self.region.slot_state(slot)

        if state == STATE_STARTING:
            self.region.set_slot_state(slot, STATE_READY)

# ################################################################################################################################

    def _on_logs_reopened(self, slot:'int', rotation_id:'int') -> 'None':
        self.log_rotator.on_reopened(slot, rotation_id)

# ################################################################################################################################

    def _on_replaced(self, slot:'int') -> 'None':
        """ Drains every worker once one of them learned that another server took over the pub/sub database,
        because the generation that the arbiter raised is no longer current for any worker of this server.
        """
        logger.warning('Worker of slot %s reported that another server took over the pub/sub database, stopping', slot)
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
                set_process_name(ModuleCtx.Process_Name_Worker.format(ctx.slot))
                self._reset_signals_in_worker()
                self.hub.close_in_worker()

                if self.writer:
                    self.writer.listener.close()

                gevent.reinit()

                # .. it runs on the CPU of its slot if the workers are pinned ..
                if ctx.cpu is not None:
                    os.sched_setaffinity(0, {ctx.cpu})

                # .. its log records and audit events name its slot, its metrics go to the row of its slot,
                # its MLLP channels and connections use the region, the records it writes carry its process instance,
                # and the depths and publish locks of its outgoing queues are those of the region ..
                set_worker_slot(ctx.slot)
                set_worker_generation(ctx.generation)
                bind_metrics(self.region, ctx.slot)
                bind_mllp(self.region, ctx.slot, ctx.generation)
                bind_process_instance(self.region, ctx.slot, ctx.generation)
                bind_outgoing(self.region, ctx.slot)

                # .. and it runs until it returns.
                self.worker_main(ctx)
                exit_code = ModuleCtx.Exit_Code_OK

        except BaseException:
            logger.exception('Worker of slot %s terminated with an exception', ctx.slot)

        finally:
            os._exit(exit_code)

# ################################################################################################################################

    def _run_writer(self, writer:'WriterProcess') -> 'None':
        """ Runs in the forked writer process and never returns.
        """
        exit_code = ModuleCtx.Exit_Code_Worker_Error

        try:

            # The writer terminates with the arbiter, including an arbiter that terminated before this call ..
            set_parent_death_signal()

            if os.getppid() != self.pid:
                exit_code = ModuleCtx.Exit_Code_Parent_Gone

            # .. it holds no control socket, and it ignores the SIGTERM that killpg delivers to the process group,
            # because the draining workers continue to send it items until the arbiter stops it after them ..
            else:
                set_process_name(ModuleCtx.Process_Name_Writer)
                self._reset_signals_in_worker()
                _ = _signal(signal.SIGTERM, signal.SIG_IGN)
                self.hub.close_in_worker()
                gevent.reinit()

                # .. it receives no command to reopen its log files, so its handlers follow the renames by themselves ..
                watch_worker_handlers()

                # .. and it serves the listening socket until it is terminated.
                listen_fd = writer.listener.fileno()
                writer.main(listen_fd)
                exit_code = ModuleCtx.Exit_Code_OK

        except BaseException:
            logger.exception('Pub/sub writer process terminated with an exception')

        finally:
            os._exit(exit_code)

# ################################################################################################################################

    def _spawn_writer(self, writer:'WriterProcess') -> 'None':
        """ Starts the next pub/sub writer process on the listening socket that the arbiter holds.
        """
        pid = _fork()

        if pid == 0:
            self._run_writer(writer)

        writer.process.pid = pid
        writer.process.respawn_at = None
        writer.process.is_killed = False

        logger.info('Started pub/sub writer process, PID %s', pid)

# ################################################################################################################################

    def _spawn(self, worker:'WorkerSlot') -> 'None':
        """ Starts the next generation of the worker of a slot.
        """
        slot = worker.slot

        # The new generation and a fresh heartbeat are in the slot before the worker exists ..
        generation = self.region.next_slot_generation(slot)
        write_heartbeat(self.region, slot)
        self.region.set_slot_state(slot, STATE_STARTING)
        worker_end = self.hub.open_slot(slot)

        ctx = WorkerContext()
        ctx.slot       = slot
        ctx.generation = generation
        ctx.control_fd = worker_end.fileno()
        ctx.body_dir   = self.body_dir

        ctx.writer_address  = None
        ctx.writer_deadline = self.config.writer_deadline

        if self.writer:
            ctx.writer_address = self.writer.address

        if self.worker_cpus:
            ctx.cpu = self.worker_cpus[slot]
        else:
            ctx.cpu = None

        # .. the worker is forked ..
        pid = _fork()

        if pid == 0:
            self._run_worker(ctx)

        # .. and the arbiter records it.
        worker_end.close()
        self.region.set_slot_pid(slot, pid)

        worker.pid = pid
        worker.respawn_at = None
        worker.is_killed = False
        self.pid_to_worker[pid] = worker

        logger.info('Started worker of slot %s, generation %s, PID %s', slot, generation, pid)

# ################################################################################################################################

    def _get_respawn_delay(self, worker:'WorkerSlot', now:'float') -> 'float':
        """ Records a termination of the worker of a slot and returns how long the slot waits for its next worker.
        """
        window_start = now - self.config.failure_window
        failure_times:'floatlist' = []

        for failure_time in worker.failure_times:
            if failure_time >= window_start:
                failure_times.append(failure_time)

        failure_times.append(now)
        worker.failure_times = failure_times

        # Each termination within the window doubles the delay, up to its ceiling ..
        failure_count = len(failure_times)
        exponent = failure_count - 1
        multiplier = 2 ** exponent
        delay = self.config.respawn_delay_initial * multiplier
        delay = min(delay, self.config.respawn_delay_max)

        # .. and a slot that terminates too often is reported and waits for the ceiling.
        if failure_count > self.config.failure_count_max:
            delay = self.config.respawn_delay_max
            logger.error('The %s terminated %s times within %ss, the next one starts after the maximum delay',
                worker.label, failure_count, self.config.failure_window)

        out = delay
        return out

# ################################################################################################################################

    def _on_worker_exit(self, worker:'WorkerSlot', status:'int') -> 'None':
        """ Withdraws the places of a terminated worker in every queue and schedules its replacement.
        """
        slot = worker.slot
        _ = self.pid_to_worker.pop(worker.pid)

        # The places of the worker in the writer queues and in the queues of the keyed locks
        # are withdrawn before any replacement starts ..
        for queue in range(self.region.queue_count):
            self.region.queue_abandon(queue, slot)

        for entry in range(self.region.lock_capacity):
            self.region.lock_abandon(entry, slot)

        self.hub.close_slot(slot)
        self.region.set_slot_state(slot, STATE_STOPPED)
        self.log_rotator.on_worker_exit(slot)
        exit_code = os.waitstatus_to_exitcode(status)

        logger.info('Worker of slot %s, PID %s, terminated with exit code %s', slot, worker.pid, exit_code)
        worker.pid = 0

        # .. a replacement is scheduled unless the server is stopping ..
        if self.is_stopping:
            return

        now = monotonic()
        delay = self._get_respawn_delay(worker, now)
        worker.respawn_at = now + delay

        # .. and a worker that terminated abnormally may have committed a change without sending its event,
        # so every other worker reads its configuration again.
        if exit_code != ModuleCtx.Exit_Code_OK:
            self.hub.broadcast_reload()

# ################################################################################################################################

    def _reap(self, options:'int') -> 'None':
        """ Collects the workers that terminated, waiting for each when options are 0.
        """
        for worker in self.workers:
            if not worker.pid:
                continue

            pid, status = _waitpid(worker.pid, options)

            if pid:
                self._on_worker_exit(worker, status)

        # The writer is never waited for here, because on stop it runs until the workers are reaped
        if self.writer:
            self._reap_writer(self.writer, os.WNOHANG)

# ################################################################################################################################

    def _reap_writer(self, writer:'WriterProcess', options:'int') -> 'None':
        """ Collects a terminated writer and schedules its replacement, waiting for it when options are 0.
        """
        if not writer.process.pid:
            return

        pid, status = _waitpid(writer.process.pid, options)

        if not pid:
            return

        exit_code = os.waitstatus_to_exitcode(status)
        logger.info('Pub/sub writer process, PID %s, terminated with exit code %s', writer.process.pid, exit_code)

        writer.process.pid = 0

        # The place of the writer in the writer queues is withdrawn before its replacement starts
        writer_place = self.region.writer_place

        for queue in range(self.region.queue_count):
            self.region.queue_abandon(queue, writer_place)

        # The workers resend their unanswered items once the replacement accepts their connections
        if not self.is_stopping:
            now = monotonic()
            delay = self._get_respawn_delay(writer.process, now)
            writer.process.respawn_at = now + delay

# ################################################################################################################################

    def _check_heartbeats(self) -> 'None':
        """ Terminates with SIGKILL each worker whose heartbeat is older than the threshold of the state of its slot.
        """
        now = now_us()
        heartbeat_threshold_us = self.config.heartbeat_threshold * ModuleCtx.Microseconds_Per_Second
        startup_timeout_us = self.config.startup_timeout * ModuleCtx.Microseconds_Per_Second

        for worker in self.workers:
            if not worker.pid:
                continue

            if worker.is_killed:
                continue

            # A starting worker loads its services with its hub blocked, so it has the startup timeout,
            # counted from the heartbeat that the arbiter wrote when it forked the worker.
            state = self.region.slot_state(worker.slot)

            if state == STATE_STARTING:
                threshold_us = startup_timeout_us
            else:
                threshold_us = heartbeat_threshold_us

            heartbeat = self.region.slot_heartbeat(worker.slot)
            age_us = now - heartbeat

            if age_us > threshold_us:
                age_seconds = age_us / ModuleCtx.Microseconds_Per_Second
                logger.error('Worker of slot %s, PID %s, sent no heartbeat for %.1fs, terminating it',
                    worker.slot, worker.pid, age_seconds)

                os.kill(worker.pid, signal.SIGKILL)
                worker.is_killed = True

# ################################################################################################################################

    def _respawn_due(self) -> 'None':
        now = monotonic()

        # The worker of the first slot commits the startup writes, which every other worker reads,
        # so the other slots start only while it is ready
        first_slot_state = self.region.slot_state(ModuleCtx.First_Slot)
        is_first_slot_ready = first_slot_state == STATE_READY

        for worker in self.workers:
            if worker.respawn_at is None:
                continue

            if worker.slot != ModuleCtx.First_Slot and not is_first_slot_ready:
                continue

            if worker.respawn_at <= now:
                self._spawn(worker)

        if self.writer:
            if self.writer.process.respawn_at is not None:
                if self.writer.process.respawn_at <= now:
                    self._spawn_writer(self.writer)

# ################################################################################################################################

    def _wait(self, timeout:'float') -> 'None':
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

    def _get_live_workers(self) -> 'workerlist':
        out:'workerlist' = []

        for worker in self.workers:
            if worker.pid:
                out.append(worker)

        return out

# ################################################################################################################################

    def _stop(self) -> 'None':
        """ Sends a drain command to every worker and terminates with SIGKILL those that remain after the grace period.
        """
        # Each worker receives its drain command ..
        for worker in self._get_live_workers():
            self.region.set_slot_state(worker.slot, STATE_DRAINING)
            self.hub.send_drain(worker.slot)

        now = monotonic()
        deadline = now + self.config.grace_period

        # .. the workers exit within the grace period ..
        while self._get_live_workers():
            now = monotonic()
            remaining = deadline - now

            if remaining <= 0:
                break

            timeout = min(remaining, self.config.loop_interval)
            self._wait(timeout)
            self._reap(os.WNOHANG)

        # .. any that did not is terminated ..
        for worker in self._get_live_workers():
            logger.warning('Worker of slot %s, PID %s, did not exit within %ss, terminating it',
                worker.slot, worker.pid, self.config.grace_period)
            os.kill(worker.pid, signal.SIGKILL)

        self._reap(0)

        # .. and the writer stops once no worker can send it an item.
        if self.writer:
            self._stop_writer(self.writer)

# ################################################################################################################################

    def _stop_writer(self, writer:'WriterProcess') -> 'None':
        """ Terminates the writer with SIGKILL, which rolls back a commit that is in progress, and removes its listening socket.
        """
        if writer.process.pid:
            os.kill(writer.process.pid, signal.SIGKILL)
            self._reap_writer(writer, 0)

        writer.listener.close()
        os.remove(writer.address)
        os.rmdir(writer.socket_dir)

# ################################################################################################################################

    def run(self) -> 'int':
        """ Starts the workers, supervises them until a stop is requested, and returns the exit code of the arbiter.
        """
        set_process_name(ModuleCtx.Process_Name_Arbiter)
        self._install_signals()

        # The collector of a worker never visits the objects loaded before the fork, so it writes none of their pages,
        # which remain shared among the workers ..
        _ = gc.collect()
        gc.freeze()

        # .. a server with a writer keeps the traces of delivered messages for the grace period, which the workers
        # and the writer inherit, so that a resent publication finds the row of its message ..
        if self.writer:
            os.environ[PubSubConfigCtx.Env_Trace_Grace_Seconds] = str(self.config.trace_grace_seconds)
            self._spawn_writer(self.writer)

        # .. the first slot receives its first worker at once, and every other slot once the first one is ready ..
        now = monotonic()

        for worker in self.workers:
            if worker.slot == ModuleCtx.First_Slot:
                self._spawn(worker)
            else:
                worker.respawn_at = now

        # .. the workers are supervised ..
        while not self.is_stopping:
            self._wait(self.config.loop_interval)
            self._reap(os.WNOHANG)
            self._check_heartbeats()
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
