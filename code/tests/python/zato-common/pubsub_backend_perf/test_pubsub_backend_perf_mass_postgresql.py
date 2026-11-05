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
from common import Mass_Drain_Backlog_Mass, Mass_Drain_Deadline_Mass, Mass_Drain_Publish_Floor_Mass, \
    Operations_Backlog_Mass, Operations_Clear_Budget_Mass, Operations_Cleared_Mass, Operations_Delivery_Floor_Mass, \
    Operations_Topics_Mass
from mass_drain import run_mass_drain_scenario
from operations import run_operations_scenario
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
    database = start_pubsub_database('perfmass', request.param)
    database.env[ModuleCtx.Env_Generation_File] = os.path.join(database.work_dir, 'pubsub-generation')

    try:
        yield database
    finally:
        stop_pubsub_database(database)

# ################################################################################################################################
# ################################################################################################################################

def test_pubsub_backend_perf_mass_postgresql(pubsub_database:'PubSubDatabase') -> 'None':
    """ The mass-recovery scenario at full scale against PostgreSQL, in plain TCP and TLS -
    one hundred subscribers, each with a hundred-thousand-message backlog,
    ten million messages in total.
    """
    with pubsub_db_env(pubsub_database.env):

        try:
            # As in production, every transaction runs under the generation of this process.
            _ = take_over(get_pubsub_engine)

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
            get_pubsub_engine().dispose()

# ################################################################################################################################
# ################################################################################################################################
