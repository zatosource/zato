# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import contextmanager

# SQLAlchemy
from sqlalchemy import select

# Zato
from live_sql.asserts import assert_mysql_connection_encrypted as assert_mysql_engine_encrypted, \
    assert_postgresql_connection_encrypted as assert_postgresql_engine_encrypted
from live_sql.env import database_env
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.pubsub.sql.schema import delivery_table, message_table, topic_sub_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import anylist, stranydict

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The prefix all the pub/sub database environment variables share.
_env_prefix = 'Zato_PubSub_DB_'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def pubsub_backend_env(details:'stranydict') -> 'envgen':
    """ Points the Zato_PubSub_DB_* variables at one backend for the duration of a test.
    """
    with database_env(_env_prefix, details):
        yield

# ################################################################################################################################

def delete_all_rows() -> 'None':
    """ Starts a scenario from empty tables because containers can be reused between test runs.
    """
    engine = get_pubsub_engine()

    with engine.begin() as connection:
        _ = connection.execute(delivery_table.delete())
        _ = connection.execute(message_table.delete())
        _ = connection.execute(topic_sub_table.delete())

# ################################################################################################################################

def get_message_rows(topic_name:'str') -> 'anylist':
    """ Reads all of one topic's message rows straight from the database,
    bypassing the backend - what schema-level assertions look at.
    """
    engine = get_pubsub_engine()

    query = select(message_table)
    query = query.where(message_table.c.topic_name == topic_name)
    query = query.order_by(message_table.c.id)

    with engine.connect() as connection:
        out = connection.execute(query).fetchall()

    return out

# ################################################################################################################################

def get_delivery_rows(sub_key:'str') -> 'anylist':
    """ Reads all of one subscriber's delivery rows straight from the database.
    """
    engine = get_pubsub_engine()

    query = select(delivery_table)
    query = query.where(delivery_table.c.sub_key == sub_key)
    query = query.order_by(delivery_table.c.id)

    with engine.connect() as connection:
        out = connection.execute(query).fetchall()

    return out

# ################################################################################################################################

def assert_mysql_connection_encrypted() -> 'None':
    """ Confirms that the current MySQL session is encrypted.
    """
    engine = get_pubsub_engine()
    assert_mysql_engine_encrypted(engine)

# ################################################################################################################################

def assert_postgresql_connection_encrypted() -> 'None':
    """ Confirms that the current PostgreSQL session is encrypted.
    """
    engine = get_pubsub_engine()
    assert_postgresql_engine_encrypted(engine)

# ################################################################################################################################
# ################################################################################################################################
