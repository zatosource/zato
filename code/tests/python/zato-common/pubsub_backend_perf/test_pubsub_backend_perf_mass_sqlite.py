# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from common import cleanup_sqlite_db, pubsub_backend_env, Mass_Drain_Backlog_Mass, Mass_Drain_Deadline_Mass, Mass_Drain_Publish_Floor_Mass, \
    Operations_Backlog_Mass, Operations_Clear_Budget_Mass, Operations_Cleared_Mass, Operations_Delivery_Floor_Mass, \
    Operations_Topics_Mass
from mass_drain import run_mass_drain_scenario
from operations import run_operations_scenario
from zato.common.pubsub.sql.config import ModuleCtx as PubSubDBCtx

# ################################################################################################################################
# ################################################################################################################################

def test_pubsub_backend_perf_mass_sqlite(tmp_path:'os.PathLike') -> 'None':
    """ The mass-recovery scenario at full scale against the default SQLite backend -
    one hundred subscribers, each with a hundred-thousand-message backlog,
    ten million messages in total.
    """
    db_path = os.path.join(str(tmp_path), 'pubsub.db')

    details = {
        'type': PubSubDBCtx.Type_SQLite,
        'name': db_path,
    }

    try:
        with pubsub_backend_env(details):
            run_mass_drain_scenario(
                backlog_per_subscriber=Mass_Drain_Backlog_Mass,
                deadline_seconds=Mass_Drain_Deadline_Mass,
                min_publish_rate=Mass_Drain_Publish_Floor_Mass,
            )
            run_operations_scenario(
                topic_count=Operations_Topics_Mass,
                backlog_per_subscriber=Operations_Backlog_Mass,
                cleared_queue_count=Operations_Cleared_Mass,
                clear_budget_seconds=Operations_Clear_Budget_Mass,
                deadline_seconds=Mass_Drain_Deadline_Mass,
                min_publish_rate=Mass_Drain_Publish_Floor_Mass,
                min_delivery_rate=Operations_Delivery_Floor_Mass,
                drain_to_zero=False,
            )
    finally:
        with pubsub_backend_env(details):
            cleanup_sqlite_db(db_path)

# ################################################################################################################################
# ################################################################################################################################
