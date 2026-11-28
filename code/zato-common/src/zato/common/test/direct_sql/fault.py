# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Fault injection - the rows that a failure leaves behind are written in one transaction with the durability settings
# of every other write, as serialized writes, which may never change the tables of the audit log.

# SQLAlchemy
from sqlalchemy import text

# Zato
from zato.common.db_env.engine import call_database
from zato.common.pubsub.sql.schema import message_table, topic_sub_table, trace_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_

    any_ = any_
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

def _execute(engine:'Engine', *statements:'any_') -> 'None':
    with engine.begin() as connection:
        for statement in statements:
            _ = connection.execute(statement)

# ################################################################################################################################

def interrupt_topic_rename(engine:'Engine', old_topic_name:'str', new_topic_name:'str') -> 'None':
    """ Moves the message rows of one topic, with their traces, and nothing else, which is what a rename that ended
    halfway through leaves behind - the deliveries and the subscription remain under the old name.
    """
    message_statement = message_table.update()
    message_statement = message_statement.where(message_table.c.topic_name == old_topic_name)
    message_statement = message_statement.values(topic_name=new_topic_name)

    trace_statement = trace_table.update()
    trace_statement = trace_statement.where(trace_table.c.topic_name == old_topic_name)
    trace_statement = trace_statement.values(topic_name=new_topic_name)

    _ = call_database(engine, _execute, engine, message_statement, trace_statement)

# ################################################################################################################################

def remove_topic_subscriptions(engine:'Engine', topic_name:'str') -> 'None':
    """ Removes the subscription rows of one topic without the server, which is what a subscription that disappeared
    outside of the server leaves behind.
    """
    statement = topic_sub_table.delete()
    statement = statement.where(topic_sub_table.c.topic_name == topic_name)

    _ = call_database(engine, _execute, engine, statement)

# ################################################################################################################################

def restore_previous_generation(engine:'Engine') -> 'None':
    """ Lowers the generation by one, which is what a failover to a replica that did not receive the last raise
    of the generation leaves behind.
    """
    statement = text('update zato_active set generation = generation - 1 where id = 1')

    _ = call_database(engine, _execute, engine, statement)

# ################################################################################################################################
# ################################################################################################################################
