# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import unittest
from datetime import datetime
from time import sleep, time

# Zato
from live_environment.redis_process import SchedulerRedis
from zato.common.test.conftest_base_multi_cpu import MultiCPUTestConfig, WorkerControl
from zato.common.test.config_multi_cpu_scheduler import SchedulerConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, list_

    floatlist = list_[float]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_scheduler.redis_restart')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the test waits for a run of the slow job in the worker that it kills, and how often it checks, in seconds
    Slow_Run_Wait_Timeout = 60.0
    Slow_Run_Poll_Interval = 0.2

    # How long Redis stays stopped after the replacement worker is ready, in seconds
    Outage_Period = 5.0

    # How long the jobs are given to settle after Redis starts again, and how long the test observes them, in seconds
    Settle_Period = 5.0
    Observe_Period = 15.0

    # The worker that the test kills is the one of the last slot, which runs no duties of its own
    Last_Slot_Offset = 1

# ################################################################################################################################
# ################################################################################################################################

def _read_entries(job:'str', phase:'str') -> 'anylist':
    """ The entries of one phase of the runs of a job, each with its nominal fire time as a timestamp.
    """
    out:'anylist' = []

    with open(os.environ[SchedulerConfig.Fire_Log_Env]) as fire_log:
        for line in fire_log.read().splitlines():
            entry = json.loads(line)

            if entry['job'] == job and entry['phase'] == phase:
                entry['nominal_ts'] = datetime.fromisoformat(entry['nominal']).timestamp()
                out.append(entry)

    return out

# ################################################################################################################################

def _get_nominal_set(entries:'anylist') -> 'set[float]':
    out:'set[float]' = set()

    for entry in entries:
        out.add(entry['nominal_ts'])

    return out

# ################################################################################################################################

def _wait_for_slow_run(slot:'int') -> 'None':
    """ Waits until a run of the slow job is in progress in the worker of a slot, which runs one at a time across all workers.
    """
    deadline = time() + ModuleCtx.Slow_Run_Wait_Timeout

    while time() < deadline:

        # The workers create the file with the first run that they record
        if not os.path.exists(os.environ[SchedulerConfig.Fire_Log_Env]):
            sleep(ModuleCtx.Slow_Run_Poll_Interval)
            continue

        ended = _get_nominal_set(_read_entries(SchedulerConfig.Slow_Job, SchedulerConfig.Phase_End))

        for entry in _read_entries(SchedulerConfig.Slow_Job, SchedulerConfig.Phase_Start):
            if entry['slot'] == slot and entry['nominal_ts'] not in ended:
                return

        sleep(ModuleCtx.Slow_Run_Poll_Interval)

    raise Exception(f'No run of the slow job started in slot {slot} within {ModuleCtx.Slow_Run_Wait_Timeout}s')

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerRedisRestart(unittest.TestCase):
    """ A restart of the Redis of the scheduler, while runs are in progress and while a killed worker is replaced,
    is followed by every fire event being processed once, including the entries that the killed worker had read.
    """

    def test_fires_after_a_restart_of_redis(self) -> 'None':

        control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        _ = control.wait_for_all_ready()

        # The worker is killed while it runs a fire of the slow job that it read and did not acknowledge ..
        slot = MultiCPUTestConfig.worker_count - ModuleCtx.Last_Slot_Offset
        _wait_for_slow_run(slot)

        killed = control.kill(slot)
        kill_time = time()
        logger.info('Killed slot %s -> %s', slot, killed)

        # .. Redis stops before its replacement starts, so the replacement starts without Redis ..
        SchedulerRedis.process.stop()

        respawned = control.wait_for_respawn(slot, killed['generation'])
        logger.info('Respawned slot %s -> %s', slot, respawned)

        sleep(ModuleCtx.Outage_Period)

        # .. and Redis starts again in its directory, with the streams, groups and pending entries it had.
        SchedulerRedis.process.start()
        recovery_time = time()
        logger.info('Redis started again')

        sleep(ModuleCtx.Settle_Period + ModuleCtx.Observe_Period + SchedulerConfig.Slow_Run_Seconds)

        # Each run of the slow job that the killed worker began and did not finish completes after the recovery ..
        slow_starts = _read_entries(SchedulerConfig.Slow_Job, SchedulerConfig.Phase_Start)
        slow_ends = _read_entries(SchedulerConfig.Slow_Job, SchedulerConfig.Phase_End)

        ended_before_kill:'set[float]' = set()
        for entry in slow_ends:
            if entry['time'] < kill_time:
                ended_before_kill.add(entry['nominal_ts'])

        interrupted:'set[float]' = set()
        for entry in slow_starts:
            if entry['slot'] == slot and entry['time'] < kill_time:
                if entry['nominal_ts'] not in ended_before_kill:
                    interrupted.add(entry['nominal_ts'])

        self.assertTrue(interrupted, f'No run of slot {slot} was in progress when it was killed')

        completed = _get_nominal_set(slow_ends)
        not_completed = interrupted - completed
        self.assertEqual(not_completed, set(), 'Interrupted runs that never completed')

        # .. no fire of either job completes more than once ..
        for job in (SchedulerConfig.Slow_Job, SchedulerConfig.Quick_Job):
            seen:'set[float]' = set()

            for entry in _read_entries(job, SchedulerConfig.Phase_End):
                self.assertNotIn(entry['nominal_ts'], seen, f'Fire {entry["nominal"]} of {job} completed twice')
                seen.add(entry['nominal_ts'])

        # .. and after the recovery, every fire of the quick job runs once, one interval after the previous one.
        window_start = recovery_time + ModuleCtx.Settle_Period
        window_end = window_start + ModuleCtx.Observe_Period

        nominal:'floatlist' = []
        for entry in _read_entries(SchedulerConfig.Quick_Job, SchedulerConfig.Phase_Start):
            if window_start <= entry['nominal_ts'] <= window_end:
                nominal.append(entry['nominal_ts'])

        nominal.sort()
        self.assertTrue(nominal, 'No runs of the quick job after the recovery')

        for index in range(1, len(nominal)):
            previous = nominal[index - 1]
            current = nominal[index]
            self.assertEqual(current - previous, SchedulerConfig.Interval_Seconds, f'Runs at {previous} and {current}')

# ################################################################################################################################
# ################################################################################################################################
