# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from pubsub_perf.config import get_scenario_name, Level_Scenarios
from pubsub_perf.progress import Progress
from pubsub_perf.runner import begin_measurement, new_prefix, run_scenario
from pubsub_perf.scenario import ScenarioRun, verify_and_report
# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# How long the publishers of each level publish, in seconds
_level_duration = 20.0

# ################################################################################################################################
# ################################################################################################################################

def test_concurrency_levels(zato_server:'any_') -> 'None':
    """ Rising numbers of publishers publish to a topic of their own, with as many subscribers, each with
    a subscription of its own, receiving every message. At each level each subscriber processes each message
    exactly once.
    """
    test_name = 'test_concurrency_levels'

    for scenario in Level_Scenarios:

        level_name = get_scenario_name(test_name, scenario)

        prefix = new_prefix()
        run = ScenarioRun(scenario, prefix)
        progress = Progress(level_name)

        measurement = begin_measurement()
        timing = run_scenario(progress, run, _level_duration, 0)

        verify_and_report(measurement, level_name, run, timing, 0)

# ################################################################################################################################
# ################################################################################################################################
