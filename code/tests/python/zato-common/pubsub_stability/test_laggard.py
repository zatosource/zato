# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# SQLAlchemy
from sqlalchemy import text

# Zato
from monitor import Limits, Monitor
from runner import get_count_mismatches, get_duration, get_report_path, run_for, start_cleanup_process, \
    stop_cleanup_process
from seeding import seed_backlog
from traffic import get_traffic_profile, Traffic
from zato.common.pubsub.sql.config import get_pubsub_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

# How many messages the partner is behind, unless Zato_Test_Laggard_Messages says otherwise.
_backlog_messages = 20_000_000

# How long the partner stays away while the traffic continues, in seconds.
_lag_seconds = 15 * 60

# How long the backlog may take to drain once the partner is back, in seconds.
_drain_seconds = 4 * 60 * 60

# The first partner of the traffic is the one that is behind - its topic and its subscriber,
# named as the traffic names them, so that the seeded backlog is in its queue.
_partner_topic_prefix = 'stability.partner'
_partner_sub_key_prefix = 'zpsk.stability.partner'
_laggard_sub_key = 'zpsk.stability.partner.0000'

# The minute after the warm-up, whose resources the last minute is compared with.
_baseline_minute = 5

# How often the cleanup process sweeps, in seconds.
_cleanup_interval_seconds = 60

# How often the depth of the queue of the partner is checked during the drain, in seconds.
_depth_check_seconds = 30

# How many deliveries are left in the queue of the partner.
_laggard_depth_query = text('select count(*) from pubsub_delivery where sub_key = :sub_key')

# ################################################################################################################################
# ################################################################################################################################

def _get_laggard_depth() -> 'int':
    with get_pubsub_engine().connect() as connection:
        out = connection.execute(_laggard_depth_query, {'sub_key': _laggard_sub_key}).scalar_one()
    return out

# ################################################################################################################################

def _is_laggard_drained() -> 'bool':
    out = _get_laggard_depth() == 0
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_laggard(stability_env:'strstrdict') -> 'None':
    """ A partner a week behind, with a backlog of tens of millions of messages, does not slow down the publishers
    or the other partners, and once it is back, its whole backlog drains while the traffic continues.
    """
    backlog_messages = get_duration('Zato_Test_Laggard_Messages', _backlog_messages)
    lag_seconds = get_duration('Zato_Test_Laggard_Seconds', _lag_seconds)
    drain_seconds = get_duration('Zato_Test_Laggard_Drain_Seconds', _drain_seconds)

    # The backlog is in the queue of the partner before the traffic starts ..
    seed_seconds = seed_backlog(
        topic_count=1,
        messages_per_topic=backlog_messages,
        topic_prefix=_partner_topic_prefix,
        sub_key_prefix=_partner_sub_key_prefix,
    )
    print(f'Seeded {backlog_messages} messages in {seed_seconds:.0f}s', flush=True)

    traffic = Traffic(get_traffic_profile())
    traffic.backend.take_over()
    traffic.subscribe_all()

    # .. and the partner neither pulls nor counts towards the delivery latency of the others.
    traffic.extra_deliveries = backlog_messages
    traffic.paused_sub_keys.add(_laggard_sub_key)
    traffic.unmeasured_sub_keys.add(_laggard_sub_key)

    cleanup = start_cleanup_process(_cleanup_interval_seconds)
    monitor = Monitor(traffic, Limits(max_message_rows=backlog_messages * 2), get_report_path('laggard'), 'laggard')

    try:
        traffic.start()
        monitor.start()

        # The others are served while the partner is away ..
        run_for(monitor, lag_seconds)

        # .. then it is back and drains its backlog while the traffic continues.
        traffic.paused_sub_keys.clear()
        drain_started = monotonic()

        run_for(monitor, drain_seconds, is_done=_is_laggard_drained, is_done_interval=_depth_check_seconds)

        laggard_drain_seconds = monotonic() - drain_started
        laggard_depth = _get_laggard_depth()

        traffic.stop_publishing()
        monitor.checks_rate = False
        _ = traffic.wait_until_drained(_cleanup_interval_seconds * 10)

    finally:
        monitor.stop()
        traffic.stop()
        stop_cleanup_process(cleanup)

    print(f'Backlog of {backlog_messages} drained in {laggard_drain_seconds:.0f}s', flush=True)

    assert not monitor.is_disk_low, 'The run stopped because the disk ran low'
    assert laggard_depth == 0, f'{laggard_depth} messages left after {drain_seconds}s'
    assert not monitor.get_failures(), monitor.get_failures()
    assert not monitor.get_resource_growth(_baseline_minute), monitor.get_resource_growth(_baseline_minute)
    assert not get_count_mismatches(), get_count_mismatches()

# ################################################################################################################################
# ################################################################################################################################
