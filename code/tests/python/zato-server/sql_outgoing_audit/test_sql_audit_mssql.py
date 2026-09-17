# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import run_mssql_callproc_audit_scenario, run_sql_audit_scenario, Engine_MSSQL

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import os
    from live_sql.containers import DatabaseServer

    os = os
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_sql_audit_mssql(mssql_server:'DatabaseServer', tmp_path:'os.PathLike') -> 'None':
    """ The complete SQL audit scenario against a live MS SQL server.
    """
    run_sql_audit_scenario(mssql_server.details, Engine_MSSQL, tmp_path)

# ################################################################################################################################

def test_sql_audit_mssql_callproc(mssql_server:'DatabaseServer', tmp_path:'os.PathLike') -> 'None':
    """ Stored procedure calls against a live MS SQL server are on record like statements are.
    """
    run_mssql_callproc_audit_scenario(mssql_server.details, tmp_path)

# ################################################################################################################################
# ################################################################################################################################
