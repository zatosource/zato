# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import pubsub_backend_env
from encryption import run_encryption_scenario
from lifecycle import run_lifecycle_scenario
from queues import run_queues_scenario
from stats import run_stats_scenario
from wakeup import run_wakeup_scenario

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_pubsub_backend_postgresql(postgresql_server:'DatabaseServer') -> 'None':
    """ The complete pub/sub backend scenario against a plain PostgreSQL server.
    """
    with pubsub_backend_env(postgresql_server.details):
        run_lifecycle_scenario()
        run_queues_scenario()
        run_stats_scenario()
        run_wakeup_scenario()
        run_encryption_scenario()

# ################################################################################################################################
# ################################################################################################################################
