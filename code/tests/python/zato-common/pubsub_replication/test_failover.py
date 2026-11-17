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
from zato.common.pubsub.sql.replaced import PubSubReplaced
from zato.common.test.pubsub_replication import kill_primary, promote_standby
from zato.common.test.takeover import take_over_as_another_server

# local
from checks import check_counts_equal_rows, check_delivery, read_generation, stored_msg_ids
from environment import replicated_environment
from workload import Pull_Topic, Workload

# ################################################################################################################################
# ################################################################################################################################

# How long the traffic runs before the primary is lost, in seconds.
_traffic_before_seconds = 5

# How long a managed service takes to detect the loss of its primary before it promotes the standby, in seconds.
_detection_seconds = 2

# How long the traffic runs on the new primary, and how long the backlog may take to drain, in seconds.
_traffic_after_seconds = 10
_drain_timeout = 120

# The pool size that gives the server which takes the promoted database over an engine of its own
_other_server_pool_size = 2

# ################################################################################################################################
# ################################################################################################################################

def test_failover_synchronous() -> 'None':
    """ With synchronous replication, no acknowledged publication is lost when the primary is lost.
    """
    with replicated_environment('sync') as database:

        workload = Workload('sync')
        workload.backend.take_over()

        guard = workload.backend.generation_guard
        assert guard is not None

        workload.subscribe()
        workload.start()

        sleep(_traffic_before_seconds)

        # The primary is lost in the middle of the traffic ..
        acknowledged_before = len(workload.acknowledged)
        kill_primary(database)

        # .. and the standby is promoted once the service detects the loss ..
        sleep(_detection_seconds)
        promote_seconds = promote_standby(database)
        restore_time = monotonic()

        sleep(_traffic_after_seconds)
        workload.stop_publishing()

        # .. no acknowledged publication may be missing from the promoted standby ..
        lost = set(workload.acknowledged) - stored_msg_ids(database)
        assert not lost, f'Lost: {sorted(lost)[:10]}'

        # .. and every publication reaches its subscriber.
        workload.wait_until_delivered(_drain_timeout, lost)
        workload.stop()

        measurements = check_delivery(database, workload, restore_time)
        measurements['acknowledged_before_kill'] = acknowledged_before
        measurements['promote_seconds'] = round(promote_seconds, 3)

        assert measurements['lost'] == 0, measurements

        check_counts_equal_rows(database, workload)

        # .. the generation was replicated with everything else, so the server is still the active one ..
        assert read_generation(database) == guard.generation
        assert not workload.backend.is_replaced

        # .. and once another server takes over the promoted database, this one changes nothing.
        other = take_over_as_another_server(database.env, _other_server_pool_size)

        other_guard = other.generation_guard
        assert other_guard is not None

        with pytest.raises(PubSubReplaced):
            _ = workload.backend.publish(Pull_Topic, 'rejected')

        assert workload.backend.is_replaced
        guard.uninstall(workload.backend.engine)
        other_guard.uninstall(other.engine)

# ################################################################################################################################
# ################################################################################################################################
