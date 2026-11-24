# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# For twenty minutes, one server is active while the jobs run and the pub/sub workload publishes, pulls and receives
# pushes, and the resources of its container are sampled throughout.

# stdlib
import time
from dataclasses import asdict
from typing import cast

# pytest
import pytest

# Zato
from checks import check_run_log
from pair import stop_server
from resources import get_resource_growth, ResourceMonitor
from workload import get_count_mismatches, get_repeats_not_in_flight, Topic_Name, Workload
from zato.common.test.client import AdminClient
from zato.common.test.perf_report import report_result, start_measurement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pair import SchedulerPair
    from zato.common.typing_ import any_, anydict

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
    of the active server remain bounded. The figures of the run are recorded with the settings of the active server.
    """
    pair = workload_pair

    # The server measured is the active one, on the database that the servers share
    client = AdminClient(pair.a.server.base_url, pair.invoke_password)
    measurement = start_measurement(client, pair.database)

    workload = Workload(cast('any_', pair), [pair.a.server])

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

    # The settings are read while the measured server still runs.
    resources:'list[anydict]' = []

    for period in monitor.periods:
        resources.append(asdict(period))

    _ = report_result(measurement, 'scheduler-soak', {
        'seconds': _duration_seconds,
        'publications_acknowledged': len(workload.acknowledged),
        'messages_pulled': len(workload.pulled),
        'pushes_received': len(records),
        'resources': resources,
    })

    stop_server(pair.a)

    # .. with the stored counts equal to the rows ..
    mismatches = get_count_mismatches(cast('any_', pair))
    assert not mismatches, mismatches

    # .. no slot ran twice and the run counts equal the run state ..
    _ = check_run_log(pair)

    # .. and the resources of the server remained within their bounds.
    growth = get_resource_growth(monitor.periods)
    assert not growth, growth

# ################################################################################################################################
# ################################################################################################################################
