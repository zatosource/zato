# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import ext_db_env, run_ext_db_scenario

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_ext_db_postgresql(postgresql_server:'DatabaseServer') -> 'None':
    """ The complete external AS2/AS4 database scenario against a live PostgreSQL server.
    """
    with ext_db_env(postgresql_server.details):
        run_ext_db_scenario()

# ################################################################################################################################
# ################################################################################################################################
