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
from zato.common.test.conftest_base_multi_cpu import enmasse_import, MultiCPUTestConfig, WorkerControl
from zato.common.test.config_multi_cpu_scheduler import SchedulerConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, list_

    floatlist = list_[float]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_scheduler.scheduler')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long a test observes the runs of a job, in seconds
    Observe_Period = 20.0

    # How long a test waits before it kills a worker, in seconds, so that runs are in progress when it does
    Kill_Delay = 5.0

    # How long the runs of a job are given to settle after a respawn or a change, in seconds
    Settle_Period = 5.0

    # The first slot whose worker a test kills is the last one, which runs no duties of its own
    Last_Slot_Offset = 1

    # How long a completion of a run takes to reach the scheduler after the run returned, at most, in seconds
    Completion_Latency = 0.5

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

def _in_window(entries:'anylist', start:'float', end:'float') -> 'anylist':
    """ The entries whose nominal fire time is within the window.
    """
    out:'anylist' = []

    for entry in entries:
        if start <= entry['nominal_ts'] <= end:
            out.append(entry)

    return out

# ################################################################################################################################

def _sorted_nominal(entries:'anylist') -> 'floatlist':
    out:'floatlist' = []

    for entry in entries:
        out.append(entry['nominal_ts'])

    out.sort()
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerAcrossWorkers(unittest.TestCase):
    """ Fire events are processed once each by the workers together, and the jobs keep their cadence
    across a termination of a worker and the reload that follows it.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)

# ################################################################################################################################

    def _assert_once_each_on_cadence(self, entries:'anylist', interval:'int') -> 'None':
        """ Each nominal fire time of the entries occurs once, and consecutive ones are one interval apart.
        """
        nominal = _sorted_nominal(entries)
        self.assertTrue(nominal, 'No runs in the window')

        for index in range(1, len(nominal)):
            previous = nominal[index - 1]
            current = nominal[index]
            self.assertEqual(current - previous, interval, f'Runs at {previous} and {current}')

# ################################################################################################################################

    def _assert_next_slot_after_each_run(self, end_entries:'anylist', interval:'int') -> 'None':
        """ Each run of a job that outlasts its interval is followed by the first slot after the run returned,
        because the scheduler skips the slots that a run in flight outlasted and no other one.
        """
        self.assertTrue(end_entries, 'No runs in the window')

        end_entries = sorted(end_entries, key=_nominal_key)

        for index in range(1, len(end_entries)):
            previous:'anydict' = end_entries[index - 1]
            current:'anydict' = end_entries[index]

            gap = current['nominal_ts'] - previous['nominal_ts']
            latest = previous['time'] + interval + ModuleCtx.Completion_Latency

            self.assertEqual(gap % interval, 0, f'Runs at {previous["nominal"]} and {current["nominal"]} off the slots')
            self.assertLessEqual(current['nominal_ts'], latest, f'Slot after {previous["nominal"]} skipped')

# ################################################################################################################################

    def _kill_and_wait(self) -> 'None':
        """ Kills the worker of the last slot and waits for its replacement.
        """
        _ = self.control.wait_for_all_ready()

        slot = MultiCPUTestConfig.worker_count - ModuleCtx.Last_Slot_Offset
        killed = self.control.kill(slot)
        logger.info('Killed slot %s -> %s', slot, killed)

        respawned = self.control.wait_for_respawn(slot, killed['generation'])
        logger.info('Respawned slot %s -> %s', slot, respawned)

# ################################################################################################################################

    def test_fires_are_processed_once_each_on_cadence(self) -> 'None':
        """ Each fire of a job runs once, the fires keep the interval of the job, and more than one worker runs them.
        """
        _ = self.control.wait_for_all_ready()

        window_start = time()
        sleep(ModuleCtx.Observe_Period)
        window_end = time() - ModuleCtx.Settle_Period

        entries = _read_entries(SchedulerConfig.Quick_Job, SchedulerConfig.Phase_Start)
        entries = _in_window(entries, window_start, window_end)

        self._assert_once_each_on_cadence(entries, SchedulerConfig.Interval_Seconds)

        slots = set()
        for entry in entries:
            slots.add(entry['slot'])

        self.assertGreater(len(slots), 1, f'Every run in slots {slots}')

# ################################################################################################################################

    def test_runs_of_a_killed_worker_complete_once(self) -> 'None':
        """ The runs that a killed worker had taken complete once each in its replacement, no fire is lost,
        and the run numbers continue across the reload that the termination causes.
        """
        _ = self.control.wait_for_all_ready()

        window_start = time()
        sleep(ModuleCtx.Kill_Delay)

        self._kill_and_wait()

        sleep(ModuleCtx.Settle_Period + SchedulerConfig.Slow_Run_Seconds)
        window_end = time() - ModuleCtx.Settle_Period - SchedulerConfig.Slow_Run_Seconds

        entries = _read_entries(SchedulerConfig.Slow_Job, SchedulerConfig.Phase_End)
        entries = _in_window(entries, window_start, window_end)

        # Each fire completes once, and no slot is lost other than those that a run in flight outlasted ..
        nominal = _sorted_nominal(entries)
        self.assertEqual(len(nominal), len(set(nominal)), f'A fire completed more than once in {nominal}')

        self._assert_next_slot_after_each_run(entries, SchedulerConfig.Interval_Seconds)

        # .. the run numbers rise with the fire times and never start again from the beginning.
        entries.sort(key=_nominal_key)

        for index in range(1, len(entries)):
            previous:'anydict' = entries[index - 1]
            current:'anydict' = entries[index]
            self.assertGreater(current['run'], previous['run'], f'Run {current["run"]} after run {previous["run"]}')

# ################################################################################################################################

    def test_job_change_during_a_reload(self) -> 'None':
        """ A change of the interval of a job made while a killed worker is replaced is in effect afterwards.
        """
        _ = self.control.wait_for_all_ready()

        slot = MultiCPUTestConfig.worker_count - ModuleCtx.Last_Slot_Offset
        killed = self.control.kill(slot)
        logger.info('Killed slot %s -> %s', slot, killed)

        enmasse_import({
            'scheduler': [{
                'name': SchedulerConfig.Changed_Job,
                'service': SchedulerConfig.Record_Service,
                'job_type': 'interval_based',
                'seconds': SchedulerConfig.Changed_Interval_Seconds,
                'is_active': True,
                'extra': json.dumps({'job': SchedulerConfig.Changed_Job, 'run_seconds': 0}),
            }],
        })

        respawned = self.control.wait_for_respawn(slot, killed['generation'])
        logger.info('Respawned slot %s -> %s', slot, respawned)

        window_start = time() + ModuleCtx.Settle_Period
        sleep(ModuleCtx.Settle_Period + ModuleCtx.Observe_Period)
        window_end = time()

        entries = _read_entries(SchedulerConfig.Changed_Job, SchedulerConfig.Phase_Start)
        entries = _in_window(entries, window_start, window_end)

        self._assert_once_each_on_cadence(entries, SchedulerConfig.Changed_Interval_Seconds)

# ################################################################################################################################
# ################################################################################################################################

def _nominal_key(entry:'anydict') -> 'float':
    out = entry['nominal_ts']
    return out

# ################################################################################################################################
# ################################################################################################################################
