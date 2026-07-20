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
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

# The topic and subscriber all the wake-up assertions share.
_topic = 'pubsub.backend.test.wakeup'
_sub_key = 'zpsk.test.wakeup.1'

# How long an empty blocking fetch waits in the timeout assertion, in milliseconds.
_short_block_ms = 300

# How long the woken-up fetches are allowed to wait at most, in milliseconds -
# far below their block time, proving they were woken up rather than timing out.
_long_block_ms = 5000

# How long the publisher greenlet sleeps before publishing, in seconds.
_publish_delay_seconds = 0.3

# ################################################################################################################################
# ################################################################################################################################

def _publish_after_delay(backend:'SQLPubSubBackend') -> 'None':
    """ What the publisher greenlet runs - a delayed publish that must wake up
    a fetch already blocking on its event.
    """
    sleep(_publish_delay_seconds)
    _ = backend.publish(_topic, 'published-while-fetch-was-waiting')

# ################################################################################################################################

def run_wakeup_scenario() -> 'None':
    """ Blocking fetches - an empty queue waits out its timeout, a non-empty one
    returns at once and a publish wakes up a fetch already waiting.
    """
    delete_all_rows()

    backend = SQLPubSubBackend()
    backend.subscribe(_sub_key, _topic)

    # An empty queue makes a blocking fetch wait out its full timeout ..
    wait_start = monotonic()
    messages = backend.fetch_messages(_sub_key, block_ms=_short_block_ms)
    elapsed_seconds = monotonic() - wait_start

    assert messages == []
    assert elapsed_seconds >= _short_block_ms / 1000

    # .. a queue with messages returns at once no matter the block time ..
    _ = backend.publish(_topic, 'already-here')

    wait_start = monotonic()
    messages = backend.fetch_messages(_sub_key, block_ms=_long_block_ms)
    elapsed_seconds = monotonic() - wait_start

    assert len(messages) == 1
    assert elapsed_seconds < 1

    _ = backend.ack_message(_sub_key, messages[0]['msg_id'])

    # .. and a publish arriving while a fetch is already blocking wakes it up early -
    # .. well before the block time would have elapsed on its own.
    publisher = spawn(_publish_after_delay, backend)

    wait_start = monotonic()
    messages = backend.fetch_messages(_sub_key, block_ms=_long_block_ms)
    elapsed_seconds = monotonic() - wait_start

    publisher.join()

    assert len(messages) == 1
    assert messages[0]['data'] == 'published-while-fetch-was-waiting'
    assert elapsed_seconds < 2

# ################################################################################################################################
# ################################################################################################################################
