# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import run_sql_audit_scenario, Engine_PostgreSQL

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import os
    from live_sql.containers import DatabaseServer

    os = os
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_sql_audit_postgresql(postgresql_server:'DatabaseServer', tmp_path:'os.PathLike') -> 'None':
    """ The complete SQL audit scenario against a live PostgreSQL server.
    """
    run_sql_audit_scenario(postgresql_server.details, Engine_PostgreSQL, tmp_path)

# ################################################################################################################################
# ################################################################################################################################
