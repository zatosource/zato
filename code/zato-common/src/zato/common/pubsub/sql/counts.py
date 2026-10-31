# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The counts the statistics of the pub/sub database read in place of counting rows - the depth of each
# (subscriber, topic) queue, the number of messages of each topic and the number of messages each publisher
# published to a topic in each minute. Triggers of the database update the counts in the transaction
# that inserts, updates or deletes the rows, whichever code issues the statement.

# SQLAlchemy
from sqlalchemy import DDL, event

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import MetaData
    from zato.common.typing_ import strlist

    # Dummy assignments to satisfy type checkers
    MetaData = MetaData
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# One minute expressed in milliseconds, the width of the publication counts.
Milliseconds_Per_Minute = 60 * 1000

# What the publisher column of a publication count holds for messages published without a publisher.
No_Publisher = ''

# ################################################################################################################################
# ################################################################################################################################

def _add_to_queue(row:'str') -> 'str':
    """ The statement that adds one to the depth of the queue of a delivery row.
    """
    out = 'INSERT INTO pubsub_queue_count (sub_key, topic_name, depth) ' + \
        f'VALUES ({row}.sub_key, {row}.topic_name, 1) ' + \
        'ON CONFLICT (sub_key, topic_name) DO UPDATE SET depth = depth + 1;'

    return out

# ################################################################################################################################

def _remove_from_queue(row:'str') -> 'str':
    """ The statement that subtracts one from the depth of the queue of a delivery row.
    """
    out = 'UPDATE pubsub_queue_count SET depth = depth - 1 ' + \
        f'WHERE sub_key = {row}.sub_key AND topic_name = {row}.topic_name;'

    return out

# ################################################################################################################################

def _add_to_topic(row:'str') -> 'str':
    """ The statements that add one to the message count of the topic of a message row
    and to the publication count of its minute and publisher.
    """
    minute = f'{row}.pub_time_ms - {row}.pub_time_ms % {Milliseconds_Per_Minute}'
    publisher = "coalesce({0}.publisher, '{1}')".format(row, No_Publisher)

    add_message = 'INSERT INTO pubsub_topic_count (topic_name, total) ' + \
        f'VALUES ({row}.topic_name, 1) ' + \
        'ON CONFLICT (topic_name) DO UPDATE SET total = total + 1;'

    add_publication = 'INSERT INTO pubsub_publish_count (topic_name, minute_ms, publisher, total) ' + \
        f'VALUES ({row}.topic_name, {minute}, {publisher}, 1) ' + \
        'ON CONFLICT (topic_name, minute_ms, publisher) DO UPDATE SET total = total + 1;'

    out = f'{add_message} {add_publication}'
    return out

# ################################################################################################################################

def _remove_from_topic(row:'str') -> 'str':
    """ The statements that subtract one from the message count of the topic of a message row
    and from the publication count of its minute and publisher.
    """
    minute = f'{row}.pub_time_ms - {row}.pub_time_ms % {Milliseconds_Per_Minute}'
    publisher = "coalesce({0}.publisher, '{1}')".format(row, No_Publisher)

    remove_message = 'UPDATE pubsub_topic_count SET total = total - 1 ' + \
        f'WHERE topic_name = {row}.topic_name;'

    remove_publication = 'UPDATE pubsub_publish_count SET total = total - 1 ' + \
        f'WHERE topic_name = {row}.topic_name AND minute_ms = {minute} AND publisher = {publisher};'

    out = f'{remove_message} {remove_publication}'
    return out

# ################################################################################################################################

def _trigger_statements() -> 'strlist':
    """ The row triggers that keep the counts in step with the delivery and message rows.
    """
    add_new_delivery = _add_to_queue('new')
    remove_old_delivery = _remove_from_queue('old')

    add_new_message = _add_to_topic('new')
    remove_old_message = _remove_from_topic('old')

    # A delivery row is one message waiting in the queue of its subscriber and topic ..
    delivery_insert = 'CREATE TRIGGER IF NOT EXISTS pubsub_queue_count_insert AFTER INSERT ON pubsub_delivery ' + \
        f'BEGIN {add_new_delivery} END'

    delivery_delete = 'CREATE TRIGGER IF NOT EXISTS pubsub_queue_count_delete AFTER DELETE ON pubsub_delivery ' + \
        f'BEGIN {remove_old_delivery} END'

    # .. and an update moves it to another queue only when it changes the subscriber or the topic ..
    delivery_changed = 'old.sub_key IS NOT new.sub_key OR old.topic_name IS NOT new.topic_name'

    delivery_update = 'CREATE TRIGGER IF NOT EXISTS pubsub_queue_count_update ' + \
        f'AFTER UPDATE OF sub_key, topic_name ON pubsub_delivery WHEN {delivery_changed} ' + \
        f'BEGIN {remove_old_delivery} {add_new_delivery} END'

    # .. a message row counts towards its topic, minute and publisher ..
    message_insert = 'CREATE TRIGGER IF NOT EXISTS pubsub_topic_count_insert AFTER INSERT ON pubsub_message ' + \
        f'BEGIN {add_new_message} END'

    message_delete = 'CREATE TRIGGER IF NOT EXISTS pubsub_topic_count_delete AFTER DELETE ON pubsub_message ' + \
        f'BEGIN {remove_old_message} END'

    # .. and an update moves it to other counts only when it changes one of the three.
    message_changed = 'old.topic_name IS NOT new.topic_name OR old.pub_time_ms IS NOT new.pub_time_ms ' + \
        'OR old.publisher IS NOT new.publisher'

    message_update = 'CREATE TRIGGER IF NOT EXISTS pubsub_topic_count_update ' + \
        f'AFTER UPDATE OF topic_name, pub_time_ms, publisher ON pubsub_message WHEN {message_changed} ' + \
        f'BEGIN {remove_old_message} {add_new_message} END'

    out = [delivery_insert, delivery_delete, delivery_update, message_insert, message_delete, message_update]
    return out

# ################################################################################################################################

def register_counts(metadata:'MetaData') -> 'None':
    """ Attaches the creation of the triggers to the creation of the schema. The triggers are created
    after all the tables, each one only if it does not exist yet.
    """
    for statement in _trigger_statements():

        # DDL formats its statement with the % operator, so the modulo operator is written twice.
        statement = statement.replace('%', '%%')

        ddl = DDL(statement)
        event.listen(metadata, 'after_create', ddl)

# ################################################################################################################################
# ################################################################################################################################
