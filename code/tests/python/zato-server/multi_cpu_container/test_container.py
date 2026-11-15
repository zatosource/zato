# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import unittest
from uuid import uuid4

# local
from _processes import inspect, wait_for_workers
from local_docker import run_command
from zato_container import remove_container, start_container, wait_until_started

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strintdict, strtuple

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_container.container')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Container_Prefix = 'zato-test-multi-cpu-'

    # The CPU limit of the container whose worker count derives from its cgroup
    CPU_Limit = 2

    Exit_Code_OK = '0'
    Restart_Count_None = '0'

    # The worker whose process a test kills
    Killed_Worker = 'zato-worker-0'

    # How long docker stop waits before it kills the container, in seconds, which is the default of Docker
    Stop_Timeout = 10

# ################################################################################################################################
# ################################################################################################################################

class TestMultiCPUContainer(unittest.TestCase):
    """ The workers of a server in a container follow the limits of the container, the container stops gracefully,
    and a killed worker is replaced within the running container.
    """

    def _start(self, run_options:'strtuple') -> 'str':
        """ Starts a container of its own for the test and removes it when the test ends.
        """
        container_name = ModuleCtx.Container_Prefix + uuid4().hex[:8]

        start_container(container_name, {}, run_options)
        self.addCleanup(remove_container, container_name)

        wait_until_started(container_name)

        out = container_name
        return out

# ################################################################################################################################

    def _wait_for_count(self, container_name:'str', count:'int') -> 'strintdict':

        def _has_count(workers:'strintdict') -> 'bool':
            out = len(workers) == count
            return out

        out = wait_for_workers(container_name, _has_count, f'{count} workers')
        return out

# ################################################################################################################################

    def test_worker_count_from_cgroup_limit(self) -> 'None':
        """ A container limited to two CPUs runs two workers.
        """
        container_name = self._start(('--cpus', str(ModuleCtx.CPU_Limit)))
        workers = self._wait_for_count(container_name, ModuleCtx.CPU_Limit)

        logger.info('Workers with a limit of %s CPUs -> %s', ModuleCtx.CPU_Limit, workers)

# ################################################################################################################################

    def test_worker_count_without_limit(self) -> 'None':
        """ A container without a CPU limit runs a worker for each CPU that it may run on.
        """
        container_name = self._start(())
        cpu_count = len(os.sched_getaffinity(0))
        workers = self._wait_for_count(container_name, cpu_count)

        logger.info('Workers without a limit -> %s', workers)

# ################################################################################################################################

    def test_docker_stop_is_graceful(self) -> 'None':
        """ docker stop drains the server within the grace period of Docker, and the container exits with status 0.
        """
        container_name = self._start(('--cpus', str(ModuleCtx.CPU_Limit)))
        _ = self._wait_for_count(container_name, ModuleCtx.CPU_Limit)

        _ = run_command(['docker', 'stop', '--time', str(ModuleCtx.Stop_Timeout), container_name])

        self.assertEqual(inspect(container_name, '{{.State.ExitCode}}'), ModuleCtx.Exit_Code_OK)

# ################################################################################################################################

    def test_killed_worker_is_replaced_in_the_container(self) -> 'None':
        """ SIGKILL of a worker through docker exec results in a new worker, and the container itself is not restarted.
        """
        container_name = self._start(('--cpus', str(ModuleCtx.CPU_Limit)))
        workers = self._wait_for_count(container_name, ModuleCtx.CPU_Limit)

        started_at = inspect(container_name, '{{.State.StartedAt}}')
        killed_pid = workers[ModuleCtx.Killed_Worker]

        _ = run_command(['docker', 'exec', container_name, 'kill', '-9', str(killed_pid)])

        def _is_replaced(current:'strintdict') -> 'bool':
            if ModuleCtx.Killed_Worker not in current:
                return False
            out = current[ModuleCtx.Killed_Worker] != killed_pid
            return out

        replaced = wait_for_workers(container_name, _is_replaced, f'a replacement of {ModuleCtx.Killed_Worker}')
        logger.info('Worker %s replaced -> %s', killed_pid, replaced)

        self.assertEqual(inspect(container_name, '{{.State.StartedAt}}'), started_at)
        self.assertEqual(inspect(container_name, '{{.RestartCount}}'), ModuleCtx.Restart_Count_None)

# ################################################################################################################################
# ################################################################################################################################
