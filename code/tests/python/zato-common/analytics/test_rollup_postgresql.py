# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import run_rollup_scenario
from live_sql.env import database_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_rollup_postgresql(postgresql_server:'DatabaseServer') -> 'None':
    """ The complete rollup scenario with the audit log and the analytics store in the Zato database
    of a live PostgreSQL server.
    """
    with database_env(postgresql_server.details):
        run_rollup_scenario()

# ################################################################################################################################
# ################################################################################################################################
