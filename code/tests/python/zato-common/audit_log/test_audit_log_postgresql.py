# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import audit_log_env, run_audit_log_scenario

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_audit_log_postgresql(postgresql_server:'DatabaseServer') -> 'None':
    """ The complete audit log scenario against a live PostgreSQL server.
    """
    with audit_log_env(postgresql_server.env):
        run_audit_log_scenario()

# ################################################################################################################################
# ################################################################################################################################
