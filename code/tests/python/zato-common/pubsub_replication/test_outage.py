# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
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

if 0:
    from _pytest.logging import LogCaptureFixture
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# How long the traffic runs before the outage and after it, and how long the backlog may take to drain, in seconds.
_traffic_before_seconds = 5
_traffic_after_seconds = 10
_drain_timeout = 300

# The outages, from a restart of a self-managed database to a long maintenance event of a managed service, in seconds.
_outage_seconds = [10, 30, 120, 600]

# The logger of the resume times, and the components that log theirs.
_outage_logger_name = 'zato.common.db_env.outage'
_resuming_components = ['Pub/sub commit writer', 'PubSub delivery for sub_key', 'Pub/sub cleanup']

# ################################################################################################################################
# ################################################################################################################################

def _is_logged(entries:'strlist', component:'str') -> 'bool':
    for entry in entries:
        if entry.startswith(component):
            return True
    return False

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('outage_seconds', _outage_seconds)
def test_database_outage(outage_seconds:'int', caplog:'LogCaptureFixture') -> 'None':
    """ The database is unavailable for a while during traffic. Publications that were not written fail and are
    repeated, nothing acknowledged is lost, every component resumes without a restart and the server remains
    the active one with its generation unchanged.
    """
    label = f'outage{outage_seconds}'
    caplog.set_level(logging.INFO, logger=_outage_logger_name)

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

        # .. every publication reaches its subscriber ..
        workload.wait_until_delivered(_drain_timeout, set())
        workload.stop()

        measurements = check_delivery(database, workload, restore_time)
        measurements['acknowledged_during_outage'] = acknowledged_during

        resumed_entries:'strlist' = []
        for record in caplog.records:
            if record.name == _outage_logger_name:
                resumed_entries.append(record.getMessage())

        measurements['resumed_entries'] = resumed_entries

        print(f'\nOutage {outage_seconds}s -> {measurements}')

        # .. the commit writer, the push delivery and the cleanup each logged how long they took to resume ..
        for component in _resuming_components:
            assert _is_logged(resumed_entries, component), (component, resumed_entries)

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
