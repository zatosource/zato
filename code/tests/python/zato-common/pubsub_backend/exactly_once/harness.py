# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# SQLAlchemy
from sqlalchemy import select

# Zato
from common import delete_all_rows, get_delivery_rows, get_message_rows
from zato.common.db_env.engine import call_database
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.pubsub.sql.config import get_pull_lease_seconds
from zato.common.pubsub.sql.publication import build_publication
from zato.common.pubsub.sql.pull import lease_messages
from zato.common.pubsub.sql.schema import delivery_table, message_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.pubsub.sql.publication import BuiltPublication
    from zato.common.typing_ import anylist, intdict, strintdict, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

# The topic of the consumed messages and its subscriber
Input_Topic   = 'exactly-once.backend.input'
Input_Sub_Key = 'zpsk.exactly-once.backend.input'

# The topics that the publications of an acknowledgement go to, each with a subscriber of its own
First_Output_Topic    = 'exactly-once.backend.output.first'
Second_Output_Topic   = 'exactly-once.backend.output.second'
First_Output_Sub_Key  = 'zpsk.exactly-once.backend.output.first'
Second_Output_Sub_Key = 'zpsk.exactly-once.backend.output.second'

# How many messages one lease may hand out and how many bytes their payloads may have in total
_lease_max_messages = 50
_lease_max_len      = 10_000_000

# How long an input message remains in the queue, in seconds
_input_expiration = 3600

# One second and one day expressed in milliseconds
Milliseconds_Per_Second = 1000
Milliseconds_Per_Day    = 86_400_000

# ################################################################################################################################
# ################################################################################################################################

class LeaseResult(NamedTuple):
    """ The delivery attempt of each message that the last of several leases handed out, by message ID,
    and the time of that lease.
    """
    attempts: 'strintdict'
    now_ms: 'int'

# ################################################################################################################################
# ################################################################################################################################

def new_backend() -> 'SQLPubSubBackend':
    """ Returns a backend over empty tables, with one subscriber of the input topic and one of each output topic.
    """
    delete_all_rows()

    out = SQLPubSubBackend(audit_log=new_test_audit_log())

    out.subscribe(Input_Sub_Key, Input_Topic)
    out.subscribe(First_Output_Sub_Key, First_Output_Topic)
    out.subscribe(Second_Output_Sub_Key, Second_Output_Topic)

    return out

# ################################################################################################################################

def get_lease_ms() -> 'int':
    """ Returns how long a pull leases a message, in milliseconds.
    """
    lease_seconds = get_pull_lease_seconds()

    out = lease_seconds * Milliseconds_Per_Second
    return out

# ################################################################################################################################

def _lease_in_transaction(engine:'Engine', now_ms:'int', max_messages:'int', leased_until_ms:'int') -> 'tuple[anylist, intdict]':
    """ Leases the deliverable messages of the input subscriber in a transaction of its own.
    """
    with engine.begin() as connection:
        out = lease_messages(connection, Input_Sub_Key, max_messages, _lease_max_len, now_ms, leased_until_ms)

    return out

# ################################################################################################################################

def lease(backend:'SQLPubSubBackend', now_ms:'int', max_messages:'int'=_lease_max_messages) -> 'strintdict':
    """ Leases the deliverable messages of the input subscriber as of the given time,
    and returns the delivery attempt of each, by its message ID.
    """
    engine = backend.engine
    lease_ms = get_lease_ms()
    leased_until_ms = now_ms + lease_ms

    rows, attempts = call_database(engine, _lease_in_transaction, engine, now_ms, max_messages, leased_until_ms)

    out:'strintdict' = {}

    for row in rows:
        out[row.msg_id] = attempts[row.id]

    return out

# ################################################################################################################################

def lease_repeatedly(backend:'SQLPubSubBackend', now_ms:'int', count:'int') -> 'LeaseResult':
    """ Leases the messages of the input subscriber the given number of times, each time after the previous lease
    ran out, and returns what the last lease handed out and the time it was taken at.
    """
    lease_ms = get_lease_ms()
    lease_step_ms = lease_ms + 1

    attempts:'strintdict' = {}
    lease_now_ms = now_ms

    for index in range(count):
        lease_now_ms = now_ms + index * lease_step_ms
        attempts = lease(backend, lease_now_ms)

    out = LeaseResult(attempts, lease_now_ms)
    return out

# ################################################################################################################################

def build(backend:'SQLPubSubBackend', topic_name:'str', data:'str', msg_id:'strnone'=None) -> 'BuiltPublication':
    """ Builds one publication of an acknowledgement.
    """
    out = build_publication(backend, topic_name, data, msg_id=msg_id)
    return out

# ################################################################################################################################

def publish_input(backend:'SQLPubSubBackend', data:'str', expiration:'int'=_input_expiration) -> 'str':
    """ Publishes one message to the input topic and returns its message ID.
    """
    result = backend.publish(Input_Topic, data, expiration=expiration)

    out = result.msg_id
    return out

# ################################################################################################################################

def get_built_msg_id(built:'BuiltPublication') -> 'str':
    """ Returns the message ID of a built publication.
    """
    message_values = built.pending.message_values

    out = message_values['msg_id']
    return out

# ################################################################################################################################

def count_messages(topic_name:'str') -> 'int':
    """ Returns how many messages of a topic are stored.
    """
    rows = get_message_rows(topic_name)

    out = len(rows)
    return out

# ################################################################################################################################

def count_deliveries(sub_key:'str') -> 'int':
    """ Returns how many delivery rows a subscriber has.
    """
    rows = get_delivery_rows(sub_key)

    out = len(rows)
    return out

# ################################################################################################################################

def get_attempt(backend:'SQLPubSubBackend', msg_id:'str') -> 'int':
    """ Returns the delivery attempt that the delivery row of the input subscriber for a message has.
    """
    joined = delivery_table.join(message_table, message_table.c.id == delivery_table.c.message_id)

    query = select(delivery_table.c.attempt)
    query = query.select_from(joined)
    query = query.where(delivery_table.c.sub_key == Input_Sub_Key)
    query = query.where(message_table.c.msg_id == msg_id)

    with backend.engine.connect() as connection:
        out = connection.execute(query).scalar_one()

    return out

# ################################################################################################################################

def get_msg_ids(topic_name:'str') -> 'strlist':
    """ Returns the message IDs of the messages of a topic, in the order of their primary keys.
    """
    rows = get_message_rows(topic_name)

    out:'strlist' = []

    for row in rows:
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

# ################################################################################################################################

    def _database_now_ms(self) -> 'int':
        now_ms = super()._database_now_ms()

        out = now_ms + self.offset_ms
        return out

# ################################################################################################################################
# ################################################################################################################################
