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
from zato.common.audit_log.api import event_attr_table, event_body_table, event_link_table, event_table, AuditEvent, \
    AuditSource
from zato.common.audit_log.common import event_count_table, event_dedup_table, event_open_table, event_payload_table
from zato.common.db_env.database import get_database_engine
from zato.common.pubsub.sql.schema import delivery_table, message_table, publish_count_table, queue_count_table, \
    topic_count_table, topic_sub_table
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.test.direct_sql.fault import interrupt_topic_rename
from zato.common.test.direct_sql.reset import reset_table_rows

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy import Column
    from zato.common.typing_ import anylist, intset

    anylist = anylist
    Column = Column
    intset = intset

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def pubsub_path_env(db_path:'str') -> 'envgen':
    """ Points Zato_Database_Path at one SQLite file for the duration of a test.
    """
    old_path = os.environ.get(DatabaseEnv.Env_Path)
    os.environ[DatabaseEnv.Env_Path] = db_path

    try:
        yield
    finally:
        if old_path is None:
            _ = os.environ.pop(DatabaseEnv.Env_Path, None)
        else:
            os.environ[DatabaseEnv.Env_Path] = old_path

# ################################################################################################################################

def delete_all_rows() -> 'None':
    """ Starts a scenario from empty tables because containers can be reused between test runs.
    """
    engine = get_database_engine()
    tables = [delivery_table, message_table, topic_sub_table, queue_count_table, topic_count_table, publish_count_table]

    reset_table_rows(engine, tables)

# ################################################################################################################################

def delete_audit_rows() -> 'None':
    """ Starts a scenario from empty audit tables, which the publications and pulls of the earlier scenarios wrote to.
    """
    engine = get_database_engine()

    # The counts and the open exchanges are emptied last, after the triggers of the deleted events have written to them.
    tables = [event_attr_table, event_body_table, event_link_table, event_dedup_table, event_table, event_payload_table,
        event_count_table, event_open_table]

    reset_table_rows(engine, tables)

# ################################################################################################################################

def get_received_event_rows(topic_name:'str') -> 'anylist':
    """ Reads the audit events of the messages of one topic that pulls handed out, each with the text of its payload,
    in the order of their ids.
    """
    engine = get_database_engine()

    query = select(event_table, event_payload_table.c.data)
    query = query.select_from(event_table.outerjoin(event_payload_table, event_table.c.payload_id == event_payload_table.c.id))
    query = query.where(event_table.c.source == AuditSource.PubSub)
    query = query.where(event_table.c.event_type == AuditEvent.Received)
    query = query.where(event_table.c.object_name == topic_name)
    query = query.order_by(event_table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            values = dict(row._mapping)
            out.append(values)

    return out

# ################################################################################################################################

def get_event_ids(column:'Column') -> 'intset':
    """ Returns the ids of the events that one column of a companion table of the audit log refers to.
    """
    engine = get_database_engine()

    query = select(column)

    out:'intset' = set()

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.add(row[0])

    return out

# ################################################################################################################################

def get_message_rows(topic_name:'str') -> 'anylist':
    """ Reads all of one topic's message rows straight from the database,
    bypassing the backend - what schema-level assertions look at.
    """
    engine = get_database_engine()

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
    engine = get_database_engine()

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
    engine = get_database_engine()

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
    engine = get_database_engine()
    interrupt_topic_rename(engine, old_topic_name, new_topic_name)

# ################################################################################################################################
# ################################################################################################################################
