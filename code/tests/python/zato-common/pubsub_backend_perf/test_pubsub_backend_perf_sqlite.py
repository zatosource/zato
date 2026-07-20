# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from backbone import run_backbone_scenario
from backlog import run_backlog_scenario
from common import cleanup_sqlite_db, pubsub_backend_env, Mass_Drain_Backlog_Main, Mass_Drain_Deadline_Main, Mass_Drain_Publish_Floor_Main, \
    Operations_Clear_Budget_Main, Operations_Cleared_Main, Operations_Topics_Main
from drain import run_drain_scenario
from fanout import run_fanout_scenario
from laggard import run_laggard_scenario
from mass_drain import run_mass_drain_scenario
from operations import run_operations_scenario
from subscriptions import run_subscriptions_scenario
from throughput import run_delivery_throughput_scenario, run_publish_throughput_scenario
from zato.common.pubsub.sql.config import ModuleCtx as PubSubDBCtx

# ################################################################################################################################
# ################################################################################################################################

def test_pubsub_backend_perf_sqlite(tmp_path:'os.PathLike') -> 'None':
    """ The complete pub/sub backend performance scenario against the default SQLite backend.
    """
    db_path = os.path.join(str(tmp_path), 'pubsub.db')

    details = {
        'type': PubSubDBCtx.Type_SQLite,
        'name': db_path,
    }

    try:
        with pubsub_backend_env(details):
            run_publish_throughput_scenario()
            run_delivery_throughput_scenario()
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
            )
            run_backlog_scenario()
    finally:
        with pubsub_backend_env(details):
            cleanup_sqlite_db(db_path)

# ################################################################################################################################
# ################################################################################################################################
