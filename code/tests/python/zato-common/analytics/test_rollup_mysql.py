# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from common import analytics_test_env, run_rollup_scenario

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_rollup_mysql(mysql_server:'DatabaseServer', tmp_path:'os.PathLike') -> 'None':
    """ The complete rollup scenario with the audit log in a live MySQL server
    and the analytics store in its local SQLite file.
    """
    analytics_db_path = os.path.join(str(tmp_path), 'analytics.db')

    with analytics_test_env(mysql_server.details, analytics_db_path):
        run_rollup_scenario()

    assert os.path.exists(analytics_db_path)

# ################################################################################################################################
# ################################################################################################################################
