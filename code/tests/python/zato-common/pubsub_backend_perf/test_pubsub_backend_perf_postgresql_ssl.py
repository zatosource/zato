# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from backbone import run_backbone_scenario
from backlog import run_backlog_scenario
from common import pubsub_backend_env, Mass_Drain_Backlog_Main, Mass_Drain_Deadline_Main, Mass_Drain_Publish_Floor_Main, \
    Min_Delivery_Rate_Per_Second, Operations_Clear_Budget_Main, Operations_Cleared_Main, Operations_Topics_Main
from drain import run_drain_scenario
from fanout import run_fanout_scenario
from laggard import run_laggard_scenario
from mass_drain import run_mass_drain_scenario
from operations import run_operations_scenario
from push import run_push_delivery_scenario
from retention import run_retention_scenario
from subscriptions import run_subscriptions_scenario
from throughput import run_delivery_throughput_scenario, run_publish_throughput_scenario

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_pubsub_backend_perf_postgresql_ssl(postgresql_ssl_server:'DatabaseServer') -> 'None':
    """ The complete pub/sub backend performance scenario against a PostgreSQL server that requires TLS.
    """
    with pubsub_backend_env(postgresql_ssl_server.details):
        run_publish_throughput_scenario()
        run_delivery_throughput_scenario()
        run_push_delivery_scenario()
        run_fanout_scenario()
        run_backbone_scenario()
        run_subscriptions_scenario()
        run_laggard_scenario()
        run_drain_scenario()
        run_mass_drain_scenario(
            backlog_per_subscriber=Mass_Drain_Backlog_Main,
            deadline_seconds=Mass_Drain_Deadline_Main,
            min_publish_rate=Mass_Drain_Publish_Floor_Main,
        )
        run_operations_scenario(
            topic_count=Operations_Topics_Main,
            backlog_per_subscriber=Mass_Drain_Backlog_Main,
            cleared_queue_count=Operations_Cleared_Main,
            clear_budget_seconds=Operations_Clear_Budget_Main,
            deadline_seconds=Mass_Drain_Deadline_Main,
            min_publish_rate=Mass_Drain_Publish_Floor_Main,
            min_delivery_rate=Min_Delivery_Rate_Per_Second,
            drain_to_zero=True,
        )
        run_retention_scenario()
        run_backlog_scenario()

# ################################################################################################################################
# ################################################################################################################################
