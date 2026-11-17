# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from uuid import uuid4

# gevent
import gevent

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.audit_log.common import event_dedup_table
from zato.common.common_db.schema import shared_object_table
from zato.common.db_env.engine import execute_write
from zato.common.db_env.write_path import Mechanism, write_path, WritePathViolation
from zato.common.test.zato_database import file_database_engine
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from sqlalchemy.engine import Engine
    from sqlalchemy.sql.dml import Insert

    Engine = Engine
    Insert = Insert
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The type of the shared objects that the tests insert
    Object_Type = 'write-path-test'

    # The outcome of a dedup row that the tests insert
    Dedup_Outcome = ''

# ################################################################################################################################
# ################################################################################################################################

def _new_shared_object_insert(name:'str') -> 'Insert':
    """ Returns an insert of one shared object, a table outside of the audit log.
    """
    out = shared_object_table.insert().values(
        object_type=ModuleCtx.Object_Type,
        name=name,
        data='{}',
        version=1,
        last_updated=utcnow(),
    )

    return out

# ################################################################################################################################

def _new_dedup_insert(dedup_key:'str') -> 'Insert':
    """ Returns an insert of one row of the dedup ledger, a table of the audit log.
    """
    out = event_dedup_table.insert().values(
        dedup_key=dedup_key,
        cid=dedup_key,
        action=ModuleCtx.Object_Type,
        actor=ModuleCtx.Object_Type,
        created_at=utcnow(),
        outcome=ModuleCtx.Dedup_Outcome,
        completed_at=None,
    )

    return out

# ################################################################################################################################

def _count_shared_objects(engine:'Engine', name:'str') -> 'int':
    statement = select(func.count()).select_from(shared_object_table).where(shared_object_table.c.name == name)

    with engine.connect() as connection:
        out = connection.execute(statement).scalar_one()

    return out

# ################################################################################################################################

def _insert_in_transaction(engine:'Engine', statement:'Insert') -> 'None':
    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################
# ################################################################################################################################

def test_write_outside_mechanism_refused(tmp_path:'Path') -> 'None':
    """ An insert on an engine of the Zato database outside of every mechanism is refused before it reaches the database.
    """
    name = uuid4().hex

    with file_database_engine(tmp_path) as engine:

        with pytest.raises(WritePathViolation):
            _insert_in_transaction(engine, _new_shared_object_insert(name))

        assert _count_shared_objects(engine, name) == 0

# ################################################################################################################################

def test_serialized_write_accepted(tmp_path:'Path') -> 'None':
    """ The same insert through a serialized write is committed.
    """
    name = uuid4().hex

    with file_database_engine(tmp_path) as engine:
        _ = execute_write(engine, _new_shared_object_insert(name))

        assert _count_shared_objects(engine, name) == 1

# ################################################################################################################################

def test_audit_table_refused_to_serialized_write(tmp_path:'Path') -> 'None':
    """ A serialized write cannot insert into a table of the audit log, which only its group commit,
    maintenance, schema creation, a takeover and a seed write.
    """
    with file_database_engine(tmp_path) as engine:
        with pytest.raises(WritePathViolation):
            _ = execute_write(engine, _new_dedup_insert(uuid4().hex))

# ################################################################################################################################

def test_write_deferred_to_greenlet_refused(tmp_path:'Path') -> 'None':
    """ A greenlet that a mechanism starts begins without the mark of the mechanism, so a write handed over to it
    is refused rather than committed after the mechanism ended.
    """
    name = uuid4().hex

    with file_database_engine(tmp_path) as engine:

        with write_path(Mechanism.Serialized_Write):
            greenlet = gevent.spawn(_insert_in_transaction, engine, _new_shared_object_insert(name))

        with pytest.raises(WritePathViolation):
            greenlet.get()

        assert _count_shared_objects(engine, name) == 0

# ################################################################################################################################

def test_seed_cannot_change_rows(tmp_path:'Path') -> 'None':
    """ A seed inserts and removes rows, a table of the audit log included, and is refused when it changes one.
    """
    name = uuid4().hex

    with file_database_engine(tmp_path) as engine:

        with write_path(Mechanism.Seed):
            _insert_in_transaction(engine, _new_shared_object_insert(name))
            _insert_in_transaction(engine, _new_dedup_insert(name))

            update = shared_object_table.update().where(shared_object_table.c.name == name).values(version=2)

            with pytest.raises(WritePathViolation), engine.begin() as connection:
                _ = connection.execute(update)

        assert _count_shared_objects(engine, name) == 1

# ################################################################################################################################
# ################################################################################################################################
