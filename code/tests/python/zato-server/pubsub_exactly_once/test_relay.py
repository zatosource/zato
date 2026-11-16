# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from pubsub_exactly_once.harness import import_enmasse, new_keys, publish_inputs, stage_batch, verify
from pubsub_exactly_once.rest import drain, get_correl_ids
from pubsub_exactly_once.server import start_server, stop_server_releasing
from zato.common.test.exactly_once.config import TestConfig
from zato.common.test.exactly_once.control import count_invocations, fail_once, release

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# How many input messages the baseline test publishes
_baseline_count = 200

# How many input messages the tests of one batch publish
_batch_count = 10

# ################################################################################################################################
# ################################################################################################################################

def test_baseline_relay(zato_server:'any_') -> 'None':
    """ Each input message is relayed to exactly one output message, in the order of publication.
    """
    prefix, keys = new_keys(_baseline_count)

    publish_inputs(keys)
    _ = verify(prefix, keys)

# ################################################################################################################################

def test_failed_attempt_inside_batch(zato_server:'any_') -> 'None':
    """ A relay invocation that publishes and then fails, inside a batch, commits nothing of its batch,
    and the batch delivered again relays each key once.
    """
    prefix, keys = new_keys(_batch_count)

    failed_key = keys[5]
    fail_once(failed_key)

    publish_inputs(keys)
    _ = verify(prefix, keys)

    # The failed key was processed again ..
    assert count_invocations(failed_key) >= 2

# ################################################################################################################################

def test_subscription_stopped_during_batch(zato_server:'any_') -> 'None':
    """ A batch whose delivery is stopped while its last key is held, and which is delivered again
    once the delivery is active again, relays each key once.
    """
    prefix, keys = new_keys(_batch_count)
    last_key = keys[-1]

    # The batch is held at its last key ..
    stage_batch(keys)

    # .. its delivery is stopped and started again ..
    import_enmasse(False)
    import_enmasse(True)

    # .. and the invocation that the stopped delivery left is released.
    release(last_key)

    _ = verify(prefix, keys)

    # The held key was processed again by the new delivery.
    assert count_invocations(last_key) >= 2

# ################################################################################################################################

def test_graceful_stop_during_batch(zato_server:'any_') -> 'None':
    """ A batch that is held at its last key while the server stops, and is released while the server drains
    its deliveries, relays each key once after the server started again.
    """
    prefix, keys = new_keys(_batch_count)
    last_key = keys[-1]

    stage_batch(keys)

    stop_server_releasing(last_key)
    start_server()

    _ = verify(prefix, keys)

# ################################################################################################################################

def test_no_visibility_before_commit(zato_server:'any_') -> 'None':
    """ A subscriber of the output topic receives none of the publications of a batch until the batch is committed.
    """
    reader_username = TestConfig.reader_username
    reader_password = TestConfig.reader_password

    # The queue of the reader holds the outputs of the earlier tests, which are not of interest ..
    _ = drain(reader_username, reader_password)

    prefix, keys = new_keys(_batch_count)
    gate_key = keys[0]
    last_key = keys[-1]
    processed_keys = keys[1:-1]

    # .. the batch is held at its last key, with all the keys before it processed ..
    stage_batch(keys)

    # .. so the reader receives only the output of the first key, whose batch was committed before ..
    messages = drain(reader_username, reader_password)
    early_keys = get_correl_ids(messages, prefix)

    assert early_keys == [gate_key], early_keys

    # .. until the batch is released and committed.
    release(last_key)
    _ = verify(prefix, keys)

    messages = drain(reader_username, reader_password)
    received_keys = get_correl_ids(messages, prefix)

    expected_keys = processed_keys + [last_key]
    assert received_keys == expected_keys, received_keys

# ################################################################################################################################
# ################################################################################################################################
