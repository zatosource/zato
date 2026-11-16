# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import select

# Zato
from common import delete_all_rows, get_delivery_rows, get_message_rows
from zato.common.db_env.engine import call_database
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.pubsub.sql.config import get_pull_lease_seconds
from zato.common.pubsub.sql.publication import build_publication
from zato.common.pubsub.sql.pull import lease_messages
from zato.common.pubsub.sql.schema import delivery_table, message_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.publication import BuiltPublication
    from zato.common.typing_ import anylist, strintdict, strnone

# ################################################################################################################################
# ################################################################################################################################

# The topic that the consumed messages are published to, and its subscriber
In_Topic   = 'exactly-once.backend.in'
In_Sub_Key = 'zpsk.exactly-once.backend.in'

# The topics that the publications of an acknowledgement go to, each with its own subscriber
Out_Topic_A   = 'exactly-once.backend.out.a'
Out_Topic_B   = 'exactly-once.backend.out.b'
Out_Sub_Key_A = 'zpsk.exactly-once.backend.out.a'
Out_Sub_Key_B = 'zpsk.exactly-once.backend.out.b'

# How many messages one lease may hand out and how many bytes of their payloads
_lease_max_messages = 50
_lease_max_len = 10_000_000

# One second expressed in milliseconds
_ms_per_second = 1000

# ################################################################################################################################
# ################################################################################################################################

def new_backend() -> 'SQLPubSubBackend':
    """ Returns a backend over empty tables, with one subscriber of the input topic and one of each output topic.
    """
    delete_all_rows()

    out = SQLPubSubBackend()

    out.subscribe(In_Sub_Key, In_Topic)
    out.subscribe(Out_Sub_Key_A, Out_Topic_A)
    out.subscribe(Out_Sub_Key_B, Out_Topic_B)

    return out

# ################################################################################################################################

def get_lease_ms() -> 'int':
    """ Returns how long a pull leases a message, in milliseconds.
    """
    out = get_pull_lease_seconds() * _ms_per_second
    return out

# ################################################################################################################################

def lease(backend:'SQLPubSubBackend', now_ms:'int', max_messages:'int'=_lease_max_messages) -> 'strintdict':
    """ Leases the deliverable messages of the input subscriber as of the given time,
    and returns the delivery attempt of each, by its message ID.
    """
    engine = backend.engine
    leased_until_ms = now_ms + get_lease_ms()

    rows, attempts = call_database(engine, lease_messages, engine, In_Sub_Key, max_messages, _lease_max_len,
        now_ms, leased_until_ms)

    out:'strintdict' = {}

    for row in rows:
        out[row.msg_id] = attempts[row.id]

    return out

# ################################################################################################################################

def lease_again(backend:'SQLPubSubBackend', now_ms:'int', count:'int') -> 'tuple[strintdict, int]':
    """ Leases the messages of the input subscriber the given number of times, each time after the previous lease
    ran out, and returns what the last lease handed out and the time it was taken at.
    """
    out:'strintdict' = {}
    lease_now_ms = now_ms

    for index in range(count):
        lease_now_ms = now_ms + index * (get_lease_ms() + 1)
        out = lease(backend, lease_now_ms)

    return out, lease_now_ms

# ################################################################################################################################

def build(backend:'SQLPubSubBackend', topic_name:'str', data:'str', msg_id:'strnone'=None) -> 'BuiltPublication':
    """ Builds one publication of an acknowledgement.
    """
    out = build_publication(backend, topic_name, data, msg_id=msg_id)
    return out

# ################################################################################################################################

def publish_input(backend:'SQLPubSubBackend', data:'str', expiration:'int'=3600) -> 'str':
    """ Publishes one message to the input topic and returns its message ID.
    """
    result = backend.publish(In_Topic, data, expiration=expiration)
    return result.msg_id

# ################################################################################################################################

def count_messages(topic_name:'str') -> 'int':
    """ Returns how many messages of a topic are stored.
    """
    rows = get_message_rows(topic_name)
    return len(rows)

# ################################################################################################################################

def count_deliveries(sub_key:'str') -> 'int':
    """ Returns how many delivery rows a subscriber has.
    """
    rows = get_delivery_rows(sub_key)
    return len(rows)

# ################################################################################################################################

def get_attempt(backend:'SQLPubSubBackend', msg_id:'str') -> 'int':
    """ Returns the delivery attempt that the delivery row of the input subscriber for a message holds.
    """
    query = select(delivery_table.c.attempt)
    query = query.select_from(delivery_table.join(message_table, message_table.c.id == delivery_table.c.message_id))
    query = query.where(delivery_table.c.sub_key == In_Sub_Key)
    query = query.where(message_table.c.msg_id == msg_id)

    with backend.engine.connect() as connection:
        out = connection.execute(query).scalar_one()

    return out

# ################################################################################################################################

def expire_lease(backend:'SQLPubSubBackend', now_ms:'int') -> 'None':
    """ Makes the leases of the input subscriber run out before the given time, with no other pull taking place.
    """
    statement = delivery_table.update()
    statement = statement.where(delivery_table.c.sub_key == In_Sub_Key)
    statement = statement.values(leased_until_ms=now_ms - 1)

    with backend.engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def get_msg_ids(topic_name:'str') -> 'anylist':
    """ Returns the message IDs of the messages of a topic, in the order of their primary keys.
    """
    out:'anylist' = []

    for row in get_message_rows(topic_name):
        out.append(row.msg_id)

    return out

# ################################################################################################################################
# ################################################################################################################################

class FutureCleanup(PubSubCleanup):
    """ A cleanup whose sweeps run as if the clock of the database were ahead by the given number of milliseconds.
    """

    def __init__(self, offset_ms:'int') -> 'None':
        super().__init__()
        self.offset_ms = offset_ms

    def _database_now_ms(self) -> 'int':
        out = super()._database_now_ms() + self.offset_ms
        return out

# ################################################################################################################################
# ################################################################################################################################
