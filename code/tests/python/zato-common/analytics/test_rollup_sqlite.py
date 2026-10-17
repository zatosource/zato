# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from common import analytics_test_env, run_rollup_scenario
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx

# ################################################################################################################################
# ################################################################################################################################

def test_rollup_sqlite(tmp_path:'os.PathLike') -> 'None':
    """ The complete rollup scenario with the audit log and the analytics store
    each in its own SQLite file.
    """
    audit_db_path = os.path.join(str(tmp_path), 'audit.db')
    analytics_db_path = os.path.join(str(tmp_path), 'analytics.db')

    audit_details = {
        'type': AuditLogCtx.Type_SQLite,
        'name': audit_db_path,
    }

    with analytics_test_env(audit_details, analytics_db_path):
        run_rollup_scenario()

    # Each store created its own file under the path its environment pointed at
    assert os.path.exists(audit_db_path)
    assert os.path.exists(analytics_db_path)

# ################################################################################################################################
# ################################################################################################################################
