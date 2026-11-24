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
from conftest import ModuleCtx
from live_sql.env import database_env
from support import insert_seed_event, new_batch, record_statements, Server_Name
from zato.common.audit_log.api import AuditLog
from zato.common.db_env.database import dispose_database_engine, get_database_engine
from zato.common.db_env.database_env import DatabaseEnv

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator

    strgen = Iterator[str]

# ################################################################################################################################
# ################################################################################################################################

# How many events the batch of the test holds
_event_count = 10

# The statement that opens the transaction of a batch, with the write lock of the file
_expected_begin_statements = ['BEGIN IMMEDIATE']

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def sqlite_db_path(tmp_path:'os.PathLike') -> 'strgen':
    """ Opens the SQLite audit database before the test, as a server opens it at startup.
    """
    db_path = os.path.join(str(tmp_path), ModuleCtx.SQLite_File_Name)

    details = {
        'type': DatabaseEnv.Type_SQLite,
        'path': db_path,
    }

    with database_env(details):
        _ = get_database_engine()
        yield db_path
        dispose_database_engine()

# ################################################################################################################################

def test_batch_opens_its_transaction_with_the_write_lock(sqlite_db_path:'str') -> 'None':
    """ The transaction of a batch takes the write lock of the file with its first statement,
    before the payloads of the batch are looked up.
    """
    audit_log = AuditLog(Server_Name)
    seed_event_id = insert_seed_event(audit_log)

    batch = new_batch(audit_log, _event_count, seed_event_id)
    engine = get_database_engine()

    with record_statements(engine) as recorder:
        audit_log.write_pending(batch)

    assert recorder.begin_statements == _expected_begin_statements
    assert recorder.commit_count == 1

# ################################################################################################################################
# ################################################################################################################################
