# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from scenarios import run_delivery_scenarios
from zato.common.db_env.database import get_database_engine
from zato.common.test.pubsub_database import get_suite_modes, pubsub_db_env, PubSubDBMode, start_pubsub_database, \
    stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_modes = get_suite_modes([PubSubDBMode.PostgreSQL, PubSubDBMode.PostgreSQL_TLS, PubSubDBMode.PostgreSQL_MTLS])

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module', params=_modes)
def pubsub_database(request:'pytest.FixtureRequest') -> 'any_':
    """ A PostgreSQL container per mode, removed with its data once the mode's tests complete.
    """
    database = start_pubsub_database('delivery', request.param)

    try:
        yield database
    finally:
        stop_pubsub_database(database)

# ################################################################################################################################
# ################################################################################################################################

def test_pubsub_delivery_postgresql(pubsub_database:'PubSubDatabase') -> 'None':
    """ The delivery of messages to pull and push subscribers against PostgreSQL, in plain TCP, TLS and mutual TLS.
    """
    with pubsub_db_env(pubsub_database.env):

        engine = get_database_engine()
        assert engine.dialect.name == 'postgresql'

        run_delivery_scenarios()

# ################################################################################################################################
# ################################################################################################################################
