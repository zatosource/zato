# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from pubsub_perf.config import Capacity_Scenario, Faults_Scenario, get_scenario_name
from pubsub_perf.progress import Progress
from pubsub_perf.runner import begin_measurement, new_prefix, run_scenario
from pubsub_perf.scenario import ScenarioRun, verify_and_report

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# How long the publishers of each test publish, in seconds
_capacity_duration = 30.0
_faults_duration   = 60.0

# How many times the worker is killed while the publishers publish
_worker_kills = 3

# ################################################################################################################################
# ################################################################################################################################

def test_publishers_to_subscribers(zato_server:'any_') -> 'None':
    """ Sixteen publishers publish to one topic as fast as the server accepts, and eight pull subscribers and eight
    push subscribers, each with a subscription of its own, receive every message. Each subscriber processes
    each message exactly once.
    """
    test_name = get_scenario_name('test_publishers_to_subscribers', Capacity_Scenario)

    prefix = new_prefix()
    run = ScenarioRun(Capacity_Scenario, prefix)
    progress = Progress(test_name)

    measurement = begin_measurement()
    timing = run_scenario(progress, run, _capacity_duration, 0)

    verify_and_report(measurement, test_name, run, timing, 0)

# ################################################################################################################################

def test_publishers_to_subscribers_under_worker_kills(zato_server:'any_') -> 'None':
    """ Eight publishers publish to one topic and four pull subscribers and four push subscribers, each with
    a subscription of its own, receive every message, while the worker of the server is killed three times.
    Each pull subscriber processes each message exactly once and each push subscriber receives each message.
    """
    test_name = get_scenario_name('test_publishers_to_subscribers_under_worker_kills', Faults_Scenario)

    prefix = new_prefix()
    run = ScenarioRun(Faults_Scenario, prefix)
    progress = Progress(test_name)

    measurement = begin_measurement()
    timing = run_scenario(progress, run, _faults_duration, _worker_kills)

    verify_and_report(measurement, test_name, run, timing, _worker_kills)

# ################################################################################################################################
# ################################################################################################################################
