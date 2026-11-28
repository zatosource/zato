# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import sleep, spawn

# Zato
from common import delete_all_rows
from fast_path_common import wait_until
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.test.timing import Timer_Tolerance_Seconds

# ################################################################################################################################
# ################################################################################################################################

# The topic and subscriber all the wake-up assertions share.
_topic = 'pubsub.backend.test.wakeup'
_sub_key = 'zpsk.test.wakeup.1'

# How long an empty blocking fetch waits in the timeout assertion, in milliseconds.
_short_block_ms = 300

# The block time of the fetches that must return before it elapses, in milliseconds.
_long_block_ms = 60_000

# How long such a fetch may take at most, in seconds - half of its block time,
# proving it returned on its own or was woken up rather than timing out.
_long_block_bound_seconds = 30

# How long the publisher greenlet sleeps before publishing, in seconds.
_publish_delay_seconds = 0.3

# How long a pull of the pull part waits for a publication at most, in milliseconds.
_pull_wait_ms = 60_000

# ################################################################################################################################
# ################################################################################################################################

def _publish_after_delay(backend:'SQLPubSubBackend') -> 'None':
    """ What the publisher greenlet runs - a delayed publish that must wake up
    a fetch already blocking on its event.
    """
    sleep(_publish_delay_seconds)
    _ = backend.publish(_topic, 'published-while-fetch-was-waiting')

# ################################################################################################################################

def _get_waiting_pulls(backend:'SQLPubSubBackend') -> 'int':
    """ Returns how many pulls of the subscriber wait for a publication without having been woken up.
    """
    out = 0

    if waiters := backend.fast_path._pull_waiters.get(_sub_key):
        for waiter in waiters:
            if not waiter.is_notified:
                out += 1

    return out

# ################################################################################################################################

def _run_pull_wakeup(backend:'SQLPubSubBackend') -> 'None':
    """ A wake-up of a subscriber without a publication of its own makes a waiting pull read its empty queue again
    and wait on, and a publication that follows is handed over to it.
    """
    def _is_waiting() -> 'bool':
        return _get_waiting_pulls(backend) == 1

    pull = spawn(backend.pull_messages, _sub_key, wait_ms=_pull_wait_ms)
    wait_until(_is_waiting, 'the pull waits for a publication')

    version = backend.fast_path.get_version(_sub_key)
    backend.notify_sub_keys([_sub_key])

    assert backend.fast_path.get_version(_sub_key) == version + 1

    wait_until(_is_waiting, 'the woken pull waits again')
    assert not pull.ready()

    result = backend.publish(_topic, 'published-while-pull-was-waiting')
    messages = pull.get()

    assert len(messages) == 1, messages
    assert messages[0]['msg_id'] == result.msg_id

    _ = backend.ack_message(_sub_key, result.msg_id)

# ################################################################################################################################

def run_wakeup_scenario() -> 'None':
    """ Blocking fetches - an empty queue waits out its timeout, a non-empty one
    returns at once and a publish wakes up a fetch already waiting, and a wake-up reaches a waiting pull as well.
    """
    delete_all_rows()

    backend = SQLPubSubBackend(audit_log=new_test_audit_log())
    backend.subscribe(_sub_key, _topic)

    # An empty queue makes a blocking fetch wait out its full timeout ..
    wait_start = monotonic()
    messages = backend.fetch_messages(_sub_key, block_ms=_short_block_ms)
    elapsed_seconds = monotonic() - wait_start

    assert messages == []
    assert elapsed_seconds >= _short_block_ms / 1000 - Timer_Tolerance_Seconds

    # .. a queue with messages returns at once no matter the block time ..
    _ = backend.publish(_topic, 'already-here')

    wait_start = monotonic()
    messages = backend.fetch_messages(_sub_key, block_ms=_long_block_ms)
    elapsed_seconds = monotonic() - wait_start

    assert len(messages) == 1
    assert elapsed_seconds < _long_block_bound_seconds

    _ = backend.ack_message(_sub_key, messages[0]['msg_id'])

    # .. and a publish arriving while a fetch is already blocking wakes it up -
    # .. no earlier than the publish and well before the block time would have elapsed on its own.
    publisher = spawn(_publish_after_delay, backend)

    wait_start = monotonic()
    messages = backend.fetch_messages(_sub_key, block_ms=_long_block_ms)
    elapsed_seconds = monotonic() - wait_start

    publisher.join()

    assert len(messages) == 1
    assert messages[0]['data'] == 'published-while-fetch-was-waiting'
    assert elapsed_seconds >= _publish_delay_seconds - Timer_Tolerance_Seconds
    assert elapsed_seconds < _long_block_bound_seconds

    _ = backend.ack_message(_sub_key, messages[0]['msg_id'])

    # A waiting pull is woken up in the same way.
    _run_pull_wakeup(backend)

# ################################################################################################################################
# ################################################################################################################################
