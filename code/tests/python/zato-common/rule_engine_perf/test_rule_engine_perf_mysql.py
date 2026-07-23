# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from common import database_from_details
from runner import run_complete_perf

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer

    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_rule_engine_perf_mysql(mysql_server:'DatabaseServer') -> 'None':
    """ The complete rule-engine SQL layer performance scenario against a plain MySQL server.
    """
    perf_database = database_from_details('MySQL', mysql_server.details)
    run_complete_perf(perf_database)

# ################################################################################################################################
# ################################################################################################################################
