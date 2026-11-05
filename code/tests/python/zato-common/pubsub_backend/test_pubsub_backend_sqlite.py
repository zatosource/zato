# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from cleanup_lock import run_cleanup_lock_scenario
from common import pubsub_path_env
from scenarios import run_common_scenarios

# ################################################################################################################################
# ################################################################################################################################

def test_pubsub_backend_sqlite(tmp_path:'os.PathLike') -> 'None':
    """ The complete pub/sub backend scenario against the default SQLite backend.
    """
    db_path = os.path.join(str(tmp_path), 'pubsub.db')

    with pubsub_path_env(db_path):
        run_common_scenarios()
        run_cleanup_lock_scenario()

    # The database file was created under the path the environment pointed at.
    assert os.path.exists(db_path)

# ################################################################################################################################
# ################################################################################################################################
