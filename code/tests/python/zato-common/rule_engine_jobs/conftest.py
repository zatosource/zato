# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.rule_engine.notify.credentials import Env_Secret_Key

# The credentials tests need the encryption key before any application code runs.
_secret_key = CryptoManager.generate_key()
os.environ[Env_Secret_Key] = _secret_key.decode('utf-8')

# Test helpers import flat from the local lib directory.
_lib_dir = os.path.join(os.path.dirname(__file__), 'lib')
sys.path.insert(0, _lib_dir)

# pytest
import pytest

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.rule_engine.sql import create_database_engine, create_schema, RuleSQLBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def database_engine(tmp_path:'any_') -> 'any_':
    """ A file-backed SQLite rule engine database, one per test.
    """
    # Build a file-backed database usable across threads ..
    database_path = tmp_path / 'rule-engine.sqlite'
    database_url = f'sqlite:///{database_path}'
    connection_options = {'check_same_thread': False}
    engine = create_database_engine(database_url, connect_args=connection_options)

    # .. create only the rule-engine tables ..
    create_schema(engine)

    yield engine

    # .. and release every pooled connection afterwards.
    engine.dispose()

# ################################################################################################################################

@pytest.fixture()
def backend(database_engine:'any_') -> 'any_':
    """ The typed SQL facade over the per-test database.
    """
    out = RuleSQLBackend.from_engine(database_engine)
    return out

# ################################################################################################################################

@pytest.fixture(autouse=True)
def audit_db_env(tmp_path:'any_') -> 'any_':
    """ Points the deduplicating alert store at a per-test SQLite file
    so spike sweeps run on their own isolated database.
    """
    database_path = os.path.join(str(tmp_path), 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = database_path

    yield database_path

    del os.environ[AuditLogCtx.Env_Type]
    del os.environ[AuditLogCtx.Env_Name]

# ################################################################################################################################
# ################################################################################################################################
