# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from cleanup import run_cleanup_scenario
from common import pubsub_backend_env
from encryption import run_encryption_scenario
from lifecycle import run_lifecycle_scenario
from push_delivery import run_push_delivery_scenario
from queues import run_queues_scenario
from stats import run_stats_scenario
from wakeup import run_wakeup_scenario
from zato.common.pubsub.sql.config import ModuleCtx as PubSubDBCtx

# ################################################################################################################################
# ################################################################################################################################

def test_pubsub_backend_sqlite(tmp_path:'os.PathLike') -> 'None':
    """ The complete pub/sub backend scenario against the default SQLite backend.
    """
    db_path = os.path.join(str(tmp_path), 'pubsub.db')

    details = {
        'type': PubSubDBCtx.Type_SQLite,
        'name': db_path,
    }

    with pubsub_backend_env(details):
        run_lifecycle_scenario()
        run_queues_scenario()
        run_stats_scenario()
        run_wakeup_scenario()
        run_encryption_scenario()
        run_cleanup_scenario()
        run_push_delivery_scenario()

    # The database file was created under the path the environment pointed at
    assert os.path.exists(db_path)

# ################################################################################################################################
# ################################################################################################################################
