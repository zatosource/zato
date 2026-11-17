# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from pubsub_perf.config import Capacity_Scenario, Faults_Scenario
from pubsub_perf.progress import PerfReport, Progress
from pubsub_perf.runner import new_prefix, run_scenario
from pubsub_perf.scenario import report_and_verify, ScenarioRun

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# How long the publishers of each test publish, in seconds
_capacity_duration = 15.0
_faults_duration   = 15.0

# How many times the worker is killed while the publishers publish
_worker_kills = 3

# ################################################################################################################################
# ################################################################################################################################

def test_publishers_to_subscribers(zato_server:'any_') -> 'None':
    """ Sixteen publishers publish to one topic as fast as the server accepts, and sixteen subscribers, each with
    a subscription of its own, receive every message. Each subscriber processes each message exactly once.
    """
    test_name = 'test_publishers_to_subscribers'

    prefix = new_prefix()
    run = ScenarioRun(Capacity_Scenario, prefix)
    progress = Progress(test_name)

    timing = run_scenario(progress, run, _capacity_duration, 0)

    report = PerfReport(test_name)
    report_and_verify(report, run, timing, progress)

# ################################################################################################################################

def test_publishers_to_subscribers_under_worker_kills(zato_server:'any_') -> 'None':
    """ Eight publishers publish to one topic and eight subscribers, each with a subscription of its own, receive
    every message, while the worker of the server is killed three times. Each subscriber processes each message
    exactly once.
    """
    test_name = 'test_publishers_to_subscribers_under_worker_kills'

    prefix = new_prefix()
    run = ScenarioRun(Faults_Scenario, prefix)
    progress = Progress(test_name)

    timing = run_scenario(progress, run, _faults_duration, _worker_kills)

    report = PerfReport(test_name)
    report.add_value('Worker kills', f'{_worker_kills}')
    report_and_verify(report, run, timing, progress)

# ################################################################################################################################
# ################################################################################################################################
