# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from exactly_once.generation import Operation_Names, run_replaced_generation_scenario
from exactly_once.scenarios import get_scenario_id, Scenarios
from zato.common.test.pubsub_database import get_suite_modes, pubsub_db_env, PubSubDBMode, start_pubsub_database, \
    stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, callable_

# ################################################################################################################################
# ################################################################################################################################

_modes = get_suite_modes([PubSubDBMode.PostgreSQL])

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module', params=_modes)
def pubsub_database(request:'pytest.FixtureRequest') -> 'any_':
    """ A PostgreSQL container per mode, removed with its data once the tests of the mode complete.
    """
    database = start_pubsub_database('exactly-once', request.param)

    try:
        yield database
    finally:
        stop_pubsub_database(database)

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('scenario', Scenarios, ids=get_scenario_id)
def test_backend_scenario(pubsub_database:'PubSubDatabase', scenario:'callable_') -> 'None':
    """ One exactly-once scenario of the backend against PostgreSQL.
    """
    with pubsub_db_env(pubsub_database.env):
        scenario()

# ################################################################################################################################

@pytest.mark.parametrize('operation_name', Operation_Names)
def test_replaced_generation(pubsub_database:'PubSubDatabase', operation_name:'str') -> 'None':
    """ A write operation of a server that another server replaced is rejected and changes no row.
    """
    run_replaced_generation_scenario(pubsub_database, operation_name)

# ################################################################################################################################
# ################################################################################################################################
