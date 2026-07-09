# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from common import audit_log_env, run_audit_log_scenario
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx

# ################################################################################################################################
# ################################################################################################################################

def test_audit_log_sqlite(tmp_path:'os.PathLike') -> 'None':
    """ The complete audit log scenario against the default SQLite backend.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    env = {
        AuditLogCtx.Env_Type: AuditLogCtx.Type_SQLite,
        AuditLogCtx.Env_Name: db_path,
    }

    with audit_log_env(env):
        run_audit_log_scenario()

    # The database file was created under the path the environment pointed at
    assert os.path.exists(db_path)

# ################################################################################################################################
# ################################################################################################################################
