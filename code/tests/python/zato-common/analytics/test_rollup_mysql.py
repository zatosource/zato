# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import analytics_test_env, run_rollup_scenario

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_rollup_mysql(mysql_server:'DatabaseServer') -> 'None':
    """ The complete rollup scenario against a live MySQL server.
    """
    with analytics_test_env(mysql_server.details):
        run_rollup_scenario()

# ################################################################################################################################
# ################################################################################################################################
