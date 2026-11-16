# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The verification of what the relay service of the exactly-once tests committed.

# stdlib
import time
from dataclasses import dataclass
from functools import partial

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.pubsub.sql.schema import delivery_table, message_table
from zato.common.test.exactly_once.control import Input_Topic, Output_Topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import callable_, strintdict, strlist

    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

# How often the outputs are read, in seconds
_poll_seconds = 0.1

# How long the outputs remain unchanged before the delivery is considered settled, in seconds
_quiet_seconds = 2.0

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OutputCheck:
    """ What the relay committed for the keys of one test.
    """

    # The keys with no output row and the keys with more than one
    missing_keys: 'strlist'
    duplicated_keys: 'strlist'

    # The output rows of the test whose key was never published
    unexpected_keys: 'strlist'

    # The key of each output row of the test, in the order of the message IDs
    output_keys: 'strlist'

    # The delivery rows of the input topic that remain
    pending_count: 'int'

    def __repr__(self) -> 'str':
        output_count = len(self.output_keys)

        out = f'<OutputCheck missing:{self.missing_keys} duplicated:{self.duplicated_keys} ' + \
            f'unexpected:{self.unexpected_keys} pending:{self.pending_count} outputs:{output_count}>'
        return out

# ################################################################################################################################

    @property
    def is_ok(self) -> 'bool':
        if self.missing_keys:
            return False

        if self.duplicated_keys:
            return False

        if self.unexpected_keys:
            return False

        if self.pending_count:
            return False

        out = True
        return out

# ################################################################################################################################

def read_correl_ids(engine:'Engine', topic_name:'str', prefix:'str') -> 'strlist':
    """ Returns the correlation ID of each message of a topic whose correlation ID starts with the prefix,
    in the order in which the messages were stored.
    """
    correl_id_pattern = prefix + '%'

    query = select(message_table.c.correl_id)
    query = query.where(message_table.c.topic_name == topic_name)
    query = query.where(message_table.c.correl_id.like(correl_id_pattern))
    query = query.order_by(message_table.c.id)

    with engine.connect() as connection:
        rows = connection.execute(query).fetchall()

    out:'strlist' = []

    for row in rows:
        out.append(row.correl_id)

    return out

# ################################################################################################################################

def count_topic_deliveries(engine:'Engine', topic_name:'str') -> 'int':
    """ Returns how many delivery rows the messages of a topic have, across all of its subscribers.
    """
    query = select(func.count())
    query = query.select_from(delivery_table)
    query = query.where(delivery_table.c.topic_name == topic_name)

    with engine.connect() as connection:
        out = connection.execute(query).scalar_one()

    return out

# ################################################################################################################################

def check_outputs(engine:'Engine', keys:'strlist', prefix:'str') -> 'OutputCheck':
    """ Reads the output rows of the keys with the given prefix and the delivery rows of the input topic.
    """
    output_keys = read_correl_ids(engine, Output_Topic, prefix)
    pending_count = count_topic_deliveries(engine, Input_Topic)

    counts:'strintdict' = {}

    for key in output_keys:
        if key in counts:
            counts[key] += 1
        else:
            counts[key] = 1

    expected = set(keys)

    missing_keys:'strlist' = []
    duplicated_keys:'strlist' = []
    unexpected_keys:'strlist' = []

    for key in keys:
        if key not in counts:
            missing_keys.append(key)
        elif counts[key] > 1:
            duplicated_keys.append(key)

    for key in counts:
        if key not in expected:
            unexpected_keys.append(key)

    out = OutputCheck()
    out.missing_keys    = missing_keys
    out.duplicated_keys = duplicated_keys
    out.unexpected_keys = unexpected_keys
    out.output_keys     = output_keys
    out.pending_count   = pending_count

    return out

# ################################################################################################################################

def wait_for_outputs(engine:'Engine', keys:'strlist', prefix:'str', timeout:'float') -> 'OutputCheck':
    """ Waits until no input delivery remains and every key has an output row, and then until the outputs
    remain unchanged for a while, which a commit still in flight would change, and returns the final check.
    """
    read_check = partial(check_outputs, engine, keys, prefix)

    out = wait_for_checks(read_check, timeout)
    return out

# ################################################################################################################################

def wait_for_checks(read_check:'callable_', timeout:'float') -> 'OutputCheck':
    """ Waits until a check that the callable reads shows no input delivery and an output row for every key,
    and then until the outputs remain unchanged for a while, and returns the final check.
    """
    deadline = time.monotonic() + timeout

    while True:
        out:'OutputCheck' = read_check()

        if not out.missing_keys:
            if not out.pending_count:
                break

        if time.monotonic() > deadline:
            return out

        time.sleep(_poll_seconds)

    while True:
        time.sleep(_quiet_seconds)

        latest:'OutputCheck' = read_check()

        if latest.output_keys == out.output_keys:
            if latest.pending_count == out.pending_count:
                return latest

        if time.monotonic() > deadline:
            return latest

        out = latest

# ################################################################################################################################

def count_deliveries(engine:'Engine', msg_id:'str') -> 'int':
    """ Returns how many delivery rows the message with the given message ID has.
    """
    joined = delivery_table.join(message_table, message_table.c.id == delivery_table.c.message_id)

    query = select(func.count())
    query = query.select_from(joined)
    query = query.where(message_table.c.msg_id == msg_id)

    with engine.connect() as connection:
        out = connection.execute(query).scalar_one()

    return out

# ################################################################################################################################

def assert_exactly_once(check:'OutputCheck', keys:'strlist') -> 'None':
    """ Fails unless each key has exactly one output row, no other row exists, no input delivery remains
    and the output rows follow the order of publication.
    """
    assert check.is_ok, check
    assert check.output_keys == keys, check

# ################################################################################################################################
# ################################################################################################################################
