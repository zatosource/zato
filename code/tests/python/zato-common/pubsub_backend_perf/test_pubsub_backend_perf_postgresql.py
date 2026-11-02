# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# Zato
from backbone import run_backbone_scenario
from backlog import run_backlog_scenario
from common import Mass_Drain_Backlog_Main, Mass_Drain_Deadline_Main, Mass_Drain_Publish_Floor_Main, \
    Min_Delivery_Rate_Per_Second, Operations_Clear_Budget_Main, Operations_Cleared_Main, Operations_Topics_Main
from document_mix import run_document_mix_scenario
from drain import run_drain_scenario
from fanout import run_fanout_scenario
from laggard import run_laggard_scenario
from mass_drain import run_mass_drain_scenario
from operations import run_operations_scenario
from production_mix import run_production_mix_scenario
from push import run_push_delivery_scenario
from retention import run_retention_scenario
from subscriptions import run_subscriptions_scenario
from throughput import run_delivery_throughput_scenario, run_publish_throughput_scenario
from zato.common.pubsub.sql.config import get_pubsub_engine, ModuleCtx
from zato.common.pubsub.sql.generation import take_over
from zato.common.test.pubsub_database import get_suite_modes, pubsub_db_env, PubSubDBMode, start_pubsub_database, \
    stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_modes = get_suite_modes([PubSubDBMode.PostgreSQL, PubSubDBMode.PostgreSQL_TLS])

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module', params=_modes)
def pubsub_database(request:'pytest.FixtureRequest') -> 'any_':
    database = start_pubsub_database('perf', request.param)

    # The cleanup process that the retention scenario starts sweeps under the generation recorded in this file.
    database.env[ModuleCtx.Env_Generation_File] = os.path.join(database.work_dir, 'pubsub-generation')

    try:
        yield database
    finally:
        stop_pubsub_database(database)

# ################################################################################################################################
# ################################################################################################################################

def test_pubsub_backend_perf_postgresql(pubsub_database:'PubSubDatabase') -> 'None':
    """ The complete pub/sub backend performance scenario against PostgreSQL, in plain TCP and TLS,
    with the same floors as SQLite.
    """
    with pubsub_db_env(pubsub_database.env):

        try:
            # As in production, every transaction runs under the generation of this process.
            _ = take_over(get_pubsub_engine)

            _ = run_publish_throughput_scenario()
            _ = run_delivery_throughput_scenario()
            run_push_delivery_scenario()
            run_fanout_scenario()
            run_document_mix_scenario()
            run_production_mix_scenario()
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
        finally:
            get_pubsub_engine().dispose()

# ################################################################################################################################
# ################################################################################################################################
