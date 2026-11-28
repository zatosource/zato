# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from time import monotonic

# gevent
from gevent import sleep, spawn

# Zato
from common import delete_all_rows, delete_audit_rows, get_delivery_rows, get_message_rows, get_received_event_rows, \
    write_in_one_commit
from fast_path_common import ClaimFailed, install_hooked_fast_path, wait_until
from transaction_statements import assert_one_transaction, get_event_statements, get_expected, record_transactions, \
    statements_publication_claimed
from zato.common.db_env.database import get_database_engine
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.config import get_pull_lease_seconds, ModuleCtx
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict
from zato.common.pubsub.sql.publication import add_published_event, build_publication
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.test.timing import Timer_Tolerance_Seconds

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from zato.common.typing_ import anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The topic and the subscribers of the scenario
_topic = 'pubsub.backend.test.fast-path-pull'
_sub_key = 'zpsk.test.fast-path-pull.1'
_sub_key_other = 'zpsk.test.fast-path-pull.2'

# How long a pull that is handed its messages waits at most, in milliseconds, and how long it may take at most,
# in seconds, which proves that it returned on a publication rather than on its timeout
_wait_ms = 20_000
_handover_bound_seconds = 10

# How long a pull waits in the timeout part, in milliseconds
_short_wait_ms = 300

_ms_per_second = 1000

# The budgets of the pulls
_max_messages = 100
_max_len = 20_000_000
_small_max_len = 50

# The payloads of the budget parts, each of a known size in bytes
_data_30 = 'Order ORD-1001 for Anna Muller'
_data_80 = 'Invoice INV-2002 for Maria Johnson, 3 items, 42.50 USD, due within thirty days..'

# The priorities of the order part
_priority_low = 3
_priority_high = 7

# How long the leases of the expiry part are, in seconds
Env_Pull_Lease_Seconds = ModuleCtx.Env_Pull_Lease_Seconds
_lease_seconds_none = '0'

# How long the expiry part waits for a lease of no time at all to run out, in seconds
_lease_expiry_seconds = 0.01

# ################################################################################################################################
# ################################################################################################################################

class _RacingBackend(SQLPubSubBackend):
    """ A backend whose first read of a queue that finds nothing is followed by a publication that commits
    before the pull begins to wait.
    """
    has_raced: 'bool'

    def _lease_now(self, sub_key:'str', max_messages:'int', max_len:'int') -> 'anylist':

        out = super()._lease_now(sub_key, max_messages, max_len)

        if not out:
            if not self.has_raced:
                self.has_raced = True
                _ = self.publish(_topic, _data_30)

        return out

# ################################################################################################################################
# ################################################################################################################################

def _new_backend() -> 'SQLPubSubBackend':
    """ Returns a backend with one subscriber, starting from empty tables.
    """
    delete_all_rows()
    delete_audit_rows()

    out = SQLPubSubBackend(audit_log=new_test_audit_log())
    out.subscribe(_sub_key, _topic)

    return out

# ################################################################################################################################

def _get_waiter_count(backend:'SQLPubSubBackend') -> 'int':
    """ Returns how many pulls of the subscriber wait for a publication without having been woken up.
    """
    out = 0

    if waiters := backend.fast_path._pull_waiters.get(_sub_key):
        for waiter in waiters:
            if not waiter.is_notified:
                out += 1

    return out

# ################################################################################################################################

def _spawn_waiting_pull(
    backend:'SQLPubSubBackend',
    max_messages:'int'=_max_messages,
    max_len:'int'=_max_len,
    ) -> 'Greenlet':
    """ Starts a pull that waits for a publication and returns once it waits.
    """
    expected_count = _get_waiter_count(backend) + 1

    out = spawn(backend.pull_messages, _sub_key, max_messages, max_len, _wait_ms)

    def _is_waiting() -> 'bool':
        return _get_waiter_count(backend) == expected_count

    wait_until(_is_waiting, 'the pull waits for a publication')

    return out

# ################################################################################################################################

def _publish_in_one_commit(backend:'SQLPubSubBackend', items:'anylist') -> 'strlist':
    """ Publishes the given data and priority pairs in one commit and returns the identifiers of their messages.
    """
    pending_list:'anylist' = []
    out:'strlist' = []

    for data, priority in items:
        built = build_publication(backend, _topic, data, priority=priority)
        add_published_event(backend, built)

        pending_list.append(built.pending)
        out.append(built.pending.msg_id)

    write_in_one_commit(backend, pending_list)

    return out

# ################################################################################################################################

def _get_attempts() -> 'anylist':
    """ Returns the attempt and the lease of each delivery row of the subscriber, in the order of the rows.
    """
    out:'anylist' = []

    for row in get_delivery_rows(_sub_key):
        out.append((row.attempt, row.leased_until_ms))

    return out

# ################################################################################################################################

def _get_msg_ids(messages:'anylist') -> 'strlist':
    """ Returns the identifiers of the given pulled messages, in their order.
    """
    out:'strlist' = []

    for message in messages:
        out.append(message['msg_id'])

    return out

# ################################################################################################################################
# ################################################################################################################################

def _run_handover() -> 'None':
    """ A waiting pull is handed a publication with its first attempt and its lease, in the transaction
    of the publication, which records its reception as well, and the message is acknowledged with that attempt.
    """
    backend = _new_backend()
    pull = _spawn_waiting_pull(backend)

    publish_start = monotonic()
    publish_start_ms = backend.clock.now_ms()

    result = backend.publish(_topic, _data_30)

    publish_end_ms = backend.clock.now_ms()

    messages = pull.get()
    elapsed = monotonic() - publish_start

    # The pull returned on the publication ..
    assert elapsed < _handover_bound_seconds, elapsed
    assert _get_msg_ids(messages) == [result.msg_id], messages
    assert messages[0]['delivery_attempt'] == 1, messages
    assert _get_waiter_count(backend) == 0

    # .. its row is leased with the first attempt for as long as pulls lease their messages ..
    lease_ms = get_pull_lease_seconds() * _ms_per_second
    [(attempt, leased_until_ms)] = _get_attempts()

    assert attempt == 1
    assert publish_start_ms + lease_ms <= leased_until_ms <= publish_end_ms + lease_ms, leased_until_ms

    # .. its reception is recorded ..
    events = get_received_event_rows(_topic)

    assert len(events) == 1, events
    assert events[0]['msg_id'] == result.msg_id, events

    # .. and an acknowledgement with the first attempt removes it.
    ack = backend.ack_pulled_with_publications(_sub_key, [(result.msg_id, 1)], [])

    assert ack.removed_count == 1
    assert get_delivery_rows(_sub_key) == []

# ################################################################################################################################

def _run_timeout() -> 'None':
    """ A pull that no publication reaches returns no messages once its wait is over and is no longer registered.
    """
    backend = _new_backend()

    start = monotonic()
    messages = backend.pull_messages(_sub_key, wait_ms=_short_wait_ms)
    elapsed = monotonic() - start

    assert messages == []
    assert elapsed >= _short_wait_ms / _ms_per_second - Timer_Tolerance_Seconds, elapsed
    assert backend.fast_path._pull_waiters == {}

# ################################################################################################################################

def _run_probe_race() -> 'None':
    """ A publication that commits between the read of an empty queue and the beginning of the wait is pulled
    by a second read, without waiting for the timeout.
    """
    delete_all_rows()
    delete_audit_rows()

    backend = _RacingBackend(audit_log=new_test_audit_log())
    backend.has_raced = False
    backend.subscribe(_sub_key, _topic)

    start = monotonic()
    messages = backend.pull_messages(_sub_key, wait_ms=_wait_ms)
    elapsed = monotonic() - start

    assert backend.has_raced
    assert len(messages) == 1, messages
    assert messages[0]['delivery_attempt'] == 1, messages
    assert elapsed < _handover_bound_seconds, elapsed

# ################################################################################################################################

def _run_limits() -> 'None':
    """ A waiting pull takes no more messages than it asks for and no more bytes than its budget, except for
    a message larger than the budget, which it takes on its own, and the rest of the publication waits in the queue.
    """
    # The number of messages ..
    backend = _new_backend()
    pull = _spawn_waiting_pull(backend, max_messages=2)

    three = [(_data_30, _priority_low), (_data_30, _priority_low), (_data_30, _priority_low)]
    msg_ids = _publish_in_one_commit(backend, three)
    messages = pull.get()

    assert _get_msg_ids(messages) == msg_ids[:2], messages
    assert _get_attempts()[2] == (0, 0)

    # .. the budget of bytes ..
    backend = _new_backend()
    pull = _spawn_waiting_pull(backend, max_len=_small_max_len)

    msg_ids = _publish_in_one_commit(backend, [(_data_30, _priority_low), (_data_30, _priority_low)])
    messages = pull.get()

    assert _get_msg_ids(messages) == msg_ids[:1], messages
    assert _get_attempts()[1] == (0, 0)

    # .. and a message larger than the budget.
    backend = _new_backend()
    pull = _spawn_waiting_pull(backend, max_len=_small_max_len)

    msg_ids = _publish_in_one_commit(backend, [(_data_80, _priority_low), (_data_30, _priority_low)])
    messages = pull.get()

    assert _get_msg_ids(messages) == msg_ids[:1], messages
    assert _get_attempts()[1] == (0, 0)

# ################################################################################################################################

def _run_priority() -> 'None':
    """ A waiting pull takes the messages of a publication in the order of the queue, the highest priority first.
    """
    backend = _new_backend()
    pull = _spawn_waiting_pull(backend, max_messages=1)

    msg_ids = _publish_in_one_commit(backend, [(_data_30, _priority_low), (_data_30, _priority_high)])
    messages = pull.get()

    assert _get_msg_ids(messages) == [msg_ids[1]], messages

# ################################################################################################################################

def _run_two_waiters() -> 'None':
    """ Two waiting pulls of one subscriber take the messages of a publication in the order in which they began to wait,
    each receiving messages of its own.
    """
    backend = _new_backend()

    first = _spawn_waiting_pull(backend, max_messages=1)
    second = _spawn_waiting_pull(backend, max_messages=1)

    msg_ids = _publish_in_one_commit(backend, [(_data_30, _priority_low), (_data_30, _priority_low)])

    first_messages = first.get()
    second_messages = second.get()

    assert _get_msg_ids(first_messages) == [msg_ids[0]], first_messages
    assert _get_msg_ids(second_messages) == [msg_ids[1]], second_messages

    for attempt, _ in _get_attempts():
        assert attempt == 1

# ################################################################################################################################

def _run_rolled_back() -> 'None':
    """ A publication whose transaction does not commit hands nothing over, and the pull that it claimed waits on
    and is handed the next publication.
    """
    backend = _new_backend()
    fast_path = install_hooked_fast_path(backend)
    fast_path.fail_count = 1

    pull = _spawn_waiting_pull(backend)

    try:
        _ = backend.publish(_topic, _data_30)
    except ClaimFailed:
        pass
    else:
        raise Exception('Expected ClaimFailed')

    assert get_message_rows(_topic) == []
    assert get_delivery_rows(_sub_key) == []

    def _waits_again() -> 'bool':
        return _get_waiter_count(backend) == 1

    wait_until(_waits_again, 'the released pull waits again')

    result = backend.publish(_topic, _data_80)
    messages = pull.get()

    assert _get_msg_ids(messages) == [result.msg_id], messages
    assert messages[0]['delivery_attempt'] == 1, messages

# ################################################################################################################################

def _run_lease_expiry() -> 'None':
    """ A message handed over whose lease runs out is handed out again by a later pull with the second attempt,
    after which an acknowledgement with the first attempt is refused and one with the second attempt is accepted.
    """
    backend = _new_backend()
    pull = _spawn_waiting_pull(backend)

    os.environ[Env_Pull_Lease_Seconds] = _lease_seconds_none

    try:
        result = backend.publish(_topic, _data_30)
        messages = pull.get()
    finally:
        del os.environ[Env_Pull_Lease_Seconds]

    assert messages[0]['delivery_attempt'] == 1, messages

    sleep(_lease_expiry_seconds)

    messages = backend.pull_messages(_sub_key)

    assert _get_msg_ids(messages) == [result.msg_id], messages
    assert messages[0]['delivery_attempt'] == 2, messages

    try:
        _ = backend.ack_pulled_with_publications(_sub_key, [(result.msg_id, 1)], [])
    except PubSubAckConflict:
        pass
    else:
        raise Exception('Expected PubSubAckConflict')

    ack = backend.ack_pulled_with_publications(_sub_key, [(result.msg_id, 2)], [])

    assert ack.removed_count == 1

# ################################################################################################################################

def _run_statements() -> 'None':
    """ A publication that hands one subscriber its row inserts that row first, leased, and the row of the other
    subscriber after it, in one transaction with the audit events of the publication and of the reception.
    """
    backend = _new_backend()
    backend.subscribe(_sub_key_other, _topic)

    pull = _spawn_waiting_pull(backend)
    engine = get_database_engine()

    built = build_publication(backend, _topic, _data_30)
    add_published_event(backend, built)

    # The clock of the database is read before the recording, so that no reading of it is due within it.
    _ = backend.clock.now_ms()

    with record_transactions(engine) as recorder:
        write_in_one_commit(backend, [built.pending])

    _ = pull.get()

    assert_one_transaction(recorder, get_expected([statements_publication_claimed, get_event_statements(False)]))

# ################################################################################################################################
# ################################################################################################################################

def run_fast_path_pull_scenario() -> 'None':
    """ Pulls that wait for publications and are handed their messages in the transactions of the publications.
    """
    _run_handover()
    _run_timeout()
    _run_probe_race()
    _run_limits()
    _run_priority()
    _run_two_waiters()
    _run_rolled_back()
    _run_lease_expiry()
    _run_statements()

# ################################################################################################################################
# ################################################################################################################################
