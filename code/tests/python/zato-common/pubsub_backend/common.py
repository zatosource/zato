# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import contextmanager

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.pubsub.sql.config import get_pubsub_engine, ModuleCtx
from zato.common.pubsub.sql.schema import delivery_table, message_table, topic_sub_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import anylist

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def pubsub_path_env(db_path:'str') -> 'envgen':
    """ Points Zato_PubSub_DB_Path at one SQLite file for the duration of a test.
    """
    old_path = os.environ.get(ModuleCtx.Env_Path)
    os.environ[ModuleCtx.Env_Path] = db_path

    try:
        yield
    finally:
        if old_path is None:
            _ = os.environ.pop(ModuleCtx.Env_Path, None)
        else:
            os.environ[ModuleCtx.Env_Path] = old_path

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

def get_sub_rows(sub_key:'str') -> 'anylist':
    """ Reads all of one subscriber's subscription rows straight from the database, which is
    what tells how many queues a connection has and what topic each of them is under.
    """
    engine = get_pubsub_engine()

    query = select(topic_sub_table)
    query = query.where(topic_sub_table.c.sub_key == sub_key)
    query = query.order_by(topic_sub_table.c.topic_name)

    with engine.connect() as connection:
        out = connection.execute(query).fetchall()

    return out

# ################################################################################################################################

def move_message_rows(old_topic_name:'str', new_topic_name:'str') -> 'None':
    """ Moves one topic's message rows and nothing else, which is what a rename interrupted
    halfway through leaves behind - the deliveries and the subscription still under the old name.
    """
    engine = get_pubsub_engine()

    update_statement = message_table.update()
    update_statement = update_statement.where(message_table.c.topic_name == old_topic_name)
    update_statement = update_statement.values(topic_name=new_topic_name)

    with engine.begin() as connection:
        _ = connection.execute(update_statement)

# ################################################################################################################################
# ################################################################################################################################
