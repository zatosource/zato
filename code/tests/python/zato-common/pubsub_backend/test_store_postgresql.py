# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import inspect, text

# Zato
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.pubsub.sql.schema import metadata
from zato.common.test.pubsub_database import pubsub_db_env, PubSubDBMode, start_pubsub_database, stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

_expected_tables = {
    'pubsub_active',
    'pubsub_delivery',
    'pubsub_message',
    'pubsub_publish_count',
    'pubsub_queue_count',
    'pubsub_topic_count',
    'pubsub_topic_sub',
}

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
}

_high_churn_options = [
    'autovacuum_vacuum_scale_factor=0.01',
    'autovacuum_vacuum_insert_scale_factor=0.01',
    'autovacuum_analyze_scale_factor=0.02',
]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def pubsub_database() -> 'any_':
    database = start_pubsub_database('store', PubSubDBMode.PostgreSQL)

    try:
        yield database
    finally:
        stop_pubsub_database(database)

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

        engine = get_pubsub_engine()
        inspector = inspect(engine)

        # The tables ..
        table_names = set(inspector.get_table_names())
        assert table_names == _expected_tables, table_names

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

            # .. the generation row ..
            generation = connection.execute(text('select generation from pubsub_active where id = 1')).scalar()
            assert generation == 0, generation

            # .. the compression of the payloads ..
            compression = connection.execute(text("""
                select attcompression from pg_attribute
                where attrelid = 'pubsub_message'::regclass and attname = 'payload'
            """)).scalar()

            assert compression == 'l', compression

            # .. and the storage parameters of the tables and of the TOAST table of the messages.
            table_query = 'select reloptions from pg_class where oid = cast(:table_name as regclass)'
            toast_query = """
                select toast.reloptions from pg_class main join pg_class toast on toast.oid = main.reltoastrelid
                where main.oid = cast(:table_name as regclass)
            """

            for table_name in ('pubsub_message', 'pubsub_delivery'):
                options = _get_options(connection, table_query, table_name)
                assert 'fillfactor=90' in options, (table_name, options)

            for table_name in ('pubsub_message', 'pubsub_delivery', *_count_key_indexes):
                options = _get_options(connection, table_query, table_name)
                for option in _high_churn_options:
                    assert option in options, (table_name, options)

            toast_options = _get_options(connection, toast_query, 'pubsub_message')
            assert 'autovacuum_vacuum_scale_factor=0.01' in toast_options, toast_options

# ################################################################################################################################

def test_postgresql_schema_created_once(pubsub_database:'PubSubDatabase') -> 'None':
    """ Creating the schema again, as each new process does, changes nothing and raises nothing.
    """
    with pubsub_db_env(pubsub_database.env):

        engine = get_pubsub_engine()
        metadata.create_all(engine)

        inspector = inspect(engine)
        assert set(inspector.get_table_names()) == _expected_tables

# ################################################################################################################################
# ################################################################################################################################
