# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The arbiter's supervision of the config process of a server. The config process commits every change of configuration
# and processes no messages. The arbiter forks it before the workers, which start once it reported ready, respawns it
# with the backoff of a slot, and after an abnormal termination asks every worker to load its configuration again
# once the replacement reported ready, because the terminated process may have committed a change whose event never left.

# stdlib
import os
import signal
from logging import getLogger
from time import monotonic

# gevent
from gevent.monkey import get_original

# Zato
from zato.common.worker_slot import ModuleCtx as WorkerSlotCtx, set_worker_generation, set_worker_slot
from zato.server.arbiter_config import ModuleCtx, new_worker_slot, WorkerContext
from zato.server.worker_liveness import set_parent_death_signal
from zato_server_core.zato_server_core import set_process_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_
    from zato.server.arbiter import Arbiter

    Arbiter = Arbiter
    callable_ = callable_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_fork    = get_original('os', 'fork')
_waitpid = get_original('os', 'waitpid')

# ################################################################################################################################
# ################################################################################################################################

class ConfigProcessCtx:

    # The name that ps and top list for the config process
    Process_Name = 'zato-config'

    # How the logs name the processes of the config process
    Label = 'config processes'

# ################################################################################################################################
# ################################################################################################################################

class ConfigSupervisor:
    """ Forks, respawns and stops the config process of one arbiter.
    """

    def __init__(self, arbiter:'Arbiter', main:'callable_') -> 'None':

        # The main function of the config process is called with its WorkerContext
        self.arbiter = arbiter
        self.main = main

        self.process = new_worker_slot(WorkerSlotCtx.Config_Slot, ConfigProcessCtx.Label)
        self.generation = 0

        # Whether the current config process reported ready, before which no worker starts
        self.is_ready = False

        # Whether the previous config process terminated abnormally, after which every worker loads its configuration again
        self.needs_reload = False

# ################################################################################################################################

    def _run(self, ctx:'WorkerContext') -> 'None':
        """ Runs in the forked config process and never returns.
        """
        arbiter = self.arbiter
        exit_code = ModuleCtx.Exit_Code_Worker_Error

        try:

            # The config process terminates with the arbiter, including an arbiter that terminated before this call ..
            set_parent_death_signal()

            if os.getppid() != arbiter.pid:
                exit_code = ModuleCtx.Exit_Code_Parent_Gone

            # .. its signals, its hub and its control socket are its own ..
            else:
                set_process_name(ConfigProcessCtx.Process_Name)
                arbiter.reset_signals_in_child()
                arbiter.hub.close_in_worker()

                if arbiter.writer:
                    arbiter.writer.listener.close()

                arbiter.reinit_hub_in_child()

                # .. its log records and audit events name the slot of the config process ..
                set_worker_slot(ctx.slot)
                set_worker_generation(ctx.generation)

                # .. and it runs until it returns.
                self.main(ctx)
                exit_code = ModuleCtx.Exit_Code_OK

        except BaseException:
            logger.exception('Config process terminated with an exception')

        finally:
            os._exit(exit_code)

# ################################################################################################################################

    def spawn(self) -> 'None':
        """ Starts the next config process.
        """
        arbiter = self.arbiter

        self.generation += 1
        self.is_ready = False

        process_end = arbiter.hub.open_slot(WorkerSlotCtx.Config_Slot)

        ctx = WorkerContext()
        ctx.slot       = WorkerSlotCtx.Config_Slot
        ctx.generation = self.generation
        ctx.control_fd = process_end.fileno()
        ctx.body_dir   = arbiter.body_dir
        ctx.cpu        = None

        ctx.writer_address  = None
        ctx.writer_deadline = arbiter.config.writer_deadline

        if arbiter.writer:
            ctx.writer_address = arbiter.writer.address

        pid = _fork()

        if pid == 0:
            self._run(ctx)

        process_end.close()

        self.process.pid = pid
        self.process.respawn_at = None
        self.process.is_killed = False

        logger.info('Started config process, generation %s, PID %s', self.generation, pid)

# ################################################################################################################################

    def on_ready(self) -> 'None':
        """ Records that the config process reported ready and asks every worker to load its configuration again
        if the previous config process terminated abnormally.
        """
        self.is_ready = True

        if self.needs_reload:
            self.needs_reload = False
            self.arbiter.hub.broadcast_reload()

# ################################################################################################################################

    def reap(self, options:'int') -> 'None':
        """ Collects a terminated config process and schedules its replacement, waiting for it when options are 0.
        """
        if not self.process.pid:
            return

        pid, status = _waitpid(self.process.pid, options)

        if not pid:
            return

        arbiter = self.arbiter
        region = arbiter.region
        config_place = region.config_place

        # The places of the config process in the writer queues and in the queues of the keyed locks
        # are withdrawn before its replacement starts ..
        for queue in range(region.queue_count):
            region.queue_abandon(queue, config_place)

        for entry in range(region.lock_capacity):
            region.lock_abandon(entry, config_place)

        # .. the invocations forwarded to it fail to their callers ..
        arbiter.hub.close_slot(WorkerSlotCtx.Config_Slot)
        arbiter.log_rotator.on_worker_exit(WorkerSlotCtx.Config_Slot)

        exit_code = os.waitstatus_to_exitcode(status)
        logger.info('Config process, PID %s, terminated with exit code %s', self.process.pid, exit_code)

        self.process.pid = 0
        self.is_ready = False

        if arbiter.is_stopping:
            return

        # .. its replacement is scheduled ..
        now = monotonic()
        delay = arbiter.get_respawn_delay(self.process, now)
        self.process.respawn_at = now + delay

        # .. and a config process that terminated abnormally may have committed a change without sending its event.
        if exit_code != ModuleCtx.Exit_Code_OK:
            self.needs_reload = True

# ################################################################################################################################

    def respawn_due(self, now:'float') -> 'None':
        if self.process.respawn_at is not None:
            if self.process.respawn_at <= now:
                self.spawn()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Drains the config process after the workers, which may forward invocations to it until they exit,
        and terminates it with SIGKILL if it remains after the grace period.
        """
        if not self.process.pid:
            return

        arbiter = self.arbiter
        arbiter.hub.send_drain(WorkerSlotCtx.Config_Slot)

        deadline = monotonic() + arbiter.config.grace_period

        while self.process.pid:
            remaining = deadline - monotonic()

            if remaining <= 0:
                logger.warning('Config process, PID %s, did not exit within %ss, terminating it',
                    self.process.pid, arbiter.config.grace_period)
                os.kill(self.process.pid, signal.SIGKILL)
                self.reap(0)
                break

            timeout = min(remaining, arbiter.config.loop_interval)
            arbiter.wait(timeout)
            self.reap(os.WNOHANG)

# ################################################################################################################################
# ################################################################################################################################
