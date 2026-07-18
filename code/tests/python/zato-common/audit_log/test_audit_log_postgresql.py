# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import audit_log_env, run_audit_log_scenario
from resubmit_core import run_resubmit_core_scenario
from retention_tiers import run_retention_tiers_scenario
from structured import run_structured_events_scenario

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_audit_log_postgresql(postgresql_server:'DatabaseServer') -> 'None':
    """ The complete audit log scenario against a live PostgreSQL server.
    """
    with audit_log_env(postgresql_server.details):
        run_audit_log_scenario()
        run_structured_events_scenario()
        run_retention_tiers_scenario()
        run_resubmit_core_scenario()

# ################################################################################################################################
# ################################################################################################################################
