# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from common import audit_log_env, run_audit_log_scenario
from config_audit import run_config_audit_scenario
from resubmit_core import run_resubmit_core_scenario
from retention_tiers import run_retention_tiers_scenario
from structured import run_structured_events_scenario
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx

# ################################################################################################################################
# ################################################################################################################################

def test_audit_log_sqlite(tmp_path:'os.PathLike') -> 'None':
    """ The complete audit log scenario against the default SQLite backend.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    details = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with audit_log_env(details):
        run_audit_log_scenario()
        run_structured_events_scenario()
        run_retention_tiers_scenario()
        run_resubmit_core_scenario()
        run_config_audit_scenario()

    # The database file was created under the path the environment pointed at
    assert os.path.exists(db_path)

# ################################################################################################################################
# ################################################################################################################################
