# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import sleep

# pytest
import pytest

# Zato
from zato.common.test.pubsub_replication import start_primary, stop_primary

# local
from checks import check_counts_equal_rows, check_delivery, read_generation
from environment import replicated_environment
from workload import Workload

# ################################################################################################################################
# ################################################################################################################################

# How long the traffic runs before the outage and after it, and how long the backlog may take to drain, in seconds.
_traffic_before_seconds = 5
_traffic_after_seconds = 10
_drain_timeout = 300

# How many messages one pull hands out at most, which bounds what a pull whose response was lost takes along.
_pull_max_messages = 100

# The outages, from a restart of a self-managed database to a long maintenance event of a managed service, in seconds.
_outage_seconds = [10, 30, 120, 600]

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('outage_seconds', _outage_seconds)
def test_database_outage(outage_seconds:'int') -> 'None':
    """ The database is unavailable for a while during traffic. Publications that were not written fail and are
    repeated, nothing acknowledged is lost, every component resumes without a restart and the server remains
    the active one with its generation unchanged.
    """
    label = f'outage{outage_seconds}'

    with replicated_environment(label, True) as database:

        workload = Workload(label)
        workload.backend.take_over()

        guard = workload.backend.generation_guard
        assert guard is not None

        workload.subscribe()
        workload.start()

        sleep(_traffic_before_seconds)

        # The database goes away in the middle of the traffic ..
        stop_time = monotonic()
        stop_primary(database)

        sleep(outage_seconds)

        acknowledged_during = 0
        for acknowledged_time in workload.acknowledged.values():
            if acknowledged_time > stop_time + 1:
                acknowledged_during += 1

        # .. and returns after the outage ..
        start_primary(database)
        restore_time = monotonic()

        sleep(_traffic_after_seconds)
        workload.stop_publishing()

        # .. each pull whose response was lost may have taken at most one batch along ..
        failed_pulls = 0
        for failed_time in workload.failed_pull_times:
            if failed_time >= stop_time - 1:
                failed_pulls += 1

        workload.wait_until_delivered(_drain_timeout, failed_pulls * _pull_max_messages, set())
        workload.stop()

        measurements = check_delivery(database, workload, restore_time)
        measurements['acknowledged_during_outage'] = acknowledged_during

        print(f'\nOutage {outage_seconds}s -> {measurements}')

        # .. nothing was acknowledged while the database was away, nothing acknowledged was lost ..
        assert acknowledged_during == 0, measurements
        assert measurements['lost'] == 0, measurements

        # .. every component resumed ..
        for name in ('publish_resumed_after', 'pull_resumed_after', 'push_resumed_after', 'cleanup_resumed_after'):
            assert measurements[name] >= 0, measurements

        check_counts_equal_rows(database, workload)

        # .. and the server is still the active one.
        assert read_generation(database) == guard.generation
        assert not workload.backend.is_replaced

        guard.uninstall(workload.backend.engine)

# ################################################################################################################################
# ################################################################################################################################
