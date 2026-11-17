# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# For twenty minutes, one server is active while the jobs run and the pub/sub workload publishes, pulls and receives
# pushes, and the resources of its container are sampled throughout.

# stdlib
import time

# pytest
import pytest

# Zato
from checks import check_run_log
from pair import stop_server
from resources import get_resource_growth, ResourceMonitor
from workload import get_count_mismatches, get_repeats_not_in_flight, Topic_Name, Workload
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pair import SchedulerPair
    from zato.common.typing_ import any_

    SchedulerPair = SchedulerPair
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# How long the server runs, in seconds.
_duration_seconds = 20 * 60

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.soak
def test_soak(workload_pair:'SchedulerPair') -> 'None':
    """ No slot runs twice, the run counts equal the run state, the pub/sub workload loses nothing, and the resources
    of the active server remain bounded.
    """
    pair = workload_pair

    workload = Workload(cast_('any_', pair), [pair.a.server])

    monitor = ResourceMonitor()
    monitor.set_active(pair.a)
    monitor.start()

    workload.start()

    try:
        time.sleep(_duration_seconds)

    finally:
        workload.is_publishing.clear()
        monitor.stop()

    # The pull subscriber took every acknowledged publication, and the receiver received no push more than once,
    # as no fault took place. The publishers produce more than one push subscriber receives in the same time,
    # so the pushes still queued at the end are not waited for ..
    workload.drain_pulls()

    unexpected = workload.get_unexpected_repeated_pulls()
    assert not unexpected, sorted(unexpected)[:10]

    records = pair.receivers[Topic_Name].get_request_records()
    repeated = get_repeats_not_in_flight(records, workload.fault_windows)
    assert not repeated, repeated[:10]

    stop_server(pair.a)

    # .. with the stored counts equal to the rows ..
    mismatches = get_count_mismatches(cast_('any_', pair))
    assert not mismatches, mismatches

    # .. no slot ran twice and the run counts equal the run state ..
    _ = check_run_log(pair)

    # .. and the resources of the server remained within their bounds.
    growth = get_resource_growth(monitor.periods)
    assert not growth, growth

# ################################################################################################################################
# ################################################################################################################################
