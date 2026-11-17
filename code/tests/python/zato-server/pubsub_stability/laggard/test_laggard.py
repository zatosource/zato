# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# Zato
from pubsub_rest.monitor import Limits
from pubsub_rest.runner import get_duration, run_for
from pubsub_rest.suite import TrafficRun
from pubsub_rest.traffic import Default_Expiration
from zato.common.test.perf_report import report_result, start_measurement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_rest.server import PubSubServer

# ################################################################################################################################
# ################################################################################################################################

# How long the partner stays away while the traffic continues, in seconds.
_lag_seconds = 2 * 60

# How long the backlog may take to drain once the partner is back, in seconds.
_drain_seconds = 4 * 60 * 60

# The expirations of the publications, none of them shorter than the lag and the drain together, because the messages
# published to the partner while it is away wait behind its backlog for that long and would otherwise expire undelivered.
_laggard_expirations = [Default_Expiration, 86_400, 7 * 86_400]

# The minute after the warm-up, whose resources the last minute is compared with.
_baseline_minute = 5

# How often the depth of the queue of the partner is checked during the drain, in seconds.
_depth_check_seconds = 30

# How long the remaining traffic may take to drain once the publications stop, in seconds.
_final_drain_seconds = 600

# ################################################################################################################################
# ################################################################################################################################

def test_laggard(server:'PubSubServer') -> 'None':
    """ A partner a week behind, with a backlog of tens of millions of messages, does not slow down the publishers
    or the other partners, and once it is back, its whole backlog drains while the traffic continues.
    """
    backlog_messages = server.properties['backlog_messages']
    lag_seconds = get_duration('Zato_Test_Laggard_Seconds', _lag_seconds)
    drain_seconds = get_duration('Zato_Test_Laggard_Drain_Seconds', _drain_seconds)

    measurement = start_measurement(server.get_client(), server.get_database())
    run = TrafficRun(server, Limits())

    run.monitor.limits.max_message_rows = backlog_messages * 2

    traffic = run.traffic
    traffic.expirations = _laggard_expirations

    laggard_sub_key = traffic.partner_sub_keys[server.properties['laggard_index']]

    def is_laggard_drained() -> 'bool':
        out = server.get_queue_depth(laggard_sub_key) == 0
        return out

    # The backlog is in the queue of the partner, which neither pulls nor counts towards the delivery latency of the others.
    traffic.extra_deliveries = backlog_messages
    traffic.paused_sub_keys.add(laggard_sub_key)
    traffic.unmeasured_sub_keys.add(laggard_sub_key)

    try:
        run.start()

        # The others are served while the partner is away ..
        run_for(run.monitor, lag_seconds)

        # .. then it is back and drains its backlog while the traffic continues.
        traffic.paused_sub_keys.clear()
        drain_started = monotonic()

        run_for(run.monitor, drain_seconds, is_done=is_laggard_drained, is_done_interval=_depth_check_seconds)

        laggard_drain_seconds = monotonic() - drain_started
        laggard_depth = server.get_queue_depth(laggard_sub_key)

        drained_seconds = run.drain(_final_drain_seconds)

    finally:
        run.stop()

    figures = run.get_figures({
        'backlog_messages': backlog_messages,
        'seed_seconds': server.properties['seed_seconds'],
        'laggard_drain_seconds': laggard_drain_seconds,
        'drain_seconds': drained_seconds,
    })
    _ = report_result(measurement, 'pubsub-laggard', figures)

    monitor = run.monitor

    assert not monitor.is_disk_low, 'The run stopped because the disk ran low'
    assert laggard_depth == 0, f'{laggard_depth} messages left after {drain_seconds}s'
    assert not monitor.get_failures(), monitor.get_failures()
    assert not monitor.get_resource_growth(_baseline_minute), monitor.get_resource_growth(_baseline_minute)
    assert not server.get_count_mismatches(), server.get_count_mismatches()

# ################################################################################################################################
# ################################################################################################################################
