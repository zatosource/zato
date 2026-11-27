# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The rows that one lease statement selects within the size budget of a pull, compared with the rule that a pull applies,
# for queues of generated sizes and budgets - an empty queue, a single message larger than the budget, a message larger
# than the budget after smaller ones and messages that fill the budget exactly among them.

# stdlib
from itertools import count

# hypothesis
from hypothesis import example, given, HealthCheck, settings, strategies as st

# SQLAlchemy
from sqlalchemy import select

# Zato
from common import delete_all_rows, delete_audit_rows
from zato.common.db_env.database import get_database_engine
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.pull import lease_messages
from zato.common.pubsub.sql.schema import delivery_table, message_table
from zato.common.test.audit_log_ import new_test_audit_log

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist

    intlist = intlist

# ################################################################################################################################
# ################################################################################################################################

# The topic and the subscriber of each example are named after its number
_topic_prefix   = 'pubsub.backend.test.lease-budget'
_sub_key_prefix = 'zpsk.test.lease-budget'

# How long each lease of the scenario lasts
_lease_ms = 60_000

# The sizes of the payloads, the size of a queue and the budgets the examples are generated from
_min_payload_size = 1
_max_payload_size = 40
_max_queue_size   = 8
_min_max_len      = 1
_max_max_len      = 60
_max_max_messages = 10

# How many examples are generated
_max_examples = 60

_example_number = count()

# ################################################################################################################################
# ################################################################################################################################

def _expected_sizes(sizes:'intlist', max_messages:'int', max_len:'int') -> 'intlist':
    """ Returns the sizes of the messages that a pull hands out, in the order of the queue, except that a message
    larger than the budget is handed out by the pull that reaches it, after the messages ahead of it, and ends that pull.
    """
    out:'intlist' = []
    total_len = 0

    for size in sizes[:max_messages]:

        is_oversized = size > max_len

        if out and total_len + size > max_len and not is_oversized:
            break

        total_len += size
        out.append(size)

        if is_oversized:
            break

    return out

# ################################################################################################################################

def _get_queue_sizes(sub_key:'str') -> 'intlist':
    """ Returns the sizes of the messages of one subscriber in the order of its queue.
    """
    engine = get_database_engine()

    query = select(message_table.c.data_size)
    query = query.select_from(delivery_table.join(message_table, message_table.c.id == delivery_table.c.message_id))
    query = query.where(delivery_table.c.sub_key == sub_key)
    query = query.order_by(delivery_table.c.priority.desc(), delivery_table.c.message_id.asc())

    out:'intlist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(row.data_size)

    return out

# ################################################################################################################################

def _run_example(backend:'SQLPubSubBackend', payload_sizes:'intlist', max_messages:'int', max_len:'int') -> 'None':
    """ Leases the queue of a new subscriber once, compares what the lease selected with the rule of a pull
    and rolls the lease back.
    """
    number = next(_example_number)
    topic_name = f'{_topic_prefix}.{number}'
    sub_key = f'{_sub_key_prefix}.{number}'

    backend.subscribe(sub_key, topic_name)

    for size in payload_sizes:
        _ = backend.publish(topic_name, 'x' * size)

    queue_sizes = _get_queue_sizes(sub_key)
    expected = _expected_sizes(queue_sizes, max_messages, max_len)

    now_ms = backend.clock.now_ms()
    leased_until_ms = now_ms + _lease_ms

    engine = get_database_engine()

    with engine.connect() as connection:
        transaction = connection.begin()

        rows, attempts = lease_messages(
            connection, backend.subscription_list, sub_key, max_messages, max_len, now_ms, leased_until_ms)

        transaction.rollback()

    leased_sizes:'intlist' = []

    for row in rows:
        leased_sizes.append(row.data_size)
        assert attempts[row.id] == 1, attempts

    assert leased_sizes == expected, (queue_sizes, max_messages, max_len, leased_sizes, expected)

# ################################################################################################################################

def run_lease_budget_scenario() -> 'None':
    """ The rows that one lease statement selects, for generated queues and budgets, starting from empty tables.
    """
    delete_all_rows()
    delete_audit_rows()

    backend = SQLPubSubBackend(audit_log=new_test_audit_log())

    sizes = st.lists(st.integers(_min_payload_size, _max_payload_size), max_size=_max_queue_size)
    max_messages = st.integers(1, _max_max_messages)
    max_len = st.integers(_min_max_len, _max_max_len)

    @settings(max_examples=_max_examples, deadline=None, database=None, suppress_health_check=[HealthCheck.too_slow])
    @given(sizes, max_messages, max_len)
    @example([], 5, 10)
    @example([20], 5, 10)
    @example([3, 4, 20, 2], 5, 10)
    @example([3, 7, 1], 5, 10)
    @example([10], 5, 10)
    @example([4, 4, 4], 2, 100)
    def _check(payload_sizes:'intlist', max_messages:'int', max_len:'int') -> 'None':
        _run_example(backend, payload_sizes, max_messages, max_len)

    _check()

# ################################################################################################################################
# ################################################################################################################################
