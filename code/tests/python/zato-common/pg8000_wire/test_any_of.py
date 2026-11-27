# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import column, select, table
from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite

# Zato
from zato.common.common_db.message_dedup import dedup_records_query, dedup_upsert
from zato.common.common_db.schema import message_dedup_table
from zato.common.db_env.any_of import any_of
from zato.common.pubsub.sql import dedup, fenced_ack, payloads, pull, writes
from zato.common.pubsub.sql.schema import metadata as pubsub_metadata

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.db_env.plain_sql import PlainStatement
    from zato.common.typing_ import any_, anydict, anylist

    any_ = any_
    anydict = anydict
    anylist = anylist
    Engine = Engine
    PlainStatement = PlainStatement

# ################################################################################################################################
# ################################################################################################################################

# The numbers of values that each statement is executed with
_value_counts = (1, 3, 17)

# The values of the parameters that are not lists, by their names
_scalar_values:'anydict' = {
    'dedup_kind': 'pubsub',
    'dedup_scope': 'orders',
    'fenced_sub_key': 'zpsk.orders.1',
    'fetch_sub_key': 'zpsk.orders.1',
    'fetch_now_ms': 1_700_000_000_000,
    'fetch_max_messages': 50,
    'fetch_is_unrestricted': False,
    'probe_sub_key': 'zpsk.orders.1',
    'probe_now_ms': 1_700_000_000_000,
    'probe_is_unrestricted': False,
    'lease_sub_key': 'zpsk.orders.1',
    'lease_now_ms': 1_700_000_000_000,
    'lease_max_messages': 50,
    'lease_max_len': 1_000_000,
    'lease_leased_until_ms': 1_700_000_060_000,
    'lease_is_unrestricted': False,
}

# Each statement whose list parameters are bound as arrays on PostgreSQL, with the names of its list parameters
# and whether the elements of each are integers.
_statements:'anylist' = [
    (writes._subscribers_query_plain, {'write_topic_names': False}),
    (writes._existing_messages_query_plain, {'write_msg_ids': False}),
    (writes._ack_deliveries_query_plain, {'ack_message_ids': True, 'ack_sub_keys': False}),
    (writes._delivery_delete_plain, {'ack_delivery_ids': True}),
    (writes._record_attempts_statement_plain, {'attempt_delivery_ids': True}),
    (payloads._message_ids_query_plain, {'write_msg_ids': False}),
    (payloads._drop_payloads_statement_plain, {'drop_message_ids': True}),
    (payloads._lock_messages_query_plain, {'drop_message_ids': True}),
    (payloads._needed_messages_query_plain, {'drop_message_ids': True}),
    (fenced_ack._fenced_rows_query_plain, {'fenced_msg_ids': False}),
    (fenced_ack._fenced_delete_plain, {'fenced_delivery_ids': True}),
    (dedup._fingerprint_rewrite, {'dedup_message_ids': False}),
    (dedup._existing_fingerprints_query, {'write_msg_ids': False, 'dedup_message_ids': False}),
    (dedup_records_query, {'dedup_message_ids': False}),
    (pull.payload_statement, {'payload_message_ids': True}),
    (pull.fetch_statement, {'fetch_delivered_topics': False}),
    (pull._lease_probe_statement, {'probe_delivered_topics': False}),
    (pull._lease_statement, {'lease_delivered_topics': False}),
]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def schema_engine(engine:'Engine') -> 'Engine':
    """ An engine of a database with the pub/sub tables and the table of dedup records.
    """
    pubsub_metadata.create_all(engine)
    message_dedup_table.create(engine, checkfirst=True)

    return engine

# ################################################################################################################################

def _new_parameters(statement:'PlainStatement', list_names:'anydict', value_count:'int') -> 'anydict':
    """ Returns the parameters of a statement, each of its lists with as many values as given.
    """
    out:'anydict' = {}

    compiled = statement.statement.compile()

    for name in compiled.params:
        if name in _scalar_values:
            out[name] = _scalar_values[name]

    for name, is_integer in list_names.items():
        values:'anylist' = []

        for idx in range(value_count):
            if is_integer:
                values.append(idx + 1)
            else:
                values.append(f'{name}-{idx}')

        out[name] = values

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOnePlan:
    """ On PostgreSQL, a statement with list parameters has one text, and so one plan, whatever the number of the values.
    """

    def test_list_parameters(self, schema_engine:'Engine') -> 'None':

        for statement, list_names in _statements:

            with schema_engine.connect() as connection:
                transaction = connection.begin()

                for value_count in _value_counts:
                    parameters = _new_parameters(statement, list_names, value_count)
                    _ = statement.execute(connection, parameters).fetchall()

                transaction.rollback()

            assert len(statement._plans) == 1, statement.statement

    def test_inserts(self, schema_engine:'Engine') -> 'None':

        with schema_engine.connect() as connection:
            transaction = connection.begin()

            for value_count in _value_counts:

                rows:'anylist' = []

                for idx in range(value_count):
                    rows.append({'sub_key': f'zpsk.orders.{value_count}.{idx}', 'topic_name': 'orders'})

                inserted = writes._topic_sub_insert_plain.insert_rows(connection, rows)
                assert inserted == []

            transaction.rollback()

        assert len(writes._topic_sub_insert_plain._plans) == 1

    def test_insert_returning(self, schema_engine:'Engine') -> 'None':

        with schema_engine.connect() as connection:
            transaction = connection.begin()

            for value_count in _value_counts:

                rows:'anylist' = []

                for idx in range(value_count):
                    message_id = f'msg-{value_count}-{idx}'
                    rows.append({
                        'kind': 'pubsub',
                        'scope': 'orders',
                        'message_id': message_id,
                        'fingerprint': f'orders:{idx}',
                        'received_ms': 1_700_000_000_000,
                        'expires_ms': 1_700_000_600_000,
                    })

                returned_ids:'anylist' = []

                for row in dedup_upsert.insert_rows(connection, rows):
                    returned_ids.append(row.message_id)

                expected_ids:'anylist' = []

                for row in rows:
                    expected_ids.append(row['message_id'])

                assert sorted(returned_ids) == sorted(expected_ids)

            transaction.rollback()

        assert len(dedup_upsert._plans) == 1

# ################################################################################################################################
# ################################################################################################################################

class TestOtherDatabases:
    """ On any database other than PostgreSQL, the membership in a list is an expanding IN.
    """

    def test_sqlite(self) -> 'None':
        orders = table('orders', column('id'))

        query = select(orders.c.id)
        query = query.where(any_of(orders.c.id, 'order_ids'))

        compiled = query.compile(dialect=SQLiteDialect_pysqlite())
        assert compiled.string.endswith('WHERE orders.id IN (__[POSTCOMPILE_order_ids])'), compiled.string

# ################################################################################################################################
# ################################################################################################################################
