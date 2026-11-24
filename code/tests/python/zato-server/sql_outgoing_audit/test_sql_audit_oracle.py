# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import run_oracle_callproc_audit_scenario, run_sql_audit_scenario, Engine_Oracle

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer

    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_sql_audit_oracle(oracle_server:'DatabaseServer') -> 'None':
    """ The complete SQL audit scenario against a live Oracle server.
    """
    run_sql_audit_scenario(oracle_server.details, Engine_Oracle)

# ################################################################################################################################

def test_sql_audit_oracle_callproc(oracle_server:'DatabaseServer') -> 'None':
    """ Stored procedure calls against a live Oracle server are on record like statements are.
    """
    run_oracle_callproc_audit_scenario(oracle_server.details)

# ################################################################################################################################
# ################################################################################################################################
