# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import inspect, MetaData, text

# Zato
from zato.common.db_env.database import database_config, get_database_engine
from zato.common.db_env.engine import create_schema
from zato.common.pubsub.sql.counts import postgresql_function, register_triggers
from zato.common.pubsub.sql.schema import metadata
from zato.common.test.pubsub_database import get_suite_modes, pubsub_db_env, PubSubDBMode, start_pubsub_database, \
    stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, strlist, strset

# ################################################################################################################################
# ################################################################################################################################

# The count tables hold insert-only change rows on PostgreSQL, so their keys are indexed, not unique.
_count_key_indexes = {
    'pubsub_queue_count': 'idx_pubsub_queue_count_key',
    'pubsub_topic_count': 'idx_pubsub_topic_count_key',
    'pubsub_publish_count': 'idx_pubsub_publish_count_key',
}

_expected_triggers = {
    ('pubsub_delivery', 'pubsub_queue_count_insert'),
    ('pubsub_delivery', 'pubsub_queue_count_delete'),
    ('pubsub_delivery', 'pubsub_queue_count_update'),
    ('pubsub_message', 'pubsub_topic_count_insert'),
    ('pubsub_message', 'pubsub_topic_count_delete'),
    ('pubsub_message', 'pubsub_topic_count_update'),
    ('pubsub_message', 'pubsub_trace_insert'),
    ('pubsub_message', 'pubsub_trace_delete'),
}

# The trigger that kept the traces in step with every update of the messages, which the schema setup removes
# from a database created before the statements that update the messages took this over.
_dropped_trigger = ('pubsub_message', 'pubsub_trace_update')

_dropped_trigger_statement = 'CREATE TRIGGER pubsub_trace_update AFTER UPDATE ON pubsub_message ' + \
    'REFERENCING NEW TABLE AS new_rows FOR EACH STATEMENT EXECUTE FUNCTION pubsub_trace_update()'

_dropped_function_query = "select 1 from pg_proc where proname = 'pubsub_trace_update'"

_dropped_trigger_query = """
    select 1 from pg_trigger
    where tgname = 'pubsub_trace_update' and tgrelid = cast('pubsub_message' as regclass)
"""

# The pages of the tables whose rows are updated after their insert keep half of their space free.
_updated_fillfactor = 'fillfactor=50'

_high_churn_options = [
    'autovacuum_vacuum_scale_factor=0.01',
    'autovacuum_vacuum_insert_scale_factor=0.01',
    'autovacuum_analyze_scale_factor=0.02',
]

# ################################################################################################################################
# ################################################################################################################################

_modes = get_suite_modes([PubSubDBMode.PostgreSQL])

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module', params=_modes)
def pubsub_database(request:'pytest.FixtureRequest') -> 'any_':
    database = start_pubsub_database('store', request.param)

    try:
        yield database
    finally:
        stop_pubsub_database(database)

# ################################################################################################################################

def _get_expected_tables() -> 'strset':
    """ Returns the names of the tables of every schema of the Zato database, all of which the engine creates.
    """
    out:'strset' = set()

    for schema_metadata in database_config.metadata_tuple:
        for table_name in schema_metadata.tables:
            out.add(table_name)

    return out

# ################################################################################################################################

def _get_options(connection:'Connection', relation_query:'str', table_name:'str') -> 'strlist':
    """ Returns the storage parameters of a table or of its TOAST table.
    """
    result = connection.execute(text(relation_query), {'table_name': table_name}).scalar()

    if result is None:
        out:'strlist' = []
    else:
        out = list(result)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_postgresql_schema(pubsub_database:'PubSubDatabase') -> 'None':
    """ The tables, the indexes of the count keys, the trigger functions and the storage parameters exist on PostgreSQL.
    """
    with pubsub_db_env(pubsub_database.env):

        engine = get_database_engine()
        inspector = inspect(engine)

        # The tables ..
        table_names = set(inspector.get_table_names())
        assert table_names == _get_expected_tables(), table_names

        # .. the count tables have no primary key, only an index of their keys ..
        for table_name, index_name in _count_key_indexes.items():

            primary_key = inspector.get_pk_constraint(table_name)
            assert primary_key['constrained_columns'] == [], (table_name, primary_key)

            index_names:'strlist' = []
            for index in inspector.get_indexes(table_name):
                index_names.append(index['name'])

            assert index_name in index_names, (table_name, index_names)

        with engine.connect() as connection:

            # .. the triggers that write the change rows ..
            trigger_rows = connection.execute(text("""
                select event_object_table, trigger_name from information_schema.triggers
                where trigger_schema = current_schema()
            """)).fetchall()

            triggers:'set[tuple[str, str]]' = set()
            for row in trigger_rows:
                triggers.add((row.event_object_table, row.trigger_name))

            assert _expected_triggers <= triggers, triggers
            assert _dropped_trigger not in triggers, triggers

            # .. the generation row ..
            generation = connection.execute(text('select generation from zato_active where id = 1')).scalar()
            assert generation == 0, generation

            # .. and the storage parameters of the tables.
            table_query = 'select reloptions from pg_class where oid = cast(:table_name as regclass)'

            for table_name in ('pubsub_message', 'pubsub_delivery'):
                options = _get_options(connection, table_query, table_name)
                assert _updated_fillfactor in options, (table_name, options)

            for table_name in ('pubsub_message', 'pubsub_delivery', 'pubsub_trace', 'pubsub_released_payload',
                *_count_key_indexes):
                options = _get_options(connection, table_query, table_name)
                for option in _high_churn_options:
                    assert option in options, (table_name, options)

# ################################################################################################################################

def test_postgresql_schema_created_once(pubsub_database:'PubSubDatabase') -> 'None':
    """ Creating the schema again, as each new process does, changes nothing and raises nothing.
    """
    with pubsub_db_env(pubsub_database.env):

        engine = get_database_engine()
        create_schema(engine, metadata)

        inspector = inspect(engine)
        assert set(inspector.get_table_names()) == _get_expected_tables()

# ################################################################################################################################

def test_postgresql_schema_drops_trace_update_trigger(pubsub_database:'PubSubDatabase') -> 'None':
    """ Creating the schema over a database that still has the trigger of the trace updates removes the trigger
    and its function.
    """
    with pubsub_db_env(pubsub_database.env):

        engine = get_database_engine()

        # A database created before the change holds the trigger and its function, which a schema of its own
        # creates over the tables that exist ..
        legacy_metadata = MetaData()
        legacy_function = postgresql_function('pubsub_trace_update', '')
        legacy_trigger = ('pubsub_trace_update', 'pubsub_message', _dropped_trigger_statement)
        register_triggers(legacy_metadata, [([legacy_function], [legacy_trigger])])

        create_schema(engine, legacy_metadata)

        with engine.connect() as connection:
            assert connection.execute(text(_dropped_trigger_query)).scalar() == 1

        # .. and the schema setup of the next process removes them.
        create_schema(engine, metadata)

        with engine.connect() as connection:
            assert connection.execute(text(_dropped_trigger_query)).scalar() is None
            assert connection.execute(text(_dropped_function_query)).scalar() is None

# ################################################################################################################################
# ################################################################################################################################
