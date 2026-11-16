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
from common import pubsub_path_env
from exactly_once.scenarios import get_scenario_id, Scenarios
from zato.common.pubsub.sql.config import get_pubsub_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

# The value of PRAGMA synchronous that stands for FULL
_synchronous_full = 2

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('scenario', Scenarios, ids=get_scenario_id)
def test_backend_scenario(tmp_path:'os.PathLike', scenario:'callable_') -> 'None':
    """ One exactly-once scenario of the backend against a SQLite file of its own.
    """
    db_path = os.path.join(tmp_path, 'pubsub.db')

    with pubsub_path_env(db_path):
        scenario()

# ################################################################################################################################

def test_synchronous_full(tmp_path:'os.PathLike') -> 'None':
    """ The engine of the SQLite pub/sub file commits with PRAGMA synchronous set to FULL.
    """
    db_path = os.path.join(tmp_path, 'pubsub.db')

    with pubsub_path_env(db_path):
        engine = get_pubsub_engine()

        with engine.connect() as connection:
            synchronous = connection.exec_driver_sql('PRAGMA synchronous').scalar_one()

    assert synchronous == _synchronous_full

# ################################################################################################################################
# ################################################################################################################################
