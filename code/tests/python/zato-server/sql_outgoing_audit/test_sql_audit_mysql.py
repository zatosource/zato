# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import run_sql_audit_scenario, Engine_MySQL

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import os
    from live_sql.containers import DatabaseServer

    os = os
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_sql_audit_mysql(mysql_server:'DatabaseServer', tmp_path:'os.PathLike') -> 'None':
    """ The complete SQL audit scenario against a live MySQL server.
    """
    run_sql_audit_scenario(mysql_server.details, Engine_MySQL, tmp_path)

# ################################################################################################################################
# ################################################################################################################################
