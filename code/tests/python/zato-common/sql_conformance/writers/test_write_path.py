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
from sqlalchemy import func, literal_column, select
from sqlalchemy.dialects import postgresql

# Zato
from zato.common.audit_log.common import event_dedup_table
from zato.common.common_db.message_dedup import dedup_records_query, dedup_upsert
from zato.common.common_db.schema import shared_object_table
from zato.common.db_env.engine import execute_write
from zato.common.db_env.write_path import _parse_statement, Mechanism, ModuleCtx as WritePathCtx, write_path, \
    WritePathViolation
from zato.common.pubsub.sql import ack_deletes, dedup, fenced_ack, payloads, publication_inserts, pull, writes
from zato.common.test.zato_database import zato_database_engine
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from sqlalchemy.sql.dml import Insert
    from sqlalchemy.sql.selectable import Select
    from zato.common.typing_ import any_, strlist, strtuple

    Engine = Engine
    Insert = Insert
    Select = Select

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The type of the shared objects that the tests insert
    Object_Type = 'write-path-test'

    # The outcome of a dedup row that the tests insert
    Dedup_Outcome = ''

    # The text of the statements that fill the cache of the parses beyond its size
    Filler_Statement = 'select {} as write_path_filler'

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

def _insert_in_transaction(engine:'Engine', statement:'Insert | Select[any_]') -> 'None':
    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def _new_cte_write(insert:'Insert', name:'str') -> 'Select[any_]':
    """ Returns a select of the rows that an insert in a common table expression of the select writes,
    which writes rows although the statement that follows its WITH clause only reads them.
    """
    written = insert.returning(literal_column('1').label('is_written')).cte(name)
    out = select(written.c.is_written)

    return out

def _execute_and_roll_back(engine:'Engine', statement:'Insert | Select[any_]') -> 'None':
    """ Executes a statement in a transaction that is rolled back, so that the statement leaves no rows behind.
    """
    with engine.connect() as connection:
        transaction = connection.begin()
        _ = connection.execute(statement)
        transaction.rollback()

# ################################################################################################################################

def _parse_uncached(statement:'str') -> 'tuple[strtuple, strtuple]':
    """ Applies the four patterns of the guard to a statement without the cache of the parses.
    """
    keywords:'strlist' = []
    table_names:'strlist' = []

    if write_match := WritePathCtx.Write_Statement.match(statement):
        keywords.append(write_match.group(1).lower())

    for keyword in WritePathCtx.CTE_Write_Statement.findall(statement):
        keywords.append(keyword.lower())

    if keywords:

        if match := WritePathCtx.Statement_Table.match(statement):
            table_names.append(match.group(1).lower())

        for table_name in WritePathCtx.CTE_Statement_Table.findall(statement):
            table_names.append(table_name.lower())

    out = (tuple(keywords), tuple(table_names))
    return out

# ################################################################################################################################

def _get_platform_statements() -> 'strlist':
    """ Returns the texts of the statements of pub/sub, of the dedup records and of the tests of the guard,
    compiled for PostgreSQL.
    """
    dialect = postgresql.dialect()

    plain_statements = [
        publication_inserts._subscribers_query_plain,
        publication_inserts._existing_messages_query_plain,
        ack_deletes._ack_deliveries_query_plain,
        ack_deletes._delivery_delete_plain,
        writes._record_attempts_statement_plain,
        payloads._message_ids_query_plain,
        payloads._drop_payloads_statement_plain,
        payloads._lock_messages_query_plain,
        payloads._needed_messages_query_plain,
        fenced_ack._fenced_rows_query_plain,
        fenced_ack._fenced_delete_plain,
        dedup._fingerprint_rewrite,
        dedup._existing_fingerprints_query,
        dedup_records_query,
        dedup_upsert,
        pull.payload_statement,
        pull.fetch_statement,
        pull._lease_probe_statement,
        pull._lease_statement,
    ]

    statements:'list[any_]' = []

    for plain_statement in plain_statements:
        statements.append(plain_statement.statement)

    shared_object_insert = _new_shared_object_insert('write-path-statements')
    dedup_insert = _new_dedup_insert('write-path-statements')

    statements.append(shared_object_insert)
    statements.append(dedup_insert)
    statements.append(_new_cte_write(shared_object_insert, 'shared_object_written'))
    statements.append(_new_cte_write(dedup_insert, 'dedup_written'))
    statements.append(shared_object_table.update().values(version=2))
    statements.append(shared_object_table.delete())

    out:'strlist' = []

    for statement in statements:
        compiled = statement.compile(dialect=dialect)
        out.append(compiled.string)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_write_outside_mechanism_refused() -> 'None':
    """ An insert on an engine of the Zato database outside of every mechanism is refused before it reaches the database.
    """
    name = uuid4().hex

    with zato_database_engine() as engine:

        with pytest.raises(WritePathViolation):
            _insert_in_transaction(engine, _new_shared_object_insert(name))

        assert _count_shared_objects(engine, name) == 0

# ################################################################################################################################

def test_serialized_write_accepted() -> 'None':
    """ The same insert through a serialized write is committed.
    """
    name = uuid4().hex

    with zato_database_engine() as engine:
        _ = execute_write(engine, _new_shared_object_insert(name))

        assert _count_shared_objects(engine, name) == 1

# ################################################################################################################################

def test_audit_table_refused_to_serialized_write() -> 'None':
    """ A serialized write cannot insert into a table of the audit log, which only its group commit,
    maintenance, schema creation, a takeover and a seed write.
    """
    with zato_database_engine() as engine:
        with pytest.raises(WritePathViolation):
            _ = execute_write(engine, _new_dedup_insert(uuid4().hex))

# ################################################################################################################################

def test_write_in_common_table_expression_outside_mechanism_refused() -> 'None':
    """ An insert in a common table expression of a select, outside of every mechanism, is refused
    before it reaches the database.
    """
    name = uuid4().hex

    with zato_database_engine() as engine:

        with pytest.raises(WritePathViolation):
            _insert_in_transaction(engine, _new_cte_write(_new_shared_object_insert(name), 'shared_object_written'))

        assert _count_shared_objects(engine, name) == 0

# ################################################################################################################################

def test_audit_table_in_common_table_expression_refused_to_serialized_write() -> 'None':
    """ A serialized write cannot insert into a table of the audit log in a common table expression of a select either.
    """
    with zato_database_engine() as engine:
        with pytest.raises(WritePathViolation):
            _ = execute_write(engine, _new_cte_write(_new_dedup_insert(uuid4().hex), 'dedup_written'))

# ################################################################################################################################

def test_write_deferred_to_greenlet_refused() -> 'None':
    """ A greenlet that a mechanism starts begins without the mark of the mechanism, so a write handed over to it
    is refused rather than committed after the mechanism ended.
    """
    name = uuid4().hex

    with zato_database_engine() as engine:

        with write_path(Mechanism.Serialized_Write):
            greenlet = gevent.spawn(_insert_in_transaction, engine, _new_shared_object_insert(name))

        with pytest.raises(WritePathViolation):
            greenlet.get()

        assert _count_shared_objects(engine, name) == 0

# ################################################################################################################################

def test_seed_cannot_change_rows() -> 'None':
    """ A seed inserts and removes rows, a table of the audit log included, and is refused when it changes one.
    """
    name = uuid4().hex

    with zato_database_engine() as engine:

        with write_path(Mechanism.Seed):
            _insert_in_transaction(engine, _new_shared_object_insert(name))
            _insert_in_transaction(engine, _new_dedup_insert(name))

            update = shared_object_table.update().where(shared_object_table.c.name == name).values(version=2)

            with pytest.raises(WritePathViolation), engine.begin() as connection:
                _ = connection.execute(update)

        assert _count_shared_objects(engine, name) == 1

# ################################################################################################################################

def test_cached_statement_refused_outside_mechanism() -> 'None':
    """ A write accepted under a mechanism is refused when the same statement runs again outside of every mechanism.
    """
    name = uuid4().hex

    with zato_database_engine() as engine:

        with write_path(Mechanism.Serialized_Write):
            _execute_and_roll_back(engine, _new_shared_object_insert(name))

        hits_before = _parse_statement.cache_info().hits

        with pytest.raises(WritePathViolation):
            _insert_in_transaction(engine, _new_shared_object_insert(name))

        # The second execution took the parse of the first one
        assert _parse_statement.cache_info().hits > hits_before
        assert _count_shared_objects(engine, name) == 0

# ################################################################################################################################

def test_cached_audit_statement_refused_to_other_mechanism() -> 'None':
    """ A write to a table of the audit log accepted under a group commit is refused when the same statement runs again
    under a serialized write.
    """
    dedup_key = uuid4().hex

    with zato_database_engine() as engine:

        with write_path(Mechanism.Group_Commit):
            _execute_and_roll_back(engine, _new_dedup_insert(dedup_key))

        with write_path(Mechanism.Serialized_Write), pytest.raises(WritePathViolation):
            _execute_and_roll_back(engine, _new_dedup_insert(dedup_key))

# ################################################################################################################################

def test_cached_update_refused_to_seed() -> 'None':
    """ A seed inserts a row, and an update accepted under a serialized write is refused when the same statement
    runs again under the seed.
    """
    name = uuid4().hex
    update = shared_object_table.update().where(shared_object_table.c.name == name).values(version=2)

    with zato_database_engine() as engine:

        with write_path(Mechanism.Seed):
            _execute_and_roll_back(engine, _new_shared_object_insert(name))

        with write_path(Mechanism.Serialized_Write):
            _execute_and_roll_back(engine, update)

        with write_path(Mechanism.Seed), pytest.raises(WritePathViolation):
            _execute_and_roll_back(engine, update)

# ################################################################################################################################

def test_cached_write_in_common_table_expression_refused_outside_mechanism() -> 'None':
    """ An insert in a common table expression accepted under a mechanism is refused when the same statement runs again
    outside of every mechanism.
    """
    name = uuid4().hex

    with zato_database_engine() as engine:

        with write_path(Mechanism.Serialized_Write):
            _execute_and_roll_back(engine, _new_cte_write(_new_shared_object_insert(name), 'shared_object_written'))

        with pytest.raises(WritePathViolation):
            _insert_in_transaction(engine, _new_cte_write(_new_shared_object_insert(name), 'shared_object_written'))

        assert _count_shared_objects(engine, name) == 0

# ################################################################################################################################

def test_evicted_statement_refused_outside_mechanism() -> 'None':
    """ A write accepted under a mechanism, whose parse the cache evicted, is parsed again and refused outside
    of every mechanism.
    """
    name = uuid4().hex

    with zato_database_engine() as engine:

        with write_path(Mechanism.Serialized_Write):
            _execute_and_roll_back(engine, _new_shared_object_insert(name))

        # The cache is filled beyond its size with statements that read only ..
        for idx in range(WritePathCtx.Max_Parsed_Statements):
            _ = _parse_statement(ModuleCtx.Filler_Statement.format(idx))

        misses_before = _parse_statement.cache_info().misses

        # .. so the write is parsed again and refused.
        with pytest.raises(WritePathViolation):
            _insert_in_transaction(engine, _new_shared_object_insert(name))

        assert _parse_statement.cache_info().misses > misses_before
        assert _count_shared_objects(engine, name) == 0

# ################################################################################################################################

def test_parse_matches_uncached_patterns() -> 'None':
    """ Each statement of the platform has the same write keywords and table names from the cache of the parses
    as from the patterns of the guard applied without it.
    """
    for statement in _get_platform_statements():
        assert _parse_statement(statement) == _parse_uncached(statement), statement

# ################################################################################################################################
# ################################################################################################################################
