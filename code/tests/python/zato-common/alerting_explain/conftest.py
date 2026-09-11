# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def audit_db_env(tmp_path:'os.PathLike') -> 'any_':
    """ Points the audit database at a per-test SQLite file so every test
    runs on its own isolated database.
    """
    database_path = os.path.join(str(tmp_path), 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = database_path

    yield database_path

    del os.environ[AuditLogCtx.Env_Type]
    del os.environ[AuditLogCtx.Env_Name]

# ################################################################################################################################
# ################################################################################################################################
