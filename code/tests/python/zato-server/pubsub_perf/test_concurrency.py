# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from pubsub_perf.config import get_scenario_name, Level_Scenarios
from pubsub_perf.progress import Progress
from pubsub_perf.runner import begin_measurement, new_prefix, run_scenario
from pubsub_perf.scenario import ScenarioRun, verify_and_report
# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_perf.config import Scenario
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# How long the publishers of each level publish, in seconds
_level_duration = 20.0

# Each level is a test of its own, selected by the name of its topic, e.g. -k perf.level.32
_level_ids = [scenario.topic_name for scenario in Level_Scenarios]

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('scenario', Level_Scenarios, ids=_level_ids)
def test_concurrency_levels(zato_server:'any_', scenario:'Scenario') -> 'None':
    """ Rising numbers of publishers publish to a topic of their own, with as many subscribers, each with
    a subscription of its own, receiving every message. At each level each subscriber processes each message
    exactly once.
    """
    test_name = 'test_concurrency_levels'
    level_name = get_scenario_name(test_name, scenario)

    prefix = new_prefix()
    run = ScenarioRun(scenario, prefix)
    progress = Progress(level_name)

    measurement = begin_measurement()
    timing = run_scenario(progress, run, _level_duration, 0)

    verify_and_report(measurement, level_name, run, timing, 0)

# ################################################################################################################################
# ################################################################################################################################
