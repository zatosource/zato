# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Read-side helpers for server-level pub/sub tests - they open the same database
# the test server uses, selected through the Zato_PubSub_DB_* environment variables
# that the shared server fixture points at the current quickstart directory.

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.pubsub.sql.schema import delivery_table, message_table, topic_sub_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

def get_subscribed_topics(sub_key:'str') -> 'strlist':
    """ Returns the names of all the topics a subscriber holds subscription rows for.
    """
    query = select(topic_sub_table.c.topic_name)
    query = query.where(topic_sub_table.c.sub_key == sub_key)

    engine = get_pubsub_engine()

    out:'strlist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(row.topic_name)

    return out

# ################################################################################################################################

def get_topic_subscribers(topic_name:'str') -> 'strlist':
    """ Returns the sub_keys of all the subscribers a topic has subscription rows for.
    """
    query = select(topic_sub_table.c.sub_key)
    query = query.where(topic_sub_table.c.topic_name == topic_name)

    engine = get_pubsub_engine()

    out:'strlist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(row.sub_key)

    return out

# ################################################################################################################################

def count_topic_messages(topic_name:'str') -> 'int':
    """ Counts all of one topic's message rows, delivered traces included.
    """
    query = select(func.count())
    query = query.select_from(message_table)
    query = query.where(message_table.c.topic_name == topic_name)

    engine = get_pubsub_engine()

    with engine.connect() as connection:
        out = connection.execute(query).scalar()

    return out

# ################################################################################################################################

def count_pending(sub_key:'str', topic_name:'str'='') -> 'int':
    """ Counts a subscriber's delivery rows, optionally within one topic only.
    """
    query = select(func.count())
    query = query.select_from(delivery_table)
    query = query.where(delivery_table.c.sub_key == sub_key)

    if topic_name:
        query = query.where(delivery_table.c.topic_name == topic_name)

    engine = get_pubsub_engine()

    with engine.connect() as connection:
        out = connection.execute(query).scalar()

    return out

# ################################################################################################################################

def count_topic_deliveries(topic_name:'str') -> 'int':
    """ Counts all the delivery rows of one topic across every subscriber.
    """
    query = select(func.count())
    query = query.select_from(delivery_table)
    query = query.where(delivery_table.c.topic_name == topic_name)

    engine = get_pubsub_engine()

    with engine.connect() as connection:
        out = connection.execute(query).scalar()

    return out

# ################################################################################################################################

def get_pending_msg_ids(sub_key:'str') -> 'strlist':
    """ Returns the public message identifiers of everything still pending for a subscriber.
    """
    join_clause = delivery_table.join(message_table, message_table.c.id == delivery_table.c.message_id)

    query = select(message_table.c.msg_id)
    query = query.select_from(join_clause)
    query = query.where(delivery_table.c.sub_key == sub_key)

    engine = get_pubsub_engine()

    out:'strlist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(row.msg_id)

    return out

# ################################################################################################################################

def count_message_rows(msg_ids:'strlist') -> 'int':
    """ Counts how many of the given messages still have a row in the database,
    no matter whether their payloads were already dropped.
    """
    query = select(func.count())
    query = query.select_from(message_table)
    query = query.where(message_table.c.msg_id.in_(msg_ids))

    engine = get_pubsub_engine()

    with engine.connect() as connection:
        out = connection.execute(query).scalar()

    return out

# ################################################################################################################################

def count_messages_with_payload(msg_ids:'strlist') -> 'int':
    """ Counts how many of the given messages still hold their payload -
    the payload column is nulled once every subscriber has acknowledged a message.
    """
    query = select(func.count())
    query = query.select_from(message_table)
    query = query.where(message_table.c.msg_id.in_(msg_ids))
    query = query.where(message_table.c.payload.isnot(None))

    engine = get_pubsub_engine()

    with engine.connect() as connection:
        out = connection.execute(query).scalar()

    return out

# ################################################################################################################################

def delete_all_messages() -> 'None':
    """ Removes every message and delivery row so no in-flight deliveries leak
    across tests, while the subscription state stays as the server knows it.
    """
    engine = get_pubsub_engine()

    with engine.begin() as connection:
        _ = connection.execute(delivery_table.delete())
        _ = connection.execute(message_table.delete())

# ################################################################################################################################

def remove_topic_subscriptions(topic_name:'str') -> 'None':
    """ Removes all of one topic's subscription rows straight from the database,
    the way tests simulate a subscription that disappeared behind the server's back.
    """
    delete_statement = topic_sub_table.delete()
    delete_statement = delete_statement.where(topic_sub_table.c.topic_name == topic_name)

    engine = get_pubsub_engine()

    with engine.begin() as connection:
        _ = connection.execute(delete_statement)

# ################################################################################################################################
# ################################################################################################################################
